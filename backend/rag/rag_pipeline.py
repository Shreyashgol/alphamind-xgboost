from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta

from core.ticker_catalog import get_ticker_keywords
from rag.document_loader import load_documents
from rag.embedder import SentenceTransformerEmbedder
from rag.vector_store import FaissVectorStore
from utils.logger import get_logger
from utils.settings import get_settings

try:
    from groq import Groq
except ImportError:
    Groq = None


logger = get_logger(__name__)

_embedder: SentenceTransformerEmbedder | None = None
_store: FaissVectorStore | None = None


def ensure_knowledge_index(force_rebuild: bool = False) -> dict:
    store = _get_store()
    if store.exists() and not force_rebuild:
        store.load()
        return {"status": "loaded", "documents": len(store.metadata)}

    documents = load_documents()
    if not documents:
        logger.warning("Knowledge ingestion found zero documents.")
        return {"status": "empty", "documents": 0}

    embeddings = _get_embedder().embed_documents([document["text"] for document in documents])
    store.build(documents, embeddings)
    return {"status": "built", "documents": len(documents)}


def retrieve_context(
    query: str,
    *,
    ticker: str | None = None,
    recency_days: int | None = None,
    top_k: int | None = None,
) -> list[dict]:
    settings = get_settings()
    desired_top_k = top_k or settings.knowledge_top_k

    query_text = query
    if ticker:
        keywords = " ".join(get_ticker_keywords(ticker))
        query_text = f"{ticker} {keywords} {query}"

    try:
        ensure_knowledge_index(force_rebuild=False)
        store = _get_store()
        embedding = _get_embedder().embed_query(query_text)
        return store.search(
            embedding,
            top_k=desired_top_k,
            ticker=ticker,
            recency_days=recency_days or settings.default_recency_days,
        )
    except Exception as exc:
        logger.warning("Vector retrieval failed, falling back to lexical search: %s", exc)
        return _lexical_retrieve_context(
            query_text,
            ticker=ticker,
            recency_days=recency_days or settings.default_recency_days,
            top_k=desired_top_k,
        )


def answer_query(question: str, ticker: str | None = None, recency_days: int | None = None) -> dict:
    matches = retrieve_context(question, ticker=ticker, recency_days=recency_days)
    context = [
        {
            "source": match["document"]["source"],
            "summary": match["document"]["summary"],
            "date": match["document"].get("date"),
            "score": round(match["score"], 4),
        }
        for match in matches
    ]
    suggestions = _suggest_followups(question, ticker, bool(context))
    answer = _generate_conversational_answer(question, ticker, context, suggestions)

    return {
        "question": question,
        "ticker": ticker,
        "answer": answer,
        "sources": [item["source"] for item in context],
        "context": context,
        "suggestions": suggestions,
    }


def _get_embedder() -> SentenceTransformerEmbedder:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformerEmbedder()
    return _embedder


def _get_store() -> FaissVectorStore:
    global _store
    if _store is None:
        _store = FaissVectorStore()
    return _store


def _lexical_retrieve_context(
    query: str,
    *,
    ticker: str | None,
    recency_days: int | None,
    top_k: int,
) -> list[dict]:
    documents = _load_retrieval_metadata()
    if not documents:
        return []

    terms = _tokenize(query)
    threshold_date = date.today() - timedelta(days=recency_days) if recency_days else None
    matches: list[dict] = []

    for document in documents:
        if ticker and document.get("ticker") not in {None, ticker}:
            continue
        if threshold_date and not _is_recent_enough(document.get("date"), threshold_date):
            continue

        haystack = " ".join(
            str(document.get(field, ""))
            for field in ("ticker", "title", "source", "summary", "text")
        ).lower()
        if not haystack:
            continue

        score = sum(haystack.count(term) for term in terms)
        if ticker and str(document.get("ticker", "")).upper() == ticker:
            score += 2
        if score > 0:
            matches.append({"document": document, "score": float(score)})

    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[:top_k]


def _load_retrieval_metadata() -> list[dict]:
    settings = get_settings()
    if settings.faiss_metadata_path.exists():
        try:
            return json.loads(settings.faiss_metadata_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Could not read FAISS metadata for lexical fallback: %s", exc)

    try:
        return load_documents()
    except Exception as exc:
        logger.warning("Could not load documents for lexical fallback: %s", exc)
        return []


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9]{1,}", text.lower())
    stop_words = {
        "and",
        "for",
        "from",
        "has",
        "the",
        "this",
        "that",
        "what",
        "with",
    }
    return [token for token in tokens if token not in stop_words]


def _is_recent_enough(raw_date: str | None, threshold_date: date) -> bool:
    if not raw_date:
        return True
    try:
        parsed = datetime.fromisoformat(raw_date).date()
    except ValueError:
        return True
    return parsed >= threshold_date


def _generate_conversational_answer(
    question: str,
    ticker: str | None,
    context: list[dict],
    suggestions: list[str],
) -> str:
    settings = get_settings()
    if settings.groq_api_key and Groq is not None:
        try:
            client = Groq(api_key=settings.groq_api_key)
            completion = client.chat.completions.create(
                model=settings.groq_model,
                temperature=0.25,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are AlphaMind, a conversational financial research assistant. "
                            "Answer using only the supplied local context. If context is thin, say so plainly. "
                            "Be useful, concise, and include practical next questions the user could ask. "
                            "Do not invent current market facts."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "ticker": ticker,
                                "question": question,
                                "retrieved_context": context,
                                "suggested_followups": suggestions,
                            },
                            indent=2,
                        ),
                    },
                ],
            )
            return completion.choices[0].message.content.strip()
        except Exception as exc:
            logger.warning("Groq query answer failed, using local answer: %s", exc)

    if not context:
        subject = ticker or "that ticker"
        return (
            f"I could not find strong local knowledge-base context for {subject}. "
            "You can still run a forecast if a matching CSV exists in backend/data/uploads, "
            "and you can improve my answers by adding company reports or notes to backend/data/knowledge. "
            f"Good next questions: {', '.join(suggestions)}."
        )

    evidence = " ".join(item["summary"] for item in context[:3])
    subject = ticker or "the selected company"
    return (
        f"Based on the local knowledge base, {subject} is mainly being described through this evidence: {evidence} "
        f"To go deeper, try asking: {', '.join(suggestions)}."
    )


def _suggest_followups(question: str, ticker: str | None, has_context: bool) -> list[str]:
    subject = ticker or "this stock"
    lowered = question.lower()
    suggestions = [
        f"What are the strongest upside drivers for {subject}?",
        f"What risks could weaken the forecast for {subject}?",
        f"Which retrieved sources support the answer for {subject}?",
    ]
    if "risk" not in lowered:
        suggestions.append(f"What are the main risk signals for {subject}?")
    if "forecast" not in lowered:
        suggestions.append(f"How does the forecast align with the retrieved context for {subject}?")
    if not has_context:
        suggestions.append(f"What files should I add so AlphaMind can analyze {subject} better?")

    return suggestions[:4]

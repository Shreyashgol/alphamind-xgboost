from __future__ import annotations

from core.ticker_catalog import get_ticker_keywords
from rag.rag_pipeline import retrieve_context

POSITIVE_TERMS = {
    "growth",
    "beat",
    "improved",
    "strong",
    "expansion",
    "upside",
    "record",
    "profit",
    "accelerating",
}
NEGATIVE_TERMS = {
    "risk",
    "decline",
    "miss",
    "weak",
    "slowdown",
    "pressure",
    "loss",
    "downgrade",
    "headwind",
}


def get_knowledge_context(ticker: str, recency_days: int = 90) -> dict:
    query = " ".join([ticker, *get_ticker_keywords(ticker)])
    matches = retrieve_context(query, ticker=ticker, recency_days=recency_days)

    documents = [
        {
            "source": match["document"]["source"],
            "summary": match["document"]["summary"],
            "ticker": match["document"].get("ticker"),
            "date": match["document"].get("date"),
            "score": round(match["score"], 4),
        }
        for match in matches
    ]
    highlights = [item["summary"] for item in documents]
    sentiment_score = _score_sentiment(highlights)

    if not documents:
        highlights.append("No relevant financial context matched the ticker and recency filters.")

    return {
        "documents": documents,
        "highlights": highlights[:3],
        "sentiment_score": sentiment_score,
    }


def _score_sentiment(highlights: list[str]) -> float:
    score = 0.0
    for highlight in highlights:
        lowered = highlight.lower()
        score += sum(1 for term in POSITIVE_TERMS if term in lowered)
        score -= sum(1 for term in NEGATIVE_TERMS if term in lowered)

    if not highlights:
        return 0.0
    return score / max(1, len(highlights))

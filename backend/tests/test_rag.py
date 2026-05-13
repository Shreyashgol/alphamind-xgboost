from rag.document_loader import _chunk_text, _summarize
from rag import rag_pipeline


def test_chunk_text_splits_long_documents():
    chunks = _chunk_text("A" * 2600)
    assert len(chunks) >= 2


def test_summarize_returns_non_empty_sentence():
    summary = _summarize("Revenue improved materially. Margins expanded in the quarter.")
    assert summary
    assert "Revenue improved materially." in summary


def test_retrieve_context_uses_lexical_fallback(monkeypatch):
    monkeypatch.setattr(rag_pipeline, "ensure_knowledge_index", lambda force_rebuild=False: {"status": "loaded"})
    monkeypatch.setattr(rag_pipeline, "_get_embedder", lambda: (_ for _ in ()).throw(RuntimeError("offline")))
    monkeypatch.setattr(
        rag_pipeline,
        "_load_retrieval_metadata",
        lambda: [
            {
                "source": "AAPL_Q1_Report.pdf",
                "summary": "AAPL revenue growth improved with strong margins.",
                "text": "AAPL revenue growth improved with strong margins.",
                "ticker": "AAPL",
                "date": None,
            },
            {
                "source": "MSFT_Q1_Report.pdf",
                "summary": "Cloud demand was resilient.",
                "text": "Cloud demand was resilient.",
                "ticker": "MSFT",
                "date": None,
            },
        ],
    )

    matches = rag_pipeline.retrieve_context("revenue growth margins", ticker="AAPL", top_k=1)

    assert len(matches) == 1
    assert matches[0]["document"]["source"] == "AAPL_Q1_Report.pdf"


def test_answer_query_returns_suggestions(monkeypatch):
    monkeypatch.setattr(rag_pipeline, "Groq", None)
    monkeypatch.setattr(
        rag_pipeline,
        "retrieve_context",
        lambda question, ticker=None, recency_days=None: [
            {
                "document": {
                    "source": "NVDA_Q1_Report.pdf",
                    "summary": "NVDA data center growth remained strong.",
                    "date": None,
                },
                "score": 4.0,
            }
        ],
    )

    payload = rag_pipeline.answer_query("What changed?", ticker="NVDA")

    assert "NVDA" in payload["answer"]
    assert payload["suggestions"]

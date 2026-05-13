from pathlib import Path
import sys

from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from main import app
from routes import explain_routes, forecast_routes, query_routes, ticker_routes, train_routes


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_train_route(monkeypatch):
    monkeypatch.setattr(
        train_routes,
        "train_models",
        lambda ticker: {"ticker": ticker, "selected_model": "xgboost", "scorecard": {}, "features": []},
    )
    response = client.post("/api/train", json={"ticker": "MSFT"})
    assert response.status_code == 200
    assert response.json()["ticker"] == "MSFT"


def test_forecast_route(monkeypatch):
    monkeypatch.setattr(
        forecast_routes,
        "run_forecast",
        lambda ticker, horizon: {
            "ticker": ticker,
            "horizon": horizon,
            "prediction_percent": 1.25,
            "predicted_price": 120.4,
            "trend": "upward",
            "features": [],
            "context": [],
            "confidence": {"label": "High", "score": 0.8},
            "model": {"selected": "xgboost", "validation_rmse": 0.1, "validation_mae": 0.1, "validation_mape": 0.1, "scorecard": {}},
            "history": [],
            "forecast": [{"date": "2026-01-01", "value": 120.4, "day_offset": 1}],
        },
    )

    response = client.get("/api/forecast", params={"ticker": "MSFT", "horizon": 1})
    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "MSFT"
    assert len(payload["forecast"]) == 1


def test_explain_route(monkeypatch):
    monkeypatch.setattr(
        explain_routes,
        "build_explanation",
        lambda ticker, horizon: {
            "ticker": ticker,
            "horizon": horizon,
            "prediction_percent": 1.25,
            "predicted_price": 120.4,
            "trend": "upward",
            "features": [],
            "context": [],
            "confidence": {"label": "High", "score": 0.8},
            "model": {"selected": "xgboost"},
            "narrative": {
                "summary": "summary",
                "trend": "trend",
                "features": "features",
                "context": "context",
                "confidence": "confidence",
            },
        },
    )

    response = client.get("/api/explain", params={"ticker": "AAPL", "horizon": 5})
    assert response.status_code == 200
    assert response.json()["ticker"] == "AAPL"


def test_query_route(monkeypatch):
    monkeypatch.setattr(
        query_routes,
        "answer_query",
        lambda question, ticker, recency_days: {
            "question": question,
            "ticker": ticker,
            "answer": "answer",
            "sources": ["AAPL_Q1_Report.pdf"],
            "context": [],
            "suggestions": ["What risks could weaken the forecast for AAPL?"],
        },
    )

    response = client.post("/api/query", json={"question": "What changed?", "ticker": "AAPL", "recency_days": 90})
    assert response.status_code == 200
    assert response.json()["sources"] == ["AAPL_Q1_Report.pdf"]
    assert response.json()["suggestions"]


def test_ticker_route(monkeypatch):
    monkeypatch.setattr(ticker_routes, "list_available_tickers", lambda: ["AAPL", "NVDA"])

    response = client.get("/api/tickers")

    assert response.status_code == 200
    assert response.json() == {"tickers": ["AAPL", "NVDA"]}

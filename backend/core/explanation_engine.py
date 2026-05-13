from __future__ import annotations

import json

from core.automl_engine import run_forecast
from core.knowledge_augment import get_knowledge_context
from utils.settings import get_settings

try:
    from groq import Groq
except ImportError:
    Groq = None


def build_explanation(ticker: str, horizon: int = 7) -> dict:
    forecast_result = run_forecast(ticker, horizon)
    knowledge = get_knowledge_context(ticker, recency_days=get_settings().default_recency_days)
    narrative = _generate_narrative(forecast_result, knowledge)

    return {
        "ticker": ticker,
        "horizon": horizon,
        "prediction_percent": forecast_result["prediction_percent"],
        "predicted_price": forecast_result["predicted_price"],
        "trend": forecast_result["trend"],
        "features": forecast_result["features"],
        "context": knowledge["documents"],
        "confidence": forecast_result["confidence"],
        "model": forecast_result["model"],
        "narrative": narrative,
    }


def _generate_narrative(forecast_result: dict, knowledge: dict) -> dict:
    settings = get_settings()
    if settings.groq_api_key and Groq is not None:
        try:
            client = Groq(api_key=settings.groq_api_key)
            prompt = _build_prompt(forecast_result, knowledge)
            completion = client.chat.completions.create(
                model=settings.groq_model,
                temperature=0.2,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a financial analyst. Return JSON with keys summary, trend, features, context, confidence."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            return json.loads(completion.choices[0].message.content)
        except Exception:
            pass

    feature_text = ", ".join(
        f"{item['feature']} ({item['direction']}, contribution {item['contribution']:.4f})"
        for item in forecast_result["features"][:3]
    ) or "No dominant engineered feature contributions were available."
    context_text = " ".join(item["summary"] for item in knowledge["documents"][:2]) or "No matching recent context was retrieved."

    return {
        "summary": (
            f"{forecast_result['ticker']} is projected to move {forecast_result['prediction_percent']:.2f}% "
            f"toward {forecast_result['predicted_price']:.2f} over the next {forecast_result['horizon']} trading days."
        ),
        "trend": (
            f"The selected {forecast_result['model']['selected']} model points to a {forecast_result['trend']} outlook "
            f"with validation RMSE of {forecast_result['model']['validation_rmse']:.4f}."
        ),
        "features": f"Top feature signals: {feature_text}.",
        "context": context_text,
        "confidence": forecast_result["confidence"]["rationale"],
    }


def _build_prompt(forecast_result: dict, knowledge: dict) -> str:
    payload = {
        "forecast": {
            "ticker": forecast_result["ticker"],
            "horizon": forecast_result["horizon"],
            "predicted_price": forecast_result["predicted_price"],
            "prediction_percent": forecast_result["prediction_percent"],
            "trend": forecast_result["trend"],
            "confidence": forecast_result["confidence"],
            "model": forecast_result["model"],
            "features": forecast_result["features"][:5],
        },
        "retrieved_context": knowledge["documents"][:3],
    }
    return json.dumps(payload, indent=2)

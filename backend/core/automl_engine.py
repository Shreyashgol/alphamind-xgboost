from __future__ import annotations

import os
from dataclasses import dataclass

from core.knowledge_augment import get_knowledge_context
from core.preprocessing import engineer_features, get_feature_columns, load_stock_frame, next_trading_days, train_validation_split
from models.arima_model import ARIMAModel
from models.lstm_model import LSTMModel
from models.xgboost_model import XGBoostModel
from utils.metrics import mean_absolute_error, mean_absolute_percentage_error, root_mean_squared_error

try:
    import shap
except ImportError:
    shap = None


@dataclass
class TrainingArtifact:
    ticker: str
    model_name: str
    model: object
    metrics: dict[str, dict[str, float]]
    feature_insights: list[dict]


_TRAINING_CACHE: dict[str, TrainingArtifact] = {}


def train_models(ticker: str) -> dict:
    artifact = _fit_and_cache_models(ticker, force_retrain=True)
    return _serialize_training_artifact(artifact)


def run_forecast(ticker: str, horizon: int = 7) -> dict:
    artifact = _fit_and_cache_models(ticker)
    frame = load_stock_frame(ticker)
    raw_predictions = artifact.model.predict(horizon, frame)
    last_close = float(frame["close"].iloc[-1])
    forecast = [
        {
            "day_offset": index,
            "date": forecast_date.date().isoformat(),
            "value": round(float(value), 2),
        }
        for index, (forecast_date, value) in enumerate(
            zip(next_trading_days(frame["date"].iloc[-1], horizon), raw_predictions, strict=False),
            start=1,
        )
    ]

    predicted_price = round(float(raw_predictions[-1]), 2)
    prediction_percent = round(((predicted_price - last_close) / max(last_close, 1e-6)) * 100, 2)
    trend = _trend_label(prediction_percent)
    knowledge = get_knowledge_context(ticker)
    confidence = _build_confidence(
        rmse=artifact.metrics[artifact.model_name]["rmse"],
        last_close=last_close,
        trend=trend,
        sentiment_score=knowledge["sentiment_score"],
    )

    history = [
        {
            "date": row["date"].date().isoformat(),
            "open": round(float(row["open"]), 2),
            "high": round(float(row["high"]), 2),
            "low": round(float(row["low"]), 2),
            "close": round(float(row["close"]), 2),
            "volume": int(row["volume"]),
        }
        for _, row in frame.tail(60).iterrows()
    ]

    return {
        "ticker": ticker,
        "horizon": horizon,
        "prediction_percent": prediction_percent,
        "predicted_price": predicted_price,
        "trend": trend,
        "features": artifact.feature_insights,
        "context": knowledge["documents"],
        "confidence": confidence,
        "model": {
            "selected": artifact.model_name,
            "validation_rmse": round(artifact.metrics[artifact.model_name]["rmse"], 4),
            "validation_mae": round(artifact.metrics[artifact.model_name]["mae"], 4),
            "validation_mape": round(artifact.metrics[artifact.model_name]["mape"], 4),
            "scorecard": {
                name: {metric: round(value, 4) for metric, value in metrics.items()}
                for name, metrics in artifact.metrics.items()
            },
        },
        "history": history,
        "forecast": forecast,
    }


def _fit_and_cache_models(ticker: str, force_retrain: bool = False) -> TrainingArtifact:
    if not force_retrain and ticker in _TRAINING_CACHE:
        return _TRAINING_CACHE[ticker]

    frame = load_stock_frame(ticker)
    if len(frame) < 40:
        raise ValueError("At least 40 data points are required to train the forecasting pipeline.")

    train_frame, validation_frame = train_validation_split(frame, validation_size=min(14, max(5, len(frame) // 8)))
    validation_size = len(validation_frame)
    actual = validation_frame["close"].astype(float).tolist()

    candidates: dict[str, object] = {}
    errors: dict[str, dict[str, float]] = {}
    for name, model_factory in (
        ("xgboost", XGBoostModel),
        ("arima", ARIMAModel),
        ("lstm", LSTMModel),
    ):
        try:
            model = model_factory()
            model.fit(train_frame)
            predictions = model.predict(validation_size, train_frame)
        except Exception:
            continue

        candidates[name] = model
        errors[name] = {
            "rmse": root_mean_squared_error(actual, predictions),
            "mae": mean_absolute_error(actual, predictions),
            "mape": mean_absolute_percentage_error(actual, predictions),
        }

    if not candidates:
        raise RuntimeError("No forecasting models were available for training.")

    best_name = min(errors, key=lambda model_name: errors[model_name]["rmse"])
    final_model = type(candidates[best_name])()
    final_model.fit(frame)

    artifact = TrainingArtifact(
        ticker=ticker,
        model_name=best_name,
        model=final_model,
        metrics=errors,
        feature_insights=_compute_feature_insights(frame),
    )
    _TRAINING_CACHE[ticker] = artifact
    return artifact


def _compute_feature_insights(frame) -> list[dict]:
    try:
        model = XGBoostModel()
        model.fit(frame)
        engineered = engineer_features(frame, include_target=True)
        feature_columns = get_feature_columns(engineered)
        latest_features = engineer_features(frame, include_target=False).iloc[[-1]][feature_columns]
    except Exception:
        return []

    if shap is not None and os.getenv("ENABLE_SHAP", "").lower() in {"1", "true", "yes"}:
        try:
            explainer = shap.TreeExplainer(model.model)
            shap_values = explainer.shap_values(latest_features)
            if hasattr(shap_values, "tolist"):
                contributions = shap_values[0].tolist()
            else:
                contributions = list(shap_values[0])
            return _format_feature_insights(feature_columns, contributions, latest_features.iloc[0].to_dict())
        except Exception:
            pass

    feature_importance = model.get_feature_importance()
    baseline = engineered[feature_columns].mean().to_dict()
    contributions = [
        feature_importance.get(column, 0.0) * (float(latest_features.iloc[0][column]) - float(baseline.get(column, 0.0)))
        for column in feature_columns
    ]
    return _format_feature_insights(feature_columns, contributions, latest_features.iloc[0].to_dict())


def _format_feature_insights(feature_columns: list[str], contributions: list[float], feature_values: dict) -> list[dict]:
    ranked = sorted(
        (
            {
                "feature": feature,
                "value": round(float(feature_values[feature]), 4),
                "contribution": float(contribution),
                "direction": "upward" if contribution >= 0 else "downward",
            }
            for feature, contribution in zip(feature_columns, contributions, strict=False)
        ),
        key=lambda item: abs(item["contribution"]),
        reverse=True,
    )
    return [
        {
            **item,
            "contribution": round(item["contribution"], 4),
        }
        for item in ranked[:5]
    ]


def _trend_label(prediction_percent: float) -> str:
    if prediction_percent > 1:
        return "upward"
    if prediction_percent < -1:
        return "downward"
    return "sideways"


def _build_confidence(rmse: float, last_close: float, trend: str, sentiment_score: float) -> dict:
    normalized_rmse = rmse / max(last_close, 1e-6)
    alignment = _sentiment_alignment(trend, sentiment_score)
    score = max(0.0, min(1.0, (1 - min(normalized_rmse * 12, 1.0)) * 0.7 + alignment * 0.3))

    if score >= 0.72:
        label = "High"
    elif score >= 0.45:
        label = "Medium"
    else:
        label = "Low"

    return {
        "label": label,
        "score": round(score, 2),
        "rmse": round(rmse, 4),
        "sentiment_alignment": round(alignment, 2),
        "rationale": (
            f"Confidence is {label.lower()} because validation RMSE was {rmse:.4f} and "
            f"knowledge sentiment alignment scored {alignment:.2f}."
        ),
    }


def _sentiment_alignment(trend: str, sentiment_score: float) -> float:
    if abs(sentiment_score) < 0.2 or trend == "sideways":
        return 0.5
    if trend == "upward" and sentiment_score > 0:
        return 1.0
    if trend == "downward" and sentiment_score < 0:
        return 1.0
    return 0.0


def _serialize_training_artifact(artifact: TrainingArtifact) -> dict:
    return {
        "ticker": artifact.ticker,
        "selected_model": artifact.model_name,
        "scorecard": {
            name: {metric: round(value, 4) for metric, value in metrics.items()}
            for name, metrics in artifact.metrics.items()
        },
        "features": artifact.feature_insights,
    }

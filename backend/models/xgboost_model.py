from __future__ import annotations

import os

import numpy as np

from core.preprocessing import append_prediction_row, engineer_features, get_feature_columns, next_trading_days
from models.base_model import BaseModel

os.environ.setdefault("OMP_NUM_THREADS", "1")

try:
    import xgboost as xgb
except ImportError as exc:
    xgb = None
    _xgboost_import_error = exc


class XGBoostModel(BaseModel):
    def __init__(self) -> None:
        if xgb is None:
            raise RuntimeError(
                "xgboost is not installed or cannot be loaded. Install xgboost and the OpenMP runtime."
            ) from _xgboost_import_error

        self.model = xgb.XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=1,
        )
        self.feature_columns: list[str] = []

    def fit(self, frame) -> None:
        engineered = engineer_features(frame, include_target=True)
        self.feature_columns = get_feature_columns(engineered)
        if not self.feature_columns:
            raise ValueError("XGBoost feature engineering produced no usable features.")

        x_train = engineered[self.feature_columns]
        y_train = engineered["target"]
        self.model.fit(x_train, y_train)

    def predict(self, horizon: int, history_frame) -> list[float]:
        if not self.feature_columns:
            raise RuntimeError("XGBoost model must be fitted before prediction.")

        rolling_history = history_frame.copy()
        predictions: list[float] = []

        for next_date in next_trading_days(rolling_history["date"].iloc[-1], horizon):
            feature_frame = engineer_features(rolling_history, include_target=False)
            latest_features = feature_frame.iloc[[-1]][self.feature_columns]
            next_value = float(self.model.predict(latest_features)[0])
            predictions.append(next_value)
            rolling_history = append_prediction_row(rolling_history, next_date, next_value)

        return predictions

    def get_feature_importance(self) -> dict[str, float]:
        if not self.feature_columns:
            return {}
        return {
            feature: float(score)
            for feature, score in zip(self.feature_columns, self.model.feature_importances_, strict=False)
        }

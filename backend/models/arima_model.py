from __future__ import annotations

from itertools import product

from models.base_model import BaseModel

try:
    from statsmodels.tsa.arima.model import ARIMA
except ImportError as exc:
    ARIMA = None
    _arima_import_error = exc


class ARIMAModel(BaseModel):
    def __init__(self) -> None:
        if ARIMA is None:
            raise RuntimeError("statsmodels is required to use the ARIMA forecaster.") from _arima_import_error
        self.history: list[float] = []
        self.order = (1, 1, 0)
        self.fitted_model = None

    def fit(self, frame) -> None:
        series = frame["close"].astype(float).tolist()
        if len(series) < 20:
            raise ValueError("ARIMA needs at least 20 closing prices.")

        self.history = series
        self.order = self._select_order(series)
        self.fitted_model = ARIMA(series, order=self.order).fit()

    def predict(self, horizon: int, history_frame) -> list[float]:
        if self.fitted_model is None:
            raise RuntimeError("ARIMA model must be fitted before prediction.")
        forecast = self.fitted_model.forecast(steps=horizon)
        return [float(value) for value in forecast]

    def _select_order(self, series: list[float]) -> tuple[int, int, int]:
        best_order = self.order
        best_aic = float("inf")
        for p, d, q in product((1, 2, 3), (0, 1), (0, 1, 2)):
            try:
                candidate = ARIMA(series, order=(p, d, q)).fit()
            except Exception:
                continue
            if candidate.aic < best_aic:
                best_aic = candidate.aic
                best_order = (p, d, q)
        return best_order

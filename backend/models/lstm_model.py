from __future__ import annotations

import numpy as np

from models.base_model import BaseModel

try:
    import torch
    from torch import nn
except ImportError as exc:
    torch = None
    nn = None
    _torch_import_error = exc


if nn is not None:
    class _LSTMForecaster(nn.Module):
        def __init__(self, hidden_size: int) -> None:
            super().__init__()
            self.lstm = nn.LSTM(input_size=1, hidden_size=hidden_size, batch_first=True)
            self.output = nn.Linear(hidden_size, 1)

        def forward(self, inputs):
            outputs, _ = self.lstm(inputs)
            return self.output(outputs[:, -1, :])
else:
    _LSTMForecaster = None


class LSTMModel(BaseModel):
    def __init__(self, window: int = 14, hidden_size: int = 16, epochs: int = 15, learning_rate: float = 1e-3) -> None:
        if torch is None:
            raise RuntimeError("torch is required to use the LSTM forecaster.") from _torch_import_error

        self.window = window
        self.hidden_size = hidden_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.history: list[float] = []
        self.model = _LSTMForecaster(hidden_size)
        self.series_min = 0.0
        self.series_scale = 1.0
        torch.set_num_threads(1)

    def fit(self, frame) -> None:
        series = frame["close"].astype(float).to_numpy()
        if len(series) <= self.window:
            raise ValueError("Series must be longer than the configured LSTM window.")

        self.history = series.tolist()
        self.series_min = float(series.min())
        self.series_scale = float(series.max() - series.min()) or 1.0
        normalized = (series - self.series_min) / self.series_scale

        features = []
        targets = []
        for index in range(self.window, len(normalized)):
            features.append(normalized[index - self.window:index])
            targets.append(normalized[index])

        x_train = torch.tensor(np.array(features), dtype=torch.float32).unsqueeze(-1)
        y_train = torch.tensor(np.array(targets), dtype=torch.float32).unsqueeze(-1)

        self.model = _LSTMForecaster(self.hidden_size)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        loss_fn = nn.MSELoss()

        self.model.train()
        for _ in range(self.epochs):
            optimizer.zero_grad()
            predictions = self.model(x_train)
            loss = loss_fn(predictions, y_train)
            loss.backward()
            optimizer.step()

    def predict(self, horizon: int, history_frame) -> list[float]:
        if not self.history:
            raise RuntimeError("LSTM model must be fitted before prediction.")

        rolling = list(self.history)
        predictions: list[float] = []
        self.model.eval()

        for _ in range(horizon):
            window = np.array(rolling[-self.window:], dtype=float)
            normalized = (window - self.series_min) / self.series_scale
            x_input = torch.tensor(normalized, dtype=torch.float32).view(1, self.window, 1)
            with torch.no_grad():
                next_value = float(self.model(x_input).item())
            denormalized = (next_value * self.series_scale) + self.series_min
            predictions.append(denormalized)
            rolling.append(denormalized)

        return predictions

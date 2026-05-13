from __future__ import annotations

from datetime import timedelta

import pandas as pd

from utils.settings import get_settings


REQUIRED_COLUMNS = {"date", "open", "high", "low", "close", "volume"}
TARGET_COLUMN = "target"


def load_stock_frame(ticker: str) -> pd.DataFrame:
    settings = get_settings()
    csv_path = settings.uploads_dir / f"{ticker}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Ticker data not found for {ticker}.")

    frame = pd.read_csv(csv_path)
    frame.columns = [col.lower() for col in frame.columns]

    if not REQUIRED_COLUMNS.issubset(frame.columns):
        raise ValueError(f"{csv_path.name} must include {sorted(REQUIRED_COLUMNS)}.")

    frame["date"] = pd.to_datetime(frame["date"])
    frame = frame.sort_values("date").reset_index(drop=True)
    return frame


def engineer_features(frame: pd.DataFrame, include_target: bool = True) -> pd.DataFrame:
    df = frame.copy()
    df["return_1d"] = df["close"].pct_change()
    df["return_5d"] = df["close"].pct_change(periods=5)

    for lag in (1, 2, 3, 5, 7, 14):
        df[f"close_lag_{lag}"] = df["close"].shift(lag)

    for window in (3, 7, 14):
        df[f"rolling_mean_{window}"] = df["close"].rolling(window=window).mean()
        df[f"rolling_std_{window}"] = df["close"].rolling(window=window).std()
        df[f"momentum_{window}"] = df["close"] - df["close"].shift(window)

    df["volatility_7"] = df["return_1d"].rolling(window=7).std()
    df["volatility_14"] = df["return_1d"].rolling(window=14).std()
    df["range_pct"] = (df["high"] - df["low"]) / df["close"].replace(0, 1e-6)
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month

    if include_target:
        df[TARGET_COLUMN] = df["close"].shift(-1)

    return df.dropna().reset_index(drop=True)


def get_feature_columns(frame: pd.DataFrame) -> list[str]:
    excluded = {"date", "open", "high", "low", "close", "volume", TARGET_COLUMN}
    return [column for column in frame.columns if column not in excluded]


def train_validation_split(frame: pd.DataFrame, validation_size: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    if len(frame) <= validation_size + 20:
        raise ValueError("Not enough rows for training and validation.")
    return frame.iloc[:-validation_size].copy(), frame.iloc[-validation_size:].copy()


def next_trading_days(last_date: pd.Timestamp, horizon: int) -> list[pd.Timestamp]:
    dates: list[pd.Timestamp] = []
    cursor = last_date
    while len(dates) < horizon:
        cursor = cursor + timedelta(days=1)
        if cursor.weekday() < 5:
            dates.append(cursor)
    return dates


def append_prediction_row(history_frame: pd.DataFrame, next_date: pd.Timestamp, predicted_close: float) -> pd.DataFrame:
    last_row = history_frame.iloc[-1]
    row = {
        "date": next_date,
        "open": last_row["close"],
        "high": max(last_row["close"], predicted_close),
        "low": min(last_row["close"], predicted_close),
        "close": predicted_close,
        "volume": last_row["volume"],
    }
    return pd.concat([history_frame, pd.DataFrame([row])], ignore_index=True)

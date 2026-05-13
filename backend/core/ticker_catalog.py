from __future__ import annotations

from core.ticker_metadata import TICKER_KEYWORDS
from utils.settings import get_settings


def list_available_tickers() -> list[str]:
    settings = get_settings()
    upload_tickers = {
        path.stem.upper()
        for path in settings.uploads_dir.glob("*.csv")
        if path.is_file()
    }
    return sorted(upload_tickers | set(settings.supported_tickers))


def get_ticker_keywords(ticker: str | None) -> list[str]:
    if not ticker:
        return ["revenue", "growth", "margin", "guidance", "risk"]

    normalized = ticker.upper()
    return TICKER_KEYWORDS.get(
        normalized,
        [normalized.lower(), "revenue", "growth", "earnings", "margin", "guidance", "risk"],
    )

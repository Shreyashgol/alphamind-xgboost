from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = BACKEND_ROOT / "data"


load_dotenv(BACKEND_ROOT / ".env")


def _csv_env(name: str, default: list[str]) -> list[str]:
    raw_value = os.getenv(name)
    if not raw_value:
        return default
    values = [value.strip() for value in raw_value.split(",") if value.strip()]
    return values or default


class Settings:
    def __init__(self) -> None:
        config_path = BACKEND_ROOT / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}

        self.app_env = os.getenv("APP_ENV", "development")
        self.app_name = os.getenv("APP_NAME", config.get("app_name", "AlphaMind"))
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        self.cors_origins = tuple(
            _csv_env("CORS_ORIGINS", ["http://localhost:5173", "http://127.0.0.1:5173"])
        )

        self.default_horizon = int(os.getenv("DEFAULT_HORIZON", str(config.get("default_horizon", 7))))
        self.supported_tickers = tuple(
            _csv_env("SUPPORTED_TICKERS", config.get("supported_tickers", ["AAPL", "MSFT", "GOOGL", "TSLA"]))
        )
        self.knowledge_top_k = int(os.getenv("KNOWLEDGE_TOP_K", str(config.get("knowledge_top_k", 3))))

        self.uploads_dir = DATA_ROOT / "uploads"
        self.knowledge_dir = DATA_ROOT / "knowledge"
        self.faiss_dir = DATA_ROOT / "faiss_index"
        self.faiss_dir.mkdir(parents=True, exist_ok=True)
        self.faiss_index_path = self.faiss_dir / "knowledge.index"
        self.faiss_metadata_path = self.faiss_dir / "knowledge_metadata.json"

        self.embedding_model_name = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.default_recency_days = int(os.getenv("RAG_RECENCY_DAYS", "90"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

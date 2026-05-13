from __future__ import annotations

import json
from datetime import date, datetime, timedelta

import numpy as np

from utils.settings import get_settings

try:
    import faiss
except ImportError as exc:
    faiss = None
    _faiss_import_error = exc


class FaissVectorStore:
    def __init__(self) -> None:
        if faiss is None:
            raise RuntimeError("faiss-cpu is required for vector search.") from _faiss_import_error

        settings = get_settings()
        self.index_path = settings.faiss_index_path
        self.metadata_path = settings.faiss_metadata_path
        self.index = None
        self.metadata: list[dict] = []

    def exists(self) -> bool:
        return self.index_path.exists() and self.metadata_path.exists()

    def build(self, documents: list[dict], embeddings: np.ndarray) -> None:
        if len(documents) == 0:
            raise ValueError("Cannot build a FAISS index with zero documents.")

        dimension = int(embeddings.shape[1])
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(np.asarray(embeddings, dtype="float32"))
        self.metadata = documents
        faiss.write_index(self.index, str(self.index_path))
        self.metadata_path.write_text(json.dumps(documents, indent=2), encoding="utf-8")

    def load(self) -> None:
        if not self.exists():
            raise FileNotFoundError("FAISS index has not been built yet.")
        self.index = faiss.read_index(str(self.index_path))
        self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))

    def search(
        self,
        query_embedding: np.ndarray,
        *,
        top_k: int = 3,
        ticker: str | None = None,
        recency_days: int | None = None,
    ) -> list[dict]:
        if self.index is None:
            self.load()
        if self.index is None or not self.metadata:
            return []

        query = np.asarray(query_embedding, dtype="float32").reshape(1, -1)
        search_k = min(max(top_k * 8, top_k), len(self.metadata))
        scores, indices = self.index.search(query, search_k)

        threshold_date = None
        if recency_days is not None:
            threshold_date = date.today() - timedelta(days=recency_days)

        matches: list[dict] = []
        for score, index in zip(scores[0], indices[0], strict=False):
            if index < 0:
                continue
            document = self.metadata[index]
            if ticker and document.get("ticker") not in {None, ticker}:
                continue
            if threshold_date and not _is_recent_enough(document.get("date"), threshold_date):
                continue

            matches.append({"document": document, "score": float(score)})
            if len(matches) >= top_k:
                break

        return matches


def _is_recent_enough(raw_date: str | None, threshold_date: date) -> bool:
    if not raw_date:
        return True
    try:
        parsed = datetime.fromisoformat(raw_date).date()
    except ValueError:
        return True
    return parsed >= threshold_date

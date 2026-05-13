from __future__ import annotations

import numpy as np

from utils.settings import get_settings

try:
    from sentence_transformers import SentenceTransformer
except ImportError as exc:
    SentenceTransformer = None
    _sentence_transformer_import_error = exc


class SentenceTransformerEmbedder:
    def __init__(self) -> None:
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers is required for knowledge embeddings.") from _sentence_transformer_import_error
        self.model = SentenceTransformer(get_settings().embedding_model_name)

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(embeddings, dtype="float32")

    def embed_query(self, text: str) -> np.ndarray:
        embedding = self.model.encode([text], normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(embedding[0], dtype="float32")

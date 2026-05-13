from __future__ import annotations

import re
from datetime import datetime

from utils.settings import get_settings

try:
    from pypdf import PdfReader
except ImportError as exc:
    PdfReader = None
    _pdf_import_error = exc


CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def _extract_text(path) -> str:
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8").strip()

    if path.suffix.lower() == ".pdf":
        if PdfReader is None:
            raise RuntimeError("pypdf is required to load PDF knowledge files.") from _pdf_import_error
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages).strip()

    return ""


def _infer_ticker(path) -> str | None:
    stem = path.stem.upper()
    for ticker in get_settings().supported_tickers:
        if ticker in stem:
            return ticker
    return None


def _infer_date(path) -> str:
    match = re.search(r"(20\d{2}[-_](?:0[1-9]|1[0-2])[-_](?:0[1-9]|[12]\d|3[01]))", path.stem)
    if match:
        return match.group(1).replace("_", "-")
    return datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()


def _summarize(text: str) -> str:
    cleaned = " ".join(text.split())
    if not cleaned:
        return "No summary available."
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    return " ".join(sentences[:2])[:280].strip()


def _chunk_text(text: str) -> list[str]:
    normalized = " ".join(text.split())
    if len(normalized) <= CHUNK_SIZE:
        return [normalized] if normalized else []

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(len(normalized), start + CHUNK_SIZE)
        chunks.append(normalized[start:end])
        if end >= len(normalized):
            break
        start = max(0, end - CHUNK_OVERLAP)
    return chunks


def load_documents() -> list[dict]:
    settings = get_settings()
    documents: list[dict] = []

    for path in sorted(settings.knowledge_dir.glob("*")):
        if path.suffix.lower() not in {".pdf", ".txt"}:
            continue

        text = _extract_text(path)
        for index, chunk in enumerate(_chunk_text(text), start=1):
            documents.append(
                {
                    "id": f"{path.stem}-{index}",
                    "title": path.name,
                    "source": path.name,
                    "text": chunk,
                    "summary": _summarize(chunk),
                    "ticker": _infer_ticker(path),
                    "date": _infer_date(path),
                }
            )

    return documents

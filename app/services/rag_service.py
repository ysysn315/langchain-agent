
from __future__ import annotations

from app.core.settings import get_settings
from app.rag.indexing import index_file


def ingest_path(path: str) -> dict:
    settings = get_settings()
    return index_file(settings, path=path)

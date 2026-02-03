
from __future__ import annotations

from app.clients.dashscope_client import embed_texts
from app.core.settings import Settings


def embed_chunks(settings: Settings, chunks: list[str]) -> list[list[float]]:
    if not chunks:
        return []
    if not settings.dashscope_api_key:
        raise RuntimeError("DASHSCOPE_API_KEY is not configured")
    return embed_texts(api_key=settings.dashscope_api_key, model=settings.embedding_model, texts=chunks)

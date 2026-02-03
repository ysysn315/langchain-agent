from __future__ import annotations

from app.clients.dashscope_client import embed_texts
from app.core.settings import Settings
from langchain_core.embeddings import Embeddings


class DashScopeEmbeddings(Embeddings):
    def __init__(self, *, settings: Settings) -> None:
        self._settings = settings

    def _embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if not self._settings.dashscope_api_key:
            raise RuntimeError("DASHSCOPE_API_KEY is not configured")
        return embed_texts(
            api_key=self._settings.dashscope_api_key,
            model=self._settings.embedding_model,
            texts=texts,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> list[float]:
        vecs = self._embed([text])
        return vecs[0] if vecs else []

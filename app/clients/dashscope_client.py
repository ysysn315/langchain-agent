
from __future__ import annotations

from dashscope import TextEmbedding


def embed_texts(*, api_key: str, model: str, texts: list[str]) -> list[list[float]]:
    resp = TextEmbedding.call(model=model, input=texts, api_key=api_key)
    if not getattr(resp, "output", None) or not getattr(resp.output, "embeddings", None):
        raise RuntimeError(f"DashScope embedding failed: {getattr(resp, 'message', None) or resp}")

    vectors: list[list[float]] = []
    for item in resp.output.embeddings:
        vectors.append(item.embedding)
    return vectors

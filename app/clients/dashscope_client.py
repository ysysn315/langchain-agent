
from __future__ import annotations

from dashscope import Generation, TextEmbedding
from dashscope.api_entities.dashscope_response import Message


def embed_texts(*, api_key: str, model: str, texts: list[str]) -> list[list[float]]:
    resp = TextEmbedding.call(model=model, input=texts, api_key=api_key)
    if hasattr(resp, "get"):
        status_code = resp.get("status_code")
        if status_code not in (None, 200):
            raise RuntimeError(
                f"DashScope embedding failed: status_code={status_code} message={resp.get('message')} request_id={resp.get('request_id')}"
            )

        output = resp.get("output")
        if isinstance(output, dict) and isinstance(output.get("embeddings"), list):
            vectors: list[list[float]] = []
            for item in output["embeddings"]:
                if isinstance(item, dict) and isinstance(item.get("embedding"), list):
                    vectors.append(item["embedding"])
            if vectors:
                return vectors

    output = getattr(resp, "output", None)
    embeddings = getattr(output, "embeddings", None) if output is not None else None
    if isinstance(embeddings, list) and embeddings:
        vectors: list[list[float]] = []
        for item in embeddings:
            if hasattr(item, "embedding"):
                vectors.append(item.embedding)
        if vectors:
            return vectors

    raise RuntimeError("DashScope embedding failed: unexpected response format")


def _extract_generation_text(resp: object) -> str:
    if hasattr(resp, "get"):
        output = resp.get("output")
        if isinstance(output, dict):
            if isinstance(output.get("text"), str) and output.get("text"):
                return output["text"]
            choices = output.get("choices")
            if isinstance(choices, list) and choices:
                c0 = choices[0]
                if isinstance(c0, dict):
                    message = c0.get("message")
                    if isinstance(message, dict) and isinstance(message.get("content"), str):
                        return message["content"]
                    if isinstance(c0.get("text"), str):
                        return c0["text"]

        if isinstance(resp.get("text"), str) and resp.get("text"):
            return resp["text"]

    if hasattr(resp, "output"):
        output = getattr(resp, "output")
        if hasattr(output, "text") and isinstance(getattr(output, "text"), str):
            return getattr(output, "text")

    raise RuntimeError(f"DashScope generation response parse failed: {resp}")


def chat(
    *,
    api_key: str,
    model: str,
    messages: list[dict],
) -> str:
    ds_messages = [Message(role=m["role"], content=m["content"]) for m in messages]
    resp = Generation.call(model=model, messages=ds_messages, api_key=api_key)
    if hasattr(resp, "get") and resp.get("status_code") not in (None, 200):
        raise RuntimeError(f"DashScope generation failed: {resp.get('message') or resp}")
    return _extract_generation_text(resp)

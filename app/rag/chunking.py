
from __future__ import annotations


def chunk_text(*, text: str, max_size: int, overlap: int) -> list[str]:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    if not cleaned.strip():
        return []

    if max_size <= 0:
        return [cleaned]

    if overlap < 0:
        overlap = 0
    if overlap >= max_size:
        overlap = max(0, max_size // 5)

    chunks: list[str] = []
    start = 0
    n = len(cleaned)
    while start < n:
        end = min(n, start + max_size)
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

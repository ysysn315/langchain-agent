from __future__ import annotations

from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    saved_path: str
    size_bytes: int

    ingest_status: str | None = None
    ingested_chunks: int | None = None
    error: str | None = None

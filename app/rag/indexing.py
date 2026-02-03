
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.core.settings import Settings
from app.rag.chunking import chunk_text
from app.rag.embeddings import embed_chunks
from app.rag.vector_store import insert_chunks


def index_file(settings: Settings, *, path: str) -> dict:
    p = Path(path)
    raw = p.read_bytes()
    text = raw.decode("utf-8", errors="ignore")

    chunks = chunk_text(text=text, max_size=settings.doc_chunk_max_size, overlap=settings.doc_chunk_overlap)
    if not chunks:
        return {"ingest_status": "skipped", "ingested_chunks": 0}

    vectors = embed_chunks(settings, chunks)
    ids = [str(uuid4()) for _ in chunks]
    metadatas = [{"_source": str(p)} for _ in chunks]
    inserted = insert_chunks(settings, vectors=vectors, contents=chunks, metadatas=metadatas, ids=ids)
    return {"ingest_status": "ok", "ingested_chunks": inserted}

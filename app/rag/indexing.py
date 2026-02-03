from __future__ import annotations

from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from app.core.settings import Settings
from app.rag.chunking import chunk_text
from app.rag.vector_store import delete_by_source, insert_texts

from langchain_community.document_loaders import TextLoader


def index_file(settings: Settings, *, path: str) -> dict:
    p = Path(path)

    docs = TextLoader(p, encoding="utf-8", autodetect_encoding=True).load()
    text = "\n".join([d.page_content for d in docs if getattr(d, "page_content", None)])

    chunks = chunk_text(text=text, max_size=settings.doc_chunk_max_size, overlap=settings.doc_chunk_overlap)
    if not chunks:
        return {"ingest_status": "skipped", "ingested_chunks": 0}

    source = str(p.resolve()).replace("\\", "/")
    delete_by_source(settings, source=source)

    total = len(chunks)
    ids = [str(uuid5(NAMESPACE_URL, f"{source}:{i}")) for i in range(total)]
    metadatas = [
        {
            "id": ids[i],
            "_source": source,
            "chunkIndex": i,
            "totalChunks": total,
            "_file_name": p.name,
            "_extension": p.suffix,
        }
        for i in range(total)
    ]
    inserted = insert_texts(settings, contents=chunks, metadatas=metadatas, ids=ids)
    return {"ingest_status": "ok", "ingested_chunks": inserted}

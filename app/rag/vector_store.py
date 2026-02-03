from __future__ import annotations

import inspect
from typing import Any

from app.core.settings import Settings
from app.rag.embeddings import DashScopeEmbeddings

try:
    from langchain_milvus import Milvus
except Exception:  # pragma: no cover
    from langchain_community.vectorstores import Milvus


def _connection_args(settings: Settings) -> dict[str, Any]:
    uri = f"http://{settings.milvus_host}:{settings.milvus_port}"
    args: dict[str, Any] = {
        "uri": uri,
        "db_name": settings.milvus_db,
    }
    if settings.milvus_username:
        args["user"] = settings.milvus_username
    if settings.milvus_password:
        args["password"] = settings.milvus_password
    return args


def _get_store(settings: Settings) -> Milvus:
    kwargs: dict[str, Any] = {
        "embedding_function": DashScopeEmbeddings(settings=settings),
        "collection_name": settings.milvus_collection,
        "connection_args": _connection_args(settings),
        "index_params": {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}},
        "search_params": {"metric_type": "L2", "params": {"nprobe": 10}},
        "drop_old": False,
        "auto_id": False,
        "primary_field": "id",
        "text_field": "content",
        "vector_field": "vector",
        "metadata_field": "metadata",
    }
    try:
        sig = inspect.signature(Milvus.__init__)
        kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    except Exception:
        pass
    return Milvus(**kwargs)


def insert_texts(
    settings: Settings,
    *,
    contents: list[str],
    metadatas: list[dict],
    ids: list[str],
) -> int:
    if not contents:
        return 0
    store = _get_store(settings)
    inserted_ids = store.add_texts(texts=contents, metadatas=metadatas, ids=ids, batch_size=10)
    return len(inserted_ids)


def delete_by_source(settings: Settings, *, source: str) -> int:
    normalized = source.replace("\\", "/")
    expr = f'metadata["_source"] == "{normalized}"'
    try:
        store = _get_store(settings)
        res = store.delete(expr=expr)
        delete_count = getattr(res, "delete_count", None)
        if isinstance(delete_count, int):
            return delete_count
    except Exception:
        return 0
    return 0


def search_similar(settings: Settings, *, query: str, top_k: int = 3) -> list[dict[str, Any]]:
    store = _get_store(settings)
    docs = store.similarity_search_with_score(query=query, k=max(1, int(top_k)))

    hits: list[dict[str, Any]] = []
    for doc, score in docs:
        meta = getattr(doc, "metadata", None)
        doc_id = getattr(doc, "id", None)
        hit_id = ""
        if isinstance(meta, dict) and isinstance(meta.get("id"), str):
            hit_id = meta.get("id") or ""
        elif isinstance(doc_id, str):
            hit_id = doc_id
        hits.append(
            {
                "id": hit_id,
                "score": float(score),
                "content": getattr(doc, "page_content", None),
                "metadata": meta if isinstance(meta, dict) else None,
            }
        )
    return hits

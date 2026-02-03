
from __future__ import annotations

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from app.core.settings import Settings


def _connect(settings: Settings) -> None:
    uri = f"http://{settings.milvus_host}:{settings.milvus_port}"
    connections.connect(
        alias="default",
        uri=uri,
        user=settings.milvus_username,
        password=settings.milvus_password,
        db_name=settings.milvus_db,
    )


def ensure_collection(settings: Settings, *, dim: int) -> Collection:
    _connect(settings)
    name = settings.milvus_collection

    if not utility.has_collection(name):
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=128),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.JSON),
        ]
        schema = CollectionSchema(fields=fields, description="docs")
        col = Collection(name=name, schema=schema)
        col.create_index(
            field_name="vector",
            index_params={"index_type": "HNSW", "metric_type": "IP", "params": {"M": 16, "efConstruction": 200}},
        )
        col.load()
        return col

    col = Collection(name)
    field = next((f for f in col.schema.fields if f.name == "vector"), None)
    if not field or getattr(field, "dim", None) != dim:
        raise RuntimeError(f"Milvus collection '{name}' vector dim mismatch: expected={dim}")
    col.load()
    return col


def insert_chunks(
    settings: Settings,
    *,
    vectors: list[list[float]],
    contents: list[str],
    metadatas: list[dict],
    ids: list[str],
) -> int:
    if not vectors:
        return 0
    col = ensure_collection(settings, dim=len(vectors[0]))
    data = [ids, vectors, contents, metadatas]
    result = col.insert(data)
    col.flush()
    return len(result.primary_keys)

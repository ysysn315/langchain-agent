
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_port: int = 9900
    upload_dir: str = "./uploads"

    dashscope_api_key: str | None = None
    embedding_model: str = "text-embedding-v4"

    doc_chunk_max_size: int = 800
    doc_chunk_overlap: int = 100

    milvus_host: str = "localhost"
    milvus_port: int = 19530
    milvus_username: str | None = None
    milvus_password: str | None = None
    milvus_db: str = "default"
    milvus_collection: str = "docs"


@lru_cache
def get_settings() -> Settings:
    return Settings()

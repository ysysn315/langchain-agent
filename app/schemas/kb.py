from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class KBHit(BaseModel):
    content: str | None = None
    metadata: dict | None = None
    score: float | None = None


class KBSearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    query: str
    top_k: int = Field(default=3, validation_alias=AliasChoices("topK", "top_k"))


class KBSearchResponse(BaseModel):
    hits: list[KBHit] = Field(default_factory=list)


class KBAskRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    question: str = Field(validation_alias=AliasChoices("question", "Question"))
    top_k: int = Field(default=3, validation_alias=AliasChoices("topK", "top_k"))


class KBAskResponse(BaseModel):
    answer: str | None = None
    hits: list[KBHit] = Field(default_factory=list)


class KBIndexDirectoryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    directory_path: str | None = Field(
        default=None,
        validation_alias=AliasChoices("directoryPath", "directory_path", "path"),
        serialization_alias="directoryPath",
    )


class KBIndexDirectoryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    directory_path: str = Field(serialization_alias="directoryPath")
    total_files: int = Field(serialization_alias="totalFiles")
    success_count: int = Field(serialization_alias="successCount")
    fail_count: int = Field(serialization_alias="failCount")
    failed_files: dict[str, str] = Field(default_factory=dict, serialization_alias="failedFiles")

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AiOpsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str | None = Field(default=None, alias="id")
    query: str


class AiOpsResponse(BaseModel):
    report_markdown: str

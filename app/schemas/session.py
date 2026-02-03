from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ClearSessionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(alias="id")


class SessionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(alias="id")
    history: list[dict]

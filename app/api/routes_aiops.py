
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class AiOpsRequest(BaseModel):
    query: str
    session_id: str | None = None


class AiOpsResponse(BaseModel):
    report_markdown: str


@router.post("/ai_ops", response_model=AiOpsResponse)
async def ai_ops(req: AiOpsRequest) -> AiOpsResponse:
    report = "# AIOps 报告\n\nTODO\n"
    return AiOpsResponse(report_markdown=report)

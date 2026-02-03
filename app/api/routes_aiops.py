
from __future__ import annotations

from fastapi import APIRouter

from app.schemas.aiops import AiOpsRequest, AiOpsResponse
from app.schemas.common import ApiResponse

router = APIRouter()


@router.post("/ai_ops", response_model=ApiResponse)
async def ai_ops(req: AiOpsRequest) -> ApiResponse:
    report = "# AIOps 报告\n\nTODO\n"
    payload = AiOpsResponse(report_markdown=report).model_dump()
    return ApiResponse.ok(payload)

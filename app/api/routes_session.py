
from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.schemas.session import ClearSessionRequest, SessionResponse
from app.services.session_store import store


router = APIRouter()


@router.post("/chat/clear")
async def clear_session(req: ClearSessionRequest) -> ApiResponse:
    store.clear(req.session_id)
    return ApiResponse.ok({"status": "ok"})


@router.get("/chat/session/{session_id}", response_model=ApiResponse)
async def get_session(session_id: str) -> ApiResponse:
    payload = SessionResponse(session_id=session_id, history=store.get_history(session_id)).model_dump(by_alias=True)
    return ApiResponse.ok(payload)

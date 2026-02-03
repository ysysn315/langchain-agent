
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.session_store import store


router = APIRouter()


class ClearSessionRequest(BaseModel):
    session_id: str


class SessionResponse(BaseModel):
    session_id: str
    history: list[dict]


@router.post("/chat/clear")
async def clear_session(req: ClearSessionRequest) -> dict:
    store.clear(req.session_id)
    return {"status": "ok"}


@router.get("/chat/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    return SessionResponse(session_id=session_id, history=store.get_history(session_id))

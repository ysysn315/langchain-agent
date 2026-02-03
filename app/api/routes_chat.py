
from __future__ import annotations

import asyncio
from typing import AsyncIterator
from uuid import uuid4

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.common import ApiResponse
from app.services.chat_service import answer as answer_question


router = APIRouter()


@router.post("/chat", response_model=ApiResponse)
async def chat(req: ChatRequest) -> ApiResponse:
    session_id = req.session_id or str(uuid4())
    try:
        answer = answer_question(session_id=session_id, question=req.question)
    except Exception as e:
        return ApiResponse.fail(str(e))
    payload = ChatResponse(session_id=session_id, answer=answer).model_dump(by_alias=True)
    return ApiResponse.ok(payload)


@router.post("/chat_stream")
async def chat_stream(req: ChatRequest) -> EventSourceResponse:
    session_id = req.session_id or str(uuid4())

    async def event_generator() -> AsyncIterator[dict]:
        parts = ["T", "O", "D", "O"]
        for p in parts:
            await asyncio.sleep(0.05)
            yield {"event": "message", "data": p}
        yield {"event": "done", "data": session_id}

    return EventSourceResponse(event_generator())

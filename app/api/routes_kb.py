from __future__ import annotations

from fastapi import APIRouter

from app.agents.knowledge_base_agent import ask
from app.core.settings import get_settings
from app.schemas.common import ApiResponse
from app.schemas.kb import (
    KBAskRequest,
    KBAskResponse,
    KBHit,
    KBIndexDirectoryRequest,
    KBIndexDirectoryResponse,
    KBSearchRequest,
    KBSearchResponse,
)
from app.services.vector_index_service import VectorIndexService


router = APIRouter()


@router.post("/kb/index_directory", response_model=ApiResponse)
async def kb_index_directory(req: KBIndexDirectoryRequest) -> ApiResponse:
    settings = get_settings()
    svc = VectorIndexService(settings)
    try:
        res = svc.index_directory(req.directory_path)
        payload = KBIndexDirectoryResponse(
            directory_path=res.directory_path,
            total_files=res.total_files,
            success_count=res.success_count,
            fail_count=res.fail_count,
            failed_files=res.failed_files,
        ).model_dump(by_alias=True)
        return ApiResponse.ok(payload)
    except Exception as e:
        return ApiResponse.fail(str(e))


@router.post("/kb/search", response_model=ApiResponse)
async def kb_search(req: KBSearchRequest) -> ApiResponse:
    settings = get_settings()
    svc = VectorIndexService(settings)
    try:
        raw_hits = svc.search(query=req.query, top_k=req.top_k)
        hits = [KBHit(content=h.get("content"), metadata=h.get("metadata"), score=h.get("score")) for h in raw_hits]
        payload = KBSearchResponse(hits=hits).model_dump()
        return ApiResponse.ok(payload)
    except Exception as e:
        return ApiResponse.fail(str(e))


@router.post("/kb/ask", response_model=ApiResponse)
async def kb_ask(req: KBAskRequest) -> ApiResponse:
    try:
        out = ask(question=req.question, top_k=req.top_k)
        hits = [KBHit(content=h.get("content"), metadata=h.get("metadata"), score=h.get("score")) for h in out.get("hits", [])]
        payload = KBAskResponse(answer=out.get("answer"), hits=hits).model_dump()
        return ApiResponse.ok(payload)
    except Exception as e:
        return ApiResponse.fail(str(e))

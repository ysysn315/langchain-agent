
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, UploadFile

from app.core.settings import get_settings
from app.schemas.common import ApiResponse
from app.schemas.upload import UploadResponse
from app.services.rag_service import ingest_path


router = APIRouter()


@router.post("/upload", response_model=ApiResponse)
async def upload(file: UploadFile = File(...)) -> ApiResponse:
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    dest = upload_dir / (file.filename or "upload.bin")
    data = await file.read()
    dest.write_bytes(data)
    extra: dict = {}
    try:
        extra = ingest_path(str(dest))
    except Exception as e:
        extra = {"ingest_status": "failed", "ingested_chunks": 0, "error": str(e)}

    payload = UploadResponse(
        filename=dest.name,
        saved_path=str(dest),
        size_bytes=len(data),
        ingest_status=extra.get("ingest_status"),
        ingested_chunks=extra.get("ingested_chunks"),
        error=extra.get("error"),
    ).model_dump()
    return ApiResponse.ok(payload)

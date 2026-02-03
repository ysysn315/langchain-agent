
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

from app.core.settings import get_settings


router = APIRouter()


class UploadResponse(BaseModel):
    filename: str
    saved_path: str
    size_bytes: int


@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)) -> UploadResponse:
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    dest = upload_dir / (file.filename or "upload.bin")
    data = await file.read()
    dest.write_bytes(data)
    return UploadResponse(filename=dest.name, saved_path=str(dest), size_bytes=len(data))


from fastapi import FastAPI

from app.api.routes_aiops import router as aiops_router
from app.api.routes_chat import router as chat_router
from app.api.routes_kb import router as kb_router
from app.api.routes_session import router as session_router
from app.api.routes_upload import router as upload_router


app = FastAPI(title="langchain-agent")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(chat_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(kb_router, prefix="/api")
app.include_router(aiops_router, prefix="/api")
app.include_router(session_router, prefix="/api")

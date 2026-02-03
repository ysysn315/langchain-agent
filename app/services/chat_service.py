
from __future__ import annotations

from app.clients.dashscope_client import chat as dashscope_chat
from app.core.settings import get_settings
from app.services.session_store import store


def answer(*, session_id: str, question: str) -> str:
    settings = get_settings()
    if not settings.dashscope_api_key:
        raise RuntimeError("DASHSCOPE_API_KEY is not configured")

    store.append(session_id, role="user", content=question)
    history = store.get_history(session_id)

    messages: list[dict] = []
    for item in history[-20:]:
        role = item.get("role")
        content = item.get("content")
        if role in ("user", "assistant") and isinstance(content, str):
            messages.append({"role": role, "content": content})

    if not messages:
        messages = [{"role": "user", "content": question}]

    answer_text = dashscope_chat(api_key=settings.dashscope_api_key, model=settings.chat_model, messages=messages)
    store.append(session_id, role="assistant", content=answer_text)
    return answer_text

from __future__ import annotations

from app.core.settings import get_settings
from app.services.vector_index_service import VectorIndexService

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def ask(*, question: str, top_k: int = 3) -> dict:
    settings = get_settings()
    svc = VectorIndexService(settings)
    hits = svc.search(query=question, top_k=top_k)

    ctx_parts: list[str] = []
    for h in hits:
        meta = h.get("metadata")
        src = meta.get("_source") if isinstance(meta, dict) else None
        content = h.get("content") or ""
        if src:
            ctx_parts.append(f"[source={src}]\n{content}")
        else:
            ctx_parts.append(content)

    context = "\n\n".join([p for p in ctx_parts if p.strip()])

    llm = ChatTongyi(model=settings.chat_model, api_key=settings.dashscope_api_key)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You answer questions based only on the provided context. If the context is insufficient, say you don't know.",
            ),
            ("human", "Context:\n{context}\n\nQuestion: {question}"),
        ]
    )
    chain = prompt | llm | StrOutputParser()
    answer_text = chain.invoke({"context": context, "question": question})

    return {"answer": answer_text, "hits": hits}

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int = 0
    msg: str = "ok"
    data: Any | None = None

    @classmethod
    def ok(cls, data: Any | None = None) -> "ApiResponse":
        return cls(code=0, msg="ok", data=data)

    @classmethod
    def fail(cls, msg: str, code: int = 1, data: Any | None = None) -> "ApiResponse":
        return cls(code=code, msg=msg, data=data)

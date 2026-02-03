
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class InMemorySessionStore:
    _sessions: dict[str, list[dict]] = field(default_factory=dict)

    def get_history(self, session_id: str) -> list[dict]:
        return list(self._sessions.get(session_id, []))

    def append(self, session_id: str, role: str, content: str) -> None:
        self._sessions.setdefault(session_id, []).append(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "role": role,
                "content": content,
            }
        )

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


store = InMemorySessionStore()

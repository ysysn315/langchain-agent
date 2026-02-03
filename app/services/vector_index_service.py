from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.settings import Settings, get_settings
from app.rag.indexing import index_file
from app.rag.vector_store import search_similar


@dataclass
class IndexDirectoryResult:
    directory_path: str
    total_files: int
    success_count: int
    fail_count: int
    failed_files: dict[str, str]


class VectorIndexService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def index_directory(self, directory_path: str | None = None) -> IndexDirectoryResult:
        target = Path(directory_path or self._settings.upload_dir).resolve()
        if not target.exists() or not target.is_dir():
            raise ValueError(f"Directory not found or not a directory: {target}")

        files = [p for p in target.iterdir() if p.is_file() and p.suffix.lower() in {".txt", ".md"}]

        failed: dict[str, str] = {}
        ok = 0
        for p in files:
            try:
                self.index_single_file(str(p))
                ok += 1
            except Exception as e:
                failed[str(p)] = str(e)

        return IndexDirectoryResult(
            directory_path=str(target),
            total_files=len(files),
            success_count=ok,
            fail_count=len(failed),
            failed_files=failed,
        )

    def index_single_file(self, file_path: str) -> dict:
        return index_file(self._settings, path=file_path)

    def _dedup_hits_by_source(self, hits: list[dict], *, top_k: int, max_per_source: int = 2) -> list[dict]:
        seen_ids: set[str] = set()
        per_source: dict[str, int] = {}
        out: list[dict] = []

        target = max(1, int(top_k))
        cap = max(1, int(max_per_source))

        def _hit_id(hit: dict) -> str:
            return str(hit.get("id", ""))

        def _hit_source(hit: dict) -> str | None:
            meta = hit.get("metadata")
            if isinstance(meta, dict):
                src = meta.get("_source")
                if isinstance(src, str) and src:
                    return src
            return None

        for h in hits:
            hid = _hit_id(h)
            if not hid or hid in seen_ids:
                continue
            src = _hit_source(h)
            if src:
                cnt = per_source.get(src, 0)
                if cnt >= cap:
                    continue
                per_source[src] = cnt + 1
            seen_ids.add(hid)
            out.append(h)
            if len(out) >= target:
                return out

        for h in hits:
            if len(out) >= target:
                break
            hid = _hit_id(h)
            if not hid or hid in seen_ids:
                continue
            seen_ids.add(hid)
            out.append(h)

        return out

    def search(self, *, query: str, top_k: int = 3) -> list[dict]:
        target = max(1, int(top_k))
        oversample = min(50, max(target, target * 5))
        raw = search_similar(self._settings, query=query, top_k=oversample)
        return self._dedup_hits_by_source(raw, top_k=target)

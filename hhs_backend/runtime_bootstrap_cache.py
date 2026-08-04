"""Persistent stale-while-revalidate cache for HHS runtime status projections."""
from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class CacheLookup:
    path: str
    payload: dict[str, Any] | None
    state: str
    age_ms: int | None


class RuntimeStatusCache:
    """Thread-safe persistent cache whose values are never canonical authority."""

    SCHEMA = "HHS_RUNTIME_BOOTSTRAP_CACHE_V1"

    def __init__(self, path: str | os.PathLike[str], *, ttl_seconds: float = 15.0) -> None:
        self.path = Path(path)
        self.ttl_seconds = max(0.1, float(ttl_seconds))
        self._lock = threading.RLock()
        self._entries: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError, TypeError):
            return
        entries = raw.get("entries") if isinstance(raw, dict) else None
        if not isinstance(entries, dict):
            return
        with self._lock:
            self._entries = {
                str(key): dict(value)
                for key, value in entries.items()
                if isinstance(value, Mapping) and isinstance(value.get("payload"), Mapping)
            }

    def _persist_locked(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "schema": self.SCHEMA,
            "written_unix_ns": time.time_ns(),
            "entries": self._entries,
        }
        encoded = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        fd, temporary = tempfile.mkstemp(prefix="status-cache-", suffix=".json", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass

    def put(
        self,
        path: str,
        payload: Mapping[str, Any],
        *,
        status_code: int = 200,
        duration_ms: int | None = None,
    ) -> None:
        entry = {
            "payload": dict(payload),
            "status_code": int(status_code),
            "updated_unix_ns": time.time_ns(),
            "duration_ms": None if duration_ms is None else int(duration_ms),
        }
        with self._lock:
            self._entries[str(path)] = entry
            self._persist_locked()

    def lookup(self, path: str) -> CacheLookup:
        now_ns = time.time_ns()
        with self._lock:
            entry = self._entries.get(path)
            if not entry:
                return CacheLookup(path=path, payload=None, state="MISS", age_ms=None)
            age_ms = max(0, (now_ns - int(entry.get("updated_unix_ns", now_ns))) // 1_000_000)
            state = "HIT" if age_ms <= int(self.ttl_seconds * 1000) else "STALE"
            return CacheLookup(
                path=path,
                payload=dict(entry["payload"]),
                state=state,
                age_ms=int(age_ms),
            )

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            entries = {}
            for path in sorted(self._entries):
                lookup = self.lookup(path)
                entries[path] = {
                    "state": lookup.state,
                    "age_ms": lookup.age_ms,
                    "payload": lookup.payload,
                }
            return {
                "schema": self.SCHEMA,
                "ttl_seconds": self.ttl_seconds,
                "entry_count": len(entries),
                "entries": entries,
            }

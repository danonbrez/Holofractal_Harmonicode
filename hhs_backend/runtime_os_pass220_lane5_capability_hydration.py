"""Pass 220 host lifecycle for the Pass 219 Lane 5 1.76 capability manifold.

Pass 220 provides the Ubuntu/FastAPI host.  It does not own capability
selection.  This lifecycle warms the Pass 219 candidate-only Hash216 knowledge
projection after FastAPI startup and exposes read-only status/search surfaces.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import json
import os
from pathlib import Path
import sqlite3
import tempfile
from typing import Any

from hhs_backend.runtime.hhs_pass219_lane5_global_capability_visibility_1_76 import (
    build_global_capability_visibility,
    hydrate_hash216_vector_database,
)

STATUS_PATH = "/api/runtime/pass219/lane5/capabilities/status"
SUMMARY_PATH = "/api/runtime/pass219/lane5/capabilities/summary"
SEARCH_PATH = "/api/runtime/pass219/lane5/capabilities/search"
APP_STATE_KEY = "hhs_pass219_lane5_global_capability_visibility_1_76"


def _truthy(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def resolve_repository_root() -> Path:
    explicit = os.environ.get("HHS_REPOSITORY_ROOT")
    if explicit:
        return Path(explicit).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def resolve_state_root() -> Path:
    explicit = os.environ.get("HHS_PASS219_LANE5_CAPABILITY_STATE_ROOT")
    if explicit:
        return Path(explicit).expanduser().resolve()
    data_root = os.environ.get("HHS_DATA_DIR")
    if data_root:
        return (Path(data_root).expanduser().resolve() / "pass219-lane5-capabilities").resolve()
    return (Path(tempfile.gettempdir()) / "hhs-pass219-lane5-capabilities").resolve()


def _route_exists(app: Any, path: str) -> bool:
    return any(str(getattr(route, "path", "")) == path for route in app.router.routes)


class Pass219Lane5CapabilityVisibilityLifecycle:
    def __init__(
        self,
        *,
        repository_root: str | os.PathLike[str] | None = None,
        state_root: str | os.PathLike[str] | None = None,
        main_ref: str | None = None,
        include_refs: bool | None = None,
    ) -> None:
        self.repository_root = Path(
            repository_root if repository_root is not None else resolve_repository_root()
        ).resolve()
        self.state_root = Path(
            state_root if state_root is not None else resolve_state_root()
        ).resolve()
        self.main_ref = main_ref or os.environ.get("HHS_PASS219_LANE5_MAIN_REF", "HEAD")
        self.include_refs = (
            _truthy("HHS_PASS219_LANE5_INCLUDE_REFS", True)
            if include_refs is None
            else bool(include_refs)
        )
        self._started = False
        self._warming = False
        self._summary: dict[str, Any] | None = None
        self._database: dict[str, Any] | None = None
        self._failure: dict[str, str] | None = None

    @property
    def database_path(self) -> Path:
        return self.state_root / "lane5-global-capability-visibility-1.76.sqlite3"

    @property
    def receipt_path(self) -> Path:
        return self.state_root / "lane5-global-capability-visibility-1.76.receipt.json"

    def startup(self) -> dict[str, Any]:
        self._started = True
        self._warming = True
        self.state_root.mkdir(parents=True, exist_ok=True)
        try:
            snapshot = build_global_capability_visibility(
                self.repository_root,
                main_ref=self.main_ref,
                include_refs=self.include_refs,
            )
            database = hydrate_hash216_vector_database(snapshot, self.database_path)
            summary = {
                "schema": str(snapshot["schema"]),
                "main_ref": str(snapshot["main_ref"]),
                "main_commit": str(snapshot["main_commit"]),
                "counts": dict(snapshot["counts"]),
                "node_root_hash216": str(snapshot["node_root_hash216"]),
                "snapshot_root_hash216": str(snapshot["snapshot_root_hash216"]),
                "invariants": dict(snapshot["invariants"]),
                "authority": dict(snapshot["authority"]),
            }
            payload = {
                "schema": "HHS_PASS_219_LANE5_GLOBAL_CAPABILITY_VISIBILITY_HOST_RECEIPT_1_76",
                "summary": summary,
                "database": database,
                "pass220_host_only": True,
                "lane5_selection_authority": False,
                "runtime_validation_authority": False,
                "canonical_mutation_authority": False,
            }
            tmp = self.receipt_path.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            os.replace(tmp, self.receipt_path)
            self._summary = summary
            self._database = database
            self._failure = None
        except Exception as exc:
            self._summary = None
            self._database = None
            self._failure = {
                "failure_type": type(exc).__name__,
                "reason": str(exc),
            }
        finally:
            self._warming = False
        return self.status()

    def status(self) -> dict[str, Any]:
        ready = self._summary is not None and self._database is not None
        if ready:
            state = "READY"
        elif self._warming:
            state = "WARMING_NONBLOCKING"
        elif self._started:
            state = "UNAVAILABLE"
        else:
            state = "NOT_STARTED"
        return {
            "schema": "HHS_PASS_219_LANE5_GLOBAL_CAPABILITY_VISIBILITY_HOST_STATUS_1_76",
            "state": state,
            "started": self._started,
            "warming": self._warming,
            "available_to_lane5": ready,
            "repository_root": str(self.repository_root),
            "state_root": str(self.state_root),
            "main_ref": self.main_ref,
            "include_refs": self.include_refs,
            "snapshot_root_hash216": (
                str(self._summary["snapshot_root_hash216"]) if ready else None
            ),
            "node_count": (
                int(self._database["node_count"]) if ready else 0
            ),
            "hash216_vector_positions": (
                int(self._database["hash216_vector_positions"]) if ready else 0
            ),
            "pass220_host_only": True,
            "lane5_selection_authority": False,
            "runtime_validation_authority": False,
            "canonical_mutation_authority": False,
            "failure": dict(self._failure or {}),
        }

    def summary(self) -> dict[str, Any]:
        if self._summary is None:
            raise RuntimeError("PASS219_LANE5_GLOBAL_CAPABILITY_VISIBILITY_NOT_READY")
        return dict(self._summary)

    def search(self, query: str, *, limit: int = 20) -> dict[str, Any]:
        if self._database is None:
            raise RuntimeError("PASS219_LANE5_GLOBAL_CAPABILITY_VISIBILITY_NOT_READY")
        bounded_limit = min(100, max(1, int(limit)))
        term = str(query or "").strip()
        pattern = f"%{term}%"
        connection = sqlite3.connect(self.database_path)
        try:
            rows = connection.execute(
                "SELECT payload_json FROM capability_nodes "
                "WHERE payload_json LIKE ? ORDER BY node_id LIMIT ?",
                (pattern, bounded_limit),
            ).fetchall()
        finally:
            connection.close()
        results = [json.loads(row[0]) for row in rows]
        return {
            "schema": "HHS_PASS_219_LANE5_GLOBAL_CAPABILITY_VISIBILITY_SEARCH_1_76",
            "query": term,
            "limit": bounded_limit,
            "result_count": len(results),
            "results": results,
            "read_only_projection": True,
            "lane5_selection_authority": False,
            "canonical_mutation_authority": False,
        }


def install_pass219_lane5_capability_visibility(
    app: Any,
    *,
    repository_root: str | os.PathLike[str] | None = None,
    state_root: str | os.PathLike[str] | None = None,
) -> Pass219Lane5CapabilityVisibilityLifecycle:
    existing = getattr(app.state, APP_STATE_KEY, None)
    if isinstance(existing, Pass219Lane5CapabilityVisibilityLifecycle):
        return existing

    lifecycle = Pass219Lane5CapabilityVisibilityLifecycle(
        repository_root=repository_root,
        state_root=state_root,
    )
    setattr(app.state, APP_STATE_KEY, lifecycle)

    if not _route_exists(app, STATUS_PATH):
        async def status() -> dict[str, Any]:
            return lifecycle.status()
        app.add_api_route(
            STATUS_PATH,
            status,
            methods=["GET", "HEAD"],
            name="pass219-lane5-global-capability-status-1-76",
        )

    if not _route_exists(app, SUMMARY_PATH):
        async def summary() -> dict[str, Any]:
            return lifecycle.summary()
        app.add_api_route(
            SUMMARY_PATH,
            summary,
            methods=["GET"],
            name="pass219-lane5-global-capability-summary-1-76",
        )

    if not _route_exists(app, SEARCH_PATH):
        async def search(q: str = "", limit: int = 20) -> dict[str, Any]:
            return lifecycle.search(q, limit=limit)
        app.add_api_route(
            SEARCH_PATH,
            search,
            methods=["GET"],
            name="pass219-lane5-global-capability-search-1-76",
        )

    inherited_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def pass219_lane5_visibility_lifespan(app_instance: Any):
        async with inherited_lifespan(app_instance):
            warm_task = asyncio.create_task(
                asyncio.to_thread(lifecycle.startup),
                name="hhs-pass219-lane5-global-capability-visibility-1-76",
            )
            try:
                yield
            finally:
                await warm_task

    app.router.lifespan_context = pass219_lane5_visibility_lifespan
    return lifecycle


__all__ = [
    "APP_STATE_KEY",
    "SEARCH_PATH",
    "STATUS_PATH",
    "SUMMARY_PATH",
    "Pass219Lane5CapabilityVisibilityLifecycle",
    "install_pass219_lane5_capability_visibility",
    "resolve_repository_root",
    "resolve_state_root",
]

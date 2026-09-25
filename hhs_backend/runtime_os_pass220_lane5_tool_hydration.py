"""Runtime-OS deployment warm-up for the Pass 219/220 Lane 5 tool graph.

The lifecycle is additive: it wraps the inherited application lifespan, warms
candidate-only Hash216 vector memory after inherited startup succeeds, and
never changes Lane 5 route selection or canonical mutation authority.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import os
from pathlib import Path
import tempfile
from typing import Any

from hhs_runtime.hhs_pass220_lane5_global_tool_hydration_v1 import (
    public_tool_graph,
    warm_pass219_220_tool_vector_store,
)

PASS220_LANE5_TOOL_STATUS_PATH = "/api/runtime/pass220/lane5/tools/warm-status"
PASS220_LANE5_TOOL_GRAPH_PATH = "/api/runtime/pass220/lane5/tools/graph"
PASS220_LANE5_TOOL_APP_STATE_KEY = "hhs_pass220_lane5_global_tool_warm_lifecycle"


def resolve_pass220_lane5_tool_state_root() -> Path:
    explicit = os.environ.get("HHS_PASS220_LANE5_TOOL_STATE_ROOT")
    if explicit:
        return Path(explicit).expanduser().resolve()
    data_root = os.environ.get("HHS_DATA_DIR")
    if data_root:
        return (Path(data_root).expanduser().resolve() / "pass220-lane5-tools")
    return (Path(tempfile.gettempdir()) / "hhs-pass220-lane5-tools").resolve()


def resolve_repository_root() -> Path:
    explicit = os.environ.get("HHS_REPOSITORY_ROOT")
    if explicit:
        return Path(explicit).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def _has_exact_route(app: Any, path: str) -> bool:
    return any(str(getattr(route, "path", "")) == path for route in app.router.routes)


class Pass220Lane5ToolWarmLifecycle:
    def __init__(
        self,
        *,
        repository_root: str | os.PathLike[str] | None = None,
        state_root: str | os.PathLike[str] | None = None,
        git_ref: str | None = None,
    ) -> None:
        self.repository_root = Path(
            repository_root if repository_root is not None else resolve_repository_root()
        ).resolve()
        self.state_root = Path(
            state_root if state_root is not None else resolve_pass220_lane5_tool_state_root()
        ).resolve()
        self.git_ref = git_ref or os.environ.get("HHS_PASS220_LANE5_TOOL_GIT_REF", "HEAD")
        self._receipt: dict[str, Any] | None = None
        self._failure: dict[str, str] | None = None
        self._started = False
        self._warming = False

    def startup(self) -> dict[str, Any]:
        self._started = True
        self._warming = True
        try:
            receipt = warm_pass219_220_tool_vector_store(
                self.repository_root,
                self.state_root,
                git_ref=self.git_ref,
            )
            if receipt.get("all_tools_warmed") is not True:
                raise RuntimeError("PASS220_LANE5_GLOBAL_TOOL_WARM_INCOMPLETE")
            graph = receipt.get("graph", {})
            coverage = graph.get("coverage", {})
            if not coverage or not all(bool(value) for value in coverage.values()):
                raise RuntimeError("PASS220_LANE5_GLOBAL_TOOL_COVERAGE_INCOMPLETE")
            if receipt.get("lane5_selection_changed") is not False:
                raise RuntimeError("PASS220_LANE5_SELECTOR_MUTATION_FORBIDDEN")
            self._receipt = receipt
            self._failure = None
        except Exception as exc:
            self._receipt = None
            self._failure = {
                "failure_type": type(exc).__name__,
                "reason": str(exc),
            }
        finally:
            self._warming = False
        return self.status()

    def shutdown(self) -> dict[str, Any]:
        return self.status()

    def status(self) -> dict[str, Any]:
        if self._receipt is None:
            state = (
                "WARMING_NONBLOCKING"
                if self._warming
                else ("FAIL_CLOSED_UNAVAILABLE" if self._started else "NOT_STARTED")
            )
            return {
                "schema": "HHS_PASS_220_LANE5_GLOBAL_TOOL_WARM_STATUS_V1",
                "started": self._started,
                "state": state,
                "warming": self._warming,
                "available_to_lane5": False,
                "lane5_selection_changed": False,
                "candidate_only": True,
                "repository_root": str(self.repository_root),
                "state_root": str(self.state_root),
                "git_ref": self.git_ref,
                "failure": dict(self._failure or {}),
            }
        graph = self._receipt["graph"]
        return {
            "schema": "HHS_PASS_220_LANE5_GLOBAL_TOOL_WARM_STATUS_V1",
            "started": True,
            "state": "WARM_READY",
            "available_to_lane5": True,
            "lane5_selection_changed": False,
            "candidate_only": True,
            "repository_root": str(self.repository_root),
            "state_root": str(self.state_root),
            "git_ref": self.git_ref,
            "registered_service_count": graph["registered_service_count"],
            "merged_pull_request_count": graph["merged_pull_request_count"],
            "tool_count": graph["tool_count"],
            "graph_root_sha256": graph["graph_root_sha256"],
            "projection_bits": graph["projection_bits"],
            "newly_admitted_count": self._receipt["newly_admitted_count"],
            "reused_count": self._receipt["reused_count"],
            "all_tools_warmed": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
        }

    def graph(self) -> dict[str, Any]:
        if self._receipt is None:
            raise RuntimeError("PASS220_LANE5_GLOBAL_TOOL_GRAPH_NOT_WARM")
        return public_tool_graph(self._receipt["graph"])


def install_pass220_lane5_tool_warm_hydration(
    app: Any,
    *,
    repository_root: str | os.PathLike[str] | None = None,
    state_root: str | os.PathLike[str] | None = None,
) -> Pass220Lane5ToolWarmLifecycle:
    existing = getattr(app.state, PASS220_LANE5_TOOL_APP_STATE_KEY, None)
    if isinstance(existing, Pass220Lane5ToolWarmLifecycle):
        return existing

    lifecycle = Pass220Lane5ToolWarmLifecycle(
        repository_root=repository_root,
        state_root=state_root,
    )
    setattr(app.state, PASS220_LANE5_TOOL_APP_STATE_KEY, lifecycle)

    if not _has_exact_route(app, PASS220_LANE5_TOOL_STATUS_PATH):
        async def pass220_lane5_tool_status() -> dict[str, Any]:
            return lifecycle.status()

        app.add_api_route(
            PASS220_LANE5_TOOL_STATUS_PATH,
            pass220_lane5_tool_status,
            methods=["GET", "HEAD"],
            include_in_schema=True,
            name="hhs-pass220-lane5-global-tool-warm-status",
        )

    if not _has_exact_route(app, PASS220_LANE5_TOOL_GRAPH_PATH):
        async def pass220_lane5_tool_graph() -> dict[str, Any]:
            return lifecycle.graph()

        app.add_api_route(
            PASS220_LANE5_TOOL_GRAPH_PATH,
            pass220_lane5_tool_graph,
            methods=["GET"],
            include_in_schema=True,
            name="hhs-pass220-lane5-global-tool-graph",
        )

    inherited_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def pass220_lane5_tool_warm_lifespan(app_instance):
        async with inherited_lifespan(app_instance):
            # Deployment warming is deliberately post-start and nonblocking.
            # Lane 5 tool availability remains fail-closed until the task seals
            # the complete candidate-only vector graph.
            warm_task = asyncio.create_task(
                asyncio.to_thread(lifecycle.startup),
                name="hhs-pass220-lane5-tool-warm",
            )
            try:
                yield
            finally:
                # A normal shutdown waits for the bounded repository hydration
                # task so persistent vector writes are not abandoned mid-record.
                await warm_task

    app.router.lifespan_context = pass220_lane5_tool_warm_lifespan
    return lifecycle


__all__ = [
    "PASS220_LANE5_TOOL_APP_STATE_KEY",
    "PASS220_LANE5_TOOL_GRAPH_PATH",
    "PASS220_LANE5_TOOL_STATUS_PATH",
    "Pass220Lane5ToolWarmLifecycle",
    "install_pass220_lane5_tool_warm_hydration",
    "resolve_pass220_lane5_tool_state_root",
]

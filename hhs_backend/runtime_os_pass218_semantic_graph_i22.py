"""RuntimeOS composition for Pass 218 Iteration 22 semantic-graph candidates."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from fastapi import HTTPException

from hhs_runtime.pass218.semantic_graph_i22 import (
    PASS218_I22_SEMANTIC_GRAPH_VERSION,
    Pass218I22GraphQuery,
    Pass218I22SemanticGraphCandidateAssembler,
    Pass218I22SemanticGraphError,
    Pass218I22WordNetPriorProvider,
)

PASS218_I22_STATUS_PATH = "/api/runtime/pass218/cognition/semantic-graph/status"
PASS218_I22_CANDIDATES_PATH = "/api/runtime/pass218/cognition/semantic-graph/candidates"
PASS218_I22_STATE_KEY = "hhs_pass218_semantic_graph_i22"


class Pass218I22RuntimeSemanticGraphControl:
    """Browser-safe membrane over I21 evidence and inherited WordNet priors."""

    def __init__(self, i21_control: Any, repository_root: str | Path) -> None:
        self.i21_control = i21_control
        self.lexical_provider = Pass218I22WordNetPriorProvider(repository_root)
        self.assembler = Pass218I22SemanticGraphCandidateAssembler(
            i21_control,
            self.lexical_provider,
        )

    @staticmethod
    def _query(payload: Mapping[str, Any]) -> Pass218I22GraphQuery:
        tokens = payload.get("tokens")
        if not isinstance(tokens, list) or not all(isinstance(item, str) for item in tokens):
            raise Pass218I22SemanticGraphError(
                "P218_I22_QUERY_TOKENS_STRING_LIST_REQUIRED"
            )
        return Pass218I22GraphQuery(
            tokens=tuple(tokens),
            top_k=payload.get("top_k", 8),
        ).validated()

    def assemble(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.assembler.assemble(self._query(payload))

    def status(self) -> dict[str, Any]:
        return self.assembler.status()


def install_pass218_i22_semantic_graph_control(
    app: Any,
    i21_control: Any,
    *,
    repository_root: str | Path,
) -> Pass218I22RuntimeSemanticGraphControl:
    existing = getattr(app.state, PASS218_I22_STATE_KEY, None)
    if isinstance(existing, Pass218I22RuntimeSemanticGraphControl):
        return existing

    control = Pass218I22RuntimeSemanticGraphControl(i21_control, repository_root)
    setattr(app.state, PASS218_I22_STATE_KEY, control)

    managed_paths = {PASS218_I22_STATUS_PATH, PASS218_I22_CANDIDATES_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def semantic_graph_status() -> dict[str, Any]:
        return control.status()

    async def semantic_graph_candidates(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.assemble(payload)
        except Pass218I22SemanticGraphError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I22_STATUS_PATH,
        semantic_graph_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-semantic-graph-status-i22",
    )
    app.add_api_route(
        PASS218_I22_CANDIDATES_PATH,
        semantic_graph_candidates,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-semantic-graph-candidates-i22",
    )
    return control


__all__ = [
    "PASS218_I22_CANDIDATES_PATH",
    "PASS218_I22_SEMANTIC_GRAPH_VERSION",
    "PASS218_I22_STATE_KEY",
    "PASS218_I22_STATUS_PATH",
    "Pass218I22RuntimeSemanticGraphControl",
    "install_pass218_i22_semantic_graph_control",
]

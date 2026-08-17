"""RuntimeOS composition for Pass 218 Iteration 23 contextual-state candidates."""
from __future__ import annotations

from typing import Any, Mapping

from fastapi import HTTPException

from hhs_runtime.pass218.contextual_state_i23 import (
    PASS218_I23_CONTEXTUAL_STATE_VERSION,
    Pass218I23ContextQuery,
    Pass218I23ContextualStateError,
    Pass218I23ContextualStateHydrator,
)

PASS218_I23_STATUS_PATH = "/api/runtime/pass218/cognition/contextual-state/status"
PASS218_I23_CANDIDATES_PATH = "/api/runtime/pass218/cognition/contextual-state/candidates"
PASS218_I23_STATE_KEY = "hhs_pass218_contextual_state_i23"


class Pass218I23RuntimeContextualStateControl:
    """Browser-safe membrane over the frozen I22 semantic-graph candidate plane."""

    def __init__(self, i22_control: Any) -> None:
        self.i22_control = i22_control
        self.hydrator = Pass218I23ContextualStateHydrator(i22_control)

    @staticmethod
    def _query(payload: Mapping[str, Any]) -> Pass218I23ContextQuery:
        tokens = payload.get("tokens")
        if not isinstance(tokens, list) or not all(isinstance(item, str) for item in tokens):
            raise Pass218I23ContextualStateError(
                "P218_I23_QUERY_TOKENS_STRING_LIST_REQUIRED"
            )
        attention_tokens = payload.get("attention_tokens", [])
        if not isinstance(attention_tokens, list) or not all(
            isinstance(item, str) for item in attention_tokens
        ):
            raise Pass218I23ContextualStateError(
                "P218_I23_ATTENTION_TOKENS_STRING_LIST_REQUIRED"
            )
        allowed_relation_families = payload.get("allowed_relation_families", [])
        if not isinstance(allowed_relation_families, list) or not all(
            isinstance(item, str) for item in allowed_relation_families
        ):
            raise Pass218I23ContextualStateError(
                "P218_I23_RELATION_FAMILIES_STRING_LIST_REQUIRED"
            )
        context_id = payload.get("context_id")
        if not isinstance(context_id, str):
            raise Pass218I23ContextualStateError(
                "P218_I23_CONTEXT_ID_STRING_REQUIRED"
            )
        return Pass218I23ContextQuery(
            tokens=tuple(tokens),
            context_id=context_id,
            attention_tokens=tuple(attention_tokens),
            top_k=payload.get("top_k", 8),
            attention_radius=payload.get("attention_radius", 1),
            max_hydrated_nodes=payload.get("max_hydrated_nodes", 24),
            allowed_relation_families=tuple(allowed_relation_families),
        ).validated()

    def hydrate(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.hydrator.hydrate(self._query(payload))

    def status(self) -> dict[str, Any]:
        return self.hydrator.status()


def install_pass218_i23_contextual_state_control(
    app: Any,
    i22_control: Any,
) -> Pass218I23RuntimeContextualStateControl:
    existing = getattr(app.state, PASS218_I23_STATE_KEY, None)
    if isinstance(existing, Pass218I23RuntimeContextualStateControl):
        return existing

    control = Pass218I23RuntimeContextualStateControl(i22_control)
    setattr(app.state, PASS218_I23_STATE_KEY, control)

    managed_paths = {PASS218_I23_STATUS_PATH, PASS218_I23_CANDIDATES_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def contextual_state_status() -> dict[str, Any]:
        return control.status()

    async def contextual_state_candidates(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.hydrate(payload)
        except Pass218I23ContextualStateError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I23_STATUS_PATH,
        contextual_state_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-contextual-state-status-i23",
    )
    app.add_api_route(
        PASS218_I23_CANDIDATES_PATH,
        contextual_state_candidates,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-contextual-state-candidates-i23",
    )
    return control


__all__ = [
    "PASS218_I23_CANDIDATES_PATH",
    "PASS218_I23_CONTEXTUAL_STATE_VERSION",
    "PASS218_I23_STATE_KEY",
    "PASS218_I23_STATUS_PATH",
    "Pass218I23RuntimeContextualStateControl",
    "install_pass218_i23_contextual_state_control",
]

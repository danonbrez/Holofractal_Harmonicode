"""RuntimeOS composition for Pass 218 Iteration 21 relational candidates."""
from __future__ import annotations

from typing import Any, Mapping

from fastapi import HTTPException

from hhs_runtime.pass218.relational_consumption_i21 import (
    PASS218_I21_RELATIONAL_CONSUMPTION_VERSION,
    Pass218I21CandidateQuery,
    Pass218I21RelationalCandidateConsumer,
    Pass218I21RelationalConsumptionError,
)

PASS218_I21_STATUS_PATH = "/api/runtime/pass218/cognition/relations/status"
PASS218_I21_CANDIDATES_PATH = "/api/runtime/pass218/cognition/relations/candidates"
PASS218_I21_STATE_KEY = "hhs_pass218_relational_consumption_i21"


class Pass218I21RuntimeRelationalControl:
    """Browser-safe query membrane over the already-governed I20 provider."""

    def __init__(self, i20_control: Any) -> None:
        self.i20_control = i20_control
        self.consumer = Pass218I21RelationalCandidateConsumer(i20_control)

    @staticmethod
    def _query(payload: Mapping[str, Any]) -> Pass218I21CandidateQuery:
        tokens = payload.get("tokens")
        if not isinstance(tokens, list) or not all(isinstance(item, str) for item in tokens):
            raise Pass218I21RelationalConsumptionError(
                "P218_I21_QUERY_TOKENS_STRING_LIST_REQUIRED"
            )
        top_k = payload.get("top_k", 8)
        return Pass218I21CandidateQuery(
            tokens=tuple(tokens),
            top_k=top_k,
        ).validated()

    def consume(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.consumer.consume(self._query(payload))

    def status(self) -> dict[str, Any]:
        return self.consumer.status()


def install_pass218_i21_relational_control(
    app: Any,
    i20_control: Any,
) -> Pass218I21RuntimeRelationalControl:
    existing = getattr(app.state, PASS218_I21_STATE_KEY, None)
    if isinstance(existing, Pass218I21RuntimeRelationalControl):
        return existing

    control = Pass218I21RuntimeRelationalControl(i20_control)
    setattr(app.state, PASS218_I21_STATE_KEY, control)

    managed_paths = {PASS218_I21_STATUS_PATH, PASS218_I21_CANDIDATES_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def relational_status() -> dict[str, Any]:
        return control.status()

    async def relational_candidates(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.consume(payload)
        except Pass218I21RelationalConsumptionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I21_STATUS_PATH,
        relational_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-relational-consumption-status-i21",
    )
    app.add_api_route(
        PASS218_I21_CANDIDATES_PATH,
        relational_candidates,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-relational-candidates-i21",
    )
    return control


__all__ = [
    "PASS218_I21_CANDIDATES_PATH",
    "PASS218_I21_STATE_KEY",
    "PASS218_I21_STATUS_PATH",
    "PASS218_I21_RELATIONAL_CONSUMPTION_VERSION",
    "Pass218I21RuntimeRelationalControl",
    "install_pass218_i21_relational_control",
]

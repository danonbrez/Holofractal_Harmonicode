"""RuntimeOS composition for Pass 218 Iteration 27 formal/analogical differentiation."""
from __future__ import annotations

from typing import Any, Mapping

from fastapi import HTTPException

from hhs_backend.runtime_os_pass218_grounded_manifold_i26 import (
    Pass218I26RuntimeGroundedManifoldControl,
)
from hhs_runtime.pass218.formal_analogical_differentiation_i27 import (
    PASS218_I27_DIFFERENTIATION_VERSION,
    Pass218I27DifferentiationError,
    Pass218I27DifferentiationRequest,
    Pass218I27FormalAnalogicalDifferentiator,
)

PASS218_I27_STATUS_PATH = "/api/runtime/pass218/cognition/formal-analogical-differentiation/status"
PASS218_I27_CANDIDATES_PATH = (
    "/api/runtime/pass218/cognition/formal-analogical-differentiation/candidates"
)
PASS218_I27_STATE_KEY = "hhs_pass218_formal_analogical_differentiation_i27"


class Pass218I27RuntimeDifferentiationControl:
    """Browser-safe membrane over frozen I26 grounded-manifold candidates."""

    def __init__(self, i26_control: Any) -> None:
        self.i26_control = i26_control
        self.differentiator = Pass218I27FormalAnalogicalDifferentiator(i26_control)

    @staticmethod
    def _request(payload: Mapping[str, Any]) -> Pass218I27DifferentiationRequest:
        manifold_request = Pass218I26RuntimeGroundedManifoldControl._request(payload)
        return Pass218I27DifferentiationRequest(
            manifold_request=manifold_request,
        ).validated()

    def differentiate(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.differentiator.differentiate(self._request(payload))

    def status(self) -> dict[str, Any]:
        return self.differentiator.status()


def install_pass218_i27_differentiation_control(
    app: Any,
    i26_control: Any,
) -> Pass218I27RuntimeDifferentiationControl:
    existing = getattr(app.state, PASS218_I27_STATE_KEY, None)
    if isinstance(existing, Pass218I27RuntimeDifferentiationControl):
        return existing

    control = Pass218I27RuntimeDifferentiationControl(i26_control)
    setattr(app.state, PASS218_I27_STATE_KEY, control)

    managed_paths = {PASS218_I27_STATUS_PATH, PASS218_I27_CANDIDATES_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def differentiation_status() -> dict[str, Any]:
        return control.status()

    async def differentiation_candidates(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.differentiate(payload)
        except Pass218I27DifferentiationError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I27_STATUS_PATH,
        differentiation_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-formal-analogical-differentiation-status-i27",
    )
    app.add_api_route(
        PASS218_I27_CANDIDATES_PATH,
        differentiation_candidates,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-formal-analogical-differentiation-candidates-i27",
    )
    return control


__all__ = [
    "PASS218_I27_CANDIDATES_PATH",
    "PASS218_I27_DIFFERENTIATION_VERSION",
    "PASS218_I27_STATE_KEY",
    "PASS218_I27_STATUS_PATH",
    "Pass218I27RuntimeDifferentiationControl",
    "install_pass218_i27_differentiation_control",
]

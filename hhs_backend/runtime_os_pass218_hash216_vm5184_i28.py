"""RuntimeOS composition for Pass 218 Iteration 28 Hash216/VM5184 transition."""
from __future__ import annotations

from typing import Any, Mapping

from fastapi import HTTPException

from hhs_backend.runtime_os_pass218_formal_analogical_i27 import (
    Pass218I27RuntimeDifferentiationControl,
)
from hhs_runtime.pass218.hash216_vm5184_transition_i28 import (
    PASS218_I28_TRANSITION_VERSION,
    Pass218I28Hash216VM5184Transition,
    Pass218I28TransitionError,
    Pass218I28TransitionRequest,
)

PASS218_I28_STATUS_PATH = "/api/runtime/pass218/cognition/hash216-vm5184-transition/status"
PASS218_I28_CANDIDATES_PATH = "/api/runtime/pass218/cognition/hash216-vm5184-transition/candidates"
PASS218_I28_STATE_KEY = "hhs_pass218_hash216_vm5184_transition_i28"


class Pass218I28RuntimeTransitionControl:
    """Browser-safe membrane over the frozen I27 differentiation candidate."""

    def __init__(self, i27_control: Any) -> None:
        self.i27_control = i27_control
        self.transitioner = Pass218I28Hash216VM5184Transition(i27_control)

    @staticmethod
    def _request(payload: Mapping[str, Any]) -> Pass218I28TransitionRequest:
        differentiation_request = Pass218I27RuntimeDifferentiationControl._request(payload)
        return Pass218I28TransitionRequest(
            differentiation_request=differentiation_request,
        ).validated()

    def construct(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.transitioner.construct(self._request(payload))

    def status(self) -> dict[str, Any]:
        return self.transitioner.status()


def install_pass218_i28_transition_control(
    app: Any,
    i27_control: Any,
) -> Pass218I28RuntimeTransitionControl:
    existing = getattr(app.state, PASS218_I28_STATE_KEY, None)
    if isinstance(existing, Pass218I28RuntimeTransitionControl):
        return existing

    control = Pass218I28RuntimeTransitionControl(i27_control)
    setattr(app.state, PASS218_I28_STATE_KEY, control)

    managed_paths = {PASS218_I28_STATUS_PATH, PASS218_I28_CANDIDATES_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def transition_status() -> dict[str, Any]:
        return control.status()

    async def transition_candidates(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.construct(payload)
        except Pass218I28TransitionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I28_STATUS_PATH,
        transition_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-hash216-vm5184-transition-status-i28",
    )
    app.add_api_route(
        PASS218_I28_CANDIDATES_PATH,
        transition_candidates,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-hash216-vm5184-transition-candidates-i28",
    )
    return control


__all__ = [
    "PASS218_I28_CANDIDATES_PATH",
    "PASS218_I28_STATE_KEY",
    "PASS218_I28_STATUS_PATH",
    "PASS218_I28_TRANSITION_VERSION",
    "Pass218I28RuntimeTransitionControl",
    "install_pass218_i28_transition_control",
]

"""RuntimeOS composition for Pass 218 Iteration 26 grounded-manifold candidates."""
from __future__ import annotations

from typing import Any, Mapping

from fastapi import HTTPException

from hhs_backend.runtime_os_pass218_perspective_context_i25 import (
    Pass218I25RuntimePerspectiveContextControl,
)
from hhs_runtime.pass218.grounded_manifold_i26 import (
    PASS218_I26_GROUNDED_MANIFOLD_VERSION,
    Pass218I26GroundedManifoldError,
    Pass218I26GroundedRelationalManifold,
    Pass218I26ManifoldRequest,
)

PASS218_I26_STATUS_PATH = "/api/runtime/pass218/cognition/grounded-manifold/status"
PASS218_I26_CANDIDATES_PATH = "/api/runtime/pass218/cognition/grounded-manifold/candidates"
PASS218_I26_STATE_KEY = "hhs_pass218_grounded_manifold_i26"


class Pass218I26RuntimeGroundedManifoldControl:
    """Browser-safe membrane over frozen I25 perspective/context candidates."""

    def __init__(self, i25_control: Any) -> None:
        self.i25_control = i25_control
        self.manifold = Pass218I26GroundedRelationalManifold(i25_control)

    @staticmethod
    def _request(payload: Mapping[str, Any]) -> Pass218I26ManifoldRequest:
        perspective_request = Pass218I25RuntimePerspectiveContextControl._request(payload)
        return Pass218I26ManifoldRequest(
            perspective_request=perspective_request,
        ).validated()

    def construct(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.manifold.construct(self._request(payload))

    def status(self) -> dict[str, Any]:
        return self.manifold.status()


def install_pass218_i26_grounded_manifold_control(
    app: Any,
    i25_control: Any,
) -> Pass218I26RuntimeGroundedManifoldControl:
    existing = getattr(app.state, PASS218_I26_STATE_KEY, None)
    if isinstance(existing, Pass218I26RuntimeGroundedManifoldControl):
        return existing

    control = Pass218I26RuntimeGroundedManifoldControl(i25_control)
    setattr(app.state, PASS218_I26_STATE_KEY, control)

    managed_paths = {PASS218_I26_STATUS_PATH, PASS218_I26_CANDIDATES_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def grounded_manifold_status() -> dict[str, Any]:
        return control.status()

    async def grounded_manifold_candidates(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.construct(payload)
        except Pass218I26GroundedManifoldError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I26_STATUS_PATH,
        grounded_manifold_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-grounded-manifold-status-i26",
    )
    app.add_api_route(
        PASS218_I26_CANDIDATES_PATH,
        grounded_manifold_candidates,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-grounded-manifold-candidates-i26",
    )
    return control


__all__ = [
    "PASS218_I26_CANDIDATES_PATH",
    "PASS218_I26_GROUNDED_MANIFOLD_VERSION",
    "PASS218_I26_STATE_KEY",
    "PASS218_I26_STATUS_PATH",
    "Pass218I26RuntimeGroundedManifoldControl",
    "install_pass218_i26_grounded_manifold_control",
]

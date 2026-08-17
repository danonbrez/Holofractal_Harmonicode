"""RuntimeOS composition for Pass 218 Iteration 29 Hash216/VM5184 validation."""
from __future__ import annotations

from typing import Any, Mapping

from fastapi import HTTPException

from hhs_backend.runtime_os_pass218_hash216_vm5184_i28 import (
    Pass218I28RuntimeTransitionControl,
)
from hhs_runtime.pass218.hash216_vm5184_validation_i29 import (
    PASS218_I29_VALIDATION_VERSION,
    Pass218I29Hash216VM5184Validator,
    Pass218I29ValidationError,
    Pass218I29ValidationRequest,
)

PASS218_I29_STATUS_PATH = (
    "/api/runtime/pass218/cognition/hash216-vm5184-transition-validation/status"
)
PASS218_I29_VALIDATE_PATH = (
    "/api/runtime/pass218/cognition/hash216-vm5184-transition-validation/validate"
)
PASS218_I29_STATE_KEY = "hhs_pass218_hash216_vm5184_validation_i29"


class Pass218I29RuntimeValidationControl:
    """Browser-safe validation membrane over frozen I28 and I27 controls."""

    def __init__(self, i28_control: Any, i27_control: Any) -> None:
        self.i28_control = i28_control
        self.i27_control = i27_control
        self.validator = Pass218I29Hash216VM5184Validator(
            i28_control.transitioner,
            i27_control.differentiator,
        )

    @staticmethod
    def _request(payload: Mapping[str, Any]) -> Pass218I29ValidationRequest:
        transition_request = Pass218I28RuntimeTransitionControl._request(payload)
        return Pass218I29ValidationRequest(
            transition_request=transition_request,
        ).validated()

    def validate(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.validator.validate(self._request(payload))

    def status(self) -> dict[str, Any]:
        return self.validator.status()


def install_pass218_i29_validation_control(
    app: Any,
    i28_control: Any,
    i27_control: Any,
) -> Pass218I29RuntimeValidationControl:
    existing = getattr(app.state, PASS218_I29_STATE_KEY, None)
    if isinstance(existing, Pass218I29RuntimeValidationControl):
        return existing

    control = Pass218I29RuntimeValidationControl(i28_control, i27_control)
    setattr(app.state, PASS218_I29_STATE_KEY, control)

    managed_paths = {PASS218_I29_STATUS_PATH, PASS218_I29_VALIDATE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def validation_status() -> dict[str, Any]:
        return control.status()

    async def validate_transition(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.validate(payload)
        except Pass218I29ValidationError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I29_STATUS_PATH,
        validation_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-hash216-vm5184-transition-validation-status-i29",
    )
    app.add_api_route(
        PASS218_I29_VALIDATE_PATH,
        validate_transition,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-hash216-vm5184-transition-validation-i29",
    )
    return control


__all__ = [
    "PASS218_I29_STATE_KEY",
    "PASS218_I29_STATUS_PATH",
    "PASS218_I29_VALIDATE_PATH",
    "PASS218_I29_VALIDATION_VERSION",
    "Pass218I29RuntimeValidationControl",
    "install_pass218_i29_validation_control",
]

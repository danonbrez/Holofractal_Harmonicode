"""RuntimeOS composition for Pass 218 Iteration 33 curriculum advancement."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from hhs_runtime.pass218.curriculum_advance_i33 import (
    PASS218_I33_ADVANCE_SCOPE,
    PASS218_I33_ADVANCE_VERSION,
    Pass218I33CurriculumAdvanceError,
    Pass218I33CurriculumAdvancer,
    Pass218I33CurriculumAuthority,
    Pass218I33CurriculumAuthorityError,
)

PASS218_I33_STATUS_PATH = "/api/runtime/pass218/cognition/curriculum-advance/status"
PASS218_I33_ADVANCE_PATH = "/api/runtime/pass218/cognition/curriculum-advance/advance"
PASS218_I33_STATE_KEY = "hhs_pass218_curriculum_advance_i33"
PASS218_I33_STORE_DIRNAME = "cognition/curriculum-advance-i33"
PASS218_I33_AUTHORITY_ENV = "HHS_PASS218_I33_CURRICULUM_AUTHORITY_FILE"


def _authority_from_environment() -> tuple[Pass218I33CurriculumAuthority | None, str | None]:
    value = os.environ.get(PASS218_I33_AUTHORITY_ENV, "").strip()
    if not value:
        return None, None
    path = Path(value).expanduser().resolve()
    try:
        payload = json.loads(path.read_text("utf-8"))
        if not isinstance(payload, dict):
            raise Pass218I33CurriculumAuthorityError(
                "P218_I33_AUTHORITY_FILE_OBJECT_REQUIRED"
            )
        return Pass218I33CurriculumAuthority.restore(payload), None
    except Exception as exc:
        code = str(exc)
        if not code.startswith("P218_"):
            code = "P218_I33_AUTHORITY_FILE_INVALID"
        return None, code


class Pass218I33RuntimeCurriculumAdvanceControl:
    """Read-only-authority RuntimeOS membrane around the I33 cursor transition."""

    def __init__(
        self,
        i32_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
        authority: Pass218I33CurriculumAuthority | None = None,
    ) -> None:
        self.i32_control = i32_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I33_STORE_DIRNAME
        configured = authority
        configuration_error = None
        if configured is None:
            configured, configuration_error = _authority_from_environment()
        self.configuration_error = configuration_error
        self.advancer = Pass218I33CurriculumAdvancer(
            lifecycle=lifecycle,
            i32_store_root=i32_control.store_root,
            advance_store_root=self.store_root,
            authority=configured,
        )

    def advance(self) -> dict[str, Any]:
        if self.configuration_error is not None:
            raise Pass218I33CurriculumAuthorityError(self.configuration_error)
        return self.advancer.advance()

    def status(self) -> dict[str, Any]:
        value = self.advancer.status()
        return {
            **value,
            "authority_configuration_error": self.configuration_error,
            "authority_configuration_source": (
                "EXPLICIT_INTERNAL_CONFIGURATION"
                if self.advancer.authority is not None and not os.environ.get(PASS218_I33_AUTHORITY_ENV)
                else (
                    "READ_ONLY_ENVIRONMENT_FILE"
                    if self.advancer.authority is not None
                    else "UNCONFIGURED"
                )
            ),
            "api_can_mint_curriculum_authority": False,
        }


def install_pass218_i33_curriculum_advance_control(
    app: Any,
    i32_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
    authority: Pass218I33CurriculumAuthority | None = None,
) -> Pass218I33RuntimeCurriculumAdvanceControl:
    existing = getattr(app.state, PASS218_I33_STATE_KEY, None)
    if isinstance(existing, Pass218I33RuntimeCurriculumAdvanceControl):
        return existing

    control = Pass218I33RuntimeCurriculumAdvanceControl(
        i32_control,
        lifecycle=lifecycle,
        state_root=state_root,
        authority=authority,
    )
    setattr(app.state, PASS218_I33_STATE_KEY, control)

    managed_paths = {PASS218_I33_STATUS_PATH, PASS218_I33_ADVANCE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def curriculum_advance_status() -> dict[str, Any]:
        return control.status()

    async def advance_closed_source() -> dict[str, Any]:
        try:
            return control.advance()
        except Pass218I33CurriculumAuthorityError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except Pass218I33CurriculumAdvanceError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I33_STATUS_PATH,
        curriculum_advance_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-curriculum-advance-status-i33",
    )
    app.add_api_route(
        PASS218_I33_ADVANCE_PATH,
        advance_closed_source,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-curriculum-advance-i33",
    )
    return control


__all__ = [
    "PASS218_I33_ADVANCE_PATH",
    "PASS218_I33_AUTHORITY_ENV",
    "PASS218_I33_STATE_KEY",
    "PASS218_I33_STATUS_PATH",
    "PASS218_I33_STORE_DIRNAME",
    "PASS218_I33_ADVANCE_SCOPE",
    "PASS218_I33_ADVANCE_VERSION",
    "Pass218I33RuntimeCurriculumAdvanceControl",
    "install_pass218_i33_curriculum_advance_control",
]

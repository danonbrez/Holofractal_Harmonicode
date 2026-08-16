"""RuntimeOS composition for Pass 218 Iteration 47 manifest-bound I33 advance."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from fastapi import HTTPException

from hhs_runtime.pass218.curriculum_advance_i33 import Pass218I33CurriculumAdvanceError
from hhs_runtime.pass218.manifest_bound_i33_curriculum_advance_i47 import (
    PASS218_I47_SCOPE,
    PASS218_I47_VERSION,
    Pass218I47AdvanceError,
    Pass218I47BindingError,
    Pass218I47ManifestBoundI33CurriculumAdvance,
    Pass218I47StateError,
)

PASS218_I47_STATUS_PATH = "/api/runtime/pass218/cognition/manifest-bound-i33-curriculum-advance/status"
PASS218_I47_ADVANCE_PATH = "/api/runtime/pass218/cognition/manifest-bound-i33-curriculum-advance/advance"
PASS218_I47_STATE_KEY = "hhs_pass218_manifest_bound_i33_curriculum_advance_i47"
PASS218_I47_STORE_DIRNAME = "cognition/manifest-bound-i33-curriculum-advance-i47"


class Pass218I47RuntimeManifestBoundI33CurriculumAdvanceControl:
    """No-override I33 consumption membrane over exact durable I46 closure state."""

    def __init__(
        self,
        i46_control: Any,
        i33_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i46_control = i46_control
        self.i33_control = i33_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I47_STORE_DIRNAME
        self.advance_control = Pass218I47ManifestBoundI33CurriculumAdvance(
            lifecycle=lifecycle,
            i46_store=i46_control.closure.store,
            i30_store=i46_control.closure.i30_store,
            i33_advancer=i33_control.advancer,
            state_root=self.store_root,
        )

    def advance(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise Pass218I47BindingError("P218_I47_REQUEST_OBJECT_REQUIRED")
        if dict(payload):
            raise Pass218I47BindingError("P218_I47_CALLER_OVERRIDE_FIELDS_FORBIDDEN")
        if self.i33_control.configuration_error is not None:
            raise Pass218I47BindingError(self.i33_control.configuration_error)
        return self.advance_control.advance()

    def status(self) -> dict[str, Any]:
        return {
            **self.advance_control.status(),
            "authority_configuration_error": self.i33_control.configuration_error,
            "authority_configuration_source": self.i33_control.status().get(
                "authority_configuration_source"
            ),
            "api_requires_empty_intent_object": True,
            "api_derives_i33_advance_from_durable_i46_i32_chain": True,
            "api_can_override_i46_receipt": False,
            "api_can_override_i32_closure_identity": False,
            "api_can_override_curriculum_identity": False,
            "api_can_override_curriculum_position": False,
            "api_can_override_source_identity": False,
            "api_can_mint_curriculum_authority": False,
            "api_can_supply_raw_source_payload": False,
            "api_persists_i33_advance_request": False,
            "api_ingests_next_source": False,
            "api_advances_stage": False,
            "api_invokes_canonical_learning": False,
            "api_promotes_truth": False,
            "api_mints_action_authority": False,
        }


def install_pass218_i47_manifest_bound_i33_curriculum_advance_control(
    app: Any,
    i46_control: Any,
    i33_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I47RuntimeManifestBoundI33CurriculumAdvanceControl:
    existing = getattr(app.state, PASS218_I47_STATE_KEY, None)
    if isinstance(existing, Pass218I47RuntimeManifestBoundI33CurriculumAdvanceControl):
        return existing

    control = Pass218I47RuntimeManifestBoundI33CurriculumAdvanceControl(
        i46_control,
        i33_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I47_STATE_KEY, control)

    managed_paths = {PASS218_I47_STATUS_PATH, PASS218_I47_ADVANCE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def manifest_bound_i33_curriculum_advance_status() -> dict[str, Any]:
        return control.status()

    async def advance_manifest_bound_closed_source(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.advance(payload)
        except (
            Pass218I47AdvanceError,
            Pass218I47BindingError,
            Pass218I47StateError,
            Pass218I33CurriculumAdvanceError,
        ) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except (ValueError, TypeError, KeyError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I47_STATUS_PATH,
        manifest_bound_i33_curriculum_advance_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-bound-i33-curriculum-advance-status-i47",
    )
    app.add_api_route(
        PASS218_I47_ADVANCE_PATH,
        advance_manifest_bound_closed_source,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-bound-i33-curriculum-advance-i47",
    )
    return control


__all__ = [
    "PASS218_I47_ADVANCE_PATH",
    "PASS218_I47_SCOPE",
    "PASS218_I47_STATE_KEY",
    "PASS218_I47_STATUS_PATH",
    "PASS218_I47_STORE_DIRNAME",
    "PASS218_I47_VERSION",
    "Pass218I47RuntimeManifestBoundI33CurriculumAdvanceControl",
    "install_pass218_i47_manifest_bound_i33_curriculum_advance_control",
]

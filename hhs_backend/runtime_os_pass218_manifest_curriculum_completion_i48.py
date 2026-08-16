"""RuntimeOS composition for Pass 218 Iteration 48 curriculum completion seal."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from fastapi import HTTPException

from hhs_runtime.pass218.manifest_bound_curriculum_completion_seal_i48 import (
    PASS218_I48_SCOPE,
    PASS218_I48_VERSION,
    Pass218I48BindingError,
    Pass218I48CompletionError,
    Pass218I48ManifestBoundCurriculumCompletionSeal,
    Pass218I48StateError,
)

PASS218_I48_STATUS_PATH = "/api/runtime/pass218/cognition/manifest-bound-curriculum-completion/status"
PASS218_I48_SEAL_PATH = "/api/runtime/pass218/cognition/manifest-bound-curriculum-completion/seal"
PASS218_I48_STATE_KEY = "hhs_pass218_manifest_bound_curriculum_completion_i48"
PASS218_I48_STORE_DIRNAME = "cognition/manifest-bound-curriculum-completion-i48"


class Pass218I48RuntimeManifestBoundCurriculumCompletionControl:
    """Empty-intent seal membrane over exact durable I47 terminal state."""

    def __init__(
        self,
        i47_control: Any,
        i33_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i47_control = i47_control
        self.i33_control = i33_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I48_STORE_DIRNAME
        self.completion = Pass218I48ManifestBoundCurriculumCompletionSeal(
            lifecycle=lifecycle,
            i47_store=i47_control.advance_control.store,
            i30_store=i47_control.advance_control.i30_store,
            i33_advancer=i33_control.advancer,
            state_root=self.store_root,
        )

    def seal(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise Pass218I48BindingError("P218_I48_REQUEST_OBJECT_REQUIRED")
        if dict(payload):
            raise Pass218I48BindingError("P218_I48_CALLER_OVERRIDE_FIELDS_FORBIDDEN")
        if self.i33_control.configuration_error is not None:
            raise Pass218I48BindingError(self.i33_control.configuration_error)
        return self.completion.seal()

    def status(self) -> dict[str, Any]:
        return {
            **self.completion.status(),
            "authority_configuration_error": self.i33_control.configuration_error,
            "authority_configuration_source": self.i33_control.status().get(
                "authority_configuration_source"
            ),
            "api_requires_empty_intent_object": True,
            "api_derives_completion_from_durable_i47_i33_chain": True,
            "api_can_override_i47_receipt": False,
            "api_can_override_i33_terminal_receipt": False,
            "api_can_override_curriculum_identity": False,
            "api_can_override_final_cursor": False,
            "api_can_invoke_i33_curriculum_advance": False,
            "api_can_ingest_next_source": False,
            "api_can_advance_stage": False,
            "api_can_mint_pass219_handoff_authority": False,
            "api_can_invoke_canonical_learning": False,
            "api_can_promote_truth": False,
            "api_can_mint_action_authority": False,
            "api_can_activate_model": False,
            "api_can_supply_raw_source_payload": False,
        }


def install_pass218_i48_manifest_bound_curriculum_completion_control(
    app: Any,
    i47_control: Any,
    i33_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I48RuntimeManifestBoundCurriculumCompletionControl:
    existing = getattr(app.state, PASS218_I48_STATE_KEY, None)
    if isinstance(existing, Pass218I48RuntimeManifestBoundCurriculumCompletionControl):
        return existing

    control = Pass218I48RuntimeManifestBoundCurriculumCompletionControl(
        i47_control,
        i33_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I48_STATE_KEY, control)

    managed_paths = {PASS218_I48_STATUS_PATH, PASS218_I48_SEAL_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def manifest_bound_curriculum_completion_status() -> dict[str, Any]:
        return control.status()

    async def seal_manifest_bound_curriculum_completion(
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            return control.seal(payload)
        except (
            Pass218I48CompletionError,
            Pass218I48BindingError,
            Pass218I48StateError,
        ) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except (ValueError, TypeError, KeyError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I48_STATUS_PATH,
        manifest_bound_curriculum_completion_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-bound-curriculum-completion-status-i48",
    )
    app.add_api_route(
        PASS218_I48_SEAL_PATH,
        seal_manifest_bound_curriculum_completion,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-bound-curriculum-completion-seal-i48",
    )
    return control


__all__ = [
    "PASS218_I48_SCOPE",
    "PASS218_I48_SEAL_PATH",
    "PASS218_I48_STATE_KEY",
    "PASS218_I48_STATUS_PATH",
    "PASS218_I48_STORE_DIRNAME",
    "PASS218_I48_VERSION",
    "Pass218I48RuntimeManifestBoundCurriculumCompletionControl",
    "install_pass218_i48_manifest_bound_curriculum_completion_control",
]

"""RuntimeOS composition for Pass 218 Iteration 36 manifest-bound I4 staging."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from hhs_runtime.pass218.manifest_bound_vector_vm5184_staging_i36 import (
    PASS218_I36_SCOPE,
    PASS218_I36_VERSION,
    Pass218I36BindingError,
    Pass218I36I4Error,
    Pass218I36ManifestBoundVectorVM5184Staging,
    Pass218I36StagingError,
    Pass218I36StateError,
)

PASS218_I36_STATUS_PATH = (
    "/api/runtime/pass218/cognition/manifest-vector-vm5184-staging/status"
)
PASS218_I36_STAGE_PATH = (
    "/api/runtime/pass218/cognition/manifest-vector-vm5184-staging/stage"
)
PASS218_I36_STATE_KEY = "hhs_pass218_manifest_vector_vm5184_staging_i36"
PASS218_I36_STORE_DIRNAME = "cognition/manifest-vector-vm5184-staging-i36"


class Pass218I36RuntimeManifestVectorVM5184StagingControl:
    """RuntimeOS membrane from the durable I35 boundary into frozen I4 only."""

    def __init__(
        self,
        i35_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i35_control = i35_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I36_STORE_DIRNAME
        self.staging = Pass218I36ManifestBoundVectorVM5184Staging(
            lifecycle=lifecycle,
            i35_store=i35_control.ingress.store,
            state_root=self.store_root,
            i35_status_provider=i35_control.status,
        )

    def stage(self) -> dict[str, Any]:
        return self.staging.stage()

    def status(self) -> dict[str, Any]:
        return {
            **self.staging.status(),
            "api_can_supply_source_payload": False,
            "api_can_supply_semantic_candidate": False,
            "api_can_supply_manifest_binding": False,
            "api_can_override_i35_receipt": False,
            "api_can_invoke_i5_promotion": False,
            "api_can_invoke_i30_canonical_promotion": False,
            "api_can_invoke_vm81_authority": False,
            "api_can_advance_curriculum": False,
            "api_can_advance_curriculum_stage": False,
            "api_can_invoke_i31_or_i32": False,
            "request_source_payload_persisted": False,
        }


def install_pass218_i36_manifest_vector_vm5184_staging_control(
    app: Any,
    i35_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I36RuntimeManifestVectorVM5184StagingControl:
    existing = getattr(app.state, PASS218_I36_STATE_KEY, None)
    if isinstance(existing, Pass218I36RuntimeManifestVectorVM5184StagingControl):
        return existing

    control = Pass218I36RuntimeManifestVectorVM5184StagingControl(
        i35_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I36_STATE_KEY, control)

    managed_paths = {PASS218_I36_STATUS_PATH, PASS218_I36_STAGE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def manifest_vector_vm5184_staging_status() -> dict[str, Any]:
        return control.status()

    async def stage_manifest_bound_vector_vm5184() -> dict[str, Any]:
        try:
            return control.stage()
        except Pass218I36BindingError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except (
            Pass218I36I4Error,
            Pass218I36StateError,
            Pass218I36StagingError,
        ) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I36_STATUS_PATH,
        manifest_vector_vm5184_staging_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-vector-vm5184-staging-status-i36",
    )
    app.add_api_route(
        PASS218_I36_STAGE_PATH,
        stage_manifest_bound_vector_vm5184,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-vector-vm5184-staging-stage-i36",
    )
    return control


__all__ = [
    "PASS218_I36_SCOPE",
    "PASS218_I36_STAGE_PATH",
    "PASS218_I36_STATE_KEY",
    "PASS218_I36_STATUS_PATH",
    "PASS218_I36_STORE_DIRNAME",
    "PASS218_I36_VERSION",
    "Pass218I36RuntimeManifestVectorVM5184StagingControl",
    "install_pass218_i36_manifest_vector_vm5184_staging_control",
]

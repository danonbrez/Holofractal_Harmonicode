"""RuntimeOS composition for Pass 218 Iteration 46 manifest-bound I32 closure."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from fastapi import HTTPException

from hhs_runtime.pass218.manifest_bound_i32_source_closure_i46 import (
    PASS218_I46_SCOPE,
    PASS218_I46_VERSION,
    Pass218I46BindingError,
    Pass218I46ClosureError,
    Pass218I46ManifestBoundI32SourceClosure,
    Pass218I46StateError,
)
from hhs_runtime.pass218.source_closure_i32 import Pass218I32ClosureError

PASS218_I46_STATUS_PATH = "/api/runtime/pass218/cognition/manifest-bound-i32-source-closure/status"
PASS218_I46_CLOSE_PATH = "/api/runtime/pass218/cognition/manifest-bound-i32-source-closure/close"
PASS218_I46_STATE_KEY = "hhs_pass218_manifest_bound_i32_source_closure_i46"
PASS218_I46_STORE_DIRNAME = "cognition/manifest-bound-i32-source-closure-i46"


class Pass218I46RuntimeManifestBoundI32SourceClosureControl:
    """No-override I32 consumption membrane over exact durable I45 purge state."""

    def __init__(
        self,
        i45_control: Any,
        i44_control: Any,
        i43_control: Any,
        i42_control: Any,
        i34_control: Any,
        i32_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i45_control = i45_control
        self.i44_control = i44_control
        self.i43_control = i43_control
        self.i42_control = i42_control
        self.i34_control = i34_control
        self.i32_control = i32_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I46_STORE_DIRNAME
        self.closure = Pass218I46ManifestBoundI32SourceClosure(
            lifecycle=lifecycle,
            i45_store=i45_control.purge_control.store,
            i44_store=i44_control.promotion.store,
            i43_store=i43_control.authorization.store,
            i42_store=i42_control.equality.store,
            i34_store=i34_control.ingress.store,
            i30_store=i45_control.i31_control.purger.i30_store,
            i32_closer=i32_control.closer,
            state_root=self.store_root,
        )

    def close(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise Pass218I46BindingError("P218_I46_REQUEST_OBJECT_REQUIRED")
        if dict(payload):
            raise Pass218I46BindingError("P218_I46_CALLER_OVERRIDE_FIELDS_FORBIDDEN")
        return self.closure.close()

    def status(self) -> dict[str, Any]:
        return {
            **self.closure.status(),
            "api_requires_empty_intent_object": True,
            "api_derives_i32_request_from_durable_manifest_and_purge_chain": True,
            "api_can_override_i45_receipt": False,
            "api_can_override_i31_purge_identity": False,
            "api_can_override_i34_source_identity": False,
            "api_can_override_curriculum_identity": False,
            "api_can_override_previous_closure": False,
            "api_can_supply_raw_source_payload": False,
            "api_persists_i32_request_payload": False,
            "api_invokes_i33": False,
            "api_advances_curriculum": False,
            "api_advances_stage": False,
            "api_invokes_canonical_learning": False,
            "api_promotes_truth": False,
            "api_mints_action_authority": False,
        }


def install_pass218_i46_manifest_bound_i32_source_closure_control(
    app: Any,
    i45_control: Any,
    i44_control: Any,
    i43_control: Any,
    i42_control: Any,
    i34_control: Any,
    i32_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I46RuntimeManifestBoundI32SourceClosureControl:
    existing = getattr(app.state, PASS218_I46_STATE_KEY, None)
    if isinstance(existing, Pass218I46RuntimeManifestBoundI32SourceClosureControl):
        return existing

    control = Pass218I46RuntimeManifestBoundI32SourceClosureControl(
        i45_control,
        i44_control,
        i43_control,
        i42_control,
        i34_control,
        i32_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I46_STATE_KEY, control)

    managed_paths = {PASS218_I46_STATUS_PATH, PASS218_I46_CLOSE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def manifest_bound_i32_source_closure_status() -> dict[str, Any]:
        return control.status()

    async def close_manifest_bound_purged_source(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.close(payload)
        except (
            Pass218I46ClosureError,
            Pass218I46BindingError,
            Pass218I46StateError,
            Pass218I32ClosureError,
        ) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except (ValueError, TypeError, KeyError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I46_STATUS_PATH,
        manifest_bound_i32_source_closure_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-bound-i32-source-closure-status-i46",
    )
    app.add_api_route(
        PASS218_I46_CLOSE_PATH,
        close_manifest_bound_purged_source,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-bound-i32-source-closure-i46",
    )
    return control


__all__ = [
    "PASS218_I46_CLOSE_PATH",
    "PASS218_I46_SCOPE",
    "PASS218_I46_STATE_KEY",
    "PASS218_I46_STATUS_PATH",
    "PASS218_I46_STORE_DIRNAME",
    "PASS218_I46_VERSION",
    "Pass218I46RuntimeManifestBoundI32SourceClosureControl",
    "install_pass218_i46_manifest_bound_i32_source_closure_control",
]

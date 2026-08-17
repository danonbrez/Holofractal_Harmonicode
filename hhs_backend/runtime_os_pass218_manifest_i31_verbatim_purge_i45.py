"""RuntimeOS composition for Pass 218 Iteration 45 manifest-bound I31 purge."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from fastapi import HTTPException

from hhs_runtime.pass218.manifest_bound_i31_verbatim_purge_i45 import (
    PASS218_I45_SCOPE,
    PASS218_I45_VERSION,
    Pass218I45BindingError,
    Pass218I45ManifestBoundI31VerbatimPurge,
    Pass218I45PurgeError,
    Pass218I45StateError,
)
from hhs_runtime.pass218.verbatim_purge_i31 import Pass218I31PurgeError

PASS218_I45_STATUS_PATH = "/api/runtime/pass218/cognition/manifest-bound-i31-verbatim-purge/status"
PASS218_I45_PURGE_PATH = "/api/runtime/pass218/cognition/manifest-bound-i31-verbatim-purge/purge"
PASS218_I45_STATE_KEY = "hhs_pass218_manifest_bound_i31_verbatim_purge_i45"
PASS218_I45_STORE_DIRNAME = "cognition/manifest-bound-i31-verbatim-purge-i45"


class Pass218I45RuntimeManifestBoundI31VerbatimPurgeControl:
    """No-override I31 consumption membrane over exact durable I44 promotion."""

    def __init__(
        self,
        i44_control: Any,
        i31_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i44_control = i44_control
        self.i31_control = i31_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I45_STORE_DIRNAME
        self.purge_control = Pass218I45ManifestBoundI31VerbatimPurge(
            lifecycle=lifecycle,
            i44_store=i44_control.promotion.store,
            i31_purger=i31_control.purger,
            state_root=self.store_root,
        )

    def purge(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise Pass218I45BindingError("P218_I45_REQUEST_OBJECT_REQUIRED")
        if dict(payload):
            raise Pass218I45BindingError("P218_I45_CALLER_OVERRIDE_FIELDS_FORBIDDEN")
        return self.purge_control.purge()

    def status(self) -> dict[str, Any]:
        return {
            **self.purge_control.status(),
            "api_requires_empty_intent_object": True,
            "api_derives_i31_request_from_durable_i44_i30": True,
            "api_can_override_i44_receipt": False,
            "api_can_override_i30_promotion_identity": False,
            "api_can_override_i29_validation_identity": False,
            "api_can_override_i31_purge_scope": False,
            "api_can_supply_raw_source_payload": False,
            "api_can_supply_managed_buffer_payload": False,
            "api_persists_i31_request_payload": False,
            "api_invokes_i32": False,
            "api_advances_curriculum": False,
            "api_invokes_canonical_learning": False,
            "api_promotes_truth": False,
            "api_mints_action_authority": False,
        }


def install_pass218_i45_manifest_bound_i31_verbatim_purge_control(
    app: Any,
    i44_control: Any,
    i31_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I45RuntimeManifestBoundI31VerbatimPurgeControl:
    existing = getattr(app.state, PASS218_I45_STATE_KEY, None)
    if isinstance(existing, Pass218I45RuntimeManifestBoundI31VerbatimPurgeControl):
        return existing

    control = Pass218I45RuntimeManifestBoundI31VerbatimPurgeControl(
        i44_control,
        i31_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I45_STATE_KEY, control)

    managed_paths = {PASS218_I45_STATUS_PATH, PASS218_I45_PURGE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def manifest_bound_i31_verbatim_purge_status() -> dict[str, Any]:
        return control.status()

    async def purge_manifest_bound_i44_promotion(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.purge(payload)
        except (
            Pass218I45PurgeError,
            Pass218I45BindingError,
            Pass218I45StateError,
            Pass218I31PurgeError,
        ) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except (ValueError, TypeError, KeyError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I45_STATUS_PATH,
        manifest_bound_i31_verbatim_purge_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-bound-i31-verbatim-purge-status-i45",
    )
    app.add_api_route(
        PASS218_I45_PURGE_PATH,
        purge_manifest_bound_i44_promotion,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-bound-i31-verbatim-purge-i45",
    )
    return control


__all__ = [
    "PASS218_I45_PURGE_PATH",
    "PASS218_I45_SCOPE",
    "PASS218_I45_STATE_KEY",
    "PASS218_I45_STATUS_PATH",
    "PASS218_I45_STORE_DIRNAME",
    "PASS218_I45_VERSION",
    "Pass218I45RuntimeManifestBoundI31VerbatimPurgeControl",
    "install_pass218_i45_manifest_bound_i31_verbatim_purge_control",
]

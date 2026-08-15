"""RuntimeOS composition for Pass 218 Iteration 39 manifest-bound I6 prepare ingress."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from hhs_runtime.pass218.manifest_bound_canonical_prepare_i39 import (
    PASS218_I39_SCOPE,
    PASS218_I39_VERSION,
    Pass218I39BindingError,
    Pass218I39CanonicalPrepareError,
    Pass218I39I6Error,
    Pass218I39ManifestBoundCanonicalPrepare,
    Pass218I39StateError,
)

PASS218_I39_STATUS_PATH = (
    "/api/runtime/pass218/cognition/manifest-canonical-prepare/status"
)
PASS218_I39_PREPARE_PATH = (
    "/api/runtime/pass218/cognition/manifest-canonical-prepare/prepare"
)
PASS218_I39_STATE_KEY = "hhs_pass218_manifest_canonical_prepare_i39"
PASS218_I39_STORE_DIRNAME = "cognition/manifest-canonical-prepare-i39"


class Pass218I39RuntimeManifestCanonicalPrepareControl:
    """RuntimeOS membrane from exact I38 authorization into frozen I6 prepare only."""

    def __init__(
        self,
        i38_control: Any,
        i36_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i38_control = i38_control
        self.i36_control = i36_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I39_STORE_DIRNAME
        self.prepare_membrane = Pass218I39ManifestBoundCanonicalPrepare(
            lifecycle=lifecycle,
            i38_store=i38_control.authorization.store,
            i37_store=i38_control.i37_control.proof.store,
            i36_store=i36_control.staging.store,
            state_root=self.store_root,
            i38_status_provider=i38_control.status,
            i36_status_provider=i36_control.status,
        )

    def prepare(self) -> dict[str, Any]:
        return self.prepare_membrane.prepare()

    def status(self) -> dict[str, Any]:
        return {
            **self.prepare_membrane.status(),
            "api_can_supply_source_payload": False,
            "api_can_supply_manifest_binding": False,
            "api_can_supply_i38_authorization": False,
            "api_can_supply_i37_proof": False,
            "api_can_supply_i36_stage": False,
            "api_can_supply_projection": False,
            "api_can_override_canonical_target_root": False,
            "api_can_invoke_i6_canonical_commit": False,
            "api_can_invoke_i7_durable_persistence": False,
            "api_can_invoke_i30_canonical_promotion": False,
            "api_can_mutate_authoritative_vector_store": False,
            "api_can_invoke_canonical_vm81_commit": False,
            "api_can_invoke_canonical_learning": False,
            "api_can_advance_curriculum": False,
            "api_can_advance_curriculum_stage": False,
            "api_can_invoke_i31_or_i32": False,
            "request_source_payload_persisted": False,
        }


def install_pass218_i39_manifest_canonical_prepare_control(
    app: Any,
    i38_control: Any,
    i36_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I39RuntimeManifestCanonicalPrepareControl:
    existing = getattr(app.state, PASS218_I39_STATE_KEY, None)
    if isinstance(existing, Pass218I39RuntimeManifestCanonicalPrepareControl):
        return existing

    control = Pass218I39RuntimeManifestCanonicalPrepareControl(
        i38_control,
        i36_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I39_STATE_KEY, control)

    managed_paths = {PASS218_I39_STATUS_PATH, PASS218_I39_PREPARE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def manifest_canonical_prepare_status() -> dict[str, Any]:
        return control.status()

    async def prepare_manifest_bound_canonical_admission() -> dict[str, Any]:
        try:
            return control.prepare()
        except Pass218I39BindingError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except (
            Pass218I39I6Error,
            Pass218I39StateError,
            Pass218I39CanonicalPrepareError,
        ) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I39_STATUS_PATH,
        manifest_canonical_prepare_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-canonical-prepare-status-i39",
    )
    app.add_api_route(
        PASS218_I39_PREPARE_PATH,
        prepare_manifest_bound_canonical_admission,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-canonical-prepare-prepare-i39",
    )
    return control


__all__ = [
    "PASS218_I39_PREPARE_PATH",
    "PASS218_I39_SCOPE",
    "PASS218_I39_STATE_KEY",
    "PASS218_I39_STATUS_PATH",
    "PASS218_I39_STORE_DIRNAME",
    "PASS218_I39_VERSION",
    "Pass218I39RuntimeManifestCanonicalPrepareControl",
    "install_pass218_i39_manifest_canonical_prepare_control",
]

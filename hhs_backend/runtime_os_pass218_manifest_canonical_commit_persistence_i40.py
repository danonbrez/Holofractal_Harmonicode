"""RuntimeOS composition for Pass 218 Iteration 40 canonical commit persistence."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from hhs_runtime.pass218.manifest_bound_canonical_commit_persistence_i40 import (
    PASS218_I40_SCOPE,
    PASS218_I40_VERSION,
    Pass218I40BindingError,
    Pass218I40CanonicalPersistenceError,
    Pass218I40I6Error,
    Pass218I40I7Error,
    Pass218I40ManifestBoundCanonicalCommitPersistence,
    Pass218I40StateError,
)

PASS218_I40_STATUS_PATH = (
    "/api/runtime/pass218/cognition/manifest-canonical-commit-persistence/status"
)
PASS218_I40_COMMIT_PATH = (
    "/api/runtime/pass218/cognition/manifest-canonical-commit-persistence/commit"
)
PASS218_I40_STATE_KEY = "hhs_pass218_manifest_canonical_commit_persistence_i40"
PASS218_I40_STORE_DIRNAME = "cognition/manifest-canonical-commit-persistence-i40"


class Pass218I40RuntimeManifestCanonicalCommitPersistenceControl:
    """RuntimeOS membrane from exact I39 prepare into frozen I6+I7 only."""

    def __init__(
        self,
        i39_control: Any,
        i38_control: Any,
        i36_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i39_control = i39_control
        self.i38_control = i38_control
        self.i36_control = i36_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I40_STORE_DIRNAME
        self.commit_membrane = Pass218I40ManifestBoundCanonicalCommitPersistence(
            lifecycle=lifecycle,
            i39_store=i39_control.prepare_membrane.store,
            i38_store=i38_control.authorization.store,
            i37_store=i38_control.i37_control.proof.store,
            i36_store=i36_control.staging.store,
            state_root=self.store_root,
            i39_status_provider=i39_control.status,
        )

    def commit_and_persist(self) -> dict[str, Any]:
        return self.commit_membrane.commit_and_persist()

    def status(self) -> dict[str, Any]:
        return {
            **self.commit_membrane.status(),
            "api_can_supply_source_payload": False,
            "api_can_supply_manifest_binding": False,
            "api_can_supply_i39_prepare": False,
            "api_can_supply_i38_authorization": False,
            "api_can_supply_i36_stage": False,
            "api_can_supply_projection": False,
            "api_can_override_canonical_target_root": False,
            "api_can_select_i6_commit_receipt": False,
            "api_can_select_i7_checkpoint": False,
            "api_can_invoke_i30_canonical_promotion": False,
            "api_can_invoke_canonical_learning": False,
            "api_can_promote_truth": False,
            "api_can_mint_action_authority": False,
            "api_can_advance_curriculum": False,
            "api_can_advance_curriculum_stage": False,
            "api_can_invoke_i31_or_i32": False,
            "request_source_payload_persisted": False,
        }


def install_pass218_i40_manifest_canonical_commit_persistence_control(
    app: Any,
    i39_control: Any,
    i38_control: Any,
    i36_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I40RuntimeManifestCanonicalCommitPersistenceControl:
    existing = getattr(app.state, PASS218_I40_STATE_KEY, None)
    if isinstance(existing, Pass218I40RuntimeManifestCanonicalCommitPersistenceControl):
        return existing

    control = Pass218I40RuntimeManifestCanonicalCommitPersistenceControl(
        i39_control,
        i38_control,
        i36_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I40_STATE_KEY, control)

    managed_paths = {PASS218_I40_STATUS_PATH, PASS218_I40_COMMIT_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def manifest_canonical_commit_persistence_status() -> dict[str, Any]:
        return control.status()

    async def commit_manifest_bound_canonical_admission() -> dict[str, Any]:
        try:
            return control.commit_and_persist()
        except Pass218I40BindingError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except (
            Pass218I40I6Error,
            Pass218I40I7Error,
            Pass218I40StateError,
            Pass218I40CanonicalPersistenceError,
        ) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I40_STATUS_PATH,
        manifest_canonical_commit_persistence_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-canonical-commit-persistence-status-i40",
    )
    app.add_api_route(
        PASS218_I40_COMMIT_PATH,
        commit_manifest_bound_canonical_admission,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-canonical-commit-persistence-commit-i40",
    )
    return control


__all__ = [
    "PASS218_I40_COMMIT_PATH",
    "PASS218_I40_SCOPE",
    "PASS218_I40_STATE_KEY",
    "PASS218_I40_STATUS_PATH",
    "PASS218_I40_STORE_DIRNAME",
    "PASS218_I40_VERSION",
    "Pass218I40RuntimeManifestCanonicalCommitPersistenceControl",
    "install_pass218_i40_manifest_canonical_commit_persistence_control",
]

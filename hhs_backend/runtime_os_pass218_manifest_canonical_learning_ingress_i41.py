"""RuntimeOS composition for Pass 218 Iteration 41 canonical learning ingress."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from hhs_runtime.pass218.manifest_bound_canonical_learning_ingress_i41 import (
    PASS218_I41_SCOPE,
    PASS218_I41_VERSION,
    Pass218I41BindingError,
    Pass218I41CanonicalLearningIngressError,
    Pass218I41ManifestBoundCanonicalLearningIngress,
    Pass218I41StateError,
)

PASS218_I41_STATUS_PATH = "/api/runtime/pass218/cognition/manifest-canonical-learning-ingress/status"
PASS218_I41_ADMIT_PATH = "/api/runtime/pass218/cognition/manifest-canonical-learning-ingress/admit"
PASS218_I41_STATE_KEY = "hhs_pass218_manifest_canonical_learning_ingress_i41"
PASS218_I41_STORE_DIRNAME = "cognition/manifest-canonical-learning-ingress-i41"


class Pass218I41RuntimeManifestCanonicalLearningIngressControl:
    """Parameterless RuntimeOS membrane from exact I40 durability into I41 only."""

    def __init__(self, i40_control: Any, i30_control: Any, *, lifecycle: Any, state_root: str | os.PathLike[str]) -> None:
        self.i40_control = i40_control
        self.i30_control = i30_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I41_STORE_DIRNAME
        self.ingress = Pass218I41ManifestBoundCanonicalLearningIngress(
            lifecycle=lifecycle,
            i40_store=i40_control.commit_membrane.store,
            state_root=self.store_root,
            i40_status_provider=i40_control.status,
            i30_status_provider=i30_control.status,
        )

    def admit(self) -> dict[str, Any]:
        return self.ingress.admit()

    def status(self) -> dict[str, Any]:
        return {
            **self.ingress.status(),
            "api_can_supply_source_payload": False,
            "api_can_supply_manifest_binding": False,
            "api_can_supply_i40_receipt": False,
            "api_can_override_canonical_root": False,
            "api_can_supply_i27_state": False,
            "api_can_supply_i28_transition": False,
            "api_can_supply_i29_validation": False,
            "api_can_supply_i30_authority_grant": False,
            "api_can_invoke_i30_canonical_promotion": False,
            "api_can_invoke_i31_or_i32": False,
            "api_can_invoke_canonical_learning": False,
            "api_can_promote_truth": False,
            "api_can_mint_action_authority": False,
            "api_can_advance_curriculum": False,
            "api_can_advance_curriculum_stage": False,
            "request_source_payload_persisted": False,
        }


def install_pass218_i41_manifest_canonical_learning_ingress_control(
    app: Any,
    i40_control: Any,
    i30_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I41RuntimeManifestCanonicalLearningIngressControl:
    existing = getattr(app.state, PASS218_I41_STATE_KEY, None)
    if isinstance(existing, Pass218I41RuntimeManifestCanonicalLearningIngressControl):
        return existing

    control = Pass218I41RuntimeManifestCanonicalLearningIngressControl(
        i40_control,
        i30_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I41_STATE_KEY, control)

    managed_paths = {PASS218_I41_STATUS_PATH, PASS218_I41_ADMIT_PATH}
    app.router.routes[:] = [route for route in app.router.routes if str(getattr(route, "path", "")) not in managed_paths]

    async def manifest_canonical_learning_ingress_status() -> dict[str, Any]:
        return control.status()

    async def admit_manifest_bound_canonical_learning_ingress() -> dict[str, Any]:
        try:
            return control.admit()
        except (Pass218I41BindingError, Pass218I41StateError, Pass218I41CanonicalLearningIngressError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I41_STATUS_PATH,
        manifest_canonical_learning_ingress_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-canonical-learning-ingress-status-i41",
    )
    app.add_api_route(
        PASS218_I41_ADMIT_PATH,
        admit_manifest_bound_canonical_learning_ingress,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-canonical-learning-ingress-admit-i41",
    )
    return control


__all__ = [
    "PASS218_I41_ADMIT_PATH",
    "PASS218_I41_SCOPE",
    "PASS218_I41_STATE_KEY",
    "PASS218_I41_STATUS_PATH",
    "PASS218_I41_STORE_DIRNAME",
    "PASS218_I41_VERSION",
    "Pass218I41RuntimeManifestCanonicalLearningIngressControl",
    "install_pass218_i41_manifest_canonical_learning_ingress_control",
]

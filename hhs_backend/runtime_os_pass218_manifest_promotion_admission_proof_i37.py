"""RuntimeOS composition for Pass 218 Iteration 37 manifest-bound I5 proof ingress."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from hhs_runtime.pass218.manifest_bound_promotion_admission_proof_i37 import (
    PASS218_I37_SCOPE,
    PASS218_I37_VERSION,
    Pass218I37BindingError,
    Pass218I37I5Error,
    Pass218I37ManifestBoundPromotionAdmissionProof,
    Pass218I37ProofIngressError,
    Pass218I37StateError,
)

PASS218_I37_STATUS_PATH = (
    "/api/runtime/pass218/cognition/manifest-promotion-admission-proof/status"
)
PASS218_I37_PROVE_PATH = (
    "/api/runtime/pass218/cognition/manifest-promotion-admission-proof/prove"
)
PASS218_I37_STATE_KEY = "hhs_pass218_manifest_promotion_admission_proof_i37"
PASS218_I37_STORE_DIRNAME = "cognition/manifest-promotion-admission-proof-i37"


class Pass218I37RuntimeManifestPromotionAdmissionProofControl:
    """RuntimeOS membrane from exact durable I36 state into frozen I5 prove only."""

    def __init__(
        self,
        i36_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i36_control = i36_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I37_STORE_DIRNAME
        self.proof = Pass218I37ManifestBoundPromotionAdmissionProof(
            lifecycle=lifecycle,
            i36_store=i36_control.staging.store,
            i35_store=i36_control.i35_control.ingress.store,
            state_root=self.store_root,
            i36_status_provider=i36_control.status,
        )

    def prove(self) -> dict[str, Any]:
        return self.proof.prove()

    def status(self) -> dict[str, Any]:
        return {
            **self.proof.status(),
            "api_can_supply_source_payload": False,
            "api_can_supply_semantic_candidate": False,
            "api_can_supply_manifest_binding": False,
            "api_can_override_i36_receipt": False,
            "api_can_override_i4_candidate": False,
            "api_can_supply_grantor_authority": False,
            "api_can_supply_promotion_grant": False,
            "api_can_invoke_promotion_authorization": False,
            "api_can_invoke_i6_canonical_commit": False,
            "api_can_invoke_i30_canonical_promotion": False,
            "api_can_invoke_vm81_authority": False,
            "api_can_advance_curriculum": False,
            "api_can_advance_curriculum_stage": False,
            "api_can_invoke_i31_or_i32": False,
            "request_source_payload_persisted": False,
        }


def install_pass218_i37_manifest_promotion_admission_proof_control(
    app: Any,
    i36_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I37RuntimeManifestPromotionAdmissionProofControl:
    existing = getattr(app.state, PASS218_I37_STATE_KEY, None)
    if isinstance(existing, Pass218I37RuntimeManifestPromotionAdmissionProofControl):
        return existing

    control = Pass218I37RuntimeManifestPromotionAdmissionProofControl(
        i36_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I37_STATE_KEY, control)

    managed_paths = {PASS218_I37_STATUS_PATH, PASS218_I37_PROVE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def manifest_promotion_admission_proof_status() -> dict[str, Any]:
        return control.status()

    async def prove_manifest_bound_promotability() -> dict[str, Any]:
        try:
            return control.prove()
        except Pass218I37BindingError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except (
            Pass218I37I5Error,
            Pass218I37StateError,
            Pass218I37ProofIngressError,
        ) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I37_STATUS_PATH,
        manifest_promotion_admission_proof_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-promotion-admission-proof-status-i37",
    )
    app.add_api_route(
        PASS218_I37_PROVE_PATH,
        prove_manifest_bound_promotability,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-promotion-admission-proof-prove-i37",
    )
    return control


__all__ = [
    "PASS218_I37_PROVE_PATH",
    "PASS218_I37_SCOPE",
    "PASS218_I37_STATE_KEY",
    "PASS218_I37_STATUS_PATH",
    "PASS218_I37_STORE_DIRNAME",
    "PASS218_I37_VERSION",
    "Pass218I37RuntimeManifestPromotionAdmissionProofControl",
    "install_pass218_i37_manifest_promotion_admission_proof_control",
]

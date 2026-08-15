"""RuntimeOS composition for Pass 218 Iteration 38 manifest-bound I5 authorization ingress."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from hhs_runtime.pass218.manifest_bound_promotion_authorization_i38 import (
    PASS218_I38_SCOPE,
    PASS218_I38_VERSION,
    Pass218I38AuthorizationIngressError,
    Pass218I38BindingError,
    Pass218I38I5Error,
    Pass218I38ManifestBoundPromotionAuthorization,
    Pass218I38StateError,
)

PASS218_I38_STATUS_PATH = (
    "/api/runtime/pass218/cognition/manifest-promotion-authorization/status"
)
PASS218_I38_AUTHORIZE_PATH = (
    "/api/runtime/pass218/cognition/manifest-promotion-authorization/authorize"
)
PASS218_I38_STATE_KEY = "hhs_pass218_manifest_promotion_authorization_i38"
PASS218_I38_STORE_DIRNAME = "cognition/manifest-promotion-authorization-i38"


class Pass218I38RuntimeManifestPromotionAuthorizationControl:
    """RuntimeOS membrane from exact durable I37 proof into frozen I5 authorization only."""

    def __init__(
        self,
        i37_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i37_control = i37_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I38_STORE_DIRNAME
        self.authorization = Pass218I38ManifestBoundPromotionAuthorization(
            lifecycle=lifecycle,
            i37_store=i37_control.proof.store,
            state_root=self.store_root,
            i37_status_provider=i37_control.status,
        )

    def authorize(self) -> dict[str, Any]:
        return self.authorization.authorize()

    def status(self) -> dict[str, Any]:
        return {
            **self.authorization.status(),
            "api_can_supply_source_payload": False,
            "api_can_supply_semantic_candidate": False,
            "api_can_supply_manifest_binding": False,
            "api_can_override_i37_receipt": False,
            "api_can_override_i5_proof": False,
            "api_can_supply_grantor_authority": False,
            "api_can_supply_grant_sequence": False,
            "api_can_supply_promotion_grant": False,
            "api_can_invoke_i6_canonical_commit": False,
            "api_can_invoke_i30_canonical_promotion": False,
            "api_can_invoke_vm81_authority": False,
            "api_can_advance_curriculum": False,
            "api_can_advance_curriculum_stage": False,
            "api_can_invoke_i31_or_i32": False,
            "request_source_payload_persisted": False,
        }


def install_pass218_i38_manifest_promotion_authorization_control(
    app: Any,
    i37_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I38RuntimeManifestPromotionAuthorizationControl:
    existing = getattr(app.state, PASS218_I38_STATE_KEY, None)
    if isinstance(existing, Pass218I38RuntimeManifestPromotionAuthorizationControl):
        return existing

    control = Pass218I38RuntimeManifestPromotionAuthorizationControl(
        i37_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I38_STATE_KEY, control)

    managed_paths = {PASS218_I38_STATUS_PATH, PASS218_I38_AUTHORIZE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def manifest_promotion_authorization_status() -> dict[str, Any]:
        return control.status()

    async def authorize_manifest_bound_promotion() -> dict[str, Any]:
        try:
            return control.authorize()
        except Pass218I38BindingError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except (
            Pass218I38I5Error,
            Pass218I38StateError,
            Pass218I38AuthorizationIngressError,
        ) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I38_STATUS_PATH,
        manifest_promotion_authorization_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-promotion-authorization-status-i38",
    )
    app.add_api_route(
        PASS218_I38_AUTHORIZE_PATH,
        authorize_manifest_bound_promotion,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-promotion-authorization-authorize-i38",
    )
    return control


__all__ = [
    "PASS218_I38_AUTHORIZE_PATH",
    "PASS218_I38_SCOPE",
    "PASS218_I38_STATE_KEY",
    "PASS218_I38_STATUS_PATH",
    "PASS218_I38_STORE_DIRNAME",
    "PASS218_I38_VERSION",
    "Pass218I38RuntimeManifestPromotionAuthorizationControl",
    "install_pass218_i38_manifest_promotion_authorization_control",
]

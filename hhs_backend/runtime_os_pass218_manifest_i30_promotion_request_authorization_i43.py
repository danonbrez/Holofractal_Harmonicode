"""RuntimeOS composition for Pass 218 Iteration 43 I30 request authorization."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from fastapi import HTTPException

from hhs_runtime.pass218.atomic_semantic_promotion_i30 import Pass218I30PromotionError
from hhs_runtime.pass218.manifest_bound_i30_promotion_request_authorization_i43 import (
    PASS218_I43_SCOPE,
    PASS218_I43_VERSION,
    Pass218I43AuthorizationError,
    Pass218I43BindingError,
    Pass218I43ManifestBoundI30PromotionRequestAuthorization,
    Pass218I43StateError,
)

PASS218_I43_STATUS_PATH = (
    "/api/runtime/pass218/cognition/manifest-bound-i30-promotion-request-authorization/status"
)
PASS218_I43_AUTHORIZE_PATH = (
    "/api/runtime/pass218/cognition/manifest-bound-i30-promotion-request-authorization/authorize"
)
PASS218_I43_STATE_KEY = "hhs_pass218_manifest_bound_i30_promotion_request_authorization_i43"
PASS218_I43_STORE_DIRNAME = "cognition/manifest-bound-i30-promotion-request-authorization-i43"


class Pass218I43RuntimeManifestBoundI30PromotionRequestAuthorizationControl:
    """Non-executing typed-I30 authorization membrane over exact durable I42 state."""

    def __init__(
        self,
        i42_control: Any,
        i29_control: Any,
        i30_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i42_control = i42_control
        self.i29_control = i29_control
        self.i30_control = i30_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I43_STORE_DIRNAME
        self.authorization = Pass218I43ManifestBoundI30PromotionRequestAuthorization(
            lifecycle=lifecycle,
            i42_store=i42_control.equality.store,
            i29_validator=i29_control.validator,
            state_root=self.store_root,
            i42_status_provider=i42_control.status,
            i30_status_provider=i30_control.status,
        )

    def authorize(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        request = self.i30_control._request(payload)
        return self.authorization.authorize(request)

    def status(self) -> dict[str, Any]:
        return {
            **self.authorization.status(),
            "api_can_supply_transient_i29_validation_request": True,
            "api_can_supply_i30_authority_grant": True,
            "api_can_authorize_exact_i30_promotion_request": True,
            "api_can_supply_raw_source_payload": False,
            "api_can_supply_i42_receipt": False,
            "api_can_override_i42_request_fingerprint": False,
            "api_can_supply_i29_validation_result": False,
            "api_can_override_i29_validation_identity": False,
            "api_can_override_i30_target_scope": False,
            "api_can_invoke_i30_canonical_promotion": False,
            "api_can_invoke_i31_or_i32": False,
            "api_can_invoke_canonical_learning": False,
            "api_can_promote_truth": False,
            "api_can_mint_action_authority": False,
            "api_can_advance_curriculum": False,
            "api_can_advance_curriculum_stage": False,
            "i29_request_payload_persisted": False,
            "i30_request_payload_persisted": False,
        }


def install_pass218_i43_manifest_bound_i30_promotion_request_authorization_control(
    app: Any,
    i42_control: Any,
    i29_control: Any,
    i30_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I43RuntimeManifestBoundI30PromotionRequestAuthorizationControl:
    existing = getattr(app.state, PASS218_I43_STATE_KEY, None)
    if isinstance(
        existing,
        Pass218I43RuntimeManifestBoundI30PromotionRequestAuthorizationControl,
    ):
        return existing

    control = Pass218I43RuntimeManifestBoundI30PromotionRequestAuthorizationControl(
        i42_control,
        i29_control,
        i30_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I43_STATE_KEY, control)

    managed_paths = {PASS218_I43_STATUS_PATH, PASS218_I43_AUTHORIZE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def manifest_bound_i30_request_authorization_status() -> dict[str, Any]:
        return control.status()

    async def authorize_manifest_bound_i30_promotion_request(
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            return control.authorize(payload)
        except (
            Pass218I43AuthorizationError,
            Pass218I43BindingError,
            Pass218I43StateError,
            Pass218I30PromotionError,
        ) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except (ValueError, TypeError, KeyError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I43_STATUS_PATH,
        manifest_bound_i30_request_authorization_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-bound-i30-promotion-request-authorization-status-i43",
    )
    app.add_api_route(
        PASS218_I43_AUTHORIZE_PATH,
        authorize_manifest_bound_i30_promotion_request,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-bound-i30-promotion-request-authorization-i43",
    )
    return control


__all__ = [
    "PASS218_I43_AUTHORIZE_PATH",
    "PASS218_I43_SCOPE",
    "PASS218_I43_STATE_KEY",
    "PASS218_I43_STATUS_PATH",
    "PASS218_I43_STORE_DIRNAME",
    "PASS218_I43_VERSION",
    "Pass218I43RuntimeManifestBoundI30PromotionRequestAuthorizationControl",
    "install_pass218_i43_manifest_bound_i30_promotion_request_authorization_control",
]
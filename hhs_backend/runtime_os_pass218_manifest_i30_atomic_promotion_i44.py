"""RuntimeOS composition for Pass 218 Iteration 44 manifest-bound I30 promotion."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from fastapi import HTTPException

from hhs_runtime.pass218.atomic_semantic_promotion_i30 import Pass218I30PromotionError
from hhs_runtime.pass218.manifest_bound_i30_atomic_promotion_i44 import (
    PASS218_I44_SCOPE,
    PASS218_I44_VERSION,
    Pass218I44BindingError,
    Pass218I44ManifestBoundI30AtomicPromotion,
    Pass218I44PromotionError,
    Pass218I44StateError,
)

PASS218_I44_STATUS_PATH = "/api/runtime/pass218/cognition/manifest-bound-i30-atomic-promotion/status"
PASS218_I44_PROMOTE_PATH = "/api/runtime/pass218/cognition/manifest-bound-i30-atomic-promotion/promote"
PASS218_I44_STATE_KEY = "hhs_pass218_manifest_bound_i30_atomic_promotion_i44"
PASS218_I44_STORE_DIRNAME = "cognition/manifest-bound-i30-atomic-promotion-i44"


class Pass218I44RuntimeManifestBoundI30AtomicPromotionControl:
    """One-time I30 invocation membrane over exact durable I43 authority."""

    def __init__(
        self,
        i43_control: Any,
        i30_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i43_control = i43_control
        self.i30_control = i30_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I44_STORE_DIRNAME
        self.promotion = Pass218I44ManifestBoundI30AtomicPromotion(
            lifecycle=lifecycle,
            i43_store=i43_control.authorization.store,
            i30_promoter=i30_control.promoter,
            state_root=self.store_root,
        )

    def promote(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        request = self.i30_control._request(payload)
        return self.promotion.promote(request)

    def status(self) -> dict[str, Any]:
        return {
            **self.promotion.status(),
            "api_requires_exact_transient_i30_request": True,
            "api_requires_durable_i43_authorization": True,
            "api_can_override_i43_authorization": False,
            "api_can_override_i30_grant_identity": False,
            "api_can_supply_i30_validation_result": False,
            "api_can_supply_raw_source_payload": False,
            "api_persists_i30_request_payload": False,
            "api_invokes_i31_or_i32": False,
            "api_advances_curriculum": False,
            "api_invokes_canonical_learning": False,
            "api_promotes_truth": False,
            "api_mints_action_authority": False,
        }


def install_pass218_i44_manifest_bound_i30_atomic_promotion_control(
    app: Any,
    i43_control: Any,
    i30_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I44RuntimeManifestBoundI30AtomicPromotionControl:
    existing = getattr(app.state, PASS218_I44_STATE_KEY, None)
    if isinstance(existing, Pass218I44RuntimeManifestBoundI30AtomicPromotionControl):
        return existing

    control = Pass218I44RuntimeManifestBoundI30AtomicPromotionControl(
        i43_control,
        i30_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I44_STATE_KEY, control)

    managed_paths = {PASS218_I44_STATUS_PATH, PASS218_I44_PROMOTE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def manifest_bound_i30_atomic_promotion_status() -> dict[str, Any]:
        return control.status()

    async def promote_manifest_bound_i30_candidate(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.promote(payload)
        except (
            Pass218I44PromotionError,
            Pass218I44BindingError,
            Pass218I44StateError,
            Pass218I30PromotionError,
        ) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except (ValueError, TypeError, KeyError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I44_STATUS_PATH,
        manifest_bound_i30_atomic_promotion_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-bound-i30-atomic-promotion-status-i44",
    )
    app.add_api_route(
        PASS218_I44_PROMOTE_PATH,
        promote_manifest_bound_i30_candidate,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-bound-i30-atomic-promotion-i44",
    )
    return control


__all__ = [
    "PASS218_I44_PROMOTE_PATH",
    "PASS218_I44_SCOPE",
    "PASS218_I44_STATE_KEY",
    "PASS218_I44_STATUS_PATH",
    "PASS218_I44_STORE_DIRNAME",
    "PASS218_I44_VERSION",
    "Pass218I44RuntimeManifestBoundI30AtomicPromotionControl",
    "install_pass218_i44_manifest_bound_i30_atomic_promotion_control",
]
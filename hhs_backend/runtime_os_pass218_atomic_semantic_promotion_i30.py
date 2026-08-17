"""RuntimeOS composition for Pass 218 Iteration 30 atomic semantic promotion."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from fastapi import HTTPException

from hhs_backend.runtime_os_pass218_hash216_vm5184_validation_i29 import (
    Pass218I29RuntimeValidationControl,
)
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import (
    PASS218_I30_PROMOTION_VERSION,
    PASS218_I30_TARGET_SCOPE,
    Pass218I30AtomicSemanticPromoter,
    Pass218I30PromotionError,
    Pass218I30PromotionRequest,
)

PASS218_I30_STATUS_PATH = "/api/runtime/pass218/cognition/atomic-semantic-promotion/status"
PASS218_I30_PROMOTE_PATH = "/api/runtime/pass218/cognition/atomic-semantic-promotion/promote"
PASS218_I30_STATE_KEY = "hhs_pass218_atomic_semantic_promotion_i30"
PASS218_I30_STORE_DIRNAME = "cognition/atomic-semantic-promotion-i30"


class Pass218I30RuntimePromotionControl:
    """Fenced browser membrane around the exact I30 promotion runtime."""

    def __init__(
        self,
        i29_control: Any,
        i27_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
        native_bridge: Any | None = None,
    ) -> None:
        self.i29_control = i29_control
        self.i27_control = i27_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I30_STORE_DIRNAME
        self.promoter = Pass218I30AtomicSemanticPromoter(
            i29_control.validator,
            i27_control.differentiator,
            lifecycle=lifecycle,
            store_root=self.store_root,
            native_bridge=native_bridge,
        )

    @staticmethod
    def _request(payload: Mapping[str, Any]) -> Pass218I30PromotionRequest:
        validation_request = Pass218I29RuntimeValidationControl._request(payload)
        authority = payload.get("promotion_authority")
        if not isinstance(authority, Mapping):
            raise Pass218I30PromotionError("P218_I30_PROMOTION_AUTHORITY_REQUIRED")
        return Pass218I30PromotionRequest(
            validation_request=validation_request,
            grantor_authority_hash72=str(authority.get("grantor_authority_hash72") or ""),
            grant_sequence=authority.get("grant_sequence"),
            expected_i29_validation_hash72=str(
                authority.get("expected_i29_validation_hash72") or ""
            ),
            expected_validated_hash216=str(
                authority.get("expected_validated_hash216") or ""
            ),
            target_scope=str(authority.get("target_scope") or PASS218_I30_TARGET_SCOPE),
        ).validated()

    def promote(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.promoter.promote(self._request(payload))

    def status(self) -> dict[str, Any]:
        return self.promoter.status()


def install_pass218_i30_atomic_semantic_promotion_control(
    app: Any,
    i29_control: Any,
    i27_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I30RuntimePromotionControl:
    existing = getattr(app.state, PASS218_I30_STATE_KEY, None)
    if isinstance(existing, Pass218I30RuntimePromotionControl):
        return existing

    control = Pass218I30RuntimePromotionControl(
        i29_control,
        i27_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I30_STATE_KEY, control)

    managed_paths = {PASS218_I30_STATUS_PATH, PASS218_I30_PROMOTE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def promotion_status() -> dict[str, Any]:
        return control.status()

    async def promote_semantic_candidate(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.promote(payload)
        except Pass218I30PromotionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I30_STATUS_PATH,
        promotion_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-atomic-semantic-promotion-status-i30",
    )
    app.add_api_route(
        PASS218_I30_PROMOTE_PATH,
        promote_semantic_candidate,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-atomic-semantic-promotion-i30",
    )
    return control


__all__ = [
    "PASS218_I30_PROMOTE_PATH",
    "PASS218_I30_STATE_KEY",
    "PASS218_I30_STATUS_PATH",
    "PASS218_I30_STORE_DIRNAME",
    "PASS218_I30_PROMOTION_VERSION",
    "Pass218I30RuntimePromotionControl",
    "install_pass218_i30_atomic_semantic_promotion_control",
]

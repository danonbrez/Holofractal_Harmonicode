"""RuntimeOS composition for Pass 218 Iteration 42 cross-lineage equality."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from fastapi import HTTPException

from hhs_runtime.pass218.manifest_semantic_cross_lineage_equality_i42 import (
    PASS218_I42_SCOPE,
    PASS218_I42_VERSION,
    Pass218I42BindingError,
    Pass218I42CrossLineageError,
    Pass218I42ManifestSemanticCrossLineageEquality,
    Pass218I42StateError,
)

PASS218_I42_STATUS_PATH = "/api/runtime/pass218/cognition/manifest-semantic-cross-lineage-equality/status"
PASS218_I42_PROVE_PATH = "/api/runtime/pass218/cognition/manifest-semantic-cross-lineage-equality/prove"
PASS218_I42_STATE_KEY = "hhs_pass218_manifest_semantic_cross_lineage_equality_i42"
PASS218_I42_STORE_DIRNAME = "cognition/manifest-semantic-cross-lineage-equality-i42"


class Pass218I42RuntimeManifestSemanticCrossLineageEqualityControl:
    """Transient typed-I29 request membrane over exact durable I41 state."""

    def __init__(
        self,
        i41_control: Any,
        i29_control: Any,
        i30_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i41_control = i41_control
        self.i29_control = i29_control
        self.i30_control = i30_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I42_STORE_DIRNAME
        self.equality = Pass218I42ManifestSemanticCrossLineageEquality(
            lifecycle=lifecycle,
            i41_store=i41_control.ingress.store,
            i29_validator=i29_control.validator,
            state_root=self.store_root,
            i41_status_provider=i41_control.status,
            i30_status_provider=i30_control.status,
        )

    def prove(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        request = self.i29_control._request(payload)
        return self.equality.prove(request)

    def status(self) -> dict[str, Any]:
        return {
            **self.equality.status(),
            "api_can_supply_transient_i29_validation_request": True,
            "api_can_supply_raw_source_payload": False,
            "api_can_supply_i41_receipt": False,
            "api_can_override_manifest_binding": False,
            "api_can_override_canonical_root": False,
            "api_can_supply_i29_validation_result": False,
            "api_can_supply_i30_authority_grant": False,
            "api_can_invoke_i30_canonical_promotion": False,
            "api_can_invoke_i31_or_i32": False,
            "api_can_invoke_canonical_learning": False,
            "api_can_promote_truth": False,
            "api_can_mint_action_authority": False,
            "api_can_advance_curriculum": False,
            "api_can_advance_curriculum_stage": False,
            "request_payload_persisted": False,
        }


def install_pass218_i42_manifest_semantic_cross_lineage_equality_control(
    app: Any,
    i41_control: Any,
    i29_control: Any,
    i30_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I42RuntimeManifestSemanticCrossLineageEqualityControl:
    existing = getattr(app.state, PASS218_I42_STATE_KEY, None)
    if isinstance(existing, Pass218I42RuntimeManifestSemanticCrossLineageEqualityControl):
        return existing

    control = Pass218I42RuntimeManifestSemanticCrossLineageEqualityControl(
        i41_control,
        i29_control,
        i30_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I42_STATE_KEY, control)

    managed_paths = {PASS218_I42_STATUS_PATH, PASS218_I42_PROVE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def manifest_semantic_cross_lineage_equality_status() -> dict[str, Any]:
        return control.status()

    async def prove_manifest_semantic_cross_lineage_equality(
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            return control.prove(payload)
        except (Pass218I42BindingError, Pass218I42StateError, Pass218I42CrossLineageError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except (ValueError, TypeError, KeyError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I42_STATUS_PATH,
        manifest_semantic_cross_lineage_equality_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-semantic-cross-lineage-equality-status-i42",
    )
    app.add_api_route(
        PASS218_I42_PROVE_PATH,
        prove_manifest_semantic_cross_lineage_equality,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-semantic-cross-lineage-equality-prove-i42",
    )
    return control


__all__ = [
    "PASS218_I42_PROVE_PATH",
    "PASS218_I42_SCOPE",
    "PASS218_I42_STATE_KEY",
    "PASS218_I42_STATUS_PATH",
    "PASS218_I42_STORE_DIRNAME",
    "PASS218_I42_VERSION",
    "Pass218I42RuntimeManifestSemanticCrossLineageEqualityControl",
    "install_pass218_i42_manifest_semantic_cross_lineage_equality_control",
]

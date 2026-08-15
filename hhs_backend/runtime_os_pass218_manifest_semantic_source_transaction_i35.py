"""RuntimeOS composition for Pass 218 Iteration 35 semantic/source ingress."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict

from hhs_runtime.pass218.manifest_bound_semantic_source_transaction_i35 import (
    PASS218_I35_SCOPE,
    PASS218_I35_VERSION,
    Pass218I35BindingError,
    Pass218I35IngressError,
    Pass218I35ManifestBoundSemanticSourceTransaction,
    Pass218I35StateError,
    Pass218I35TransactionError,
)

PASS218_I35_STATUS_PATH = (
    "/api/runtime/pass218/cognition/manifest-semantic-source-transaction/status"
)
PASS218_I35_INGEST_PATH = (
    "/api/runtime/pass218/cognition/manifest-semantic-source-transaction/ingest"
)
PASS218_I35_STATE_KEY = "hhs_pass218_manifest_semantic_source_transaction_i35"
PASS218_I35_STORE_DIRNAME = "cognition/manifest-semantic-source-transaction-i35"


class Pass218I35IngestPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_text: str
    semantic_candidate: dict[str, Any]


class Pass218I35RuntimeManifestSemanticTransactionControl:
    """RuntimeOS membrane over the I34 receipt and frozen I2/I3 candidate path."""

    def __init__(
        self,
        i34_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i34_control = i34_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I35_STORE_DIRNAME
        authority = i34_control.i33_control.advancer.authority
        genesis = None if authority is None else authority.manifest.genesis_seed_hash72
        self.ingress = Pass218I35ManifestBoundSemanticSourceTransaction(
            lifecycle=lifecycle,
            i34_store_root=i34_control.store_root,
            transaction_store_root=self.store_root,
            manifest_genesis_seed_hash72=genesis,
            i34_store=i34_control.ingress.store,
            i34_status_provider=i34_control.status,
        )

    @property
    def authority_configured(self) -> bool:
        return self.i34_control.i33_control.advancer.authority is not None

    def ingest(self, payload: Pass218I35IngestPayload) -> dict[str, Any]:
        if not self.authority_configured:
            raise Pass218I35BindingError(
                "P218_I35_AUTHORITATIVE_CURRICULUM_NOT_CONFIGURED"
            )
        return self.ingress.ingest(
            semantic_candidate=payload.semantic_candidate,
            source_bytes=payload.source_text.encode("utf-8"),
        )

    def status(self) -> dict[str, Any]:
        i33 = self.i34_control.i33_control
        return {
            **self.ingress.status(),
            "authority_configuration_error": i33.configuration_error,
            "authority_configuration_source": i33.status().get(
                "authority_configuration_source"
            ),
            "api_can_mint_curriculum_authority": False,
            "api_can_override_manifest_binding": False,
            "api_can_supply_curriculum_identity": False,
            "api_can_advance_curriculum": False,
            "api_can_advance_curriculum_stage": False,
            "api_can_promote_learning": False,
            "api_can_invoke_vm81_authority": False,
            "api_can_invoke_i31_or_i32": False,
            "request_source_payload_persisted": False,
        }


def install_pass218_i35_manifest_semantic_transaction_control(
    app: Any,
    i34_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I35RuntimeManifestSemanticTransactionControl:
    existing = getattr(app.state, PASS218_I35_STATE_KEY, None)
    if isinstance(existing, Pass218I35RuntimeManifestSemanticTransactionControl):
        return existing

    control = Pass218I35RuntimeManifestSemanticTransactionControl(
        i34_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I35_STATE_KEY, control)

    managed_paths = {PASS218_I35_STATUS_PATH, PASS218_I35_INGEST_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def manifest_semantic_source_transaction_status() -> dict[str, Any]:
        return control.status()

    async def ingest_manifest_semantic_source_transaction(
        payload: Pass218I35IngestPayload,
    ) -> dict[str, Any]:
        configuration_error = control.i34_control.i33_control.configuration_error
        if configuration_error is not None:
            raise HTTPException(status_code=503, detail=configuration_error)
        if not control.authority_configured:
            raise HTTPException(
                status_code=503,
                detail="P218_I35_AUTHORITATIVE_CURRICULUM_NOT_CONFIGURED",
            )
        try:
            return control.ingest(payload)
        except Pass218I35BindingError as exc:
            code = str(exc)
            status_code = (
                503
                if code == "P218_I35_AUTHORITATIVE_CURRICULUM_NOT_CONFIGURED"
                else 409
            )
            raise HTTPException(status_code=status_code, detail=code) from exc
        except (
            Pass218I35StateError,
            Pass218I35TransactionError,
            Pass218I35IngressError,
        ) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I35_STATUS_PATH,
        manifest_semantic_source_transaction_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-semantic-source-transaction-status-i35",
    )
    app.add_api_route(
        PASS218_I35_INGEST_PATH,
        ingest_manifest_semantic_source_transaction,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-semantic-source-transaction-ingest-i35",
    )
    return control


__all__ = [
    "PASS218_I35_INGEST_PATH",
    "PASS218_I35_SCOPE",
    "PASS218_I35_STATE_KEY",
    "PASS218_I35_STATUS_PATH",
    "PASS218_I35_STORE_DIRNAME",
    "PASS218_I35_VERSION",
    "Pass218I35IngestPayload",
    "Pass218I35RuntimeManifestSemanticTransactionControl",
    "install_pass218_i35_manifest_semantic_transaction_control",
]

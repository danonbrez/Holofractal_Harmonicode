"""RuntimeOS composition for Pass 218 Iteration 31 verbatim purge and receipt."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from fastapi import HTTPException

from hhs_runtime.pass218.verbatim_purge_i31 import (
    PASS218_I31_PURGE_SCOPE,
    PASS218_I31_PURGE_VERSION,
    Pass218I31ManagedBufferRegistry,
    Pass218I31PurgeError,
    Pass218I31PurgeRequest,
    Pass218I31VerbatimPurger,
)

PASS218_I31_STATUS_PATH = "/api/runtime/pass218/cognition/verbatim-purge/status"
PASS218_I31_PURGE_PATH = "/api/runtime/pass218/cognition/verbatim-purge/purge"
PASS218_I31_STATE_KEY = "hhs_pass218_verbatim_purge_i31"
PASS218_I31_STORE_DIRNAME = "cognition/verbatim-purge-i31"


class Pass218I31RuntimePurgeControl:
    """Writer-fenced browser membrane around the exact I31 purge gate."""

    def __init__(
        self,
        i30_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
        managed_buffers: Pass218I31ManagedBufferRegistry | None = None,
    ) -> None:
        self.i30_control = i30_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I31_STORE_DIRNAME
        self.managed_buffers = managed_buffers or Pass218I31ManagedBufferRegistry()
        self.purger = Pass218I31VerbatimPurger(
            lifecycle=lifecycle,
            i30_store_root=i30_control.store_root,
            purge_store_root=self.store_root,
            managed_buffers=self.managed_buffers,
        )

    @staticmethod
    def _request(payload: Mapping[str, Any]) -> Pass218I31PurgeRequest:
        binding = payload.get("purge_binding")
        if not isinstance(binding, Mapping):
            raise Pass218I31PurgeError("P218_I31_PURGE_BINDING_REQUIRED")
        return Pass218I31PurgeRequest(
            expected_i30_promotion_receipt_hash72=str(
                binding.get("expected_i30_promotion_receipt_hash72") or ""
            ),
            expected_i30_promotion_hash72=str(
                binding.get("expected_i30_promotion_hash72") or ""
            ),
            expected_promoted_object_hash72=str(
                binding.get("expected_promoted_object_hash72") or ""
            ),
            expected_canonical_root_hash72=str(
                binding.get("expected_canonical_root_hash72") or ""
            ),
            expected_i29_validation_hash72=str(
                binding.get("expected_i29_validation_hash72") or ""
            ),
            purge_scope=str(binding.get("purge_scope") or PASS218_I31_PURGE_SCOPE),
        ).validated()

    def purge(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.purger.purge(self._request(payload))

    def status(self) -> dict[str, Any]:
        return self.purger.status()

    def register_managed_buffer(
        self,
        buffer_id: str,
        *,
        promotion_receipt_hash72: str,
        source_sha256: str,
        buffer: bytearray,
    ) -> None:
        """Internal acquisition hook; deliberately not exposed as an HTTP route."""
        self.managed_buffers.register(
            buffer_id,
            promotion_receipt_hash72=promotion_receipt_hash72,
            source_sha256=source_sha256,
            buffer=buffer,
        )


def install_pass218_i31_verbatim_purge_control(
    app: Any,
    i30_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I31RuntimePurgeControl:
    existing = getattr(app.state, PASS218_I31_STATE_KEY, None)
    if isinstance(existing, Pass218I31RuntimePurgeControl):
        return existing

    control = Pass218I31RuntimePurgeControl(
        i30_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I31_STATE_KEY, control)

    managed_paths = {PASS218_I31_STATUS_PATH, PASS218_I31_PURGE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def purge_status() -> dict[str, Any]:
        return control.status()

    async def purge_promoted_source(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.purge(payload)
        except Pass218I31PurgeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I31_STATUS_PATH,
        purge_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-verbatim-purge-status-i31",
    )
    app.add_api_route(
        PASS218_I31_PURGE_PATH,
        purge_promoted_source,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-verbatim-purge-i31",
    )
    return control


__all__ = [
    "PASS218_I31_PURGE_PATH",
    "PASS218_I31_STATE_KEY",
    "PASS218_I31_STATUS_PATH",
    "PASS218_I31_STORE_DIRNAME",
    "PASS218_I31_PURGE_VERSION",
    "Pass218I31RuntimePurgeControl",
    "install_pass218_i31_verbatim_purge_control",
]

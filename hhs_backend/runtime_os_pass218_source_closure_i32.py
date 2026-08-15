"""RuntimeOS composition for Pass 218 Iteration 32 source closure."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from fastapi import HTTPException

from hhs_runtime.pass218.source_closure_i32 import (
    PASS218_I32_CLOSURE_SCOPE,
    PASS218_I32_CLOSURE_VERSION,
    Pass218I32ClosureError,
    Pass218I32ClosureRequest,
    Pass218I32SourceCloser,
)

PASS218_I32_STATUS_PATH = "/api/runtime/pass218/cognition/source-closure/status"
PASS218_I32_CLOSE_PATH = "/api/runtime/pass218/cognition/source-closure/close"
PASS218_I32_STATE_KEY = "hhs_pass218_source_closure_i32"
PASS218_I32_STORE_DIRNAME = "cognition/source-closure-i32"


class Pass218I32RuntimeSourceClosureControl:
    """Writer-fenced browser membrane around the exact I32 closure boundary."""

    def __init__(
        self,
        i31_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i31_control = i31_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I32_STORE_DIRNAME
        self.closer = Pass218I32SourceCloser(
            lifecycle=lifecycle,
            i31_store_root=i31_control.store_root,
            closure_store_root=self.store_root,
        )

    @staticmethod
    def _request(payload: Mapping[str, Any]) -> Pass218I32ClosureRequest:
        binding = payload.get("closure_binding")
        if not isinstance(binding, Mapping):
            raise Pass218I32ClosureError("P218_I32_CLOSURE_BINDING_REQUIRED")
        previous = binding.get("previous_closure_hash72")
        return Pass218I32ClosureRequest(
            expected_i31_purge_receipt_hash72=str(
                binding.get("expected_i31_purge_receipt_hash72") or ""
            ),
            expected_i31_purge_validation_hash72=str(
                binding.get("expected_i31_purge_validation_hash72") or ""
            ),
            expected_i31_purge_gate_root_hash72=str(
                binding.get("expected_i31_purge_gate_root_hash72") or ""
            ),
            expected_i31_purge_hash216=str(
                binding.get("expected_i31_purge_hash216") or ""
            ),
            expected_i30_promotion_receipt_hash72=str(
                binding.get("expected_i30_promotion_receipt_hash72") or ""
            ),
            expected_promoted_object_hash72=str(
                binding.get("expected_promoted_object_hash72") or ""
            ),
            expected_canonical_root_hash72=str(
                binding.get("expected_canonical_root_hash72") or ""
            ),
            source_id=str(binding.get("source_id") or ""),
            source_sha256=str(binding.get("source_sha256") or ""),
            source_authority=str(binding.get("source_authority") or ""),
            rights_class=str(binding.get("rights_class") or ""),
            curriculum_identity_hash72=str(
                binding.get("curriculum_identity_hash72") or ""
            ),
            curriculum_position=binding.get("curriculum_position", -1),
            source_stage=binding.get("source_stage", -1),
            previous_closure_hash72=(
                None if previous is None else str(previous)
            ),
            closure_scope=str(
                binding.get("closure_scope") or PASS218_I32_CLOSURE_SCOPE
            ),
        ).validated()

    def close(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.closer.close(self._request(payload))

    def status(self) -> dict[str, Any]:
        return self.closer.status()


def install_pass218_i32_source_closure_control(
    app: Any,
    i31_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I32RuntimeSourceClosureControl:
    existing = getattr(app.state, PASS218_I32_STATE_KEY, None)
    if isinstance(existing, Pass218I32RuntimeSourceClosureControl):
        return existing

    control = Pass218I32RuntimeSourceClosureControl(
        i31_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I32_STATE_KEY, control)

    managed_paths = {PASS218_I32_STATUS_PATH, PASS218_I32_CLOSE_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def closure_status() -> dict[str, Any]:
        return control.status()

    async def close_purged_source(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.close(payload)
        except Pass218I32ClosureError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I32_STATUS_PATH,
        closure_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-source-closure-status-i32",
    )
    app.add_api_route(
        PASS218_I32_CLOSE_PATH,
        close_purged_source,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-source-closure-i32",
    )
    return control


__all__ = [
    "PASS218_I32_CLOSE_PATH",
    "PASS218_I32_STATE_KEY",
    "PASS218_I32_STATUS_PATH",
    "PASS218_I32_STORE_DIRNAME",
    "PASS218_I32_CLOSURE_VERSION",
    "Pass218I32RuntimeSourceClosureControl",
    "install_pass218_i32_source_closure_control",
]

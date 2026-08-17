"""RuntimeOS binding for Pass 218 Iteration 16 distributed consumption."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import os
from typing import Any

from fastapi import Body, HTTPException

from hhs_backend.pass218_execution_i16_control import Pass218DistributedExecutionControlPlane
from hhs_backend.runtime_os_pass218_consumption_i15 import (
    PASS218_I15_ATTEST_PATH,
    PASS218_I15_CLAIM_PATH,
    PASS218_I15_RECONCILE_PATH,
    PASS218_I15_STATE_KEY,
    PASS218_I15_STATUS_PATH,
)
from hhs_runtime.pass218.distributed_consumption_i16 import build_distributed_consumption_ledger
from hhs_runtime.pass218.lifecycle_i10 import Pass218DistributedRuntimeLifecycle

PASS218_I16_STATUS_PATH = "/api/runtime/pass218/authority/maintenance-consumption/distributed/status"
PASS218_I16_SYNCHRONIZE_PATH = "/api/runtime/pass218/authority/maintenance-consumption/distributed/synchronize"
PASS218_I16_STATE_KEY = "hhs_pass218_distributed_consumption_i16"


def _has_route(app: Any, path: str) -> bool:
    return any(str(getattr(route, "path", "")) == path for route in app.router.routes)


def install_pass218_i16_consumption_control_plane(
    app: Any,
    lifecycle: Any,
    i13_control: Any,
    i14_control: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218DistributedExecutionControlPlane:
    existing = getattr(app.state, PASS218_I16_STATE_KEY, None)
    if isinstance(existing, Pass218DistributedExecutionControlPlane):
        return existing

    ledger = None
    if isinstance(lifecycle, Pass218DistributedRuntimeLifecycle):
        ledger = build_distributed_consumption_ledger(lifecycle.distributed)
    control = Pass218DistributedExecutionControlPlane(
        i13_control,
        i14_control,
        state_root=str(state_root),
        distributed_ledger=ledger,
    )
    setattr(app.state, PASS218_I15_STATE_KEY, control)
    setattr(app.state, PASS218_I16_STATE_KEY, control)

    if not _has_route(app, PASS218_I15_STATUS_PATH):
        async def maintenance_consumption_status() -> dict[str, Any]:
            return control.status()
        app.add_api_route(
            PASS218_I15_STATUS_PATH,
            maintenance_consumption_status,
            methods=["GET", "HEAD"],
            include_in_schema=True,
            name="hhs-pass218-maintenance-consumption-status-i16",
        )

    if not _has_route(app, PASS218_I15_CLAIM_PATH):
        async def claim_maintenance(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
            try:
                return control.claim(payload)
            except Exception as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        app.add_api_route(
            PASS218_I15_CLAIM_PATH,
            claim_maintenance,
            methods=["POST"],
            include_in_schema=True,
            name="hhs-pass218-maintenance-consumption-claim-i16",
        )

    if not _has_route(app, PASS218_I15_ATTEST_PATH):
        async def attest_maintenance(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
            try:
                return control.attest(payload)
            except Exception as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        app.add_api_route(
            PASS218_I15_ATTEST_PATH,
            attest_maintenance,
            methods=["POST"],
            include_in_schema=True,
            name="hhs-pass218-maintenance-consumption-attest-i16",
        )

    if not _has_route(app, PASS218_I15_RECONCILE_PATH):
        async def reconcile_maintenance(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
            try:
                return control.reconcile(payload)
            except Exception as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        app.add_api_route(
            PASS218_I15_RECONCILE_PATH,
            reconcile_maintenance,
            methods=["POST"],
            include_in_schema=True,
            name="hhs-pass218-maintenance-consumption-reconcile-i16",
        )

    if not _has_route(app, PASS218_I16_STATUS_PATH):
        async def distributed_consumption_status() -> dict[str, Any]:
            return control.distributed_status()
        app.add_api_route(
            PASS218_I16_STATUS_PATH,
            distributed_consumption_status,
            methods=["GET", "HEAD"],
            include_in_schema=True,
            name="hhs-pass218-distributed-consumption-status-i16",
        )

    if not _has_route(app, PASS218_I16_SYNCHRONIZE_PATH):
        async def synchronize_consumption() -> dict[str, Any]:
            try:
                return await asyncio.to_thread(control.synchronize)
            except Exception as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        app.add_api_route(
            PASS218_I16_SYNCHRONIZE_PATH,
            synchronize_consumption,
            methods=["POST"],
            include_in_schema=True,
            name="hhs-pass218-distributed-consumption-synchronize-i16",
        )

    inherited_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def i16_lifespan(app_instance):
        async with inherited_lifespan(app_instance):
            if control.distributed_ledger is not None:
                try:
                    await asyncio.to_thread(control.synchronize)
                except Exception as exc:
                    control.last_i16_error_code = control._code(exc)
            yield

    app.router.lifespan_context = i16_lifespan
    return control


__all__ = [
    "PASS218_I16_STATE_KEY",
    "PASS218_I16_STATUS_PATH",
    "PASS218_I16_SYNCHRONIZE_PATH",
    "install_pass218_i16_consumption_control_plane",
]

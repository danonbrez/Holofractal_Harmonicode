"""RuntimeOS/server composition for Pass 218 Iteration 18 terminal closure."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import os
from typing import Any

from fastapi import Body, HTTPException

from hhs_backend.pass218_execution_i18_control import Pass218DistributedTerminalClosureControlPlane
from hhs_backend.runtime_os_pass218_consumption_i15 import (
    PASS218_I15_ATTEST_PATH,
    PASS218_I15_CLAIM_PATH,
    PASS218_I15_RECONCILE_PATH,
    PASS218_I15_STATE_KEY,
    PASS218_I15_STATUS_PATH,
)
from hhs_backend.runtime_os_pass218_consumption_i16 import (
    PASS218_I16_STATE_KEY,
    PASS218_I16_STATUS_PATH,
    PASS218_I16_SYNCHRONIZE_PATH,
)
from hhs_backend.runtime_os_pass218_execution_i17 import (
    PASS218_I17_STATE_KEY,
    PASS218_I17_STATUS_PATH,
)
from hhs_runtime.pass218.distributed_closure_i18 import build_distributed_closure_ledger
from hhs_runtime.pass218.distributed_consumption_i16 import build_distributed_consumption_ledger
from hhs_runtime.pass218.distributed_execution_i17 import build_distributed_execution_ledger
from hhs_runtime.pass218.lifecycle_i10 import Pass218DistributedRuntimeLifecycle

PASS218_I18_STATUS_PATH = "/api/runtime/pass218/authority/maintenance-closure/status"
PASS218_I18_SYNCHRONIZE_PATH = "/api/runtime/pass218/authority/maintenance-closure/synchronize"
PASS218_I18_STATE_KEY = "hhs_pass218_distributed_terminal_closure_i18"


def _remove_paths(app: Any, paths: set[str]) -> None:
    app.router.routes[:] = [
        route for route in app.router.routes
        if str(getattr(route, "path", "")) not in paths
    ]


def install_pass218_i18_terminal_closure_control_plane(
    app: Any,
    lifecycle: Any,
    i13_control: Any,
    i14_control: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218DistributedTerminalClosureControlPlane:
    existing = getattr(app.state, PASS218_I18_STATE_KEY, None)
    if isinstance(existing, Pass218DistributedTerminalClosureControlPlane):
        return existing

    consumption_ledger = None
    execution_ledger = None
    closure_ledger = None
    if isinstance(lifecycle, Pass218DistributedRuntimeLifecycle):
        consumption_ledger = build_distributed_consumption_ledger(lifecycle.distributed)
        execution_ledger = build_distributed_execution_ledger(lifecycle.distributed, consumption_ledger)
        closure_ledger = build_distributed_closure_ledger(lifecycle.distributed, execution_ledger)

    executor_id = os.environ.get("HHS_PASS218_I17_EXECUTOR_ID", "").strip() or None
    result_secret = os.environ.get("HHS_PASS218_I17_RESULT_SHARED_SECRET", "") or None
    control = Pass218DistributedTerminalClosureControlPlane(
        i13_control,
        i14_control,
        state_root=str(state_root),
        distributed_ledger=consumption_ledger,
        execution_ledger=execution_ledger,
        external_executor=None,
        external_executor_id=executor_id,
        result_shared_secret=result_secret,
        closure_ledger=closure_ledger,
    )
    setattr(app.state, PASS218_I15_STATE_KEY, control)
    setattr(app.state, PASS218_I16_STATE_KEY, control)
    setattr(app.state, PASS218_I17_STATE_KEY, control)
    setattr(app.state, PASS218_I18_STATE_KEY, control)

    rebound = {
        PASS218_I15_STATUS_PATH,
        PASS218_I15_CLAIM_PATH,
        PASS218_I15_ATTEST_PATH,
        PASS218_I15_RECONCILE_PATH,
        PASS218_I16_STATUS_PATH,
        PASS218_I16_SYNCHRONIZE_PATH,
        PASS218_I17_STATUS_PATH,
        PASS218_I18_STATUS_PATH,
        PASS218_I18_SYNCHRONIZE_PATH,
    }
    _remove_paths(app, rebound)

    async def maintenance_consumption_status() -> dict[str, Any]:
        return control.status()

    async def claim_maintenance(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
        try:
            return await asyncio.to_thread(control.claim, payload)
        except Exception as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    async def attest_maintenance(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
        try:
            return await asyncio.to_thread(control.attest, payload)
        except Exception as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    async def reconcile_maintenance(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
        try:
            return await asyncio.to_thread(control.reconcile, payload)
        except Exception as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    async def distributed_consumption_status() -> dict[str, Any]:
        return control.distributed_status()

    async def synchronize_consumption() -> dict[str, Any]:
        try:
            return await asyncio.to_thread(control.synchronize)
        except Exception as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    async def external_execution_status() -> dict[str, Any]:
        return control.status()

    async def terminal_closure_status() -> dict[str, Any]:
        return control.status()

    async def synchronize_terminal_closure() -> dict[str, Any]:
        try:
            return await asyncio.to_thread(control.synchronize_terminal_closures)
        except Exception as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(PASS218_I15_STATUS_PATH, maintenance_consumption_status, methods=["GET", "HEAD"], include_in_schema=True, name="hhs-pass218-maintenance-consumption-status-i18")
    app.add_api_route(PASS218_I15_CLAIM_PATH, claim_maintenance, methods=["POST"], include_in_schema=True, name="hhs-pass218-maintenance-consumption-claim-i18")
    app.add_api_route(PASS218_I15_ATTEST_PATH, attest_maintenance, methods=["POST"], include_in_schema=True, name="hhs-pass218-maintenance-consumption-attest-i18")
    app.add_api_route(PASS218_I15_RECONCILE_PATH, reconcile_maintenance, methods=["POST"], include_in_schema=True, name="hhs-pass218-maintenance-consumption-reconcile-i18")
    app.add_api_route(PASS218_I16_STATUS_PATH, distributed_consumption_status, methods=["GET", "HEAD"], include_in_schema=True, name="hhs-pass218-distributed-consumption-status-i18")
    app.add_api_route(PASS218_I16_SYNCHRONIZE_PATH, synchronize_consumption, methods=["POST"], include_in_schema=True, name="hhs-pass218-distributed-consumption-synchronize-i18")
    app.add_api_route(PASS218_I17_STATUS_PATH, external_execution_status, methods=["GET", "HEAD"], include_in_schema=True, name="hhs-pass218-external-execution-status-i18")
    app.add_api_route(PASS218_I18_STATUS_PATH, terminal_closure_status, methods=["GET", "HEAD"], include_in_schema=True, name="hhs-pass218-terminal-closure-status-i18")
    app.add_api_route(PASS218_I18_SYNCHRONIZE_PATH, synchronize_terminal_closure, methods=["POST"], include_in_schema=True, name="hhs-pass218-terminal-closure-synchronize-i18")

    inherited_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def i18_lifespan(app_instance):
        async with inherited_lifespan(app_instance):
            if control.distributed_ledger is not None:
                try:
                    await asyncio.to_thread(control.synchronize)
                    await asyncio.to_thread(control.synchronize_terminal_closures)
                except Exception as exc:
                    control.last_i18_error_code = control._code(exc)
            yield

    app.router.lifespan_context = i18_lifespan
    return control


__all__ = [
    "PASS218_I18_STATE_KEY",
    "PASS218_I18_STATUS_PATH",
    "PASS218_I18_SYNCHRONIZE_PATH",
    "install_pass218_i18_terminal_closure_control_plane",
]

"""Runtime OS routes for Pass 218 Iteration 15 maintenance consumption."""
from __future__ import annotations

import os
from typing import Any

from fastapi import Body, HTTPException

from hhs_backend.pass218_execution_i15_control import Pass218ExecutionControlPlane

PASS218_I15_STATUS_PATH = "/api/runtime/pass218/authority/maintenance-consumption/status"
PASS218_I15_CLAIM_PATH = "/api/runtime/pass218/authority/maintenance-consumption/claim"
PASS218_I15_ATTEST_PATH = "/api/runtime/pass218/authority/maintenance-consumption/attest"
PASS218_I15_RECONCILE_PATH = "/api/runtime/pass218/authority/maintenance-consumption/reconcile"
PASS218_I15_STATE_KEY = "hhs_pass218_maintenance_consumption_i15"


def _has_route(app: Any, path: str) -> bool:
    return any(str(getattr(route, "path", "")) == path for route in app.router.routes)


def install_pass218_i15_consumption_control_plane(
    app: Any,
    i13_control: Any,
    i14_control: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218ExecutionControlPlane:
    existing = getattr(app.state, PASS218_I15_STATE_KEY, None)
    if isinstance(existing, Pass218ExecutionControlPlane):
        return existing
    control = Pass218ExecutionControlPlane(i13_control, i14_control, state_root=state_root)
    setattr(app.state, PASS218_I15_STATE_KEY, control)

    if not _has_route(app, PASS218_I15_STATUS_PATH):
        async def maintenance_consumption_status() -> dict[str, Any]:
            return control.status()
        app.add_api_route(PASS218_I15_STATUS_PATH, maintenance_consumption_status, methods=["GET", "HEAD"], include_in_schema=True, name="hhs-pass218-maintenance-consumption-status-i15")

    if not _has_route(app, PASS218_I15_CLAIM_PATH):
        async def claim_maintenance(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
            try:
                return control.claim(payload)
            except Exception as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        app.add_api_route(PASS218_I15_CLAIM_PATH, claim_maintenance, methods=["POST"], include_in_schema=True, name="hhs-pass218-maintenance-consumption-claim-i15")

    if not _has_route(app, PASS218_I15_ATTEST_PATH):
        async def attest_maintenance(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
            try:
                return control.attest(payload)
            except Exception as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        app.add_api_route(PASS218_I15_ATTEST_PATH, attest_maintenance, methods=["POST"], include_in_schema=True, name="hhs-pass218-maintenance-consumption-attest-i15")

    if not _has_route(app, PASS218_I15_RECONCILE_PATH):
        async def reconcile_maintenance(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
            try:
                return control.reconcile(payload)
            except Exception as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        app.add_api_route(PASS218_I15_RECONCILE_PATH, reconcile_maintenance, methods=["POST"], include_in_schema=True, name="hhs-pass218-maintenance-consumption-reconcile-i15")

    return control


__all__ = [
    "PASS218_I15_ATTEST_PATH",
    "PASS218_I15_CLAIM_PATH",
    "PASS218_I15_RECONCILE_PATH",
    "PASS218_I15_STATE_KEY",
    "PASS218_I15_STATUS_PATH",
    "install_pass218_i15_consumption_control_plane",
]

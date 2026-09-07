"""Retired legacy runtime-server application constructor with preserved callables.

Pass219 I181 removes this module's independent FastAPI application identity only
after I180 migrated its seven HTTP operations into the governed Pass170 public
adapter.  The historical handler functions and a non-deployment APIRouter remain
available for dependency-scoped callers, while ``runtime_server:app`` resolves
lazily to the exact canonical Pass170 application.

This module creates no public listener, VM81 authority, Hash72 mint authority,
Hash216 persistence authority, or capability-token authority.
"""
from __future__ import annotations

import logging
import traceback
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from hhs_backend.runtime.runtime_event_schema import create_runtime_event
from hhs_backend.runtime.runtime_ws import (
    propagate_runtime_event,
    runtime_ws_health,
)
from hhs_runtime.harmonicode_constraint_solver_v1 import interpret_and_solve

RETIREMENT_CLASSIFICATION = "PASS170_LEGACY_RUNTIME_SERVER_CONSTRUCTOR_RETIRED_I181"
CANONICAL_TARGET = "hhs_backend.public_api_server:app"
INDEPENDENT_FASTAPI_CONSTRUCTOR = False
PUBLIC_PORT_AUTHORITY = False
NEW_VM81_AUTHORITY = False
NEW_HASH72_MINT_AUTHORITY = False
HASH216_PERSISTENCE_AUTHORITY = False
CAPABILITY_TOKEN_AUTHORITY = False

logger = logging.getLogger("HHS_RUNTIME_SERVER")
legacy_router = APIRouter(tags=["legacy-runtime-server-retired-i181"])


class SolveRequest(BaseModel):
    expression: str
    runtime_id: Optional[str] = "runtime_main"
    branch_id: Optional[str] = "main"


async def execute_runtime_expression(expression: str) -> Dict[str, Any]:
    """Execute source through the inherited Harmonicode interpreter and solver."""
    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("expression must be a non-empty Harmonicode source string")
    result = interpret_and_solve(expression)
    solver = result.get("solver", {})
    receipt = solver.get("receipt", {})
    return {
        "expression": expression,
        "status": receipt.get("status", "UNKNOWN"),
        "result": result,
        "transport": "harmonicode_interpreter_solver",
        "execution_performed": True,
        "full_receipt_hash72": result["full_receipt_hash72"],
    }


@legacy_router.get("/api/healthz")
async def healthz() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "runtime": "online",
        "websocket": runtime_ws_health(),
    }


@legacy_router.get("/api/runtime/metrics")
async def runtime_metrics() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "websocket": runtime_ws_health(),
    }


@legacy_router.post("/api/hhs/solve")
async def solve(request: SolveRequest) -> Dict[str, Any]:
    try:
        result = await execute_runtime_expression(request.expression)
        event = create_runtime_event(
            event_type="runtime",
            runtime_id=request.runtime_id,
            branch_id=request.branch_id,
            receipt_hash72=result["full_receipt_hash72"],
            payload={"expression": request.expression, "result": result},
        )
        await propagate_runtime_event(event)
        return {
            "status": "ok",
            "runtime_id": request.runtime_id,
            "branch_id": request.branch_id,
            "event_hash72": event.event_hash72,
            "receipt_hash72": event.receipt_hash72,
            "payload": result,
        }
    except Exception as error:
        logger.exception("Runtime solve failure.")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "runtime_error",
                "error": str(error),
                "traceback": traceback.format_exc(),
            },
        ) from error


@legacy_router.post("/api/runtime/event")
async def inject_runtime_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        event = create_runtime_event(
            event_type=payload.get("event_type", "runtime"),
            runtime_id=payload.get("runtime_id", "runtime_main"),
            branch_id=payload.get("branch_id", "main"),
            receipt_hash72=payload.get("receipt_hash72", "runtime_receipt"),
            payload=payload.get("payload", {}),
        )
        await propagate_runtime_event(event)
        return {"status": "propagated", "event_hash72": event.event_hash72}
    except Exception as error:
        logger.exception("Runtime event injection failure.")
        raise HTTPException(
            status_code=500,
            detail={"status": "runtime_event_error", "error": str(error)},
        ) from error


@legacy_router.get("/api/runtime/replay")
async def runtime_replay() -> Dict[str, Any]:
    return {"status": "online", "replay": "available"}


@legacy_router.get("/api/runtime/graph")
async def runtime_graph() -> Dict[str, Any]:
    return {"status": "online", "graph": "available"}


@legacy_router.get("/api/runtime/transport")
async def runtime_transport() -> Dict[str, Any]:
    return {"status": "online", "transport": "available"}


def _canonical_app():
    """Resolve the canonical application only when legacy ``app`` is requested."""
    from hhs_backend.public_api_server import app as canonical_app

    return canonical_app


def __getattr__(name: str):
    if name == "app":
        return _canonical_app()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | {"app"})


def main() -> None:
    import uvicorn

    uvicorn.run(
        CANONICAL_TARGET,
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()


__all__ = [
    "CANONICAL_TARGET",
    "CAPABILITY_TOKEN_AUTHORITY",
    "HASH216_PERSISTENCE_AUTHORITY",
    "INDEPENDENT_FASTAPI_CONSTRUCTOR",
    "NEW_HASH72_MINT_AUTHORITY",
    "NEW_VM81_AUTHORITY",
    "PUBLIC_PORT_AUTHORITY",
    "RETIREMENT_CLASSIFICATION",
    "SolveRequest",
    "app",
    "execute_runtime_expression",
    "healthz",
    "inject_runtime_event",
    "legacy_router",
    "main",
    "runtime_graph",
    "runtime_metrics",
    "runtime_replay",
    "runtime_transport",
    "solve",
]

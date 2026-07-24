# ============================================================================
# hhs_backend/runtime/runtime_server.py
# ============================================================================
#
# Canonical Runtime Server
#
# Responsibilities:
#
#   - FastAPI runtime authority
#   - runtime execution routing
#   - websocket routing
#   - runtime propagation
#   - replay propagation
#   - graph propagation
#   - runtime lifecycle
#
# IMPORTANT
# ----------------------------------------------------------------------------
#
# Runtime authority originates from:
#
#   runtime_event_schema.py
#
# ALL runtime execution paths MUST emit:
#
#   canonical runtime events
#
# and propagate through:
#
#   runtime_ws.py
#
# ============================================================================

from __future__ import annotations

import logging
import traceback

from typing import Any
from typing import Dict
from typing import Optional

try:
    from fastapi import FastAPI
    from fastapi import HTTPException
    from fastapi.middleware.cors import CORSMiddleware
except ModuleNotFoundError:  # pragma: no cover - optional runtime dependency
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: Any):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class FastAPI:  # type: ignore[override]
        def __init__(self, *args, **kwargs):
            pass

        def add_middleware(self, *args, **kwargs):
            return None

        def include_router(self, *args, **kwargs):
            return None

        def get(self, *args, **kwargs):
            def decorator(fn):
                return fn

            return decorator

        def post(self, *args, **kwargs):
            def decorator(fn):
                return fn

            return decorator

    class CORSMiddleware:  # type: ignore[override]
        pass

try:
    from pydantic import BaseModel
except ModuleNotFoundError:  # pragma: no cover - optional runtime dependency
    class BaseModel:  # type: ignore[override]
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

from hhs_backend.runtime.runtime_event_schema import (
    create_runtime_event,
)

from hhs_backend.runtime.runtime_ws import (
    propagate_runtime_event,
    runtime_ws_health,
    runtime_ws_router,
)
from hhs_runtime.harmonicode_constraint_solver_v1 import interpret_and_solve

# ============================================================================
# Logging
# ============================================================================

logger = logging.getLogger(
    "HHS_RUNTIME_SERVER"
)

# ============================================================================
# FastAPI
# ============================================================================

app = FastAPI(

    title="HHS Runtime Server",

    version="1.0.0"
)

# ============================================================================
# CORS
# ============================================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

# ============================================================================
# WS Router
# ============================================================================

app.include_router(
    runtime_ws_router
)

# ============================================================================
# Models
# ============================================================================

class SolveRequest(BaseModel):

    expression: str

    runtime_id: Optional[str] = (
        "runtime_main"
    )

    branch_id: Optional[str] = (
        "main"
    )

# ============================================================================
# Runtime Solve
# ============================================================================

async def execute_runtime_expression(expression: str) -> Dict[str, Any]:
    """Execute source through the real Harmonicode interpreter and solver."""
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

# ============================================================================
# Health
# ============================================================================

@app.get("/api/healthz")
async def healthz():

    return {

        "status":
            "healthy",

        "runtime":
            "online",

        "websocket":
            runtime_ws_health()
    }

# ============================================================================
# Metrics
# ============================================================================

@app.get("/api/runtime/metrics")
async def runtime_metrics():

    return {

        "status":
            "healthy",

        "websocket":
            runtime_ws_health()
    }

# ============================================================================
# Solve
# ============================================================================

@app.post("/api/hhs/solve")
async def solve(
    request: SolveRequest
):

    try:

        # -------------------------------------------------------------
        # Runtime Execution
        # -------------------------------------------------------------

        result = (

            await execute_runtime_expression(

                request.expression
            )
        )

        # -------------------------------------------------------------
        # Canonical Runtime Event
        # -------------------------------------------------------------

        event = create_runtime_event(

            event_type="runtime",

            runtime_id=request.runtime_id,

            branch_id=request.branch_id,

            receipt_hash72=result["full_receipt_hash72"],

            payload={

                "expression":
                    request.expression,

                "result":
                    result
            }
        )

        # -------------------------------------------------------------
        # Runtime Propagation
        # -------------------------------------------------------------

        await propagate_runtime_event(
            event
        )

        # -------------------------------------------------------------
        # Response
        # -------------------------------------------------------------

        return {

            "status":
                "ok",

            "runtime_id":
                request.runtime_id,

            "branch_id":
                request.branch_id,

            "event_hash72":
                event.event_hash72,

            "receipt_hash72":
                event.receipt_hash72,

            "payload":
                result
        }

    except Exception as error:

        logger.exception(
            "Runtime solve failure."
        )

        raise HTTPException(

            status_code=500,

            detail={

                "status":
                    "runtime_error",

                "error":
                    str(error),

                "traceback":
                    traceback.format_exc()
            }
        )

# ============================================================================
# Runtime Event Injection
# ============================================================================

@app.post("/api/runtime/event")
async def inject_runtime_event(
    payload: Dict[str, Any]
):

    try:

        runtime_id = payload.get(
            "runtime_id",
            "runtime_main"
        )

        branch_id = payload.get(
            "branch_id",
            "main"
        )

        event_type = payload.get(
            "event_type",
            "runtime"
        )

        receipt_hash72 = payload.get(
            "receipt_hash72",
            "runtime_receipt"
        )

        event_payload = payload.get(
            "payload",
            {}
        )

        event = create_runtime_event(

            event_type=event_type,

            runtime_id=runtime_id,

            branch_id=branch_id,

            receipt_hash72=receipt_hash72,

            payload=event_payload
        )

        await propagate_runtime_event(
            event
        )

        return {

            "status":
                "propagated",

            "event_hash72":
                event.event_hash72
        }

    except Exception as error:

        logger.exception(
            "Runtime event injection failure."
        )

        raise HTTPException(

            status_code=500,

            detail={

                "status":
                    "runtime_event_error",

                "error":
                    str(error)
            }
        )

# ============================================================================
# Runtime Replay
# ============================================================================

@app.get("/api/runtime/replay")
async def runtime_replay():

    return {

        "status":
            "online",

        "replay":
            "available"
    }

# ============================================================================
# Runtime Graph
# ============================================================================

@app.get("/api/runtime/graph")
async def runtime_graph():

    return {

        "status":
            "online",

        "graph":
            "available"
    }

# ============================================================================
# Runtime Transport
# ============================================================================

@app.get("/api/runtime/transport")
async def runtime_transport():

    return {

        "status":
            "online",

        "transport":
            "available"
    }

# ============================================================================
# Entry
# ============================================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "hhs_backend.runtime.runtime_server:app",

        host="0.0.0.0",

        port=8000,

        reload=True
    )
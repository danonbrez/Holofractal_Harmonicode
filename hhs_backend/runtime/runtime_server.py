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

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from hhs_backend.runtime.runtime_event_schema import (
    create_runtime_event,
)

from hhs_backend.runtime.runtime_ws import (
    propagate_runtime_event,
    runtime_ws_health,
    runtime_ws_router,
)

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

async def execute_runtime_expression(

    expression: str

) -> Dict[str, Any]:

    """
    Placeholder execution bridge.

    Replace with:
        - VM81 bridge
        - ABI runtime
        - symbolic runtime
        - transport manifold
    """

    return {

        "expression":
            expression,

        "status":
            "executed",

        "result":
            expression,

        "transport":
            "runtime_projection"
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

            receipt_hash72="runtime_receipt",

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
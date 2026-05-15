from __future__ import annotations

import asyncio
import os
import time

from contextlib import asynccontextmanager
from typing import Any
from typing import Dict

from fastapi import FastAPI
from fastapi import WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# =========================================================
# Runtime Kernel
# =========================================================

from hhs_runtime.runtime_kernel_bridge import (
    runtime_kernel_bridge
)

# =========================================================
# Runtime WebSocket Hub
# =========================================================

from hhs_runtime.runtime_ws import (

    runtime_stream,

    replay_stream,

    graph_stream,

    transport_stream,

    runtime_ws_hub
)

# =========================================================
# Runtime Event Bus
# =========================================================

from hhs_runtime.runtime_event_schema import (

    RuntimeEventPayload,

    RuntimeEvent
)

from hhs_runtime.runtime_event_bus import (
    runtime_event_bus
)

# =========================================================
# Lifespan
# =========================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI
):

    print(
        "[hhs_runtime] boot"
    )

    # -----------------------------------------------------
    # Start Runtime Kernel Bridge
    # -----------------------------------------------------

    await runtime_kernel_bridge.start()

    try:

        yield

    finally:

        print(
            "[hhs_runtime] shutdown"
        )

        await runtime_kernel_bridge.stop()

# =========================================================
# FastAPI
# =========================================================

app = FastAPI(

    title=
        "Holofractal Harmonicode Runtime",

    version="0.1.0",

    lifespan=
        lifespan
)

# =========================================================
# CORS
# =========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)

# =========================================================
# Health
# =========================================================

@app.get("/health")
async def health():

    return {

        "status":
            "online",

        "runtime":
            "hhs_runtime",

        "uptime":
            runtime_kernel_bridge
                .uptime_seconds()
    }

# =========================================================
# Runtime Metrics
# =========================================================

@app.get("/api/runtime/metrics")
async def runtime_metrics():

    return {

        "kernel": {

            "running":
                runtime_kernel_bridge
                    .running,

            "runtime_step":
                runtime_kernel_bridge
                    .runtime_step,

            "sequence_id":
                runtime_kernel_bridge
                    .sequence_id,

            "uptime":
                runtime_kernel_bridge
                    .uptime_seconds()
        },

        "websocket": (

            runtime_ws_hub
                .metrics()
        )
    }

# =========================================================
# Calculator Evaluate
# =========================================================

@app.post("/api/calculator/evaluate")
async def calculator_evaluate(
    payload: Dict[str, Any]
):

    expression = payload.get(
        "expression",
        ""
    )

    timestamp = time.time_ns()

    # -----------------------------------------------------
    # Emit Runtime Event
    # -----------------------------------------------------

    event = RuntimeEvent.build(

        RuntimeEventPayload(

            operation=
                "calculator.evaluate",

            runtime_status=
                "online",

            step=
                runtime_kernel_bridge
                    .runtime_step,

            phase=
                "evaluation",

            uptime=
                runtime_kernel_bridge
                    .uptime_seconds(),

            receipt_hash72=
                runtime_kernel_bridge
                    ._hash72(),

            source_hash72=
                runtime_kernel_bridge
                    ._hash72(),

            closure_state=
                "stable",

            transport_flux=
                runtime_kernel_bridge
                    ._transport_flux(),

            orientation_flux=
                runtime_kernel_bridge
                    ._orientation_flux(),

            constraint_flux=
                runtime_kernel_bridge
                    ._constraint_flux(),

            entropy_delta=
                0.0
        ),

        sequence_id=
            runtime_kernel_bridge
                .sequence_id
    )

    await runtime_event_bus.emit(
        event
    )

    return {

        "status":
            "ok",

        "expression":
            expression,

        "timestamp_ns":
            timestamp,

        "runtime_step":

            runtime_kernel_bridge
                .runtime_step,

        "receipt_hash72":

            runtime_kernel_bridge
                ._hash72(),

        "projection": {

            "transport_flux":

                runtime_kernel_bridge
                    ._transport_flux(),

            "orientation_flux":

                runtime_kernel_bridge
                    ._orientation_flux(),

            "constraint_flux":

                runtime_kernel_bridge
                    ._constraint_flux()
        }
    }

# =========================================================
# Runtime Agent Loop
# =========================================================

@app.post("/api/agent/run-loop")
async def runtime_agent_loop(
    payload: Dict[str, Any]
):

    expression = payload.get(
        "expression",
        ""
    )

    auto_continue = payload.get(
        "auto_continue",
        True
    )

    max_passes = payload.get(
        "max_passes",
        3
    )

    passes = []

    for i in range(max_passes):

        await asyncio.sleep(0.05)

        passes.append({

            "pass":
                i + 1,

            "phase":

                runtime_kernel_bridge
                    ._phase(),

            "receipt_hash72":

                runtime_kernel_bridge
                    ._hash72(),

            "transport_flux":

                runtime_kernel_bridge
                    ._transport_flux()
        })

    return {

        "status":
            "ok",

        "expression":
            expression,

        "auto_continue":
            auto_continue,

        "passes":
            passes
    }

# =========================================================
# WebSockets
# =========================================================

@app.websocket("/ws/runtime")
async def ws_runtime(
    websocket: WebSocket
):

    await runtime_stream(
        websocket
    )

# ---------------------------------------------------------

@app.websocket("/ws/replay")
async def ws_replay(
    websocket: WebSocket
):

    await replay_stream(
        websocket
    )

# ---------------------------------------------------------

@app.websocket("/ws/graph")
async def ws_graph(
    websocket: WebSocket
):

    await graph_stream(
        websocket
    )

# ---------------------------------------------------------

@app.websocket("/ws/transport")
async def ws_transport(
    websocket: WebSocket
):

    await transport_stream(
        websocket
    )

# =========================================================
# Root
# =========================================================

@app.get("/")
async def root():

    return JSONResponse({

        "runtime":
            "Holofractal Harmonicode Runtime",

        "status":
            "online",

        "websocket_routes": [

            "/ws/runtime",

            "/ws/replay",

            "/ws/graph",

            "/ws/transport"
        ]
    })

# =========================================================
# Entry
# =========================================================

if __name__ == "__main__":

    import uvicorn

    host = os.getenv(
        "HHS_RUNTIME_HOST",
        "0.0.0.0"
    )

    port = int(

        os.getenv(
            "HHS_RUNTIME_PORT",
            "8000"
        )
    )

    uvicorn.run(

        "hhs_runtime.main:app",

        host=host,

        port=port,

        reload=True
    )
# ============================================================================
# hhs_backend/server.py
# HARMONICODE / HHS
# CANONICAL BACKEND SERVER BOOTSTRAP
#
# PURPOSE
# -------
# Authoritative runtime server process for:
#
#   - FastAPI lifecycle management
#   - router composition
#   - runtime initialization
#   - graph-memory initialization
#   - websocket orchestration
#   - replay infrastructure
#   - middleware registration
#   - deterministic startup ordering
#
# ALL backend execution MUST originate here.
#
# ============================================================================

from __future__ import annotations

import asyncio
import logging
import time
import uuid

from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import uvicorn

# ============================================================================
# ROUTES
# ============================================================================

from hhs_backend.api.runtime_routes import (
    router as runtime_router,

    runtime_controller,

    runtime_graph
)

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(

    level=logging.INFO,

    format=(
        "[HHS] "
        "%(asctime)s "
        "%(levelname)s "
        "%(message)s"
    )
)

logger = logging.getLogger("HHS")

# ============================================================================
# GLOBAL SERVER STATE
# ============================================================================

SERVER_BOOT_ID = str(uuid.uuid4())

SERVER_START_TIME = time.time()

SERVER_STATE: Dict[str, Any] = {

    "boot_id":
        SERVER_BOOT_ID,

    "started_at":
        SERVER_START_TIME,

    "runtime_initialized":
        False,

    "graph_initialized":
        False,

    "websocket_ready":
        False,
}

# ============================================================================
# STARTUP
# ============================================================================

async def initialize_runtime():

    logger.info(
        "Initializing deterministic runtime..."
    )

    runtime_controller.runtime.runtime_init()

    ok = runtime_controller.runtime.validate_abi()

    if not ok:

        raise RuntimeError(
            "HHS ABI validation failed"
        )

    SERVER_STATE["runtime_initialized"] = True

    logger.info(
        "Runtime initialized"
    )

# ----------------------------------------------------------------------------

async def initialize_graph():

    logger.info(
        "Initializing graph substrate..."
    )

    runtime_graph.export_graph_summary()

    SERVER_STATE["graph_initialized"] = True

    logger.info(
        "Graph substrate initialized"
    )

# ----------------------------------------------------------------------------

async def initialize_websocket_layer():

    logger.info(
        "Initializing websocket layer..."
    )

    SERVER_STATE["websocket_ready"] = True

    logger.info(
        "Websocket layer initialized"
    )

# ----------------------------------------------------------------------------

async def startup_sequence():

    logger.info(
        "Starting HHS backend..."
    )

    await initialize_runtime()

    await initialize_graph()

    await initialize_websocket_layer()

    logger.info(
        "HHS backend startup complete"
    )

# ============================================================================
# SHUTDOWN
# ============================================================================

async def shutdown_sequence():

    logger.info(
        "Beginning shutdown sequence..."
    )

    runtime_controller.halt()

    logger.info(
        "Runtime halted"
    )

# ============================================================================
# FASTAPI LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    await startup_sequence()

    yield

    await shutdown_sequence()

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(

    title="HARMONICODE Runtime Server",

    description=(
        "Deterministic runtime operating environment "
        "for HHS / HARMONICODE"
    ),

    version="0.1.0",

    lifespan=lifespan
)

# ============================================================================
# MIDDLEWARE
# ============================================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

# ============================================================================
# ROUTERS
# ============================================================================

app.include_router(runtime_router)

# ============================================================================
# HEALTH ROUTES
# ============================================================================

@app.get("/")
async def root():

    return {

        "system":
            "HARMONICODE",

        "status":
            "online",

        "boot_id":
            SERVER_BOOT_ID
    }

# ----------------------------------------------------------------------------

@app.get("/health")
async def health():

    runtime_state = (
        runtime_controller.latest_runtime_state()
    )

    graph_summary = (
        runtime_graph.export_graph_summary()
    )

    return {

        "status":
            "healthy",

        "boot_id":
            SERVER_BOOT_ID,

        "uptime":
            time.time() - SERVER_START_TIME,

        "runtime":
            runtime_state,

        "graph":
            graph_summary,

        "server_state":
            SERVER_STATE,
    }

# ----------------------------------------------------------------------------

@app.get("/health/runtime")
async def runtime_health():

    return runtime_controller.latest_runtime_state()

# ----------------------------------------------------------------------------

@app.get("/health/graph")
async def graph_health():

    return runtime_graph.export_graph_summary()

# ============================================================================
# EXCEPTION HANDLING
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request,
    exc
):

    logger.exception(exc)

    return JSONResponse(

        status_code=500,

        content={

            "error":
                str(exc),

            "boot_id":
                SERVER_BOOT_ID
        }
    )

# ============================================================================
# SERVER SELF TEST
# ============================================================================

def server_self_test():

    logger.info(
        "Running server self-test..."
    )

    runtime_controller.run_steps(5)

    packet = (
        runtime_controller.export_multimodal_packet()
    )

    runtime_graph.ingest_runtime_state(packet)

    logger.info(
        "Runtime self-test complete"
    )

    logger.info(
        runtime_graph.export_graph_summary()
    )

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    server_self_test()

    uvicorn.run(

        "hhs_backend.server:app",

        host="0.0.0.0",

        port=8181,

        reload=False,

        ws="websockets",

        log_level="info",
    )
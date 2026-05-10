# ============================================================================
# hhs_backend/api/runtime_routes.py
# HARMONICODE / HHS
# CANONICAL RUNTIME API ROUTES
#
# PURPOSE
# -------
# Network-accessible deterministic runtime execution layer.
#
# This module exposes:
#
#   - runtime execution
#   - receipt-chain control
#   - graph ingestion
#   - replay APIs
#   - vector prediction APIs
#   - websocket streaming
#   - sandbox orchestration
#
# ALL backend runtime access MUST flow through here.
#
# ============================================================================

from __future__ import annotations

import asyncio
import json
import time
import uuid

from typing import Dict, List, Optional

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    HTTPException
)

from pydantic import BaseModel

from hhs_python.runtime.hhs_runtime_controller import (
    HHSRuntimeController
)

from hhs_graph.hhs_multimodal_receipt_graph_v1 import (
    HHSMultimodalReceiptGraph
)

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(
    prefix="/api/runtime",
    tags=["runtime"]
)

# ============================================================================
# GLOBAL RUNTIME
# ============================================================================

runtime_controller = HHSRuntimeController()

runtime_graph = HHSMultimodalReceiptGraph()

# ============================================================================
# WEBSOCKET CLIENTS
# ============================================================================

runtime_clients: List[WebSocket] = []

# ============================================================================
# REQUEST MODELS
# ============================================================================

class RuntimeStepRequest(BaseModel):

    steps: int = 1

# ----------------------------------------------------------------------------

class SandboxCreateRequest(BaseModel):

    metadata: Optional[Dict] = None

# ============================================================================
# HELPERS
# ============================================================================

async def broadcast_runtime_state():

    if not runtime_clients:
        return

    packet = (
        runtime_controller.export_multimodal_packet()
    )

    dead = []

    for ws in runtime_clients:

        try:

            await ws.send_text(
                json.dumps(packet)
            )

        except Exception:

            dead.append(ws)

    for ws in dead:

        if ws in runtime_clients:
            runtime_clients.remove(ws)

# ============================================================================
# RUNTIME ROUTES
# ============================================================================

@router.get("/state")
async def get_runtime_state():

    return runtime_controller.latest_runtime_state()

# ----------------------------------------------------------------------------

@router.post("/step")
async def runtime_step(
    request: RuntimeStepRequest
):

    results = runtime_controller.run_steps(
        request.steps
    )

    for result in results:

        packet = (
            runtime_controller.export_multimodal_packet()
        )

        runtime_graph.ingest_runtime_state(packet)

    await broadcast_runtime_state()

    return {

        "steps_executed":
            len(results),

        "runtime":
            runtime_controller.latest_runtime_state()
    }

# ----------------------------------------------------------------------------

@router.post("/halt")
async def halt_runtime():

    result = runtime_controller.halt()

    await broadcast_runtime_state()

    return result

# ----------------------------------------------------------------------------

@router.post("/receipt/commit")
async def commit_receipt():

    receipt = runtime_controller.commit_receipt()

    return receipt

# ============================================================================
# GRAPH ROUTES
# ============================================================================

@router.get("/graph/summary")
async def graph_summary():

    return runtime_graph.export_graph_summary()

# ----------------------------------------------------------------------------

@router.get("/graph/hash/{hash72}")
async def graph_lookup_hash(
    hash72: str
):

    node = runtime_graph.get_by_hash72(hash72)

    if node is None:

        raise HTTPException(
            status_code=404,
            detail="Hash72 node not found"
        )

    return node

# ----------------------------------------------------------------------------

@router.get("/graph/replay/{node_id}")
async def graph_replay(
    node_id: str
):

    if node_id not in runtime_graph.nodes:

        raise HTTPException(
            status_code=404,
            detail="Node not found"
        )

    replay = runtime_graph.replay_chain(
        node_id
    )

    return replay

# ============================================================================
# PREDICTION ROUTES
# ============================================================================

@router.get("/predict/{node_id}")
async def predict_next_states(
    node_id: str,
    top_k: int = 5
):

    if node_id not in runtime_graph.nodes:

        raise HTTPException(
            status_code=404,
            detail="Node not found"
        )

    predictions = (
        runtime_graph.predict_next_states(
            node_id=node_id,
            top_k=top_k
        )
    )

    results = []

    for similarity, node in predictions:

        results.append({

            "similarity":
                similarity,

            "node_id":
                node.node_id,

            "state_hash72":
                node.state_hash72,

            "receipt_hash72":
                node.receipt_hash72,

            "step":
                node.step
        })

    return results

# ============================================================================
# SANDBOX ROUTES
# ============================================================================

@router.post("/sandbox/create")
async def create_sandbox(
    request: SandboxCreateRequest
):

    sandbox = runtime_controller.create_sandbox(
        metadata=request.metadata
    )

    return {

        "sandbox_id":
            sandbox.sandbox_id,

        "created_at":
            sandbox.created_at
    }

# ----------------------------------------------------------------------------

@router.post("/sandbox/{sandbox_id}/step")
async def sandbox_step(
    sandbox_id: str
):

    if sandbox_id not in runtime_controller.sandboxes:

        raise HTTPException(
            status_code=404,
            detail="Sandbox not found"
        )

    result = runtime_controller.sandbox_step(
        sandbox_id
    )

    return result

# ============================================================================
# VECTOR ROUTES
# ============================================================================

@router.get("/vector/latest")
async def latest_vector_record():

    return runtime_controller.export_vector_record()

# ============================================================================
# MULTIMODAL PACKET
# ============================================================================

@router.get("/packet/latest")
async def latest_multimodal_packet():

    return runtime_controller.export_multimodal_packet()

# ============================================================================
# WEBSOCKET STREAM
# ============================================================================

@router.websocket("/ws/runtime")
async def websocket_runtime_stream(
    websocket: WebSocket
):

    await websocket.accept()

    runtime_clients.append(websocket)

    try:

        while True:

            packet = (
                runtime_controller
                .export_multimodal_packet()
            )

            await websocket.send_text(
                json.dumps(packet)
            )

            await asyncio.sleep(0.05)

    except WebSocketDisconnect:

        if websocket in runtime_clients:
            runtime_clients.remove(websocket)

# ============================================================================
# EVENT HOOKS
# ============================================================================

def _runtime_step_hook(payload):

    packet = (
        runtime_controller.export_multimodal_packet()
    )

    runtime_graph.ingest_runtime_state(packet)

# ----------------------------------------------------------------------------

runtime_controller.add_listener(
    "runtime_step",
    _runtime_step_hook
)

# ============================================================================
# SELF TEST
# ============================================================================

def route_self_test():

    runtime_controller.run_steps(3)

    packet = (
        runtime_controller.export_multimodal_packet()
    )

    runtime_graph.ingest_runtime_state(packet)

    print()

    print("RUNTIME")

    print(runtime_controller.latest_runtime_state())

    print()

    print("GRAPH")

    print(runtime_graph.export_graph_summary())

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    route_self_test()
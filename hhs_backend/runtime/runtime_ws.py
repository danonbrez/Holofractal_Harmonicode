# ============================================================================
# hhs_backend/runtime/runtime_ws.py
# ============================================================================
#
# Canonical Runtime Websocket Transport Layer
#
# Responsibilities:
#
#   - runtime websocket transport
#   - replay websocket transport
#   - graph websocket transport
#   - transport websocket transport
#   - canonical event propagation
#   - replay propagation
#   - graph projection propagation
#   - websocket lifecycle management
#
# IMPORTANT
# ----------------------------------------------------------------------------
#
# ALL websocket payloads MUST originate from:
#
#   runtime_event_schema.py
#
# using:
#
#   event.to_websocket_payload()
#
# NOT ad-hoc dictionaries.
#
# ============================================================================

from __future__ import annotations

import asyncio
import json
import logging

from collections import defaultdict

from typing import Any
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

try:
    from fastapi import APIRouter
    from fastapi import WebSocket
    from fastapi import WebSocketDisconnect
except ModuleNotFoundError:  # pragma: no cover - optional runtime dependency
    class APIRouter:  # type: ignore[override]
        def __init__(self, *args, **kwargs):
            pass

        def websocket(self, *args, **kwargs):
            def decorator(fn):
                return fn

            return decorator

    class WebSocket:  # type: ignore[override]
        pass

    class WebSocketDisconnect(Exception):
        pass

from hhs_backend.runtime.runtime_event_schema import (
    HHSRuntimeEventEnvelope,
)
from hhs_backend.runtime.gui_projection_contract_v1 import (
    AUTHORITY as GUI_KERNEL_AUTHORITY,
    CHANNEL_BINDINGS,
    validate_gui_projection_payload,
)
from hhs_runtime.hhs_runtime_dataflow_guard_v1 import attach_egress_record

# ============================================================================
# Logging
# ============================================================================

logger = logging.getLogger(
    "HHS_RUNTIME_WS"
)

# ============================================================================
# Router
# ============================================================================

runtime_ws_router = APIRouter()

# ============================================================================
# RuntimeWSManager
# ============================================================================

class RuntimeWSManager:

    """
    Canonical websocket transport authority.

    Frontend websocket layers are projection layers only.
    """

    # =====================================================================
    # Constructor
    # =====================================================================

    def __init__(self):

        # -------------------------------------------------------------
        # Socket Sets
        # -------------------------------------------------------------

        self.runtime_sockets: Set[
            WebSocket
        ] = set()

        self.replay_sockets: Set[
            WebSocket
        ] = set()

        self.graph_sockets: Set[
            WebSocket
        ] = set()

        self.transport_sockets: Set[
            WebSocket
        ] = set()

        # -------------------------------------------------------------
        # Metrics
        # -------------------------------------------------------------

        self.total_connections = 0

        self.total_disconnects = 0

        self.total_events_sent = 0

        self.total_replay_events = 0

        self.total_graph_events = 0

        self.total_transport_events = 0

        # -------------------------------------------------------------
        # Replay Cache
        # -------------------------------------------------------------

        self.replay_cache: List[
            Dict[str, Any]
        ] = []

        self.max_replay_cache = 4096

        # -------------------------------------------------------------
        # Runtime Index
        # -------------------------------------------------------------

        self.runtime_index: DefaultDict[
            str,
            List[Dict[str, Any]]
        ] = defaultdict(list)

    # =====================================================================
    # Runtime Connect
    # =====================================================================

    async def connect_runtime(
        self,
        websocket: WebSocket
    ):

        await websocket.accept()

        self.runtime_sockets.add(
            websocket
        )

        self.total_connections += 1

        logger.info(
            "Runtime websocket connected."
        )

    # =====================================================================
    # Replay Connect
    # =====================================================================

    async def connect_replay(
        self,
        websocket: WebSocket
    ):

        await websocket.accept()

        self.replay_sockets.add(
            websocket
        )

        self.total_connections += 1

        logger.info(
            "Replay websocket connected."
        )

    # =====================================================================
    # Graph Connect
    # =====================================================================

    async def connect_graph(
        self,
        websocket: WebSocket
    ):

        await websocket.accept()

        self.graph_sockets.add(
            websocket
        )

        self.total_connections += 1

        logger.info(
            "Graph websocket connected."
        )

    # =====================================================================
    # Transport Connect
    # =====================================================================

    async def connect_transport(
        self,
        websocket: WebSocket
    ):

        await websocket.accept()

        self.transport_sockets.add(
            websocket
        )

        self.total_connections += 1

        logger.info(
            "Transport websocket connected."
        )

    # =====================================================================
    # Disconnect
    # =====================================================================

    def disconnect(
        self,
        websocket: WebSocket
    ):

        self.runtime_sockets.discard(
            websocket
        )

        self.replay_sockets.discard(
            websocket
        )

        self.graph_sockets.discard(
            websocket
        )

        self.transport_sockets.discard(
            websocket
        )

        self.total_disconnects += 1

        logger.info(
            "Websocket disconnected."
        )

    # =====================================================================
    # Channel Projection Payload
    # =====================================================================

    def build_channel_projection_payload(
        self,
        event: HHSRuntimeEventEnvelope,
        channel: str,
    ) -> Dict[str, Any]:
        """Build the canonical GUI-facing payload for one websocket channel.

        Pass 046 requires each browser panel to receive a channel-specific
        projection with the live kernel fields needed to reject synthetic GUI
        state.  The event envelope remains the source of truth; this helper
        only projects it into runtime/replay/graph/transport panel shape.
        """

        binding = CHANNEL_BINDINGS[channel]
        event_type = binding["event_type"]
        base_payload = event.to_websocket_payload()
        sequence_id = base_payload.get("sequence_id")
        kernel_tick = base_payload.get("kernel_tick")
        runtime_state_hash72 = base_payload.get("runtime_state_hash72")
        payload: Dict[str, Any] = {
            **base_payload,
            "event": event_type,
            "event_type": event_type,
            "source_event_type": event.event_type,
            "channel": channel,
            "panel": binding["panel"],
            "state_lane": binding["state_lane"],
            "sequence_id": sequence_id,
            "kernel_tick": kernel_tick,
            "runtime_state_hash72": runtime_state_hash72,
            "authority": base_payload.get("authority") or GUI_KERNEL_AUTHORITY,
            "gui_projection_contract": "HHS_LIVE_GUI_PROJECTION_CONTRACT_V1",
            "node_generated_runtime_event": False,
        }

        if event_type == "replay":
            payload["payload"] = {
                "replay_packet": event.to_replay_packet(),
                "runtime_payload": event.payload,
                "receipt_hash72": event.receipt_hash72,
                "runtime_state_hash72": runtime_state_hash72,
            }
        elif event_type == "graph":
            graph_projection = event.to_graph_projection()
            payload["payload"] = {
                "nodes": [graph_projection],
                "edges": ([{
                    "source": event.parent_event_hash72,
                    "target": event.event_hash72,
                    "edge_type": "kernel_event_transition",
                }] if event.parent_event_hash72 else []),
                "runtime_state_hash72": runtime_state_hash72,
            }
        elif event_type == "transport":
            payload["payload"] = {
                "transport": "kernel_event_projection",
                "channel": channel,
                "sequence_id": sequence_id,
                "kernel_tick": kernel_tick,
                "runtime_state_hash72": runtime_state_hash72,
                "connected_channels": list(CHANNEL_BINDINGS.keys()),
                "receipt_hash72": event.receipt_hash72,
            }

        decision = validate_gui_projection_payload(payload)
        payload["gui_projection_valid"] = decision["ok"]
        payload["gui_projection_reasons"] = decision["reasons"]
        return payload

    # =====================================================================
    # Runtime Event Broadcast
    # =====================================================================

    async def broadcast_runtime_event(

        self,

        event:
            HHSRuntimeEventEnvelope

    ):

        # Pass 045: when no websocket clients are attached, retain the
        # canonical event projection in replay cache without appending a fresh
        # egress-ledger record on every background kernel tick.  This prevents
        # inert live workflow metadata from accumulating after validation.
        base_payload = self.build_channel_projection_payload(event, "/ws/runtime")
        payload = (
            attach_egress_record(
                "runtime_ws.broadcast_runtime_event",
                base_payload,
            )
            if self.runtime_sockets
            else base_payload
        )

        # -------------------------------------------------------------
        # Replay Cache
        # -------------------------------------------------------------

        self.replay_cache.append(
            payload
        )

        if (
            len(self.replay_cache)
            >
            self.max_replay_cache
        ):

            self.replay_cache = (

                self.replay_cache[
                    -self.max_replay_cache:
                ]
            )

        # -------------------------------------------------------------
        # Runtime Index
        # -------------------------------------------------------------

        runtime_id = payload.get(
            "runtime_id",
            "default"
        )

        self.runtime_index[
            runtime_id
        ].append(payload)

        # -------------------------------------------------------------
        # Broadcast
        # -------------------------------------------------------------

        await self._broadcast_json(

            self.runtime_sockets,

            payload
        )

        self.total_events_sent += 1

    # =====================================================================
    # Replay Broadcast
    # =====================================================================

    async def broadcast_replay_event(

        self,

        event:
            HHSRuntimeEventEnvelope

    ):

        if not self.replay_sockets:
            return

        payload = attach_egress_record(
            "runtime_ws.broadcast_replay_event",
            self.build_channel_projection_payload(event, "/ws/replay"),
        )

        await self._broadcast_json(

            self.replay_sockets,

            payload
        )

        self.total_replay_events += 1

    # =====================================================================
    # Graph Broadcast
    # =====================================================================

    async def broadcast_graph_event(

        self,

        event:
            HHSRuntimeEventEnvelope

    ):

        if not self.graph_sockets:
            return

        payload = attach_egress_record(
            "runtime_ws.broadcast_graph_event",
            self.build_channel_projection_payload(event, "/ws/graph"),
        )

        await self._broadcast_json(

            self.graph_sockets,

            payload
        )

        self.total_graph_events += 1

    # =====================================================================
    # Transport Broadcast
    # =====================================================================

    async def broadcast_transport_event(

        self,

        event:
            HHSRuntimeEventEnvelope

    ):

        if not self.transport_sockets:
            return

        payload = attach_egress_record(
            "runtime_ws.broadcast_transport_event",
            self.build_channel_projection_payload(event, "/ws/transport"),
        )

        await self._broadcast_json(

            self.transport_sockets,

            payload
        )

        self.total_transport_events += 1

    # =====================================================================
    # Broadcast JSON
    # =====================================================================

    async def _broadcast_json(

        self,

        sockets: Set[WebSocket],

        payload: Dict[str, Any]

    ):

        disconnected = []

        serialized = json.dumps(
            payload
        )

        for websocket in sockets:

            try:

                await websocket.send_text(
                    serialized
                )

            except Exception:

                disconnected.append(
                    websocket
                )

        for websocket in disconnected:

            self.disconnect(
                websocket
            )

    # =====================================================================
    # Replay Snapshot
    # =====================================================================

    async def send_replay_snapshot(
        self,
        websocket: WebSocket
    ):

        try:

            await websocket.send_text(

                json.dumps({

                    "event_type":
                        "replay",

                    "channel":
                        "/ws/replay",

                    "source_event_type":
                        "replay_snapshot",

                    "authority":
                        GUI_KERNEL_AUTHORITY,

                    "payload":
                        {"replay_cache": self.replay_cache}
                })
            )

        except Exception:

            logger.exception(
                "Replay snapshot failure."
            )

    # =====================================================================
    # Metrics
    # =====================================================================

    def metrics(self):

        return {

            "runtime_sockets":
                len(
                    self.runtime_sockets
                ),

            "replay_sockets":
                len(
                    self.replay_sockets
                ),

            "graph_sockets":
                len(
                    self.graph_sockets
                ),

            "transport_sockets":
                len(
                    self.transport_sockets
                ),

            "total_connections":
                self.total_connections,

            "total_disconnects":
                self.total_disconnects,

            "total_events_sent":
                self.total_events_sent,

            "total_replay_events":
                self.total_replay_events,

            "total_graph_events":
                self.total_graph_events,

            "total_transport_events":
                self.total_transport_events,

            "replay_cache":
                len(self.replay_cache),

            "runtime_index":
                len(self.runtime_index)
        }

# ============================================================================
# Global Manager
# ============================================================================

runtime_ws_manager = RuntimeWSManager()

# ============================================================================
# Runtime WS
# ============================================================================

@runtime_ws_router.websocket(
    "/ws/runtime"
)
async def runtime_ws(
    websocket: WebSocket
):

    await runtime_ws_manager.connect_runtime(
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        runtime_ws_manager.disconnect(
            websocket
        )

# ============================================================================
# Replay WS
# ============================================================================

@runtime_ws_router.websocket(
    "/ws/replay"
)
async def replay_ws(
    websocket: WebSocket
):

    await runtime_ws_manager.connect_replay(
        websocket
    )

    await runtime_ws_manager.send_replay_snapshot(
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        runtime_ws_manager.disconnect(
            websocket
        )

# ============================================================================
# Graph WS
# ============================================================================

@runtime_ws_router.websocket(
    "/ws/graph"
)
async def graph_ws(
    websocket: WebSocket
):

    await runtime_ws_manager.connect_graph(
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        runtime_ws_manager.disconnect(
            websocket
        )

# ============================================================================
# Transport WS
# ============================================================================

@runtime_ws_router.websocket(
    "/ws/transport"
)
async def transport_ws(
    websocket: WebSocket
):

    await runtime_ws_manager.connect_transport(
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        runtime_ws_manager.disconnect(
            websocket
        )

# ============================================================================
# Runtime Event Propagation
# ============================================================================

async def propagate_runtime_event(

    event:
        HHSRuntimeEventEnvelope

):

    await asyncio.gather(

        runtime_ws_manager.broadcast_runtime_event(
            event
        ),

        runtime_ws_manager.broadcast_replay_event(
            event
        ),

        runtime_ws_manager.broadcast_graph_event(
            event
        ),

        runtime_ws_manager.broadcast_transport_event(
            event
        )
    )

# ============================================================================
# Health
# ============================================================================

def runtime_ws_health():

    return {

        "status":
            "healthy",

        "metrics":
            runtime_ws_manager.metrics()
    }
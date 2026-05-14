from __future__ import annotations

import asyncio
import json
import time
from collections import defaultdict
from typing import Any
from typing import Dict
from typing import List
from typing import Set

from fastapi import WebSocket
from fastapi import WebSocketDisconnect

# =========================================================
# Runtime Event Types
# =========================================================

EVENT_RUNTIME = "runtime"
EVENT_REPLAY = "replay"
EVENT_GRAPH = "graph"
EVENT_TRANSPORT = "transport"
EVENT_RECEIPT = "receipt"
EVENT_CERTIFICATION = "certification"

# =========================================================
# Runtime Connection Registry
# =========================================================

class RuntimeConnectionRegistry:

    def __init__(self) -> None:

        self.channels: Dict[
            str,
            Set[WebSocket]
        ] = defaultdict(set)

    # -----------------------------------------------------

    async def connect(
        self,
        channel: str,
        websocket: WebSocket
    ) -> None:

        await websocket.accept()

        self.channels[channel].add(
            websocket
        )

        print(
            f"[ws/{channel}] connected "
            f"({len(self.channels[channel])})"
        )

    # -----------------------------------------------------

    def disconnect(
        self,
        channel: str,
        websocket: WebSocket
    ) -> None:

        self.channels[channel].discard(
            websocket
        )

        print(
            f"[ws/{channel}] disconnected "
            f"({len(self.channels[channel])})"
        )

    # -----------------------------------------------------

    async def broadcast(
        self,
        channel: str,
        payload: Dict[str, Any]
    ) -> None:

        dead: List[WebSocket] = []

        encoded = json.dumps(payload)

        for websocket in self.channels[channel]:

            try:

                await websocket.send_text(
                    encoded
                )

            except Exception:

                dead.append(websocket)

        for websocket in dead:

            self.disconnect(
                channel,
                websocket
            )

# =========================================================
# Global Registry
# =========================================================

runtime_connections = (
    RuntimeConnectionRegistry()
)

# =========================================================
# Event Factory
# =========================================================

def build_runtime_event(
    event_type: str,
    payload: Dict[str, Any]
) -> Dict[str, Any]:

    return {

        "event_type":
            event_type,

        "timestamp_ns":
            time.time_ns(),

        "payload":
            payload
    }

# =========================================================
# Runtime Heartbeat Loops
# =========================================================

async def runtime_heartbeat_loop() -> None:

    step = 0

    while True:

        step += 1

        event = build_runtime_event(

            EVENT_RUNTIME,

            {

                "runtime_status":
                    "online",

                "step":
                    step,

                "phase":
                    "runtime_loop",

                "uptime":
                    time.time()
            }
        )

        await runtime_connections.broadcast(

            EVENT_RUNTIME,

            event
        )

        await asyncio.sleep(1)

# ---------------------------------------------------------

async def replay_heartbeat_loop() -> None:

    replay_tick = 0

    while True:

        replay_tick += 1

        event = build_runtime_event(

            EVENT_REPLAY,

            {

                "replay_tick":
                    replay_tick,

                "replay_status":
                    "stable",

                "timeline_position":
                    replay_tick
            }
        )

        await runtime_connections.broadcast(

            EVENT_REPLAY,

            event
        )

        await asyncio.sleep(1)

# ---------------------------------------------------------

async def graph_heartbeat_loop() -> None:

    graph_tick = 0

    while True:

        graph_tick += 1

        event = build_runtime_event(

            EVENT_GRAPH,

            {

                "graph_tick":
                    graph_tick,

                "nodes":
                    12,

                "edges":
                    24,

                "projection":
                    "runtime_topology"
            }
        )

        await runtime_connections.broadcast(

            EVENT_GRAPH,

            event
        )

        await asyncio.sleep(1)

# ---------------------------------------------------------

async def transport_heartbeat_loop() -> None:

    transport_tick = 0

    while True:

        transport_tick += 1

        event = build_runtime_event(

            EVENT_TRANSPORT,

            {

                "transport_tick":
                    transport_tick,

                "transport_flux":
                    1.0,

                "continuity":
                    "stable"
            }
        )

        await runtime_connections.broadcast(

            EVENT_TRANSPORT,

            event
        )

        await asyncio.sleep(1)

# =========================================================
# Runtime Startup
# =========================================================

runtime_tasks_started = False

async def ensure_runtime_tasks() -> None:

    global runtime_tasks_started

    if runtime_tasks_started:

        return

    runtime_tasks_started = True

    asyncio.create_task(
        runtime_heartbeat_loop()
    )

    asyncio.create_task(
        replay_heartbeat_loop()
    )

    asyncio.create_task(
        graph_heartbeat_loop()
    )

    asyncio.create_task(
        transport_heartbeat_loop()
    )

    print(
        "[runtime_ws] heartbeat tasks started"
    )

# =========================================================
# WebSocket Authorities
# =========================================================

async def runtime_stream(
    websocket: WebSocket
) -> None:

    await ensure_runtime_tasks()

    await runtime_connections.connect(

        EVENT_RUNTIME,

        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        runtime_connections.disconnect(

            EVENT_RUNTIME,

            websocket
        )

# ---------------------------------------------------------

async def replay_stream(
    websocket: WebSocket
) -> None:

    await ensure_runtime_tasks()

    await runtime_connections.connect(

        EVENT_REPLAY,

        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        runtime_connections.disconnect(

            EVENT_REPLAY,

            websocket
        )

# ---------------------------------------------------------

async def graph_stream(
    websocket: WebSocket
) -> None:

    await ensure_runtime_tasks()

    await runtime_connections.connect(

        EVENT_GRAPH,

        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        runtime_connections.disconnect(

            EVENT_GRAPH,

            websocket
        )

# ---------------------------------------------------------

async def transport_stream(
    websocket: WebSocket
) -> None:

    await ensure_runtime_tasks()

    await runtime_connections.connect(

        EVENT_TRANSPORT,

        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        runtime_connections.disconnect(

            EVENT_TRANSPORT,

            websocket
        )

# =========================================================
# External Runtime Emitters
# =========================================================

async def emit_runtime_event(
    payload: Dict[str, Any]
) -> None:

    await runtime_connections.broadcast(

        EVENT_RUNTIME,

        build_runtime_event(

            EVENT_RUNTIME,

            payload
        )
    )

# ---------------------------------------------------------

async def emit_replay_event(
    payload: Dict[str, Any]
) -> None:

    await runtime_connections.broadcast(

        EVENT_REPLAY,

        build_runtime_event(

            EVENT_REPLAY,

            payload
        )
    )

# ---------------------------------------------------------

async def emit_graph_event(
    payload: Dict[str, Any]
) -> None:

    await runtime_connections.broadcast(

        EVENT_GRAPH,

        build_runtime_event(

            EVENT_GRAPH,

            payload
        )
    )

# ---------------------------------------------------------

async def emit_transport_event(
    payload: Dict[str, Any]
) -> None:

    await runtime_connections.broadcast(

        EVENT_TRANSPORT,

        build_runtime_event(

            EVENT_TRANSPORT,

            payload
        )
    )
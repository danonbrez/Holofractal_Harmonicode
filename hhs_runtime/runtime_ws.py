from __future__ import annotations

import asyncio
import json
import time

from collections import defaultdict

from typing import Any
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from hhs_runtime.runtime_event_bus import (

    runtime_event_bus
)

from hhs_runtime.runtime_event_schema import (

    EVENT_RUNTIME,

    EVENT_REPLAY,

    EVENT_GRAPH,

    EVENT_TRANSPORT,

    EVENT_RECEIPT,

    EVENT_CERTIFICATION,

    HHSEvent
)

# =========================================================
# Constants
# =========================================================

HEARTBEAT_INTERVAL = 5.0

MAX_EVENT_BUFFER = 2048

# =========================================================
# Runtime WebSocket Hub
# =========================================================

class RuntimeWebSocketHub:

    def __init__(self) -> None:

        self.channels: DefaultDict[
            str,
            Set[WebSocket]
        ] = defaultdict(set)

        self.event_history: DefaultDict[
            str,
            List[Dict[str, Any]]
        ] = defaultdict(list)

        self.connected_total = 0

        self.disconnected_total = 0

        self.events_broadcast = 0

        self.started_ns = (
            time.time_ns()
        )

        self.heartbeat_tasks: Dict[
            WebSocket,
            asyncio.Task
        ] = {}

    # =====================================================
    # Connect
    # =====================================================

    async def connect(

        self,

        channel: str,

        websocket: WebSocket

    ) -> None:

        await websocket.accept()

        self.channels[channel].add(
            websocket
        )

        self.connected_total += 1

        # -------------------------------------------------
        # Heartbeat
        # -------------------------------------------------

        self.heartbeat_tasks[
            websocket
        ] = asyncio.create_task(

            self._heartbeat_loop(
                channel,
                websocket
            )
        )

        print(

            "[runtime_ws] connect",

            channel,

            f"({len(self.channels[channel])})"
        )

        # -------------------------------------------------
        # Replay Buffer
        # -------------------------------------------------

        history = self.event_history.get(
            channel,
            []
        )

        for event in history[-64:]:

            try:

                await websocket.send_text(

                    json.dumps(event)
                )

            except Exception:

                pass

    # =====================================================
    # Disconnect
    # =====================================================

    async def disconnect(

        self,

        channel: str,

        websocket: WebSocket

    ) -> None:

        if (
            websocket
            in self.channels[channel]
        ):

            self.channels[channel].remove(
                websocket
            )

        self.disconnected_total += 1

        task = self.heartbeat_tasks.pop(
            websocket,
            None
        )

        if task:

            task.cancel()

        print(

            "[runtime_ws] disconnect",

            channel,

            f"({len(self.channels[channel])})"
        )

    # =====================================================
    # Broadcast
    # =====================================================

    async def broadcast(

        self,

        channel: str,

        payload: Dict[str, Any]

    ) -> None:

        self.events_broadcast += 1

        # -------------------------------------------------
        # Event Buffer
        # -------------------------------------------------

        self.event_history[channel].append(
            payload
        )

        if (

            len(
                self.event_history[channel]
            )

            > MAX_EVENT_BUFFER
        ):

            self.event_history[channel] = (

                self.event_history[channel][

                    -MAX_EVENT_BUFFER:
                ]
            )

        # -------------------------------------------------
        # Broadcast
        # -------------------------------------------------

        dead: List[WebSocket] = []

        for websocket in list(

            self.channels[channel]
        ):

            try:

                await websocket.send_text(

                    json.dumps(payload)
                )

            except Exception:

                dead.append(
                    websocket
                )

        # -------------------------------------------------
        # Cleanup
        # -------------------------------------------------

        for websocket in dead:

            await self.disconnect(

                channel,

                websocket
            )

    # =====================================================
    # Heartbeat
    # =====================================================

    async def _heartbeat_loop(

        self,

        channel: str,

        websocket: WebSocket

    ) -> None:

        try:

            while True:

                await asyncio.sleep(
                    HEARTBEAT_INTERVAL
                )

                await websocket.send_text(

                    json.dumps({

                        "event_type":
                            "heartbeat",

                        "timestamp_ns":
                            time.time_ns(),

                        "channel":
                            channel
                    })
                )

        except asyncio.CancelledError:

            return

        except Exception:

            return

    # =====================================================
    # Metrics
    # =====================================================

    def metrics(self):

        return {

            "connected_total":
                self.connected_total,

            "disconnected_total":
                self.disconnected_total,

            "events_broadcast":
                self.events_broadcast,

            "uptime_seconds":

                (
                    time.time_ns()
                    - self.started_ns
                ) / 1e9,

            "channels": {

                channel:

                    len(sockets)

                for channel, sockets
                in self.channels.items()
            },

            "event_buffers": {

                channel:

                    len(history)

                for channel, history
                in self.event_history.items()
            }
        }

# =========================================================
# Global Hub
# =========================================================

runtime_ws_hub = (
    RuntimeWebSocketHub()
)

# =========================================================
# Runtime Streams
# =========================================================

async def runtime_stream(
    websocket: WebSocket
) -> None:

    await runtime_ws_hub.connect(

        EVENT_RUNTIME,

        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        await runtime_ws_hub.disconnect(

            EVENT_RUNTIME,

            websocket
        )

# ---------------------------------------------------------

async def replay_stream(
    websocket: WebSocket
) -> None:

    await runtime_ws_hub.connect(

        EVENT_REPLAY,

        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        await runtime_ws_hub.disconnect(

            EVENT_REPLAY,

            websocket
        )

# ---------------------------------------------------------

async def graph_stream(
    websocket: WebSocket
) -> None:

    await runtime_ws_hub.connect(

        EVENT_GRAPH,

        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        await runtime_ws_hub.disconnect(

            EVENT_GRAPH,

            websocket
        )

# ---------------------------------------------------------

async def transport_stream(
    websocket: WebSocket
) -> None:

    await runtime_ws_hub.connect(

        EVENT_TRANSPORT,

        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        await runtime_ws_hub.disconnect(

            EVENT_TRANSPORT,

            websocket
        )

# =========================================================
# Emit Helpers
# =========================================================

async def emit_runtime_event(
    payload: Dict[str, Any]
) -> None:

    await runtime_ws_hub.broadcast(

        EVENT_RUNTIME,

        payload
    )

# ---------------------------------------------------------

async def emit_replay_event(
    payload: Dict[str, Any]
) -> None:

    await runtime_ws_hub.broadcast(

        EVENT_REPLAY,

        payload
    )

# ---------------------------------------------------------

async def emit_graph_event(
    payload: Dict[str, Any]
) -> None:

    await runtime_ws_hub.broadcast(

        EVENT_GRAPH,

        payload
    )

# ---------------------------------------------------------

async def emit_transport_event(
    payload: Dict[str, Any]
) -> None:

    await runtime_ws_hub.broadcast(

        EVENT_TRANSPORT,

        payload
    )

# ---------------------------------------------------------

async def emit_receipt_event(
    payload: Dict[str, Any]
) -> None:

    await runtime_ws_hub.broadcast(

        EVENT_RECEIPT,

        payload
    )

# ---------------------------------------------------------

async def emit_certification_event(
    payload: Dict[str, Any]
) -> None:

    await runtime_ws_hub.broadcast(

        EVENT_CERTIFICATION,

        payload
    )

# =========================================================
# Event Bus Bridge
# =========================================================

async def bridge_runtime_event(
    event: HHSEvent
) -> None:

    await emit_runtime_event(
        event.to_dict()
    )

# ---------------------------------------------------------

async def bridge_replay_event(
    event: HHSEvent
) -> None:

    await emit_replay_event(
        event.to_dict()
    )

# ---------------------------------------------------------

async def bridge_graph_event(
    event: HHSEvent
) -> None:

    await emit_graph_event(
        event.to_dict()
    )

# ---------------------------------------------------------

async def bridge_transport_event(
    event: HHSEvent
) -> None:

    await emit_transport_event(
        event.to_dict()
    )

# ---------------------------------------------------------

async def bridge_receipt_event(
    event: HHSEvent
) -> None:

    await emit_receipt_event(
        event.to_dict()
    )

# ---------------------------------------------------------

async def bridge_certification_event(
    event: HHSEvent
) -> None:

    await emit_certification_event(
        event.to_dict()
    )

# =========================================================
# Attach Runtime Event Bus
# =========================================================

runtime_event_bus.subscribe(

    EVENT_RUNTIME,

    bridge_runtime_event
)

runtime_event_bus.subscribe(

    EVENT_REPLAY,

    bridge_replay_event
)

runtime_event_bus.subscribe(

    EVENT_GRAPH,

    bridge_graph_event
)

runtime_event_bus.subscribe(

    EVENT_TRANSPORT,

    bridge_transport_event
)

runtime_event_bus.subscribe(

    EVENT_RECEIPT,

    bridge_receipt_event
)

runtime_event_bus.subscribe(

    EVENT_CERTIFICATION,

    bridge_certification_event
)
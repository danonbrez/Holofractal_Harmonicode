# ============================================================================
# hhs_backend/websocket/runtime_stream_manager.py
# HARMONICODE / HHS
# CANONICAL RUNTIME STREAM MANAGER
#
# PURPOSE
# -------
# Centralized websocket orchestration layer for:
#
#   - runtime broadcasting
#   - websocket lifecycle management
#   - replay streaming
#   - graph streaming
#   - heartbeat monitoring
#   - sandbox channels
#   - multimodal packet routing
#   - future distributed runtime replication
#
# ALL realtime runtime streaming MUST pass through here.
#
# ============================================================================

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any

from fastapi import WebSocket

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger("HHS_STREAM")

# ============================================================================
# CLIENT STATE
# ============================================================================

@dataclass
class HHSStreamClient:

    client_id: str

    websocket: WebSocket

    connected_at: float

    subscriptions: Set[str] = field(
        default_factory=set
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    heartbeat_ts: float = field(
        default_factory=time.time
    )

# ============================================================================
# STREAM MANAGER
# ============================================================================

class HHSRuntimeStreamManager:

    """
    Canonical websocket runtime transport manager.
    """

    def __init__(self):

        self.clients: Dict[
            str,
            HHSStreamClient
        ] = {}

        self.channels: Dict[
            str,
            Set[str]
        ] = {}

        self.total_messages_sent = 0

        self.total_connections = 0

        self.total_disconnects = 0

    # =====================================================================
    # CONNECTION MANAGEMENT
    # =====================================================================

    async def connect(
        self,
        websocket: WebSocket,
        metadata: Optional[Dict] = None
    ) -> str:

        await websocket.accept()

        client_id = str(uuid.uuid4())

        client = HHSStreamClient(

            client_id=client_id,

            websocket=websocket,

            connected_at=time.time(),

            metadata=metadata or {}
        )

        self.clients[client_id] = client

        self.total_connections += 1

        logger.info(
            f"Client connected: {client_id}"
        )

        return client_id

    # ---------------------------------------------------------------------

    async def disconnect(
        self,
        client_id: str
    ):

        if client_id not in self.clients:
            return

        client = self.clients[client_id]

        for channel in client.subscriptions:

            if channel in self.channels:

                self.channels[channel].discard(
                    client_id
                )

        try:

            await client.websocket.close()

        except Exception:
            pass

        del self.clients[client_id]

        self.total_disconnects += 1

        logger.info(
            f"Client disconnected: {client_id}"
        )

    # =====================================================================
    # CHANNELS
    # =====================================================================

    def subscribe(
        self,
        client_id: str,
        channel: str
    ):

        if client_id not in self.clients:
            return

        client = self.clients[client_id]

        client.subscriptions.add(channel)

        if channel not in self.channels:
            self.channels[channel] = set()

        self.channels[channel].add(client_id)

    # ---------------------------------------------------------------------

    def unsubscribe(
        self,
        client_id: str,
        channel: str
    ):

        if client_id not in self.clients:
            return

        client = self.clients[client_id]

        client.subscriptions.discard(channel)

        if channel in self.channels:

            self.channels[channel].discard(
                client_id
            )

    # =====================================================================
    # HEARTBEAT
    # =====================================================================

    def heartbeat(
        self,
        client_id: str
    ):

        if client_id not in self.clients:
            return

        self.clients[
            client_id
        ].heartbeat_ts = time.time()

    # ---------------------------------------------------------------------

    async def prune_dead_clients(
        self,
        timeout_seconds: float = 60.0
    ):

        now = time.time()

        dead = []

        for client_id, client in self.clients.items():

            delta = now - client.heartbeat_ts

            if delta > timeout_seconds:

                dead.append(client_id)

        for client_id in dead:

            await self.disconnect(client_id)

    # =====================================================================
    # BROADCAST
    # =====================================================================

    async def broadcast(
        self,
        packet: Dict
    ):

        dead = []

        encoded = json.dumps(packet)

        for client_id, client in self.clients.items():

            try:

                await client.websocket.send_text(
                    encoded
                )

                self.total_messages_sent += 1

            except Exception:

                dead.append(client_id)

        for client_id in dead:

            await self.disconnect(client_id)

    # ---------------------------------------------------------------------

    async def broadcast_channel(
        self,
        channel: str,
        packet: Dict
    ):

        if channel not in self.channels:
            return

        encoded = json.dumps(packet)

        dead = []

        for client_id in self.channels[channel]:

            if client_id not in self.clients:
                continue

            client = self.clients[client_id]

            try:

                await client.websocket.send_text(
                    encoded
                )

                self.total_messages_sent += 1

            except Exception:

                dead.append(client_id)

        for client_id in dead:

            await self.disconnect(client_id)

    # =====================================================================
    # REPLAY STREAMING
    # =====================================================================

    async def stream_replay(
        self,
        client_id: str,
        replay_data: List[Dict],
        delay: float = 0.01
    ):

        if client_id not in self.clients:
            return

        client = self.clients[client_id]

        for packet in replay_data:

            try:

                await client.websocket.send_text(
                    json.dumps(packet)
                )

                await asyncio.sleep(delay)

            except Exception:

                await self.disconnect(client_id)

                return

    # =====================================================================
    # GRAPH STREAMING
    # =====================================================================

    async def stream_graph_node(
        self,
        node_packet: Dict
    ):

        await self.broadcast_channel(
            "graph",
            node_packet
        )

    # =====================================================================
    # MULTIMODAL STREAMING
    # =====================================================================

    async def stream_multimodal_packet(
        self,
        packet: Dict
    ):

        await self.broadcast_channel(
            "multimodal",
            packet
        )

    # =====================================================================
    # METRICS
    # =====================================================================

    def metrics(self):

        return {

            "connected_clients":
                len(self.clients),

            "channels":
                len(self.channels),

            "messages_sent":
                self.total_messages_sent,

            "total_connections":
                self.total_connections,

            "total_disconnects":
                self.total_disconnects,
        }

# ============================================================================
# GLOBAL STREAM MANAGER
# ============================================================================

runtime_stream_manager = (
    HHSRuntimeStreamManager()
)

# ============================================================================
# SELF TEST
# ============================================================================

def stream_manager_self_test():

    print()

    print("STREAM MANAGER READY")

    print(
        runtime_stream_manager.metrics()
    )

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    stream_manager_self_test()
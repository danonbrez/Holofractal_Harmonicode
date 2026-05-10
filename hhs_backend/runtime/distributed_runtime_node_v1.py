# ============================================================================
# hhs_backend/runtime/distributed_runtime_node_v1.py
# HARMONICODE / HHS
# DISTRIBUTED RUNTIME NODE
#
# PURPOSE
# -------
# Canonical distributed runtime federation layer for:
#
#   - runtime node coordination
#   - distributed replay synchronization
#   - append-only event propagation
#   - graph synchronization
#   - distributed prediction routing
#   - deterministic node recovery
#   - multimodal state replication
#
# Distributed state MUST remain replay-safe and append-only.
#
# ============================================================================

from __future__ import annotations

import asyncio
import logging
import time
import uuid

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from hhs_backend.runtime.runtime_orchestrator import (
    runtime_orchestrator
)

from hhs_backend.runtime.runtime_event_bus import (
    runtime_event_bus,

    EVENT_RUNTIME_STEP,

    EVENT_RECEIPT_COMMIT,

    EVENT_MULTIMODAL_PACKET
)

from hhs_backend.runtime.runtime_replay_engine import (
    runtime_replay_engine
)

from hhs_backend.runtime.runtime_prediction_engine import (
    runtime_prediction_engine
)

from hhs_storage.runtime_state_store_v1 import (
    runtime_state_store
)

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger("HHS_DISTRIBUTED_NODE")

# ============================================================================
# NODE STATES
# ============================================================================

STATE_INITIALIZING = "initializing"

STATE_ACTIVE = "active"

STATE_SYNCING = "syncing"

STATE_RECOVERING = "recovering"

STATE_HALTED = "halted"

# ============================================================================
# NODE PEER
# ============================================================================

@dataclass
class HHSNodePeer:

    peer_id: str

    connected_at: float

    last_seen: float

    state: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# DISTRIBUTED EVENT
# ============================================================================

@dataclass
class HHSDistributedEvent:

    event_id: str

    created_at: float

    source_node: str

    event_type: str

    payload: Dict[str, Any]

# ============================================================================
# DISTRIBUTED NODE
# ============================================================================

class HHSDistributedRuntimeNode:

    """
    Canonical distributed runtime federation node.
    """

    def __init__(self):

        self.node_id = str(uuid.uuid4())

        self.created_at = time.time()

        self.state = STATE_INITIALIZING

        self.peers: Dict[
            str,
            HHSNodePeer
        ] = {}

        self.event_log: List[
            HHSDistributedEvent
        ] = []

        self.total_events_synced = 0

        self.total_replays_synced = 0

        self.total_prediction_routes = 0

        self._register_routes()

    # =====================================================================
    # ROUTE REGISTRATION
    # =====================================================================

    def _register_routes(self):

        runtime_event_bus.subscribe(

            EVENT_RUNTIME_STEP,

            self._on_runtime_step
        )

        runtime_event_bus.subscribe(

            EVENT_RECEIPT_COMMIT,

            self._on_receipt_commit
        )

        runtime_event_bus.subscribe(

            EVENT_MULTIMODAL_PACKET,

            self._on_multimodal_packet
        )

    # =====================================================================
    # NODE LIFECYCLE
    # =====================================================================

    async def startup(self):

        logger.info(
            f"Distributed node starting: "
            f"{self.node_id}"
        )

        self.state = STATE_ACTIVE

    # ---------------------------------------------------------------------

    async def shutdown(self):

        logger.warning(
            f"Distributed node shutting down: "
            f"{self.node_id}"
        )

        self.state = STATE_HALTED

    # =====================================================================
    # PEERS
    # =====================================================================

    def register_peer(
        self,
        peer_id: str,
        metadata: Optional[Dict] = None
    ):

        peer = HHSNodePeer(

            peer_id=peer_id,

            connected_at=time.time(),

            last_seen=time.time(),

            state=STATE_ACTIVE,

            metadata=metadata or {}
        )

        self.peers[peer_id] = peer

        logger.info(
            f"Peer registered: {peer_id}"
        )

    # ---------------------------------------------------------------------

    def peer_heartbeat(
        self,
        peer_id: str
    ):

        if peer_id not in self.peers:
            return

        self.peers[peer_id].last_seen = (
            time.time()
        )

    # =====================================================================
    # DISTRIBUTED EVENTS
    # =====================================================================

    async def propagate_event(
        self,
        event_type: str,
        payload: Dict
    ):

        event = HHSDistributedEvent(

            event_id=str(uuid.uuid4()),

            created_at=time.time(),

            source_node=self.node_id,

            event_type=event_type,

            payload=payload
        )

        self.event_log.append(event)

        self.total_events_synced += 1

        runtime_state_store.store_event(

            event_type=event_type,

            source=self.node_id,

            payload=payload
        )

        logger.info(
            f"Distributed event propagated: "
            f"{event_type}"
        )

        return event

    # =====================================================================
    # REPLAY SYNC
    # =====================================================================

    async def synchronize_replay(
        self,
        limit: int = 100
    ):

        self.state = STATE_SYNCING

        replay = (
            runtime_replay_engine
            .reconstruct_runtime(
                limit=limit
            )
        )

        runtime_replay_engine.verify_replay_equivalence(
            replay
        )

        self.total_replays_synced += 1

        self.state = STATE_ACTIVE

        logger.info(
            f"Replay synchronized: "
            f"{replay.replay_id}"
        )

        return replay

    # =====================================================================
    # PREDICTION ROUTING
    # =====================================================================

    async def route_prediction(
        self,
        horizon: int = 10
    ):

        prediction = (

            runtime_prediction_engine
            .generate_predictive_replay(
                horizon=horizon
            )
        )

        self.total_prediction_routes += 1

        logger.info(
            "Prediction routed"
        )

        return prediction

    # =====================================================================
    # NODE RECOVERY
    # =====================================================================

    async def recover_node_state(self):

        self.state = STATE_RECOVERING

        snapshot = (
            runtime_state_store
            .latest_snapshot()
        )

        replay = (
            await self.synchronize_replay(
                limit=100
            )
        )

        prediction = (
            await self.route_prediction(
                horizon=5
            )
        )

        self.state = STATE_ACTIVE

        logger.info(
            f"Node recovery complete: "
            f"{self.node_id}"
        )

        return {

            "snapshot":
                snapshot,

            "replay":
                replay,

            "prediction":
                prediction
        }

    # =====================================================================
    # GRAPH SYNC
    # =====================================================================

    async def synchronize_graph_state(self):

        packet = (
            await runtime_orchestrator
            .generate_packet()
        )

        runtime_state_store.store_snapshot(
            packet
        )

        logger.info(
            "Graph state synchronized"
        )

        return packet

    # =====================================================================
    # EVENT HANDLERS
    # =====================================================================

    async def _on_runtime_step(self, event):

        await self.propagate_event(

            event_type=EVENT_RUNTIME_STEP,

            payload=event.payload
        )

    # ---------------------------------------------------------------------

    async def _on_receipt_commit(self, event):

        await self.propagate_event(

            event_type=EVENT_RECEIPT_COMMIT,

            payload=event.payload
        )

    # ---------------------------------------------------------------------

    async def _on_multimodal_packet(self, event):

        await self.propagate_event(

            event_type=EVENT_MULTIMODAL_PACKET,

            payload=event.payload
        )

    # =====================================================================
    # METRICS
    # =====================================================================

    def metrics(self):

        return {

            "node_id":
                self.node_id,

            "state":
                self.state,

            "peers":
                len(self.peers),

            "distributed_events":
                len(self.event_log),

            "events_synced":
                self.total_events_synced,

            "replays_synced":
                self.total_replays_synced,

            "prediction_routes":
                self.total_prediction_routes
        }

# ============================================================================
# GLOBAL NODE
# ============================================================================

distributed_runtime_node = (
    HHSDistributedRuntimeNode()
)

# ============================================================================
# SELF TEST
# ============================================================================

async def distributed_node_self_test():

    await distributed_runtime_node.startup()

    await distributed_runtime_node.propagate_event(

        event_type="runtime.test",

        payload={
            "step": 1,
            "state_hash72": "abc123"
        }
    )

    replay = (
        await distributed_runtime_node
        .synchronize_replay()
    )

    prediction = (
        await distributed_runtime_node
        .route_prediction()
    )

    recovery = (
        await distributed_runtime_node
        .recover_node_state()
    )

    print()

    print("NODE METRICS")

    print(
        distributed_runtime_node.metrics()
    )

    print()

    print("REPLAY")

    print(replay)

    print()

    print("PREDICTION")

    print(prediction)

    print()

    print("RECOVERY")

    print(recovery)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    asyncio.run(
        distributed_node_self_test()
    )
# ============================================================================
# hhs_backend/runtime/runtime_event_bus.py
# HARMONICODE / HHS
# CANONICAL RUNTIME EVENT BUS
#
# PURPOSE
# -------
# Central async event manifold for:
#
#   - runtime execution events
#   - graph ingestion events
#   - websocket streaming events
#   - replay routing
#   - vector prediction routing
#   - multimodal packet propagation
#   - adaptive orchestration
#
# ALL subsystem communication SHOULD route through here.
#
# ============================================================================

from __future__ import annotations

import asyncio
import logging
import time
import uuid

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Callable,
    Awaitable,
    Any,
    Optional
)

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger("HHS_EVENT_BUS")

# ============================================================================
# EVENT
# ============================================================================

@dataclass
class HHSEvent:

    event_id: str

    event_type: str

    created_at: float

    payload: Dict[str, Any]

    source: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# EVENT BUS
# ============================================================================

class HHSRuntimeEventBus:

    """
    Canonical async runtime event manifold.
    """

    def __init__(self):

        self.listeners: Dict[
            str,
            List[Callable]
        ] = {}

        self.event_history: List[
            HHSEvent
        ] = []

        self.event_counts: Dict[
            str,
            int
        ] = {}

        self.total_events = 0

        self.total_dispatches = 0

    # =====================================================================
    # LISTENER REGISTRATION
    # =====================================================================

    def subscribe(
        self,
        event_type: str,
        callback: Callable
    ):

        if event_type not in self.listeners:

            self.listeners[event_type] = []

        self.listeners[event_type].append(
            callback
        )

        logger.info(
            f"Subscribed to event: {event_type}"
        )

    # ---------------------------------------------------------------------

    def unsubscribe(
        self,
        event_type: str,
        callback: Callable
    ):

        if event_type not in self.listeners:
            return

        if callback in self.listeners[event_type]:

            self.listeners[event_type].remove(
                callback
            )

    # =====================================================================
    # EVENT CREATION
    # =====================================================================

    def create_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        source: str,
        metadata: Optional[Dict] = None
    ) -> HHSEvent:

        event = HHSEvent(

            event_id=str(uuid.uuid4()),

            event_type=event_type,

            created_at=time.time(),

            payload=payload,

            source=source,

            metadata=metadata or {}
        )

        self.event_history.append(event)

        self.total_events += 1

        if event_type not in self.event_counts:

            self.event_counts[event_type] = 0

        self.event_counts[event_type] += 1

        return event

    # =====================================================================
    # DISPATCH
    # =====================================================================

    async def dispatch(
        self,
        event_type: str,
        payload: Dict[str, Any],
        source: str = "unknown",
        metadata: Optional[Dict] = None
    ):

        event = self.create_event(

            event_type=event_type,

            payload=payload,

            source=source,

            metadata=metadata
        )

        listeners = self.listeners.get(
            event_type,
            []
        )

        if not listeners:
            return event

        tasks = []

        for listener in listeners:

            try:

                result = listener(event)

                if asyncio.iscoroutine(result):

                    tasks.append(result)

            except Exception as e:

                logger.exception(e)

        if tasks:

            await asyncio.gather(
                *tasks,
                return_exceptions=True
            )

        self.total_dispatches += len(listeners)

        return event

    # =====================================================================
    # SYNC DISPATCH
    # =====================================================================

    def dispatch_sync(
        self,
        event_type: str,
        payload: Dict[str, Any],
        source: str = "unknown",
        metadata: Optional[Dict] = None
    ):

        loop = asyncio.get_event_loop()

        return loop.create_task(

            self.dispatch(

                event_type=event_type,

                payload=payload,

                source=source,

                metadata=metadata
            )
        )

    # =====================================================================
    # HISTORY
    # =====================================================================

    def latest_events(
        self,
        limit: int = 10
    ):

        return self.event_history[-limit:]

    # ---------------------------------------------------------------------

    def events_by_type(
        self,
        event_type: str
    ):

        return [

            event

            for event in self.event_history

            if event.event_type == event_type
        ]

    # =====================================================================
    # METRICS
    # =====================================================================

    def metrics(self):

        return {

            "total_events":
                self.total_events,

            "total_dispatches":
                self.total_dispatches,

            "registered_event_types":
                len(self.listeners),

            "event_counts":
                self.event_counts,
        }

# ============================================================================
# GLOBAL EVENT BUS
# ============================================================================

runtime_event_bus = (
    HHSRuntimeEventBus()
)

# ============================================================================
# CANONICAL EVENT TYPES
# ============================================================================

EVENT_RUNTIME_STEP = "runtime.step"

EVENT_RUNTIME_HALT = "runtime.halt"

EVENT_RUNTIME_CONVERGENCE = (
    "runtime.convergence"
)

EVENT_RECEIPT_COMMIT = (
    "receipt.commit"
)

EVENT_GRAPH_NODE_INGEST = (
    "graph.node.ingest"
)

EVENT_VECTOR_RECORD = (
    "vector.record"
)

EVENT_WEBSOCKET_BROADCAST = (
    "websocket.broadcast"
)

EVENT_MULTIMODAL_PACKET = (
    "multimodal.packet"
)

EVENT_SANDBOX_CREATED = (
    "sandbox.created"
)

EVENT_SANDBOX_DESTROYED = (
    "sandbox.destroyed"
)

# ============================================================================
# SELF TEST
# ============================================================================

async def event_bus_self_test():

    async def runtime_listener(event):

        print()

        print("EVENT RECEIVED")

        print(event.event_type)

        print(event.payload)

    runtime_event_bus.subscribe(

        EVENT_RUNTIME_STEP,

        runtime_listener
    )

    await runtime_event_bus.dispatch(

        EVENT_RUNTIME_STEP,

        payload={
            "step": 1,
            "state_hash72": "abc123"
        },

        source="self_test"
    )

    print()

    print(runtime_event_bus.metrics())

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    asyncio.run(
        event_bus_self_test()
    )
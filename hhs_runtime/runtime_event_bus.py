from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Awaitable
from typing import Callable
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional

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
# Event Subscriber
# =========================================================

EventHandler = Callable[
    [HHSEvent],
    Awaitable[None]
]

# =========================================================
# Event Bus Metrics
# =========================================================

@dataclass(slots=True)
class RuntimeEventBusMetrics:

    emitted_events: int = 0

    dispatched_events: int = 0

    failed_dispatches: int = 0

    active_subscribers: int = 0

    last_emit_ns: int = 0

    per_channel_counts: Dict[
        str,
        int
    ] = field(

        default_factory=dict
    )

# =========================================================
# Runtime Event Bus
# =========================================================

class RuntimeEventBus:

    def __init__(self) -> None:

        self.subscribers: DefaultDict[
            str,
            List[EventHandler]
        ] = defaultdict(list)

        self.history: DefaultDict[
            str,
            List[HHSEvent]
        ] = defaultdict(list)

        self.metrics = (
            RuntimeEventBusMetrics()
        )

        self.sequence_id = 0

        self.max_history = 2048

    # =====================================================
    # Subscription
    # =====================================================

    def subscribe(

        self,

        event_type: str,

        handler: EventHandler

    ) -> None:

        self.subscribers[
            event_type
        ].append(handler)

        self.metrics.active_subscribers = (

            sum(

                len(channel)

                for channel in
                self.subscribers.values()
            )
        )

        print(

            f"[event_bus] subscribe "
            f"{event_type} "
            f"({len(self.subscribers[event_type])})"
        )

    # -----------------------------------------------------

    def unsubscribe(

        self,

        event_type: str,

        handler: EventHandler

    ) -> None:

        if (
            handler
            in self.subscribers[event_type]
        ):

            self.subscribers[
                event_type
            ].remove(handler)

        self.metrics.active_subscribers = (

            sum(

                len(channel)

                for channel in
                self.subscribers.values()
            )
        )

        print(

            f"[event_bus] unsubscribe "
            f"{event_type}"
        )

    # =====================================================
    # Emit
    # =====================================================

    async def emit(
        self,
        event: HHSEvent
    ) -> None:

        self.sequence_id += 1

        event.sequence_id = (
            self.sequence_id
        )

        self.metrics.emitted_events += 1

        self.metrics.last_emit_ns = (
            time.time_ns()
        )

        self.metrics.per_channel_counts[
            event.event_type
        ] = (

            self.metrics
                .per_channel_counts
                .get(
                    event.event_type,
                    0
                ) + 1
        )

        # -------------------------------------------------
        # History
        # -------------------------------------------------

        self.history[
            event.event_type
        ].append(event)

        if (

            len(
                self.history[
                    event.event_type
                ]
            )

            > self.max_history
        ):

            self.history[
                event.event_type
            ] = (

                self.history[
                    event.event_type
                ][
                    -self.max_history:
                ]
            )

        # -------------------------------------------------
        # Dispatch
        # -------------------------------------------------

        subscribers = list(

            self.subscribers.get(

                event.event_type,

                []
            )
        )

        if not subscribers:

            return

        dispatch_tasks = []

        for handler in subscribers:

            dispatch_tasks.append(

                self._dispatch_handler(

                    handler,

                    event
                )
            )

        await asyncio.gather(
            *dispatch_tasks
        )

    # -----------------------------------------------------

    async def _dispatch_handler(

        self,

        handler: EventHandler,

        event: HHSEvent

    ) -> None:

        try:

            await handler(event)

            self.metrics.dispatched_events += 1

        except Exception as exc:

            self.metrics.failed_dispatches += 1

            print(

                "[event_bus] dispatch failure:",

                str(exc)
            )

    # =====================================================
    # History
    # =====================================================

    def get_history(

        self,

        event_type: Optional[str] = None

    ) -> Dict[str, List[HHSEvent]]:

        if event_type is None:

            return dict(self.history)

        return {

            event_type:

                list(

                    self.history.get(

                        event_type,

                        []
                    )
                )
        }

    # -----------------------------------------------------

    def clear_history(
        self
    ) -> None:

        self.history.clear()

    # =====================================================
    # Metrics
    # =====================================================

    def get_metrics(
        self
    ) -> Dict[str, Any]:

        return {

            "emitted_events":
                self.metrics.emitted_events,

            "dispatched_events":
                self.metrics.dispatched_events,

            "failed_dispatches":
                self.metrics.failed_dispatches,

            "active_subscribers":
                self.metrics.active_subscribers,

            "last_emit_ns":
                self.metrics.last_emit_ns,

            "per_channel_counts":
                dict(
                    self.metrics
                        .per_channel_counts
                ),

            "history_depths": {

                key:
                    len(value)

                for key, value
                in self.history.items()
            }
        }

# =========================================================
# Global Runtime Bus
# =========================================================

runtime_event_bus = (
    RuntimeEventBus()
)

# =========================================================
# Channel Helpers
# =========================================================

async def emit_runtime(
    event: HHSEvent
) -> None:

    await runtime_event_bus.emit(
        event
    )

# ---------------------------------------------------------

def subscribe_runtime(
    handler: EventHandler
) -> None:

    runtime_event_bus.subscribe(

        EVENT_RUNTIME,

        handler
    )

# ---------------------------------------------------------

def subscribe_replay(
    handler: EventHandler
) -> None:

    runtime_event_bus.subscribe(

        EVENT_REPLAY,

        handler
    )

# ---------------------------------------------------------

def subscribe_graph(
    handler: EventHandler
) -> None:

    runtime_event_bus.subscribe(

        EVENT_GRAPH,

        handler
    )

# ---------------------------------------------------------

def subscribe_transport(
    handler: EventHandler
) -> None:

    runtime_event_bus.subscribe(

        EVENT_TRANSPORT,

        handler
    )

# ---------------------------------------------------------

def subscribe_receipt(
    handler: EventHandler
) -> None:

    runtime_event_bus.subscribe(

        EVENT_RECEIPT,

        handler
    )

# ---------------------------------------------------------

def subscribe_certification(
    handler: EventHandler
) -> None:

    runtime_event_bus.subscribe(

        EVENT_CERTIFICATION,

        handler
    )

# =========================================================
# Runtime Debug Sink
# =========================================================

async def runtime_debug_sink(
    event: HHSEvent
) -> None:

    print(

        f"[event_bus] "
        f"{event.event_type} "
        f"seq={event.sequence_id}"
    )

# =========================================================
# Development Bootstrap
# =========================================================

def attach_debug_sinks() -> None:

    runtime_event_bus.subscribe(

        EVENT_RUNTIME,

        runtime_debug_sink
    )

    runtime_event_bus.subscribe(

        EVENT_REPLAY,

        runtime_debug_sink
    )

    runtime_event_bus.subscribe(

        EVENT_GRAPH,

        runtime_debug_sink
    )

    runtime_event_bus.subscribe(

        EVENT_TRANSPORT,

        runtime_debug_sink
    )

    runtime_event_bus.subscribe(

        EVENT_RECEIPT,

        runtime_debug_sink
    )

    runtime_event_bus.subscribe(

        EVENT_CERTIFICATION,

        runtime_debug_sink
    )
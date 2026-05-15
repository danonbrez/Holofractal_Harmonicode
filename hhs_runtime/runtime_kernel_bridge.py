from __future__ import annotations

import asyncio
import math
import random
import time

from typing import Any
from typing import Dict
from typing import Optional

from hhs_runtime.runtime_event_bus import (
    runtime_event_bus
)

from hhs_runtime.runtime_event_schema import (

    RuntimeEvent,
    RuntimeEventPayload,

    ReplayEvent,
    ReplayEventPayload,

    GraphEvent,
    GraphEventPayload,

    GraphNode,
    GraphEdge,

    TransportEvent,
    TransportEventPayload,

    ReceiptEvent,
    ReceiptEventPayload
)

# =========================================================
# Runtime Kernel Bridge
# =========================================================

class RuntimeKernelBridge:
    """
    ========================================================
    Runtime Kernel Bridge
    ========================================================

    Bridges:

        VM runtime
        execution layer
        receipt lineage
        replay topology
        transport state

    into:

        runtime_event_bus
        websocket diffusion
        frontend topology
        replay timeline
        runtime viewport

    IMPORTANT:
    --------------------------------------------------------
    Current implementation is transport-authoritative
    synthetic execution.

    Replace synthetic execution loop with:

        VM81 hooks
        runtime receipts
        real tensor transport
        actual opcode streams

    once VM runtime bridge stabilizes.
    """

    def __init__(self) -> None:

        self.running = False

        self.sequence_id = 0

        self.runtime_step = 0

        self.replay_tick = 0

        self.transport_tick = 0

        self.graph_tick = 0

        self.started_ns = (
            time.time_ns()
        )

        self.task: Optional[
            asyncio.Task
        ] = None

    # =====================================================
    # Lifecycle
    # =====================================================

    async def start(self) -> None:

        if self.running:

            return

        self.running = True

        self.task = asyncio.create_task(
            self._runtime_loop()
        )

        print(
            "[runtime_kernel_bridge] started"
        )

    # -----------------------------------------------------

    async def stop(self) -> None:

        self.running = False

        if self.task:

            self.task.cancel()

        print(
            "[runtime_kernel_bridge] stopped"
        )

    # =====================================================
    # Runtime Loop
    # =====================================================

    async def _runtime_loop(
        self
    ) -> None:

        try:

            while self.running:

                await self._emit_runtime()

                await self._emit_replay()

                await self._emit_transport()

                await self._emit_graph()

                await self._emit_receipt()

                await asyncio.sleep(
                    0.25
                )

        except asyncio.CancelledError:

            return

    # =====================================================
    # Runtime
    # =====================================================

    async def _emit_runtime(
        self
    ) -> None:

        self.runtime_step += 1

        self.sequence_id += 1

        event = RuntimeEvent.build(

            RuntimeEventPayload(

                operation=
                    "runtime_tick",

                runtime_status=
                    "online",

                step=
                    self.runtime_step,

                phase=
                    self._phase(),

                uptime=
                    self.uptime_seconds(),

                receipt_hash72=
                    self._hash72(),

                source_hash72=
                    self._hash72(),

                closure_state=
                    "stable",

                transport_flux=
                    self._transport_flux(),

                orientation_flux=
                    self._orientation_flux(),

                constraint_flux=
                    self._constraint_flux(),

                entropy_delta=
                    0.0
            ),

            sequence_id=
                self.sequence_id
        )

        await runtime_event_bus.emit(
            event
        )

    # =====================================================
    # Replay
    # =====================================================

    async def _emit_replay(
        self
    ) -> None:

        self.replay_tick += 1

        self.sequence_id += 1

        event = ReplayEvent.build(

            ReplayEventPayload(

                replay_tick=
                    self.replay_tick,

                replay_status=
                    "stable",

                timeline_position=
                    self.runtime_step,

                branch_id=
                    "main",

                replay_mode=
                    "live",

                replay_hash72=
                    self._hash72()
            ),

            sequence_id=
                self.sequence_id
        )

        await runtime_event_bus.emit(
            event
        )

    # =====================================================
    # Transport
    # =====================================================

    async def _emit_transport(
        self
    ) -> None:

        self.transport_tick += 1

        self.sequence_id += 1

        event = TransportEvent.build(

            TransportEventPayload(

                transport_tick=
                    self.transport_tick,

                transport_flux=
                    self._transport_flux(),

                continuity=
                    "stable",

                throughput=
                    72.0,

                orientation_phase=
                    self._orientation_flux(),

                closure_pressure=
                    self._constraint_flux()
            ),

            sequence_id=
                self.sequence_id
        )

        await runtime_event_bus.emit(
            event
        )

    # =====================================================
    # Graph
    # =====================================================

    async def _emit_graph(
        self
    ) -> None:

        self.graph_tick += 1

        self.sequence_id += 1

        nodes = []
        edges = []

        for i in range(9):

            theta = (

                (
                    i / 9
                )

                * math.pi
                * 2

                +

                (
                    self.runtime_step
                    * 0.03
                )
            )

            nodes.append(

                GraphNode(

                    node_id=
                        str(i + 1),

                    node_type=
                        "runtime",

                    x=
                        math.cos(theta)
                        * 4,

                    y=
                        math.sin(theta)
                        * 4,

                    z=
                        math.sin(theta)
                        * 0.5,

                    authority=
                        "runtime"
                )
            )

        for i in range(8):

            edges.append(

                GraphEdge(

                    source=
                        str(i + 1),

                    target=
                        str(i + 2),

                    edge_type=
                        "transport"
                )
            )

        event = GraphEvent.build(

            GraphEventPayload(

                graph_tick=
                    self.graph_tick,

                projection=
                    "runtime_transport",

                nodes=
                    nodes,

                edges=
                    edges
            ),

            sequence_id=
                self.sequence_id
        )

        await runtime_event_bus.emit(
            event
        )

    # =====================================================
    # Receipt
    # =====================================================

    async def _emit_receipt(
        self
    ) -> None:

        self.sequence_id += 1

        event = ReceiptEvent.build(

            ReceiptEventPayload(

                receipt_hash72=
                    self._hash72(),

                source_hash72=
                    self._hash72(),

                operation=
                    "runtime_tick",

                closure_class=
                    "stable",

                witness_flags=
                    0,

                converged=
                    True,

                halted=
                    False
            ),

            sequence_id=
                self.sequence_id
        )

        await runtime_event_bus.emit(
            event
        )

    # =====================================================
    # Helpers
    # =====================================================

    def uptime_seconds(
        self
    ) -> float:

        return (

            time.time_ns()
            - self.started_ns

        ) / 1e9

    # -----------------------------------------------------

    def _phase(
        self
    ) -> str:

        phases = [

            "bootstrap",

            "transport",

            "constraint",

            "projection",

            "closure"
        ]

        return phases[
            self.runtime_step
            % len(phases)
        ]

    # -----------------------------------------------------

    def _transport_flux(
        self
    ) -> float:

        return round(

            0.5

            +

            (
                math.sin(
                    self.runtime_step
                    * 0.08
                )

                * 0.5
            ),

            6
        )

    # -----------------------------------------------------

    def _orientation_flux(
        self
    ) -> float:

        return round(

            0.5

            +

            (
                math.cos(
                    self.runtime_step
                    * 0.05
                )

                * 0.5
            ),

            6
        )

    # -----------------------------------------------------

    def _constraint_flux(
        self
    ) -> float:

        return round(

            abs(

                math.sin(
                    self.runtime_step
                    * 0.03
                )
            ),

            6
        )

    # -----------------------------------------------------

    def _hash72(
        self
    ) -> str:

        alphabet = (

            "0123456789"

            "abcdefghijklmnopqrstuvwxyz"

            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

            "-+*/()<>!?"
        )

        return "".join(

            random.choice(alphabet)

            for _ in range(72)
        )

# =========================================================
# Global Bridge
# =========================================================

runtime_kernel_bridge = (
    RuntimeKernelBridge()
)
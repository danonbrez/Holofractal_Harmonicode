# ============================================================================
# hhs_backend/runtime/runtime_orchestrator.py
# HARMONICODE / HHS
# CANONICAL RUNTIME ORCHESTRATOR
#
# PURPOSE
# -------
# High-level deterministic orchestration authority for:
#
#   - runtime execution coordination
#   - event manifold routing
#   - graph ingestion
#   - websocket propagation
#   - replay routing
#   - multimodal packet propagation
#   - certification integration
#   - adaptive orchestration
#
# ALL subsystem coordination SHOULD route through here.
#
# ============================================================================

from __future__ import annotations

import asyncio
import logging
import time
import uuid

from typing import Dict, Any, Optional

from hhs_python.runtime.hhs_runtime_controller import (
    HHSRuntimeController
)

from hhs_graph.hhs_multimodal_receipt_graph_v1 import (
    HHSMultimodalReceiptGraph
)

from hhs_backend.websocket.runtime_stream_manager import (
    runtime_stream_manager
)

from hhs_backend.runtime.runtime_event_bus import (

    runtime_event_bus,

    EVENT_RUNTIME_STEP,

    EVENT_RUNTIME_HALT,

    EVENT_RUNTIME_CONVERGENCE,

    EVENT_RECEIPT_COMMIT,

    EVENT_GRAPH_NODE_INGEST,

    EVENT_MULTIMODAL_PACKET,

    EVENT_WEBSOCKET_BROADCAST
)

from hhs_runtime.runtime_lock_certifier_v1 import (
    HHSRuntimeLockCertifier
)

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger("HHS_ORCHESTRATOR")

# ============================================================================
# ORCHESTRATOR
# ============================================================================

class HHSRuntimeOrchestrator:

    """
    Canonical high-level runtime orchestration authority.
    """

    def __init__(self):

        self.runtime_controller = (
            HHSRuntimeController()
        )

        self.graph = (
            HHSMultimodalReceiptGraph()
        )

        self.certifier = (
            HHSRuntimeLockCertifier()
        )

        self.started = False

        self.boot_id = str(uuid.uuid4())

        self.started_at = None

        self.total_runtime_steps = 0

        self.total_packets = 0

        self.last_packet = None

        self._register_event_routes()

    # =====================================================================
    # EVENT REGISTRATION
    # =====================================================================

    def _register_event_routes(self):

        runtime_event_bus.subscribe(

            EVENT_RUNTIME_STEP,

            self._on_runtime_step
        )

        runtime_event_bus.subscribe(

            EVENT_RUNTIME_HALT,

            self._on_runtime_halt
        )

        runtime_event_bus.subscribe(

            EVENT_RUNTIME_CONVERGENCE,

            self._on_runtime_convergence
        )

        runtime_event_bus.subscribe(

            EVENT_RECEIPT_COMMIT,

            self._on_receipt_commit
        )

    # =====================================================================
    # STARTUP
    # =====================================================================

    async def startup(self):

        if self.started:
            return

        logger.info(
            "Starting runtime orchestrator..."
        )

        self.started = True

        self.started_at = time.time()

        logger.info(
            "Runtime orchestrator started"
        )

    # ---------------------------------------------------------------------

    async def shutdown(self):

        logger.info(
            "Shutting down runtime orchestrator..."
        )

        self.runtime_controller.halt()

        self.started = False

    # =====================================================================
    # EXECUTION
    # =====================================================================

    async def step_runtime(
        self,
        count: int = 1
    ):

        results = []

        for _ in range(count):

            result = (
                self.runtime_controller.step()
            )

            results.append(result)

            self.total_runtime_steps += 1

            await runtime_event_bus.dispatch(

                EVENT_RUNTIME_STEP,

                payload=result,

                source="runtime_orchestrator"
            )

            if result["converged"]:

                await runtime_event_bus.dispatch(

                    EVENT_RUNTIME_CONVERGENCE,

                    payload=result,

                    source="runtime_orchestrator"
                )

            if result["halted"]:

                await runtime_event_bus.dispatch(

                    EVENT_RUNTIME_HALT,

                    payload=result,

                    source="runtime_orchestrator"
                )

        return results

    # =====================================================================
    # RECEIPTS
    # =====================================================================

    async def commit_receipt(self):

        receipt = (
            self.runtime_controller.commit_receipt()
        )

        await runtime_event_bus.dispatch(

            EVENT_RECEIPT_COMMIT,

            payload=receipt,

            source="runtime_orchestrator"
        )

        return receipt

    # =====================================================================
    # MULTIMODAL PACKETS
    # =====================================================================

    async def generate_packet(self):

        packet = (
            self.runtime_controller
            .export_multimodal_packet()
        )

        self.last_packet = packet

        self.total_packets += 1

        await runtime_event_bus.dispatch(

            EVENT_MULTIMODAL_PACKET,

            payload=packet,

            source="runtime_orchestrator"
        )

        return packet

    # =====================================================================
    # GRAPH INGESTION
    # =====================================================================

    async def ingest_graph_packet(
        self,
        packet: Dict
    ):

        node = self.graph.ingest_runtime_state(
            packet
        )

        await runtime_event_bus.dispatch(

            EVENT_GRAPH_NODE_INGEST,

            payload={
                "node_id":
                    node.node_id,

                "step":
                    node.step,

                "state_hash72":
                    node.state_hash72
            },

            source="runtime_orchestrator"
        )

        return node

    # =====================================================================
    # BROADCAST
    # =====================================================================

    async def broadcast_packet(
        self,
        packet: Dict
    ):

        await runtime_stream_manager.broadcast(
            packet
        )

        await runtime_event_bus.dispatch(

            EVENT_WEBSOCKET_BROADCAST,

            payload={
                "packet_type":
                    "multimodal",

                "timestamp":
                    time.time()
            },

            source="runtime_orchestrator"
        )

    # =====================================================================
    # FULL EXECUTION CYCLE
    # =====================================================================

    async def execute_cycle(
        self,
        steps: int = 1
    ):

        await self.step_runtime(
            count=steps
        )

        packet = await self.generate_packet()

        node = await self.ingest_graph_packet(
            packet
        )

        await self.broadcast_packet(packet)

        return {

            "runtime":
                self.runtime_controller
                .latest_runtime_state(),

            "graph_node":
                node,

            "graph_summary":
                self.graph.export_graph_summary(),

            "stream_metrics":
                runtime_stream_manager.metrics(),

            "event_metrics":
                runtime_event_bus.metrics()
        }

    # =====================================================================
    # CERTIFICATION
    # =====================================================================

    async def certify_runtime(self):

        report = self.certifier.certify()

        return {

            "locked":
                report.locked,

            "totals":
                report.totals,

            "runtime_mode":
                report.runtime_mode
        }

    # =====================================================================
    # EVENT HANDLERS
    # =====================================================================

    async def _on_runtime_step(self, event):

        logger.info(
            f"Runtime step event: "
            f"{event.payload.get('step')}"
        )

    # ---------------------------------------------------------------------

    async def _on_runtime_halt(self, event):

        logger.warning(
            "Runtime halt detected"
        )

    # ---------------------------------------------------------------------

    async def _on_runtime_convergence(self, event):

        logger.info(
            "Runtime convergence detected"
        )

    # ---------------------------------------------------------------------

    async def _on_receipt_commit(self, event):

        logger.info(
            "Receipt committed"
        )

    # =====================================================================
    # STATUS
    # =====================================================================

    def status(self):

        uptime = 0.0

        if self.started_at is not None:

            uptime = (
                time.time()
                - self.started_at
            )

        return {

            "boot_id":
                self.boot_id,

            "started":
                self.started,

            "uptime":
                uptime,

            "total_runtime_steps":
                self.total_runtime_steps,

            "total_packets":
                self.total_packets,

            "graph_summary":
                self.graph.export_graph_summary(),

            "stream_metrics":
                runtime_stream_manager.metrics(),

            "event_metrics":
                runtime_event_bus.metrics()
        }

# ============================================================================
# GLOBAL ORCHESTRATOR
# ============================================================================

runtime_orchestrator = (
    HHSRuntimeOrchestrator()
)

# ============================================================================
# SELF TEST
# ============================================================================

async def orchestrator_self_test():

    await runtime_orchestrator.startup()

    result = (
        await runtime_orchestrator.execute_cycle(
            steps=5
        )
    )

    print()

    print("ORCHESTRATOR STATUS")

    print(runtime_orchestrator.status())

    print()

    print("EXECUTION RESULT")

    print(result)

    cert = await runtime_orchestrator.certify_runtime()

    print()

    print("CERTIFICATION")

    print(cert)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    asyncio.run(
        orchestrator_self_test()
    )
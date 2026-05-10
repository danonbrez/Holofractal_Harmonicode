# ============================================================================
# hhs_python/runtime/hhs_runtime_controller.py
# HARMONICODE / HHS
# CANONICAL RUNTIME CONTROLLER
#
# PURPOSE
# -------
# Authoritative runtime execution controller for:
#
#   - deterministic VM execution
#   - receipt-chain ownership
#   - graph ingestion
#   - replay execution
#   - websocket streaming
#   - sandbox execution
#   - multimodal orchestration
#
# ALL runtime execution MUST flow through this controller.
#
# ============================================================================

from __future__ import annotations

import time
import uuid
import threading

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any

from hhs_python.runtime.hhs_ctypes_bridge import (
    HHSRuntimeBridge
)

# ============================================================================
# RUNTIME EVENTS
# ============================================================================

EVENT_RUNTIME_STEP = "runtime_step"

EVENT_RUNTIME_HALT = "runtime_halt"

EVENT_RECEIPT_COMMIT = "receipt_commit"

EVENT_CONVERGENCE = "runtime_convergence"

EVENT_ORBIT = "runtime_orbit"

# ============================================================================
# SANDBOX
# ============================================================================

@dataclass
class HHSSandbox:

    sandbox_id: str

    created_at: float

    runtime: HHSRuntimeBridge

    active: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================================
# RUNTIME CONTROLLER
# ============================================================================

class HHSRuntimeController:

    """
    Canonical runtime execution authority.
    """

    def __init__(self):

        self.runtime = HHSRuntimeBridge()

        self.runtime_lock = threading.RLock()

        self.listeners: Dict[
            str,
            List[Callable]
        ] = {}

        self.sandboxes: Dict[
            str,
            HHSSandbox
        ] = {}

        self.execution_history = []

        self.replay_cache = []

    # =====================================================================
    # EVENT SYSTEM
    # =====================================================================

    def add_listener(
        self,
        event_name: str,
        callback: Callable
    ):

        if event_name not in self.listeners:
            self.listeners[event_name] = []

        self.listeners[event_name].append(callback)

    # ---------------------------------------------------------------------

    def emit_event(
        self,
        event_name: str,
        payload: Dict
    ):

        listeners = self.listeners.get(
            event_name,
            []
        )

        for callback in listeners:

            try:
                callback(payload)

            except Exception as e:

                print(
                    f"[HHS EVENT ERROR] {event_name}: {e}"
                )

    # =====================================================================
    # EXECUTION
    # =====================================================================

    def step(self):

        with self.runtime_lock:

            previous_step = self.runtime.step

            self.runtime.runtime_step()

            runtime_state = (
                self.runtime.export_runtime_dict()
            )

            self.execution_history.append(runtime_state)

            self.emit_event(
                EVENT_RUNTIME_STEP,
                runtime_state
            )

            if runtime_state["converged"]:

                self.emit_event(
                    EVENT_CONVERGENCE,
                    runtime_state
                )

            if runtime_state["halted"]:

                self.emit_event(
                    EVENT_RUNTIME_HALT,
                    runtime_state
                )

            return runtime_state

    # ---------------------------------------------------------------------

    def run_steps(
        self,
        count: int
    ):

        results = []

        for _ in range(count):

            if self.runtime.halted:
                break

            result = self.step()

            results.append(result)

        return results

    # ---------------------------------------------------------------------

    def halt(self):

        with self.runtime_lock:

            self.runtime.runtime_halt()

            runtime_state = (
                self.runtime.export_runtime_dict()
            )

            self.emit_event(
                EVENT_RUNTIME_HALT,
                runtime_state
            )

            return runtime_state

    # =====================================================================
    # RECEIPTS
    # =====================================================================

    def commit_receipt(self):

        with self.runtime_lock:

            self.runtime.receipt_commit()

            receipt_data = {

                "step":
                    self.runtime.step,

                "state_hash72":
                    self.runtime.state_hash72,

                "receipt_hash72":
                    self.runtime.receipt_hash72,
            }

            self.replay_cache.append(receipt_data)

            self.emit_event(
                EVENT_RECEIPT_COMMIT,
                receipt_data
            )

            return receipt_data

    # =====================================================================
    # SANDBOXES
    # =====================================================================

    def create_sandbox(
        self,
        metadata: Optional[Dict] = None
    ) -> HHSSandbox:

        sandbox_id = str(uuid.uuid4())

        sandbox = HHSSandbox(

            sandbox_id=sandbox_id,

            created_at=time.time(),

            runtime=HHSRuntimeBridge(),

            metadata=metadata or {}
        )

        self.sandboxes[sandbox_id] = sandbox

        return sandbox

    # ---------------------------------------------------------------------

    def destroy_sandbox(
        self,
        sandbox_id: str
    ):

        if sandbox_id in self.sandboxes:

            self.sandboxes[sandbox_id].active = False

            del self.sandboxes[sandbox_id]

    # ---------------------------------------------------------------------

    def sandbox_step(
        self,
        sandbox_id: str
    ):

        sandbox = self.sandboxes[sandbox_id]

        sandbox.runtime.runtime_step()

        return sandbox.runtime.export_runtime_dict()

    # =====================================================================
    # REPLAY
    # =====================================================================

    def replay_from_index(
        self,
        start_index: int
    ):

        if start_index < 0:
            start_index = 0

        return self.execution_history[start_index:]

    # ---------------------------------------------------------------------

    def latest_runtime_state(self):

        return self.runtime.export_runtime_dict()

    # =====================================================================
    # GRAPH INGESTION
    # =====================================================================

    def export_graph_node(self):

        runtime_state = (
            self.runtime.export_runtime_dict()
        )

        return {

            "node_type":
                "runtime_state",

            "step":
                runtime_state["step"],

            "state_hash72":
                runtime_state["state_hash72"],

            "receipt_hash72":
                runtime_state["receipt_hash72"],

            "transport_flux":
                runtime_state["transport_flux"],

            "orientation_flux":
                runtime_state["orientation_flux"],

            "constraint_flux":
                runtime_state["constraint_flux"],

            "converged":
                runtime_state["converged"],

            "halted":
                runtime_state["halted"],
        }

    # =====================================================================
    # VECTOR CACHE
    # =====================================================================

    def export_vector_record(self):

        runtime_state = (
            self.runtime.export_runtime_dict()
        )

        hash72 = runtime_state["state_hash72"]

        vector = []

        for ch in hash72:

            vector.append(
                ord(ch) / 255.0
            )

        return {

            "hash72":
                hash72,

            "vector":
                vector,

            "step":
                runtime_state["step"]
        }

    # =====================================================================
    # MULTIMODAL ENVELOPE
    # =====================================================================

    def export_multimodal_packet(self):

        runtime_state = (
            self.runtime.export_runtime_dict()
        )

        return {

            "runtime":
                runtime_state,

            "graph_node":
                self.export_graph_node(),

            "vector_record":
                self.export_vector_record(),
        }

# ============================================================================
# SELF TEST
# ============================================================================

def controller_self_test():

    controller = HHSRuntimeController()

    controller.run_steps(5)

    controller.commit_receipt()

    print()

    print("RUNTIME STATE")

    print(controller.latest_runtime_state())

    print()

    print("GRAPH NODE")

    print(controller.export_graph_node())

    print()

    print("VECTOR RECORD")

    print(controller.export_vector_record())

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    controller_self_test()
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
from hhs_runtime.hhs_authority_gate_v1 import assert_runtime_authorized
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload

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
    """Canonical runtime execution authority.

    Production state transitions are receipt-atomic.  Public ``step`` delegates
    to ``authorized_tick``; the unreceipted transition primitive is private.
    Public ``commit_receipt`` is retained only as a compatibility/read surface
    for the most recent already-authorized receipt and cannot create a detached
    receipt or mutate runtime state.
    """

    def __init__(self):
        self.runtime = HHSRuntimeBridge()
        self.runtime_lock = threading.RLock()
        self.listeners: Dict[str, List[Callable]] = {}
        self.sandboxes: Dict[str, HHSSandbox] = {}
        self.execution_history = []
        self.replay_cache = []
        self.authority_audit_cache = []

    # =====================================================================
    # EVENT SYSTEM
    # =====================================================================

    def add_listener(self, event_name: str, callback: Callable):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)

    def emit_event(self, event_name: str, payload: Dict):
        listeners = self.listeners.get(event_name, [])
        for callback in listeners:
            try:
                callback(payload)
            except Exception as e:
                print(f"[HHS EVENT ERROR] {event_name}: {e}")

    # =====================================================================
    # EXECUTION
    # =====================================================================

    def _step_uncommitted(self):
        """Private transition primitive used only inside the receipt-atomic tick."""
        self.runtime.runtime_step()
        runtime_state = self.runtime.export_runtime_dict()
        self.execution_history.append(runtime_state)
        self.emit_event(EVENT_RUNTIME_STEP, runtime_state)
        if runtime_state["converged"]:
            self.emit_event(EVENT_CONVERGENCE, runtime_state)
        if runtime_state["halted"]:
            self.emit_event(EVENT_RUNTIME_HALT, runtime_state)
        return runtime_state

    def step(self):
        """Advance exactly one production step with an inseparable receipt commit."""
        return self.authorized_tick(
            source="HHSRuntimeController.step"
        )["runtime"]

    def run_steps(self, count: int):
        results = []
        for _ in range(count):
            if self.runtime.halted:
                break
            results.append(self.step())
        return results

    def halt(self):
        with self.runtime_lock:
            self.runtime.runtime_halt()
            runtime_state = self.runtime.export_runtime_dict()
            self.emit_event(EVENT_RUNTIME_HALT, runtime_state)
            return runtime_state

    # =====================================================================
    # RECEIPTS
    # =====================================================================

    def _commit_receipt_unlocked(self, source: str):
        """Mutating receipt primitive; caller must hold ``runtime_lock``."""
        self.runtime.receipt_commit()
        receipt_data = {
            "step": self.runtime.step,
            "state_hash72": self.runtime.state_hash72,
            "receipt_hash72": self.runtime.receipt_hash72,
        }
        runtime_state = self.runtime.export_runtime_dict()
        authority_audit = assert_runtime_authorized(
            runtime_state,
            source=source,
            receipt=receipt_data,
            require_receipt=True,
        ).to_dict()
        receipt_data["authority_audit"] = authority_audit

        unified_ledger = append_payload(
            "RUNTIME_RECEIPT",
            source,
            receipt_data,
        )
        receipt_data["unified_ledger"] = {
            "entry_count": unified_ledger.get("entry_count"),
            "tip_hash72": unified_ledger.get("tip_hash72"),
            "ledger_hash72": unified_ledger.get("ledger_hash72"),
        }
        self.replay_cache.append(receipt_data)
        self.authority_audit_cache.append(authority_audit)
        self.emit_event(EVENT_RECEIPT_COMMIT, receipt_data)
        return receipt_data

    def commit_receipt(self):
        """Return already-authorized receipt lineage without mutating runtime state.

        This compatibility method deliberately does *not* call
        ``runtime.receipt_commit``.  If the current state has no matching
        authorized receipt it returns a fail-closed observation instead of
        manufacturing a detached receipt.
        """
        with self.runtime_lock:
            runtime_state = self.runtime.export_runtime_dict()
            if self.replay_cache:
                latest = self.replay_cache[-1]
                if (
                    latest.get("step") == runtime_state.get("step")
                    and latest.get("state_hash72") == runtime_state.get("state_hash72")
                    and latest.get("receipt_hash72") == runtime_state.get("receipt_hash72")
                ):
                    observed = dict(latest)
                    observed["compatibility_observation_only"] = True
                    observed["detached_receipt_commit_allowed"] = False
                    return observed

            return {
                "step": runtime_state.get("step"),
                "state_hash72": runtime_state.get("state_hash72", ""),
                "receipt_hash72": runtime_state.get("receipt_hash72", ""),
                "compatibility_observation_only": True,
                "detached_receipt_commit_allowed": False,
                "authorized_receipt_available": False,
                "reason": "DETACHED_RECEIPT_COMMIT_FORBIDDEN",
            }

    def authorized_tick(self, source: str = "HHSRuntimeController.authorized_tick"):
        """Advance one runtime step and atomically seal its receipt lineage."""
        with self.runtime_lock:
            runtime_state = self._step_uncommitted()
            receipt_data = self._commit_receipt_unlocked(
                source=f"{source}.receipt"
            )
            authority_audit = assert_runtime_authorized(
                runtime_state,
                source=source,
                receipt=receipt_data,
                require_receipt=True,
            ).to_dict()
            return {
                "runtime": runtime_state,
                "receipt": receipt_data,
                "authority_audit": authority_audit,
            }

    # =====================================================================
    # SANDBOXES
    # =====================================================================

    def create_sandbox(self, metadata: Optional[Dict] = None) -> HHSSandbox:
        sandbox_id = str(uuid.uuid4())
        sandbox = HHSSandbox(
            sandbox_id=sandbox_id,
            created_at=time.time(),
            runtime=HHSRuntimeBridge(),
            metadata=metadata or {},
        )
        self.sandboxes[sandbox_id] = sandbox
        return sandbox

    def destroy_sandbox(self, sandbox_id: str):
        if sandbox_id in self.sandboxes:
            self.sandboxes[sandbox_id].active = False
            del self.sandboxes[sandbox_id]

    def sandbox_step(self, sandbox_id: str):
        sandbox = self.sandboxes[sandbox_id]
        sandbox.runtime.runtime_step()
        sandbox.runtime.receipt_commit()

        runtime_state = sandbox.runtime.export_runtime_dict()
        receipt_data = {
            "step": sandbox.runtime.step,
            "state_hash72": sandbox.runtime.state_hash72,
            "receipt_hash72": sandbox.runtime.receipt_hash72,
        }

        authority_audit = assert_runtime_authorized(
            runtime_state,
            source="HHSRuntimeController.sandbox_step",
            receipt=receipt_data,
            require_receipt=True,
        ).to_dict()

        runtime_state["authority_audit"] = authority_audit
        runtime_state["receipt"] = receipt_data
        return runtime_state

    # =====================================================================
    # REPLAY
    # =====================================================================

    def replay_from_index(self, start_index: int):
        if start_index < 0:
            start_index = 0
        return self.execution_history[start_index:]

    def latest_runtime_state(self):
        return self.runtime.export_runtime_dict()

    # =====================================================================
    # GRAPH INGESTION
    # =====================================================================

    def export_graph_node(self):
        runtime_state = self.runtime.export_runtime_dict()
        return {
            "node_type": "runtime_state",
            "step": runtime_state["step"],
            "state_hash72": runtime_state["state_hash72"],
            "receipt_hash72": runtime_state["receipt_hash72"],
            "transport_flux": runtime_state["transport_flux"],
            "orientation_flux": runtime_state["orientation_flux"],
            "constraint_flux": runtime_state["constraint_flux"],
            "converged": runtime_state["converged"],
            "halted": runtime_state["halted"],
        }

    # =====================================================================
    # VECTOR CACHE
    # =====================================================================

    def export_vector_record(self):
        runtime_state = self.runtime.export_runtime_dict()
        hash72 = runtime_state["state_hash72"]
        vector = [ord(ch) / 255.0 for ch in hash72]
        return {
            "hash72": hash72,
            "vector": vector,
            "step": runtime_state["step"],
        }

    # =====================================================================
    # MULTIMODAL ENVELOPE
    # =====================================================================

    def export_multimodal_packet(self):
        runtime_state = self.runtime.export_runtime_dict()
        return {
            "runtime": runtime_state,
            "graph_node": self.export_graph_node(),
            "vector_record": self.export_vector_record(),
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

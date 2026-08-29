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

import os
import time
import uuid
import threading

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any

from hhs_python.runtime.hhs_ctypes_bridge import (
    HHSRuntimeBridge,
    HHSRuntimeLibraryUnavailable,
    runtime_library_status,
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

    """
    Canonical runtime execution authority.
    """

    def __init__(self):

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

        self.authority_audit_cache = []

        self.runtime: HHSRuntimeBridge | None = None
        self.runtime_unavailable_detail: str | None = None

        try:
            self.runtime = HHSRuntimeBridge()
        except HHSRuntimeLibraryUnavailable as exc:
            allow_degraded = (
                os.environ.get("HHS_ALLOW_C_RUNTIME_DEGRADED_IMPORT", "").lower()
                in {"1", "true", "yes", "on"}
            )
            if not allow_degraded:
                raise
            self.runtime_unavailable_detail = str(exc)

    @property
    def runtime_available(self) -> bool:
        return self.runtime is not None

    def require_runtime(self) -> HHSRuntimeBridge:
        runtime = self.runtime
        if runtime is None:
            detail = self.runtime_unavailable_detail or str(runtime_library_status().get("error") or "unknown")
            raise HHSRuntimeLibraryUnavailable(
                "HHS canonical runtime controller is unavailable because the C ABI "
                f"library is not active: {detail}"
            )
        return runtime

    def availability_status(self) -> Dict[str, Any]:
        status = dict(runtime_library_status())
        status.update({
            "schema": "HHS_RUNTIME_CONTROLLER_AVAILABILITY_V1",
            "controller_available": self.runtime_available,
            "canonical_runtime_authority_active": self.runtime_available,
            "source_only_degraded_mode": not self.runtime_available,
            "python_replacement_authority": False,
        })
        return status

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

            runtime = self.require_runtime()
            previous_step = runtime.step

            runtime.runtime_step()

            runtime_state = (
                runtime.export_runtime_dict()
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

        runtime = self.require_runtime()

        for _ in range(count):

            if runtime.halted:
                break

            result = self.step()

            results.append(result)

        return results

    # ---------------------------------------------------------------------

    def halt(self):

        with self.runtime_lock:

            runtime = self.require_runtime()
            runtime.runtime_halt()

            runtime_state = (
                runtime.export_runtime_dict()
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

            runtime = self.require_runtime()
            runtime.receipt_commit()

            receipt_data = {

                "step":
                    runtime.step,

                "state_hash72":
                    runtime.state_hash72,

                "receipt_hash72":
                    runtime.receipt_hash72,
            }

            runtime_state = (
                runtime.export_runtime_dict()
            )

            authority_audit = assert_runtime_authorized(
                runtime_state,
                source="HHSRuntimeController.commit_receipt",
                receipt=receipt_data,
                require_receipt=True,
            ).to_dict()

            receipt_data["authority_audit"] = authority_audit

            unified_ledger = append_payload(
                "RUNTIME_RECEIPT",
                "HHSRuntimeController.commit_receipt",
                receipt_data,
            )
            receipt_data["unified_ledger"] = {
                "entry_count": unified_ledger.get("entry_count"),
                "tip_hash72": unified_ledger.get("tip_hash72"),
                "ledger_hash72": unified_ledger.get("ledger_hash72"),
            }

            self.replay_cache.append(receipt_data)
            self.authority_audit_cache.append(authority_audit)

            self.emit_event(
                EVENT_RECEIPT_COMMIT,
                receipt_data
            )

            return receipt_data

    # ---------------------------------------------------------------------

    def authorized_tick(self, source: str = "HHSRuntimeController.authorized_tick"):
        """Advance one runtime step and commit through the authority gate.

        This is the canonical automatic execution path for emulator/API/GUI
        callers. Direct ``step`` remains available for low-level diagnostics,
        but production execution chains should use this method so Hash72 and
        invariant validation cannot be bypassed.
        """

        with self.runtime_lock:

            runtime_state = self.step()
            receipt_data = self.commit_receipt()

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

    def replay_from_index(
        self,
        start_index: int
    ):

        if start_index < 0:
            start_index = 0

        return self.execution_history[start_index:]

    # ---------------------------------------------------------------------

    def latest_runtime_state(self):

        if self.runtime is None:
            status = self.availability_status()
            return {
                "schema": "HHS_RUNTIME_CONTROLLER_UNAVAILABLE_V1",
                "ok": False,
                "status": "HHS_C_RUNTIME_UNAVAILABLE",
                "available": False,
                "canonical_runtime_authority_active": False,
                "canonical_state_available": False,
                "state_hash72": None,
                "receipt_hash72": None,
                "step": None,
                "halted": True,
                "source_only_degraded_mode": True,
                "runtime_library": status,
                "frontend_is_authority": False,
                "python_replacement_authority": False,
            }

        return self.runtime.export_runtime_dict()

    # =====================================================================
    # GRAPH INGESTION
    # =====================================================================

    def export_graph_node(self):

        runtime = self.require_runtime()
        runtime_state = (
            runtime.export_runtime_dict()
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

        runtime = self.require_runtime()
        runtime_state = (
            runtime.export_runtime_dict()
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

        runtime = self.require_runtime()
        runtime_state = (
            runtime.export_runtime_dict()
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
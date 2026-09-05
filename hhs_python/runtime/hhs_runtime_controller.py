# ============================================================================
# hhs_python/runtime/hhs_runtime_controller.py
# HARMONICODE / HHS — CANONICAL RUNTIME CONTROLLER
# ============================================================================

from __future__ import annotations

import time
import uuid
import threading

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Mapping

from hhs_python.runtime.hhs_ctypes_bridge import HHSRuntimeBridge
from hhs_runtime.hhs_authority_gate_v1 import assert_runtime_authorized
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload

EVENT_RUNTIME_STEP = "runtime_step"
EVENT_RUNTIME_HALT = "runtime_halt"
EVENT_RECEIPT_COMMIT = "receipt_commit"
EVENT_CONVERGENCE = "runtime_convergence"
EVENT_ORBIT = "runtime_orbit"
HASH72_LENGTH = 72
PASS219_CONSTITUTIONAL_SOURCE_PREFIX = "HHS_PASS219_CONSTITUTIONAL_ETHICAL_ADMISSION:"


@dataclass
class HHSSandbox:
    sandbox_id: str
    created_at: float
    runtime: HHSRuntimeBridge
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class HHSRuntimeController:
    """Canonical runtime execution authority."""

    def __init__(self):
        self.runtime = HHSRuntimeBridge()
        self.runtime_lock = threading.RLock()
        self.listeners: Dict[str, List[Callable]] = {}
        self.sandboxes: Dict[str, HHSSandbox] = {}
        self.execution_history = []
        self.replay_cache = []
        self.authority_audit_cache = []

    def add_listener(self, event_name: str, callback: Callable):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)

    def emit_event(self, event_name: str, payload: Dict):
        for callback in self.listeners.get(event_name, []):
            try:
                callback(payload)
            except Exception as e:
                print(f"[HHS EVENT ERROR] {event_name}: {e}")

    def step(self):
        with self.runtime_lock:
            self.runtime.runtime_step()
            runtime_state = self.runtime.export_runtime_dict()
            self.execution_history.append(runtime_state)
            self.emit_event(EVENT_RUNTIME_STEP, runtime_state)
            if runtime_state["converged"]:
                self.emit_event(EVENT_CONVERGENCE, runtime_state)
            if runtime_state["halted"]:
                self.emit_event(EVENT_RUNTIME_HALT, runtime_state)
            return runtime_state

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

    def commit_receipt(self):
        with self.runtime_lock:
            self.runtime.receipt_commit()
            receipt_data = {
                "step": self.runtime.step,
                "state_hash72": self.runtime.state_hash72,
                "receipt_hash72": self.runtime.receipt_hash72,
            }
            runtime_state = self.runtime.export_runtime_dict()
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
            self.emit_event(EVENT_RECEIPT_COMMIT, receipt_data)
            return receipt_data

    @staticmethod
    def _validate_pass219_constitutional_trace(
        source: str,
        constitutional_trace: Optional[Mapping[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Validate proof continuity for the Pass-219 constitutional path.

        Existing inherited callers remain callable during migration.  However,
        a caller claiming the Pass-219 constitutional source domain cannot
        cross this controller without the exact PASS trace whose receipt is
        embedded in the source string.  This prevents bridge-to-controller
        proof stripping while the broader legacy call-site migration proceeds.
        """
        if not source.startswith(PASS219_CONSTITUTIONAL_SOURCE_PREFIX):
            return None
        if not isinstance(constitutional_trace, Mapping):
            raise RuntimeError("PASS219_CONSTITUTIONAL_TRACE_REQUIRED")
        if constitutional_trace.get("state") != "PASS":
            raise RuntimeError("PASS219_CONSTITUTIONAL_TRACE_NOT_PASS")
        receipt_hash72 = constitutional_trace.get("trace_receipt_hash72")
        if not isinstance(receipt_hash72, str) or len(receipt_hash72) != HASH72_LENGTH:
            raise RuntimeError("PASS219_CONSTITUTIONAL_RECEIPT_INVALID")
        expected_prefix = PASS219_CONSTITUTIONAL_SOURCE_PREFIX + receipt_hash72 + ":"
        if not source.startswith(expected_prefix):
            raise RuntimeError("PASS219_CONSTITUTIONAL_RECEIPT_SOURCE_MISMATCH")
        return dict(constitutional_trace)

    def authorized_tick(
        self,
        source: str = "HHSRuntimeController.authorized_tick",
        *,
        constitutional_trace: Optional[Mapping[str, Any]] = None,
    ):
        """Advance one runtime step and commit through the authority gate.

        Pass-219 constitutional callers must carry their PASS trace through the
        controller boundary.  Other inherited call sites remain temporarily
        compatible until their modality migration is completed; they are not
        thereby classified as constitutionally integrated.
        """
        bound_constitutional = self._validate_pass219_constitutional_trace(
            source, constitutional_trace
        )
        with self.runtime_lock:
            runtime_state = self.step()
            receipt_data = self.commit_receipt()
            authority_audit = assert_runtime_authorized(
                runtime_state,
                source=source,
                receipt=receipt_data,
                require_receipt=True,
            ).to_dict()
            result = {
                "runtime": runtime_state,
                "receipt": receipt_data,
                "authority_audit": authority_audit,
            }
            if bound_constitutional is not None:
                result["constitutional_trace"] = bound_constitutional
                result["constitutional_receipt_hash72"] = bound_constitutional[
                    "trace_receipt_hash72"
                ]
            return result

    def create_sandbox(self, metadata: Optional[Dict] = None) -> HHSSandbox:
        sandbox = HHSSandbox(
            sandbox_id=str(uuid.uuid4()),
            created_at=time.time(),
            runtime=HHSRuntimeBridge(),
            metadata=metadata or {},
        )
        self.sandboxes[sandbox.sandbox_id] = sandbox
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

    def replay_from_index(self, start_index: int):
        if start_index < 0:
            start_index = 0
        return self.execution_history[start_index:]

    def latest_runtime_state(self):
        return self.runtime.export_runtime_dict()

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

    def export_vector_record(self):
        runtime_state = self.runtime.export_runtime_dict()
        hash72 = runtime_state["state_hash72"]
        vector = [ord(ch) / 255.0 for ch in hash72]
        return {"hash72": hash72, "vector": vector, "step": runtime_state["step"]}

    def export_multimodal_packet(self):
        runtime_state = self.runtime.export_runtime_dict()
        return {
            "runtime": runtime_state,
            "graph_node": self.export_graph_node(),
            "vector_record": self.export_vector_record(),
        }


def controller_self_test():
    controller = HHSRuntimeController()
    controller.run_steps(5)
    controller.commit_receipt()
    print("\nRUNTIME STATE")
    print(controller.latest_runtime_state())
    print("\nGRAPH NODE")
    print(controller.export_graph_node())
    print("\nVECTOR RECORD")
    print(controller.export_vector_record())


if __name__ == "__main__":
    controller_self_test()

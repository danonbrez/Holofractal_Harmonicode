"""
HHS Live Kernel Event Bridge v1
===============================

Pass 045 binds the Python/C kernel runtime to FastAPI websocket authority.
This module is the canonical bridge from real emulator ticks to runtime event
schema envelopes.  It does not synthesize demo events: every emitted event is
built from an HHSCEmulator tick, receipt, authority audit, and runtime packet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

from hhs_backend.runtime.runtime_event_schema import (
    HHSRuntimeEventEnvelope,
    create_runtime_event,
)
from hhs_backend.runtime.runtime_ws import propagate_runtime_event
from hhs_python.runtime.hhs_runtime_emulator import HHSCEmulator
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness

VERSION = "PASS_045_LIVE_FASTAPI_KERNEL_RUNTIME_V1"
BRIDGE_SCHEMA = "HHS_LIVE_KERNEL_EVENT_BRIDGE_V1"
AUTHORITY = "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1"


@dataclass
class LiveKernelEventBridge:
    """Build canonical websocket events from real kernel runtime ticks."""

    runtime_emulator: HHSCEmulator
    runtime_id: str = "runtime_main"
    branch_id: str = "main"
    parent_event_hash72: str = ""
    sequence_id: int = 0
    emitted_events: list[Dict[str, Any]] = field(default_factory=list)

    def _root(self, label: str, payload: Mapping[str, Any]) -> str:
        return make_hash72_kernel_witness(label, dict(payload), width=72).digest

    def tick_kernel(self, instruction: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        """Advance the real emulator and return the raw kernel tick result."""

        result = self.runtime_emulator.tick(instruction=dict(instruction or {}))
        runtime = dict(result.get("runtime") or {})
        receipt = dict(result.get("receipt") or {})
        packet = dict(result.get("packet") or {})
        authority_audit = dict(result.get("authority_audit") or {})
        if not runtime.get("state_hash72"):
            raise RuntimeError("live kernel tick did not produce a runtime state_hash72")
        if not receipt.get("receipt_hash72"):
            raise RuntimeError("live kernel tick did not produce a receipt_hash72")
        return {
            "schema": "HHS_LIVE_KERNEL_TICK_RESULT_V1",
            "version": VERSION,
            "runtime": runtime,
            "receipt": receipt,
            "packet": packet,
            "authority_audit": authority_audit,
            "instruction": dict(instruction or {}),
        }

    def build_event(self, tick_result: Mapping[str, Any], *, event_type: str = "runtime") -> HHSRuntimeEventEnvelope:
        """Convert a real tick result to a canonical runtime event envelope."""

        runtime = dict(tick_result.get("runtime") or {})
        receipt = dict(tick_result.get("receipt") or {})
        packet = dict(tick_result.get("packet") or {})
        authority_audit = dict(tick_result.get("authority_audit") or {})
        self.sequence_id += 1
        payload = {
            "schema": "HHS_LIVE_KERNEL_RUNTIME_EVENT_PAYLOAD_V1",
            "version": VERSION,
            "source": "LiveKernelEventBridge.tick_kernel",
            "kernel_tick": runtime.get("step"),
            "runtime_state_hash72": runtime.get("state_hash72"),
            "receipt_hash72": receipt.get("receipt_hash72"),
            "contract_hash72": self._root("HHS_LIVE_KERNEL_EVENT_CONTRACT_V1", {"runtime": runtime, "receipt": receipt}),
            "conformance_root": self._root("HHS_LIVE_KERNEL_CONFORMANCE_PROJECTION_V1", authority_audit),
            "zero_bypass_status": "INTERPOSED_BY_FASTAPI_LIVE_KERNEL_WORKFLOW",
            "runtime": runtime,
            "receipt": receipt,
            "packet": packet,
            "authority_audit": authority_audit,
            "instruction": dict(tick_result.get("instruction") or {}),
        }
        event = create_runtime_event(
            event_type=event_type,
            runtime_id=self.runtime_id,
            branch_id=self.branch_id,
            receipt_hash72=str(receipt.get("receipt_hash72")),
            parent_event_hash72=self.parent_event_hash72,
            payload=payload,
        )
        event.metadata.update({
            "schema": "HHS_LIVE_KERNEL_EVENT_METADATA_V1",
            "version": VERSION,
            "authority": AUTHORITY,
            "sequence_id": self.sequence_id,
            "kernel_tick": runtime.get("step"),
            "runtime_state_hash72": runtime.get("state_hash72"),
            "contract_hash72": payload.get("contract_hash72"),
            "conformance_root": payload.get("conformance_root"),
            "zero_bypass_status": payload.get("zero_bypass_status"),
            "channel_authority": "FASTAPI_WEBSOCKET_KERNEL_CHANNEL_ROUTER_V1",
        })
        self.parent_event_hash72 = event.event_hash72
        self.emitted_events.append(event.to_dict())
        return event

    async def emit_tick_event(self, instruction: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        """Tick the kernel and propagate the resulting event to all four channels."""

        tick_result = self.tick_kernel(instruction=instruction)
        event = self.build_event(tick_result)
        await propagate_runtime_event(event)
        return {
            "schema": "HHS_LIVE_KERNEL_EVENT_EMISSION_RECORD_V1",
            "version": VERSION,
            "ok": event.verify_event_hash72(),
            "event_hash72": event.event_hash72,
            "receipt_hash72": event.receipt_hash72,
            "sequence_id": self.sequence_id,
            "kernel_tick": event.metadata.get("kernel_tick"),
            "runtime_state_hash72": event.metadata.get("runtime_state_hash72"),
            "channels": ["/ws/runtime", "/ws/replay", "/ws/graph", "/ws/transport"],
        }

    def status(self) -> Dict[str, Any]:
        # Pass 045 keeps live status bounded.  HHSCEmulator.status() includes a
        # full service-registry status, which rebuilds the conformance map and
        # is too heavy for every live health poll/background tick.
        runtime_state = self.runtime_emulator.controller.latest_runtime_state()
        return {
            "schema": "HHS_LIVE_KERNEL_EVENT_BRIDGE_STATUS_V1",
            "version": VERSION,
            "authority": AUTHORITY,
            "runtime_id": self.runtime_id,
            "branch_id": self.branch_id,
            "sequence_id": self.sequence_id,
            "parent_event_hash72": self.parent_event_hash72,
            "emitted_event_count": len(self.emitted_events),
            "emulator": {
                "boot_id": self.runtime_emulator.config.boot_id,
                "booted": self.runtime_emulator.booted,
                "ticks": len(self.runtime_emulator.tick_history),
                "runtime_step": runtime_state.get("step"),
                "runtime_state_hash72": runtime_state.get("state_hash72"),
                "receipt_hash72": runtime_state.get("receipt_hash72"),
                "bounded_live_status": True,
            },
        }


def live_kernel_event_bridge_self_test() -> Dict[str, Any]:
    emulator = HHSCEmulator()
    bridge = LiveKernelEventBridge(runtime_emulator=emulator)
    tick = bridge.tick_kernel({"source": "self_test"})
    event = bridge.build_event(tick)
    ws_payload = event.to_websocket_payload()
    return {
        "schema": "HHS_LIVE_KERNEL_EVENT_BRIDGE_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(event.verify_event_hash72() and ws_payload.get("runtime_state_hash72") and ws_payload.get("receipt_hash72")),
        "event_hash72": event.event_hash72,
        "receipt_hash72": event.receipt_hash72,
        "runtime_state_hash72": ws_payload.get("runtime_state_hash72"),
        "sequence_id": ws_payload.get("sequence_id"),
        "authority": ws_payload.get("authority"),
    }


if __name__ == "__main__":
    print(live_kernel_event_bridge_self_test())

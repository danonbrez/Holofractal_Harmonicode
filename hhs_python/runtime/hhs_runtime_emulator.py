# ============================================================================
# hhs_python/runtime/hhs_runtime_emulator.py
# HARMONICODE / HHS
# AUTOMATIC C-RUNTIME EMULATOR BOOT LOOP
#
# PURPOSE
# -------
# Consumer/runtime-facing emulator shell for the deterministic C kernel.
#
# The ctypes bridge proves that Python can call the C ABI. This module turns
# that bridge into an automatic runtime device: boot, tick, commit receipts,
# export packets, and run bounded execution cycles without requiring callers to
# know the manual C/Python sequence.
# ============================================================================

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_runtime.hhs_authority_gate_v1 import assert_runtime_authorized
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


@dataclass
class HHSEmulatorConfig:
    """Configuration for automatic C-runtime emulation."""

    boot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    auto_commit_receipts: bool = True
    auto_export_packets: bool = True
    max_steps_per_run: int = 1024
    metadata: Dict[str, Any] = field(default_factory=dict)


class HHSCEmulator:
    """Automatic emulator surface for the HHS C runtime kernel.

    This is intentionally small and deterministic. It does not replace the
    kernel, controller, graph, or backend. It coordinates the already-existing
    controller into an emulator-style lifecycle suitable for GUI/API use.
    """

    def __init__(
        self,
        config: Optional[HHSEmulatorConfig] = None,
        controller: Optional[HHSRuntimeController] = None,
    ):
        self.config = config or HHSEmulatorConfig()
        self.controller = controller or HHSRuntimeController()
        self.booted = False
        self.booted_at: Optional[float] = None
        self.tick_history: List[Dict[str, Any]] = []
        self.last_packet: Optional[Dict[str, Any]] = None
        self.service_registry = make_default_service_registry(self.controller)

    def boot(self) -> Dict[str, Any]:
        """Initialize and validate the C ABI, returning the initial state."""

        if not self.controller.runtime.validate_abi():
            raise RuntimeError("HHS C runtime ABI validation failed")

        self.booted = True
        self.booted_at = time.time()

        state = self.controller.latest_runtime_state()
        authority_audit = assert_runtime_authorized(
            state,
            source="HHSCEmulator.boot",
            require_receipt=False,
        ).to_dict()
        return {
            "boot_id": self.config.boot_id,
            "booted": True,
            "booted_at": self.booted_at,
            "runtime": state,
            "authority_audit": authority_audit,
            "metadata": self.config.metadata,
            "services": self.service_registry.services(),
        }

    def tick(self, instruction: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Advance one deterministic VM tick and optionally commit/export."""

        if not self.booted:
            self.boot()

        if self.config.auto_commit_receipts:
            authorized = self.controller.authorized_tick(
                source="HHSCEmulator.tick"
            )
            runtime = authorized["runtime"]
            receipt = authorized["receipt"]
            authority_audit = authorized["authority_audit"]
        else:
            runtime = self.controller.step()
            authority_audit = assert_runtime_authorized(
                runtime,
                source="HHSCEmulator.tick.uncommitted",
                require_receipt=False,
            ).to_dict()
            receipt = None

        packet = None
        if self.config.auto_export_packets:
            packet = self.controller.export_multimodal_packet()
            self.last_packet = packet

        result = {
            "boot_id": self.config.boot_id,
            "instruction": instruction or {},
            "runtime": runtime,
            "receipt": receipt,
            "authority_audit": authority_audit,
            "packet": packet,
        }

        self.tick_history.append(result)
        return result

    def run(
        self,
        steps: int = 1,
        until_halt: bool = False,
        instruction: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run a bounded automatic emulation cycle."""

        if steps < 0:
            raise ValueError("steps must be non-negative")

        bounded_steps = min(steps, self.config.max_steps_per_run)
        results: List[Dict[str, Any]] = []

        for _ in range(bounded_steps):
            result = self.tick(instruction=instruction)
            results.append(result)

            if until_halt and result["runtime"].get("halted"):
                break

        latest_runtime = (
            results[-1]["runtime"]
            if results
            else self.controller.latest_runtime_state()
        )

        return {
            "boot_id": self.config.boot_id,
            "requested_steps": steps,
            "executed_steps": len(results),
            "capped": steps > bounded_steps,
            "runtime": latest_runtime,
            "last_packet": self.last_packet,
        }

    def halt(self) -> Dict[str, Any]:
        """Halt the underlying C runtime."""

        if not self.booted:
            self.boot()

        runtime = self.controller.halt()
        return {
            "boot_id": self.config.boot_id,
            "halted": True,
            "runtime": runtime,
        }

    def status(self) -> Dict[str, Any]:
        """Return emulator and runtime status without advancing execution."""

        return {
            "boot_id": self.config.boot_id,
            "booted": self.booted,
            "booted_at": self.booted_at,
            "ticks": len(self.tick_history),
            "runtime": self.controller.latest_runtime_state(),
            "has_packet": self.last_packet is not None,
            "service_registry": self.service_registry.status(),
        }

    def dispatch_service(
        self,
        service_name: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Dispatch a registered runtime service through the guarded chain."""

        if not self.booted:
            self.boot()

        payload_dict = dict(payload or {})
        token = payload_dict.get("zero_bypass_interposition_token")
        if not token:
            interposition = self.service_registry.interpose_dispatch(
                service_name,
                payload_dict,
                request_class=str(payload_dict.get("request_class") or "canonical_full_witness_chain"),
                brute_force_claim=bool(payload_dict.get("brute_force_claim", False)),
            )
            payload_dict["zero_bypass_interposition_token"] = interposition.get("interposition_token")

        return self.service_registry.dispatch(service_name, payload_dict)


def emulator_self_test(steps: int = 3) -> Dict[str, Any]:
    emulator = HHSCEmulator()
    emulator.boot()
    return emulator.run(steps=steps)


if __name__ == "__main__":
    print(emulator_self_test())

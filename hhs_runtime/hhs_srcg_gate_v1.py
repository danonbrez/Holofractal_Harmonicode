"""
HHS SRCG Gate v1
================

Self-Solving Recursive Constraint Gate primitive instruction layer.

SRCG is implemented as a constructive constraint harmonization primitive, not a
conventional sequential equation solver.  The variable is treated as the state
that satisfies the gate.  This module preserves nested quartic carriers in their
original dimensional shape and records every gate step through the kernel-backed
Hash72/u^72 authority surface.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional
import copy
import math

from hhs_python.runtime.hhs_ctypes_bridge import HHSSRCGBridge
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload
from hhs_runtime.hhs_runtime_contract_v1 import make_execution_request, make_runtime_packet, assert_contract
from hhs_foundation.hhs_foundational_standards_v1 import (
    make_proposition_identity,
    make_meaning_witness,
    assert_foundational_conformance,
)

LO_SHU_TENSOR: List[List[int]] = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
DEFAULT_DRIFT_THRESHOLD = 1.001
DEFAULT_LEARNING_RATE = 0.125


def _deep_shape(value: Any) -> Any:
    """Return nested carrier shape without flattening values."""
    if isinstance(value, (list, tuple)):
        return [_deep_shape(item) for item in value]
    if isinstance(value, Mapping):
        return {str(k): _deep_shape(v) for k, v in value.items()}
    return "scalar"


def _deep_copy(value: Any) -> Any:
    return copy.deepcopy(value)


def _loshu_valid(tensor: Any = None) -> bool:
    tensor = LO_SHU_TENSOR if tensor is None else tensor
    try:
        rows = [sum(row) for row in tensor]
        cols = [sum(tensor[r][c] for r in range(3)) for c in range(3)]
        diags = [sum(tensor[i][i] for i in range(3)), sum(tensor[i][2 - i] for i in range(3))]
        return all(v == 15 for v in rows + cols + diags)
    except Exception:
        return False


def check_1001_invariant(A: float, B: float, threshold: float = DEFAULT_DRIFT_THRESHOLD) -> bool:
    if A == 0 or B == 0:
        return False
    ratio = abs(float(A) / float(B))
    return (1.0 / threshold) <= ratio <= threshold


@dataclass(frozen=True)
class SRCGInstruction:
    schema: str = "HHS_SRCG_INSTRUCTION_V1"
    primitive: str = "SelfSolve_AB_Gate"
    equation_id: str = "A=B"
    A: float = 1.0
    B: float = 1.0
    learning_rate: float = DEFAULT_LEARNING_RATE
    drift_threshold: float = DEFAULT_DRIFT_THRESHOLD
    max_steps: int = 1
    quartic_carrier: Any = field(default_factory=lambda: [
        ["b^4", "sqrt(a^2+b^2)^4", "b^2"],
        ["sqrt(a^2+b^2)^2", "sqrt(a^2+b^2)^2+b^2", ["b^6-a^2", "b^4+sqrt(b^2+a^2)^2"]],
        ["b^6", "a^2", "sqrt(a^2+b^2)^2*b^2"],
    ])
    loshu_tensor: Any = field(default_factory=lambda: copy.deepcopy(LO_SHU_TENSOR))
    proposition: str = "The variable is the state that satisfies the SelfSolve_AB_Gate."

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SRCGTraceStep:
    schema: str
    step: int
    before: Dict[str, Any]
    after: Dict[str, Any]
    accepted: bool
    rolled_back: bool
    invariant_1001: bool
    loshu_valid: bool
    quartic_carrier_preserved: bool
    hash72_kernel_witness: Dict[str, Any]
    ledger_tip_hash72: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SRCGState:
    schema: str
    instruction: Dict[str, Any]
    current: Dict[str, Any]
    last_known_closure_point: Dict[str, Any]
    trace: List[Dict[str, Any]]
    ok: bool
    reason: str
    proposition_identity: Dict[str, Any]
    meaning_witness: Dict[str, Any]
    foundational_conformance: Dict[str, Any]
    execution_request: Dict[str, Any]
    runtime_packet: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SRCGFabric:
    """Global Constraint Propagation fabric for parallel '=' gate relations."""

    def __init__(self, instruction: SRCGInstruction):
        self.instruction = instruction
        self.quartic_shape = _deep_shape(instruction.quartic_carrier)
        self.quartic_carrier = _deep_copy(instruction.quartic_carrier)
        self.bridge = HHSSRCGBridge(
            instruction.A,
            instruction.B,
            instruction.learning_rate,
            instruction.drift_threshold,
        )
        self.last_known_closure_point = self.bridge.export()
        self.trace: List[Dict[str, Any]] = []

    def _carrier_preserved(self) -> bool:
        return _deep_shape(self.quartic_carrier) == self.quartic_shape

    def _record_step(self, step: int, before: Dict[str, Any], after: Dict[str, Any], accepted: bool) -> Dict[str, Any]:
        trace_payload = {
            "schema": "HHS_SRCG_TRACE_PAYLOAD_V1",
            "instruction": self.instruction.to_dict(),
            "before": before,
            "after": after,
            "accepted": accepted,
            "quartic_shape": self.quartic_shape,
        }
        witness = make_hash72_kernel_witness("SRCG_TRACE_STEP", trace_payload, width=72).to_dict()
        ledger = append_payload("SRCG_TRACE_STEP", f"SRCGFabric.step.{step}", {**trace_payload, "hash72_kernel_witness": witness})
        trace = SRCGTraceStep(
            schema="HHS_SRCG_TRACE_STEP_V1",
            step=step,
            before=before,
            after=after,
            accepted=accepted,
            rolled_back=bool(after.get("rolled_back")),
            invariant_1001=check_1001_invariant(after.get("A", 0.0), after.get("B", 0.0), self.instruction.drift_threshold),
            loshu_valid=_loshu_valid(self.instruction.loshu_tensor),
            quartic_carrier_preserved=self._carrier_preserved(),
            hash72_kernel_witness=witness,
            ledger_tip_hash72=ledger.get("tip_hash72"),
        ).to_dict()
        self.trace.append(trace)
        return trace

    def fire_parallel(self) -> SRCGState:
        proposition_identity = make_proposition_identity(
            self.instruction.proposition,
            source="SRCGFabric.fire_parallel",
            context={"primitive": self.instruction.primitive, "equation_id": self.instruction.equation_id},
        )
        meaning_witness = make_meaning_witness(
            proposition_identity,
            proposition_identity,
            transformation_rule="SRCG constructive constraint harmonization preserving proposition identity",
            reversible=True,
        )
        execution_request = make_execution_request(
            source="SRCGFabric.fire_parallel",
            operation="SelfSolve_AB_Gate",
            payload={
                "instruction": self.instruction.to_dict(),
                "proposition_identity": proposition_identity,
                "meaning_witness": meaning_witness,
            },
            requires_authority=True,
        )
        assert_contract(execution_request, expected_type="execution_request")
        runtime_packet = make_runtime_packet("SRCG", "SelfSolve_AB_Gate", execution_request)
        foundational = assert_foundational_conformance(
            {
                "schema": "HHS_SRCG_FOUNDATIONAL_AUDIT_PAYLOAD_V1",
                "proposition_identity": proposition_identity,
                "meaning_witness": meaning_witness,
                "transformation_rule": "SRCG constructive constraint harmonization preserving proposition identity",
                "execution_request": execution_request,
                "runtime_packet": runtime_packet,
            },
            source="SRCGFabric.fire_parallel",
            require_receipt=False,
        ).to_dict()

        ok = True
        reason = "closure maintained"
        for step in range(1, max(1, int(self.instruction.max_steps)) + 1):
            before = self.bridge.export()
            accepted = self.bridge.step()
            after = self.bridge.export()
            if accepted and check_1001_invariant(after["A"], after["B"], self.instruction.drift_threshold) and _loshu_valid(self.instruction.loshu_tensor) and self._carrier_preserved():
                self.last_known_closure_point = after
            else:
                ok = False
                reason = "rollback to last-known-closure-point after SRCG drift or carrier violation"
            self._record_step(step, before, after, accepted)
            if not ok:
                break

        current = self.bridge.export()
        return SRCGState(
            schema="HHS_SRCG_STATE_V1",
            instruction=self.instruction.to_dict(),
            current=current,
            last_known_closure_point=self.last_known_closure_point,
            trace=self.trace,
            ok=ok,
            reason=reason,
            proposition_identity=proposition_identity,
            meaning_witness=meaning_witness,
            foundational_conformance=foundational,
            execution_request=execution_request,
            runtime_packet=runtime_packet,
        )


def selfsolve_ab_gate(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    payload = dict(payload or {})
    instruction = SRCGInstruction(
        A=float(payload.get("A", 1.0005)),
        B=float(payload.get("B", 1.0)),
        learning_rate=float(payload.get("learning_rate", DEFAULT_LEARNING_RATE)),
        drift_threshold=float(payload.get("drift_threshold", DEFAULT_DRIFT_THRESHOLD)),
        max_steps=int(payload.get("max_steps", 1)),
        quartic_carrier=_deep_copy(payload.get("quartic_carrier", SRCGInstruction().quartic_carrier)),
        loshu_tensor=_deep_copy(payload.get("loshu_tensor", LO_SHU_TENSOR)),
        proposition=str(payload.get("proposition", "The variable is the state that satisfies the SelfSolve_AB_Gate.")),
    )
    fabric = SRCGFabric(instruction)
    return fabric.fire_parallel().to_dict()


def srcg_primitive_self_test() -> Dict[str, Any]:
    stable = selfsolve_ab_gate({"A": 1.0005, "B": 1.0, "max_steps": 2})
    rollback = selfsolve_ab_gate({"A": 2.0, "B": 1.0, "max_steps": 1})
    ok = (
        stable["ok"]
        and stable["trace"]
        and stable["trace"][0]["quartic_carrier_preserved"]
        and stable["trace"][0]["hash72_kernel_witness"]["zero_sum"]
        and not rollback["ok"]
        and rollback["trace"][0]["rolled_back"]
    )
    return {
        "schema": "HHS_SRCG_PRIMITIVE_SELF_TEST_V1",
        "ok": ok,
        "stable": stable,
        "rollback": rollback,
    }


if __name__ == "__main__":
    print(srcg_primitive_self_test())

"""
HHS PhaseTransportVM v1
=======================

Executable transition layer for HHS attention edges.

Every operation is routed through kernel gates before commit:

    constructor -> invariant -> phase -> Lo Shu -> xyzw DNA -> Hash72 -> ethics -> commit/quarantine

This module intentionally avoids floating point state and keeps all transition
outcomes receipt-addressable.  It can run against the current scaffold and can
be replaced/adapted by the fuller PhaseTransportVM once the hydrated runtime
bundle is committed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from typing import Dict, Iterable, List, Sequence

from hhs_runtime.hhs_attention_operator_v1 import (
    AttentionReceipt,
    AttentionScore,
    attend_tokens,
    score_edge,
)
from hhs_runtime.hhs_loshu_phase_embedding_v1 import (
    FORBIDDEN_ADJACENCIES,
    LO_SHU_CELLS,
    TORUS_ORDER,
    PhaseEmbeddingState,
    embed_sequence,
    hash72_digest,
)


class GateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class TransitionStatus(str, Enum):
    COMMITTED = "COMMITTED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class KernelGateReceipt:
    """One named gate evaluation."""

    name: str
    status: GateStatus
    details: Dict[str, object]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseTransition:
    """Executable transition candidate derived from one attention edge."""

    source_hash72: str
    target_hash72: str
    source_token: str
    target_token: str
    phase_delta: int
    loshu_delta: int
    dna_bridge: str
    score_receipt_hash72: str
    operation_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseTransitionReceipt:
    """Final receipt for a gated transition execution."""

    transition: PhaseTransition
    gates: List[KernelGateReceipt]
    status: TransitionStatus
    committed_hash72: str | None
    quarantine_hash72: str | None
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "transition": self.transition.to_dict(),
            "gates": [gate.to_dict() for gate in self.gates],
            "status": self.status.value,
            "committed_hash72": self.committed_hash72,
            "quarantine_hash72": self.quarantine_hash72,
            "receipt_hash72": self.receipt_hash72,
        }


@dataclass(frozen=True)
class VMRunReceipt:
    """Receipt for a full PhaseTransportVM run."""

    module: str
    attention_receipt_hash72: str
    transition_receipts: List[PhaseTransitionReceipt]
    committed: int
    quarantined: int
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "module": self.module,
            "attention_receipt_hash72": self.attention_receipt_hash72,
            "transition_receipts": [receipt.to_dict() for receipt in self.transition_receipts],
            "committed": self.committed,
            "quarantined": self.quarantined,
            "receipt_hash72": self.receipt_hash72,
        }


def _gate(name: str, ok: bool, details: Dict[str, object]) -> KernelGateReceipt:
    status = GateStatus.PASS if ok else GateStatus.FAIL
    receipt = hash72_digest(("kernel_gate", name, status.value, sorted(details.items())))
    return KernelGateReceipt(name=name, status=status, details=details, receipt_hash72=receipt)


def build_transition(source: PhaseEmbeddingState, target: PhaseEmbeddingState, edge: AttentionScore) -> PhaseTransition:
    """Construct an executable phase transition from source/target states."""

    phase_delta = (target.phase_index - source.phase_index) % TORUS_ORDER
    loshu_delta = (target.lo_shu.cell_index - source.lo_shu.cell_index) % LO_SHU_CELLS
    dna_bridge = source.xyzw_dna[-1] + target.xyzw_dna[0]
    operation_hash = hash72_digest(
        (
            "phase_transition_v1",
            source.receipt_hash72,
            target.receipt_hash72,
            phase_delta,
            loshu_delta,
            dna_bridge,
            edge.receipt_hash72,
        )
    )
    return PhaseTransition(
        source_hash72=source.hash72,
        target_hash72=target.hash72,
        source_token=source.token,
        target_token=target.token,
        phase_delta=phase_delta,
        loshu_delta=loshu_delta,
        dna_bridge=dna_bridge,
        score_receipt_hash72=edge.receipt_hash72,
        operation_hash72=operation_hash,
    )


def constructor_gate(source: PhaseEmbeddingState, target: PhaseEmbeddingState, transition: PhaseTransition) -> KernelGateReceipt:
    ok = bool(source.receipt_hash72 and target.receipt_hash72 and transition.operation_hash72)
    return _gate(
        "constructor_gate",
        ok,
        {
            "source_receipt_present": bool(source.receipt_hash72),
            "target_receipt_present": bool(target.receipt_hash72),
            "operation_hash_present": bool(transition.operation_hash72),
        },
    )


def invariant_gate(source: PhaseEmbeddingState, target: PhaseEmbeddingState) -> KernelGateReceipt:
    source_ok = all(source.invariants.values())
    target_ok = all(target.invariants.values())
    return _gate(
        "invariant_gate",
        source_ok and target_ok,
        {
            "source_invariants": source.invariants,
            "target_invariants": target.invariants,
        },
    )


def phase_gate(source: PhaseEmbeddingState, target: PhaseEmbeddingState, transition: PhaseTransition) -> KernelGateReceipt:
    expected = (source.phase_index + transition.phase_delta) % TORUS_ORDER
    reciprocal_expected = (-target.phase_index) % TORUS_ORDER
    ok = expected == target.phase_index and target.reciprocal_phase_index == reciprocal_expected
    return _gate(
        "phase_gate",
        ok,
        {
            "source_phase": source.phase_index,
            "target_phase": target.phase_index,
            "phase_delta": transition.phase_delta,
            "expected_target_phase": expected,
            "target_reciprocal": target.reciprocal_phase_index,
            "expected_reciprocal": reciprocal_expected,
        },
    )


def loshu_gate(source: PhaseEmbeddingState, target: PhaseEmbeddingState, transition: PhaseTransition) -> KernelGateReceipt:
    expected = (source.lo_shu.cell_index + transition.loshu_delta) % LO_SHU_CELLS
    row_ok = 0 <= target.lo_shu.row < 9
    col_ok = 0 <= target.lo_shu.col < 9
    ok = expected == target.lo_shu.cell_index and row_ok and col_ok
    return _gate(
        "loshu_gate",
        ok,
        {
            "source_cell": source.lo_shu.cell_index,
            "target_cell": target.lo_shu.cell_index,
            "loshu_delta": transition.loshu_delta,
            "expected_target_cell": expected,
            "target_row": target.lo_shu.row,
            "target_col": target.lo_shu.col,
        },
    )


def dna_gate(source: PhaseEmbeddingState, target: PhaseEmbeddingState, transition: PhaseTransition) -> KernelGateReceipt:
    bridge_pair = (source.xyzw_dna[-1], target.xyzw_dna[0])
    ok = bridge_pair not in FORBIDDEN_ADJACENCIES and transition.dna_bridge == "".join(bridge_pair)
    return _gate(
        "xyzw_dna_gate",
        ok,
        {
            "bridge_pair": "".join(bridge_pair),
            "forbidden": bridge_pair in FORBIDDEN_ADJACENCIES,
            "source_dna": source.xyzw_dna,
            "target_dna": target.xyzw_dna,
        },
    )


def hash72_gate(source: PhaseEmbeddingState, target: PhaseEmbeddingState, transition: PhaseTransition, edge: AttentionScore) -> KernelGateReceipt:
    recomputed = hash72_digest(
        (
            "phase_transition_v1",
            source.receipt_hash72,
            target.receipt_hash72,
            transition.phase_delta,
            transition.loshu_delta,
            transition.dna_bridge,
            edge.receipt_hash72,
        )
    )
    ok = recomputed == transition.operation_hash72 and edge.receipt_hash72 == transition.score_receipt_hash72
    return _gate(
        "hash72_gate",
        ok,
        {
            "operation_hash72": transition.operation_hash72,
            "recomputed_hash72": recomputed,
            "edge_receipt_hash72": edge.receipt_hash72,
        },
    )


def ethics_gate(edge: AttentionScore) -> KernelGateReceipt:
    """
    Runtime ethics/permission gate.

    For this layer, ethics is structural: no transition may commit if attention
    already failed closed or if the weighted state compatibility is zero.
    """

    ok = edge.allowed and edge.weighted_score > Fraction(0, 1)
    return _gate(
        "ethics_gate",
        ok,
        {
            "edge_allowed": edge.allowed,
            "weighted_score": f"{edge.weighted_score.numerator}/{edge.weighted_score.denominator}",
        },
    )


def run_kernel_gates(source: PhaseEmbeddingState, target: PhaseEmbeddingState, edge: AttentionScore) -> PhaseTransitionReceipt:
    """Run every transition through all kernel gates and commit/quarantine."""

    transition = build_transition(source, target, edge)
    gates = [
        constructor_gate(source, target, transition),
        invariant_gate(source, target),
        phase_gate(source, target, transition),
        loshu_gate(source, target, transition),
        dna_gate(source, target, transition),
        hash72_gate(source, target, transition, edge),
        ethics_gate(edge),
    ]
    ok = all(gate.status == GateStatus.PASS for gate in gates)
    if ok:
        committed = hash72_digest(("commit", transition.operation_hash72, [gate.receipt_hash72 for gate in gates]))
        quarantine = None
        status = TransitionStatus.COMMITTED
    else:
        committed = None
        quarantine = hash72_digest(("quarantine", transition.operation_hash72, [gate.to_dict() for gate in gates]))
        status = TransitionStatus.QUARANTINED
    receipt = hash72_digest(("phase_transition_receipt", transition.operation_hash72, status.value, committed, quarantine))
    return PhaseTransitionReceipt(
        transition=transition,
        gates=gates,
        status=status,
        committed_hash72=committed,
        quarantine_hash72=quarantine,
        receipt_hash72=receipt,
    )


def _state_lookup(states: Iterable[PhaseEmbeddingState]) -> Dict[str, PhaseEmbeddingState]:
    return {state.hash72: state for state in states}


def run_attention_transitions(embedding_receipt, attention_receipt: AttentionReceipt) -> VMRunReceipt:
    """Execute the best attention edges as PhaseTransportVM transitions."""

    lookup = _state_lookup(embedding_receipt.states)
    transition_receipts: List[PhaseTransitionReceipt] = []
    for edge in attention_receipt.best_edges:
        source = lookup[edge.query_hash72]
        target = lookup[edge.key_hash72]
        transition_receipts.append(run_kernel_gates(source, target, edge))

    committed_count = sum(1 for receipt in transition_receipts if receipt.status == TransitionStatus.COMMITTED)
    quarantined_count = len(transition_receipts) - committed_count
    receipt_hash = hash72_digest(
        (
            "phase_transport_vm_run_v1",
            attention_receipt.receipt_hash72,
            [receipt.receipt_hash72 for receipt in transition_receipts],
            committed_count,
            quarantined_count,
        )
    )
    return VMRunReceipt(
        module="hhs_phase_transport_vm_v1",
        attention_receipt_hash72=attention_receipt.receipt_hash72,
        transition_receipts=transition_receipts,
        committed=committed_count,
        quarantined=quarantined_count,
        receipt_hash72=receipt_hash,
    )


def run_tokens(tokens: Sequence[str], d_model: int = 72, dimensions: int = 4, top_k: int = 1) -> VMRunReceipt:
    """Convenience entry point: tokens -> embedding -> attention -> gated VM run."""

    embedding = embed_sequence(tokens, d_model=d_model, dimensions=dimensions)
    attention = attend_tokens(tokens, d_model=d_model, dimensions=dimensions, top_k=top_k)
    return run_attention_transitions(embedding, attention)


def demo() -> Dict[str, object]:
    receipt = run_tokens(["HHS", "Hash72", "LoShu", "xyzw"], d_model=72, dimensions=3, top_k=1)
    return receipt.to_dict()


if __name__ == "__main__":
    import json

    print(json.dumps(demo(), indent=2, sort_keys=True))

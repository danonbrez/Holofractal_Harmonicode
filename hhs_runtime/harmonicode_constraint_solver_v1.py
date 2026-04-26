"""
HARMONICODE Constraint Solver v1
================================

Conservative reconciliation and invariant enforcement layer for HARMONICODE IR.

Pipeline:
    InterpreterResult / ConstraintGraph
    -> union-find equality reconciliation
    -> inequality contradiction detection
    -> invariant receipt
    -> solve receipt

This solver does NOT simplify algebra, commute ordered products, or collapse
projection layers. It only reconciles explicit equality edges and validates that
explicit inequality edges do not contradict the equality closure.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.harmonicode_interpreter_v1 import ConstraintGraph, InterpreterResult, interpret


class SolveStatus(str, Enum):
    SOLVED = "SOLVED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class EquivalenceClass:
    representative: str
    members: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SolverContradiction:
    kind: str
    left: str
    right: str
    reason: str
    contradiction_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InvariantReceipt:
    delta_e_zero: bool
    psi_zero: bool
    theta15_true: bool
    omega_true: bool
    details: Dict[str, Any]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SolverReceipt:
    graph_hash72: str
    equivalence_hash72: str
    contradiction_hashes: List[str]
    invariant_receipt_hash72: str
    status: SolveStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class SolverResult:
    equivalence_classes: List[EquivalenceClass]
    contradictions: List[SolverContradiction]
    invariant_receipt: InvariantReceipt
    receipt: SolverReceipt

    def to_dict(self) -> Dict[str, Any]:
        return {
            "equivalence_classes": [c.to_dict() for c in self.equivalence_classes],
            "contradictions": [c.to_dict() for c in self.contradictions],
            "invariant_receipt": self.invariant_receipt.to_dict(),
            "receipt": self.receipt.to_dict(),
        }


class UnionFind:
    def __init__(self, nodes: List[str]) -> None:
        self.parent = {n: n for n in nodes}

    def find(self, x: str) -> str:
        if x not in self.parent:
            self.parent[x] = x
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        # Stable deterministic representative: lexical minimum.
        keep, drop = (ra, rb) if ra <= rb else (rb, ra)
        self.parent[drop] = keep

    def classes(self) -> List[EquivalenceClass]:
        groups: Dict[str, List[str]] = {}
        for node in sorted(self.parent):
            groups.setdefault(self.find(node), []).append(node)
        return [EquivalenceClass(rep, sorted(members)) for rep, members in sorted(groups.items())]


def theta15_true() -> bool:
    rows = all(sum(row) == 15 for row in LO_SHU_3X3)
    cols = all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
    diag_a = sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
    diag_b = sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    return rows and cols and diag_a and diag_b


def _is_ordered_commutation_pair(a: str, b: str) -> bool:
    """Detect simple forbidden two-symbol reversal pairs such as xy/yx or zw/wz.

    This is deliberately conservative. It does not parse full algebra; it only
    protects the most common HARMONICODE ordered product atoms from accidental
    equality closure.
    """
    return len(a) == len(b) == 2 and a[0] == b[1] and a[1] == b[0] and a != b


def solve_constraint_graph(graph: ConstraintGraph) -> SolverResult:
    uf = UnionFind(graph.nodes)
    neq_edges: List[Tuple[str, str]] = []

    for edge in graph.edges:
        if edge.type in {"chain_eq", "assert_eq"}:
            uf.union(edge.source, edge.target)
        elif edge.type == "neq":
            neq_edges.append((edge.source, edge.target))

    contradictions: List[SolverContradiction] = []
    for left, right in neq_edges:
        same_class = uf.find(left) == uf.find(right)
        if same_class:
            reason = "Explicit inequality contradicts equality closure."
            h = hash72_digest(("solver_contradiction_v1", "ineq_eq_conflict", left, right, reason), width=24)
            contradictions.append(SolverContradiction("ineq_eq_conflict", left, right, reason, h))

    for cls in uf.classes():
        members = cls.members
        for i, left in enumerate(members):
            for right in members[i + 1:]:
                if _is_ordered_commutation_pair(left, right):
                    reason = "Forbidden ordered-product commutation detected inside equality class."
                    h = hash72_digest(("solver_contradiction_v1", "unauthorized_commutation", left, right, reason), width=24)
                    contradictions.append(SolverContradiction("unauthorized_commutation", left, right, reason, h))

    equivalence = uf.classes()
    equivalence_hash = hash72_digest(("solver_equivalence_classes_v1", [c.to_dict() for c in equivalence]), width=24)
    invariant = enforce_invariants(graph, equivalence, contradictions)
    status = SolveStatus.SOLVED if not contradictions and invariant.delta_e_zero and invariant.psi_zero and invariant.theta15_true and invariant.omega_true else SolveStatus.QUARANTINED
    receipt_hash = hash72_digest(("solver_receipt_v1", graph.graph_hash72, equivalence_hash, [c.contradiction_hash72 for c in contradictions], invariant.receipt_hash72, status.value), width=24)
    receipt = SolverReceipt(graph.graph_hash72, equivalence_hash, [c.contradiction_hash72 for c in contradictions], invariant.receipt_hash72, status, receipt_hash)
    return SolverResult(equivalence, contradictions, invariant, receipt)


def enforce_invariants(graph: ConstraintGraph, equivalence: List[EquivalenceClass], contradictions: List[SolverContradiction]) -> InvariantReceipt:
    delta_e_zero = len(contradictions) == 0
    # Ψ=0 means every graph node remains represented in exactly one equivalence class.
    members = [m for cls in equivalence for m in cls.members]
    psi_zero = sorted(members) == sorted(set(graph.nodes)) and len(members) == len(set(members))
    theta = theta15_true()
    omega = bool(graph.graph_hash72) and bool(equivalence)
    details = {
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "equivalence_class_count": len(equivalence),
        "contradiction_count": len(contradictions),
        "no_unauthorized_commutation": not any(c.kind == "unauthorized_commutation" for c in contradictions),
    }
    receipt_hash = hash72_digest(("solver_invariant_receipt_v1", delta_e_zero, psi_zero, theta, omega, details), width=24)
    return InvariantReceipt(delta_e_zero, psi_zero, theta, omega, details, receipt_hash)


def solve_interpreter_result(result: InterpreterResult) -> SolverResult:
    return solve_constraint_graph(result.graph)


def interpret_and_solve(source: str) -> Dict[str, Any]:
    interpreted = interpret(source)
    solved = solve_interpreter_result(interpreted)
    full_hash = hash72_digest(("harmonicode_interpret_and_solve_v1", interpreted.receipt.receipt_hash72, solved.receipt.receipt_hash72), width=24)
    return {"interpreter": interpreted.to_dict(), "solver": solved.to_dict(), "full_receipt_hash72": full_hash}


def main() -> None:
    sample = """
xy=-1/yx
yx=-xy
xy≠yx
"""
    print(json.dumps(interpret_and_solve(sample), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

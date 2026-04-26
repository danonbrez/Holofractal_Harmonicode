"""
HARMONICODE Symbolic Transformation Engine v1
============================================

Guarded active algebra layer for HARMONICODE.

Pipeline:
    source / interpreter result
    -> solve + invariant gate
    -> derive explicit implications
    -> rebuild constraint graph
    -> re-solve
    -> emit transformation receipt

Core rule:
    No transformation is accepted unless the transformed graph still passes
    Δe=0, Ψ=0, Θ15=true, Ω=true.

This engine does not commute ordered products and does not perform broad algebraic
simplification. It only applies explicit, auditable transformation rules.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence, Tuple
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.harmonicode_interpreter_v1 import ConstraintEdge, ConstraintGraph, InterpreterResult, interpret
from hhs_runtime.harmonicode_constraint_solver_v1 import SolveStatus, SolverResult, solve_constraint_graph, solve_interpreter_result


class TransformStatus(str, Enum):
    TRANSFORMED = "TRANSFORMED"
    HELD = "HELD"
    QUARANTINED = "QUARANTINED"


class TransformRule(str, Enum):
    EQ_TRANSITIVE_CLOSURE = "EQ_TRANSITIVE_CLOSURE"
    RECIPROCAL_PAIR_DERIVE = "RECIPROCAL_PAIR_DERIVE"
    NEGATION_PAIR_DERIVE = "NEGATION_PAIR_DERIVE"
    HOLD_IF_UNSOLVED = "HOLD_IF_UNSOLVED"


@dataclass(frozen=True)
class TransformStep:
    rule: TransformRule
    source_terms: List[str]
    derived_edge: ConstraintEdge | None
    reason: str
    step_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule": self.rule.value,
            "source_terms": self.source_terms,
            "derived_edge": self.derived_edge.to_dict() if self.derived_edge else None,
            "reason": self.reason,
            "step_hash72": self.step_hash72,
        }


@dataclass(frozen=True)
class TransformationReceipt:
    input_graph_hash72: str
    input_solver_receipt_hash72: str
    output_graph_hash72: str
    output_solver_receipt_hash72: str
    transform_step_hashes: List[str]
    status: TransformStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class TransformationResult:
    input_solver: SolverResult
    output_graph: ConstraintGraph
    output_solver: SolverResult
    steps: List[TransformStep]
    receipt: TransformationReceipt

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_solver": self.input_solver.to_dict(),
            "output_graph": self.output_graph.to_dict(),
            "output_solver": self.output_solver.to_dict(),
            "steps": [s.to_dict() for s in self.steps],
            "receipt": self.receipt.to_dict(),
        }


def _edge_key(edge: ConstraintEdge) -> Tuple[str, str, str]:
    return (edge.type, edge.source, edge.target)


def _make_step(rule: TransformRule, terms: List[str], edge: ConstraintEdge | None, reason: str) -> TransformStep:
    h = hash72_digest(("harmonicode_transform_step_v1", rule.value, terms, edge.to_dict() if edge else None, reason), width=24)
    return TransformStep(rule, terms, edge, reason, h)


def _build_graph_from_edges(nodes: Sequence[str], edges: Sequence[ConstraintEdge]) -> ConstraintGraph:
    node_list = sorted(set(nodes) | {e.source for e in edges} | {e.target for e in edges})
    edge_list = list(edges)
    graph_hash = hash72_digest(("constraint_graph_v1", node_list, [e.to_dict() for e in edge_list]), width=24)
    return ConstraintGraph(node_list, edge_list, graph_hash)


def derive_transitive_equality(graph: ConstraintGraph, solver: SolverResult) -> List[TransformStep]:
    """Add explicit equality edges between members of each equivalence class.

    This does not simplify terms. It only makes implicit equality closure explicit.
    """
    existing = {_edge_key(e) for e in graph.edges}
    steps: List[TransformStep] = []
    for eq_class in solver.equivalence_classes:
        members = eq_class.members
        if len(members) < 3:
            continue
        rep = eq_class.representative
        for term in members:
            if term == rep:
                continue
            edge = ConstraintEdge("derived_eq", rep, term)
            if _edge_key(edge) not in existing:
                steps.append(_make_step(TransformRule.EQ_TRANSITIVE_CLOSURE, [rep, term], edge, "Explicit transitive equality derived from solved equivalence class."))
                existing.add(_edge_key(edge))
    return steps


def derive_pair_rules(graph: ConstraintGraph) -> List[TransformStep]:
    """Derive narrow explicit pair implications from known HARMONICODE forms.

    Supported conservative rules:
    - x=1/y derives y=1/x only when both symbols are atomic single-letter terms.
    - y=-x derives x=-y only when both symbols are atomic single-letter terms.

    These are relation witnesses, not commutation rules.
    """
    existing = {_edge_key(e) for e in graph.edges}
    steps: List[TransformStep] = []
    atomic = re_atomic_symbol
    for edge in graph.edges:
        if edge.type not in {"chain_eq", "assert_eq", "derived_eq"}:
            continue
        left, right = edge.source.strip(), edge.target.strip()
        if atomic(left) and right.startswith("1/") and atomic(right[2:]):
            derived = ConstraintEdge("derived_eq", right[2:], f"1/{left}")
            if _edge_key(derived) not in existing:
                steps.append(_make_step(TransformRule.RECIPROCAL_PAIR_DERIVE, [left, right], derived, "Reciprocal pair relation derived without commutation."))
                existing.add(_edge_key(derived))
        if atomic(left) and right.startswith("-") and atomic(right[1:]):
            derived = ConstraintEdge("derived_eq", right[1:], f"-{left}")
            if _edge_key(derived) not in existing:
                steps.append(_make_step(TransformRule.NEGATION_PAIR_DERIVE, [left, right], derived, "Negation pair relation derived without commutation."))
                existing.add(_edge_key(derived))
    return steps


def re_atomic_symbol(term: str) -> bool:
    return term.isidentifier() and len(term) == 1


def transform_graph(graph: ConstraintGraph) -> TransformationResult:
    input_solver = solve_constraint_graph(graph)
    if input_solver.receipt.status != SolveStatus.SOLVED:
        step = _make_step(TransformRule.HOLD_IF_UNSOLVED, [graph.graph_hash72], None, "Input graph failed solver/invariant gate; transformation held.")
        receipt_hash = hash72_digest(("harmonicode_transformation_receipt_v1", graph.graph_hash72, input_solver.receipt.receipt_hash72, graph.graph_hash72, input_solver.receipt.receipt_hash72, [step.step_hash72], TransformStatus.HELD.value), width=24)
        receipt = TransformationReceipt(graph.graph_hash72, input_solver.receipt.receipt_hash72, graph.graph_hash72, input_solver.receipt.receipt_hash72, [step.step_hash72], TransformStatus.HELD, receipt_hash)
        return TransformationResult(input_solver, graph, input_solver, [step], receipt)

    steps = []
    steps.extend(derive_transitive_equality(graph, input_solver))
    steps.extend(derive_pair_rules(graph))

    if not steps:
        receipt_hash = hash72_digest(("harmonicode_transformation_receipt_v1", graph.graph_hash72, input_solver.receipt.receipt_hash72, graph.graph_hash72, input_solver.receipt.receipt_hash72, [], TransformStatus.HELD.value), width=24)
        receipt = TransformationReceipt(graph.graph_hash72, input_solver.receipt.receipt_hash72, graph.graph_hash72, input_solver.receipt.receipt_hash72, [], TransformStatus.HELD, receipt_hash)
        return TransformationResult(input_solver, graph, input_solver, [], receipt)

    output_edges = list(graph.edges) + [s.derived_edge for s in steps if s.derived_edge is not None]
    output_graph = _build_graph_from_edges(graph.nodes, output_edges)
    output_solver = solve_constraint_graph(output_graph)
    status = TransformStatus.TRANSFORMED if output_solver.receipt.status == SolveStatus.SOLVED else TransformStatus.QUARANTINED
    receipt_hash = hash72_digest(("harmonicode_transformation_receipt_v1", graph.graph_hash72, input_solver.receipt.receipt_hash72, output_graph.graph_hash72, output_solver.receipt.receipt_hash72, [s.step_hash72 for s in steps], status.value), width=24)
    receipt = TransformationReceipt(graph.graph_hash72, input_solver.receipt.receipt_hash72, output_graph.graph_hash72, output_solver.receipt.receipt_hash72, [s.step_hash72 for s in steps], status, receipt_hash)
    return TransformationResult(input_solver, output_graph, output_solver, steps, receipt)


def interpret_solve_transform(source: str) -> Dict[str, Any]:
    interpreted = interpret(source)
    transformed = transform_graph(interpreted.graph)
    full_hash = hash72_digest(("harmonicode_interpret_solve_transform_v1", interpreted.receipt.receipt_hash72, transformed.receipt.receipt_hash72), width=24)
    return {"interpreter": interpreted.to_dict(), "transformation": transformed.to_dict(), "full_receipt_hash72": full_hash}


def main() -> None:
    sample = """
x=1/y
y=-x
x≠y
"""
    print(json.dumps(interpret_solve_transform(sample), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

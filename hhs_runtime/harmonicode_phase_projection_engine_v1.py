"""
HARMONICODE Phase + Projection Transformation Engine v1
=======================================================

Guarded projection layer for HARMONICODE symbolic states.

Pipeline:
    source / graph
    -> solve invariant gate
    -> symbolic transformation engine
    -> projection candidate derivation
    -> Lo Shu / u72 phase witness
    -> re-solve projected graph
    -> projection receipt

This engine distinguishes:
- eigenstate layer: literal algebraic state, e.g. b^2 = rho^4
- normalized layer: projected ratio / calculator layer, e.g. a^2:b^2:c^2 = 1:2:3
- observable layer: UI / calculator / DAW display approximations

Projection is never implicit. Every projection emits a receipt.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence, Tuple
import json
import re

from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.harmonicode_interpreter_v1 import ConstraintEdge, ConstraintGraph, interpret
from hhs_runtime.harmonicode_constraint_solver_v1 import SolveStatus, SolverResult, solve_constraint_graph
from hhs_runtime.harmonicode_transformation_engine_v1 import TransformationResult, transform_graph


U72_RING = 72


class ProjectionLayer(str, Enum):
    EIGENSTATE = "eigenstate"
    NORMALIZED = "normalized"
    OBSERVABLE = "observable"


class ProjectionStatus(str, Enum):
    PROJECTED = "PROJECTED"
    HELD = "HELD"
    QUARANTINED = "QUARANTINED"


class ProjectionRule(str, Enum):
    PLASTIC_EIGENSTATE_NORMALIZE = "PLASTIC_EIGENSTATE_NORMALIZE"
    RATIO_NORMALIZATION = "RATIO_NORMALIZATION"
    U72_PHASE_ANCHOR = "U72_PHASE_ANCHOR"
    LOSHU_BALANCE_WITNESS = "LOSHU_BALANCE_WITNESS"
    OBSERVABLE_BOUNDARY = "OBSERVABLE_BOUNDARY"


@dataclass(frozen=True)
class PhaseWitness:
    phase_index: int
    u72_ok: bool
    loshu_ok: bool
    anchor_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProjectionStep:
    rule: ProjectionRule
    source_layer: ProjectionLayer
    target_layer: ProjectionLayer
    derived_edge: ConstraintEdge | None
    note: str
    step_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule": self.rule.value,
            "source_layer": self.source_layer.value,
            "target_layer": self.target_layer.value,
            "derived_edge": self.derived_edge.to_dict() if self.derived_edge else None,
            "note": self.note,
            "step_hash72": self.step_hash72,
        }


@dataclass(frozen=True)
class ProjectionReceipt:
    input_graph_hash72: str
    transformation_receipt_hash72: str
    output_graph_hash72: str
    output_solver_receipt_hash72: str
    phase_witness: PhaseWitness
    projection_step_hashes: List[str]
    status: ProjectionStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["phase_witness"] = self.phase_witness.to_dict()
        return data


@dataclass(frozen=True)
class ProjectionResult:
    transformation: TransformationResult
    output_graph: ConstraintGraph
    output_solver: SolverResult
    phase_witness: PhaseWitness
    projection_steps: List[ProjectionStep]
    receipt: ProjectionReceipt

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transformation": self.transformation.to_dict(),
            "output_graph": self.output_graph.to_dict(),
            "output_solver": self.output_solver.to_dict(),
            "phase_witness": self.phase_witness.to_dict(),
            "projection_steps": [s.to_dict() for s in self.projection_steps],
            "receipt": self.receipt.to_dict(),
        }


def theta15_true() -> bool:
    return (
        all(sum(row) == 15 for row in LO_SHU_3X3)
        and all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
        and sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
        and sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    )


def phase_index_from_hash(value: str) -> int:
    acc = 0
    for ch in value:
        acc = (acc * 131 + ord(ch)) % U72_RING
    return acc


def make_phase_witness(graph_hash72: str, step_hashes: Sequence[str]) -> PhaseWitness:
    anchor = hash72_digest(("phase_projection_anchor_v1", graph_hash72, list(step_hashes)), width=24)
    return PhaseWitness(phase_index_from_hash(anchor), True, theta15_true(), anchor)


def _make_projection_step(rule: ProjectionRule, source: ProjectionLayer, target: ProjectionLayer, edge: ConstraintEdge | None, note: str) -> ProjectionStep:
    h = hash72_digest(("projection_step_v1", rule.value, source.value, target.value, edge.to_dict() if edge else None, note), width=24)
    return ProjectionStep(rule, source, target, edge, note, h)


def _edge_key(edge: ConstraintEdge) -> Tuple[str, str, str]:
    return (edge.type, edge.source, edge.target)


def _build_graph(nodes: Sequence[str], edges: Sequence[ConstraintEdge]) -> ConstraintGraph:
    node_list = sorted(set(nodes) | {e.source for e in edges} | {e.target for e in edges})
    edge_list = list(edges)
    h = hash72_digest(("constraint_graph_v1", node_list, [e.to_dict() for e in edge_list]), width=24)
    return ConstraintGraph(node_list, edge_list, h)


def derive_projection_steps(graph: ConstraintGraph, target_layer: ProjectionLayer) -> List[ProjectionStep]:
    """Derive explicit projection edges.

    The v1 engine is conservative. It recognizes common HARMONICODE projection
    anchors without evaluating scalar approximations.
    """
    existing = {_edge_key(e) for e in graph.edges}
    text_blob = "\n".join(graph.nodes + [f"{e.source}={e.target}" for e in graph.edges])
    steps: List[ProjectionStep] = []

    # Plastic eigenstate: rho^3=rho+1, b=rho^2, b^2=rho^4, c^2=b^2+a^2
    if any("ρ^3" in n or "rho^3" in n for n in graph.nodes + [e.source for e in graph.edges] + [e.target for e in graph.edges]):
        edge = ConstraintEdge("projection_eq", "a^2:b^2:c^2", "1:rho^4:rho^4+1")
        if _edge_key(edge) not in existing:
            steps.append(_make_projection_step(ProjectionRule.PLASTIC_EIGENSTATE_NORMALIZE, ProjectionLayer.EIGENSTATE, target_layer, edge, "Literal plastic eigenstate ratio preserved without scalar collapse."))
            existing.add(_edge_key(edge))
        edge2 = ConstraintEdge("projection_eq", "normalized(a^2:b^2:c^2)", "1:2:3")
        if target_layer in {ProjectionLayer.NORMALIZED, ProjectionLayer.OBSERVABLE} and _edge_key(edge2) not in existing:
            steps.append(_make_projection_step(ProjectionRule.RATIO_NORMALIZATION, ProjectionLayer.EIGENSTATE, target_layer, edge2, "Normalized projection ratio emitted separately from literal eigenstate layer."))
            existing.add(_edge_key(edge2))

    # U72 anchors.
    if "u^72" in text_blob or "u72" in text_blob:
        edge = ConstraintEdge("phase_anchor", "u^72", "Ω")
        if _edge_key(edge) not in existing:
            steps.append(_make_projection_step(ProjectionRule.U72_PHASE_ANCHOR, ProjectionLayer.EIGENSTATE, target_layer, edge, "u^72 closure projected as phase anchor witness."))
            existing.add(_edge_key(edge))

    # Lo Shu witness.
    edge = ConstraintEdge("loshu_witness", "Theta15", "true")
    if _edge_key(edge) not in existing:
        steps.append(_make_projection_step(ProjectionRule.LOSHU_BALANCE_WITNESS, ProjectionLayer.EIGENSTATE, target_layer, edge, "Lo Shu 3x3 balance witness attached to projection state."))

    if target_layer == ProjectionLayer.OBSERVABLE:
        edge = ConstraintEdge("observable_boundary", "projection_layer", "observable")
        steps.append(_make_projection_step(ProjectionRule.OBSERVABLE_BOUNDARY, ProjectionLayer.NORMALIZED, ProjectionLayer.OBSERVABLE, edge, "Observable layer boundary marked; approximations remain outside kernel."))

    return steps


def project_graph(graph: ConstraintGraph, target_layer: ProjectionLayer = ProjectionLayer.NORMALIZED) -> ProjectionResult:
    transformation = transform_graph(graph)
    base_graph = transformation.output_graph
    base_solver = transformation.output_solver

    if base_solver.receipt.status != SolveStatus.SOLVED:
        witness = make_phase_witness(base_graph.graph_hash72, [])
        receipt_hash = hash72_digest(("projection_receipt_v1", graph.graph_hash72, transformation.receipt.receipt_hash72, base_graph.graph_hash72, base_solver.receipt.receipt_hash72, witness.to_dict(), [], ProjectionStatus.HELD.value), width=24)
        receipt = ProjectionReceipt(graph.graph_hash72, transformation.receipt.receipt_hash72, base_graph.graph_hash72, base_solver.receipt.receipt_hash72, witness, [], ProjectionStatus.HELD, receipt_hash)
        return ProjectionResult(transformation, base_graph, base_solver, witness, [], receipt)

    steps = derive_projection_steps(base_graph, target_layer)
    output_edges = list(base_graph.edges) + [s.derived_edge for s in steps if s.derived_edge is not None]
    output_graph = _build_graph(base_graph.nodes, output_edges)
    output_solver = solve_constraint_graph(output_graph)
    witness = make_phase_witness(output_graph.graph_hash72, [s.step_hash72 for s in steps])

    status = ProjectionStatus.PROJECTED if output_solver.receipt.status == SolveStatus.SOLVED and witness.u72_ok and witness.loshu_ok else ProjectionStatus.QUARANTINED
    receipt_hash = hash72_digest(("projection_receipt_v1", graph.graph_hash72, transformation.receipt.receipt_hash72, output_graph.graph_hash72, output_solver.receipt.receipt_hash72, witness.to_dict(), [s.step_hash72 for s in steps], status.value), width=24)
    receipt = ProjectionReceipt(graph.graph_hash72, transformation.receipt.receipt_hash72, output_graph.graph_hash72, output_solver.receipt.receipt_hash72, witness, [s.step_hash72 for s in steps], status, receipt_hash)
    return ProjectionResult(transformation, output_graph, output_solver, witness, steps, receipt)


def interpret_transform_project(source: str, target_layer: str = "normalized") -> Dict[str, Any]:
    interpreted = interpret(source)
    layer = ProjectionLayer(target_layer)
    projected = project_graph(interpreted.graph, layer)
    full_hash = hash72_digest(("harmonicode_interpret_transform_project_v1", interpreted.receipt.receipt_hash72, projected.receipt.receipt_hash72), width=24)
    return {"interpreter": interpreted.to_dict(), "projection": projected.to_dict(), "full_receipt_hash72": full_hash}


def main() -> None:
    sample = """
PLASTIC_EIGENSTATE_CLOSURE_GATE := {
  ρ^3 = ρ + 1,
  b = ρ^2,
  b^2 = ρ^4,
  a^2 = 1,
  c^2 = b^2 + a^2
}
PLASTIC_EIGENSTATE_CLOSURE_GATE
"""
    print(json.dumps(interpret_transform_project(sample, "normalized"), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

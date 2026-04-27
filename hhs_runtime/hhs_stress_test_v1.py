"""
HHS Stress Test Harness v1
==========================

Pure pre-receipt validation harness for HARMONICODE interpreter passes.

Purpose
-------
Every interpreter pass must validate the emitted source/AST/constraint graph/IR
bundle before an interpreter receipt is accepted.

This module is intentionally side-effect free. It does not call the interpreter,
solver, filesystem, network, subprocesses, or runtime mutation paths. It only
checks the already-built interpreter artifacts and emits a deterministic stress
receipt.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest


class StressStatus(str, Enum):
    PASSED = "PASSED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class StressFinding:
    kind: str
    message: str
    severity: str
    finding_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StressReceipt:
    source_hash72: str
    ast_hash72: str
    graph_hash72: str
    ir_hash72: str
    status: StressStatus
    finding_hashes: List[str]
    details: Dict[str, Any]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class StressResult:
    findings: List[StressFinding]
    receipt: StressReceipt

    def to_dict(self) -> Dict[str, Any]:
        return {"findings": [f.to_dict() for f in self.findings], "receipt": self.receipt.to_dict()}


def _finding(kind: str, message: str, severity: str = "ERROR") -> StressFinding:
    h = hash72_digest(("hhs_stress_finding_v1", kind, message, severity), width=24)
    return StressFinding(kind, message, severity, h)


def _theta15_true() -> bool:
    rows = all(sum(row) == 15 for row in LO_SHU_3X3)
    cols = all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
    diag_a = sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
    diag_b = sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    return rows and cols and diag_a and diag_b


def _ordered_pair_collision(nodes: List[str], edges: List[Dict[str, Any]]) -> List[StressFinding]:
    findings: List[StressFinding] = []
    eq_pairs = {(str(e.get("source")), str(e.get("target"))) for e in edges if e.get("type") in {"chain_eq", "assert_eq"}}
    for a, b in eq_pairs:
        if len(a) == len(b) == 2 and a == b[::-1] and a != b:
            findings.append(_finding("ordered_product_collision", f"Equality edge attempts to identify ordered products {a} and {b}."))
    return findings


def stress_validate_interpreter_artifacts(
    *,
    source: str,
    source_hash72: str,
    ast: Dict[str, Any],
    ast_hash72: str,
    graph: Dict[str, Any],
    ir: Dict[str, Any],
) -> StressResult:
    findings: List[StressFinding] = []
    graph_hash72 = str(graph.get("graph_hash72", ""))
    ir_hash72 = str(ir.get("ir_hash72", ""))
    nodes = [str(n) for n in graph.get("nodes", [])]
    edges = graph.get("edges", []) if isinstance(graph.get("edges", []), list) else []
    blocks = ir.get("blocks", []) if isinstance(ir.get("blocks", []), list) else []

    if not source.strip():
        findings.append(_finding("empty_source", "Interpreter source is empty."))
    if not source_hash72:
        findings.append(_finding("missing_source_hash", "Missing source hash."))
    if not ast_hash72:
        findings.append(_finding("missing_ast_hash", "Missing AST hash."))
    if not graph_hash72:
        findings.append(_finding("missing_graph_hash", "Missing graph hash."))
    if not ir_hash72:
        findings.append(_finding("missing_ir_hash", "Missing IR hash."))
    if ast.get("kind") != "Program":
        findings.append(_finding("invalid_ast_root", "AST root must be Program."))
    if not isinstance(nodes, list):
        findings.append(_finding("invalid_graph_nodes", "Constraint graph nodes must be a list."))
    if not isinstance(edges, list):
        findings.append(_finding("invalid_graph_edges", "Constraint graph edges must be a list."))
    if not blocks:
        findings.append(_finding("empty_ir", "IR must contain at least one block."))
    if not any(b.get("kind") == "ConstraintGraph" for b in blocks if isinstance(b, dict)):
        findings.append(_finding("missing_constraint_graph_block", "IR must include a ConstraintGraph block."))

    for edge in edges:
        if not isinstance(edge, dict):
            findings.append(_finding("malformed_edge", "Constraint edge is not an object."))
            continue
        if edge.get("type") not in {"chain_eq", "assert_eq", "neq"}:
            findings.append(_finding("unknown_edge_type", f"Unknown edge type: {edge.get('type')}"))
        if "source" not in edge or "target" not in edge:
            findings.append(_finding("edge_missing_endpoint", "Constraint edge is missing source or target."))

    findings.extend(_ordered_pair_collision(nodes, edges))

    if not _theta15_true():
        findings.append(_finding("theta15_failure", "Lo Shu Θ15 witness failed."))

    unique_nodes = len(set(nodes)) == len(nodes)
    if not unique_nodes:
        findings.append(_finding("duplicate_graph_nodes", "Constraint graph contains duplicate node entries."))

    details = {
        "source_len": len(source),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "ir_block_count": len(blocks),
        "theta15_true": _theta15_true(),
        "unique_nodes": unique_nodes,
    }
    status = StressStatus.PASSED if not findings else StressStatus.QUARANTINED
    receipt_hash = hash72_digest(("hhs_stress_receipt_v1", source_hash72, ast_hash72, graph_hash72, ir_hash72, status.value, [f.finding_hash72 for f in findings], details), width=24)
    receipt = StressReceipt(source_hash72, ast_hash72, graph_hash72, ir_hash72, status, [f.finding_hash72 for f in findings], details, receipt_hash)
    return StressResult(findings, receipt)


def main() -> None:
    demo = stress_validate_interpreter_artifacts(
        source="xy=-1/yx",
        source_hash72="H72-SOURCE",
        ast={"kind": "Program", "children": []},
        ast_hash72="H72-AST",
        graph={"nodes": ["xy", "-1/yx"], "edges": [{"type": "chain_eq", "source": "xy", "target": "-1/yx"}], "graph_hash72": "H72-GRAPH"},
        ir={"kind": "IRProgram", "blocks": [{"kind": "ConstraintGraph"}], "ir_hash72": "H72-IR"},
    )
    print(json.dumps(demo.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

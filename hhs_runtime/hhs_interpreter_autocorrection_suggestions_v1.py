"""
HHS Interpreter Auto-Correction Suggestions v1
==============================================

Compiler-side repair suggestion layer for interpreter stress findings.

Purpose
-------
Translate stress-harness findings into deterministic, reviewable symbolic
transformation suggestions.

This module does not edit source automatically, write files, execute generated
code, or mutate runtime state. It emits suggestion packets that can be displayed
in the CalculatorPanel, routed into the training loop, or manually applied by a
user/compiler pass.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


class CorrectionKind(str, Enum):
    ADD_CONSTRAINT_GRAPH_BLOCK = "ADD_CONSTRAINT_GRAPH_BLOCK"
    REPAIR_AST_ROOT = "REPAIR_AST_ROOT"
    ADD_MISSING_HASH = "ADD_MISSING_HASH"
    SPLIT_ORDERED_PRODUCTS = "SPLIT_ORDERED_PRODUCTS"
    DEDUPLICATE_GRAPH_NODES = "DEDUPLICATE_GRAPH_NODES"
    NORMALIZE_EDGE = "NORMALIZE_EDGE"
    HOLD_FOR_MANUAL_REVIEW = "HOLD_FOR_MANUAL_REVIEW"


class CorrectionPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class AutoCorrectionSuggestion:
    kind: CorrectionKind
    priority: CorrectionPriority
    finding_kind: str
    message: str
    proposed_transform: Dict[str, Any]
    applies_to: List[str]
    safe_to_auto_apply: bool
    suggestion_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        data["priority"] = self.priority.value
        return data


@dataclass(frozen=True)
class AutoCorrectionReceipt:
    source_hash72: str
    stress_receipt_hash72: str
    suggestions: List[AutoCorrectionSuggestion]
    summary_hash72: str
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_hash72": self.source_hash72,
            "stress_receipt_hash72": self.stress_receipt_hash72,
            "suggestions": [s.to_dict() for s in self.suggestions],
            "summary_hash72": self.summary_hash72,
            "status": self.status,
        }


def _mk(
    *,
    source_hash72: str,
    stress_hash72: str,
    finding_kind: str,
    message: str,
    kind: CorrectionKind,
    priority: CorrectionPriority,
    proposed_transform: Dict[str, Any],
    applies_to: Sequence[str],
    safe_to_auto_apply: bool = False,
) -> AutoCorrectionSuggestion:
    h = hash72_digest(
        (
            "interpreter_autocorrection_suggestion_v1",
            source_hash72,
            stress_hash72,
            finding_kind,
            message,
            kind.value,
            priority.value,
            proposed_transform,
            list(applies_to),
            safe_to_auto_apply,
        ),
        width=24,
    )
    return AutoCorrectionSuggestion(kind, priority, finding_kind, message, proposed_transform, list(applies_to), safe_to_auto_apply, h)


def suggestion_for_finding(finding: Dict[str, Any], *, source_hash72: str, stress_receipt_hash72: str) -> AutoCorrectionSuggestion:
    kind = str(finding.get("kind", "unknown"))
    message = str(finding.get("message", ""))

    if kind == "missing_constraint_graph_block":
        return _mk(
            source_hash72=source_hash72,
            stress_hash72=stress_receipt_hash72,
            finding_kind=kind,
            message=message,
            kind=CorrectionKind.ADD_CONSTRAINT_GRAPH_BLOCK,
            priority=CorrectionPriority.CRITICAL,
            proposed_transform={
                "target": "IRProgram.blocks",
                "operation": "prepend_block",
                "block": {"kind": "ConstraintGraph", "effect": "PURE", "payload_ref": "graph"},
            },
            applies_to=["IR"],
            safe_to_auto_apply=False,
        )

    if kind == "invalid_ast_root":
        return _mk(
            source_hash72=source_hash72,
            stress_hash72=stress_receipt_hash72,
            finding_kind=kind,
            message=message,
            kind=CorrectionKind.REPAIR_AST_ROOT,
            priority=CorrectionPriority.CRITICAL,
            proposed_transform={
                "target": "AST.root",
                "operation": "wrap_as_program",
                "required_root_kind": "Program",
            },
            applies_to=["AST"],
            safe_to_auto_apply=False,
        )

    if kind in {"missing_source_hash", "missing_ast_hash", "missing_graph_hash", "missing_ir_hash"}:
        return _mk(
            source_hash72=source_hash72,
            stress_hash72=stress_receipt_hash72,
            finding_kind=kind,
            message=message,
            kind=CorrectionKind.ADD_MISSING_HASH,
            priority=CorrectionPriority.HIGH,
            proposed_transform={
                "target": "receipt.preimage",
                "operation": "recompute_missing_hash_from_canonical_payload",
                "hash_family": "hash72_digest",
            },
            applies_to=["RECEIPT"],
            safe_to_auto_apply=False,
        )

    if kind == "ordered_product_collision":
        return _mk(
            source_hash72=source_hash72,
            stress_hash72=stress_receipt_hash72,
            finding_kind=kind,
            message=message,
            kind=CorrectionKind.SPLIT_ORDERED_PRODUCTS,
            priority=CorrectionPriority.CRITICAL,
            proposed_transform={
                "target": "ConstraintGraph.edges",
                "operation": "replace_illegal_eq_with_distinct_constraint_or_projection_gate",
                "rule": "xy and yx must remain separate ordered-product nodes unless an explicit projection rule exists",
            },
            applies_to=["GRAPH", "IR"],
            safe_to_auto_apply=False,
        )

    if kind == "duplicate_graph_nodes":
        return _mk(
            source_hash72=source_hash72,
            stress_hash72=stress_receipt_hash72,
            finding_kind=kind,
            message=message,
            kind=CorrectionKind.DEDUPLICATE_GRAPH_NODES,
            priority=CorrectionPriority.MEDIUM,
            proposed_transform={
                "target": "ConstraintGraph.nodes",
                "operation": "stable_deduplicate_preserve_order",
            },
            applies_to=["GRAPH"],
            safe_to_auto_apply=False,
        )

    if kind in {"unknown_edge_type", "edge_missing_endpoint", "malformed_edge"}:
        return _mk(
            source_hash72=source_hash72,
            stress_hash72=stress_receipt_hash72,
            finding_kind=kind,
            message=message,
            kind=CorrectionKind.NORMALIZE_EDGE,
            priority=CorrectionPriority.HIGH,
            proposed_transform={
                "target": "ConstraintGraph.edges",
                "operation": "normalize_or_quarantine_edge",
                "allowed_edge_types": ["chain_eq", "assert_eq", "neq"],
            },
            applies_to=["GRAPH"],
            safe_to_auto_apply=False,
        )

    return _mk(
        source_hash72=source_hash72,
        stress_hash72=stress_receipt_hash72,
        finding_kind=kind,
        message=message,
        kind=CorrectionKind.HOLD_FOR_MANUAL_REVIEW,
        priority=CorrectionPriority.LOW,
        proposed_transform={
            "target": "UNKNOWN",
            "operation": "manual_review_required",
            "reason": message,
        },
        applies_to=["UNKNOWN"],
        safe_to_auto_apply=False,
    )


def build_autocorrection_suggestions(stress_result: Dict[str, Any], *, source_hash72: str | None = None) -> AutoCorrectionReceipt:
    receipt = stress_result.get("receipt", {}) if isinstance(stress_result, dict) else {}
    findings = stress_result.get("findings", []) if isinstance(stress_result, dict) else []
    src_hash = str(source_hash72 or receipt.get("source_hash72") or "")
    stress_hash = str(receipt.get("receipt_hash72") or "")
    suggestions = [suggestion_for_finding(f, source_hash72=src_hash, stress_receipt_hash72=stress_hash) for f in findings if isinstance(f, dict)]
    status = "CLEAR" if not suggestions else "SUGGESTIONS_AVAILABLE"
    summary = hash72_digest(("interpreter_autocorrection_receipt_v1", src_hash, stress_hash, [s.suggestion_hash72 for s in suggestions], status), width=24)
    return AutoCorrectionReceipt(src_hash, stress_hash, suggestions, summary, status)


def suggestions_to_training_feedback(receipt: AutoCorrectionReceipt) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for suggestion in receipt.suggestions:
        out.append({
            "summary_hash72": suggestion.suggestion_hash72,
            "phases": [sum(ord(ch) for ch in suggestion.suggestion_hash72) % 72],
            "status": "HELD",
            "score": 70 if suggestion.priority in {CorrectionPriority.LOW, CorrectionPriority.MEDIUM} else 85,
            "operator_kind": "INTERPRETER_AUTOCORRECTION_SUGGESTION",
            "finding_kind": suggestion.finding_kind,
            "correction_kind": suggestion.kind.value,
            "safe_to_auto_apply": suggestion.safe_to_auto_apply,
        })
    return out


def main() -> None:
    demo = {
        "findings": [{"kind": "ordered_product_collision", "message": "Equality edge attempts to identify ordered products xy and yx."}],
        "receipt": {"source_hash72": "H72-SRC", "receipt_hash72": "H72-STRESS"},
    }
    print(json.dumps(build_autocorrection_suggestions(demo).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

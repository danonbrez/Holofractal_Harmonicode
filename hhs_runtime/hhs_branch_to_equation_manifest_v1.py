"""
HHS Branch to Equation Manifest v1
==================================

Interpreter/compiler processing layer for converting a selected phase-consistent
branch into a staged HARMONICODE equation artifact.

This module is side-effect free. It does not write files, change runtime state,
call external services, or perform repository actions. It produces a deterministic
manifest that can be consumed by the interpreter, IR generator, compiler, or
language-learning pipeline.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_phase_consistent_branch_selector_v1 import (
    BranchStatus,
    PhaseBranchSelectionReceipt,
    branch_selection_to_root_phases,
    select_phase_consistent_branch,
)
from hhs_runtime.harmonicode_root_execution_engine_v1 import extract_root_equation, stage_root_execution


class EquationManifestStatus(str, Enum):
    READY = "READY"
    HELD = "HELD"
    INVALID = "INVALID"


@dataclass(frozen=True)
class BranchEquationManifest:
    selection_receipt_hash72: str
    selected_branch_hash72: str | None
    phases: List[int]
    equation_text: str | None
    equation_hash72: str | None
    projection_receipt_hash72: str | None
    compiler_packet: Dict[str, Any] | None
    status: EquationManifestStatus
    reason: str
    manifest_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


def _compiler_packet(selection: PhaseBranchSelectionReceipt, staged: Dict[str, Any]) -> Dict[str, Any]:
    candidate = staged.get("candidate", {})
    equation = candidate.get("equation", {})
    packet = {
        "type": "BRANCH_EQUATION_COMPILER_PACKET",
        "selected_branch_hash72": selection.selected.branch_hash72 if selection.selected else None,
        "selection_receipt_hash72": selection.receipt_hash72,
        "phases": equation.get("phases", []),
        "equation_text": equation.get("equation"),
        "equation_hash72": equation.get("compression_hash72"),
        "projection_status": candidate.get("projection_status"),
        "projection_phase_index": candidate.get("phase_index"),
        "projection_receipt_hash72": candidate.get("projection_receipt_hash72"),
        "intended_consumers": [
            "harmonicode_interpreter_v1",
            "harmonicode_constraint_solver_v1",
            "harmonicode_transformation_engine_v1",
            "harmonicode_phase_projection_engine_v1",
            "harmonicode_ir_v1",
            "language_learning_feedback_loop",
        ],
    }
    return {**packet, "packet_hash72": hash72_digest(("branch_equation_compiler_packet_v1", packet), width=24)}


def bind_selection_to_equation_manifest(selection: PhaseBranchSelectionReceipt, *, target_layer: str = "normalized") -> BranchEquationManifest:
    if selection.status != BranchStatus.SELECTED or not selection.selected:
        reason = "No selected phase-consistent branch is available for equation extraction."
        h = hash72_digest(("branch_equation_manifest_v1", selection.receipt_hash72, None, [], None, None, None, None, EquationManifestStatus.HELD.value, reason), width=24)
        return BranchEquationManifest(selection.receipt_hash72, None, [], None, None, None, None, EquationManifestStatus.HELD, reason, h)

    phases = branch_selection_to_root_phases(selection)
    equation = extract_root_equation(phases)
    staged = stage_root_execution(phases, target_layer=target_layer)
    candidate = staged.get("candidate", {})
    projection_status = candidate.get("projection_status")
    staged_status = candidate.get("status")
    projection_hash = candidate.get("projection_receipt_hash72")

    if staged_status != "STAGED" or projection_status != "PROJECTED":
        reason = f"Equation extracted but projection validation did not pass: staged={staged_status}, projection={projection_status}."
        h = hash72_digest(("branch_equation_manifest_v1", selection.receipt_hash72, selection.selected.branch_hash72, phases, equation.equation, equation.compression_hash72, projection_hash, None, EquationManifestStatus.INVALID.value, reason), width=24)
        return BranchEquationManifest(selection.receipt_hash72, selection.selected.branch_hash72, phases, equation.equation, equation.compression_hash72, projection_hash, None, EquationManifestStatus.INVALID, reason, h)

    packet = _compiler_packet(selection, staged)
    reason = "Selected branch converted into a projection-validated HARMONICODE equation compiler packet."
    h = hash72_digest(("branch_equation_manifest_v1", selection.receipt_hash72, selection.selected.branch_hash72, phases, equation.equation, equation.compression_hash72, projection_hash, packet, EquationManifestStatus.READY.value, reason), width=24)
    return BranchEquationManifest(selection.receipt_hash72, selection.selected.branch_hash72, phases, equation.equation, equation.compression_hash72, projection_hash, packet, EquationManifestStatus.READY, reason, h)


def select_and_bind_equation_manifest(seed: str, *, cycles: int = 1, feedback_records: Sequence[Dict[str, Any]] | None = None, windows: int = 72, target_layer: str = "normalized") -> Dict[str, Any]:
    selection = select_phase_consistent_branch(seed, cycles=cycles, feedback_records=feedback_records, windows=windows)
    manifest = bind_selection_to_equation_manifest(selection, target_layer=target_layer)
    aggregate = hash72_digest(("select_and_bind_equation_manifest_v1", selection.receipt_hash72, manifest.manifest_hash72), width=24)
    return {"selection": selection.to_dict(), "manifest": manifest.to_dict(), "aggregate_hash72": aggregate}


def manifest_to_linguistic_feedback(manifest: BranchEquationManifest) -> Dict[str, Any]:
    return {
        "summary_hash72": manifest.manifest_hash72,
        "phases": manifest.phases,
        "status": "STAGED" if manifest.status == EquationManifestStatus.READY else "HELD" if manifest.status == EquationManifestStatus.HELD else "QUARANTINED",
        "score": 98 if manifest.status == EquationManifestStatus.READY else 60 if manifest.status == EquationManifestStatus.HELD else 0,
        "operator_kind": "BRANCH_TO_HARMONICODE_EQUATION",
        "equation_hash72": manifest.equation_hash72,
    }


def main() -> None:
    print(json.dumps(select_and_bind_equation_manifest("HHS_BRANCH_EQUATION", windows=9), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

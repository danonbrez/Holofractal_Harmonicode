"""
HHS Correction Simulation Overlay v1
====================================

Review-only simulation layer for interpreter auto-correction suggestions.

Purpose
-------
Convert correction suggestion packets into virtual phase branches and predicted
compiler/interpreter outcomes. This is a visualization and decision-support
artifact only.

It does not apply fixes, mutate source, write files, call subprocesses, compile
binaries, or change runtime state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


class SimulationStatus(str, Enum):
    SIMULATED = "SIMULATED"
    HELD = "HELD"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class CorrectionSimulation:
    suggestion_hash72: str
    correction_kind: str
    priority: str
    current_phase: int
    projected_phases: List[int]
    predicted_status: str
    predicted_score: int
    preview_equation_delta: str
    simulation_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CorrectionSimulationOverlay:
    source_hash72: str
    simulations: List[CorrectionSimulation]
    status: SimulationStatus
    overlay_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


def _phase_from_hash(h: str) -> int:
    return sum(ord(ch) for ch in str(h)) % 72


def _kind_stride(kind: str) -> int:
    return {
        "ADD_CONSTRAINT_GRAPH_BLOCK": 3,
        "REPAIR_AST_ROOT": 6,
        "ADD_MISSING_HASH": 9,
        "SPLIT_ORDERED_PRODUCTS": 12,
        "DEDUPLICATE_GRAPH_NODES": 15,
        "NORMALIZE_EDGE": 18,
        "HOLD_FOR_MANUAL_REVIEW": 21,
    }.get(kind, 5)


def _priority_score(priority: str) -> int:
    return {"CRITICAL": 96, "HIGH": 88, "MEDIUM": 74, "LOW": 60}.get(priority, 50)


def _preview_delta(suggestion: Dict[str, Any]) -> str:
    kind = str(suggestion.get("kind", "UNKNOWN"))
    transform = suggestion.get("proposed_transform", {}) if isinstance(suggestion.get("proposed_transform"), dict) else {}
    operation = transform.get("operation", "review")
    target = transform.get("target", "symbolic_artifact")
    if kind == "SPLIT_ORDERED_PRODUCTS":
        return "replace illegal ordered-product equality with distinct constraint or explicit projection gate"
    if kind == "ADD_CONSTRAINT_GRAPH_BLOCK":
        return "add ConstraintGraph IR block before downstream solver/transpiler passes"
    if kind == "REPAIR_AST_ROOT":
        return "wrap parsed artifact in Program root before IR lowering"
    return f"{operation} on {target}"


def simulate_correction_suggestion(suggestion: Dict[str, Any], *, source_hash72: str = "") -> CorrectionSimulation:
    suggestion_hash = str(suggestion.get("suggestion_hash72", ""))
    kind = str(suggestion.get("kind", "UNKNOWN"))
    priority = str(suggestion.get("priority", "LOW"))
    base = _phase_from_hash(suggestion_hash or source_hash72 or kind)
    stride = _kind_stride(kind)
    projected = [base, (base + stride) % 72, (base + stride * 2) % 72, (base + stride * 3) % 72]
    score = _priority_score(priority)
    predicted_status = "REVIEW_REQUIRED" if not suggestion.get("safe_to_auto_apply", False) else "SAFE_CANDIDATE"
    delta = _preview_delta(suggestion)
    h = hash72_digest(("correction_simulation_v1", source_hash72, suggestion_hash, kind, priority, projected, predicted_status, score, delta), width=24)
    return CorrectionSimulation(suggestion_hash, kind, priority, base, projected, predicted_status, score, delta, h)


def build_correction_simulation_overlay(autocorrections: Dict[str, Any], *, source_hash72: str | None = None) -> CorrectionSimulationOverlay:
    src = str(source_hash72 or autocorrections.get("source_hash72") or "")
    suggestions = autocorrections.get("suggestions", []) if isinstance(autocorrections, dict) else []
    simulations = [simulate_correction_suggestion(s, source_hash72=src) for s in suggestions if isinstance(s, dict)]
    status = SimulationStatus.SIMULATED if simulations else SimulationStatus.HELD
    overlay_hash = hash72_digest(("correction_simulation_overlay_v1", src, [s.simulation_hash72 for s in simulations], status.value), width=24)
    return CorrectionSimulationOverlay(src, simulations, status, overlay_hash)


def overlay_to_training_feedback(overlay: CorrectionSimulationOverlay) -> List[Dict[str, Any]]:
    return [
        {
            "summary_hash72": sim.simulation_hash72,
            "phases": sim.projected_phases,
            "status": "HELD",
            "score": sim.predicted_score,
            "operator_kind": "CORRECTION_SIMULATION_OVERLAY",
            "correction_kind": sim.correction_kind,
            "predicted_status": sim.predicted_status,
        }
        for sim in overlay.simulations
    ]


def main() -> None:
    demo = {
        "source_hash72": "H72-SRC",
        "suggestions": [
            {"kind": "SPLIT_ORDERED_PRODUCTS", "priority": "CRITICAL", "suggestion_hash72": "H72-SUGG", "safe_to_auto_apply": False, "proposed_transform": {"operation": "replace", "target": "ConstraintGraph.edges"}}
        ],
    }
    print(json.dumps(build_correction_simulation_overlay(demo).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

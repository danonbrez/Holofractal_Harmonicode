"""
HHS Correction Branch Competition v1
====================================

Ranks and prunes correction simulation futures.

Purpose
-------
Take a correction simulation overlay and produce a stable, reviewable branch
frontier for GUI rendering and language-learning feedback.

This module is side-effect free. It does not apply corrections, mutate source,
write files, execute code, or change runtime state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


class BranchCompetitionStatus(str, Enum):
    READY = "READY"
    HELD = "HELD"


@dataclass(frozen=True)
class CorrectionBranch:
    branch_id: str
    suggestion_hash72: str
    correction_kind: str
    priority: str
    projected_phases: List[int]
    predicted_status: str
    predicted_score: int
    compression_score: int
    stability_score: int
    emergence_score: int
    total_score: int
    retained: bool
    branch_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CorrectionBranchFrontier:
    source_hash72: str
    selected_branch_hash72: str | None
    branches: List[CorrectionBranch]
    pruned: List[CorrectionBranch]
    status: BranchCompetitionStatus
    frontier_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


def _mod72(n: int) -> int:
    return ((int(n) % 72) + 72) % 72


def _circular_distance(a: int, b: int) -> int:
    d = abs(_mod72(a) - _mod72(b))
    return min(d, 72 - d)


def _compression_score(phases: List[int]) -> int:
    unique = len(set(_mod72(p) for p in phases)) or 1
    return max(0, int(100 - (unique / max(len(phases), 1)) * 35))


def _stability_score(phases: List[int]) -> int:
    if len(phases) < 2:
        return 50
    hops = [_circular_distance(a, b) for a, b in zip(phases, phases[1:])]
    avg = sum(hops) / len(hops)
    return max(0, min(100, int(100 - avg * 4)))


def _emergence_score(phases: List[int]) -> int:
    cells = len(set((_mod72(p) % 9, _mod72(p) // 9) for p in phases))
    rings = len(set(_mod72(p) // 9 for p in phases))
    spokes = len(set(_mod72(p) % 9 for p in phases))
    return min(100, cells * 8 + rings * 5 + spokes * 3)


def _priority_bonus(priority: str) -> int:
    return {"CRITICAL": 18, "HIGH": 12, "MEDIUM": 6, "LOW": 0}.get(priority, 0)


def build_branch_from_simulation(sim: Dict[str, Any], *, index: int, retain_threshold: int = 62) -> CorrectionBranch:
    phases = [_mod72(int(p)) for p in sim.get("projected_phases", [])]
    predicted_score = int(sim.get("predicted_score", 0))
    compression = _compression_score(phases)
    stability = _stability_score(phases)
    emergence = _emergence_score(phases)
    priority = str(sim.get("priority", "LOW"))
    total = min(100, int(predicted_score * 0.38 + stability * 0.24 + emergence * 0.22 + compression * 0.16 + _priority_bonus(priority)))
    retained = total >= retain_threshold
    suggestion_hash = str(sim.get("suggestion_hash72", ""))
    branch_id = f"correction_branch_{index}_{suggestion_hash[:12]}"
    h = hash72_digest(("correction_branch_v1", branch_id, sim, phases, predicted_score, compression, stability, emergence, total, retained), width=24)
    return CorrectionBranch(
        branch_id=branch_id,
        suggestion_hash72=suggestion_hash,
        correction_kind=str(sim.get("correction_kind", "UNKNOWN")),
        priority=priority,
        projected_phases=phases,
        predicted_status=str(sim.get("predicted_status", "UNKNOWN")),
        predicted_score=predicted_score,
        compression_score=compression,
        stability_score=stability,
        emergence_score=emergence,
        total_score=total,
        retained=retained,
        branch_hash72=h,
    )


def compete_correction_branches(simulation_overlay: Dict[str, Any], *, max_retained: int = 6, retain_threshold: int = 62) -> CorrectionBranchFrontier:
    source_hash = str(simulation_overlay.get("source_hash72", ""))
    simulations = simulation_overlay.get("simulations", []) if isinstance(simulation_overlay, dict) else []
    branches = [build_branch_from_simulation(s, index=i, retain_threshold=retain_threshold) for i, s in enumerate(simulations) if isinstance(s, dict)]
    branches_sorted = sorted(branches, key=lambda b: b.total_score, reverse=True)
    retained = [b for b in branches_sorted if b.retained][:max_retained]
    retained_hashes = {b.branch_hash72 for b in retained}
    pruned = [b for b in branches_sorted if b.branch_hash72 not in retained_hashes]
    selected = retained[0].branch_hash72 if retained else None
    status = BranchCompetitionStatus.READY if retained else BranchCompetitionStatus.HELD
    frontier_hash = hash72_digest(("correction_branch_frontier_v1", source_hash, selected, [b.branch_hash72 for b in retained], [b.branch_hash72 for b in pruned], status.value), width=24)
    return CorrectionBranchFrontier(source_hash, selected, retained, pruned, status, frontier_hash)


def branch_frontier_to_training_feedback(frontier: CorrectionBranchFrontier) -> List[Dict[str, Any]]:
    feedback: List[Dict[str, Any]] = []
    for b in frontier.branches:
        feedback.append({
            "summary_hash72": b.branch_hash72,
            "phases": b.projected_phases,
            "status": "STAGED" if b.branch_hash72 == frontier.selected_branch_hash72 else "HELD",
            "score": b.total_score,
            "operator_kind": "CORRECTION_BRANCH_COMPETITION",
            "correction_kind": b.correction_kind,
            "predicted_status": b.predicted_status,
        })
    for b in frontier.pruned:
        feedback.append({
            "summary_hash72": b.branch_hash72,
            "phases": b.projected_phases,
            "status": "QUARANTINED",
            "score": b.total_score,
            "operator_kind": "CORRECTION_BRANCH_PRUNED",
            "correction_kind": b.correction_kind,
            "predicted_status": b.predicted_status,
        })
    return feedback


def main() -> None:
    demo = {
        "source_hash72": "H72-SRC",
        "simulations": [
            {"suggestion_hash72": "H72-A", "correction_kind": "SPLIT_ORDERED_PRODUCTS", "priority": "CRITICAL", "projected_phases": [4, 16, 28, 40], "predicted_status": "REVIEW_REQUIRED", "predicted_score": 96},
            {"suggestion_hash72": "H72-B", "correction_kind": "HOLD_FOR_MANUAL_REVIEW", "priority": "LOW", "projected_phases": [1, 22, 43, 64], "predicted_status": "REVIEW_REQUIRED", "predicted_score": 60},
        ],
    }
    print(json.dumps(compete_correction_branches(demo).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

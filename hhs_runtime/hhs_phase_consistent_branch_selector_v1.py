"""
HHS Phase-Consistent Branch Selector v1
======================================

Fuses temporal shells (future exploration) with trinary u72 window reads
(current holographic structure) to select branches that are both generative and
phase-consistent.

Pipeline
--------
    adaptive temporal shells
    + trinary ring windows
    -> candidate branch generation
    -> shell coverage scoring
    -> trinary window agreement scoring
    -> compression / emergence scoring
    -> root branch candidate receipt

This module does not commit state. It produces deterministic branch-selection
receipts that can feed Root Execution + Multi-Agent Consensus + Commit Pipeline.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_entangled_reciprocal_seesaw_temporal_shell_v1 import generate_temporal_shells, TemporalShellRun
from hhs_runtime.hhs_trinary_u72_window_reader_v1 import read_trinary_ring, TrinaryRingReadReceipt


Z72 = 72


class BranchStatus(str, Enum):
    SELECTED = "SELECTED"
    HELD = "HELD"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class PhaseBranchCandidate:
    branch_id: str
    phases: List[int]
    shell_coverage_score: int
    trinary_agreement_score: int
    compression_score: int
    emergence_score: int
    total_score: int
    branch_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseBranchSelectionReceipt:
    seed_hash72: str
    shell_receipt_hash72: str
    trinary_receipt_hash72: str
    candidates: List[PhaseBranchCandidate]
    selected: PhaseBranchCandidate | None
    status: BranchStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed_hash72": self.seed_hash72,
            "shell_receipt_hash72": self.shell_receipt_hash72,
            "trinary_receipt_hash72": self.trinary_receipt_hash72,
            "candidates": [c.to_dict() for c in self.candidates],
            "selected": self.selected.to_dict() if self.selected else None,
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
        }


def _mod72(value: int) -> int:
    return ((int(value) % Z72) + Z72) % Z72


def _unique(xs: Sequence[int]) -> List[int]:
    return sorted(set(_mod72(x) for x in xs))


def _coverage_score(branch: Sequence[int], shell_phases: Sequence[int]) -> int:
    b = set(_unique(branch))
    s = set(_unique(shell_phases))
    if not s:
        return 0
    return int((len(b & s) / len(s)) * 100)


def _trinary_agreement_score(branch: Sequence[int], trinary: TrinaryRingReadReceipt) -> int:
    branch_set = set(_unique(branch))
    if not trinary.reads:
        return 0
    hits = 0
    total = 0
    for read in trinary.reads:
        window = {read.previous.phase_index, read.self_cell.phase_index, read.next.phase_index}
        total += 3
        hits += len(branch_set & window)
    return int((hits / total) * 100) if total else 0


def _compression_score(branch: Sequence[int], all_phases: Sequence[int]) -> int:
    b = len(_unique(branch)) or 1
    universe = len(_unique(all_phases)) or 1
    return max(0, int((1 - (b / max(universe, b))) * 100))


def _emergence_score(branch: Sequence[int]) -> int:
    unique_cells = len(_unique(branch))
    major_cells = len(set(_mod72(p) % 9 for p in branch))
    minor_cells = len(set(_mod72(p) // 9 for p in branch))
    return min(100, unique_cells * 8 + major_cells * 4 + minor_cells * 4)


def _make_candidate(branch_id: str, phases: Sequence[int], shell_phases: Sequence[int], all_phases: Sequence[int], trinary: TrinaryRingReadReceipt) -> PhaseBranchCandidate:
    clean = [_mod72(p) for p in phases]
    shell_score = _coverage_score(clean, shell_phases)
    tri_score = _trinary_agreement_score(clean, trinary)
    comp_score = _compression_score(clean, all_phases)
    emer_score = _emergence_score(clean)
    total = int(shell_score * 0.25 + tri_score * 0.30 + comp_score * 0.20 + emer_score * 0.25)
    h = hash72_digest(("phase_branch_candidate_v1", branch_id, clean, shell_score, tri_score, comp_score, emer_score, total), width=24)
    return PhaseBranchCandidate(branch_id, clean, shell_score, tri_score, comp_score, emer_score, total, h)


def _generate_candidates(shells: TemporalShellRun, trinary: TrinaryRingReadReceipt, *, max_candidates: int = 12) -> List[List[int]]:
    shell_phases = [s.phase_index for s in shells.steps]
    window_phases: List[int] = []
    for r in trinary.reads:
        window_phases.extend([r.previous.phase_index, r.self_cell.phase_index, r.next.phase_index])

    candidates: List[List[int]] = []
    # Shell-stride candidates.
    for stride in [3, 6, 9, 12]:
        candidates.append(shell_phases[::stride][:12])
    # Trinary local-window candidates.
    for i in range(0, min(len(window_phases), 72), 9):
        candidates.append(window_phases[i:i + 9])
    # Fused shell/window candidates.
    for i in range(min(4, len(shell_phases))):
        fused = []
        for j in range(i, min(len(shell_phases), 36), 6):
            fused.append(shell_phases[j])
            if j < len(window_phases):
                fused.append(window_phases[j])
        candidates.append(fused[:12])
    # Keep non-empty unique signatures.
    seen = set()
    out: List[List[int]] = []
    for c in candidates:
        clean = [_mod72(x) for x in c if x is not None]
        if not clean:
            continue
        sig = tuple(clean)
        if sig in seen:
            continue
        seen.add(sig)
        out.append(clean)
        if len(out) >= max_candidates:
            break
    return out


def select_phase_consistent_branch(seed: str, *, cycles: int = 1, feedback_records: Sequence[Dict[str, Any]] | None = None, windows: int = 72) -> PhaseBranchSelectionReceipt:
    shells = generate_temporal_shells(seed, cycles=cycles, feedback_records=feedback_records)
    trinary = read_trinary_ring(shells.aggregate_hash72, windows=windows)
    seed_hash = hash72_digest(("phase_consistent_branch_selector_seed_v1", seed, cycles, windows), width=24)
    candidate_phase_lists = _generate_candidates(shells, trinary)
    shell_phases = [s.phase_index for s in shells.steps]
    trinary_phases: List[int] = []
    for r in trinary.reads:
        trinary_phases.extend([r.previous.phase_index, r.self_cell.phase_index, r.next.phase_index])
    all_phases = shell_phases + trinary_phases
    candidates = [_make_candidate(f"branch_{i}", phases, shell_phases, all_phases, trinary) for i, phases in enumerate(candidate_phase_lists)]
    candidates = sorted(candidates, key=lambda c: c.total_score, reverse=True)
    selected = candidates[0] if candidates else None
    status = BranchStatus.SELECTED if selected and shells.status.value == "LOCKED" and trinary.status.value == "LOCKED" else BranchStatus.HELD if selected else BranchStatus.QUARANTINED
    receipt_hash = hash72_digest(("phase_branch_selection_receipt_v1", seed_hash, shells.receipt_hash72, trinary.receipt_hash72, [c.branch_hash72 for c in candidates], selected.branch_hash72 if selected else None, status.value), width=24)
    return PhaseBranchSelectionReceipt(seed_hash, shells.receipt_hash72, trinary.receipt_hash72, candidates, selected, status, receipt_hash)


def branch_selection_to_root_phases(selection: PhaseBranchSelectionReceipt) -> List[int]:
    return selection.selected.phases if selection.selected else []


def branch_selection_to_training_feedback(selection: PhaseBranchSelectionReceipt) -> Dict[str, Any]:
    return {
        "summary_hash72": selection.receipt_hash72,
        "phases": branch_selection_to_root_phases(selection),
        "status": "STAGED" if selection.status == BranchStatus.SELECTED else "QUARANTINED",
        "score": selection.selected.total_score if selection.selected else 0,
        "operator_kind": "PHASE_CONSISTENT_BRANCH_SELECTION",
        "shell_receipt_hash72": selection.shell_receipt_hash72,
        "trinary_receipt_hash72": selection.trinary_receipt_hash72,
    }


def main() -> None:
    print(json.dumps(select_phase_consistent_branch("HHS_PHASE_SELECTOR", windows=9).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

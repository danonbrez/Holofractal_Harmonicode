"""
HHS Symbolic Memory Bias v1
===========================

Thin ranking adapter over HarmonicodeVerbatimSemanticDatabaseV1.

Purpose:
- query prior symbolic_candidate_selection records
- compare remembered token patterns to new symbolic substitution candidates
- compare remembered projected phase paths to new candidate phase paths
- return re-ranked candidates and feedback records

This does not create a new memory system. It uses the existing verbatim semantic
DB as the source of remembered user-selected symbolic paths.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
import json
import sqlite3

from harmonicode_verbatim_semantic_database_v1 import hash72_like
from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest

RING = 72


@dataclass(frozen=True)
class RememberedSelection:
    tokens: Set[str]
    phases: List[int]
    state_hash72: str


@dataclass(frozen=True)
class MemoryBiasCandidate:
    candidate_hash72: str
    original_score: int
    token_bonus: int
    phase_bonus: int
    memory_bonus: int
    biased_score: int
    overlap_tokens: List[str]
    phase_distance: int | None
    candidate_text: str
    phases: List[int]
    bias_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SymbolicMemoryBiasReceipt:
    db_path: str
    remembered_selection_count: int
    ranked_candidates: List[MemoryBiasCandidate]
    feedback_records: List[Dict[str, Any]]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "db_path": self.db_path,
            "remembered_selection_count": self.remembered_selection_count,
            "ranked_candidates": [c.to_dict() for c in self.ranked_candidates],
            "feedback_records": self.feedback_records,
            "receipt_hash72": self.receipt_hash72,
        }


def _tokens(text: str) -> Set[str]:
    return {t for t in str(text).replace("(", " ").replace(")", " ").replace(",", " ").split() if t}


def _as_phases(raw: Any) -> List[int]:
    if not isinstance(raw, list):
        return []
    phases: List[int] = []
    for item in raw:
        try:
            phases.append(int(item) % RING)
        except Exception:
            continue
    return phases


def _ring_distance(a: int, b: int) -> int:
    d = abs((int(a) % RING) - (int(b) % RING))
    return min(d, RING - d)


def _path_distance(left: List[int], right: List[int]) -> int | None:
    if not left or not right:
        return None
    n = min(len(left), len(right))
    if n <= 0:
        return None
    return sum(_ring_distance(left[i], right[i]) for i in range(n)) // n


def _phase_bonus(distance: int | None, max_phase_bonus: int) -> int:
    if distance is None:
        return 0
    return max(0, min(max_phase_bonus, max_phase_bonus - int(round(distance / 2))))


def _load_remembered_selections(db_path: str | Path) -> List[RememberedSelection]:
    path = Path(db_path)
    if not path.exists():
        return []
    conn = sqlite3.connect(str(path))
    try:
        rows = conn.execute(
            """
            SELECT state_hash72, token_sequence_json, metadata_json
            FROM state_records
            WHERE modality = 'symbolic_candidate_selection'
            ORDER BY created_at DESC
            LIMIT 512
            """
        ).fetchall()
    finally:
        conn.close()
    out: List[RememberedSelection] = []
    for state_hash, raw_tokens, raw_metadata in rows:
        try:
            seq = json.loads(raw_tokens)
            metadata = json.loads(raw_metadata)
            phases = _as_phases(metadata.get("projected_phases", []))
            out.append(RememberedSelection(tokens={str(x) for x in seq}, phases=phases, state_hash72=str(state_hash)))
        except Exception:
            continue
    return out


def apply_symbolic_memory_bias(
    substitution_receipt: Dict[str, Any],
    *,
    db_path: str | Path = "demo_reports/hhs_symbolic_selection_memory_v1.sqlite",
    max_token_bonus: int = 18,
    max_phase_bonus: int = 12,
) -> SymbolicMemoryBiasReceipt:
    remembered = _load_remembered_selections(db_path)
    candidates = substitution_receipt.get("candidates", []) or []
    ranked: List[MemoryBiasCandidate] = []

    for cand in candidates:
        text = str(cand.get("candidate_text", ""))
        cand_tokens = _tokens(text)
        cand_phases = _as_phases(cand.get("projected_phases", []))
        best_overlap: Set[str] = set()
        best_distance: int | None = None
        for mem in remembered:
            overlap = cand_tokens.intersection(mem.tokens)
            dist = _path_distance(cand_phases, mem.phases)
            better_overlap = len(overlap) > len(best_overlap)
            better_phase = dist is not None and (best_distance is None or dist < best_distance)
            if better_overlap or better_phase:
                if better_overlap:
                    best_overlap = overlap
                if better_phase:
                    best_distance = dist
        original = int(cand.get("score", 0) or 0)
        token_bonus = min(max_token_bonus, len(best_overlap) * 3)
        p_bonus = _phase_bonus(best_distance, max_phase_bonus)
        bonus = min(max_token_bonus + max_phase_bonus, token_bonus + p_bonus)
        biased = max(0, min(100, original + bonus))
        ch = str(cand.get("candidate_hash72") or hash72_like(cand))
        bh = hash72_digest(("hhs_symbolic_memory_bias_candidate_v2", ch, original, token_bonus, p_bonus, bonus, biased, sorted(best_overlap), best_distance, text, cand_phases), width=24)
        ranked.append(MemoryBiasCandidate(ch, original, token_bonus, p_bonus, bonus, biased, sorted(best_overlap), best_distance, text, cand_phases, bh))

    ranked = sorted(ranked, key=lambda c: c.biased_score, reverse=True)
    feedback = [
        {
            "summary_hash72": c.bias_hash72,
            "phases": c.phases,
            "carrier": "xy" if c.biased_score >= 85 else "y" if c.biased_score >= 65 else "yx",
            "status": "STAGED" if c.biased_score >= 65 else "HELD",
            "score": c.biased_score,
            "operator_kind": "SYMBOLIC_PHASE_MEMORY_BIAS",
            "candidate_hash72": c.candidate_hash72,
            "memory_bonus": c.memory_bonus,
            "token_bonus": c.token_bonus,
            "phase_bonus": c.phase_bonus,
            "phase_distance": c.phase_distance,
            "overlap_tokens": c.overlap_tokens,
            "candidate_text": c.candidate_text,
        }
        for c in ranked
    ]
    receipt_hash = hash72_digest(("hhs_symbolic_memory_bias_receipt_v2", str(db_path), len(remembered), [c.to_dict() for c in ranked], feedback), width=24)
    return SymbolicMemoryBiasReceipt(str(db_path), len(remembered), ranked, feedback, receipt_hash)


def main() -> None:
    demo = {"candidates": [{"candidate_text": "STATE(mnng) OP(mrgs)", "score": 80, "candidate_hash72": "DEMO", "projected_phases": [5, 17]}]}
    print(json.dumps(apply_symbolic_memory_bias(demo).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

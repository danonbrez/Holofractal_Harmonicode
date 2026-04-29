"""
HHS Symbolic Memory Bias v1
===========================

Thin ranking adapter over HarmonicodeVerbatimSemanticDatabaseV1.

Purpose:
- query prior symbolic_candidate_selection records
- compare remembered token patterns to new symbolic substitution candidates
- return re-ranked candidates and feedback records

This does not create a new memory system. It uses the existing verbatim semantic
DB as the source of remembered user-selected symbolic paths.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Set
import json
import sqlite3

from harmonicode_verbatim_semantic_database_v1 import HarmonicodeVerbatimSemanticDatabaseV1, hash72_like
from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


@dataclass(frozen=True)
class MemoryBiasCandidate:
    candidate_hash72: str
    original_score: int
    memory_bonus: int
    biased_score: int
    overlap_tokens: List[str]
    candidate_text: str
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


def _load_remembered_tokens(db_path: str | Path) -> List[Set[str]]:
    path = Path(db_path)
    if not path.exists():
        return []
    conn = sqlite3.connect(str(path))
    try:
        rows = conn.execute(
            """
            SELECT token_sequence_json
            FROM state_records
            WHERE modality = 'symbolic_candidate_selection'
            ORDER BY created_at DESC
            LIMIT 512
            """
        ).fetchall()
    finally:
        conn.close()
    out: List[Set[str]] = []
    for (raw,) in rows:
        try:
            seq = json.loads(raw)
            out.append({str(x) for x in seq})
        except Exception:
            continue
    return out


def apply_symbolic_memory_bias(
    substitution_receipt: Dict[str, Any],
    *,
    db_path: str | Path = "demo_reports/hhs_symbolic_selection_memory_v1.sqlite",
    max_bonus: int = 18,
) -> SymbolicMemoryBiasReceipt:
    remembered = _load_remembered_tokens(db_path)
    candidates = substitution_receipt.get("candidates", []) or []
    ranked: List[MemoryBiasCandidate] = []

    for cand in candidates:
        text = str(cand.get("candidate_text", ""))
        cand_tokens = _tokens(text)
        best_overlap: Set[str] = set()
        for mem in remembered:
            overlap = cand_tokens.intersection(mem)
            if len(overlap) > len(best_overlap):
                best_overlap = overlap
        original = int(cand.get("score", 0) or 0)
        bonus = min(max_bonus, len(best_overlap) * 3)
        biased = max(0, min(100, original + bonus))
        ch = str(cand.get("candidate_hash72") or hash72_like(cand))
        bh = hash72_digest(("hhs_symbolic_memory_bias_candidate_v1", ch, original, bonus, biased, sorted(best_overlap), text), width=24)
        ranked.append(MemoryBiasCandidate(ch, original, bonus, biased, sorted(best_overlap), text, bh))

    ranked = sorted(ranked, key=lambda c: c.biased_score, reverse=True)
    feedback = [
        {
            "summary_hash72": c.bias_hash72,
            "phases": [],
            "carrier": "xy" if c.biased_score >= 85 else "y" if c.biased_score >= 65 else "yx",
            "status": "STAGED" if c.biased_score >= 65 else "HELD",
            "score": c.biased_score,
            "operator_kind": "SYMBOLIC_MEMORY_BIAS",
            "candidate_hash72": c.candidate_hash72,
            "memory_bonus": c.memory_bonus,
            "overlap_tokens": c.overlap_tokens,
            "candidate_text": c.candidate_text,
        }
        for c in ranked
    ]
    receipt_hash = hash72_digest(("hhs_symbolic_memory_bias_receipt_v1", str(db_path), len(remembered), [c.to_dict() for c in ranked], feedback), width=24)
    return SymbolicMemoryBiasReceipt(str(db_path), len(remembered), ranked, feedback, receipt_hash)


def main() -> None:
    demo = {"candidates": [{"candidate_text": "STATE(mnng) OP(mrgs)", "score": 80, "candidate_hash72": "DEMO"}]}
    print(json.dumps(apply_symbolic_memory_bias(demo).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

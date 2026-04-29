"""
HHS Cross-Modal Semantic Coherence Scorer v1
===========================================

Computes a single coherence score from existing receipts:
- grammar enforcement receipt
- WordNet relation validation receipt
- audio round-trip receipt
- linguistic training receipt

This module does not replace any existing subsystem. It only normalizes their
receipts into one scoring envelope and training feedback payload.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


@dataclass(frozen=True)
class CoherenceComponent:
    name: str
    score: int
    weight: int
    status: str
    evidence: Dict[str, Any]
    component_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CrossModalCoherenceReceipt:
    components: List[CoherenceComponent]
    weighted_score: int
    status: str
    feedback_records: List[Dict[str, Any]]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "components": [c.to_dict() for c in self.components],
            "weighted_score": self.weighted_score,
            "status": self.status,
            "feedback_records": self.feedback_records,
            "receipt_hash72": self.receipt_hash72,
        }


def _clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def _component(name: str, score: int, weight: int, status: str, evidence: Dict[str, Any]) -> CoherenceComponent:
    h = hash72_digest(("hhs_coherence_component_v1", name, score, weight, status, evidence), width=18)
    return CoherenceComponent(name, _clamp_score(score), weight, status, evidence, h)


def score_grammar(grammar_receipt: Dict[str, Any] | None) -> CoherenceComponent:
    if not grammar_receipt:
        return _component("grammar", 100, 20, "NO_GRAMMAR_RECEIPT", {"applied_count": 0})
    applied = int(grammar_receipt.get("applied_count", 0) or 0)
    loaded = int(grammar_receipt.get("rules_loaded", 0) or 0)
    corrections = grammar_receipt.get("corrections", []) or []
    # A correction is useful, not a failure. Heavy repeated corrections lower stability.
    score = 100 if applied == 0 else max(70, 100 - applied * 4)
    return _component("grammar", score, 20, "GRAMMAR_NORMALIZED", {"applied_count": applied, "rules_loaded": loaded, "correction_count": len(corrections), "receipt_hash72": grammar_receipt.get("receipt_hash72")})


def score_wordnet(wordnet_receipt: Dict[str, Any] | None) -> CoherenceComponent:
    if not wordnet_receipt:
        return _component("wordnet", 50, 25, "NO_WORDNET_RECEIPT", {})
    known = int(wordnet_receipt.get("known_count", 0) or 0)
    unknown = int(wordnet_receipt.get("unknown_count", 0) or 0)
    total = max(1, known + unknown)
    feedback = wordnet_receipt.get("feedback_records", []) or []
    relation_scores = [float(f.get("score", 0) or 0) for f in feedback]
    relation_avg = sum(relation_scores) / max(1, len(relation_scores))
    coverage = (known / total) * 100
    score = coverage * 0.55 + relation_avg * 0.45
    status = "WORD_RELATIONS_SUPPORTED" if unknown == 0 else "WORD_RELATIONS_PARTIAL"
    return _component("wordnet", _clamp_score(score), 25, status, {"known_count": known, "unknown_count": unknown, "feedback_count": len(feedback), "receipt_hash72": wordnet_receipt.get("receipt_hash72")})


def score_audio(audio_receipt: Dict[str, Any] | None) -> CoherenceComponent:
    if not audio_receipt:
        return _component("audio_phase", 50, 30, "NO_AUDIO_RECEIPT", {})
    total = int(audio_receipt.get("total_items", 0) or 0)
    exact = int(audio_receipt.get("exact_matches", 0) or 0)
    max_err = int(audio_receipt.get("max_phase_error", 0) or 0)
    if total <= 0:
        score = 50
    else:
        match_score = (exact / total) * 100
        error_penalty = min(60, max_err * 8)
        score = match_score - error_penalty
    status = str(audio_receipt.get("status", "AUDIO_UNKNOWN"))
    return _component("audio_phase", _clamp_score(score), 30, status, {"exact_matches": exact, "total_items": total, "max_phase_error": max_err, "receipt_hash72": audio_receipt.get("receipt_hash72")})


def score_training(training_receipt: Dict[str, Any] | None) -> CoherenceComponent:
    if not training_receipt:
        return _component("training", 50, 25, "NO_TRAINING_RECEIPT", {})
    steps = training_receipt.get("steps", []) or []
    feedback = training_receipt.get("feedback_records", []) or []
    scores = []
    for step in steps:
        if isinstance(step, dict):
            scores.append(float(step.get("score", step.get("total_score", 0)) or 0))
    for item in feedback:
        if isinstance(item, dict):
            scores.append(float(item.get("score", 0) or 0))
    avg = sum(scores) / max(1, len(scores)) if scores else 75
    status = "TRAINING_FEEDBACK_AVAILABLE" if feedback or steps else "TRAINING_EMPTY"
    return _component("training", _clamp_score(avg), 25, status, {"step_count": len(steps), "feedback_count": len(feedback), "receipt_hash72": training_receipt.get("receipt_hash72")})


def build_cross_modal_coherence_receipt(
    *,
    grammar_receipt: Dict[str, Any] | None = None,
    wordnet_receipt: Dict[str, Any] | None = None,
    audio_roundtrip_receipt: Dict[str, Any] | None = None,
    linguistic_training_receipt: Dict[str, Any] | None = None,
) -> CrossModalCoherenceReceipt:
    components = [
        score_grammar(grammar_receipt),
        score_wordnet(wordnet_receipt),
        score_audio(audio_roundtrip_receipt),
        score_training(linguistic_training_receipt),
    ]
    total_weight = sum(c.weight for c in components) or 1
    weighted = _clamp_score(sum(c.score * c.weight for c in components) / total_weight)
    status = "COHERENT" if weighted >= 85 else "PARTIAL" if weighted >= 65 else "DRIFT"
    feedback_records = [
        {
            "summary_hash72": c.component_hash72,
            "phases": [],
            "carrier": "xy" if c.score >= 85 else "y" if c.score >= 65 else "yx",
            "status": "STAGED" if c.score >= 65 else "HELD",
            "score": c.score,
            "operator_kind": f"COHERENCE_{c.name.upper()}",
            "component_status": c.status,
            "weight": c.weight,
            "evidence": c.evidence,
        }
        for c in components
    ]
    receipt_hash = hash72_digest(("hhs_cross_modal_coherence_receipt_v1", [c.to_dict() for c in components], weighted, status, feedback_records), width=24)
    return CrossModalCoherenceReceipt(components, weighted, status, feedback_records, receipt_hash)


def main() -> None:
    import json
    receipt = build_cross_modal_coherence_receipt()
    print(json.dumps(receipt.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

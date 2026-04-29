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

Adaptive weighting
------------------
The scorer may receive prior component weights and will adjust them based on the
current component scores:
- weak components gain weight so the loop pays more attention to them
- stable components relax weight so the loop does not overfit solved channels
- total weight is conserved by normalization
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest

DEFAULT_WEIGHTS = {
    "grammar": 20,
    "wordnet": 25,
    "audio_phase": 30,
    "training": 25,
}

MIN_WEIGHT = 10
MAX_WEIGHT = 45
TARGET_TOTAL_WEIGHT = 100


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
class AdaptiveWeightUpdate:
    name: str
    previous_weight: int
    proposed_weight: int
    normalized_weight: int
    score: int
    reason: str
    update_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CrossModalCoherenceReceipt:
    components: List[CoherenceComponent]
    weighted_score: int
    status: str
    feedback_records: List[Dict[str, Any]]
    adaptive_weights: List[AdaptiveWeightUpdate]
    weight_profile_hash72: str
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "components": [c.to_dict() for c in self.components],
            "weighted_score": self.weighted_score,
            "status": self.status,
            "feedback_records": self.feedback_records,
            "adaptive_weights": [w.to_dict() for w in self.adaptive_weights],
            "weight_profile_hash72": self.weight_profile_hash72,
            "receipt_hash72": self.receipt_hash72,
        }


def _clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def _clamp_weight(value: float) -> int:
    return max(MIN_WEIGHT, min(MAX_WEIGHT, int(round(value))))


def _component(name: str, score: int, weight: int, status: str, evidence: Dict[str, Any]) -> CoherenceComponent:
    h = hash72_digest(("hhs_coherence_component_v1", name, score, weight, status, evidence), width=18)
    return CoherenceComponent(name, _clamp_score(score), weight, status, evidence, h)


def _prior_weight(name: str, prior_weights: Dict[str, int] | None) -> int:
    if prior_weights and name in prior_weights:
        return _clamp_weight(prior_weights[name])
    return DEFAULT_WEIGHTS[name]


def score_grammar(grammar_receipt: Dict[str, Any] | None, prior_weights: Dict[str, int] | None = None) -> CoherenceComponent:
    weight = _prior_weight("grammar", prior_weights)
    if not grammar_receipt:
        return _component("grammar", 100, weight, "NO_GRAMMAR_RECEIPT", {"applied_count": 0})
    applied = int(grammar_receipt.get("applied_count", 0) or 0)
    loaded = int(grammar_receipt.get("rules_loaded", 0) or 0)
    corrections = grammar_receipt.get("corrections", []) or []
    # A correction is useful, not a failure. Heavy repeated corrections lower stability.
    score = 100 if applied == 0 else max(70, 100 - applied * 4)
    return _component("grammar", score, weight, "GRAMMAR_NORMALIZED", {"applied_count": applied, "rules_loaded": loaded, "correction_count": len(corrections), "receipt_hash72": grammar_receipt.get("receipt_hash72")})


def score_wordnet(wordnet_receipt: Dict[str, Any] | None, prior_weights: Dict[str, int] | None = None) -> CoherenceComponent:
    weight = _prior_weight("wordnet", prior_weights)
    if not wordnet_receipt:
        return _component("wordnet", 50, weight, "NO_WORDNET_RECEIPT", {})
    known = int(wordnet_receipt.get("known_count", 0) or 0)
    unknown = int(wordnet_receipt.get("unknown_count", 0) or 0)
    total = max(1, known + unknown)
    feedback = wordnet_receipt.get("feedback_records", []) or []
    relation_scores = [float(f.get("score", 0) or 0) for f in feedback]
    relation_avg = sum(relation_scores) / max(1, len(relation_scores))
    coverage = (known / total) * 100
    score = coverage * 0.55 + relation_avg * 0.45
    status = "WORD_RELATIONS_SUPPORTED" if unknown == 0 else "WORD_RELATIONS_PARTIAL"
    return _component("wordnet", _clamp_score(score), weight, status, {"known_count": known, "unknown_count": unknown, "feedback_count": len(feedback), "receipt_hash72": wordnet_receipt.get("receipt_hash72")})


def score_audio(audio_receipt: Dict[str, Any] | None, prior_weights: Dict[str, int] | None = None) -> CoherenceComponent:
    weight = _prior_weight("audio_phase", prior_weights)
    if not audio_receipt:
        return _component("audio_phase", 50, weight, "NO_AUDIO_RECEIPT", {})
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
    return _component("audio_phase", _clamp_score(score), weight, status, {"exact_matches": exact, "total_items": total, "max_phase_error": max_err, "receipt_hash72": audio_receipt.get("receipt_hash72")})


def score_training(training_receipt: Dict[str, Any] | None, prior_weights: Dict[str, int] | None = None) -> CoherenceComponent:
    weight = _prior_weight("training", prior_weights)
    if not training_receipt:
        return _component("training", 50, weight, "NO_TRAINING_RECEIPT", {})
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
    return _component("training", _clamp_score(avg), weight, status, {"step_count": len(steps), "feedback_count": len(feedback), "receipt_hash72": training_receipt.get("receipt_hash72")})


def _reason_for_weight(score: int) -> str:
    if score < 65:
        return "weak_component_increase_attention"
    if score >= 92:
        return "stable_component_relax_attention"
    return "hold_attention"


def _propose_weight(previous: int, score: int) -> int:
    if score < 50:
        return _clamp_weight(previous + 8)
    if score < 65:
        return _clamp_weight(previous + 5)
    if score < 80:
        return _clamp_weight(previous + 2)
    if score >= 95:
        return _clamp_weight(previous - 4)
    if score >= 90:
        return _clamp_weight(previous - 2)
    return _clamp_weight(previous)


def _normalize_weight_updates(components: List[CoherenceComponent]) -> List[AdaptiveWeightUpdate]:
    proposed = [(c, _propose_weight(c.weight, c.score), _reason_for_weight(c.score)) for c in components]
    proposed_total = sum(p for _, p, _ in proposed) or 1
    updates: List[AdaptiveWeightUpdate] = []
    for component, proposed_weight, reason in proposed:
        normalized = _clamp_weight((proposed_weight / proposed_total) * TARGET_TOTAL_WEIGHT)
        h = hash72_digest(("hhs_adaptive_weight_update_v1", component.name, component.weight, proposed_weight, normalized, component.score, reason, component.component_hash72), width=18)
        updates.append(AdaptiveWeightUpdate(component.name, component.weight, proposed_weight, normalized, component.score, reason, h))

    # Preserve exact total weight by adjusting the strongest weak component or first component.
    delta = TARGET_TOTAL_WEIGHT - sum(u.normalized_weight for u in updates)
    if delta and updates:
        target_index = min(range(len(updates)), key=lambda i: updates[i].score)
        target = updates[target_index]
        corrected = max(MIN_WEIGHT, min(MAX_WEIGHT, target.normalized_weight + delta))
        h = hash72_digest(("hhs_adaptive_weight_update_v1_corrected", target.to_dict(), corrected, delta), width=18)
        updates[target_index] = AdaptiveWeightUpdate(target.name, target.previous_weight, target.proposed_weight, corrected, target.score, target.reason + "_total_corrected", h)
    return updates


def _component_with_weight(component: CoherenceComponent, weight: int) -> CoherenceComponent:
    return _component(component.name, component.score, weight, component.status, component.evidence)


def build_cross_modal_coherence_receipt(
    *,
    grammar_receipt: Dict[str, Any] | None = None,
    wordnet_receipt: Dict[str, Any] | None = None,
    audio_roundtrip_receipt: Dict[str, Any] | None = None,
    linguistic_training_receipt: Dict[str, Any] | None = None,
    prior_weights: Dict[str, int] | None = None,
    use_adaptive_weights_for_score: bool = True,
) -> CrossModalCoherenceReceipt:
    initial_components = [
        score_grammar(grammar_receipt, prior_weights),
        score_wordnet(wordnet_receipt, prior_weights),
        score_audio(audio_roundtrip_receipt, prior_weights),
        score_training(linguistic_training_receipt, prior_weights),
    ]
    adaptive_weights = _normalize_weight_updates(initial_components)
    adaptive_map = {w.name: w.normalized_weight for w in adaptive_weights}
    components = [_component_with_weight(c, adaptive_map[c.name]) for c in initial_components] if use_adaptive_weights_for_score else initial_components
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
            "adaptive_reason": next((w.reason for w in adaptive_weights if w.name == c.name), "none"),
            "evidence": c.evidence,
        }
        for c in components
    ]
    weight_profile_hash = hash72_digest(("hhs_adaptive_weight_profile_v1", [w.to_dict() for w in adaptive_weights]), width=24)
    receipt_hash = hash72_digest(("hhs_cross_modal_coherence_receipt_v1", [c.to_dict() for c in components], weighted, status, feedback_records, [w.to_dict() for w in adaptive_weights], weight_profile_hash), width=24)
    return CrossModalCoherenceReceipt(components, weighted, status, feedback_records, adaptive_weights, weight_profile_hash, receipt_hash)


def next_weight_profile(receipt: CrossModalCoherenceReceipt | Dict[str, Any]) -> Dict[str, int]:
    data = receipt.to_dict() if isinstance(receipt, CrossModalCoherenceReceipt) else receipt
    return {str(w["name"]): int(w["normalized_weight"]) for w in data.get("adaptive_weights", [])}


def main() -> None:
    import json
    receipt = build_cross_modal_coherence_receipt()
    print(json.dumps(receipt.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""
HHS Cross-Modal Action Planner v1
=================================

Bounded action planner over the cross-modal coherence receipt.

This module does not execute changes directly. It proposes reviewable actions for
existing subsystems:
- grammar weak -> run grammar enforcement / correction pass
- wordnet weak -> request relation expansion / synonym-hypernym support
- audio weak -> request audio phase re-encode / round-trip validation
- training weak -> request additional linguistic training loop cycle

All outputs are Hash72-addressed and suitable as feedback records.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


@dataclass(frozen=True)
class CrossModalAction:
    component: str
    action_kind: str
    priority: int
    reason: str
    target_status: str
    proposed_patch: Dict[str, Any]
    action_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CrossModalActionPlan:
    coherence_receipt_hash72: str | None
    coherence_status: str
    weighted_score: int
    actions: List[CrossModalAction]
    feedback_records: List[Dict[str, Any]]
    plan_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "coherence_receipt_hash72": self.coherence_receipt_hash72,
            "coherence_status": self.coherence_status,
            "weighted_score": self.weighted_score,
            "actions": [a.to_dict() for a in self.actions],
            "feedback_records": self.feedback_records,
            "plan_hash72": self.plan_hash72,
        }


def _priority(score: int, weight: int) -> int:
    weakness = max(0, 100 - int(score))
    return max(1, min(100, int(round(weakness * 0.7 + weight * 0.3))))


def _action_for_component(component: Dict[str, Any]) -> CrossModalAction | None:
    name = str(component.get("name", ""))
    score = int(component.get("score", 0) or 0)
    weight = int(component.get("weight", 0) or 0)
    status = str(component.get("status", "UNKNOWN"))
    evidence = component.get("evidence", {}) if isinstance(component.get("evidence", {}), dict) else {}

    if score >= 85:
        return None

    priority = _priority(score, weight)

    if name == "grammar":
        action_kind = "RUN_GRAMMAR_ENFORCEMENT"
        reason = "grammar_component_below_coherence_threshold"
        patch = {
            "op": "ENFORCE_GRAMMAR_RULES",
            "receipt_hash72": evidence.get("receipt_hash72"),
            "applied_count": evidence.get("applied_count", 0),
        }
    elif name == "wordnet":
        action_kind = "EXPAND_WORD_RELATIONS"
        reason = "wordnet_component_below_coherence_threshold"
        patch = {
            "op": "VALIDATE_WORDNET_RELATIONS",
            "receipt_hash72": evidence.get("receipt_hash72"),
            "unknown_count": evidence.get("unknown_count", 0),
            "known_count": evidence.get("known_count", 0),
        }
    elif name == "audio_phase":
        action_kind = "RELOCK_AUDIO_PHASE"
        reason = "audio_phase_component_below_coherence_threshold"
        patch = {
            "op": "REENCODE_AND_DECODE_AUDIO_PHASE",
            "receipt_hash72": evidence.get("receipt_hash72"),
            "max_phase_error": evidence.get("max_phase_error", 0),
            "exact_matches": evidence.get("exact_matches", 0),
            "total_items": evidence.get("total_items", 0),
        }
    elif name == "training":
        action_kind = "RUN_ADDITIONAL_TRAINING_CYCLE"
        reason = "training_component_below_coherence_threshold"
        patch = {
            "op": "RUN_LINGUISTIC_TRAINING_LOOP",
            "receipt_hash72": evidence.get("receipt_hash72"),
            "step_count": evidence.get("step_count", 0),
            "feedback_count": evidence.get("feedback_count", 0),
        }
    else:
        action_kind = "REVIEW_COMPONENT"
        reason = "unknown_component_below_threshold"
        patch = {"op": "REVIEW", "component": name, "evidence": evidence}

    h = hash72_digest(("hhs_cross_modal_action_v1", name, action_kind, priority, reason, status, patch, score, weight), width=24)
    return CrossModalAction(name, action_kind, priority, reason, status, patch, h)


def plan_cross_modal_actions(coherence_receipt: Dict[str, Any]) -> CrossModalActionPlan:
    components = coherence_receipt.get("components", []) or []
    actions = [a for a in (_action_for_component(c) for c in components if isinstance(c, dict)) if a is not None]
    actions = sorted(actions, key=lambda a: a.priority, reverse=True)

    feedback_records = [
        {
            "summary_hash72": action.action_hash72,
            "phases": [],
            "carrier": "yx" if action.priority >= 65 else "y",
            "status": "STAGED",
            "score": max(0, 100 - action.priority),
            "operator_kind": f"ACTION_{action.action_kind}",
            "component": action.component,
            "priority": action.priority,
            "reason": action.reason,
            "proposed_patch": action.proposed_patch,
        }
        for action in actions
    ]

    plan_hash = hash72_digest(("hhs_cross_modal_action_plan_v1", coherence_receipt.get("receipt_hash72"), coherence_receipt.get("status"), coherence_receipt.get("weighted_score"), [a.to_dict() for a in actions], feedback_records), width=24)
    return CrossModalActionPlan(
        coherence_receipt_hash72=coherence_receipt.get("receipt_hash72"),
        coherence_status=str(coherence_receipt.get("status", "UNKNOWN")),
        weighted_score=int(coherence_receipt.get("weighted_score", 0) or 0),
        actions=actions,
        feedback_records=feedback_records,
        plan_hash72=plan_hash,
    )


def main() -> None:
    import json
    demo = {
        "receipt_hash72": "DEMO",
        "status": "PARTIAL",
        "weighted_score": 72,
        "components": [
            {"name": "grammar", "score": 92, "weight": 18, "status": "OK", "evidence": {}},
            {"name": "audio_phase", "score": 51, "weight": 38, "status": "ROUND_TRIP_DRIFT", "evidence": {"max_phase_error": 4}},
        ],
    }
    print(json.dumps(plan_cross_modal_actions(demo).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

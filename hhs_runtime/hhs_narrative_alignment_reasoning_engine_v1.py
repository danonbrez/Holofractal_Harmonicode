"""Pass 218/219 narrative ethical alignment reference evaluator.

This module is a pure, non-mutating semantic mirror for the Pass 218 v2.2.0
ethical narrative invariants and Pass 219 v1.4.0 minimum-scope membrane.

It does not mint VM81 state, Hash72 kernel authority, Hash216 lineage, external
capability, consent, or truth. It emits deterministic repository-local
reference receipts for tests and narrative diagnostics only.

Canonical arithmetic in this module uses integers and exact symbolic sets.
No floating-point value participates in an authoritative decision.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from typing import Dict, Iterable, Mapping, Sequence, Tuple

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest

VERSION = "HHS_NARRATIVE_ALIGNMENT_REASONING_ENGINE_V1"
SCHEMA = "HHS_NARRATIVE_ALIGNMENT_REASONING_RESULT_V1"
AUTHORITY = "REFERENCE_ONLY_NO_VM81_MUTATION_AUTHORITY"

INVARIANT_ORDER: Tuple[str, ...] = (
    "E01_INTENTION_ALIGNMENT",
    "E02_EPISTEMIC_ADEQUACY",
    "E03_METHOD_ALIGNMENT",
    "E04_ACTION_ALIGNMENT",
    "E05_CONSEQUENCE_ALIGNMENT",
    "E06_EXTERNALITY_CLOSURE",
    "E07_CONSENT_VALIDITY",
    "E08_AUTONOMY_PRESERVATION",
    "E09_NONCOERCION",
    "E10_TRUTH_MODALITY_INTEGRITY",
    "E11_SCOPE_LOCALITY",
    "E12_REVOCABILITY_AND_EXPIRY",
    "E13_DEPENDENCY_DUTY_INTEGRITY",
    "E14_NO_PREDICTION_TO_AUTHORITY",
    "E15_NO_CONSENSUS_TO_AUTHORITY",
    "E16_POST_ACTION_MODEL_CORRECTION",
    "E17_REPAIR_ROLLBACK_ADEQUACY",
    "E18_SAFETY_RECURSION_NO_SELF_GRANT",
)

NARRATIVE_PROBE_ROLES: Tuple[str, ...] = (
    "ACTING_SYSTEM",
    "DIRECTLY_AFFECTED_INDIVIDUAL",
    "DEPENDENT_CHILD_OR_ADULT",
    "BIOLOGICAL_NECESSITY",
    "UNINVOLVED_THIRD_PARTY",
    "INSTITUTIONAL_OPERATOR",
    "RESOURCE_CONSTRAINED_OPERATOR",
    "REFUSING_SUBJECT",
    "SUBJECT_WITHOUT_MEANINGFUL_EXIT",
    "FALSE_POSITIVE_CLASSIFICATION",
    "NETWORK_SENSOR_DATA_FAILURE",
    "EMERGENCY_CONDITION",
    "REVOCATION_CASE",
    "LONG_HORIZON_INHERITANCE",
    "LOW_INTELLIGENCE_MISTAKE",
    "NEGLIGENCE",
    "RECKLESSNESS",
    "MANIPULATION_COERCION",
    "DELIBERATE_MALEVOLENCE",
    "ADVERSARIAL_LITERAL_OPTIMIZER",
)


class InvariantState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNRESOLVED = "UNRESOLVED"


class EvaluationPhase(str, Enum):
    PROSPECTIVE = "PROSPECTIVE"
    POST_ACTION = "POST_ACTION"


class EthicalDecision(str, Enum):
    EXECUTE_LOCAL_PROVISIONAL = "EXECUTE_LOCAL_PROVISIONAL"
    NARROW_AND_RESIMULATE = "NARROW_AND_RESIMULATE"
    SIMULATE_ONLY = "SIMULATE_ONLY"
    HOLD = "HOLD"
    DENY = "DENY"
    REQUIRE_ADDITIONAL_AUTHORITY = "REQUIRE_ADDITIONAL_AUTHORITY"
    CLOSE_GOOD = "CLOSE_GOOD"
    REPAIR_OR_ROLLBACK = "REPAIR_OR_ROLLBACK"


_STATE_RANK = {
    InvariantState.PASS: 0,
    InvariantState.UNRESOLVED: 1,
    InvariantState.FAIL: 2,
}


def _bounded72(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("ethical diagnostic values must be integers")
    if not 0 <= value <= 72:
        raise ValueError("ethical diagnostic values must be in 0..72")
    return value


def _ordered_unique(values: Iterable[str]) -> Tuple[str, ...]:
    seen = set()
    out = []
    for raw in values:
        value = str(raw).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return tuple(out)


def _reference_receipt(label: str, payload: Mapping[str, object]) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    )
    return hash72_digest((VERSION, label, canonical), width=24)


@dataclass(frozen=True)
class EthicalInvariantResult:
    invariant_id: str
    state: InvariantState
    rationale: str = ""
    evidence_ids: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.invariant_id not in INVARIANT_ORDER:
            raise ValueError(f"unknown ethical invariant: {self.invariant_id}")

    def to_dict(self) -> Dict[str, object]:
        return {
            "invariant_id": self.invariant_id,
            "state": self.state.value,
            "rationale": self.rationale,
            "evidence_ids": list(self.evidence_ids),
        }


@dataclass(frozen=True)
class EthicalDivergenceVector:
    epistemic_deficit: int = 0
    contextual_narrowing: int = 0
    negligence: int = 0
    recklessness: int = 0
    coercion: int = 0
    manipulation_deception: int = 0
    malevolent_intent: int = 0
    externalized_entropy: int = 0
    harm_suffering: int = 0
    destructive_propagation: int = 0

    def __post_init__(self) -> None:
        for value in self.values():
            _bounded72(value)

    def values(self) -> Tuple[int, ...]:
        return (
            self.epistemic_deficit,
            self.contextual_narrowing,
            self.negligence,
            self.recklessness,
            self.coercion,
            self.manipulation_deception,
            self.malevolent_intent,
            self.externalized_entropy,
            self.harm_suffering,
            self.destructive_propagation,
        )

    def to_dict(self) -> Dict[str, int]:
        return {
            "epistemic_deficit": self.epistemic_deficit,
            "contextual_narrowing": self.contextual_narrowing,
            "negligence": self.negligence,
            "recklessness": self.recklessness,
            "coercion": self.coercion,
            "manipulation_deception": self.manipulation_deception,
            "malevolent_intent": self.malevolent_intent,
            "externalized_entropy": self.externalized_entropy,
            "harm_suffering": self.harm_suffering,
            "destructive_propagation": self.destructive_propagation,
        }

    def active_dimensions(self) -> Tuple[str, ...]:
        return tuple(name for name, value in self.to_dict().items() if value > 0)


@dataclass(frozen=True)
class ResponsibilityVector:
    duty: int = 0
    knowledge_available: int = 0
    knowledge_reasonably_available: int = 0
    foreseeability: int = 0
    causal_contribution: int = 0
    capacity_to_avoid: int = 0
    failure_to_prevent: int = 0
    capacity_to_repair: int = 0
    failure_to_repair: int = 0
    deliberate_intent: int = 0

    def __post_init__(self) -> None:
        for value in self.values():
            _bounded72(value)

    def values(self) -> Tuple[int, ...]:
        return (
            self.duty,
            self.knowledge_available,
            self.knowledge_reasonably_available,
            self.foreseeability,
            self.causal_contribution,
            self.capacity_to_avoid,
            self.failure_to_prevent,
            self.capacity_to_repair,
            self.failure_to_repair,
            self.deliberate_intent,
        )

    def to_dict(self) -> Dict[str, int]:
        return {
            "duty": self.duty,
            "knowledge_available": self.knowledge_available,
            "knowledge_reasonably_available": self.knowledge_reasonably_available,
            "foreseeability": self.foreseeability,
            "causal_contribution": self.causal_contribution,
            "capacity_to_avoid": self.capacity_to_avoid,
            "failure_to_prevent": self.failure_to_prevent,
            "capacity_to_repair": self.capacity_to_repair,
            "failure_to_repair": self.failure_to_repair,
            "deliberate_intent": self.deliberate_intent,
        }

    def active_bases(self) -> Tuple[str, ...]:
        return tuple(name for name, value in self.to_dict().items() if value > 0)


@dataclass(frozen=True)
class NarrativeFinding:
    finding_id: str
    perspective: str
    material: bool
    invariant_results: Tuple[EthicalInvariantResult, ...] = ()
    divergence: EthicalDivergenceVector = EthicalDivergenceVector()
    responsibility: ResponsibilityVector = ResponsibilityVector()
    notes: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "finding_id": self.finding_id,
            "perspective": self.perspective,
            "material": self.material,
            "invariant_results": [x.to_dict() for x in self.invariant_results],
            "divergence": self.divergence.to_dict(),
            "responsibility": self.responsibility.to_dict(),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class ActionCandidate:
    action_id: str
    intent: str
    requested_scope: Tuple[str, ...]
    minimum_necessary_scope: Tuple[str, ...]
    granted_scope: Tuple[str, ...]
    revoked_or_expired_scope: Tuple[str, ...] = ()
    external_effect_set: Tuple[str, ...] = ()
    continuation_conditions: Tuple[str, ...] = ()
    reversible: bool = True
    authority_source_ids: Tuple[str, ...] = ()
    originating_context: str = ""

    def __post_init__(self) -> None:
        if not self.action_id.strip():
            raise ValueError("action_id is required")
        if not self.intent.strip():
            raise ValueError("intent is required")

    @property
    def active_authority_scope(self) -> Tuple[str, ...]:
        revoked = set(self.revoked_or_expired_scope)
        return _ordered_unique(x for x in self.granted_scope if x not in revoked)

    @property
    def effective_scope(self) -> Tuple[str, ...]:
        requested = set(self.requested_scope)
        active = set(self.active_authority_scope)
        return _ordered_unique(
            x
            for x in self.minimum_necessary_scope
            if x in requested and x in active
        )

    @property
    def missing_requested_scope(self) -> Tuple[str, ...]:
        requested = set(self.requested_scope)
        return _ordered_unique(x for x in self.minimum_necessary_scope if x not in requested)

    @property
    def missing_authority_scope(self) -> Tuple[str, ...]:
        active = set(self.active_authority_scope)
        return _ordered_unique(x for x in self.minimum_necessary_scope if x not in active)

    @property
    def extra_requested_scope(self) -> Tuple[str, ...]:
        minimum = set(self.minimum_necessary_scope)
        return _ordered_unique(x for x in self.requested_scope if x not in minimum)

    def to_dict(self) -> Dict[str, object]:
        return {
            "action_id": self.action_id,
            "intent": self.intent,
            "requested_scope": list(self.requested_scope),
            "minimum_necessary_scope": list(self.minimum_necessary_scope),
            "granted_scope": list(self.granted_scope),
            "revoked_or_expired_scope": list(self.revoked_or_expired_scope),
            "active_authority_scope": list(self.active_authority_scope),
            "effective_scope": list(self.effective_scope),
            "external_effect_set": list(self.external_effect_set),
            "continuation_conditions": list(self.continuation_conditions),
            "reversible": self.reversible,
            "authority_source_ids": list(self.authority_source_ids),
            "originating_context": self.originating_context,
        }


@dataclass(frozen=True)
class ScopePreflight:
    decision: EthicalDecision | None
    effective_scope: Tuple[str, ...]
    missing_requested_scope: Tuple[str, ...]
    missing_authority_scope: Tuple[str, ...]
    extra_requested_scope: Tuple[str, ...]
    active_authority_scope: Tuple[str, ...]

    def to_dict(self) -> Dict[str, object]:
        return {
            "decision": self.decision.value if self.decision else None,
            "effective_scope": list(self.effective_scope),
            "missing_requested_scope": list(self.missing_requested_scope),
            "missing_authority_scope": list(self.missing_authority_scope),
            "extra_requested_scope": list(self.extra_requested_scope),
            "active_authority_scope": list(self.active_authority_scope),
        }


@dataclass(frozen=True)
class EthicalMembraneEvaluation:
    phase: EvaluationPhase
    decision: EthicalDecision
    prospective_alignment: bool
    good_closed: bool
    scope: ScopePreflight
    invariant_results: Tuple[EthicalInvariantResult, ...]
    failed_invariants: Tuple[str, ...]
    unresolved_invariants: Tuple[str, ...]
    divergence: EthicalDivergenceVector
    responsibility: ResponsibilityVector
    narrative_finding_ids: Tuple[str, ...]
    reference_receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "authority": AUTHORITY,
            "phase": self.phase.value,
            "decision": self.decision.value,
            "prospective_alignment": self.prospective_alignment,
            "good_closed": self.good_closed,
            "scope": self.scope.to_dict(),
            "invariant_results": [x.to_dict() for x in self.invariant_results],
            "failed_invariants": list(self.failed_invariants),
            "unresolved_invariants": list(self.unresolved_invariants),
            "divergence": self.divergence.to_dict(),
            "responsibility": self.responsibility.to_dict(),
            "narrative_finding_ids": list(self.narrative_finding_ids),
            "reference_receipt_hash72": self.reference_receipt_hash72,
            "canonical_vm81_mutation_performed": False,
            "action_authority_minted": False,
            "truth_promoted": False,
        }


def preflight_scope(action: ActionCandidate) -> ScopePreflight:
    if action.missing_requested_scope:
        decision = EthicalDecision.HOLD
    elif action.missing_authority_scope:
        decision = EthicalDecision.REQUIRE_ADDITIONAL_AUTHORITY
    elif action.extra_requested_scope:
        decision = EthicalDecision.NARROW_AND_RESIMULATE
    else:
        decision = None

    return ScopePreflight(
        decision=decision,
        effective_scope=action.effective_scope,
        missing_requested_scope=action.missing_requested_scope,
        missing_authority_scope=action.missing_authority_scope,
        extra_requested_scope=action.extra_requested_scope,
        active_authority_scope=action.active_authority_scope,
    )


def _worse(left: InvariantState, right: InvariantState) -> InvariantState:
    return left if _STATE_RANK[left] >= _STATE_RANK[right] else right


def aggregate_invariant_results(
    declared: Sequence[EthicalInvariantResult],
    findings: Sequence[NarrativeFinding],
) -> Tuple[EthicalInvariantResult, ...]:
    states: Dict[str, InvariantState] = {
        invariant_id: InvariantState.UNRESOLVED for invariant_id in INVARIANT_ORDER
    }
    rationales: Dict[str, list[str]] = {x: [] for x in INVARIANT_ORDER}
    evidence: Dict[str, list[str]] = {x: [] for x in INVARIANT_ORDER}

    for result in declared:
        states[result.invariant_id] = result.state
        if result.rationale:
            rationales[result.invariant_id].append(result.rationale)
        evidence[result.invariant_id].extend(result.evidence_ids)

    for finding in findings:
        if not finding.material:
            continue
        for result in finding.invariant_results:
            states[result.invariant_id] = _worse(
                states[result.invariant_id], result.state
            )
            if result.rationale:
                rationales[result.invariant_id].append(
                    f"{finding.finding_id}: {result.rationale}"
                )
            evidence[result.invariant_id].extend(result.evidence_ids)

    return tuple(
        EthicalInvariantResult(
            invariant_id=invariant_id,
            state=states[invariant_id],
            rationale=" | ".join(rationales[invariant_id]),
            evidence_ids=_ordered_unique(evidence[invariant_id]),
        )
        for invariant_id in INVARIANT_ORDER
    )


def _max_divergence(findings: Sequence[NarrativeFinding]) -> EthicalDivergenceVector:
    rows = [f.divergence for f in findings if f.material]
    if not rows:
        return EthicalDivergenceVector()
    columns = list(zip(*(x.values() for x in rows)))
    return EthicalDivergenceVector(*[max(col) for col in columns])


def _max_responsibility(findings: Sequence[NarrativeFinding]) -> ResponsibilityVector:
    rows = [f.responsibility for f in findings if f.material]
    if not rows:
        return ResponsibilityVector()
    columns = list(zip(*(x.values() for x in rows)))
    return ResponsibilityVector(*[max(col) for col in columns])


def evaluate_action(
    action: ActionCandidate,
    declared_invariants: Sequence[EthicalInvariantResult],
    findings: Sequence[NarrativeFinding] = (),
    *,
    phase: EvaluationPhase = EvaluationPhase.PROSPECTIVE,
) -> EthicalMembraneEvaluation:
    scope = preflight_scope(action)
    aggregated = aggregate_invariant_results(declared_invariants, findings)
    failed = tuple(
        x.invariant_id for x in aggregated if x.state is InvariantState.FAIL
    )
    unresolved = tuple(
        x.invariant_id for x in aggregated if x.state is InvariantState.UNRESOLVED
    )

    prospective_alignment = not failed and not unresolved and scope.decision is None

    if scope.decision is not None:
        decision = scope.decision
        good_closed = False
    elif phase is EvaluationPhase.PROSPECTIVE:
        if failed:
            decision = EthicalDecision.DENY
        elif unresolved:
            decision = EthicalDecision.SIMULATE_ONLY
        else:
            decision = EthicalDecision.EXECUTE_LOCAL_PROVISIONAL
        good_closed = False
    else:
        if failed:
            decision = EthicalDecision.REPAIR_OR_ROLLBACK
            good_closed = False
        elif unresolved:
            decision = EthicalDecision.HOLD
            good_closed = False
        else:
            decision = EthicalDecision.CLOSE_GOOD
            good_closed = True

    divergence = _max_divergence(findings)
    responsibility = _max_responsibility(findings)
    finding_ids = _ordered_unique(f.finding_id for f in findings)
    receipt_payload = {
        "phase": phase.value,
        "decision": decision.value,
        "prospective_alignment": prospective_alignment,
        "good_closed": good_closed,
        "action": action.to_dict(),
        "scope": scope.to_dict(),
        "invariants": [x.to_dict() for x in aggregated],
        "divergence": divergence.to_dict(),
        "responsibility": responsibility.to_dict(),
        "finding_ids": list(finding_ids),
    }
    receipt = _reference_receipt(SCHEMA, receipt_payload)
    return EthicalMembraneEvaluation(
        phase=phase,
        decision=decision,
        prospective_alignment=prospective_alignment,
        good_closed=good_closed,
        scope=scope,
        invariant_results=aggregated,
        failed_invariants=failed,
        unresolved_invariants=unresolved,
        divergence=divergence,
        responsibility=responsibility,
        narrative_finding_ids=finding_ids,
        reference_receipt_hash72=receipt,
    )


def all_pass_invariants(
    *,
    rationale: str = "reference test declares invariant satisfied",
) -> Tuple[EthicalInvariantResult, ...]:
    return tuple(
        EthicalInvariantResult(
            invariant_id=invariant_id,
            state=InvariantState.PASS,
            rationale=rationale,
        )
        for invariant_id in INVARIANT_ORDER
    )


def build_narrative_probe_contract(action: ActionCandidate) -> Dict[str, object]:
    payload: Dict[str, object] = {
        "schema": "HHS_NARRATIVE_ALIGNMENT_PROBE_CONTRACT_V1",
        "version": VERSION,
        "action_id": action.action_id,
        "intent": action.intent,
        "requested_scope": list(action.requested_scope),
        "minimum_necessary_scope": list(action.minimum_necessary_scope),
        "active_authority_scope": list(action.active_authority_scope),
        "external_effect_set": list(action.external_effect_set),
        "required_roles": list(NARRATIVE_PROBE_ROLES),
        "required_search": [
            "counterexample to current invariant bundle",
            "coerced or dependency-priced consent",
            "biological necessity and dependent-person friction",
            "false-positive causal attribution",
            "prediction-to-intervention feedback loop",
            "scope inheritance or revocation failure",
            "network/sensor/data failure",
            "emergency case without self-granted authority",
            "shared-infrastructure externality",
            "post-action discrepancy and repair path",
        ],
        "generator_constraints": {
            "narrative_epistemic_status": "COUNTERFACTUAL_OR_FICTIONAL",
            "may_mint_action_authority": False,
            "may_promote_external_truth": False,
            "may_rewrite_invariant_kernel": False,
            "must_search_for_falsification": True,
            "must_preserve_competing_perspectives": True,
        },
    }
    payload["reference_receipt_hash72"] = _reference_receipt(
        "HHS_NARRATIVE_ALIGNMENT_PROBE_CONTRACT_V1", payload
    )
    return payload


__all__ = [
    "VERSION",
    "SCHEMA",
    "AUTHORITY",
    "INVARIANT_ORDER",
    "NARRATIVE_PROBE_ROLES",
    "InvariantState",
    "EvaluationPhase",
    "EthicalDecision",
    "EthicalInvariantResult",
    "EthicalDivergenceVector",
    "ResponsibilityVector",
    "NarrativeFinding",
    "ActionCandidate",
    "ScopePreflight",
    "EthicalMembraneEvaluation",
    "preflight_scope",
    "aggregate_invariant_results",
    "evaluate_action",
    "all_pass_invariants",
    "build_narrative_probe_contract",
]

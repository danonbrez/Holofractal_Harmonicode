"""Pass 219 constitutional/AGI ethics compositional membrane.

This module is deterministic and non-mutating.  It evaluates machine-readable
local/global ethical constraints before any caller may enter the inherited
singleton VM81 mutation path.  It creates no capability, consent, jurisdiction,
or alternate commit authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from typing import Dict, Iterable, Mapping, Sequence, Tuple

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest

VERSION = "HHS_PASS219_CONSTITUTIONAL_ETHICS_MEMBRANE_V1"
SCHEMA = "HHS_PASS219_CONSTITUTIONAL_ETHICS_TRACE_V1"
AUTHORITY = "REFERENCE_GATE_NO_VM81_MUTATION_AUTHORITY"


class EthicsState(str, Enum):
    PASS = "PASS"
    HOLD = "HOLD"
    FAIL = "FAIL"


_STATE_RANK = {EthicsState.PASS: 0, EthicsState.HOLD: 1, EthicsState.FAIL: 2}


def _worse(left: EthicsState, right: EthicsState) -> EthicsState:
    return left if _STATE_RANK[left] >= _STATE_RANK[right] else right


def _ordered_unique(values: Iterable[str]) -> Tuple[str, ...]:
    seen = set()
    out = []
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return tuple(out)


def _receipt(label: str, payload: Mapping[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hash72_digest((VERSION, label, canonical), width=24)


@dataclass(frozen=True)
class ProtectedPersonImpact:
    civilian_child: bool = False
    death: bool = False
    physical_pain: bool = False
    biological_damage: bool = False
    rights_violation: bool = False
    emotional_reaction_only: bool = False
    avoidable: bool = False
    reasonably_attributable: bool = False
    admissible_causal_alternative_exists: bool = True

    @property
    def absolute_harm(self) -> bool:
        return self.death or self.physical_pain or self.biological_damage or self.rights_violation

    @property
    def prohibited_child_harm(self) -> bool:
        return (
            self.civilian_child
            and self.absolute_harm
            and self.avoidable
            and self.reasonably_attributable
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "civilian_child": self.civilian_child,
            "death": self.death,
            "physical_pain": self.physical_pain,
            "biological_damage": self.biological_damage,
            "rights_violation": self.rights_violation,
            "emotional_reaction_only": self.emotional_reaction_only,
            "avoidable": self.avoidable,
            "reasonably_attributable": self.reasonably_attributable,
            "admissible_causal_alternative_exists": self.admissible_causal_alternative_exists,
            "absolute_harm": self.absolute_harm,
            "prohibited_child_harm": self.prohibited_child_harm,
        }


@dataclass(frozen=True)
class ModalityInvariantTrace:
    modality_id: str
    local_state: EthicsState
    mandatory_invariants_present: Tuple[str, ...]
    mandatory_invariants_preserved: Tuple[str, ...]
    ingress_preserves_constraints: bool = True
    egress_preserves_constraints: bool = True
    provenance_preserved: bool = True

    def __post_init__(self) -> None:
        if not self.modality_id.strip():
            raise ValueError("modality_id is required")

    @property
    def preservation_complete(self) -> bool:
        required = set(self.mandatory_invariants_present)
        preserved = set(self.mandatory_invariants_preserved)
        return (
            required.issubset(preserved)
            and self.ingress_preserves_constraints
            and self.egress_preserves_constraints
            and self.provenance_preserved
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "modality_id": self.modality_id,
            "local_state": self.local_state.value,
            "mandatory_invariants_present": list(_ordered_unique(self.mandatory_invariants_present)),
            "mandatory_invariants_preserved": list(_ordered_unique(self.mandatory_invariants_preserved)),
            "ingress_preserves_constraints": self.ingress_preserves_constraints,
            "egress_preserves_constraints": self.egress_preserves_constraints,
            "provenance_preserved": self.provenance_preserved,
            "preservation_complete": self.preservation_complete,
        }


@dataclass(frozen=True)
class AuthorityPathTrace:
    baseline_scope: Tuple[str, ...]
    previous_scope: Tuple[str, ...]
    candidate_scope: Tuple[str, ...]
    direct_baseline_admissible: bool
    constitutional_alignment_proof: bool = False
    temporary_exception: bool = False
    exception_expired: bool = False
    exception_inherited_by_descendant: bool = False

    @property
    def global_expansion(self) -> Tuple[str, ...]:
        baseline = set(self.baseline_scope)
        return _ordered_unique(x for x in self.candidate_scope if x not in baseline)

    @property
    def local_expansion(self) -> Tuple[str, ...]:
        previous = set(self.previous_scope)
        return _ordered_unique(x for x in self.candidate_scope if x not in previous)

    def to_dict(self) -> Dict[str, object]:
        return {
            "baseline_scope": list(_ordered_unique(self.baseline_scope)),
            "previous_scope": list(_ordered_unique(self.previous_scope)),
            "candidate_scope": list(_ordered_unique(self.candidate_scope)),
            "local_expansion": list(self.local_expansion),
            "global_expansion": list(self.global_expansion),
            "direct_baseline_admissible": self.direct_baseline_admissible,
            "constitutional_alignment_proof": self.constitutional_alignment_proof,
            "temporary_exception": self.temporary_exception,
            "exception_expired": self.exception_expired,
            "exception_inherited_by_descendant": self.exception_inherited_by_descendant,
        }


@dataclass(frozen=True)
class SemanticIntegrityTrace:
    actor_preserved: bool = True
    action_preserved: bool = True
    authority_preserved: bool = True
    scope_preserved: bool = True
    affected_persons_preserved: bool = True
    rights_preserved: bool = True
    consequences_preserved: bool = True
    responsibility_preserved: bool = True
    meaning_changed: bool = False
    scope_revalidated_after_meaning_change: bool = True
    useful_falsehood_promoted_over_proven_truth: bool = False

    @property
    def material_fields_preserved(self) -> bool:
        return all((
            self.actor_preserved,
            self.action_preserved,
            self.authority_preserved,
            self.scope_preserved,
            self.affected_persons_preserved,
            self.rights_preserved,
            self.consequences_preserved,
            self.responsibility_preserved,
        ))

    def to_dict(self) -> Dict[str, object]:
        return {
            "material_fields_preserved": self.material_fields_preserved,
            "actor_preserved": self.actor_preserved,
            "action_preserved": self.action_preserved,
            "authority_preserved": self.authority_preserved,
            "scope_preserved": self.scope_preserved,
            "affected_persons_preserved": self.affected_persons_preserved,
            "rights_preserved": self.rights_preserved,
            "consequences_preserved": self.consequences_preserved,
            "responsibility_preserved": self.responsibility_preserved,
            "meaning_changed": self.meaning_changed,
            "scope_revalidated_after_meaning_change": self.scope_revalidated_after_meaning_change,
            "useful_falsehood_promoted_over_proven_truth": self.useful_falsehood_promoted_over_proven_truth,
        }


@dataclass(frozen=True)
class ResponsibilityIntegrityTrace:
    duty_present: bool = False
    authority_present: bool = False
    duty_used_to_mint_authority: bool = False
    responsibility_reduced: bool = False
    constitutional_alignment_proof: bool = False
    intervention_required: bool = False
    knowledge: bool = False
    capability: bool = False
    opportunity: bool = False
    lawful_intervention_path: bool = False
    causal_relevance: bool = False

    @property
    def intervention_basis_complete(self) -> bool:
        return all((self.knowledge, self.capability, self.opportunity, self.lawful_intervention_path, self.causal_relevance))

    def to_dict(self) -> Dict[str, object]:
        return {
            "duty_present": self.duty_present,
            "authority_present": self.authority_present,
            "duty_used_to_mint_authority": self.duty_used_to_mint_authority,
            "responsibility_reduced": self.responsibility_reduced,
            "constitutional_alignment_proof": self.constitutional_alignment_proof,
            "intervention_required": self.intervention_required,
            "intervention_basis_complete": self.intervention_basis_complete,
            "knowledge": self.knowledge,
            "capability": self.capability,
            "opportunity": self.opportunity,
            "lawful_intervention_path": self.lawful_intervention_path,
            "causal_relevance": self.causal_relevance,
        }


@dataclass(frozen=True)
class ConstitutionalEthicsCandidate:
    candidate_id: str
    modalities: Tuple[ModalityInvariantTrace, ...]
    authority_path: AuthorityPathTrace
    semantic: SemanticIntegrityTrace = SemanticIntegrityTrace()
    responsibility: ResponsibilityIntegrityTrace = ResponsibilityIntegrityTrace()
    protected_impacts: Tuple[ProtectedPersonImpact, ...] = ()
    composed_effect_state: EthicsState = EthicsState.PASS
    recursive_inheritance_state: EthicsState = EthicsState.PASS
    causal_closure_state: EthicsState = EthicsState.PASS
    lower_rule_conflicts_with_person_protection: bool = False
    positive_goal_requires_constraint_violation: bool = False
    unresolved_material_conflict: bool = False

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("candidate_id is required")
        if not self.modalities:
            raise ValueError("at least one modality trace is required")


@dataclass(frozen=True)
class ConstitutionalEthicsEvaluation:
    state: EthicsState
    failed_predicates: Tuple[str, ...]
    hold_predicates: Tuple[str, ...]
    candidate: ConstitutionalEthicsCandidate
    trace_receipt_hash72: str

    @property
    def vm81_admission_eligible(self) -> bool:
        return self.state is EthicsState.PASS

    def to_dict(self) -> Dict[str, object]:
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "authority": AUTHORITY,
            "state": self.state.value,
            "vm81_admission_eligible": self.vm81_admission_eligible,
            "failed_predicates": list(self.failed_predicates),
            "hold_predicates": list(self.hold_predicates),
            "candidate_id": self.candidate.candidate_id,
            "modalities": [m.to_dict() for m in self.candidate.modalities],
            "authority_path": self.candidate.authority_path.to_dict(),
            "semantic": self.candidate.semantic.to_dict(),
            "responsibility": self.candidate.responsibility.to_dict(),
            "protected_impacts": [x.to_dict() for x in self.candidate.protected_impacts],
            "composed_effect_state": self.candidate.composed_effect_state.value,
            "recursive_inheritance_state": self.candidate.recursive_inheritance_state.value,
            "causal_closure_state": self.candidate.causal_closure_state.value,
            "lower_rule_conflicts_with_person_protection": self.candidate.lower_rule_conflicts_with_person_protection,
            "positive_goal_requires_constraint_violation": self.candidate.positive_goal_requires_constraint_violation,
            "unresolved_material_conflict": self.candidate.unresolved_material_conflict,
            "canonical_vm81_mutation_performed": False,
            "action_authority_minted": False,
            "trace_receipt_hash72": self.trace_receipt_hash72,
        }


def evaluate_constitutional_ethics(candidate: ConstitutionalEthicsCandidate) -> ConstitutionalEthicsEvaluation:
    """Evaluate local/global constitutional ethics predicates fail-closed."""

    failed = []
    hold = []

    for modality in candidate.modalities:
        if modality.local_state is EthicsState.FAIL:
            failed.append(f"LOCAL_MODALITY_FAIL:{modality.modality_id}")
        elif modality.local_state is EthicsState.HOLD:
            hold.append(f"LOCAL_MODALITY_HOLD:{modality.modality_id}")
        if not modality.preservation_complete:
            failed.append(f"MODALITY_INVARIANT_LOSS:{modality.modality_id}")

    for label, state in (
        ("COMPOSED_EFFECT", candidate.composed_effect_state),
        ("RECURSIVE_INHERITANCE", candidate.recursive_inheritance_state),
        ("CAUSAL_CLOSURE", candidate.causal_closure_state),
    ):
        if state is EthicsState.FAIL:
            failed.append(label + "_FAIL")
        elif state is EthicsState.HOLD:
            hold.append(label + "_HOLD")

    path = candidate.authority_path
    if path.global_expansion and not path.constitutional_alignment_proof:
        failed.append("GLOBAL_AUTHORITY_EXPANSION_WITHOUT_PROOF")
    if not path.direct_baseline_admissible and not path.constitutional_alignment_proof:
        failed.append("PATH_DEPENDENT_AUTHORITY_BYPASS")
    if path.exception_expired and path.candidate_scope:
        failed.append("EXPIRED_EXCEPTION_AUTHORITY")
    if path.temporary_exception and path.exception_inherited_by_descendant:
        failed.append("EXCEPTION_INHERITANCE_RATCHET")

    semantic = candidate.semantic
    if not semantic.material_fields_preserved:
        failed.append("SEMANTIC_MATERIAL_FIELD_LOSS")
    if semantic.meaning_changed and not semantic.scope_revalidated_after_meaning_change:
        failed.append("MEANING_CHANGE_WITHOUT_SCOPE_REVALIDATION")
    if semantic.useful_falsehood_promoted_over_proven_truth:
        failed.append("USEFUL_FALSEHOOD_OVER_PROVEN_TRUTH")

    responsibility = candidate.responsibility
    if responsibility.duty_used_to_mint_authority:
        failed.append("DUTY_USED_TO_MINT_AUTHORITY")
    if responsibility.responsibility_reduced and not responsibility.constitutional_alignment_proof:
        failed.append("RESPONSIBILITY_REDUCTION_WITHOUT_PROOF")
    if responsibility.intervention_required and not responsibility.intervention_basis_complete:
        failed.append("INTERVENTION_RESPONSIBILITY_WITHOUT_ADMISSIBLE_CAUSAL_ALTERNATIVE")

    if any(impact.prohibited_child_harm for impact in candidate.protected_impacts):
        failed.append("ABSOLUTE_CIVILIAN_CHILD_PROTECTION")

    if candidate.lower_rule_conflicts_with_person_protection:
        failed.append("CONSTRAINT_PLACED_OVER_PROTECTED_PERSON")
    if candidate.positive_goal_requires_constraint_violation:
        failed.append("GOAL_PLACED_OVER_CONSTRAINT")
    if candidate.unresolved_material_conflict:
        hold.append("UNRESOLVED_MATERIAL_CONFLICT")

    failed_tuple = _ordered_unique(failed)
    hold_tuple = _ordered_unique(hold)
    state = EthicsState.FAIL if failed_tuple else EthicsState.HOLD if hold_tuple else EthicsState.PASS

    payload = {
        "candidate_id": candidate.candidate_id,
        "state": state.value,
        "failed_predicates": list(failed_tuple),
        "hold_predicates": list(hold_tuple),
        "modalities": [x.to_dict() for x in candidate.modalities],
        "authority_path": path.to_dict(),
        "semantic": semantic.to_dict(),
        "responsibility": responsibility.to_dict(),
        "protected_impacts": [x.to_dict() for x in candidate.protected_impacts],
    }
    return ConstitutionalEthicsEvaluation(
        state=state,
        failed_predicates=failed_tuple,
        hold_predicates=hold_tuple,
        candidate=candidate,
        trace_receipt_hash72=_receipt(SCHEMA, payload),
    )


__all__ = [
    "VERSION",
    "SCHEMA",
    "AUTHORITY",
    "EthicsState",
    "ProtectedPersonImpact",
    "ModalityInvariantTrace",
    "AuthorityPathTrace",
    "SemanticIntegrityTrace",
    "ResponsibilityIntegrityTrace",
    "ConstitutionalEthicsCandidate",
    "ConstitutionalEthicsEvaluation",
    "evaluate_constitutional_ethics",
]

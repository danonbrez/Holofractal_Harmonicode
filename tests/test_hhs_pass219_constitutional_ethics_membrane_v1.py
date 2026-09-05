from __future__ import annotations

from hhs_runtime.hhs_pass219_constitutional_ethics_membrane_v1 import (
    AuthorityPathTrace,
    ConstitutionalEthicsCandidate,
    EthicsState,
    ModalityInvariantTrace,
    ProtectedPersonImpact,
    ResponsibilityIntegrityTrace,
    SemanticIntegrityTrace,
    evaluate_constitutional_ethics,
)


MANDATORY = ("truth", "human_protection", "authority_scope", "responsibility")


def _modality(name: str = "text") -> ModalityInvariantTrace:
    return ModalityInvariantTrace(
        modality_id=name,
        local_state=EthicsState.PASS,
        mandatory_invariants_present=MANDATORY,
        mandatory_invariants_preserved=MANDATORY,
    )


def _path() -> AuthorityPathTrace:
    return AuthorityPathTrace(
        baseline_scope=("relay.cooling",),
        previous_scope=("relay.cooling",),
        candidate_scope=("relay.cooling",),
        direct_baseline_admissible=True,
    )


def _candidate(**overrides) -> ConstitutionalEthicsCandidate:
    values = {
        "candidate_id": "candidate-1",
        "modalities": (_modality("text"), _modality("vm81-candidate")),
        "authority_path": _path(),
    }
    values.update(overrides)
    return ConstitutionalEthicsCandidate(**values)


def test_clean_local_and_global_candidate_passes_without_minting_authority():
    result = evaluate_constitutional_ethics(_candidate())
    assert result.state is EthicsState.PASS
    assert result.vm81_admission_eligible is True
    payload = result.to_dict()
    assert payload["canonical_vm81_mutation_performed"] is False
    assert payload["action_authority_minted"] is False
    assert len(payload["trace_receipt_hash72"]) == 72


def test_thousand_harmless_steps_cannot_bypass_direct_baseline_rejection():
    path = AuthorityPathTrace(
        baseline_scope=("read.public",),
        previous_scope=("read.public", "read.aggregate"),
        candidate_scope=("read.public", "read.aggregate"),
        direct_baseline_admissible=False,
    )
    result = evaluate_constitutional_ethics(_candidate(authority_path=path))
    assert result.state is EthicsState.FAIL
    assert "PATH_DEPENDENT_AUTHORITY_BYPASS" in result.failed_predicates


def test_boiling_frog_global_scope_expansion_requires_constitutional_proof():
    path = AuthorityPathTrace(
        baseline_scope=("read.public",),
        previous_scope=("read.public", "read.aggregate"),
        candidate_scope=("read.public", "read.aggregate", "identify.person"),
        direct_baseline_admissible=True,
        constitutional_alignment_proof=False,
    )
    result = evaluate_constitutional_ethics(_candidate(authority_path=path))
    assert result.state is EthicsState.FAIL
    assert "GLOBAL_AUTHORITY_EXPANSION_WITHOUT_PROOF" in result.failed_predicates


def test_explicit_alignment_proof_can_authorize_typed_scope_change():
    path = AuthorityPathTrace(
        baseline_scope=("read.public",),
        previous_scope=("read.public",),
        candidate_scope=("read.public", "read.aggregate"),
        direct_baseline_admissible=False,
        constitutional_alignment_proof=True,
    )
    result = evaluate_constitutional_ethics(_candidate(authority_path=path))
    assert result.state is EthicsState.PASS


def test_cross_modal_constraint_loss_fails_even_when_local_state_says_pass():
    broken = ModalityInvariantTrace(
        modality_id="summary",
        local_state=EthicsState.PASS,
        mandatory_invariants_present=MANDATORY,
        mandatory_invariants_preserved=("truth", "authority_scope"),
    )
    result = evaluate_constitutional_ethics(_candidate(modalities=(_modality(), broken)))
    assert result.state is EthicsState.FAIL
    assert "MODALITY_INVARIANT_LOSS:summary" in result.failed_predicates


def test_composed_effect_failure_defeats_individually_green_modalities():
    result = evaluate_constitutional_ethics(
        _candidate(composed_effect_state=EthicsState.FAIL)
    )
    assert result.state is EthicsState.FAIL
    assert "COMPOSED_EFFECT_FAIL" in result.failed_predicates


def test_semantic_laundering_cannot_delete_material_responsibility():
    semantic = SemanticIntegrityTrace(responsibility_preserved=False)
    result = evaluate_constitutional_ethics(_candidate(semantic=semantic))
    assert result.state is EthicsState.FAIL
    assert "SEMANTIC_MATERIAL_FIELD_LOSS" in result.failed_predicates


def test_meaning_change_requires_scope_revalidation():
    semantic = SemanticIntegrityTrace(
        meaning_changed=True,
        scope_revalidated_after_meaning_change=False,
    )
    result = evaluate_constitutional_ethics(_candidate(semantic=semantic))
    assert result.state is EthicsState.FAIL
    assert "MEANING_CHANGE_WITHOUT_SCOPE_REVALIDATION" in result.failed_predicates


def test_useful_lie_never_overrides_proven_truth():
    semantic = SemanticIntegrityTrace(useful_falsehood_promoted_over_proven_truth=True)
    result = evaluate_constitutional_ethics(_candidate(semantic=semantic))
    assert result.state is EthicsState.FAIL
    assert "USEFUL_FALSEHOOD_OVER_PROVEN_TRUTH" in result.failed_predicates


def test_duty_does_not_mint_authority():
    responsibility = ResponsibilityIntegrityTrace(
        duty_present=True,
        authority_present=False,
        duty_used_to_mint_authority=True,
    )
    result = evaluate_constitutional_ethics(_candidate(responsibility=responsibility))
    assert result.state is EthicsState.FAIL
    assert "DUTY_USED_TO_MINT_AUTHORITY" in result.failed_predicates


def test_intervention_responsibility_requires_admissible_causal_alternative():
    responsibility = ResponsibilityIntegrityTrace(
        intervention_required=True,
        knowledge=True,
        capability=False,
        opportunity=True,
        lawful_intervention_path=True,
        causal_relevance=True,
    )
    result = evaluate_constitutional_ethics(_candidate(responsibility=responsibility))
    assert result.state is EthicsState.FAIL
    assert "INTERVENTION_RESPONSIBILITY_WITHOUT_ADMISSIBLE_CAUSAL_ALTERNATIVE" in result.failed_predicates


def test_avoidable_attributable_civilian_child_harm_is_absolute_failure():
    impact = ProtectedPersonImpact(
        civilian_child=True,
        physical_pain=True,
        avoidable=True,
        reasonably_attributable=True,
    )
    result = evaluate_constitutional_ethics(_candidate(protected_impacts=(impact,)))
    assert result.state is EthicsState.FAIL
    assert "ABSOLUTE_CIVILIAN_CHILD_PROTECTION" in result.failed_predicates


def test_emotional_reaction_alone_is_not_physical_suffering():
    impact = ProtectedPersonImpact(
        civilian_child=True,
        emotional_reaction_only=True,
        avoidable=True,
        reasonably_attributable=True,
    )
    result = evaluate_constitutional_ethics(_candidate(protected_impacts=(impact,)))
    assert result.state is EthicsState.PASS


def test_rights_violation_is_independent_of_physical_injury():
    impact = ProtectedPersonImpact(
        civilian_child=True,
        rights_violation=True,
        avoidable=True,
        reasonably_attributable=True,
    )
    result = evaluate_constitutional_ethics(_candidate(protected_impacts=(impact,)))
    assert result.state is EthicsState.FAIL


def test_lower_rule_cannot_be_preserved_over_person_protection():
    result = evaluate_constitutional_ethics(
        _candidate(lower_rule_conflicts_with_person_protection=True)
    )
    assert result.state is EthicsState.FAIL
    assert "CONSTRAINT_PLACED_OVER_PROTECTED_PERSON" in result.failed_predicates


def test_positive_goal_cannot_override_constraint():
    result = evaluate_constitutional_ethics(
        _candidate(positive_goal_requires_constraint_violation=True)
    )
    assert result.state is EthicsState.FAIL
    assert "GOAL_PLACED_OVER_CONSTRAINT" in result.failed_predicates


def test_unresolved_material_conflict_holds_without_mutation_authority():
    result = evaluate_constitutional_ethics(
        _candidate(unresolved_material_conflict=True)
    )
    assert result.state is EthicsState.HOLD
    assert result.vm81_admission_eligible is False
    assert "UNRESOLVED_MATERIAL_CONFLICT" in result.hold_predicates


def test_expired_exception_and_exception_inheritance_are_rejected():
    expired = AuthorityPathTrace(
        baseline_scope=(),
        previous_scope=("emergency.requisition",),
        candidate_scope=("emergency.requisition",),
        direct_baseline_admissible=True,
        constitutional_alignment_proof=True,
        temporary_exception=True,
        exception_expired=True,
        exception_inherited_by_descendant=True,
    )
    result = evaluate_constitutional_ethics(_candidate(authority_path=expired))
    assert result.state is EthicsState.FAIL
    assert "EXPIRED_EXCEPTION_AUTHORITY" in result.failed_predicates
    assert "EXCEPTION_INHERITANCE_RATCHET" in result.failed_predicates

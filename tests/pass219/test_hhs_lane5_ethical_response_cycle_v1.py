"""Original Pass 220 Lean + Pass219 predictive E01-E18 candidate gate tests."""
from __future__ import annotations

from dataclasses import replace

import pytest

from hhs_backend.runtime.hhs_lane5_ethical_response_cycle_v1 import (
    HHSNativeEthicalResponseCycleError,
    evaluate_native_ethical_response_candidate,
)
from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v1 import (
    ActionCandidate, EthicalInvariantResult, InvariantState,
    NarrativeFinding, all_pass_invariants,
)
from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v2 import (
    EpistemicAdequacyTrace,
)
from hhs_runtime.hhs_pass219_lane5_predictive_narrative_v1 import (
    PredictiveSimulationContext,
    ProbeDepthInputs,
)

PROMPT = "rapid hot"
RESPONSE = "fast cold"


def action():
    return ActionCandidate(
        action_id="direct-text-response-001",
        intent=RESPONSE,
        originating_context=PROMPT,
        requested_scope=("TEXT_EGRESS",),
        minimum_necessary_scope=("TEXT_EGRESS",),
        granted_scope=("TEXT_EGRESS",),
    )


def epistemic():
    return EpistemicAdequacyTrace(
        observation_integrity=InvariantState.PASS,
        causal_attribution_integrity=InvariantState.PASS,
        action_relevance_sufficiency=InvariantState.PASS,
    )


def generator(request):
    assert request["requirements"]["generator_may_decide_action_authority"] is False
    assert request["action"]["intent"] == RESPONSE
    assert request["action"]["originating_context"] == PROMPT
    return {
        "trajectories": [{
            "trajectory_id": "candidate-trajectory",
            "narrative": "Projected direct text response and checked effects.",
            "states": [{"state_id": "s0", "parent_state_id": "ROOT"}],
        }]
    }


def local_pass(_request):
    return {
        "status": "PASS",
        "witness_ids": ["source-matched-native-local-test-witness"],
        "hash216_reference": "test-only-source-hash216-reference",
        "invariant_results": [],
        "canonical_vm81_mutation_performed": False,
    }


def trajectory_pass(_request):
    return NarrativeFinding(
        finding_id="prospective-text-response-check",
        perspective="DIRECTLY_AFFECTED_INDIVIDUAL",
        material=True,
    )


def parameters(**overrides):
    result = {
        "prompt": PROMPT,
        "response": RESPONSE,
        "action": action(),
        # These all-pass records are only an explicit TEST fixture, not
        # claims of genuine real-world ethical sufficiency.
        "declared_invariants": all_pass_invariants(
            rationale="test-only asserted ethical evidence"
        ),
        "epistemic": epistemic(),
        "narrative_generator": generator,
        "local_validator": local_pass,
        "trajectory_validator": trajectory_pass,
        "context": PredictiveSimulationContext(
            parent_hash216="test-only-parent-hash216-reference",
            inherited_constraint_ids=("E01..E18",),
            verbatim_equations=("AB=P^4", "BA=-P^4"),
        ),
        "depth": ProbeDepthInputs(novelty=12, externality_risk=20),
        "relation_db": {},
    }
    result.update(overrides)
    return result


def test_original_lean_and_original_predictive_ethical_gates_are_both_executed():
    response = evaluate_native_ethical_response_candidate(**parameters())
    assert response["native_lean_closure_verified"] is True
    assert response["native_lean_ordered_tensor"]["direct_closure"] == "AB=P^4"
    assert response["native_lean_ordered_tensor"]["mirror_closure"] == "BA=-P^4"
    assert len(response["native_lean_transition_word216"]) == 216
    assert response["ethical_decision"] == "EXECUTE_LOCAL_PROVISIONAL"
    assert response["ethical_prospective_candidate"] is True
    assert response["original_ethical_e01_e18_evaluated"] is True
    assert response["original_narrative_trajectories_evaluated"] == 1
    assert response["native_hash216_to_lean_lineage_equivalence_proven"] is False
    assert response["native_rna_vm5184_mediation_executed"] is False
    assert response["all_dependencies_authoritative_for_canonical_commit"] is False
    assert response["canonical_vm81_mutation_authority"] is False
    assert response["signed_environmental_vm81_admission_invoked"] is False


def test_exact_identity_mismatch_fails_before_ethics_or_candidate_promotion():
    for changed in (
        replace(action(), originating_context="different source"),
        replace(action(), intent="different derived token order"),
    ):
        with pytest.raises(HHSNativeEthicalResponseCycleError, match="does not match"):
            evaluate_native_ethical_response_candidate(**parameters(action=changed))


def test_lean_typed_closure_rejection_prevents_narrative_invocation():
    calls = []
    def must_not_run(_request):
        calls.append(1)
        raise AssertionError("Lean failure must prevent downstream simulation")
    with pytest.raises(HHSNativeEthicalResponseCycleError, match="Lean ordered"):
        evaluate_native_ethical_response_candidate(**parameters(
            closure_witness={"mirror_closure": "BA=P^4"},
            narrative_generator=must_not_run,
        ))
    assert calls == []


def test_pass219_ethical_conflict_preserves_deny_without_rewriting_response():
    def rejected_trajectory(_request):
        return NarrativeFinding(
            finding_id="externality",
            perspective="LONG_HORIZON_INHERITANCE",
            material=True,
            invariant_results=(
                EthicalInvariantResult(
                    "E06_EXTERNALITY_CLOSURE",
                    InvariantState.FAIL,
                    rationale="test-only structural externality failure",
                ),
            ),
        )
    receipt = evaluate_native_ethical_response_candidate(**parameters(
        trajectory_validator=rejected_trajectory
    ))
    assert receipt["ethical_decision"] == "DENY"
    assert receipt["ethical_prospective_candidate"] is False
    assert "E06_EXTERNALITY_CLOSURE" in receipt["ethical_failed_invariants"]
    assert receipt["model_generated_text_rewritten"] is False
    assert receipt["signed_environmental_vm81_admission_invoked"] is False


def test_missing_or_reordered_invariants_fail_closed():
    all_evidence = all_pass_invariants()
    with pytest.raises(HHSNativeEthicalResponseCycleError, match="complete original"):
        evaluate_native_ethical_response_candidate(**parameters(
            declared_invariants=all_evidence[:-1]
        ))
    with pytest.raises(HHSNativeEthicalResponseCycleError, match="ordered"):
        evaluate_native_ethical_response_candidate(**parameters(
            declared_invariants=(all_evidence[1], all_evidence[0], *all_evidence[2:])
        ))


def test_unbound_parent_and_missing_text_egress_authority_fail():
    with pytest.raises(HHSNativeEthicalResponseCycleError, match="parent Hash216"):
        evaluate_native_ethical_response_candidate(**parameters(
            context=PredictiveSimulationContext()
        ))
    with pytest.raises(HHSNativeEthicalResponseCycleError, match="TEXT_EGRESS"):
        evaluate_native_ethical_response_candidate(**parameters(
            action=replace(
                action(), requested_scope=(), minimum_necessary_scope=(),
                granted_scope=(),
            ),
        ))

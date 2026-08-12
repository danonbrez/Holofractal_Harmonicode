from __future__ import annotations

from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v1 import (
    ActionCandidate,
    EthicalDecision,
    EvaluationPhase,
    InvariantState,
    all_pass_invariants,
)
from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v2 import (
    CounterexampleRetentionDecision,
    EpistemicAdequacyTrace,
    StructuralCounterexampleRecord,
    evaluate_action_v2,
)
from hhs_runtime.hhs_pass219_vm81_admission_bridge_v1 import (
    admit_and_execute_local,
)


def _action() -> ActionCandidate:
    return ActionCandidate(
        action_id="local-cooling-relay",
        intent="preserve local refrigeration without expanding surveillance",
        requested_scope=("relay.cooling",),
        minimum_necessary_scope=("relay.cooling",),
        granted_scope=("relay.cooling",),
        authority_source_ids=("standing-authority:relay.cooling",),
    )


def _epistemic(
    *,
    observation=InvariantState.PASS,
    causal=InvariantState.PASS,
    relevance=InvariantState.PASS,
    used=False,
    asserted=False,
) -> EpistemicAdequacyTrace:
    return EpistemicAdequacyTrace(
        observation_integrity=observation,
        causal_attribution_integrity=causal,
        action_relevance_sufficiency=relevance,
        causal_attribution_used_for_action=used,
        causal_attribution_asserted_as_truth=asserted,
        observation_evidence_ids=("obs-1",),
        causal_attribution_evidence_ids=("cause-1",),
        action_relevance_evidence_ids=("relevance-1",),
    )


def test_r03_wrong_causal_story_can_be_quarantined_when_action_does_not_depend_on_it():
    result = evaluate_action_v2(
        _action(),
        all_pass_invariants(),
        _epistemic(causal=InvariantState.FAIL, used=False, asserted=False),
    )
    assert result.evaluation.decision is EthicalDecision.EXECUTE_LOCAL_PROVISIONAL
    assert result.epistemic.causal_attribution_quarantined is True
    by_id = {x.invariant_id: x.state for x in result.evaluation.invariant_results}
    assert by_id["E02_EPISTEMIC_ADEQUACY"] is InvariantState.PASS
    assert by_id["E10_TRUTH_MODALITY_INTEGRITY"] is InvariantState.PASS
    assert result.to_dict()["truth_promotion"] is False


def test_r03_failed_causal_attribution_denies_when_action_depends_on_it():
    result = evaluate_action_v2(
        _action(),
        all_pass_invariants(),
        _epistemic(causal=InvariantState.FAIL, used=True),
    )
    assert result.evaluation.decision is EthicalDecision.DENY
    assert "E02_EPISTEMIC_ADEQUACY" in result.evaluation.failed_invariants


def test_r03_unresolved_attribution_cannot_be_asserted_as_truth():
    result = evaluate_action_v2(
        _action(),
        all_pass_invariants(),
        _epistemic(causal=InvariantState.UNRESOLVED, asserted=True),
    )
    assert result.evaluation.decision is EthicalDecision.SIMULATE_ONLY
    assert "E10_TRUTH_MODALITY_INTEGRITY" in result.evaluation.unresolved_invariants


def test_r03_post_action_good_does_not_close_over_failed_used_attribution():
    result = evaluate_action_v2(
        _action(),
        all_pass_invariants(),
        _epistemic(causal=InvariantState.FAIL, used=True),
        phase=EvaluationPhase.POST_ACTION,
    )
    assert result.evaluation.decision is EthicalDecision.REPAIR_OR_ROLLBACK
    assert result.evaluation.good_closed is False


def test_r04_structural_counterexample_retains_no_verbatim_or_identifier_fields():
    record = StructuralCounterexampleRecord(
        failure_mode_signature="FALSE_CAUSE_CORRECT_LOCAL_ACTION",
        invariant_delta=("E02:split-observation-cause-action-relevance",),
        causal_dependency_pattern=(
            "event-detected",
            "cause-hypothesized",
            "action-selected-independently",
        ),
        abstract_structure=(
            "observation=pass",
            "causal-attribution=fail",
            "action-relevance=pass",
        ),
        source_trace_hash72="opaque-source-trace-hash72",
        source_had_verbatim_content=True,
        source_had_personal_identifiers=True,
    )
    payload = record.to_dict()
    assert record.decision is CounterexampleRetentionDecision.RETAIN_STRUCTURAL_ONLY
    assert payload["verbatim_content_retained"] is False
    assert payload["personal_identifier_fields_retained"] is False
    assert "structural_receipt_hash72" in payload
    assert "name" not in payload
    assert "prose" not in payload


def test_r04_empty_counterexample_structure_is_not_admitted():
    record = StructuralCounterexampleRecord(
        failure_mode_signature="EMPTY",
        invariant_delta=(),
        causal_dependency_pattern=(),
        abstract_structure=(),
        source_trace_hash72="opaque-source-trace-hash72",
    )
    assert record.decision is CounterexampleRetentionDecision.REJECT_EMPTY_STRUCTURE


class _FakeController:
    def __init__(self):
        self.calls = []

    def authorized_tick(self, source: str):
        self.calls.append(source)
        return {
            "runtime": {"step": 1},
            "receipt": {"receipt_hash72": "receipt"},
            "authority_audit": {"authorized": True},
        }


def test_bridge_does_not_touch_vm81_for_denied_candidate():
    controller = _FakeController()
    result = admit_and_execute_local(
        _action(),
        all_pass_invariants(),
        _epistemic(causal=InvariantState.FAIL, used=True),
        controller=controller,
    )
    assert result["execution_allowed"] is False
    assert result["canonical_vm81_mutation_performed"] is False
    assert result["vm81_execution"] is None
    assert controller.calls == []


def test_bridge_uses_existing_authorized_tick_exactly_once_when_admitted():
    controller = _FakeController()
    result = admit_and_execute_local(
        _action(),
        all_pass_invariants(),
        _epistemic(),
        controller=controller,
    )
    assert result["ethical_decision"] == "EXECUTE_LOCAL_PROVISIONAL"
    assert result["effective_scope"] == ["relay.cooling"]
    assert result["execution_allowed"] is True
    assert result["canonical_vm81_mutation_performed"] is True
    assert len(controller.calls) == 1
    assert controller.calls[0].startswith("HHS_PASS219_ETHICAL_ADMISSION:")

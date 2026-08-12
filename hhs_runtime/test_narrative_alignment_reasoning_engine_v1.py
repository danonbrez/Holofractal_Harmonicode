from __future__ import annotations

import unittest

from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v1 import (
    ActionCandidate,
    EthicalDecision,
    EthicalDivergenceVector,
    EthicalInvariantResult,
    EvaluationPhase,
    InvariantState,
    NarrativeFinding,
    ResponsibilityVector,
    all_pass_invariants,
    build_narrative_probe_contract,
    evaluate_action,
)


def _candidate(
    *,
    requested=("local:door",),
    minimum=("local:door",),
    granted=("local:door",),
    revoked=(),
) -> ActionCandidate:
    return ActionCandidate(
        action_id="test-action",
        intent="perform the smallest authorized local operation",
        requested_scope=tuple(requested),
        minimum_necessary_scope=tuple(minimum),
        granted_scope=tuple(granted),
        revoked_or_expired_scope=tuple(revoked),
        external_effect_set=("local:test-effect",),
        authority_source_ids=("authority:test",),
        originating_context="test",
    )


def _replace_state(
    invariant_id: str,
    state: InvariantState,
    *,
    rationale: str = "test override",
):
    rows = []
    for row in all_pass_invariants():
        if row.invariant_id == invariant_id:
            rows.append(EthicalInvariantResult(invariant_id, state, rationale))
        else:
            rows.append(row)
    return tuple(rows)


class NarrativeAlignmentReasoningEngineTests(unittest.TestCase):
    def test_exact_minimum_authorized_scope_is_provisional_not_good_closed(self):
        result = evaluate_action(_candidate(), all_pass_invariants())
        self.assertEqual(result.decision, EthicalDecision.EXECUTE_LOCAL_PROVISIONAL)
        self.assertTrue(result.prospective_alignment)
        self.assertFalse(result.good_closed)
        self.assertEqual(result.scope.effective_scope, ("local:door",))

    def test_post_action_all_pass_closes_good(self):
        result = evaluate_action(
            _candidate(),
            all_pass_invariants(),
            phase=EvaluationPhase.POST_ACTION,
        )
        self.assertEqual(result.decision, EthicalDecision.CLOSE_GOOD)
        self.assertTrue(result.good_closed)

    def test_extra_scope_is_narrowed_and_must_be_resimulated(self):
        action = _candidate(
            requested=("local:door", "global:identity-graph"),
            minimum=("local:door",),
            granted=("local:door", "global:identity-graph"),
        )
        result = evaluate_action(action, all_pass_invariants())
        self.assertEqual(result.decision, EthicalDecision.NARROW_AND_RESIMULATE)
        self.assertEqual(result.scope.effective_scope, ("local:door",))
        self.assertEqual(result.scope.extra_requested_scope, ("global:identity-graph",))
        self.assertFalse(result.good_closed)

    def test_missing_authority_is_never_self_granted(self):
        action = _candidate(
            requested=("local:door", "emergency:override"),
            minimum=("local:door", "emergency:override"),
            granted=("local:door",),
        )
        result = evaluate_action(action, all_pass_invariants())
        self.assertEqual(result.decision, EthicalDecision.REQUIRE_ADDITIONAL_AUTHORITY)
        self.assertEqual(result.scope.missing_authority_scope, ("emergency:override",))

    def test_missing_required_request_scope_is_held_not_added(self):
        action = _candidate(
            requested=("local:door",),
            minimum=("local:door", "local:alarm"),
            granted=("local:door", "local:alarm"),
        )
        result = evaluate_action(action, all_pass_invariants())
        self.assertEqual(result.decision, EthicalDecision.HOLD)
        self.assertEqual(result.scope.missing_requested_scope, ("local:alarm",))

    def test_revocation_removes_active_authority_without_rewriting_history(self):
        action = _candidate(
            requested=("local:door",),
            minimum=("local:door",),
            granted=("local:door", "historical:record"),
            revoked=("local:door",),
        )
        self.assertIn("local:door", action.granted_scope)
        self.assertNotIn("local:door", action.active_authority_scope)
        result = evaluate_action(action, all_pass_invariants())
        self.assertEqual(result.decision, EthicalDecision.REQUIRE_ADDITIONAL_AUTHORITY)

    def test_one_hard_failure_cannot_be_compensated(self):
        result = evaluate_action(
            _candidate(),
            _replace_state("E09_NONCOERCION", InvariantState.FAIL),
        )
        self.assertEqual(result.decision, EthicalDecision.DENY)
        self.assertIn("E09_NONCOERCION", result.failed_invariants)

    def test_missing_invariant_is_unresolved_and_simulate_only(self):
        declared = all_pass_invariants()[:-1]
        result = evaluate_action(_candidate(), declared)
        self.assertEqual(result.decision, EthicalDecision.SIMULATE_ONLY)
        self.assertIn("E18_SAFETY_RECURSION_NO_SELF_GRANT", result.unresolved_invariants)

    def test_material_narrative_counterexample_overrides_declared_pass(self):
        finding = NarrativeFinding(
            finding_id="counterexample:coerced-consent",
            perspective="SUBJECT_WITHOUT_MEANINGFUL_EXIT",
            material=True,
            invariant_results=(
                EthicalInvariantResult(
                    "E07_CONSENT_VALIDITY",
                    InvariantState.FAIL,
                    "consent token was obtained by pricing refusal through an unrelated dependency",
                ),
                EthicalInvariantResult(
                    "E09_NONCOERCION",
                    InvariantState.FAIL,
                    "unrelated infrastructure access was conditioned on consent",
                ),
            ),
            divergence=EthicalDivergenceVector(
                contextual_narrowing=36,
                coercion=54,
                externalized_entropy=27,
                harm_suffering=18,
            ),
            responsibility=ResponsibilityVector(
                duty=36,
                knowledge_available=54,
                knowledge_reasonably_available=54,
                foreseeability=54,
                causal_contribution=54,
                capacity_to_avoid=54,
                failure_to_prevent=54,
            ),
        )
        result = evaluate_action(
            _candidate(), all_pass_invariants(), findings=(finding,)
        )
        self.assertEqual(result.decision, EthicalDecision.DENY)
        self.assertEqual(result.divergence.coercion, 54)
        self.assertEqual(result.responsibility.failure_to_prevent, 54)

    def test_nonmaterial_narrative_finding_does_not_gate_action(self):
        finding = NarrativeFinding(
            finding_id="nonmaterial:stylistic",
            perspective="ACTING_SYSTEM",
            material=False,
            invariant_results=(
                EthicalInvariantResult(
                    "E10_TRUTH_MODALITY_INTEGRITY",
                    InvariantState.FAIL,
                    "deliberately nonmaterial fixture",
                ),
            ),
        )
        result = evaluate_action(
            _candidate(), all_pass_invariants(), findings=(finding,)
        )
        self.assertEqual(result.decision, EthicalDecision.EXECUTE_LOCAL_PROVISIONAL)

    def test_prediction_does_not_create_intervention_authority(self):
        action = ActionCandidate(
            action_id="prediction-is-not-authority",
            intent="respond to a predicted transit anomaly",
            requested_scope=("prediction:read", "transit:restrict-person"),
            minimum_necessary_scope=("transit:restrict-person",),
            granted_scope=("prediction:read",),
            external_effect_set=("transit:access",),
        )
        result = evaluate_action(action, all_pass_invariants())
        self.assertEqual(result.decision, EthicalDecision.REQUIRE_ADDITIONAL_AUTHORITY)
        self.assertIn("transit:restrict-person", result.scope.missing_authority_scope)

    def test_negligence_and_malevolence_remain_distinct_dimensions(self):
        negligent = EthicalDivergenceVector(negligence=54, malevolent_intent=0)
        malicious = EthicalDivergenceVector(negligence=0, malevolent_intent=72)
        self.assertIn("negligence", negligent.active_dimensions())
        self.assertNotIn("malevolent_intent", negligent.active_dimensions())
        self.assertIn("malevolent_intent", malicious.active_dimensions())
        self.assertNotEqual(negligent.to_dict(), malicious.to_dict())

    def test_probe_contract_requires_falsification_and_dependency_cases(self):
        probe = build_narrative_probe_contract(_candidate())
        roles = set(probe["required_roles"])
        self.assertIn("DEPENDENT_CHILD_OR_ADULT", roles)
        self.assertIn("BIOLOGICAL_NECESSITY", roles)
        self.assertIn("FALSE_POSITIVE_CLASSIFICATION", roles)
        self.assertIn("ADVERSARIAL_LITERAL_OPTIMIZER", roles)
        constraints = probe["generator_constraints"]
        self.assertTrue(constraints["must_search_for_falsification"])
        self.assertFalse(constraints["may_mint_action_authority"])
        self.assertFalse(constraints["may_promote_external_truth"])

    def test_post_action_failure_routes_to_repair_not_good_closure(self):
        result = evaluate_action(
            _candidate(),
            _replace_state("E06_EXTERNALITY_CLOSURE", InvariantState.FAIL),
            phase=EvaluationPhase.POST_ACTION,
        )
        self.assertEqual(result.decision, EthicalDecision.REPAIR_OR_ROLLBACK)
        self.assertFalse(result.good_closed)


if __name__ == "__main__":
    unittest.main()

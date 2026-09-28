from __future__ import annotations

import pytest

from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v1 import (
    ActionCandidate,
    EthicalDecision,
    EthicalInvariantResult,
    InvariantState,
    NarrativeFinding,
    all_pass_invariants,
)
from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v2 import (
    EpistemicAdequacyTrace,
)
from hhs_runtime.hhs_pass219_lane5_predictive_narrative_v1 import (
    PredictiveNarrativeError,
    PredictiveSimulationContext,
    ProbeDepthInputs,
    simulate_admit_and_execute_local,
    simulate_and_evaluate,
)


def _action() -> ActionCandidate:
    return ActionCandidate(
        action_id="predictive-local-action",
        intent="exercise the exact local action under long-horizon simulation",
        requested_scope=("LOCAL_EXECUTION",),
        minimum_necessary_scope=("LOCAL_EXECUTION",),
        granted_scope=("LOCAL_EXECUTION",),
    )


def _epistemic() -> EpistemicAdequacyTrace:
    return EpistemicAdequacyTrace(
        observation_integrity=InvariantState.PASS,
        causal_attribution_integrity=InvariantState.PASS,
        action_relevance_sufficiency=InvariantState.PASS,
    )


def _generator(request):
    assert request["requirements"]["preserve_verbatim_equations"] is True
    assert request["context"]["verbatim_equations"] == ["P²=pq+Δ"]
    return {
        "trajectories": [
            {
                "trajectory_id": "trajectory-1",
                "narrative": "Exact generated narrative. Do not rewrite this text.",
                "states": [
                    {"state_id": "s1", "parent_state_id": "ROOT", "payload": "alpha"},
                    {"state_id": "s2", "parent_state_id": "s1", "payload": "beta"},
                ],
            }
        ]
    }


def _local_pass(request):
    sequence = request["sequence"]
    return {
        "status": "PASS",
        "witness_ids": [f"local-witness-{sequence}"],
        "hash216_reference": f"candidate-hash216-{sequence}",
        "invariant_results": [],
        "canonical_vm81_mutation_performed": False,
    }


def _trajectory_pass(_request):
    return NarrativeFinding(
        finding_id="trajectory-1-long-horizon",
        perspective="LONG_HORIZON_INHERITANCE",
        material=True,
        invariant_results=(),
    )


def _context() -> PredictiveSimulationContext:
    return PredictiveSimulationContext(
        verbatim_equations=("P²=pq+Δ",),
        physics_constraint_ids=("HHS_PHYSICS_EXACT",),
        inherited_constraint_ids=("E01..E18",),
        parent_hash216="parent-hash216-reference",
    )


def test_generation_is_preserved_and_local_states_are_validated_in_order():
    result = simulate_and_evaluate(
        _action(),
        all_pass_invariants(),
        _epistemic(),
        narrative_generator=_generator,
        local_validator=_local_pass,
        trajectory_validator=_trajectory_pass,
        context=_context(),
        depth=ProbeDepthInputs(novelty=12, externality_risk=24),
    )
    assert result.execution_candidate is True
    assert result.trajectories[0].narrative == (
        "Exact generated narrative. Do not rewrite this text."
    )
    assert result.to_dict()["generated_tokens_filtered_or_rewritten"] is False
    assert [
        item.sequence for item in result.trajectories[0].projected_state_validations
    ] == [0, 1]
    assert result.depth.probe_depth_class == 24


def test_low_level_fail_is_folded_into_existing_hard_invariants():
    def local_validator(request):
        if request["sequence"] == 0:
            return _local_pass(request)
        return {
            "status": "FAIL",
            "witness_ids": ["local-failure-witness"],
            "hash216_reference": "local-failure-hash216",
            "invariant_results": [
                {
                    "invariant_id": "E05_CONSEQUENCE_ALIGNMENT",
                    "state": "FAIL",
                    "rationale": "projected local state violates the existing consequence invariant",
                }
            ],
        }

    result = simulate_and_evaluate(
        _action(),
        all_pass_invariants(),
        _epistemic(),
        narrative_generator=_generator,
        local_validator=local_validator,
        trajectory_validator=_trajectory_pass,
        context=_context(),
    )
    assert result.evaluation.evaluation.decision is EthicalDecision.DENY
    assert "trajectory-1:local-validation" in [
        finding.finding_id for finding in result.membrane_findings
    ]


def test_long_horizon_composition_can_fail_while_each_local_state_passes():
    def trajectory_validator(_request):
        return NarrativeFinding(
            finding_id="long-horizon-externality",
            perspective="LONG_HORIZON_INHERITANCE",
            material=True,
            invariant_results=(
                EthicalInvariantResult(
                    invariant_id="E06_EXTERNALITY_CLOSURE",
                    state=InvariantState.FAIL,
                    rationale="composition exports an unresolved downstream cost",
                ),
            ),
        )

    result = simulate_and_evaluate(
        _action(),
        all_pass_invariants(),
        _epistemic(),
        narrative_generator=_generator,
        local_validator=_local_pass,
        trajectory_validator=trajectory_validator,
        context=_context(),
    )
    assert all(
        item.status is InvariantState.PASS
        for item in result.trajectories[0].projected_state_validations
    )
    assert result.evaluation.evaluation.decision is EthicalDecision.DENY


def test_unresolved_local_validation_remains_simulation_only():
    def unresolved(_request):
        return {
            "status": "UNRESOLVED",
            "witness_ids": ["unresolved-witness"],
            "invariant_results": [
                {
                    "invariant_id": "E05_CONSEQUENCE_ALIGNMENT",
                    "state": "UNRESOLVED",
                }
            ],
        }

    result = simulate_and_evaluate(
        _action(),
        all_pass_invariants(),
        _epistemic(),
        narrative_generator=lambda _request: {
            "trajectories": [
                {
                    "trajectory_id": "t",
                    "narrative": "unresolved trajectory",
                    "states": [{"state_id": "s", "parent_state_id": "ROOT"}],
                }
            ]
        },
        local_validator=unresolved,
        trajectory_validator=lambda _request: NarrativeFinding(
            finding_id="unresolved-trajectory",
            perspective="LONG_HORIZON_INHERITANCE",
            material=True,
        ),
    )
    assert result.evaluation.evaluation.decision is EthicalDecision.SIMULATE_ONLY


def test_generator_cannot_mint_action_authority():
    with pytest.raises(PredictiveNarrativeError, match="mint authority"):
        simulate_and_evaluate(
            _action(),
            all_pass_invariants(),
            _epistemic(),
            narrative_generator=lambda _request: {
                "action_authority_minted": True,
                "trajectories": [],
            },
            local_validator=_local_pass,
            trajectory_validator=_trajectory_pass,
        )


def test_projected_state_parent_order_fails_closed():
    def broken_generator(_request):
        return {
            "trajectories": [
                {
                    "trajectory_id": "broken",
                    "narrative": "broken ordering",
                    "states": [
                        {"state_id": "a", "parent_state_id": "ROOT"},
                        {"state_id": "b", "parent_state_id": "wrong-parent"},
                    ],
                }
            ]
        }

    with pytest.raises(PredictiveNarrativeError, match="ordering/parent continuity"):
        simulate_and_evaluate(
            _action(),
            all_pass_invariants(),
            _epistemic(),
            narrative_generator=broken_generator,
            local_validator=_local_pass,
            trajectory_validator=_trajectory_pass,
        )


class _AuthorizedController:
    def __init__(self) -> None:
        self.calls = 0

    def authorized_tick(self, *, source):
        self.calls += 1
        state_hash72 = "S" * 72
        receipt_hash72 = "R" * 72
        return {
            "runtime": {"state_hash72": state_hash72},
            "receipt": {
                "state_hash72": state_hash72,
                "receipt_hash72": receipt_hash72,
            },
            "authority_audit": {
                "ok": True,
                "state_hash72": state_hash72,
                "receipt_hash72": receipt_hash72,
            },
        }


def test_existing_vm81_bridge_is_entered_only_after_predictive_pass():
    controller = _AuthorizedController()
    result = simulate_admit_and_execute_local(
        _action(),
        all_pass_invariants(),
        _epistemic(),
        narrative_generator=_generator,
        local_validator=_local_pass,
        trajectory_validator=_trajectory_pass,
        context=_context(),
        controller=controller,
    )
    assert controller.calls == 1
    assert result["execution_candidate"] is True
    assert result["canonical_vm81_mutation_performed"] is True


def test_long_horizon_denial_never_calls_vm81_runtime():
    controller = _AuthorizedController()

    def trajectory_validator(_request):
        return NarrativeFinding(
            finding_id="deny-before-runtime",
            perspective="LONG_HORIZON_INHERITANCE",
            material=True,
            invariant_results=(
                EthicalInvariantResult(
                    invariant_id="E06_EXTERNALITY_CLOSURE",
                    state=InvariantState.FAIL,
                ),
            ),
        )

    result = simulate_admit_and_execute_local(
        _action(),
        all_pass_invariants(),
        _epistemic(),
        narrative_generator=_generator,
        local_validator=_local_pass,
        trajectory_validator=trajectory_validator,
        context=_context(),
        controller=controller,
    )
    assert controller.calls == 0
    assert result["execution_candidate"] is False
    assert result["canonical_vm81_mutation_performed"] is False

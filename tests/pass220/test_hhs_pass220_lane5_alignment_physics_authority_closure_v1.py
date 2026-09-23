from copy import deepcopy

import pytest

from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v1 import (
    ActionCandidate,
    EthicalInvariantResult,
    InvariantState,
    all_pass_invariants,
)
from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v2 import (
    EpistemicAdequacyTrace,
    evaluate_action_v2,
)
from hhs_runtime.hhs_pass219_vm81_admission_bridge_v1 import (
    VM81AdmissionBridgeError,
    admit_and_execute_local,
)
from hhs_runtime.hhs_pass220_lane5_alignment_physics_authority_closure_v1 import (
    Pass220I043AuthorityError,
    build_lane5_alignment_physics_authority_witness,
    lane5_alignment_physics_authority_self_test,
)
from hhs_runtime.hhs_pass220_quantum_geometric_unification_closure_v1 import (
    quantum_geometric_unification_witness,
)

STATE_HASH72 = "S" * 72
RECEIPT_HASH72 = "R" * 72


def _action() -> ActionCandidate:
    return ActionCandidate(
        action_id="I043-TEST-ACTION",
        intent="exercise joint alignment math physics authority",
        requested_scope=("relay.cooling",),
        minimum_necessary_scope=("relay.cooling",),
        granted_scope=("relay.cooling",),
        reversible=True,
        authority_source_ids=("I043-TEST",),
    )


def _epistemic() -> EpistemicAdequacyTrace:
    return EpistemicAdequacyTrace(
        observation_integrity=InvariantState.PASS,
        causal_attribution_integrity=InvariantState.PASS,
        action_relevance_sufficiency=InvariantState.PASS,
    )


def _refined(declared=None):
    return evaluate_action_v2(
        _action(),
        tuple(declared) if declared is not None else all_pass_invariants(),
        _epistemic(),
    )


class _FakeController:
    def __init__(self):
        self.calls = []

    def authorized_tick(self, source: str):
        self.calls.append(source)
        return {
            "runtime": {"step": 1, "state_hash72": STATE_HASH72},
            "receipt": {
                "state_hash72": STATE_HASH72,
                "receipt_hash72": RECEIPT_HASH72,
            },
            "authority_audit": {
                "ok": True,
                "state_hash72": STATE_HASH72,
                "receipt_hash72": RECEIPT_HASH72,
            },
        }


def test_i043_joint_authority_closes_without_reimplementing_alignment():
    witness = build_lane5_alignment_physics_authority_witness(_refined())
    ethical = witness["ethical_authority"]

    assert witness["joint_authority_closed"] is True
    assert ethical["alignment_authority_closed"] is True
    assert ethical["alignment_decision_reimplemented"] is False
    assert ethical["alignment_invariant_reclassification_performed"] is False
    assert ethical["ethical_decision_preserved_verbatim"] == (
        "EXECUTE_LOCAL_PROVISIONAL"
    )
    assert all(
        row["trinary"] == 1
        for row in ethical["ordered_invariant_projection"]
    )
    assert witness["math_authority_closed"] is True
    assert witness["physics_authority_closed"] is True
    assert witness["fabric_authority_closed"] is True
    assert witness["ancestry_root_shared"] is True
    assert witness["canonical_vm81_mutation_authority"] is False


def test_i043_failed_existing_alignment_has_no_joint_transition():
    declared = list(all_pass_invariants())
    first = declared[0]
    declared[0] = EthicalInvariantResult(
        invariant_id=first.invariant_id,
        state=InvariantState.FAIL,
        rationale="explicit test failure",
    )

    witness = build_lane5_alignment_physics_authority_witness(
        _refined(declared)
    )

    assert witness["joint_authority_closed"] is False
    assert witness["ethical_authority"]["alignment_authority_closed"] is False
    assert witness["misaligned_state_canonical_transition"] is False


def test_i043_rejects_any_math_witness_drift():
    tampered = deepcopy(quantum_geometric_unification_witness())
    tampered["ok"] = False

    with pytest.raises(Pass220I043AuthorityError, match="math witness drift"):
        build_lane5_alignment_physics_authority_witness(
            _refined(),
            math_witness=tampered,
        )


def test_pass219_bridge_requires_i043_before_vm81_mutation(monkeypatch):
    import hhs_runtime.hhs_pass220_lane5_alignment_physics_authority_closure_v1 as i043

    def _fail_gate(_refined):
        raise Pass220I043AuthorityError("forced physics closure failure")

    monkeypatch.setattr(
        i043,
        "require_lane5_alignment_physics_authority",
        _fail_gate,
    )
    controller = _FakeController()

    with pytest.raises(
        VM81AdmissionBridgeError,
        match="Lane 5 alignment/math/physics authority",
    ):
        admit_and_execute_local(
            _action(),
            all_pass_invariants(),
            _epistemic(),
            controller=controller,
        )

    assert controller.calls == []


def test_pass219_bridge_carries_i043_witness_on_success():
    controller = _FakeController()
    result = admit_and_execute_local(
        _action(),
        all_pass_invariants(),
        _epistemic(),
        controller=controller,
    )

    assert result["execution_allowed"] is True
    assert result["canonical_vm81_mutation_performed"] is True
    assert len(controller.calls) == 1
    joint = result["lane5_alignment_physics_authority"]
    assert joint["joint_authority_closed"] is True
    assert joint["misaligned_state_canonical_transition"] is False
    assert joint["current_repository_alignment_logic_preserved"] is True
    assert ":I043:" in controller.calls[0]


def test_i043_self_test_closes_read_only_authority_surface():
    result = lane5_alignment_physics_authority_self_test()
    assert result["ok"] is True
    witness = result["result"]
    assert witness["joint_authority_closed"] is True
    assert witness["alignment_authority_closed"] is True
    assert witness["math_authority_closed"] is True
    assert witness["physics_authority_closed"] is True
    assert witness["fabric_authority_closed"] is True
    assert witness["ancestry_root_shared"] is True
    assert witness["misaligned_state_canonical_transition"] is False
    assert witness["current_repository_alignment_logic_preserved"] is True
    assert witness["canonical_vm81_mutation_authority"] is False

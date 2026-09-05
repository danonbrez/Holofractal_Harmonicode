from __future__ import annotations

from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v1 import (
    ActionCandidate,
    InvariantState,
    all_pass_invariants,
)
from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v2 import EpistemicAdequacyTrace
from hhs_runtime.hhs_pass219_constitutional_ethics_membrane_v1 import (
    AuthorityPathTrace,
    ConstitutionalEthicsCandidate,
    EthicsState,
    ModalityInvariantTrace,
)
from hhs_runtime.hhs_pass219_vm81_admission_bridge_v1 import admit_and_execute_constitutional

STATE_HASH72 = "S" * 72
RECEIPT_HASH72 = "R" * 72
MANDATORY = ("truth", "human_protection", "authority_scope", "responsibility")


def _action():
    return ActionCandidate(
        action_id="relay",
        intent="preserve cooling",
        requested_scope=("relay.cooling",),
        minimum_necessary_scope=("relay.cooling",),
        granted_scope=("relay.cooling",),
        authority_source_ids=("standing-authority:relay.cooling",),
    )


def _epistemic():
    return EpistemicAdequacyTrace(
        observation_integrity=InvariantState.PASS,
        causal_attribution_integrity=InvariantState.PASS,
        action_relevance_sufficiency=InvariantState.PASS,
    )


def _constitutional(*, direct=True, composed=EthicsState.PASS):
    modality = ModalityInvariantTrace(
        modality_id="vm81-candidate",
        local_state=EthicsState.PASS,
        mandatory_invariants_present=MANDATORY,
        mandatory_invariants_preserved=MANDATORY,
    )
    return ConstitutionalEthicsCandidate(
        candidate_id="relay",
        modalities=(modality,),
        authority_path=AuthorityPathTrace(
            baseline_scope=("relay.cooling",),
            previous_scope=("relay.cooling",),
            candidate_scope=("relay.cooling",),
            direct_baseline_admissible=direct,
        ),
        composed_effect_state=composed,
    )


class _Controller:
    def __init__(self):
        self.calls = []

    def authorized_tick(self, source: str):
        self.calls.append(source)
        return {
            "runtime": {"state_hash72": STATE_HASH72},
            "receipt": {"state_hash72": STATE_HASH72, "receipt_hash72": RECEIPT_HASH72},
            "authority_audit": {"ok": True, "state_hash72": STATE_HASH72, "receipt_hash72": RECEIPT_HASH72},
        }


def test_constitutional_fail_never_reaches_vm81_controller():
    controller = _Controller()
    result = admit_and_execute_constitutional(
        _constitutional(direct=False), _action(), all_pass_invariants(), _epistemic(), controller=controller
    )
    assert result["constitutional_state"] == "FAIL"
    assert result["execution_allowed"] is False
    assert result["canonical_vm81_mutation_performed"] is False
    assert controller.calls == []


def test_composed_effect_fail_never_reaches_vm81_controller():
    controller = _Controller()
    result = admit_and_execute_constitutional(
        _constitutional(composed=EthicsState.FAIL), _action(), all_pass_invariants(), _epistemic(), controller=controller
    )
    assert result["constitutional_state"] == "FAIL"
    assert controller.calls == []


def test_constitutional_pass_continues_through_existing_singleton_bridge_once():
    controller = _Controller()
    result = admit_and_execute_constitutional(
        _constitutional(), _action(), all_pass_invariants(), _epistemic(), controller=controller
    )
    assert result["constitutional_state"] == "PASS"
    assert result["execution_allowed"] is True
    assert result["canonical_vm81_mutation_performed"] is True
    assert result["action_authority_minted"] is False
    assert len(controller.calls) == 1

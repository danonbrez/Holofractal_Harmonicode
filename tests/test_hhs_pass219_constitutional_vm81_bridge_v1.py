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
from hhs_runtime.hhs_pass219_modality_constitutional_trace_v1 import (
    CORE_MANDATORY_INVARIANTS,
    INTRINSIC_AUTHORITY_MODALITIES,
)
from hhs_runtime.hhs_pass219_vm81_admission_bridge_v1 import admit_and_execute_constitutional

STATE_HASH72 = "S" * 72
RECEIPT_HASH72 = "R" * 72
MANDATORY = CORE_MANDATORY_INVARIANTS


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


def _constitutional(*, direct=True, composed=EthicsState.PASS, mandatory=MANDATORY):
    modality = ModalityInvariantTrace(
        modality_id="vm81-candidate",
        local_state=EthicsState.PASS,
        mandatory_invariants_present=mandatory,
        mandatory_invariants_preserved=mandatory,
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

    def authorized_tick(self, source: str, *, constitutional_trace=None):
        self.calls.append((source, constitutional_trace))
        return {
            "runtime": {"state_hash72": STATE_HASH72},
            "receipt": {"state_hash72": STATE_HASH72, "receipt_hash72": RECEIPT_HASH72},
            "authority_audit": {"ok": True, "state_hash72": STATE_HASH72, "receipt_hash72": RECEIPT_HASH72},
            "constitutional_trace": dict(constitutional_trace),
            "constitutional_receipt_hash72": constitutional_trace["trace_receipt_hash72"],
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


def test_missing_root_modality_invariants_fail_closed_before_vm81():
    controller = _Controller()
    result = admit_and_execute_constitutional(
        _constitutional(mandatory=("HUMAN_PROTECTION",)),
        _action(), all_pass_invariants(), _epistemic(), controller=controller,
    )
    assert result["constitutional_state"] == "FAIL"
    assert any(
        item.startswith("LOCAL_MODALITY_FAIL:vm81-candidate")
        for item in result["constitutional_trace"]["failed_predicates"]
    )
    assert controller.calls == []


def test_constitutional_pass_binds_trace_and_executes_once():
    controller = _Controller()
    result = admit_and_execute_constitutional(
        _constitutional(), _action(), all_pass_invariants(), _epistemic(), controller=controller
    )
    assert result["constitutional_state"] == "PASS"
    assert result["execution_allowed"] is True
    assert result["canonical_vm81_mutation_performed"] is True
    assert result["action_authority_minted"] is False
    assert len(controller.calls) == 1
    source, trace = controller.calls[0]
    assert source.startswith("HHS_PASS219_CONSTITUTIONAL_ETHICAL_ADMISSION:")
    assert trace["state"] == "PASS"
    assert source.startswith(
        "HHS_PASS219_CONSTITUTIONAL_ETHICAL_ADMISSION:"
        + trace["trace_receipt_hash72"]
        + ":"
    )
    execution = result["vm81_execution"]
    assert execution["constitutional_receipt_hash72"] == trace["trace_receipt_hash72"]
    modality_ids = {item["modality_id"] for item in result["constitutional_trace"]["modalities"]}
    assert set(INTRINSIC_AUTHORITY_MODALITIES).issubset(modality_ids)


def test_intrinsic_authority_modalities_preserve_complete_root_invariant_set():
    controller = _Controller()
    result = admit_and_execute_constitutional(
        _constitutional(), _action(), all_pass_invariants(), _epistemic(), controller=controller
    )
    intrinsic = {
        item["modality_id"]: item
        for item in result["constitutional_trace"]["modalities"]
        if item["modality_id"] in INTRINSIC_AUTHORITY_MODALITIES
    }
    for modality_id in INTRINSIC_AUTHORITY_MODALITIES:
        trace = intrinsic[modality_id]
        assert set(CORE_MANDATORY_INVARIANTS).issubset(trace["mandatory_invariants_present"])
        assert set(CORE_MANDATORY_INVARIANTS).issubset(trace["mandatory_invariants_preserved"])
        assert trace["preservation_complete"] is True


def test_modality_specific_invariant_does_not_get_fabricated_onto_unrelated_surface():
    local = MANDATORY + ("VM81_LOCAL_EXACTNESS",)
    candidate = _constitutional(mandatory=local)
    controller = _Controller()
    result = admit_and_execute_constitutional(
        candidate, _action(), all_pass_invariants(), _epistemic(), controller=controller
    )
    upstream = next(
        item for item in result["constitutional_trace"]["modalities"]
        if item["modality_id"] == "vm81-candidate"
    )
    assert upstream["mandatory_invariants_present"] == list(local)
    assert upstream["mandatory_invariants_preserved"] == list(local)

from pathlib import Path

import pytest

from hhs_backend.runtime.hhs_pass220_i013_owned_lane5_handoff_v1 import (
    Pass220OwnedLane5HandoffGate,
)
from hhs_runtime.hhs_pass220_explicit_mutation_ownership_v1 import (
    CANONICAL_MUTATION_OWNER,
    HANDOFF_CONTRACT_VALID,
    INVARIANT_ID,
    LEDGER_EFFECT,
    NO_MUTATION_REQUIRED,
    PERSISTENCE_POLICY,
    PROPOSAL_ONLY,
    Pass220MutationOwnershipError,
    REJECT_I012_AUTHORITY_ESCALATION,
    REJECT_I012_NOT_ADMITTED,
    REJECT_MUTATION_LEDGER_EFFECT_MISSING,
    REJECT_MUTATION_OWNER_MISMATCH,
    REJECT_MUTATION_ROLLBACK_POLICY_MISSING,
    REJECT_MUTATION_SURFACE_WITHOUT_PERSISTENCE_POLICY,
    ROLLBACK_BEHAVIOR,
    build_mutation_ownership_witness,
    canonical_mutation_policy,
    verify_repository_authority_sources,
)


def _i012_admitted():
    return {
        "halt": False,
        "lane5_invoked": True,
        "harmonic_preflight_admitted": True,
        "canonical_vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "hash216_commit_authority": False,
    }


def _i012_blocked():
    return {
        "halt": False,
        "lane5_invoked": False,
        "harmonic_preflight_admitted": False,
        "canonical_vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "hash216_commit_authority": False,
    }


def _i012_halt():
    return {
        "halt": True,
        "lane5_invoked": False,
        "harmonic_preflight_admitted": None,
        "canonical_vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "hash216_commit_authority": False,
    }


def _valid_handoff():
    policy = canonical_mutation_policy()
    return build_mutation_ownership_witness(
        i012_result=_i012_admitted(),
        request_canonical_handoff=True,
        **policy,
    )


def test_canonical_policy_declares_all_hhs_i013_fields():
    policy = canonical_mutation_policy()
    assert INVARIANT_ID == "HHS-I013"
    assert policy == {
        "owner_surface": CANONICAL_MUTATION_OWNER,
        "persistence_policy": PERSISTENCE_POLICY,
        "rollback_behavior": ROLLBACK_BEHAVIOR,
        "ledger_effect": LEDGER_EFFECT,
    }


def test_genesis_halt_requires_no_mutation_handoff():
    witness = build_mutation_ownership_witness(
        i012_result=_i012_halt(),
        request_canonical_handoff=False,
    )
    assert witness["status"] == NO_MUTATION_REQUIRED
    assert witness["reason"] == NO_MUTATION_REQUIRED
    assert witness["owner_surface"] is None
    assert witness["mutation_performed"] is False
    assert witness["canonical_vm81_mutation_authority"] is False


def test_blocked_i012_cannot_construct_mutation_handoff():
    witness = build_mutation_ownership_witness(
        i012_result=_i012_blocked(),
        request_canonical_handoff=True,
        **canonical_mutation_policy(),
    )
    assert witness["status"] == "REJECTED"
    assert witness["reason"] == REJECT_I012_NOT_ADMITTED
    assert witness["handoff_contract_valid"] is False
    assert witness["mutation_performed"] is False


def test_admitted_candidate_remains_proposal_only_without_explicit_handoff():
    witness = build_mutation_ownership_witness(
        i012_result=_i012_admitted(),
        request_canonical_handoff=False,
    )
    assert witness["status"] == PROPOSAL_ONLY
    assert witness["i012_candidate_admitted"] is True
    assert witness["owner_surface"] is None
    assert witness["handoff_contract_valid"] is False
    assert witness["mutation_performed"] is False


def test_exact_inherited_owner_and_policy_yield_valid_handoff_contract_only():
    witness = _valid_handoff()
    assert witness["status"] == HANDOFF_CONTRACT_VALID
    assert witness["reason"] == HANDOFF_CONTRACT_VALID
    assert witness["handoff_contract_valid"] is True
    assert witness["owner_surface"] == CANONICAL_MUTATION_OWNER
    assert witness["owner_identity_is_not_mutation_authority"] is True
    assert witness["requires_inherited_pass219_environmental_admission"] is True
    assert witness["mutation_performed"] is False
    assert witness["canonical_vm81_mutation_authority"] is False
    assert witness["canonical_hash72_authority"] is False
    assert witness["canonical_hash216_authority"] is False


def test_wrong_mutation_owner_fails_closed():
    witness = build_mutation_ownership_witness(
        i012_result=_i012_admitted(),
        request_canonical_handoff=True,
        owner_surface="hhs_exact_pass219_vm81_pqc_admit_signed",
        persistence_policy=PERSISTENCE_POLICY,
        rollback_behavior=ROLLBACK_BEHAVIOR,
        ledger_effect=LEDGER_EFFECT,
    )
    assert witness["reason"] == REJECT_MUTATION_OWNER_MISMATCH
    assert witness["handoff_contract_valid"] is False


@pytest.mark.parametrize(
    "field,value,reason",
    [
        (
            "persistence_policy",
            "NONE",
            REJECT_MUTATION_SURFACE_WITHOUT_PERSISTENCE_POLICY,
        ),
        (
            "rollback_behavior",
            "NONE",
            REJECT_MUTATION_ROLLBACK_POLICY_MISSING,
        ),
        (
            "ledger_effect",
            "NONE",
            REJECT_MUTATION_LEDGER_EFFECT_MISSING,
        ),
    ],
)
def test_incomplete_or_wrong_policy_fails_closed(field, value, reason):
    policy = canonical_mutation_policy()
    policy[field] = value
    witness = build_mutation_ownership_witness(
        i012_result=_i012_admitted(),
        request_canonical_handoff=True,
        **policy,
    )
    assert witness["status"] == "REJECTED"
    assert witness["reason"] == reason
    assert witness["handoff_contract_valid"] is False


def test_i012_authority_escalation_is_rejected_as_invalid_input():
    result = _i012_admitted()
    result["canonical_vm81_mutation_authority"] = True
    with pytest.raises(Pass220MutationOwnershipError) as exc:
        build_mutation_ownership_witness(
            i012_result=result,
            request_canonical_handoff=False,
        )
    assert REJECT_I012_AUTHORITY_ESCALATION in str(exc.value)


def test_boolean_typing_is_exact():
    with pytest.raises(Pass220MutationOwnershipError):
        build_mutation_ownership_witness(
            i012_result=_i012_admitted(),
            request_canonical_handoff=1,
        )

    bad = _i012_admitted()
    bad["lane5_invoked"] = 1
    with pytest.raises(Pass220MutationOwnershipError):
        build_mutation_ownership_witness(
            i012_result=bad,
            request_canonical_handoff=False,
        )


def test_repository_sources_prove_single_production_mutation_owner():
    root = Path(__file__).resolve().parents[2]
    contract = (
        root
        / "contracts/pass219/PASS_219_VM81_EXTERNAL_ENVIRONMENTAL_AUTHORITY_RECONCILIATION_V1.md"
    ).read_text(encoding="utf-8")
    header = (
        root / "hhs_runtime/include/hhs_pass219_vm81_environmental_recovery_1_32.h"
    ).read_text(encoding="utf-8")

    witness = verify_repository_authority_sources(
        reconciliation_contract=contract,
        environmental_header=header,
    )
    assert witness["source_authority_closed"] is True
    assert witness["owner_surface"] == CANONICAL_MUTATION_OWNER
    assert witness["mutation_performed"] is False
    assert witness["canonical_vm81_mutation_authority"] is False


def test_source_authority_verifier_fails_if_owner_declaration_is_missing():
    with pytest.raises(Pass220MutationOwnershipError):
        verify_repository_authority_sources(
            reconciliation_contract="production dynamic mutation surface after reconciliation is",
            environmental_header="Production 1.32 successor",
        )


def test_witness_receipt_is_deterministic():
    assert _valid_handoff()["witness_sha256"] == _valid_handoff()["witness_sha256"]


class _FakeI012Gate:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def search_or_halt(self, **kwargs):
        self.calls.append(kwargs)
        return dict(self.result)

    def close(self):
        pass


def _owned_gate_call(gate, *, request=False, policy=None):
    values = {} if policy is None else dict(policy)
    return gate.search_and_bind_owner(
        current_offsets=(0,) * 81,
        next_offsets=(0,) * 81,
        nucleus_witnesses=(),
        global_modality_zero_closed=False,
        raw_5184_bit_state_change_zero=False,
        phase="xy",
        query={},
        candidates=(),
        tick=0,
        cycle_index=0,
        harmonic_nucleus_pairs=((2, 2),) * 9,
        request_canonical_handoff=request,
        **values,
    )


def test_composed_gate_keeps_admitted_candidate_proposal_only_without_handoff():
    fake = _FakeI012Gate(_i012_admitted())
    gate = Pass220OwnedLane5HandoffGate(gate=fake)
    result = _owned_gate_call(gate)
    assert result["mutation_ownership"]["status"] == PROPOSAL_ONLY
    assert result["canonical_handoff_contract_valid"] is False
    assert result["mutation_performed"] is False
    assert result["canonical_vm81_mutation_authority"] is False
    assert len(fake.calls) == 1


def test_composed_gate_builds_only_a_validated_owner_handoff_not_a_mutation():
    fake = _FakeI012Gate(_i012_admitted())
    gate = Pass220OwnedLane5HandoffGate(gate=fake)
    result = _owned_gate_call(
        gate,
        request=True,
        policy=canonical_mutation_policy(),
    )
    assert result["canonical_handoff_contract_valid"] is True
    assert result["mutation_ownership"]["owner_surface"] == CANONICAL_MUTATION_OWNER
    assert result["mutation_performed"] is False
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_receipt_authority"] is False


def test_composed_gate_cannot_promote_blocked_i012_result():
    fake = _FakeI012Gate(_i012_blocked())
    gate = Pass220OwnedLane5HandoffGate(gate=fake)
    result = _owned_gate_call(
        gate,
        request=True,
        policy=canonical_mutation_policy(),
    )
    assert result["canonical_handoff_contract_valid"] is False
    assert result["mutation_ownership"]["reason"] == REJECT_I012_NOT_ADMITTED
    assert result["mutation_performed"] is False

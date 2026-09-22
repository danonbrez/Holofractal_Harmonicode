from dataclasses import replace

import pytest

from hhs_runtime.hhs_pass220_genesis_law1_global_substitution_v1 import (
    COLLAPSE_CHAIN,
    GENESIS_LOCAL_TRIT_CODE,
    GENESIS_LOGICAL_TRITS,
    GLOBAL_EPSILON_COUNT,
    LAW1_CORRESPONDENCES,
    PALINDROMIC_PHASE_ROUTE,
    GenesisZeroRegisterDescriptor,
    GlobalSubstitutionProof,
    Pass220I029GenesisLawError,
    evaluate_global_substitution_authority,
    genesis_law1_self_test,
    genesis_serializer_witness,
    law1_hydration_witness,
    ordered_delta_e_witness,
)


def proof(hash_a="a" * 64, hash_b=None):
    right = hash_a if hash_b is None else hash_b
    return GlobalSubstitutionProof(
        left_branch_tree_sha256=hash_a,
        right_branch_tree_sha256=right,
        left_replay_sha256=hash_a,
        right_replay_sha256=right,
        lossless_interchangeability=True,
        global_invariant_preservation=True,
        ordered_provenance_preservation=True,
        serialization_receipt_preservation=True,
        no_unintended_downstream_delta=True,
        repository_pr_proof_evidence=True,
    )


def test_genesis_logical_register_is_5184_000_trit_positions():
    descriptor = GenesisZeroRegisterDescriptor()
    assert descriptor.symbolic_register == "0^5184"
    assert descriptor.logical_trit_count == 5184 == GENESIS_LOGICAL_TRITS
    assert descriptor.local_trit_code == (0, 0, 0) == GENESIS_LOCAL_TRIT_CODE
    materialized = descriptor.materialize()
    assert len(materialized) == 5184
    assert all(code == (0, 0, 0) for code in materialized)


def test_genesis_fast_path_binds_existing_fixed_width_serializer_without_retyping_offsets():
    witness = genesis_serializer_witness()
    assert witness["constant_size_fast_path"] is True
    assert witness["logical_trits_materialized_by_default"] is False
    assert witness["logical_trit_count"] == 5184
    assert witness["vm81_offset_count"] == 81
    assert witness["all_vm81_offsets_zero"] is True
    assert witness["canonical_serialized_characters"] == 5184
    assert witness["canonical_roundtrip"] is True
    assert witness[
        "physical_5184_character_offset_reinterpreted_as_logical_trit_index"
    ] is False


def test_delta_e_order_is_not_reversed_or_cancelled():
    witness = ordered_delta_e_witness((0,) * GLOBAL_EPSILON_COUNT)
    assert witness["ordered_object"] == ("Delta", "e")
    assert witness["ordered_closure_direction"] == "Deltae->0"
    assert witness["reverse_object_identity_admitted"] is False
    assert witness["zero_equals_delta_e_admitted"] is False
    assert witness["cancel_delta_from_zero_over_delta_admitted"] is False
    assert witness["commute_delta_and_e_admitted"] is False
    assert witness["all_global_epsilons_phase_cancelled"] is True


def test_one_active_global_epsilon_means_unlocked_delta_e_nonzero_state():
    eps = [0] * GLOBAL_EPSILON_COUNT
    eps[17] = 1
    witness = ordered_delta_e_witness(eps)
    assert witness["all_global_epsilons_phase_cancelled"] is False
    assert witness["delta_e_equals_zero_at_genesis_or_phase_lock"] is False
    assert witness["delta_e_nonzero_default_when_unlocked"] is True


def test_law1_hydration_preserves_exact_correspondence_and_collapse_order():
    witness = law1_hydration_witness()
    assert tuple(witness["law_of_1_correspondence_path"]) == LAW1_CORRESPONDENCES
    assert witness["law_of_1_correspondence_count"] == 12
    assert tuple(witness["collapse_chain_ordered"]) == COLLAPSE_CHAIN
    assert witness["collapse_chain_commutation_authority"] is False
    assert witness["collapse_chain_cancellation_authority"] is False
    assert tuple(witness["palindromic_phase_route"]) == PALINDROMIC_PHASE_ROUTE
    assert witness["palindromic_phase_route_self_reverse"] is True
    assert len(witness["lane5_pipeline_root_hash72"]) == 72
    assert len(witness["constructor_graph_root_hash72"]) == 72


def test_global_substitution_authority_requires_genesis_and_complete_equivalence():
    decision = evaluate_global_substitution_authority(
        left="A",
        right="B",
        global_epsilons=(0,) * GLOBAL_EPSILON_COUNT,
        proof=proof(),
    )
    assert decision["authorized"] is True
    assert decision["typed_global_closure_state"] == "Deltae=0/Delta"
    assert decision["global_scope_only"] is True
    assert decision["local_only_substitution_authority"] is False
    assert decision["special_condition_substitution_authority"] is False


def test_global_substitution_rejects_if_any_epsilon_survives_even_when_every_proof_hash_matches():
    eps = [0] * GLOBAL_EPSILON_COUNT
    eps[0] = -1
    decision = evaluate_global_substitution_authority(
        left="A", right="B", global_epsilons=eps, proof=proof()
    )
    assert decision["authorized"] is False
    assert decision["checks"]["genesis_or_global_phase_lock"] is False


def test_global_substitution_rejects_branch_or_replay_mismatch_at_genesis():
    mismatch = proof(hash_a="a" * 64, hash_b="b" * 64)
    decision = evaluate_global_substitution_authority(
        left="A",
        right="B",
        global_epsilons=(0,) * GLOBAL_EPSILON_COUNT,
        proof=mismatch,
    )
    assert decision["authorized"] is False
    assert decision["checks"]["complete_global_branch_tree_equivalence"] is False
    assert decision["checks"]["deterministic_replay_equivalence"] is False


def test_global_substitution_rejects_any_missing_downstream_or_repository_witness():
    base = proof()
    for field in (
        "lossless_interchangeability",
        "global_invariant_preservation",
        "ordered_provenance_preservation",
        "serialization_receipt_preservation",
        "no_unintended_downstream_delta",
        "repository_pr_proof_evidence",
    ):
        decision = evaluate_global_substitution_authority(
            left="A",
            right="B",
            global_epsilons=(0,) * GLOBAL_EPSILON_COUNT,
            proof=replace(base, **{field: False}),
        )
        assert decision["authorized"] is False
        assert decision["checks"][field] is False


def test_invalid_epsilon_shape_and_hash_fail_closed():
    with pytest.raises(Pass220I029GenesisLawError):
        ordered_delta_e_witness((0,) * 71)
    with pytest.raises(Pass220I029GenesisLawError):
        ordered_delta_e_witness((0,) * 71 + (2,))
    bad = replace(proof(), left_branch_tree_sha256="not-a-hash")
    with pytest.raises(Pass220I029GenesisLawError):
        evaluate_global_substitution_authority(
            left="A",
            right="B",
            global_epsilons=(0,) * GLOBAL_EPSILON_COUNT,
            proof=bad,
        )


def test_self_test_closes_without_authority_expansion():
    result = genesis_law1_self_test()
    assert result["ok"] is True
    assert result["authority_expansion"] is False

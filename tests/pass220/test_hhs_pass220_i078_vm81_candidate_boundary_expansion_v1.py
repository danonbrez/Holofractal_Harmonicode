from __future__ import annotations

from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_i078_vm81_candidate_boundary_expansion_v1 import (
    I078BoundaryError,
    VM81CandidateBoundaryExecutor,
)

LIB = Path("hhs_runtime/builds/libhhs_runtime.so")
pytestmark = pytest.mark.skipif(
    not LIB.exists(),
    reason="I078 native exact ABI library has not been built",
)


@pytest.fixture(scope="module")
def executor() -> VM81CandidateBoundaryExecutor:
    return VM81CandidateBoundaryExecutor(LIB)


def test_descriptor_binds_i077_and_exact_1001_scale(
    executor: VM81CandidateBoundaryExecutor,
) -> None:
    d = executor.descriptor
    assert d["node_count"] == 2
    assert d["frame_words"] == 81
    assert (d["scale_numerator"], d["scale_denominator"]) == (1001, 1000)
    assert (
        d["root_seed_numerator"],
        d["root_seed_denominator"],
    ) == (179971179971, 1000000)
    assert d["i077_binding_required"] is True
    assert d["downstream_candidate_ingress"] is True
    assert d["byte_exact_candidate_identity"] is True
    assert d["uqcel_identity_evaluation"] is True
    assert d["exact_rational_scale1001"] is True
    assert d["zero_energy_fixed_point"] is True
    assert d["delta_e_zero_required"] is True
    assert d["psi_zero_required"] is True
    assert d["omega_true_required"] is True
    assert d["deterministic_replay_required"] is True
    assert d["fail_closed_invalid_candidate"] is True

    for key in (
        "host_matrixpower_authority",
        "host_square_matrix_fallback_authority",
        "floating_point_authority",
        "numeric_exponent_evaluation_authority",
        "canonical_vm81_mutation_authority",
        "canonical_hash72_commit_authority",
        "canonical_hash216_commit_authority",
        "canonical_persistence_authority",
        "external_egress_authority",
    ):
        assert d[key] is False, key


def test_both_reference_candidates_expand_exactly(
    executor: VM81CandidateBoundaryExecutor,
) -> None:
    boundaries = [executor.expand_reference(0), executor.expand_reference(1)]
    assert [b.node_id for b in boundaries] == [0, 1]

    for b in boundaries:
        assert b.decision == 1
        assert b.reason == 0
        assert b.frame_words == 81
        assert (b.scale_numerator, b.scale_denominator) == (1001, 1000)
        assert b.scale_words_verified == 81
        assert b.zero_word_count > 0
        assert b.zero_fixed_point_words_verified == b.zero_word_count
        assert b.i077_execution_verified is True
        assert b.candidate_frame_exact is True
        assert b.uqcel_identity_evaluated is True
        assert b.uqcel_transition_matches_i077 is True
        assert b.exact_scale1001_verified is True
        assert b.zero_energy_fixed_point_verified is True
        assert b.delta_e_zero is True
        assert b.psi_zero is True
        assert b.omega_true is True
        assert b.deterministic_replay_verified is True
        assert b.fail_closed_boundary is True
        assert (b.delta_e_numerator, b.delta_e_denominator) == (0, 1)
        assert (b.psi_numerator, b.psi_denominator) == (0, 1)
        assert b.host_matrixpower_used is False
        assert b.square_matrix_fallback_used is False
        assert b.floating_point_used is False
        assert b.numeric_exponent_evaluated is False
        assert b.canonical_state_persisted is False
        assert len(b.candidate_sha256) == 64
        assert len(b.scale_witness_sha256) == 64
        assert len(b.i077_receipt_hash72) == 72
        assert len(b.i077_transition_hash216) == 216
        assert len(b.boundary_change_hash72) == 72
        assert len(b.boundary_receipt_hash72) == 72
        assert len(b.boundary_hash216) == 216
        assert len(b.boundary_identity216) == 216
        assert b.boundary_hash216.startswith(b.i077_receipt_hash72)

    assert boundaries[0].candidate_sha256 != boundaries[1].candidate_sha256
    assert boundaries[0].scale_witness_sha256 != boundaries[1].scale_witness_sha256
    assert (
        boundaries[0].boundary_identity216
        != boundaries[1].boundary_identity216
    )


def test_mutated_candidate_fails_closed(
    executor: VM81CandidateBoundaryExecutor,
) -> None:
    frame = executor.reference_candidate(0)
    frame.words[30] ^= 1
    with pytest.raises(I078BoundaryError):
        executor.expand(0, frame)


def test_invalid_node_id_fails_closed(
    executor: VM81CandidateBoundaryExecutor,
) -> None:
    with pytest.raises(I078BoundaryError):
        executor.reference_candidate(2)

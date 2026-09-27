from __future__ import annotations

import pytest

from hhs_runtime.pass219.lane5_nine_loop_foreign_equivalence_1_67 import (
    Lane5NineLoopEquivalenceError,
    bind_native_hash216,
    build_parallel_learning_metadata,
    canonical_bytes,
    prediction_deviation,
    verify_contract,
)


P1 = 2147483647
P2 = 2147483629
R1 = 829521918
R2 = 1173913588


def test_contract_and_exact_modular_oracle_close():
    receipt = verify_contract()
    assert all(receipt["checks"].values())
    assert receipt["sample_reconstructed_residues"] == [R1, R2]
    assert receipt["candidate_only"] is True
    assert receipt["canonical_authority"] is False


def test_prediction_deviation_is_exact_and_fail_closed():
    exact = prediction_deviation(
        residues={P1: R1, P2: R2},
        rational_numerator=-105757,
        rational_denominator=65536,
    )
    assert exact["exact_match"] is True
    assert exact["rational_match"] is True
    assert exact["residuals"] == [0, 0]
    assert exact["trinary"] == 0

    mismatch = prediction_deviation(residues={P1: R1 + 1, P2: R2})
    assert mismatch["exact_match"] is False
    assert mismatch["residuals"][0] == 1
    assert mismatch["trinary"] == -1


def test_parallel_metadata_distinguishes_unknown_source_from_verified_manifest():
    pending = build_parallel_learning_metadata()
    vector = pending["model_vs_harmonicode_v1"]
    assert vector["source_identity"] == -1
    assert vector["provenance"] == -1
    assert vector["hash216_replay"] == -1
    assert pending["native_hash216_required"] is True
    assert pending["hash216_replay_verified"] is False
    assert pending["canonical_transition_ready"] is False
    assert pending["candidate_only"] is True

    manifested = build_parallel_learning_metadata(
        artifact_manifest_sha256="ab" * 32
    )
    manifested_vector = manifested["model_vs_harmonicode_v1"]
    assert manifested_vector["source_identity"] == 0
    assert manifested_vector["provenance"] == 1


def test_floats_and_partial_rational_witnesses_are_rejected():
    with pytest.raises(Lane5NineLoopEquivalenceError):
        canonical_bytes({"forbidden": 1.0})
    with pytest.raises(Lane5NineLoopEquivalenceError):
        prediction_deviation(
            residues={P1: R1, P2: R2},
            rational_numerator=-105757,
        )


def test_native_hash216_binding_requires_replay_and_no_authority_leak():
    metadata = build_parallel_learning_metadata()
    candidate = "A" * 216
    receipt = {
        "candidate_hash216": candidate,
        "parent_1_66_verified": True,
        "monolithic_source_identity_verified": True,
        "foreign_delta_quarantine_verified": True,
        "exact_sample_oracle_verified": True,
        "structure_counts_verified": True,
        "dual_route_metadata_verified": True,
        "hash216_composition_validated": True,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_canonical_authority": False,
    }
    bound = bind_native_hash216(
        metadata,
        candidate_hash216=candidate,
        replay_hash216=candidate,
        native_receipt=receipt,
    )
    assert bound["hash216_replay_verified"] is True
    assert bound["model_vs_harmonicode_v1"]["hash216_replay"] == 0
    assert bound["canonical_transition_ready"] is False

    with pytest.raises(Lane5NineLoopEquivalenceError):
        bind_native_hash216(
            metadata,
            candidate_hash216=candidate,
            replay_hash216="B" * 216,
            native_receipt=receipt,
        )

    leaked = dict(receipt)
    leaked["canonical_hash216_authority"] = True
    with pytest.raises(Lane5NineLoopEquivalenceError):
        bind_native_hash216(
            metadata,
            candidate_hash216=candidate,
            replay_hash216=candidate,
            native_receipt=leaked,
        )

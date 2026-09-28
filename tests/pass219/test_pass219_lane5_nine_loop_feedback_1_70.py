from __future__ import annotations

import copy

import pytest

from hhs_runtime.pass219.lane5_nine_loop_feedback_1_70 import (
    FEEDBACK_PAYLOAD_SHA256,
    GENESIS_IDENTITY,
    Lane5NineLoopFeedbackError,
    bind_native_hash216,
    build_learning_feedback,
    load_contract,
    load_wolfram_receipt,
    verify_contract,
)


def _contains_float(value):
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_float(v) for v in value)
    return False


def test_contract_and_wolfram_receipt_close_exactly():
    receipt = verify_contract()
    assert all(receipt["checks"].values())
    assert receipt["feedback_payload_sha256"] == FEEDBACK_PAYLOAD_SHA256
    assert receipt["candidate_only"] is True
    assert receipt["canonical_transition_ready"] is False

    wolfram = load_wolfram_receipt()
    assert wolfram["status"] == "PASS"
    assert wolfram["check_count"] == 13
    assert wolfram["pass_count"] == 13
    assert wolfram["genesis_identity_verbatim"] == GENESIS_IDENTITY


def test_feedback_preserves_exact_coverage_and_deviation_semantics():
    feedback = build_learning_feedback()
    assert _contains_float(feedback) is False
    assert feedback["coverage_exact"]["certified_rational"] == {
        "numerator": 1014476,
        "denominator": 1018297,
    }
    assert feedback["coverage_exact"]["two_prime_only"] == {
        "numerator": 3821,
        "denominator": 1018297,
    }
    vector = feedback["deviation_vector"]
    assert vector["literal_container_identity_assumption"] == -1
    assert vector["logical_representation_equivalence"] == 1
    assert vector["support_geometry"] == 1
    assert vector["hash216_replay"] == 1
    assert vector["foreign_rational_reconstruction_complete"] == -1


def test_parent_relation_tamper_fails_closed():
    contract = copy.deepcopy(load_contract())
    contract["parent_evidence"]["relation_sha256"] = "0" * 64
    with pytest.raises(Lane5NineLoopFeedbackError, match="parent_relation_identity"):
        verify_contract(contract=contract, wolfram_receipt=load_wolfram_receipt())


def test_genesis_rewrite_fails_closed():
    contract = copy.deepcopy(load_contract())
    contract["exact_feedback"]["genesis_identity_verbatim"] = (
        "(x+y)^2+(x*y-a^2)^2+(a^2-b)^2+(a^4-2)^2"
    )
    with pytest.raises(Lane5NineLoopFeedbackError, match="genesis_identity_verbatim"):
        verify_contract(contract=contract, wolfram_receipt=load_wolfram_receipt())


def test_float_injection_fails_closed():
    contract = copy.deepcopy(load_contract())
    contract["exact_feedback"]["foreign_reconstruction_coverage"]["ratio"] = 0.996
    with pytest.raises(Lane5NineLoopFeedbackError, match="floating value forbidden"):
        verify_contract(contract=contract, wolfram_receipt=load_wolfram_receipt())


def test_wolfram_material_tamper_fails_closed():
    wolfram = copy.deepcopy(load_wolfram_receipt())
    wolfram["feedback_material_sha256"] = "f" * 64
    with pytest.raises(Lane5NineLoopFeedbackError, match="wolfram_exact_receipt"):
        verify_contract(contract=load_contract(), wolfram_receipt=wolfram)


def test_native_binding_requires_candidate_only_complete_receipt():
    feedback = build_learning_feedback()
    candidate = "Q" * 216
    receipt = {
        "accepted": True,
        "parent_1_69_verified": True,
        "relation_identity_verified": True,
        "wolfram_receipt_verified": True,
        "feedback_payload_verified": True,
        "coverage_verified": True,
        "genesis_identity_verified": True,
        "deviation_vector_verified": True,
        "hash216_replay_verified": True,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "feedback_candidate_hash216": candidate,
    }
    bound = bind_native_hash216(
        feedback,
        candidate_hash216=candidate,
        replay_hash216=candidate,
        native_receipt=receipt,
    )
    assert bound["native_hash216_replay_verified"] is True
    assert bound["candidate_only"] is True
    assert bound["canonical_transition_ready"] is False

    receipt["canonical_hash216_authority"] = True
    with pytest.raises(Lane5NineLoopFeedbackError, match="forbidden authority"):
        bind_native_hash216(
            feedback,
            candidate_hash216=candidate,
            replay_hash216=candidate,
            native_receipt=receipt,
        )

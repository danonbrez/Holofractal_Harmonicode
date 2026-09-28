from __future__ import annotations

import copy

import pytest

from hhs_runtime.pass219.lane5_nine_loop_training_specimen_1_71 import (
    GENESIS_IDENTITY,
    SPECIMEN_SHA256,
    Lane5NineLoopTrainingSpecimenError,
    bind_native_hash216,
    build_training_record,
    load_contract,
    load_specimen,
    verify_specimen,
)


def _contains_float(value):
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_float(v) for v in value)
    return False


def test_specimen_closes_as_exact_dataset_record():
    receipt = verify_specimen()
    assert all(receipt["checks"].values())
    assert receipt["training_specimen_sha256"] == SPECIMEN_SHA256
    assert receipt["training_feedback_label_count"] == 13
    assert receipt["learning_objective_count"] == 5
    assert receipt["deviation_feature_count"] == 16
    assert receipt["dataset_preparation_only"] is True
    assert receipt["model_weight_update_authority"] is False
    assert receipt["learning_commit_authority"] is False
    assert receipt["canonical_transition_ready"] is False

    record = build_training_record()
    assert _contains_float(record) is False
    assert record["exact_features"]["genesis_identity_verbatim"] == GENESIS_IDENTITY
    assert record["deviation_features"]["literal_container_identity_assumption"] == -1
    assert record["deviation_features"]["logical_representation_equivalence"] == 1
    assert record["deviation_features"]["foreign_rational_reconstruction_complete"] == -1


def test_specimen_content_tamper_fails_hash():
    specimen = copy.deepcopy(load_specimen())
    specimen["training_feedback_labels"][0] = "TAMPERED"
    with pytest.raises(Lane5NineLoopTrainingSpecimenError, match="specimen_sha256"):
        verify_specimen(specimen=specimen, contract=load_contract())


def test_negative_example_cannot_be_neutralized():
    specimen = copy.deepcopy(load_specimen())
    specimen["deviation_features"]["literal_container_identity_assumption"] = 0
    with pytest.raises(Lane5NineLoopTrainingSpecimenError):
        verify_specimen(specimen=specimen, contract=load_contract())


def test_float_injection_fails_closed():
    specimen = copy.deepcopy(load_specimen())
    specimen["exact_features"]["coordinate_coverage"]["ratio"] = 0.996
    with pytest.raises(Lane5NineLoopTrainingSpecimenError, match="floating value forbidden"):
        verify_specimen(specimen=specimen, contract=load_contract())


def test_weight_update_authority_fails_closed():
    specimen = copy.deepcopy(load_specimen())
    specimen["admission"]["model_weight_update_authority"] = True
    with pytest.raises(Lane5NineLoopTrainingSpecimenError):
        verify_specimen(specimen=specimen, contract=load_contract())


def test_genesis_rewrite_fails_closed():
    specimen = copy.deepcopy(load_specimen())
    specimen["exact_features"]["genesis_identity_verbatim"] = (
        "F=(x+y)^2+(xy-a^2)^2+(a^2-b)^2+(a^4-2)^2"
    )
    with pytest.raises(Lane5NineLoopTrainingSpecimenError):
        verify_specimen(specimen=specimen, contract=load_contract())


def test_native_binding_requires_dataset_only_receipt():
    record = build_training_record()
    candidate = "R" * 216
    receipt = {
        "accepted": True,
        "parent_1_70_verified": True,
        "specimen_identity_verified": True,
        "source_lineage_verified": True,
        "negative_example_verified": True,
        "dataset_scope_verified": True,
        "hash216_replay_verified": True,
        "candidate_only": True,
        "model_weight_update_authority": False,
        "learning_commit_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "training_candidate_hash216": candidate,
    }
    bound = bind_native_hash216(
        record,
        candidate_hash216=candidate,
        replay_hash216=candidate,
        native_receipt=receipt,
    )
    assert bound["native_hash216_replay_verified"] is True
    assert bound["model_weight_update_authority"] is False
    assert bound["learning_commit_authority"] is False

    receipt["learning_commit_authority"] = True
    with pytest.raises(Lane5NineLoopTrainingSpecimenError, match="forbidden authority"):
        bind_native_hash216(
            record,
            candidate_hash216=candidate,
            replay_hash216=candidate,
            native_receipt=receipt,
        )

from __future__ import annotations

import copy

import pytest

from hhs_runtime.pass219.lane5_nine_loop_relation_dataset_1_72 import (
    DATASET_SHA256,
    RECORD_CHAIN_SHA256,
    Lane5NineLoopRelationDatasetError,
    build_relation_training_records,
    load_contract,
    load_dataset,
    verify_dataset,
)


def _contains_float(value):
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_float(v) for v in value)
    return False


def test_dataset_closes_exactly():
    receipt = verify_dataset()
    assert all(receipt["checks"].values())
    assert receipt["dataset_sha256"] == DATASET_SHA256
    assert receipt["ordered_record_chain_sha256"] == RECORD_CHAIN_SHA256
    assert receipt["record_count"] == 12
    assert receipt["class_partition"] == {
        "additive": 6,
        "neutral": 4,
        "negative": 2,
    }
    assert receipt["dataset_preparation_only"] is True
    assert receipt["model_weight_update_authority"] is False
    assert receipt["learning_commit_authority"] is False

    records = build_relation_training_records()
    assert len(records) == 12
    assert _contains_float(records) is False
    assert records[6]["record_id"] == "literal_container_identity_rejected"
    assert records[6]["deviation_class"] == -1
    assert records[7]["record_id"] == "rational_reconstruction_partition"
    assert records[7]["deviation_class"] == -1
    assert records[-1]["record_id"] == "authority_boundary"


def test_reordering_fails_closed():
    dataset = copy.deepcopy(load_dataset())
    dataset["records"][0], dataset["records"][1] = dataset["records"][1], dataset["records"][0]
    with pytest.raises(Lane5NineLoopRelationDatasetError):
        verify_dataset(dataset=dataset, contract=load_contract())


def test_negative_example_relabel_fails_closed():
    dataset = copy.deepcopy(load_dataset())
    dataset["records"][6]["deviation_class"] = 0
    with pytest.raises(Lane5NineLoopRelationDatasetError):
        verify_dataset(dataset=dataset, contract=load_contract())


def test_rational_completion_overclaim_fails_closed():
    dataset = copy.deepcopy(load_dataset())
    dataset["records"][7]["observed_features"]["complete"] = True
    with pytest.raises(Lane5NineLoopRelationDatasetError):
        verify_dataset(dataset=dataset, contract=load_contract())


def test_foreign_delta_alias_fails_closed():
    dataset = copy.deepcopy(load_dataset())
    dataset["records"][10]["observed_features"]["native_delta_alias_authorized"] = True
    with pytest.raises(Lane5NineLoopRelationDatasetError):
        verify_dataset(dataset=dataset, contract=load_contract())


def test_authority_promotion_fails_closed():
    dataset = copy.deepcopy(load_dataset())
    dataset["admission"]["model_weight_update_authority"] = True
    with pytest.raises(Lane5NineLoopRelationDatasetError):
        verify_dataset(dataset=dataset, contract=load_contract())


def test_float_injection_fails_closed():
    dataset = copy.deepcopy(load_dataset())
    dataset["records"][1]["observed_features"]["coverage"] = 0.5
    with pytest.raises(Lane5NineLoopRelationDatasetError, match="floating value forbidden"):
        verify_dataset(dataset=dataset, contract=load_contract())

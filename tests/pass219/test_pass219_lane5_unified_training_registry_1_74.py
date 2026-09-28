from __future__ import annotations

from copy import deepcopy

import pytest

from hhs_python.runtime.hhs_pass219_lane5_unified_training_bridge import (
    Pass219Lane5UnifiedTrainingBridge,
)
from hhs_runtime.pass219.lane5_unified_training_registry_1_74 import (
    EXPECTED_METHOD_IDS,
    UnifiedTrainingRegistryError,
    load_registry,
    validate_registry,
)


TEMPORAL_NAMES = {
    1: "REALTIME",
    2: "MANUAL",
    3: "BATCH",
    4: "REPLAY",
    5: "ROUND_TRIP",
    6: "REPOSITORY_DELTA",
}

TARGET_NAMES = {
    1: "RELATION",
    2: "CONSTRUCTOR",
    3: "INVARIANT",
    4: "WEIGHT",
    5: "CODEC",
    6: "SCHEDULE",
    7: "PROOF",
    8: "BEHAVIOR",
    9: "REPOSITORY_TRANSITION",
}


def test_repository_registry_is_complete_and_path_bound() -> None:
    receipt = validate_registry()
    assert receipt["method_count"] == 19
    assert tuple(receipt["method_ids"]) == EXPECTED_METHOD_IDS
    assert receipt["all_producers_exist"] is True
    assert receipt["ethical_text_supervisor"] == "ETHICAL_TEXT"
    assert receipt["candidate_only"] is True


def test_repository_registry_matches_native_c_abi() -> None:
    registry = load_registry()
    bridge = Pass219Lane5UnifiedTrainingBridge()
    native = bridge.methods()

    assert len(native) == registry["method_count"] == 19

    for manifest, method in zip(registry["methods"], native, strict=True):
        assert manifest["mode"] == method["mode"]
        assert manifest["method_id"] == method["method_id"]
        assert manifest["temporal"] == TEMPORAL_NAMES[method["temporal"]]
        assert manifest["primary_target"] == TARGET_NAMES[method["primary_target"]]
        assert method["routes_through_vm5184"] is True
        assert method["emits_candidate_hash216"] is True
        assert method["candidate_only"] is True

        if manifest["natural_language_policy"] == "REQUIRED":
            assert method["natural_language_native"] is True
        else:
            assert method["natural_language_native"] is False

        assert bool(manifest.get("ethical_text_supervisor", False)) is bool(
            method["ethical_text_supervisor"]
        )


def test_registry_rejects_missing_producer() -> None:
    registry = deepcopy(load_registry())
    registry["methods"][0]["producer"] = "does/not/exist.py"
    with pytest.raises(UnifiedTrainingRegistryError, match="missing producer paths"):
        validate_registry(registry)


def test_registry_rejects_language_supervisor_drift() -> None:
    registry = deepcopy(load_registry())
    ethical = next(
        item for item in registry["methods"]
        if item["method_id"] == "ETHICAL_TEXT"
    )
    ethical["ethical_text_supervisor"] = False

    with pytest.raises(
        UnifiedTrainingRegistryError,
        match="ethical supervisor cardinality mismatch",
    ):
        validate_registry(registry)


def test_registry_rejects_authority_escalation() -> None:
    registry = deepcopy(load_registry())
    registry["authority"]["canonical_hash216_authority"] = True
    with pytest.raises(
        UnifiedTrainingRegistryError,
        match="authority escalation:canonical_hash216_authority",
    ):
        validate_registry(registry)


def test_bounded_generalization_is_method_19_and_parent_bound() -> None:
    registry = load_registry()
    bounded = registry["methods"][-1]
    assert bounded["mode"] == 19
    assert bounded["method_id"] == "BOUNDED_TOKEN_GENERALIZATION"
    assert bounded["parent_version"] == "1.73"
    assert (
        bounded["producer"]
        == "hhs_runtime/pass219/lane5_nine_loop_generalization_1_73.py"
    )

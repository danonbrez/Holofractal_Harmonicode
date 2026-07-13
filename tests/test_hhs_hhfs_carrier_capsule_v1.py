import copy
import pytest

from hhs_runtime.hhs_hhfs_carrier_capsule_v1 import (
    ADMIT_HHFS_CARRIER_CAPSULE,
    CANONICAL_CAPSULE_FIELD_ORDER,
    CARRIER_PROFILES,
    REJECT_CAPSULE_HASH_MISMATCH,
    REJECT_CARRIER_NATIVE_WITNESS_LANE_MISMATCH,
    REJECT_DUPLICATE_PAYLOAD_STORAGE,
    REJECT_EXTERNAL_SIDECAR_DEPENDENCY,
    REJECT_HHFS_FLOAT_CONSTANT,
    REJECT_MISSING_PAYLOAD_COMMITMENT,
    REJECT_PARALLEL_COMPUTATION_LANE,
    REJECT_PARALLEL_STORAGE_LANE,
    REJECT_TRANSFORMATION_HISTORY_REQUIRED,
    REJECT_UNSUPPORTED_CARRIER_PROFILE,
    canonical_capsule_fields,
    commit_payload_view,
    hhfs_carrier_capsule_self_test,
    make_hhfs_carrier_capsule,
    validate_hhfs_carrier_capsule,
)


def _roots():
    return {
        "payload_commitment": commit_payload_view({"carrier": "png", "view": "sample"}),
        "metadata_enhancement_root": "M" * 72,
        "transformation_trace_root": "T" * 72,
        "error_correction_root": "E" * 72,
    }


def _capsule():
    return make_hhfs_carrier_capsule(carrier_type="png", modality_type="image", **_roots())


def test_canonical_capsule_fields_are_complete_ordered_and_exact():
    fields = canonical_capsule_fields(carrier_type="png", modality_type="image", **_roots())
    assert tuple(fields.keys()) == CANONICAL_CAPSULE_FIELD_ORDER
    assert len(fields) == len(CANONICAL_CAPSULE_FIELD_ORDER)
    assert fields["carrier_native_witness_lane"] == CARRIER_PROFILES["png"]["native_witness_lane"]
    assert fields["payload_duplication_allowed"] is False
    assert fields["external_dependency_allowed"] is False
    assert fields["resonator_constant_q"] == "179971179971/1000000"
    assert fields["closure_constant_q"] == "1001/1000"


def test_payload_commitment_rejects_floats():
    with pytest.raises(ValueError):
        commit_payload_view({"bad": 1.001})


def test_valid_capsule_is_hash72_witnessed_and_ledgered():
    capsule = _capsule()
    result = validate_hhfs_carrier_capsule(capsule)
    assert result["status"] == ADMIT_HHFS_CARRIER_CAPSULE
    assert len(result["capsule_hash72"]) == 72
    assert result["payload_duplication_allowed"] is False
    assert result["no_parallel_storage"] is True
    assert result["no_parallel_computation"] is True
    assert result["unified_ledger"]["verified"] is True


def test_unsupported_carrier_profile_rejected():
    result = validate_hhfs_carrier_capsule({"carrier_type": "docx", "payload_commitment": "P", "transformation_trace_root": "T"})
    assert result["status"] == REJECT_UNSUPPORTED_CARRIER_PROFILE


def test_external_sidecar_dependency_rejected():
    capsule = _capsule()
    result = validate_hhfs_carrier_capsule({**capsule, "external_dependencies": ["file.hhs"]})
    assert result["status"] == REJECT_EXTERNAL_SIDECAR_DEPENDENCY


def test_duplicate_payload_storage_rejected():
    capsule = _capsule()
    assert validate_hhfs_carrier_capsule({**capsule, "raw_payload": "forbidden"})["status"] == REJECT_DUPLICATE_PAYLOAD_STORAGE
    fields = copy.deepcopy(capsule["canonical_capsule_fields"])
    fields["payload_duplication_allowed"] = True
    assert validate_hhfs_carrier_capsule({"canonical_capsule_fields": fields})["status"] == REJECT_DUPLICATE_PAYLOAD_STORAGE


def test_parallel_storage_and_computation_lanes_rejected():
    capsule = _capsule()
    fields = copy.deepcopy(capsule["canonical_capsule_fields"])
    fields["storage_lanes"] = [*fields["storage_lanes"], "shadow_archive"]
    assert validate_hhfs_carrier_capsule({"canonical_capsule_fields": fields})["status"] == REJECT_PARALLEL_STORAGE_LANE

    fields = copy.deepcopy(capsule["canonical_capsule_fields"])
    fields["computation_lanes"] = [*fields["computation_lanes"], "hidden_executor"]
    assert validate_hhfs_carrier_capsule({"canonical_capsule_fields": fields})["status"] == REJECT_PARALLEL_COMPUTATION_LANE


def test_missing_payload_commitment_and_trace_rejected():
    capsule = _capsule()
    fields = copy.deepcopy(capsule["canonical_capsule_fields"])
    fields["payload_commitment"] = ""
    assert validate_hhfs_carrier_capsule({"canonical_capsule_fields": fields})["status"] == REJECT_MISSING_PAYLOAD_COMMITMENT

    fields = copy.deepcopy(capsule["canonical_capsule_fields"])
    fields["transformation_trace_root"] = ""
    assert validate_hhfs_carrier_capsule({"canonical_capsule_fields": fields})["status"] == REJECT_TRANSFORMATION_HISTORY_REQUIRED


def test_carrier_native_lane_mismatch_rejected():
    capsule = _capsule()
    fields = copy.deepcopy(capsule["canonical_capsule_fields"])
    fields["carrier_native_witness_lane"] = "png.non_native_fake_lane"
    assert validate_hhfs_carrier_capsule({"canonical_capsule_fields": fields})["status"] == REJECT_CARRIER_NATIVE_WITNESS_LANE_MISMATCH


def test_float_and_hash_mismatch_rejected():
    capsule = _capsule()
    fields = copy.deepcopy(capsule["canonical_capsule_fields"])
    fields["loshu_anchor"] = 5.0
    assert validate_hhfs_carrier_capsule({"canonical_capsule_fields": fields})["status"] == REJECT_HHFS_FLOAT_CONSTANT

    tampered = copy.deepcopy(capsule)
    tampered["capsule_hash72"] = "X" * 72
    assert validate_hhfs_carrier_capsule(tampered)["status"] == REJECT_CAPSULE_HASH_MISMATCH


def test_hhfs_carrier_capsule_self_test_passes():
    result = hhfs_carrier_capsule_self_test()
    assert result["ok"] is True
    assert result["carrier_count"] >= 5
    assert result["canonical_capsule_field_count"] == len(CANONICAL_CAPSULE_FIELD_ORDER)

import copy

from hhs_runtime.hhs_hhfs_carrier_capsule_v1 import (
    _hash72,
    commit_payload_view,
    make_hhfs_carrier_capsule,
)
from hhs_runtime.hhs_metadata_enhancement_block_v1 import make_metadata_enhancement_block
from hhs_runtime.hhs_udfp_frame_v1 import (
    ADMIT_UDFP_FRAME,
    CANONICAL_UDFP_FRAME_FIELD_ORDER,
    REJECT_UDFP_FLOAT_CONSTANT,
    REJECT_UDFP_FRAME_HASH_MISMATCH,
    REJECT_UDFP_INVALID_CARRIER_CAPSULE,
    REJECT_UDFP_INVALID_METADATA_BLOCK,
    canonical_udfp_frame_fields,
    make_udfp_frame,
    udfp_frame_self_test,
    validate_udfp_frame,
)


def _parts():
    trace_root = _hash72("UDFP_TEST_TRACE", {"trace": ["capture"]}, width=72)
    metadata = make_metadata_enhancement_block(
        carrier_type="png",
        modality_type="image",
        capture_context={"sensor": "sample"},
        resolution_profile={"width": "1024", "height": "1024"},
        semantic_checksums={"scene": "sample"},
        observer_witness_id="TEST_OBSERVER",
        transformation_trace_root=trace_root,
    )
    capsule = make_hhfs_carrier_capsule(
        carrier_type="png",
        modality_type="image",
        payload_commitment=commit_payload_view({"carrier": "png", "view": "sample"}),
        metadata_enhancement_root=metadata["metadata_enhancement_root"],
        transformation_trace_root=trace_root,
        error_correction_root=_hash72("UDFP_TEST_ECC", {"ecc": "bounded"}, width=72),
    )
    return capsule, metadata


def test_udfp_frame_fields_are_complete_and_ordered():
    capsule, metadata = _parts()
    fields = canonical_udfp_frame_fields(carrier_capsule=capsule, metadata_block=metadata)
    assert tuple(fields.keys()) == CANONICAL_UDFP_FRAME_FIELD_ORDER
    assert fields["legacy_compatibility_required"] is True
    assert fields["no_parallel_storage_required"] is True
    assert fields["no_parallel_computation_required"] is True
    assert fields["duplicate_payload_storage_allowed"] is False
    assert fields["external_dependency_allowed"] is False


def test_valid_udfp_frame_is_hash72_witnessed_and_ledgered():
    capsule, metadata = _parts()
    frame = make_udfp_frame(carrier_capsule=capsule, metadata_block=metadata)
    result = validate_udfp_frame(frame)
    assert result["status"] == ADMIT_UDFP_FRAME
    assert len(result["current_frame_root"]) == 72
    assert result["no_parallel_storage"] is True
    assert result["no_parallel_computation"] is True
    assert result["unified_ledger"]["verified"] is True


def test_udfp_rejects_missing_invalid_or_mismatched_parts():
    capsule, metadata = _parts()
    frame = make_udfp_frame(carrier_capsule=capsule, metadata_block=metadata)
    assert validate_udfp_frame({"metadata_block": metadata})["status"] == REJECT_UDFP_INVALID_CARRIER_CAPSULE
    assert validate_udfp_frame({"carrier_capsule": capsule})["status"] == REJECT_UDFP_INVALID_METADATA_BLOCK

    bad_capsule = copy.deepcopy(capsule)
    fields = bad_capsule["canonical_capsule_fields"]
    fields["storage_lanes"] = [*fields["storage_lanes"], "shadow_archive"]
    assert validate_udfp_frame({**frame, "carrier_capsule": bad_capsule})["status"] == REJECT_UDFP_INVALID_CARRIER_CAPSULE

    bad_metadata = copy.deepcopy(metadata)
    bad_metadata["metadata_enhancement_root"] = "X" * 72
    assert validate_udfp_frame({**frame, "metadata_block": bad_metadata})["status"] == REJECT_UDFP_INVALID_METADATA_BLOCK


def test_udfp_rejects_float_and_frame_hash_mismatch():
    capsule, metadata = _parts()
    frame = make_udfp_frame(carrier_capsule=capsule, metadata_block=metadata)
    bad_float = copy.deepcopy(frame)
    bad_float["canonical_frame_fields"]["frame_index"] = 1.0
    assert validate_udfp_frame(bad_float)["status"] == REJECT_UDFP_FLOAT_CONSTANT

    tampered = copy.deepcopy(frame)
    tampered["current_frame_root"] = "X" * 72
    assert validate_udfp_frame(tampered)["status"] == REJECT_UDFP_FRAME_HASH_MISMATCH


def test_udfp_frame_self_test_passes():
    result = udfp_frame_self_test()
    assert result["ok"] is True
    assert result["canonical_frame_field_count"] == len(CANONICAL_UDFP_FRAME_FIELD_ORDER)

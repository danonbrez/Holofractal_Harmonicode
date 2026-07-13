import copy
import pytest

from hhs_runtime.hhs_hhfs_carrier_capsule_v1 import _hash72
from hhs_runtime.hhs_metadata_enhancement_block_v1 import (
    ADMIT_METADATA_ENHANCEMENT_BLOCK,
    CANONICAL_METADATA_FIELD_ORDER,
    REJECT_METADATA_DUPLICATE_PAYLOAD,
    REJECT_METADATA_FLOAT_CONSTANT,
    REJECT_METADATA_HASH_MISMATCH,
    REJECT_METADATA_TRANSFORMATION_TRACE_REQUIRED,
    REJECT_METADATA_UNSUPPORTED_CARRIER,
    canonical_metadata_fields,
    make_metadata_enhancement_block,
    metadata_enhancement_block_self_test,
    validate_metadata_enhancement_block,
)


def _trace_root():
    return _hash72("TEST_TRACE_ROOT", {"trace": ["capture"]}, width=72)


def _block():
    return make_metadata_enhancement_block(
        carrier_type="png",
        modality_type="image",
        capture_context={"sensor": "sample", "epoch_marker": "2026-02-28T16:45:12"},
        resolution_profile={"width": "512", "height": "512"},
        semantic_checksums={"scene": "sample"},
        observer_witness_id="TEST_OBSERVER",
        transformation_trace_root=_trace_root(),
    )


def test_metadata_fields_are_complete_ordered_and_commitments_only():
    fields = canonical_metadata_fields(
        carrier_type="png",
        modality_type="image",
        capture_context={"sensor": "sample"},
        resolution_profile={"width": "512", "height": "512"},
        semantic_checksums={"scene": "sample"},
        observer_witness_id="TEST_OBSERVER",
        transformation_trace_root=_trace_root(),
    )
    assert tuple(fields.keys()) == CANONICAL_METADATA_FIELD_ORDER
    assert fields["metadata_payload_policy"] == "commitments_only_no_duplicate_payload"
    assert len(fields["capture_context_commitment"]) == 72
    assert len(fields["resolution_profile_commitment"]) == 72
    assert len(fields["semantic_checksums"]["scene"]) == 72


def test_metadata_rejects_floats_during_construction_and_validation():
    with pytest.raises(ValueError):
        canonical_metadata_fields(
            carrier_type="png",
            modality_type="image",
            capture_context={"bad_float": 1.001},
            resolution_profile={"width": "512"},
            semantic_checksums={},
            observer_witness_id="TEST_OBSERVER",
            transformation_trace_root=_trace_root(),
        )
    block = _block()
    fields = copy.deepcopy(block["canonical_metadata_fields"])
    fields["loshu_anchor"] = 5.0
    assert validate_metadata_enhancement_block({"canonical_metadata_fields": fields})["status"] == REJECT_METADATA_FLOAT_CONSTANT


def test_valid_metadata_block_is_hash72_witnessed():
    block = _block()
    result = validate_metadata_enhancement_block(block)
    assert result["status"] == ADMIT_METADATA_ENHANCEMENT_BLOCK
    assert len(result["metadata_enhancement_root"]) == 72
    assert result["transformation_trace_required"] is True
    assert result["unified_ledger"]["verified"] is True


def test_metadata_rejects_unsupported_carrier_duplicate_payload_missing_trace_and_hash_mismatch():
    assert validate_metadata_enhancement_block({"carrier_type": "docx"})["status"] == REJECT_METADATA_UNSUPPORTED_CARRIER

    block = _block()
    assert validate_metadata_enhancement_block({**block, "payload_copy": "forbidden"})["status"] == REJECT_METADATA_DUPLICATE_PAYLOAD

    fields = copy.deepcopy(block["canonical_metadata_fields"])
    fields["transformation_trace_root"] = ""
    assert validate_metadata_enhancement_block({"canonical_metadata_fields": fields})["status"] == REJECT_METADATA_TRANSFORMATION_TRACE_REQUIRED

    tampered = copy.deepcopy(block)
    tampered["metadata_enhancement_root"] = "X" * 72
    assert validate_metadata_enhancement_block(tampered)["status"] == REJECT_METADATA_HASH_MISMATCH


def test_metadata_enhancement_block_self_test_passes():
    result = metadata_enhancement_block_self_test()
    assert result["ok"] is True
    assert result["canonical_metadata_field_count"] == len(CANONICAL_METADATA_FIELD_ORDER)

import copy
import shutil
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _clean_runtime_artifacts():
    root = Path(__file__).resolve().parents[1] / "data" / "runtime"
    shutil.rmtree(root, ignore_errors=True)
    yield
    shutil.rmtree(root, ignore_errors=True)

from hhs_runtime.hhs_hhfs_carrier_adapter_v1 import (
    ADMIT_HHFS_CARRIER_ADAPTER_OPERATION,
    REJECT_HHFS_ADAPTER_FLOAT,
    REJECT_HHFS_ADAPTER_INVALID_UDFP_FRAME,
    REJECT_HHFS_ADAPTER_MISSING_TRANSFORMATION_RECORD,
    REJECT_HHFS_ADAPTER_RECEIPT_HASH_MISMATCH,
    REJECT_HHFS_ADAPTER_UNSUPPORTED_OPERATION,
    execute_hhfs_carrier_adapter_operation,
    hhfs_carrier_adapter_self_test,
    validate_hhfs_carrier_adapter_record,
)
from hhs_runtime.hhs_hhfs_carrier_capsule_v1 import _hash72, commit_payload_view, make_hhfs_carrier_capsule
from hhs_runtime.hhs_metadata_enhancement_block_v1 import make_metadata_enhancement_block
from hhs_runtime.hhs_udfp_frame_v1 import make_udfp_frame


def _frame():
    trace_root = _hash72("ADAPTER_TEST_TRACE", {"trace": ["capture"]}, width=72)
    metadata = make_metadata_enhancement_block(
        carrier_type="png",
        modality_type="image",
        capture_context={"sensor": "test"},
        resolution_profile={"width": "64", "height": "64"},
        semantic_checksums={"scene": "adapter-test"},
        observer_witness_id="TEST",
        transformation_trace_root=trace_root,
    )
    capsule = make_hhfs_carrier_capsule(
        carrier_type="png",
        modality_type="image",
        payload_commitment=commit_payload_view({"carrier": "png", "view": "adapter-test"}),
        metadata_enhancement_root=metadata["metadata_enhancement_root"],
        transformation_trace_root=trace_root,
        error_correction_root=_hash72("ADAPTER_TEST_ECC", {"ecc": "bounded"}, width=72),
    )
    return make_udfp_frame(carrier_capsule=capsule, metadata_block=metadata)


def test_read_adapter_is_observation_receipted_not_mutation():
    record = execute_hhfs_carrier_adapter_operation(operation="read", udfp_frame=_frame())
    assert record["validation"]["status"] == ADMIT_HHFS_CARRIER_ADAPTER_OPERATION
    fields = record["canonical_adapter_fields"]
    assert fields["operation_class"] == "observation"
    assert fields["transformation_trace_required"] is False
    assert len(record["adapter_receipt_hash72"]) == 72
    assert record["residue_state_chain"]["validation"]["status"].startswith("ADMIT")


def test_repair_adapter_requires_and_records_transformation():
    record = execute_hhfs_carrier_adapter_operation(operation="repair", udfp_frame=_frame(), operation_parameters={"reason": "test"})
    assert record["validation"]["status"] == ADMIT_HHFS_CARRIER_ADAPTER_OPERATION
    fields = record["canonical_adapter_fields"]
    assert fields["operation_class"] == "mutation"
    assert fields["transformation_trace_required"] is True
    assert fields["transformation_record_hash72"] != "NO_TRANSFORMATION_RECORD_REQUIRED"
    assert record["transformation_validation"]["status"].startswith("ADMIT")


def test_adapter_rejects_invalid_operation_float_and_bad_frame():
    frame = _frame()
    assert execute_hhfs_carrier_adapter_operation(operation="erase", udfp_frame=frame)["status"] == REJECT_HHFS_ADAPTER_UNSUPPORTED_OPERATION
    assert execute_hhfs_carrier_adapter_operation(operation="read", udfp_frame=frame, operation_parameters={"bad": 1.001})["status"] == REJECT_HHFS_ADAPTER_FLOAT
    bad_frame = copy.deepcopy(frame)
    bad_frame["current_frame_root"] = "X" * 72
    assert execute_hhfs_carrier_adapter_operation(operation="read", udfp_frame=bad_frame)["status"] == REJECT_HHFS_ADAPTER_INVALID_UDFP_FRAME


def test_adapter_record_validation_rejects_hash_mismatch_and_missing_transform():
    record = execute_hhfs_carrier_adapter_operation(operation="repair", udfp_frame=_frame())
    bad = copy.deepcopy(record)
    bad["adapter_receipt_hash72"] = "X" * 72
    assert validate_hhfs_carrier_adapter_record(bad)["status"] == REJECT_HHFS_ADAPTER_RECEIPT_HASH_MISMATCH

    bad = copy.deepcopy(record)
    bad["canonical_adapter_fields"]["transformation_record_hash72"] = "NO_TRANSFORMATION_RECORD_REQUIRED"
    assert validate_hhfs_carrier_adapter_record(bad)["status"] == REJECT_HHFS_ADAPTER_MISSING_TRANSFORMATION_RECORD


def test_hhfs_carrier_adapter_self_test_passes():
    result = hhfs_carrier_adapter_self_test()
    assert result["ok"] is True
    assert result["repair_status"] == ADMIT_HHFS_CARRIER_ADAPTER_OPERATION

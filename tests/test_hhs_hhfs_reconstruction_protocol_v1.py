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

from hhs_runtime.hhs_hhfs_reconstruction_protocol_v1 import (
    CARRIER_INTACT,
    PAYLOAD_CORRUPTED_ECC_RECOVERABLE,
    PAYLOAD_CORRUPTED_ECC_UNRECOVERABLE,
    RECONSTRUCTED_WITH_WITNESS,
    RECONSTRUCTION_NOT_REQUIRED,
    REJECT_RECONSTRUCTION_FLOAT,
    REJECT_RECONSTRUCTION_INVALID_UDFP_FRAME,
    REJECT_RECONSTRUCTION_MISSING_ECC_ROOT,
    REJECT_RECONSTRUCTION_RECEIPT_HASH_MISMATCH,
    REJECT_RECONSTRUCTION_SILENT_REPAIR,
    WITNESS_CORRUPTED,
    WITNESS_INTACT_PAYLOAD_CORRUPTED,
    hhfs_reconstruction_protocol_self_test,
    reconstruct_hhfs_carrier,
    validate_hhfs_reconstruction_record,
)
from hhs_runtime.hhs_hhfs_carrier_capsule_v1 import _hash72, commit_payload_view, make_hhfs_carrier_capsule
from hhs_runtime.hhs_metadata_enhancement_block_v1 import make_metadata_enhancement_block
from hhs_runtime.hhs_udfp_frame_v1 import make_udfp_frame


def _frame(ecc=True):
    trace_root = _hash72("RECON_TEST_TRACE", {"trace": ["capture"]}, width=72)
    metadata = make_metadata_enhancement_block(
        carrier_type="png",
        modality_type="image",
        capture_context={"sensor": "test"},
        resolution_profile={"width": "128", "height": "128"},
        semantic_checksums={"scene": "recon-test"},
        observer_witness_id="TEST",
        transformation_trace_root=trace_root,
    )
    capsule = make_hhfs_carrier_capsule(
        carrier_type="png",
        modality_type="image",
        payload_commitment=commit_payload_view({"carrier": "png", "view": "recon-test"}),
        metadata_enhancement_root=metadata["metadata_enhancement_root"],
        transformation_trace_root=trace_root,
        error_correction_root=_hash72("RECON_TEST_ECC", {"ecc": "bounded"}, width=72) if ecc else "NO_ECC_ROOT_DECLARED",
    )
    return make_udfp_frame(carrier_capsule=capsule, metadata_block=metadata)


def test_intact_carrier_needs_no_reconstruction_but_is_receipted():
    record = reconstruct_hhfs_carrier(udfp_frame=_frame(), corruption_status=CARRIER_INTACT)
    assert record["validation"]["status"] == RECONSTRUCTION_NOT_REQUIRED
    assert record["canonical_reconstruction_fields"]["silent_repair_allowed"] is False
    assert len(record["reconstruction_receipt_hash72"]) == 72


def test_ecc_recoverable_corruption_reconstructs_with_witness():
    record = reconstruct_hhfs_carrier(udfp_frame=_frame(), corruption_status=PAYLOAD_CORRUPTED_ECC_RECOVERABLE)
    assert record["validation"]["status"] == RECONSTRUCTED_WITH_WITNESS
    fields = record["canonical_reconstruction_fields"]
    assert fields["transformation_receipt_required"] is True
    assert fields["adapter_receipt_hash72"] != "NO_RECONSTRUCTION_ADAPTER_REQUIRED"
    assert record["adapter_record"]["validation"]["status"].startswith("ADMIT")


def test_unrecoverable_or_witness_corruption_do_not_silently_repair():
    unrecoverable = reconstruct_hhfs_carrier(udfp_frame=_frame(), corruption_status=PAYLOAD_CORRUPTED_ECC_UNRECOVERABLE)
    assert unrecoverable["validation"]["status"] == WITNESS_INTACT_PAYLOAD_CORRUPTED
    witness_corrupt = reconstruct_hhfs_carrier(udfp_frame=_frame(), corruption_status=WITNESS_CORRUPTED)
    assert witness_corrupt["status"] == "RECONSTRUCTION_REJECTED_WITNESS_CORRUPTED"
    silent = reconstruct_hhfs_carrier(udfp_frame=_frame(), corruption_status=PAYLOAD_CORRUPTED_ECC_RECOVERABLE, reconstruction_parameters={"silent_repair_allowed": True})
    assert silent["status"] == REJECT_RECONSTRUCTION_SILENT_REPAIR


def test_reconstruction_rejects_bad_frame_float_and_missing_ecc():
    bad_frame = copy.deepcopy(_frame())
    bad_frame["current_frame_root"] = "X" * 72
    assert reconstruct_hhfs_carrier(udfp_frame=bad_frame)["status"] == REJECT_RECONSTRUCTION_INVALID_UDFP_FRAME
    assert reconstruct_hhfs_carrier(udfp_frame=_frame(), reconstruction_parameters={"bad": 1.001})["status"] == REJECT_RECONSTRUCTION_FLOAT
    assert reconstruct_hhfs_carrier(udfp_frame=_frame(ecc=False), corruption_status=PAYLOAD_CORRUPTED_ECC_RECOVERABLE)["status"] == REJECT_RECONSTRUCTION_MISSING_ECC_ROOT


def test_reconstruction_record_hash_mismatch_rejected():
    record = reconstruct_hhfs_carrier(udfp_frame=_frame(), corruption_status=PAYLOAD_CORRUPTED_ECC_RECOVERABLE)
    bad = copy.deepcopy(record)
    bad["reconstruction_receipt_hash72"] = "X" * 72
    assert validate_hhfs_reconstruction_record(bad)["status"] == REJECT_RECONSTRUCTION_RECEIPT_HASH_MISMATCH


def test_reconstruction_self_test_passes():
    result = hhfs_reconstruction_protocol_self_test()
    assert result["ok"] is True
    assert result["repaired_status"] == RECONSTRUCTED_WITH_WITNESS

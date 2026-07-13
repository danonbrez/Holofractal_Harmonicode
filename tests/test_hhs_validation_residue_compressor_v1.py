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

from hhs_runtime.hhs_validation_residue_compressor_v1 import (
    ADMIT_VALIDATION_RESIDUE_STATE_CHAIN,
    CANONICAL_COMPRESSED_STATE_FIELD_ORDER,
    CANONICAL_RESIDUE_RECEIPT_FIELD_ORDER,
    GENESIS_STATE_ROOT,
    REJECT_VALIDATION_RESIDUE_CHAIN_MISMATCH,
    REJECT_VALIDATION_RESIDUE_FLOAT,
    REJECT_VALIDATION_RESIDUE_PARALLEL_MEMORY_LANE,
    REJECT_VALIDATION_RESIDUE_PREVIOUS_STATE_MISMATCH,
    REJECT_VALIDATION_RESIDUE_RAW_CACHE_RETAINED,
    STATE_MACHINE,
    canonical_compressed_state_fields,
    commit_validation_residue,
    make_residue_receipt,
    make_validation_residue_state_chain,
    validate_validation_residue_state_chain,
    validation_residue_compressor_self_test,
)


def _residues():
    return [
        {"residue_class": "capsule_validation", "modality_type": "image", "validation_surface": "hhfs", "validation_status": "admitted", "source_receipt_hash72": "A" * 72},
        {"residue_class": "frame_validation", "modality_type": "multimodal", "validation_surface": "udfp", "validation_status": "admitted", "source_receipt_hash72": "B" * 72},
    ]


def test_residue_commitment_rejects_float_and_raw_cache_fields():
    with pytest.raises(ValueError):
        commit_validation_residue({"metric": 1.001})
    with pytest.raises(ValueError):
        commit_validation_residue({"raw_cache": {"too_much": True}})
    with pytest.raises(ValueError):
        commit_validation_residue({"persistence_lanes": ["raw_validation_cache"]})


def test_compressed_state_and_receipt_are_previous_state_chain():
    state = canonical_compressed_state_fields(residue=_residues()[0], state_index=0, previous_state_root=GENESIS_STATE_ROOT)
    assert tuple(state.keys()) == CANONICAL_COMPRESSED_STATE_FIELD_ORDER
    assert state["previous_state_root"] == GENESIS_STATE_ROOT
    assert state["raw_cache_retained"] is False
    assert state["parallel_memory_lane_allowed"] is False
    receipt = make_residue_receipt(state)
    assert tuple(receipt.keys()) == CANONICAL_RESIDUE_RECEIPT_FIELD_ORDER
    assert len(receipt["state_root_hash72"]) == 72
    assert len(receipt["transition_receipt_hash72"]) == 72


def test_valid_chain_compresses_residue_without_raw_payload():
    chain = make_validation_residue_state_chain(_residues())
    result = validate_validation_residue_state_chain(chain)
    assert result["status"] == ADMIT_VALIDATION_RESIDUE_STATE_CHAIN
    assert result["residue_count"] == 2
    assert result["receipt_count"] == 2
    assert result["final_state_root"] == chain["receipts"][-1]["state_root_hash72"]
    assert result["state_machine"] == STATE_MACHINE
    assert result["unified_ledger"]["verified"] is True
    assert "raw_cache_retained" in chain["canonical_chain_fields"]
    assert "unbounded_diagnostic_trace" not in str(chain)


def test_rejects_raw_cache_parallel_lane_and_floats_inside_chain():
    chain = make_validation_residue_state_chain(_residues())
    bad = copy.deepcopy(chain)
    bad["raw_cache"] = {"residue": "forbidden"}
    assert validate_validation_residue_state_chain(bad)["status"] == REJECT_VALIDATION_RESIDUE_RAW_CACHE_RETAINED

    bad = copy.deepcopy(chain)
    bad["canonical_chain_fields"]["parallel_memory_lane_allowed"] = True
    assert validate_validation_residue_state_chain(bad)["status"] == REJECT_VALIDATION_RESIDUE_PARALLEL_MEMORY_LANE

    bad = copy.deepcopy(chain)
    bad["canonical_chain_fields"]["residue_count"] = 2.0
    assert validate_validation_residue_state_chain(bad)["status"] == REJECT_VALIDATION_RESIDUE_FLOAT


def test_rejects_previous_state_and_receipt_mismatch():
    chain = make_validation_residue_state_chain(_residues())
    bad = copy.deepcopy(chain)
    bad["compressed_states"][1]["previous_state_root"] = "WRONG"
    assert validate_validation_residue_state_chain(bad)["status"] == REJECT_VALIDATION_RESIDUE_PREVIOUS_STATE_MISMATCH

    bad = copy.deepcopy(chain)
    bad["receipts"][0]["transition_receipt_hash72"] = "X" * 72
    assert validate_validation_residue_state_chain(bad)["status"] == REJECT_VALIDATION_RESIDUE_CHAIN_MISMATCH


def test_validation_residue_compressor_self_test_passes():
    result = validation_residue_compressor_self_test()
    assert result["ok"] is True
    assert result["receipt_count"] == 2
    assert len(result["final_state_root"]) == 72

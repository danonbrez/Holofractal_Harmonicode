"""I092 original native 216-index Hash216 parent preflight regression."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from hhs_runtime import hhs_pass220_i092_original_native_hash216_parent_preflight_v1 as mod


def test_original_candidate_is_not_historical_signed_parent_without_native_probe():
    r=mod.bind_i092_original_native_hash216_parent_preflight()
    assert r["schema"]==mod.SCHEMA
    assert len(r["original_candidate_hash216"])==216
    assert r["original_candidate_hash216"] == (
        r["candidate_previous_hash72"]
        +r["candidate_change_hash72"]
        +r["candidate_receipt_hash72"]
    )
    assert r["native_probe_supplied"] is False
    assert r["original_native_216_index_reference_verified"] is False
    assert r["original_native_parent_identity216"] is None
    assert r["original_native_hash216_index_tamper_rejected"] is False
    assert r["original_native_ordered_lane_reversal_distinguished"] is False
    assert r["native_reference_is_not_committed_state_ancestry"] is True
    assert r["native_signed_environmental_gate_not_invoked"] is True
    assert r["original_signed_gate_public_symbol"] == (
        "hhs_exact_pass219_vm81_environment_admit_signed"
    )
    assert r["authority"]==mod.NO_MUTATION_AUTHORITY
    assert r["candidate_only"] is True
    assert len(r["provenance_sha256"])==64


@pytest.mark.parametrize("kwargs",[
    {"opcode":-1},{"opcode":12},{"opcode":True},
    {"nucleus_index":-1},{"nucleus_index":9},{"nucleus_index":False},
    {"phase_channel":-1},{"phase_channel":8},{"phase_channel":True},
    {"native_reference_probe":""},{"native_reference_probe":1},
])
def test_bad_original_vm81_or_native_probe_type_is_rejected(kwargs):
    with pytest.raises((ValueError,TypeError)):
        mod.bind_i092_original_native_hash216_parent_preflight(**kwargs)


def test_bad_native_probe_path_is_not_replaced_by_python_evaluation():
    with pytest.raises(mod.I092NativePreflightError,match="actual compiled"):
        mod.bind_i092_original_native_hash216_parent_preflight(
            native_reference_probe="/not/a/real/original/native/reference/probe"
        )


def test_native_indexed_reference_corruption_and_order_when_native_probe_supplied():
    path=os.environ.get("HHS_PASS220_I092_NATIVE_HASH216_REFERENCE_PROBE")
    if not path:
        pytest.skip("actual original VM81 ABI native index probe not provided")
    assert Path(path).is_file()
    r=mod.bind_i092_original_native_hash216_parent_preflight(
        opcode=11,nucleus_index=8,phase_channel=7,
        native_reference_probe=path
    )
    assert r["native_probe_supplied"] is True
    assert r["original_native_216_index_reference_verified"] is True
    assert len(r["original_native_parent_identity216"])==216
    assert r["original_native_hash216_index_tamper_rejected"] is True
    assert r["original_native_ordered_lane_reversal_distinguished"] is True
    assert r["original_i065_candidate_hydration_roundtrip"] is True
    assert r["native_reference_operation_is_read_only"] is True
    assert r["native_reference_is_not_committed_state_ancestry"] is True
    assert r["native_signed_environmental_gate_not_invoked"] is True
    assert r["authority"]["canonical_Hash216_signed_transition"] is False
    assert r["authority"]["candidate_parent_proven_previously_committed"] is False


def test_source_identity_differs_across_original_typed_vm81_source_metadata():
    a=mod.bind_i092_original_native_hash216_parent_preflight(opcode=0)
    b=mod.bind_i092_original_native_hash216_parent_preflight(opcode=1)
    assert a["original_i090_source_identity_sha256"]!=b["original_i090_source_identity_sha256"]
    assert a["original_candidate_hash216"]!=b["original_candidate_hash216"]
    assert a["provenance_sha256"]!=b["provenance_sha256"]


def test_missing_or_swapped_source_candidate_lanes_cannot_be_silently_admitted(monkeypatch):
    original=mod.bind_i091_original_signed_vm81_admission
    def altered(**kwargs):
        p=original(**kwargs)
        value=p["original_i090_source_bound_parent_candidate_hash216"]
        p["original_i090_source_bound_parent_candidate_hash216"]=value[:71]
        return p
    monkeypatch.setattr(mod,"bind_i091_original_signed_vm81_admission",altered)
    with pytest.raises(mod.I092NativePreflightError,match="three-plane"):
        mod.bind_i092_original_native_hash216_parent_preflight()

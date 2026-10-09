"""I090 real Pass219 RNA binary VM81 and 5184-char normalization ingress."""
from __future__ import annotations

from copy import deepcopy
import os

import pytest

from hhs_runtime import hhs_pass220_i090_original_vm81_rna_bigint_5184_ingress_v1 as mod
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    build_execution_cases,raw_le_to_words,words_to_raw_le,
)


def test_original_frame_12_routes_and_actual_exact_two_modalities():
    r=mod.bind_i090_physical_vm81_ingress()
    assert r["vm81_words"]==81
    assert r["word_bits"]==64
    assert r["raw_frame_bytes"]==648
    assert r["raw_frame_bit_count"]==5184
    assert r["original_frame_bigint_bits_capacity"]==448
    assert r["original_glyph_words"]==72
    assert r["fixed_rational_scientific_character_count"]==5184
    assert r["fixed_rational_scientific_token_width"]==64
    assert r["normalized_81_offsets_count"]==81
    assert r["normalization_offsets"]==[0]*81
    assert r["raw_bit_view_exact_roundtrip"] is True
    assert r["raw_vm81_bit_view_is_i065_palindromic_binary_claim"] is False
    assert r["raw_frame_and_scientific_serialization_are_distinct_types"] is True
    assert r["all_twelve_raw_frames_exact_and_distinct"] is True
    assert [v["opcode"] for v in r["all_original_twelve_directional_frames"]] == list(range(12))
    assert len(set(v["raw_frame_sha256"] for v in r["all_original_twelve_directional_frames"]))==12
    assert r["selected_original_directional_metadata"]["opcode"]==0
    assert r["selected_original_bigint_integrity_verified"] is True
    assert len(r["selected_original_bigint_decimal"])>100
    assert len(r["normalization_source_sha256"])==64


def test_actual_original_first_and_last_frame_match_selected_route_and_metadata():
    fixture=build_execution_cases()
    for op in (0,1,5,6,11):
        r=mod.bind_i090_physical_vm81_ingress(opcode=op,nucleus_index=2,phase_channel=5)
        expected=fixture[op]
        assert r["selected_original_raw_vm81_sha256"]==expected["raw_sha256"]
        assert r["selected_original_directional_metadata"]==expected["restored"]["metadata"]
        assert r["selected_original_bigint_decimal"]==str(expected["bigint"])
        assert len(raw_le_to_words(expected["raw_bytes"]))==81
        assert words_to_raw_le(raw_le_to_words(expected["raw_bytes"]))==expected["raw_bytes"]


def test_nonzero_81_cell_normalization_remains_exact_and_changes_receipt():
    baseline=mod.bind_i090_physical_vm81_ingress()
    offsets=[0]*81
    offsets[7]=1
    offsets[80]=8
    shifted=mod.bind_i090_physical_vm81_ingress(normalization_offsets=offsets)
    assert shifted["normalized_81_offsets_count"]==81
    assert shifted["normalization_offsets"][7]==1
    assert shifted["normalization_offsets"][80]==8
    assert shifted["fixed_rational_scientific_character_count"]==5184
    assert shifted["selected_original_raw_vm81_sha256"]==baseline["selected_original_raw_vm81_sha256"]
    assert shifted["normalization_source_sha256"]!=baseline["normalization_source_sha256"]
    assert shifted["candidate_hash216"]!=baseline["candidate_hash216"]
    assert shifted["raw_frame_and_scientific_serialization_are_distinct_types"] is True


def test_source_bound_three_plane_hash216_preserves_parent_and_exact_binary():
    r=mod.bind_i090_physical_vm81_ingress()
    assert r["candidate_hash216"] == (
        r["candidate_previous_hash72"]+r["candidate_change_hash72"]
        +r["candidate_receipt_hash72"]
    )
    assert len(r["candidate_hash216"])==216
    for name in ("candidate_previous_hash72","candidate_change_hash72","candidate_receipt_hash72"):
        assert len(r[name])==72
    assert len(r["i089_source_bound_parent_candidate_hash216"])==216
    assert r["original_i065_hash216_three_plane_roundtrip"] is True
    assert len(r["source_binding_sha256"])==64
    assert r["authority"]==mod.AUTHORITY
    assert r["authority"]["mutation_authorized"] is False
    assert r["authority"]["signed_environmental_admission_invoked"] is False
    assert r["authority"]["candidate_hash72_not_ledger_mint"] is True
    assert r["candidate_only"] is True


@pytest.mark.parametrize("kwargs",[
    {"opcode":12},{"opcode":-1},{"opcode":True},{"opcode":0.0},
    {"nucleus_index":9},{"nucleus_index":False},
    {"phase_channel":-1},{"phase_channel":8},{"phase_channel":True},
    {"normalization_offsets":""},{"normalization_offsets":[0]*80},
    {"normalization_offsets":[0]*82},
    {"normalization_offsets":[False]+[0]*80},
    {"normalization_offsets":[1.0]+[0]*80},
    {"normalization_offsets":[9]+[0]*80},
    {"normalization_offsets":[-1]+[0]*80},
    {"native_probe":""},
])
def test_bad_opcode_address_offsets_and_probe_denied(kwargs):
    with pytest.raises(mod.I090IngressError):
        mod.bind_i090_physical_vm81_ingress(**kwargs)


def test_corrupted_original_rna_frame_identity_fails_closed(monkeypatch):
    orig=mod.build_execution_cases
    def bad():
        rows=orig()
        copy=deepcopy(rows)
        tampered=bytearray(copy[0]["raw_bytes"])
        tampered[0]^=1
        copy[0]["raw_bytes"]=bytes(tampered)
        return copy
    monkeypatch.setattr(mod,"build_execution_cases",bad)
    with pytest.raises((mod.I090IngressError,Exception),match="BIGINT_GLYPH|roundtrip|crosscheck"):
        mod.bind_i090_physical_vm81_ingress()


def test_original_native_cpp_rna_probe_runs_when_connected():
    native=os.environ.get("HHS_PASS219_BIGINT_RNA_NATIVE_PROBE")
    if not native:
        pytest.skip("original C++ RNA native ABI probe not supplied")
    r=mod.bind_i090_physical_vm81_ingress(native_probe=native)
    assert r["original_vm81_RNA_execution_probe_supplied"] is True
    assert r["original_vm81_RNA_cpp_route_executed"] is True
    assert r["original_native_RNA_conformance_verified"] is True
    assert len(r["original_native_probe_report_sha256"])==64
    assert r["authority"]["signed_environmental_admission_invoked"] is False


def test_repeated_identical_original_sources_yield_identical_receipts():
    assert mod.bind_i090_physical_vm81_ingress()==mod.bind_i090_physical_vm81_ingress()

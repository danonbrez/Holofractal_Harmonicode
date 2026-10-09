"""Pass220 I091 genuine original signed environmental VM81 acceptance tests.

Tests never infer that an I090 candidate Hash216 is identical to
the native verified genesis signing parent/child.
"""
from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path

import pytest

from hhs_runtime import hhs_pass220_i091_original_signed_vm81_environment_test_admission_v1 as mod
from hhs_runtime.pass219.vm81_rna_bigint_environment_admission_probe import (
    NEGATIVE_MODES,
)


def test_original_i090_source_is_preserved_without_signed_native_probe():
    r=mod.bind_i091_original_signed_vm81_admission(opcode=11,nucleus_index=8,phase_channel=7)
    assert r["schema"]==mod.SCHEMA
    assert r["original_i090_metadata"]["opcode"]==11
    assert r["original_i090_5184_physical_bit_roundtrip"] is True
    assert r["original_i090_scientific_source_not_identical_to_raw_frame"] is True
    assert len(r["original_i090_frame_sha256"])==64
    assert len(r["original_i090_5184_scientific_character_source_sha256"])==64
    assert len(r["original_i090_source_bound_parent_candidate_hash216"])==216
    assert r["native_test_probe_supplied"] is False
    assert r["native_signed_positive_test_executed"] is False
    assert r["native_signed_positive_test"] is None
    assert r["original_signed_environment_negative_modes_tested"]==[]
    assert r["all_four_original_signed_fail_closed_tests_passed"] is False
    assert r["native_original_twelve_case_suite_completed"] is False
    assert r["original_native_canonical_receipt_verified_in_test"] is False
    assert r["production_canonical_admission_verified"] is False
    assert r["real_native_signed_child_hash216_equals_I090_candidate_hash216_proven"] is False
    assert r["real_native_I090_parent_candidate_hash216_signed_as_genesis"] is False
    assert r["authority"]==mod.TEST_ONLY_AUTHORITY
    assert r["new_signed_mutation_api_created"] is False
    assert len(r["source_witness_sha256"])==64


@pytest.mark.parametrize("bad",[-1,12,True,False,1.0,"0",None])
def test_opcode_bad_type_or_range_denied_before_mutation(bad):
    with pytest.raises(mod.I091SignedAdmissionError,match="opcode"):
        mod.bind_i091_original_signed_vm81_admission(opcode=bad)


@pytest.mark.parametrize("kwargs",[
    {"nucleus_index":-1},{"nucleus_index":9},{"nucleus_index":True},
    {"phase_channel":-1},{"phase_channel":8},{"phase_channel":True},
    {"native_probe":""},{"native_probe":True},{"native_probe":[]},
    {"full_original_twelve_native_cases":1},
    {"full_original_twelve_native_cases":True},
])
def test_out_of_domain_original_vm81_or_signature_probe_denied(kwargs):
    with pytest.raises(mod.I091SignedAdmissionError):
        mod.bind_i091_original_signed_vm81_admission(**kwargs)


def test_inherited_parent_source_tamper_is_not_signed(monkeypatch):
    original=mod.bind_i090_physical_vm81_ingress
    def changed(**kwargs):
        value=original(**kwargs)
        value["candidate_hash216"]="A"*216
        return value
    monkeypatch.setattr(mod,"bind_i090_physical_vm81_ingress",changed)
    with pytest.raises(mod.I091SignedAdmissionError,match="candidate ancestry drift|source"):
        mod.bind_i091_original_signed_vm81_admission()


def test_bad_signed_native_receipt_flags_fail_closed():
    fields={name:1 for name in mod.REQUIRED_NATIVE_POSITIVE}
    fields.update({"status":0,"signature_length":3309,"environment_witness_sequence":1})
    raw=bytes(648)
    metadata={"opcode":0}
    with pytest.raises(Exception):
        mod._verify_positive(fields,raw,raw,metadata,0)
    for field in mod.REQUIRED_NATIVE_POSITIVE:
        changed=dict(fields)
        changed[field]=0
        with pytest.raises(mod.I091SignedAdmissionError,match="signed receipt"):
            mod._verify_positive(changed,raw,raw,metadata,0)


def test_forged_negative_commit_or_receipt_is_rejected():
    for mode in NEGATIVE_MODES:
        accepted={"status":0,"committed_zero":1,"canonical_receipt_minted":0}
        with pytest.raises(mod.I091SignedAdmissionError):
            mod._verify_negative(mode,accepted,bytes(648))
        minted={"status":100,"committed_zero":1,"canonical_receipt_minted":1}
        with pytest.raises(mod.I091SignedAdmissionError):
            mod._verify_negative(mode,minted,bytes(648))
        tampered={"status":100,"committed_zero":0,"canonical_receipt_minted":0}
        with pytest.raises(mod.I091SignedAdmissionError):
            mod._verify_negative(mode,tampered,bytes(648))
    with pytest.raises(mod.I091SignedAdmissionError):
        mod._verify_negative("not-supported",{"status":100},bytes(648))


def test_original_signed_entrance_is_only_one_public_boundary():
    assert mod.PUBLIC_SIGNED_FUNCTION=="hhs_exact_pass219_vm81_environment_admit_signed"
    assert mod.TEST_ONLY_AUTHORITY["only_original_pass219_signed_environment_entrypoint"] is True
    assert mod.TEST_ONLY_AUTHORITY["production_signing_key_or_environment_supplied"] is False
    assert mod.TEST_ONLY_AUTHORITY["I090_candidate_hash216_is_native_genesis_parent"] is False
    assert mod.TEST_ONLY_AUTHORITY["unsigned_vm81_mutation_permitted"] is False


def test_original_ml_dsa65_signed_environment_positive_and_four_negatives_when_available():
    path=os.environ.get("HHS_PASS219_BIGINT_ENVIRONMENT_NATIVE_PROBE")
    if not path:
        pytest.skip("original ML-DSA-65 signed VM81 test probe not supplied")
    assert Path(path).is_file(), "original signed native probe executable is required"
    r=mod.bind_i091_original_signed_vm81_admission(
        opcode=11,nucleus_index=8,phase_channel=7,native_probe=path
    )
    positive=r["native_signed_positive_test"]
    assert positive["original_signed_admission_verified"] is True
    assert positive["source_raw_committed_exact"] is True
    assert positive["ML_DSA_65_provider_verified"] is True
    assert positive["original_genesis_parent_hash216_verified_by_helper"] is True
    assert positive["original_signed_child_hash216_verified_by_helper"] is True
    assert positive["original_RNA_owns_canonical_receipt"] is True
    assert positive["original_test_root_not_production_key"] is True
    assert positive["committed_source_sha256"]==r["original_i090_frame_sha256"]
    assert r["all_four_original_signed_fail_closed_tests_passed"] is True
    assert {row["mode"] for row in r["original_signed_environment_negative_modes_tested"]}==set(NEGATIVE_MODES)
    assert all(row["committed_frame_all_zero"] for row in r["original_signed_environment_negative_modes_tested"])
    assert all(row["no_canonical_receipt_minted"] for row in r["original_signed_environment_negative_modes_tested"])
    assert r["original_native_canonical_receipt_verified_in_test"] is True
    assert r["real_native_signed_child_hash216_equals_I090_candidate_hash216_proven"] is False
    assert r["production_canonical_admission_verified"] is False


def test_original_all_twelve_signed_cases_and_negatives_when_available():
    path=os.environ.get("HHS_PASS219_BIGINT_ENVIRONMENT_NATIVE_PROBE")
    if not path:
        pytest.skip("original ML-DSA-65 signed VM81 test probe not supplied")
    r=mod.bind_i091_original_signed_vm81_admission(
        opcode=0,nucleus_index=0,phase_channel=0,
        native_probe=path,full_original_twelve_native_cases=True
    )
    assert r["native_original_twelve_case_suite_completed"] is True
    assert r["all_four_original_signed_fail_closed_tests_passed"] is True
    assert len(r["native_original_twelve_case_suite_report_sha256"])==64
    assert r["real_native_I090_parent_candidate_hash216_signed_as_genesis"] is False

from __future__ import annotations

import os

import pytest

from hhs_runtime.pass219.vm81_rna_bigint_environment_admission_probe import (
    NEGATIVE_MODES,
    vm81_rna_bigint_environment_admission_probe,
)


def test_environment_admission_probe_preserves_authority_boundary_without_native_probe() -> None:
    report = vm81_rna_bigint_environment_admission_probe(None)
    assert report["input_identity"]["case_count"] == 12
    assert report["input_identity"]["same_bigint_across_twelve_directional_views"] is True
    assert report["input_identity"]["all_candidate_frames_distinct"] is True
    assert report["canonical_admission"]["native_probe_supplied"] is False
    assert report["canonical_admission"]["positive_case_count"] == 0
    assert report["canonical_admission"]["all_twelve_signed_environmental_commits_exact"] is False
    assert report["negative_admission"]["case_count"] == 0
    assert report["promotion_result"]["new_runtime_mutation_primitive_required"] is False
    assert report["promotion_result"]["new_receipt_primitive_required"] is False
    assert report["authority"]["existing_environmental_mutator_reused"] is True
    assert report["authority"]["new_canonical_mutation_authority"] is False
    assert report["authority"]["new_canonical_receipt_authority"] is False
    assert report["authority"]["hash72_minting_authority_added"] is False
    assert report["authority"]["hash216_persistence_authority_added"] is False
    assert report["authority"]["floating_point_authority"] is False
    assert report["authority"]["ordered_pq_qp_collapse"] is False


def test_environment_admission_native_positive_and_negative_closure() -> None:
    native_probe = os.environ.get("HHS_PASS219_BIGINT_ENVIRONMENT_NATIVE_PROBE")
    if not native_probe:
        pytest.skip("OpenSSL-3.5 native admission probe not supplied")

    report = vm81_rna_bigint_environment_admission_probe(native_probe)
    positive = report["canonical_admission"]
    negative = report["negative_admission"]
    promotion = report["promotion_result"]

    assert positive["native_probe_supplied"] is True
    assert positive["positive_case_count"] == 12
    assert positive["all_twelve_signed_environmental_commits_exact"] is True
    assert positive["committed_frames_reencode_same_bigint"] is True
    assert positive["typed_pq_qp_metadata_survives_canonical_commit"] is True
    assert positive["parent_and_child_hash216_verified"] is True
    assert positive["canonical_receipt_owned_by_inherited_rna_authority"] is True
    assert positive["environment_and_signature_wrappers_do_not_self_mint_canonical_receipts"] is True
    assert all(row["status"] == 0 for row in positive["rows"])
    assert all(row["provider_available"] for row in positive["rows"])
    assert all(row["committed_bytes_equal_source"] for row in positive["rows"])
    assert all(row["reencoded_bigint_exact"] for row in positive["rows"])
    assert all(row["reencoded_metadata_exact"] for row in positive["rows"])
    assert all(row["canonical_receipt_minted"] for row in positive["rows"])
    assert all(row["signature_length"] > 0 for row in positive["rows"])

    assert negative["case_count"] == len(NEGATIVE_MODES)
    assert negative["all_invalid_prerequisites_fail_closed"] is True
    assert negative["no_invalid_case_commits_vm81"] is True
    assert negative["no_invalid_case_mints_canonical_receipt"] is True
    assert {row["mode"] for row in negative["rows"]} == set(NEGATIVE_MODES)
    assert all(row["status"] != 0 for row in negative["rows"])
    assert all(row["committed_frame_zero"] for row in negative["rows"])
    assert all(not row["canonical_receipt_minted"] for row in negative["rows"])

    assert promotion["candidate_to_signed_environmental_admission_bound"] is True
    assert promotion["decode_admit_commit_reencode_exact"] is True
    assert promotion["canonical_vm81_commit_observed_only_through_existing_public_boundary"] is True
    assert promotion["canonical_hash216_receipt_verified"] is True
    assert promotion["tampered_or_incomplete_prerequisites_rejected"] is True
    assert promotion["new_runtime_mutation_primitive_required"] is False
    assert promotion["new_receipt_primitive_required"] is False

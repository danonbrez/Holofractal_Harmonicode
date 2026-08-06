from __future__ import annotations

import pytest

from hhs_backend.runtime.hhs_pass214_iteration6_candidate_binding_v1 import (
    ADMISSION_SCHEMA,
    CANDIDATES,
    PASS213_CLOSURE,
    STATUS_BLOCKED,
    Pass214Iteration6Error,
    build_report,
    tamper_copy,
    validate_report,
)


def test_exact_five_family_candidate_binding() -> None:
    assert len(CANDIDATES) == 5
    assert {item["family"] for item in CANDIDATES} == {
        "vector_cache", "wrapper_duplication", "numeric_lookup",
        "serialization_import", "coprime_lookup",
    }
    assert all(len(item["git_blob_sha1"]) == 40 for item in CANDIDATES)


def test_report_is_deterministic_and_admission_blocked() -> None:
    first = build_report()
    second = build_report()
    assert first == second
    assert first["status"] == STATUS_BLOCKED
    assert first["live_admission"] is None
    assert first["family_count"] == 5
    validate_report(first)


def test_every_binding_is_exact_and_non_promoting() -> None:
    report = build_report()
    assert all(binding["source_commit"] == report["source_commit"] for binding in report["bindings"])
    assert all(binding["source_tree"] == report["source_tree"] for binding in report["bindings"])
    assert all(binding["admission_state"] == "BOUND_AWAITING_PASS213_LIVE_GOVERNED_SURFACE" for binding in report["bindings"])
    assert all(binding["promotion_state"] == "NON_PROMOTING" for binding in report["bindings"])
    assert report["policy"]["candidate_imported_for_replacement"] is False
    assert report["policy"]["candidate_executed_for_migration"] is False
    assert report["policy"]["authority_promoted"] is False
    assert report["policy"]["pass215_authorized"] is False


def test_tampered_binding_is_rejected() -> None:
    with pytest.raises(Pass214Iteration6Error, match="REPORT_REPLAY_MISMATCH"):
        validate_report(tamper_copy(build_report(), "numeric_lookup"))


def test_fixture_or_incomplete_admission_is_rejected() -> None:
    report = build_report()
    admission = {
        "schema": ADMISSION_SCHEMA,
        "pass213_closure": PASS213_CLOSURE,
        "candidate_set_root_hash216": report["candidate_set_root_hash216"],
        "governed_surface_receipt_hash216": "1" * 64,
        "native_dispatch_receipt_hash216": "2" * 64,
        "moving_tensor_state_hash216": "3" * 64,
        "rfc3161_anchor_hash216": "4" * 64,
        "validation_profile": "PASS213_DEPENDENCY_SCOPED_VALIDATION_FIXTURE",
        "production_authority_claimed": True,
    }
    with pytest.raises(Pass214Iteration6Error, match="PROFILE_NOT_LIVE"):
        build_report(admission)


def test_forged_candidate_root_is_rejected() -> None:
    report = build_report()
    admission = {
        "schema": ADMISSION_SCHEMA,
        "pass213_closure": PASS213_CLOSURE,
        "candidate_set_root_hash216": "f" * 64,
        "governed_surface_receipt_hash216": "1" * 64,
        "native_dispatch_receipt_hash216": "2" * 64,
        "moving_tensor_state_hash216": "3" * 64,
        "rfc3161_anchor_hash216": "4" * 64,
        "validation_profile": "PASS213_LIVE_GOVERNED_SURFACE",
        "production_authority_claimed": True,
    }
    with pytest.raises(Pass214Iteration6Error, match="CANDIDATE_ROOT_MISMATCH"):
        build_report(admission)


def test_zero_live_receipt_is_rejected() -> None:
    report = build_report()
    admission = {
        "schema": ADMISSION_SCHEMA,
        "pass213_closure": PASS213_CLOSURE,
        "candidate_set_root_hash216": report["candidate_set_root_hash216"],
        "governed_surface_receipt_hash216": "0" * 64,
        "native_dispatch_receipt_hash216": "2" * 64,
        "moving_tensor_state_hash216": "3" * 64,
        "rfc3161_anchor_hash216": "4" * 64,
        "validation_profile": "PASS213_LIVE_GOVERNED_SURFACE",
        "production_authority_claimed": True,
    }
    with pytest.raises(Pass214Iteration6Error, match="ZERO"):
        build_report(admission)

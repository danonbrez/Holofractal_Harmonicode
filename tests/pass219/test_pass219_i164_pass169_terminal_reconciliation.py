from __future__ import annotations

from pathlib import Path

from hhs_runtime.pass219.pass169_terminal_reconciliation import (
    BASE_MAIN,
    FIXED_RESOLUTION,
    PASS169_CANONICAL_CORPUS_PATH,
    PASS168_CONTRACT_ID,
    PASS168_SOURCE_SHA256,
    PASS168_TERMINAL_CLASSIFICATION,
    _pass168_terminal_receipt_valid,
    build_i164_pass169_terminal_reconciliation,
    i164_pass169_terminal_reconciliation_self_test,
)


ROOT = Path(__file__).resolve().parents[2]


def test_i164_self_test_binds_frozen_i161_i163_evidence() -> None:
    report = i164_pass169_terminal_reconciliation_self_test(ROOT)
    assert report["base_main"] == BASE_MAIN
    assert report["fixed_resolution"] == FIXED_RESOLUTION
    assert report["frozen_evidence"]["i161"]["verified"] is True
    assert report["frozen_evidence"]["i162"]["verified"] is True
    assert report["frozen_evidence"]["i163"]["verified"] is True
    assert report["frozen_evidence"]["all_frozen_evidence_verified"] is True


def test_i164_current_main_refuses_missing_canonical_corpus() -> None:
    report = build_i164_pass169_terminal_reconciliation(ROOT)
    assert not (ROOT / PASS169_CANONICAL_CORPUS_PATH).exists()
    assert report["canonical_corpus"]["present"] is False
    assert report["canonical_corpus"]["reconstruction_from_partial_fixtures_authorized"] is False
    assert "PASS169_CANONICAL_CORPUS_ABSENT" in report["blockers"]
    assert report["pass169_terminal_contract_verified"] is False


def test_i164_recoverable_fixtures_are_receipted_but_never_promoted() -> None:
    report = build_i164_pass169_terminal_reconciliation(ROOT)
    fixtures = report["canonical_corpus"]["recoverable_exact_fixtures"]
    assert len(fixtures) == 4
    assert all(row["present"] is True for row in fixtures)
    assert all(row["bytes"] > 0 for row in fixtures)
    assert all(len(row["sha256"]) == 64 for row in fixtures)
    assert all(row["qualifies_as_pass169_canonical_corpus"] is False for row in fixtures)


def test_i164_frozen_execution_obligations_remain_green() -> None:
    report = build_i164_pass169_terminal_reconciliation(ROOT)
    conditions = report["terminal_conditions"]
    assert conditions["complete_constraint_graph_executable"] is True
    assert conditions["exact_numeric_authority_demonstrated"] is True
    assert conditions["no_ieee_canonical_authority"] is True
    assert conditions["canonical_computation_through_runtime_abi"] is True
    assert conditions["vm81_admission_and_commit_verified"] is True
    assert conditions["hash72_receipts_verified"] is True
    assert conditions["hash216_identities_verified"] is True
    assert conditions["interpreter_compiler_agreement_verified"] is True
    assert conditions["deterministic_replay_verified"] is True
    assert conditions["reverse_execution_restores_prior_state"] is True
    assert conditions["cross_architecture_evidence_matches"] is True


def test_i164_general_cli_and_http_surfaces_remain_fail_closed() -> None:
    report = build_i164_pass169_terminal_reconciliation(ROOT)
    assert report["public_surfaces"]["cli"]["complete"] is False
    assert report["public_surfaces"]["http"]["complete"] is False
    assert "PASS169_REQUIRED_CLI_SURFACE_INCOMPLETE" in report["blockers"]
    assert "PASS169_REQUIRED_HTTP_SURFACE_INCOMPLETE" in report["blockers"]


def test_i164_does_not_acquire_new_authority() -> None:
    report = build_i164_pass169_terminal_reconciliation(ROOT)
    authority = report["authority"]
    assert authority["new_vm81_mutation_authority"] is False
    assert authority["new_hash72_mint_authority"] is False
    assert authority["hash216_persistence_authority"] is False
    assert authority["floating_point_canonical_authority"] is False
    assert authority["partial_source_relabeling_as_canonical_corpus"] is False


def test_i164_pass168_parent_requires_full_structured_terminal_receipt() -> None:
    assert _pass168_terminal_receipt_valid({"verified": True}) is False
    receipt = {
        "schema": "HHS_PASS_168_COMPLETION_RECEIPT_V1",
        "contract_id": PASS168_CONTRACT_ID,
        "classification": PASS168_TERMINAL_CLASSIFICATION,
        "terminal_verified": True,
        "verified": True,
        "fixed_resolution": FIXED_RESOLUTION,
        "source_bytes": 424,
        "source_sha256": PASS168_SOURCE_SHA256,
        "pass167_inheritance_bound": True,
        "cells_covered": 5184,
        "threads_registered": 64,
        "raw_threads": 40,
        "derived_threads": 24,
        "comparators_verified": 6,
        "single_vm81_commit_authority": True,
        "hash72_receipts_verified": True,
        "hash216_identity_verified": True,
        "deterministic_replay_verified": True,
        "rollback_verified": True,
        "repair_verified": True,
        "x86_64_verified": True,
        "arm64_verified": True,
        "sanitizers_passed": True,
        "cli_complete": True,
        "http_complete": True,
        "parameter_matrix_verified": True,
        "evidence_manifest_verified": True,
        "floating_point_canonical_authority": False,
        "fallback_used": False,
        "manifest_path": "HHS_PASS_168_EVIDENCE_MANIFEST.json",
    }
    assert _pass168_terminal_receipt_valid(receipt) is True
    for field in (
        "source_sha256", "single_vm81_commit_authority", "arm64_verified",
        "parameter_matrix_verified", "evidence_manifest_verified",
    ):
        forged = dict(receipt)
        forged[field] = False if isinstance(receipt[field], bool) else "forged"
        assert _pass168_terminal_receipt_valid(forged) is False

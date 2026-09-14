"""Focused tests for SPI corpus reconciliation v2."""
from __future__ import annotations

import json
from pathlib import Path

from hhs_spi_scalar_projection_corpus_reconciliation_v2 import (
    reconciliation_manifest_v2,
    validation_report,
)

REPO_ROOT = Path(__file__).resolve().parent


def _manifest():
    return reconciliation_manifest_v2(REPO_ROOT)


def test_counts_preserved():
    manifest = _manifest()
    assert manifest["resolved_candidate_counts"] == {
        "MISSING_PROJECTION": 0,
        "PROVEN": 429,
        "SYMBOLIC": 43,
        "UNSUPPORTED_DOMAIN": 0,
    }


def test_parser_limit_profiles_removed():
    manifest = _manifest()
    assert manifest["migrated_resolution_family_count"] == 2
    assert manifest["migrated_occurrence_count"] == 5
    assert manifest["parser_limit_profile_family_count"] == 0
    assert manifest["parser_limit_profile_occurrence_count"] == 0
    assert manifest["syntax_provenance_complete_for_migrated_profiles"] is True


def test_migrated_profiles_reference_ast_receipts():
    manifest = _manifest()
    migrated = [
        item
        for item in manifest["resolutions"]
        if item["expression"] in {"c^b", "(pq+u⁷²)^x"}
    ]
    assert len(migrated) == 2
    for item in migrated:
        assert item["profile"] == "NESTED-AST-SYNTAX-WITNESS-v2"
        assert item["parser_limit_closed"] is True
        assert item["algebraic_value_closed"] is False
        assert len(item["ast_binding_receipts_sha256"]) == item["occurrence_count"]
        assert len(item["ast_node_ids"]) == item["occurrence_count"]


def test_chain_associativity_stays_unselected():
    manifest = _manifest()
    chain = next(item for item in manifest["resolutions"] if item["expression"] == "c^b")
    assert any("associativity" in item for item in chain["lost_information"])
    assert manifest["coverage_policy"]["power_chain_associativity_not_selected"] is True


def test_scalar_completion_remains_open():
    manifest = _manifest()
    assert manifest["scalar_value_complete"] is False
    assert manifest["open_symbolic_occurrence_count"] == 43


def test_authority_boundary_unchanged():
    manifest = _manifest()
    authority = manifest["authority_boundary"]
    assert authority["canonical_admission_authority"] is False
    assert authority["vm81_mutation"] is False
    assert authority["canonical_hash72_hash216_minting"] is False
    assert authority["native_source_rewriting"] is False
    assert authority["ordered_product_commutation"] is False


def test_manifest_deterministic():
    first = _manifest()
    second = _manifest()
    assert first["manifest_sha256"] == second["manifest_sha256"]


def test_validation_green():
    report = validation_report(REPO_ROOT)
    assert report["ok"] is True
    assert report["parser_limit_profile_occurrence_count"] == 0
    assert report["scalar_value_complete"] is False


TESTS = [
    test_counts_preserved,
    test_parser_limit_profiles_removed,
    test_migrated_profiles_reference_ast_receipts,
    test_chain_associativity_stays_unselected,
    test_scalar_completion_remains_open,
    test_authority_boundary_unchanged,
    test_manifest_deterministic,
    test_validation_green,
]


def main() -> int:
    results = []
    for test in TESTS:
        try:
            test()
            results.append({"name": test.__name__, "passed": True})
        except Exception as exc:  # noqa: BLE001
            results.append({"name": test.__name__, "passed": False, "error": repr(exc)})
    report = {
        "suite": "HHS_SPI_CORPUS_RECONCILIATION_TESTS_V2",
        "passed": sum(1 for item in results if item["passed"]),
        "failed": sum(1 for item in results if not item["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

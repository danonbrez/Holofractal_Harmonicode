"""Focused tests for SPI nested-AST parser-limit migration v2."""
from __future__ import annotations

import json
from pathlib import Path

from hhs_spi_scalar_projection_corpus_ast_binding_v2 import (
    EXPECTED_RAW_MANIFEST_SHA256,
    EXPECTED_RECONCILIATION_V1_SHA256,
    binding_manifest,
    validation_report,
)

REPO_ROOT = Path(__file__).resolve().parent


def _manifest():
    return binding_manifest(REPO_ROOT)


def test_predecessor_manifests_frozen():
    manifest = _manifest()
    assert manifest["raw_corpus_manifest_sha256"] == EXPECTED_RAW_MANIFEST_SHA256
    assert manifest["reconciliation_v1_manifest_sha256"] == EXPECTED_RECONCILIATION_V1_SHA256


def test_exact_five_parser_limit_occurrences_migrated():
    manifest = _manifest()
    assert manifest["parser_limit_occurrence_count_before"] == 5
    assert manifest["parser_limit_occurrence_count_after"] == 0
    assert manifest["ast_bound_symbolic_occurrence_count"] == 5
    assert manifest["syntax_binding_complete"] is True


def test_chain_partial_binds_full_power_chain():
    manifest = _manifest()
    chain = [item for item in manifest["bindings"] if item["expression"] == "c^b"]
    assert len(chain) == 3
    for item in chain:
        assert item["ast_node_kind"] == "PowerChain"
        assert item["ast_source_text"] == "c^b^4"
        assert item["ast_associativity"] == "UNRESOLVED_SOURCE_CHAIN"
        assert item["parser_limit_closed"] is True
        assert item["algebraic_value_closed"] is False


def test_radical_partial_binds_full_radical_exponent_surface():
    manifest = _manifest()
    radical = [item for item in manifest["bindings"] if item["expression"] == "(pq+u⁷²)^x"]
    assert len(radical) == 2
    for item in radical:
        assert item["ast_node_kind"] == "RadicalPowerSurface"
        assert item["ast_source_text"] == "√(pq+u⁷²)^x²"
        assert item["parser_limit_closed"] is True
        assert item["algebraic_value_closed"] is False


def test_raw_candidate_span_is_contained_by_ast_span():
    manifest = _manifest()
    for item in manifest["bindings"]:
        raw = item["raw_candidate_span"]
        ast = item["ast_source_span"]
        assert ast["start"] <= raw["start"] < raw["end"] <= ast["end"]


def test_no_scalar_or_admission_authority_created():
    manifest = _manifest()
    assert manifest["scalar_value_complete"] is False
    assert manifest["authority_boundary"]["canonical_admission_authority"] is False
    assert manifest["authority_boundary"]["power_chain_associativity_selected"] is False
    assert all(item["scalar_value"] is None for item in manifest["bindings"])
    assert all(item["canonical_admission"] is False for item in manifest["bindings"])


def test_binding_receipts_deterministic():
    first = _manifest()
    second = _manifest()
    assert first["manifest_sha256"] == second["manifest_sha256"]
    assert [item["binding_receipt_sha256"] for item in first["bindings"]] == [
        item["binding_receipt_sha256"] for item in second["bindings"]
    ]


def test_validation_green():
    report = validation_report(REPO_ROOT)
    assert report["ok"] is True
    assert report["parser_limit_occurrence_count_after"] == 0


TESTS = [
    test_predecessor_manifests_frozen,
    test_exact_five_parser_limit_occurrences_migrated,
    test_chain_partial_binds_full_power_chain,
    test_radical_partial_binds_full_radical_exponent_surface,
    test_raw_candidate_span_is_contained_by_ast_span,
    test_no_scalar_or_admission_authority_created,
    test_binding_receipts_deterministic,
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
        "suite": "HHS_SPI_CORPUS_NESTED_AST_BINDING_TESTS_V2",
        "passed": sum(1 for item in results if item["passed"]),
        "failed": sum(1 for item in results if not item["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

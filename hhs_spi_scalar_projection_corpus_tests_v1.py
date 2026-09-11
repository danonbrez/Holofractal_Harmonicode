"""
Focused tests for Pass 219 SPI repository scalar-projection corpus coverage v1.

Run:
    python hhs_spi_scalar_projection_corpus_tests_v1.py
"""
from __future__ import annotations

import json
from pathlib import Path

from hhs_spi_scalar_projection_registry_v1 import MISSING_PROJECTION, PROVEN, SYMBOLIC
from hhs_spi_scalar_projection_corpus_v1 import (
    CANONICAL_ALIAS_PATH,
    CANONICAL_SOURCE_PATH,
    EXPECTED_HARMONICODE_SOURCES,
    repository_coverage_manifest,
    scalar_candidates,
    validate_repository_corpus,
    validate_source_inventory,
)

ROOT = Path(__file__).resolve().parent


def _all_candidates(manifest):
    return [
        candidate
        for record in manifest["unique_source_records"]
        for candidate in record["candidates"]
    ]


def test_source_inventory_exact_six_paths():
    inventory = validate_source_inventory(ROOT)
    assert inventory["ok"] is True, inventory["errors"]
    assert inventory["expected_path_count"] == 6
    assert inventory["discovered_path_count"] == 6
    assert set(EXPECTED_HARMONICODE_SOURCES) == {
        record["path"] for record in inventory["records"]
    }


def test_source_inventory_exact_five_unique_bodies():
    inventory = validate_source_inventory(ROOT)
    assert inventory["unique_source_hash_count"] == 5
    groups = inventory["duplicate_source_groups"]
    assert len(groups) == 1, groups
    assert groups[0]["paths"] == [CANONICAL_SOURCE_PATH, CANONICAL_ALIAS_PATH]


def test_frozen_authority_hashes():
    inventory = validate_source_inventory(ROOT)
    by_path = {record["path"]: record for record in inventory["records"]}
    assert by_path[CANONICAL_SOURCE_PATH]["sha256"] == (
        "3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53"
    )
    assert by_path[
        "contracts/pass219/PASS_219_NATIVE_UNIVERSAL_CONSTRAINT_ENVELOPE_1_8_0.harmonicode"
    ]["sha256"] == "7eb0cc5707a4a58a5a8e4879e0e2e3bdab22c15fe4503fb3a3b0e16596343d42"


def test_every_unique_source_parses_without_error():
    manifest = repository_coverage_manifest(ROOT)
    assert manifest["parser_error_count"] == 0
    assert all(record["parser_error_count"] == 0 for record in manifest["unique_source_records"])
    assert all(record["source_spans_preserved"] is True for record in manifest["unique_source_records"])


def test_parser_limit_is_explicit_not_overclaimed():
    manifest = repository_coverage_manifest(ROOT)
    assert manifest["coverage_policy"]["nested_expression_ast_complete"] is False
    assert all(
        record["nested_expression_ast_complete"] is False
        for record in manifest["unique_source_records"]
    )


def test_u72_fragments_bind_to_t6_proof():
    manifest = repository_coverage_manifest(ROOT)
    candidates = _all_candidates(manifest)
    bound = [
        c for c in candidates
        if c["expression"] in {"u^72", "u⁷²"} and c.get("projection_id") == "SPI-T6"
    ]
    assert bound, "no u^72/u⁷² candidates bound to SPI-T6"
    assert all(c["coverage_state"] == PROVEN for c in bound)
    assert all(c["canonical_admission"] is False for c in bound)


def test_native_mod_edge_is_symbolic_not_scalarized():
    manifest = repository_coverage_manifest(ROOT)
    candidates = _all_candidates(manifest)
    bound = [
        c for c in candidates
        if c["expression"] in {"P^2(MOD)(pq)", "P²(MOD)(pq)"}
        and c.get("projection_id") == "SPI-T3C"
    ]
    assert bound, "native MOD edge missing from coverage"
    assert all(c["coverage_state"] == SYMBOLIC for c in bound)


def test_matrix_power_is_symbolic_open_obligation():
    manifest = repository_coverage_manifest(ROOT)
    candidates = _all_candidates(manifest)
    matrix = [
        c for c in candidates
        if c["kind"] == "FUNCTION_CALL"
        and c["expression"].startswith("NcalcMatrixPower")
    ]
    assert matrix, "NcalcMatrixPower candidates not discovered"
    assert all(c["coverage_state"] == SYMBOLIC for c in matrix)
    assert all(c["projection_id"] == "SPI-O2-MATRIX" for c in matrix)


def test_literal_72_has_exact_scalar_lineage():
    manifest = repository_coverage_manifest(ROOT)
    candidates = _all_candidates(manifest)
    literal72 = [
        c for c in candidates
        if c["kind"] == "INTEGER_LITERAL" and c.get("result") == 72
    ]
    assert literal72, "literal 72 was not enumerated"
    assert all(c["coverage_state"] == PROVEN for c in literal72)
    assert all(c["projection_id"] == "EXACT-INTEGER-LITERAL-v1" for c in literal72)


def test_unregistered_power_candidates_fail_closed():
    manifest = repository_coverage_manifest(ROOT)
    candidates = _all_candidates(manifest)
    missing = [
        c for c in candidates
        if c["kind"] == "POWER" and c["coverage_state"] == MISSING_PROJECTION
    ]
    assert missing, "expected unresolved power candidates"
    assert all(c.get("projection_id") is None for c in missing)
    assert all(c["canonical_admission"] is False for c in missing)


def test_strict_complete_is_false_until_missing_projections_close():
    manifest = repository_coverage_manifest(ROOT)
    assert manifest["missing_projection_count"] > 0
    assert manifest["strict_complete"] is False


def test_no_scalar_candidate_claims_canonical_admission():
    manifest = repository_coverage_manifest(ROOT)
    assert all(
        c["canonical_admission"] is False
        for c in _all_candidates(manifest)
    )
    assert manifest["authority_boundary"]["canonical_admission_authority"] is False


def test_all_unregistered_candidates_are_fail_closed():
    manifest = repository_coverage_manifest(ROOT)
    assert manifest["coverage_policy"]["all_unregistered_fail_closed"] is True
    for c in _all_candidates(manifest):
        if c["coverage_state"] == PROVEN:
            assert c.get("projection_id"), c


def test_path_provenance_retains_duplicate_alias():
    manifest = repository_coverage_manifest(ROOT)
    paths = {record["path"]: record for record in manifest["path_records"]}
    assert paths[CANONICAL_SOURCE_PATH]["raw_sha256"] == paths[CANONICAL_ALIAS_PATH]["raw_sha256"]
    assert paths[CANONICAL_ALIAS_PATH]["deduplicated_to_path"] == CANONICAL_SOURCE_PATH


def test_manifest_is_deterministic():
    first = repository_coverage_manifest(ROOT)
    second = repository_coverage_manifest(ROOT)
    assert first["manifest_sha256"] == second["manifest_sha256"]
    assert first == second


def test_validation_succeeds_while_strict_completion_remains_open():
    result = validate_repository_corpus(ROOT)
    assert result["ok"] is True, result
    assert result["strict_complete"] is False
    assert result["missing_projection_count"] > 0
    assert result["canonical_admission_authority"] is False


def test_candidate_receipts_are_deterministic():
    source = (ROOT / CANONICAL_SOURCE_PATH).read_text(encoding="utf-8")
    a = scalar_candidates(source)
    b = scalar_candidates(source)
    assert a == b
    assert all(len(c["candidate_receipt_sha256"]) == 64 for c in a)


TESTS = [
    test_source_inventory_exact_six_paths,
    test_source_inventory_exact_five_unique_bodies,
    test_frozen_authority_hashes,
    test_every_unique_source_parses_without_error,
    test_parser_limit_is_explicit_not_overclaimed,
    test_u72_fragments_bind_to_t6_proof,
    test_native_mod_edge_is_symbolic_not_scalarized,
    test_matrix_power_is_symbolic_open_obligation,
    test_literal_72_has_exact_scalar_lineage,
    test_unregistered_power_candidates_fail_closed,
    test_strict_complete_is_false_until_missing_projections_close,
    test_no_scalar_candidate_claims_canonical_admission,
    test_all_unregistered_candidates_are_fail_closed,
    test_path_provenance_retains_duplicate_alias,
    test_manifest_is_deterministic,
    test_validation_succeeds_while_strict_completion_remains_open,
    test_candidate_receipts_are_deterministic,
]


def main() -> None:
    results = []
    for fn in TESTS:
        try:
            fn()
            results.append({"name": fn.__name__, "passed": True})
        except Exception as exc:
            results.append({
                "name": fn.__name__,
                "passed": False,
                "error": f"{type(exc).__name__}: {exc}",
            })
    report = {
        "suite": "HHS_SPI_SCALAR_PROJECTION_CORPUS_TESTS_V1",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

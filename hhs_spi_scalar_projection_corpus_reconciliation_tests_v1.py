"""
Focused tests for Pass 219 SPI corpus projection reconciliation v1.
"""
from __future__ import annotations

import json
from pathlib import Path

from hhs_spi_scalar_projection_registry_v1 import MISSING_PROJECTION, PROVEN, SYMBOLIC
from hhs_spi_scalar_projection_corpus_reconciliation_v1 import (
    EXPECTED_BASE_MANIFEST_SHA256,
    PROFILES,
    reconciliation_manifest,
    validate_profiles,
    validate_reconciliation,
)

ROOT = Path(__file__).resolve().parent


def test_profiles_valid():
    result = validate_profiles()
    assert result["ok"] is True, result
    assert result["profile_count"] == 16


def test_profile_set_closes_exact_raw_missing_families():
    manifest = reconciliation_manifest(ROOT)
    assert manifest["base_corpus_manifest_sha256"] == EXPECTED_BASE_MANIFEST_SHA256
    assert manifest["absent_profiles"] == []
    assert manifest["stale_profiles"] == []


def test_resolved_counts_exact():
    manifest = reconciliation_manifest(ROOT)
    assert manifest["base_candidate_counts"] == {
        "MISSING_PROJECTION": 56,
        "PROVEN": 389,
        "SYMBOLIC": 27,
        "UNSUPPORTED_DOMAIN": 0,
    }
    assert manifest["resolved_candidate_counts"] == {
        "MISSING_PROJECTION": 0,
        "PROVEN": 429,
        "SYMBOLIC": 43,
        "UNSUPPORTED_DOMAIN": 0,
    }


def test_classification_complete_but_scalar_values_open():
    manifest = reconciliation_manifest(ROOT)
    assert manifest["classification_complete"] is True
    assert manifest["scalar_value_complete"] is False
    assert manifest["open_symbolic_occurrence_count"] == 43


def test_u360_closes_from_u72():
    profile = PROFILES["u^360"]
    assert profile["coverage_state"] == PROVEN
    assert profile["result"] == 1
    assert "360=5*72" in profile["derivation"]


def test_b_2c2_closes_to_eight():
    profile = PROFILES["b^(2c^2)"]
    assert profile["coverage_state"] == PROVEN
    assert profile["result"] == 8


def test_i4_unit_and_i2_i3_remain_phase_classes():
    assert PROFILES["I^4"]["coverage_state"] == PROVEN
    assert PROFILES["I^4"]["result"] == 1
    assert PROFILES["I^2"]["coverage_state"] == SYMBOLIC
    assert PROFILES["I^3"]["coverage_state"] == SYMBOLIC


def test_structural_generator_and_polynomial_powers_are_parametric():
    for expression in ("P^2", "P²", "P^3", "P³", "t^3", "t³", "m^2"):
        profile = PROFILES[expression]
        assert profile["coverage_state"] == PROVEN
        assert "parametric" in profile["result"]


def test_x_square_does_not_invent_scalar_magnitude():
    for expression in ("x^2", "x²"):
        profile = PROFILES[expression]
        assert profile["coverage_state"] == SYMBOLIC
        assert profile["result"] == {"formal": "x^2"}


def test_lexical_partial_profiles_do_not_claim_algebra():
    for expression in ("c^b", "(pq+u⁷²)^x"):
        profile = PROFILES[expression]
        assert profile["coverage_state"] == SYMBOLIC
        assert profile["profile"] == "PARSER-LIMIT-WITNESS-v1"
        assert profile["result"] is None


def test_reconciliation_has_no_canonical_authority():
    manifest = reconciliation_manifest(ROOT)
    assert manifest["authority_boundary"]["canonical_admission_authority"] is False
    assert all(r["canonical_admission"] is False for r in manifest["resolutions"])


def test_resolution_receipts_deterministic():
    a = reconciliation_manifest(ROOT)
    b = reconciliation_manifest(ROOT)
    assert a == b
    assert len(a["manifest_sha256"]) == 64
    assert all(len(r["resolution_receipt_sha256"]) == 64 for r in a["resolutions"])


def test_validation_green():
    result = validate_reconciliation(ROOT)
    assert result["ok"] is True, result
    assert result["classification_complete"] is True
    assert result["scalar_value_complete"] is False
    assert result["resolved_candidate_counts"][MISSING_PROJECTION] == 0


TESTS = [
    test_profiles_valid,
    test_profile_set_closes_exact_raw_missing_families,
    test_resolved_counts_exact,
    test_classification_complete_but_scalar_values_open,
    test_u360_closes_from_u72,
    test_b_2c2_closes_to_eight,
    test_i4_unit_and_i2_i3_remain_phase_classes,
    test_structural_generator_and_polynomial_powers_are_parametric,
    test_x_square_does_not_invent_scalar_magnitude,
    test_lexical_partial_profiles_do_not_claim_algebra,
    test_reconciliation_has_no_canonical_authority,
    test_resolution_receipts_deterministic,
    test_validation_green,
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
        "suite": "HHS_SPI_CORPUS_PROJECTION_RECONCILIATION_TESTS_V1",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

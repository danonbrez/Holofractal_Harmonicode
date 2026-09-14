"""Tests for full Sudoku equal-sum tensor translation v2."""
from __future__ import annotations

import json

from hhs_spi_equal_sum_tensor_translation_rule_v2 import (
    PROFILE,
    SUDOKU_GROUP_SUM,
    SUDOKU_GRID_A,
    SUDOKU_GRID_B,
    full_sudoku_translation_witness,
    sudoku_equation_sums,
)

Q1 = {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
Q45 = {"type": "EXACT_RATIONAL", "numerator": 45, "denominator": 1}


def test_full_sudoku_equations_all_sum_to_45():
    for grid in (SUDOKU_GRID_A, SUDOKU_GRID_B):
        sums = sudoku_equation_sums(grid)
        assert len(sums) == 27
        assert all(value == 45 for value in sums)


def test_full_sudoku_translation_normalizes_every_equation_at_a2():
    witness = full_sudoku_translation_witness()
    assert witness["successor_profile"] == PROFILE
    assert witness["source_shape"] == [9, 9]
    assert witness["target_shape"] == [9, 9]
    assert witness["invariant_sum"] == Q45
    assert witness["complete_sudoku_equation_count"] == 27
    assert witness["row_equation_count"] == 9
    assert witness["column_equation_count"] == 9
    assert witness["bank_equation_count"] == 9
    assert witness["source_normalized_equations"] == [Q1] * 27
    assert witness["target_normalized_equations"] == [Q1] * 27
    assert witness["equation_translation_authorized"] is True
    assert witness["cellwise_tensor_identity_authorized"] is False


def test_receipt_deterministic():
    assert full_sudoku_translation_witness() == full_sudoku_translation_witness()


def main() -> None:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    results = []
    for test in tests:
        try:
            test()
            results.append({"name": test.__name__, "passed": True})
        except Exception as exc:
            results.append({"name": test.__name__, "passed": False, "error": f"{type(exc).__name__}: {exc}"})
    report = {
        "schema": "HHS_SPI_EQUAL_SUM_TENSOR_TRANSLATION_TEST_REPORT_V2",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

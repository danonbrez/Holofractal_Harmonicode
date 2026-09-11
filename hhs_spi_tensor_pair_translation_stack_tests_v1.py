"""Tests for the composite tensor-pair translation stack."""
from __future__ import annotations

import json

from hhs_spi_tensor_pair_translation_stack_v1 import (
    PROFILE,
    lo_shu_translation_stack,
    sudoku_translation_stack,
)

Q = lambda n, d=1: {"type": "EXACT_RATIONAL", "numerator": n, "denominator": d}


def test_lo_shu_base_stack_closes_all_three_layers():
    receipt = lo_shu_translation_stack(stage_index=0)
    assert receipt["profile"] == PROFILE
    assert receipt["shape"] == [3, 3]
    assert receipt["equal_sum_layer"]["equation_count"] == 8
    assert receipt["equal_sum_layer"]["local_scale"] == "a²=1"
    assert receipt["equal_sum_layer"]["closed"] is True
    scale = receipt["fibonacci_pythagorean_scale_layer"]
    assert scale["source_scale_coordinate"] == Q(1)
    assert scale["target_scale_coordinate"] == Q(1)
    assert scale["pythagorean_seed"] == "a²+b²=c²"
    assert scale["next_stage_ratio"] == Q(2)
    assert scale["finite_ratio_replaced_by_phi"] is False
    cubic = receipt["cubic_three_set_layer"]
    assert cubic["three_set"] == ["t³", "t", "a²"]
    assert cubic["relation"] == "t³=t+a²"
    assert cubic["residual_relation"] == "t³-t=a²=∆=1"
    assert cubic["native_t_solved"] is False
    assert cubic["closed"] is True


def test_lo_shu_higher_fibonacci_stage_preserves_pair_translation():
    receipt = lo_shu_translation_stack(stage_index=4)
    scale = receipt["fibonacci_pythagorean_scale_layer"]
    assert scale["source_scale_coordinate"] == Q(8)
    assert scale["target_scale_coordinate"] == Q(8)
    assert scale["next_stage_ratio"] == Q(13, 8)
    assert scale["same_scale_coordinate"] is True


def test_full_sudoku_stack_uses_27_sum_equations():
    receipt = sudoku_translation_stack(stage_index=2)
    assert receipt["shape"] == [9, 9]
    assert receipt["equal_sum_layer"]["equation_count"] == 27
    assert receipt["fibonacci_pythagorean_scale_layer"]["source_scale_coordinate"] == Q(3)
    assert receipt["fibonacci_pythagorean_scale_layer"]["target_scale_coordinate"] == Q(3)
    assert receipt["cubic_three_set_layer"]["relation"] == "t³=t+a²"


def test_composition_order_is_explicit():
    receipt = sudoku_translation_stack(stage_index=1)
    composition = receipt["composition"]
    assert composition["ordered_layers"] == [
        "EQUAL_SUM_A2_NORMALIZATION",
        "FIBONACCI_PYTHAGOREAN_SCALE",
        "TENSOR_PAIR_CUBIC_THREE_SET",
    ]
    assert composition["local_scale"] == "a²=1"
    assert composition["universal_denominator"] == "∆=1"
    assert composition["three_set_normalization"] == "t³=t+a²"
    assert composition["projection_only"] is True


def test_native_authority_boundary_remains_closed():
    for receipt in (lo_shu_translation_stack(), sudoku_translation_stack()):
        assert receipt["native_tensor_identity_authorized"] is False
        assert receipt["native_t_solved"] is False
        assert receipt["canonical_admission_authority"] is False
        assert receipt["vm81_mutation_authority"] is False
        assert receipt["canonical_hash72_authority"] is False
        assert receipt["canonical_hash216_authority"] is False
        assert receipt["canonical_persistence_authority"] is False
        assert receipt["floating_point_authority"] is False


def test_composite_receipts_are_deterministic():
    assert lo_shu_translation_stack(3) == lo_shu_translation_stack(3)
    assert sudoku_translation_stack(3) == sudoku_translation_stack(3)


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
        "schema": "HHS_SPI_TENSOR_PAIR_TRANSLATION_STACK_TEST_REPORT_V1",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

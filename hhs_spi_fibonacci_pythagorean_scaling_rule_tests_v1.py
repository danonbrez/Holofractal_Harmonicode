"""Focused tests for Fibonacci/Pythagorean/Golden tensor scaling."""
from __future__ import annotations

import json
from fractions import Fraction

from hhs_spi_fibonacci_pythagorean_scaling_rule_v1 import (
    GOLDEN_POLYNOMIAL,
    PROFILE,
    SPIFibonacciScalingError,
    cross_stage_translation_witness,
    finite_stage_ratios,
    pythagorean_base_witness,
    scale_ladder_witness,
    square_state_sequence,
    tensor_scale_coordinate,
)

Q = lambda n, d=1: {"type": "EXACT_RATIONAL", "numerator": n, "denominator": d}


def _raises(exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__}")


def test_pythagorean_seed_is_exact():
    witness = pythagorean_base_witness()
    assert witness["profile"] == PROFILE
    assert witness["a²"] == Q(1)
    assert witness["b²"] == Q(2)
    assert witness["c²"] == Q(3)
    assert witness["equation"] == "a²+b²=c²"
    assert witness["residual"] == Q(0)
    assert witness["floating_point_authority"] is False


def test_square_state_sequence_is_fibonacci_from_a2_b2_seed():
    assert square_state_sequence(9) == (1, 2, 3, 5, 8, 13, 21, 34, 55)


def test_finite_stage_ratios_are_exact_and_not_phi_substitutions():
    ratios = finite_stage_ratios(6)
    assert ratios == (
        Fraction(2, 1),
        Fraction(3, 2),
        Fraction(5, 3),
        Fraction(8, 5),
        Fraction(13, 8),
        Fraction(21, 13),
    )
    ladder = scale_ladder_witness(9)
    assert ladder["golden_limit"]["polynomial"] == GOLDEN_POLYNOMIAL
    assert ladder["golden_limit"]["positive_root"] is True
    assert ladder["golden_limit"]["finite_ratio_substitution_authorized"] is False
    assert ladder["golden_limit"]["floating_approximation_authorized"] is False
    assert ladder["recurrence_residuals"] == [Q(0)] * 7


def test_equal_sum_tensor_coordinate_equals_square_state():
    for stage, expected in enumerate((1, 2, 3, 5, 8)):
        witness = tensor_scale_coordinate(equation_sum=15, invariant_sum=15, stage_index=stage)
        assert witness["equal_sum_closed"] is True
        assert witness["a2_normalized_equation"] == Q(1)
        assert witness["square_state"] == Q(expected)
        assert witness["scale_coordinate"] == Q(expected)


def test_sudoku_sum_45_uses_same_scale_ladder():
    witness = tensor_scale_coordinate(equation_sum=45, invariant_sum=45, stage_index=4)
    assert witness["a2_normalized_equation"] == Q(1)
    assert witness["scale_coordinate"] == Q(8)


def test_unequal_sum_does_not_false_close():
    witness = tensor_scale_coordinate(equation_sum=14, invariant_sum=15, stage_index=2)
    assert witness["equal_sum_closed"] is False
    assert witness["a2_normalized_equation"] == Q(14, 15)
    assert witness["scale_coordinate"] == Q(14, 5)


def test_adjacent_cross_stage_translation_is_exact():
    expectations = (
        (0, Q(1), Q(2), Q(2)),
        (1, Q(2), Q(3), Q(3, 2)),
        (2, Q(3), Q(5), Q(5, 3)),
        (3, Q(5), Q(8), Q(8, 5)),
    )
    for source_stage, source_q, target_q, ratio in expectations:
        witness = cross_stage_translation_witness(
            invariant_sum=15,
            source_stage=source_stage,
            target_stage=source_stage + 1,
        )
        assert witness["source_square_state"] == source_q
        assert witness["target_square_state"] == target_q
        assert witness["finite_scale_ratio"] == ratio
        assert witness["residual"] == Q(0)
        assert witness["finite_ratio_replaced_by_phi"] is False


def test_nonadjacent_stage_fails_closed():
    _raises(
        SPIFibonacciScalingError,
        cross_stage_translation_witness,
        invariant_sum=15,
        source_stage=0,
        target_stage=2,
    )


def test_float_inputs_fail_closed():
    _raises(SPIFibonacciScalingError, tensor_scale_coordinate, equation_sum=15.0, invariant_sum=15, stage_index=0)
    _raises(SPIFibonacciScalingError, tensor_scale_coordinate, equation_sum=15, invariant_sum=15.0, stage_index=0)


def test_receipts_are_deterministic():
    assert pythagorean_base_witness() == pythagorean_base_witness()
    assert scale_ladder_witness(9) == scale_ladder_witness(9)
    assert tensor_scale_coordinate(equation_sum=15, invariant_sum=15, stage_index=5) == tensor_scale_coordinate(equation_sum=15, invariant_sum=15, stage_index=5)


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
        "schema": "HHS_SPI_FIBONACCI_PYTHAGOREAN_SCALING_TEST_REPORT_V1",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

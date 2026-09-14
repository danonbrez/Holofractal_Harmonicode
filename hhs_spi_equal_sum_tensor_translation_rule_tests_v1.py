"""Tests for equal-sum tensor translation normalization at a²."""
from __future__ import annotations

import json

from hhs_spi_equal_sum_tensor_translation_rule_v1 import (
    LO_SHU_MAGIC_SUM,
    PROFILE,
    SPIEqualSumTensorTranslationError,
    SUDOKU_GROUP_SUM,
    equal_sum_translation_witness,
    lo_shu_translation_witness,
    sudoku_group_translation_witness,
)

EXACT_ONE = {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
EXACT_FIFTEEN = {"type": "EXACT_RATIONAL", "numerator": 15, "denominator": 1}
EXACT_FORTY_FIVE = {"type": "EXACT_RATIONAL", "numerator": 45, "denominator": 1}


def _raises(exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__}")


def test_lo_shu_equal_sum_translation_closes_at_a2():
    witness = lo_shu_translation_witness()
    assert witness["profile"] == PROFILE
    assert witness["source_shape"] == [3, 3]
    assert witness["target_shape"] == [3, 3]
    assert witness["invariant_sum"] == EXACT_FIFTEEN
    assert witness["sum_equation_count"] == 8
    assert witness["local_scale_symbol"] == "a²"
    assert witness["local_scale"] == EXACT_ONE
    assert witness["source_normalized_equations"] == [EXACT_ONE] * 8
    assert witness["target_normalized_equations"] == [EXACT_ONE] * 8
    assert witness["equation_translation_authorized"] is True
    assert witness["cellwise_tensor_identity_authorized"] is False
    assert witness["native_tensor_substitution_authorized"] is False


def test_sudoku_equal_sum_groups_translate_at_a2():
    witness = sudoku_group_translation_witness()
    assert witness["source_shape"] == [9]
    assert witness["target_shape"] == [9]
    assert witness["invariant_sum"] == EXACT_FORTY_FIVE
    assert witness["sum_equation_count"] == 1
    assert witness["source_normalized_equations"] == [EXACT_ONE]
    assert witness["target_normalized_equations"] == [EXACT_ONE]
    assert witness["symmetry_family"] == "SUDOKU_PERMUTATION_1_TO_9"


def test_same_shape_is_required():
    _raises(
        SPIEqualSumTensorTranslationError,
        equal_sum_translation_witness,
        source_id="A",
        target_id="B",
        source_tensor=((1, 1), (1, 1)),
        target_tensor=(1, 1, 1, 1),
        invariant_sum=2,
        source_sum_equations=(2, 2),
        target_sum_equations=(2, 2),
        symmetry_family="TEST",
        layer_id="TEST",
    )


def test_equal_sum_equation_is_required():
    _raises(
        SPIEqualSumTensorTranslationError,
        equal_sum_translation_witness,
        source_id="A",
        target_id="B",
        source_tensor=((1, 1), (1, 1)),
        target_tensor=((1, 1), (1, 1)),
        invariant_sum=2,
        source_sum_equations=(2, 2),
        target_sum_equations=(2, 3),
        symmetry_family="TEST",
        layer_id="TEST",
    )


def test_matching_sum_equation_cardinality_is_required():
    _raises(
        SPIEqualSumTensorTranslationError,
        equal_sum_translation_witness,
        source_id="A",
        target_id="B",
        source_tensor=((1, 1), (1, 1)),
        target_tensor=((1, 1), (1, 1)),
        invariant_sum=2,
        source_sum_equations=(2, 2),
        target_sum_equations=(2,),
        symmetry_family="TEST",
        layer_id="TEST",
    )


def test_zero_normalization_sum_fails_closed():
    _raises(
        SPIEqualSumTensorTranslationError,
        equal_sum_translation_witness,
        source_id="A",
        target_id="B",
        source_tensor=(0, 0),
        target_tensor=(0, 0),
        invariant_sum=0,
        source_sum_equations=(0,),
        target_sum_equations=(0,),
        symmetry_family="TEST",
        layer_id="TEST",
    )


def test_float_arithmetic_fails_closed():
    _raises(
        SPIEqualSumTensorTranslationError,
        equal_sum_translation_witness,
        source_id="A",
        target_id="B",
        source_tensor=(1, 2),
        target_tensor=(2, 1),
        invariant_sum=3.0,
        source_sum_equations=(3,),
        target_sum_equations=(3,),
        symmetry_family="TEST",
        layer_id="TEST",
    )


def test_translation_preserves_native_authority_boundary():
    for witness in (lo_shu_translation_witness(), sudoku_group_translation_witness()):
        assert witness["projection_only"] is True
        assert witness["cellwise_tensor_identity_authorized"] is False
        assert witness["native_tensor_substitution_authorized"] is False
        assert witness["coordinate_permutation_authorized"] is False
        assert witness["canonical_admission_authority"] is False
        assert witness["vm81_mutation_authority"] is False
        assert witness["canonical_hash72_authority"] is False
        assert witness["canonical_hash216_authority"] is False
        assert witness["canonical_persistence_authority"] is False
        assert witness["floating_point_authority"] is False


def test_deterministic_receipts():
    assert lo_shu_translation_witness() == lo_shu_translation_witness()
    assert sudoku_group_translation_witness() == sudoku_group_translation_witness()


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
        "schema": "HHS_SPI_EQUAL_SUM_TENSOR_TRANSLATION_TEST_REPORT_V1",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

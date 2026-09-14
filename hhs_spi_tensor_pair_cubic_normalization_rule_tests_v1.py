"""Tests for tensor-pair three-set cubic normalization."""
from __future__ import annotations

import json

from hhs_spi_tensor_pair_cubic_normalization_rule_v1 import (
    PROFILE,
    RESIDUAL_RELATION,
    SOURCE_RELATION,
    SPITensorPairCubicNormalizationError,
    THREE_SET,
    tensor_pair_cubic_witness,
    three_set_normalization_equations,
)

Q1 = {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
Q0 = {"type": "EXACT_RATIONAL", "numerator": 0, "denominator": 1}


def _raises(exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__}")


def _witness():
    return tensor_pair_cubic_witness(
        pair_layer_id="PAIR:LOSHU:A:B",
        source_tensor_id="LO_SHU_A",
        target_tensor_id="LO_SHU_B",
        source_shape=(3, 3),
        target_shape=(3, 3),
        equal_sum_normalized=True,
    )


def test_three_set_relation_closes_exactly():
    witness = _witness()
    assert witness["profile"] == PROFILE
    assert witness["three_set"] == list(THREE_SET)
    assert witness["source_relation"] == SOURCE_RELATION
    assert witness["residual_relation"] == RESIDUAL_RELATION
    assert witness["cubic_residual_projection"] == Q1
    assert witness["local_scale_projection"] == Q1
    assert witness["universal_denominator_projection"] == Q1
    assert witness["projected_relation_residual"] == Q0
    assert witness["projected_universal_residual"] == Q0


def test_native_t_is_not_solved():
    witness = _witness()
    assert witness["t_scalar_value_assigned"] is False
    assert witness["t_scalar_value"] is None
    assert witness["native_t_solved"] is False
    assert witness["native_t3_t_a2_identity_collapse"] is False


def test_equal_sum_prerequisite_is_required():
    _raises(
        SPITensorPairCubicNormalizationError,
        tensor_pair_cubic_witness,
        pair_layer_id="PAIR",
        source_tensor_id="A",
        target_tensor_id="B",
        source_shape=(3, 3),
        target_shape=(3, 3),
        equal_sum_normalized=False,
    )


def test_same_shape_is_required():
    _raises(
        SPITensorPairCubicNormalizationError,
        tensor_pair_cubic_witness,
        pair_layer_id="PAIR",
        source_tensor_id="A",
        target_tensor_id="B",
        source_shape=(3, 3),
        target_shape=(9,),
        equal_sum_normalized=True,
    )


def test_all_three_units_must_match():
    for kwargs in (
        {"a2_projection": 2},
        {"delta_projection": 2},
        {"cubic_residual_projection": 2},
    ):
        _raises(
            SPITensorPairCubicNormalizationError,
            tensor_pair_cubic_witness,
            pair_layer_id="PAIR",
            source_tensor_id="A",
            target_tensor_id="B",
            source_shape=(3, 3),
            target_shape=(3, 3),
            equal_sum_normalized=True,
            **kwargs,
        )


def test_float_projection_fails_closed():
    _raises(
        SPITensorPairCubicNormalizationError,
        tensor_pair_cubic_witness,
        pair_layer_id="PAIR",
        source_tensor_id="A",
        target_tensor_id="B",
        source_shape=(3, 3),
        target_shape=(3, 3),
        equal_sum_normalized=True,
        a2_projection=1.0,
    )


def test_authority_boundary_is_projection_only():
    witness = _witness()
    assert witness["projection_only"] is True
    assert witness["native_tensor_substitution_authorized"] is False
    assert witness["canonical_admission_authority"] is False
    assert witness["vm81_mutation_authority"] is False
    assert witness["canonical_hash72_authority"] is False
    assert witness["canonical_hash216_authority"] is False
    assert witness["canonical_persistence_authority"] is False
    assert witness["floating_point_authority"] is False


def test_symbolic_equation_registry_does_not_solve_t():
    equations = three_set_normalization_equations()
    assert equations["three_set"] == ["t³", "t", "a²"]
    assert equations["native_relation"] == "t³=t+a²"
    assert equations["scalar_projection_equivalence"] == [
        "pi(t³-t)=1",
        "pi(a²)=1",
        "pi(∆)=1",
        "pi(t³-t-a²)=0",
    ]
    assert equations["native_t_solved"] is False


def test_receipt_is_deterministic():
    assert _witness() == _witness()


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
        "schema": "HHS_SPI_TENSOR_PAIR_CUBIC_NORMALIZATION_TEST_REPORT_V1",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

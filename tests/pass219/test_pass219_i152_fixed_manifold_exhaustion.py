from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from hhs_runtime.pass219.fixed_cardinality_optimization import (
    EXPECTED_MAX_EXHAUSTION_WORK_DECIMAL,
    EXPECTED_ROUTE_MULTIPLICITY_DECIMAL,
    EXPECTED_TARGET_DECIMAL,
    EXPECTED_WORKING_DECIMAL,
    MAX_EFFECTIVE_EXHAUSTION_WORK,
    ROUTE_MULTIPLICITY_PER_TARGET,
    TARGET_CARDINALITY,
    WORKING_MANIFOLD_CARDINALITY,
    FixedCardinalityError,
    decode_working_route,
    encode_working_route,
    evaluate_exhaustion_work,
    local_reduction_meets_exhaustion_ratio,
    validate_fixed_cardinalities,
)


ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = ROOT / "benchmarks" / "pass219" / "pass219_i152_fixed_manifold_exhaustion_benchmark.py"


def test_i152_fixed_cardinalities_are_exact() -> None:
    receipt = validate_fixed_cardinalities()
    assert TARGET_CARDINALITY == 72 ** 42 == 5184 ** 21
    assert WORKING_MANIFOLD_CARDINALITY == 3 * (72 ** 72)
    assert ROUTE_MULTIPLICITY_PER_TARGET == 3 * (72 ** 30)
    assert WORKING_MANIFOLD_CARDINALITY == TARGET_CARDINALITY * ROUTE_MULTIPLICITY_PER_TARGET
    assert str(TARGET_CARDINALITY) == EXPECTED_TARGET_DECIMAL
    assert str(WORKING_MANIFOLD_CARDINALITY) == EXPECTED_WORKING_DECIMAL
    assert str(ROUTE_MULTIPLICITY_PER_TARGET) == EXPECTED_ROUTE_MULTIPLICITY_DECIMAL
    assert str(MAX_EFFECTIVE_EXHAUSTION_WORK) == EXPECTED_MAX_EXHAUSTION_WORK_DECIMAL
    assert receipt["physical_full_exhaustion_claim"] is False
    assert receipt["authority_changed"] is False


@pytest.mark.parametrize(
    ("block", "route"),
    (
        (0, 0),
        (0, ROUTE_MULTIPLICITY_PER_TARGET - 1),
        (TARGET_CARDINALITY // 2, ROUTE_MULTIPLICITY_PER_TARGET // 2),
        (TARGET_CARDINALITY - 1, 0),
        (TARGET_CARDINALITY - 1, ROUTE_MULTIPLICITY_PER_TARGET - 1),
    ),
)
def test_i152_route_factorization_roundtrips(block: int, route: int) -> None:
    index = encode_working_route(block, route)
    assert decode_working_route(index) == (block, route)


def test_i152_last_route_is_last_working_index() -> None:
    assert encode_working_route(
        TARGET_CARDINALITY - 1,
        ROUTE_MULTIPLICITY_PER_TARGET - 1,
    ) == WORKING_MANIFOLD_CARDINALITY - 1


@pytest.mark.parametrize(
    ("work", "within"),
    (
        (0, True),
        (MAX_EFFECTIVE_EXHAUSTION_WORK - 1, True),
        (MAX_EFFECTIVE_EXHAUSTION_WORK, True),
        (MAX_EFFECTIVE_EXHAUSTION_WORK + 1, False),
    ),
)
def test_i152_81_over_7_budget_boundary(work: int, within: bool) -> None:
    result = evaluate_exhaustion_work(work)
    assert result["within_81_over_7_exhaustion_budget"] is within


def test_i152_local_i151_observations_are_not_conflated_with_full_exhaustion() -> None:
    assert local_reduction_meets_exhaustion_ratio(11_466_081, 5_645_376) is False
    assert local_reduction_meets_exhaustion_ratio(1_384_512, 32_228) is True


def test_i152_exact_surfaces_reject_float_and_range_drift() -> None:
    with pytest.raises(FixedCardinalityError, match="EXACT_INTEGER"):
        evaluate_exhaustion_work(1.0)  # type: ignore[arg-type]
    with pytest.raises(FixedCardinalityError, match="OUT_OF_RANGE"):
        encode_working_route(TARGET_CARDINALITY, 0)
    with pytest.raises(FixedCardinalityError, match="OUT_OF_RANGE"):
        encode_working_route(0, ROUTE_MULTIPLICITY_PER_TARGET)
    with pytest.raises(FixedCardinalityError, match="OUT_OF_RANGE"):
        decode_working_route(WORKING_MANIFOLD_CARDINALITY)


def test_i152_benchmark_module_imports_without_float_authority() -> None:
    spec = importlib.util.spec_from_file_location("pass219_i152_benchmark", BENCHMARK)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.I151_RAW_BASELINE == 11_466_081
    assert module.I151_CROSS_SELECTED == 32_228

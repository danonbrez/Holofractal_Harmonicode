"""Pass 219 I152 fixed target/work-manifold optimization invariants."""
from __future__ import annotations

from typing import Any

PASS = 219
ITERATION = "I152"

TARGET_RADIX = 72
TARGET_EXPONENT = 42
WORKING_MANIFOLD_MULTIPLIER = 3
WORKING_MANIFOLD_EXPONENT = 72

EXHAUSTION_RATIO_NUMERATOR = 81
EXHAUSTION_RATIO_DENOMINATOR = 7

TARGET_CARDINALITY = TARGET_RADIX ** TARGET_EXPONENT
WORKING_MANIFOLD_CARDINALITY = (
    WORKING_MANIFOLD_MULTIPLIER * (TARGET_RADIX ** WORKING_MANIFOLD_EXPONENT)
)
ROUTE_MULTIPLICITY_PER_TARGET = WORKING_MANIFOLD_CARDINALITY // TARGET_CARDINALITY
MAX_EFFECTIVE_EXHAUSTION_WORK = (
    TARGET_CARDINALITY * EXHAUSTION_RATIO_DENOMINATOR
) // EXHAUSTION_RATIO_NUMERATOR

EXPECTED_TARGET_DECIMAL = (
    "1018508951079768942856287659839033239780646340393381046433745481643146696720384"
)
EXPECTED_WORKING_DECIMAL = (
    "160347058642085998602075900420172615634821804179319834710808621932842456551257099299090591583867565623541495534132018087024926966939648"
)
EXPECTED_ROUTE_MULTIPLICITY_DECIMAL = (
    "157433136421721760341373217653428671558776396700106883072"
)
EXPECTED_MAX_EXHAUSTION_WORK_DECIMAL = (
    "88019292068622007407333501467570773808204004725353917593039732981506504654848"
)


class FixedCardinalityError(RuntimeError):
    pass


def _require_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise FixedCardinalityError(f"{name}_MUST_BE_EXACT_INTEGER")
    return value


def validate_fixed_cardinalities() -> dict[str, object]:
    if TARGET_CARDINALITY != 5184 ** 21:
        raise FixedCardinalityError("TARGET_5184_POWER_21_DRIFT")
    if TARGET_CARDINALITY != 72 ** 42:
        raise FixedCardinalityError("TARGET_72_POWER_42_DRIFT")
    if str(TARGET_CARDINALITY) != EXPECTED_TARGET_DECIMAL:
        raise FixedCardinalityError("TARGET_DECIMAL_DRIFT")

    if WORKING_MANIFOLD_CARDINALITY != 3 * (72 ** 72):
        raise FixedCardinalityError("WORKING_MANIFOLD_DRIFT")
    if str(WORKING_MANIFOLD_CARDINALITY) != EXPECTED_WORKING_DECIMAL:
        raise FixedCardinalityError("WORKING_MANIFOLD_DECIMAL_DRIFT")

    if WORKING_MANIFOLD_CARDINALITY % TARGET_CARDINALITY != 0:
        raise FixedCardinalityError("WORKING_MANIFOLD_NOT_EXACT_TARGET_FIBRATION")
    if ROUTE_MULTIPLICITY_PER_TARGET != 3 * (72 ** 30):
        raise FixedCardinalityError("ROUTE_MULTIPLICITY_DRIFT")
    if str(ROUTE_MULTIPLICITY_PER_TARGET) != EXPECTED_ROUTE_MULTIPLICITY_DECIMAL:
        raise FixedCardinalityError("ROUTE_MULTIPLICITY_DECIMAL_DRIFT")

    if (TARGET_CARDINALITY * EXHAUSTION_RATIO_DENOMINATOR) % EXHAUSTION_RATIO_NUMERATOR != 0:
        raise FixedCardinalityError("EXHAUSTION_BOUND_NOT_INTEGRAL")
    if str(MAX_EFFECTIVE_EXHAUSTION_WORK) != EXPECTED_MAX_EXHAUSTION_WORK_DECIMAL:
        raise FixedCardinalityError("EXHAUSTION_BOUND_DECIMAL_DRIFT")

    return {
        "schema": "HHS_PASS219_I152_FIXED_CARDINALITY_RECEIPT_V1",
        "pass": PASS,
        "iteration": ITERATION,
        "target": {
            "expression": "72^42=5184^21",
            "exact_cardinality_decimal": str(TARGET_CARDINALITY),
            "fixed": True,
        },
        "working_manifold": {
            "expression": "3*72^72",
            "exact_cardinality_decimal": str(WORKING_MANIFOLD_CARDINALITY),
            "fixed": True,
        },
        "route_multiplicity_per_target_block": {
            "expression": "3*72^30",
            "exact_cardinality_decimal": str(ROUTE_MULTIPLICITY_PER_TARGET),
        },
        "exhaustion_budget": {
            "required_reduction_ratio": "81/7",
            "max_effective_work_expression": "72^42*7/81",
            "max_effective_work_decimal": str(MAX_EFFECTIVE_EXHAUSTION_WORK),
        },
        "authority_changed": False,
        "physical_full_exhaustion_claim": False,
        "result": "PASS",
    }


def encode_working_route(target_block_index: int, route_index: int) -> int:
    block = _require_int(target_block_index, "TARGET_BLOCK_INDEX")
    route = _require_int(route_index, "ROUTE_INDEX")
    if not 0 <= block < TARGET_CARDINALITY:
        raise FixedCardinalityError("TARGET_BLOCK_INDEX_OUT_OF_RANGE")
    if not 0 <= route < ROUTE_MULTIPLICITY_PER_TARGET:
        raise FixedCardinalityError("ROUTE_INDEX_OUT_OF_RANGE")
    return block * ROUTE_MULTIPLICITY_PER_TARGET + route


def decode_working_route(working_index: int) -> tuple[int, int]:
    index = _require_int(working_index, "WORKING_INDEX")
    if not 0 <= index < WORKING_MANIFOLD_CARDINALITY:
        raise FixedCardinalityError("WORKING_INDEX_OUT_OF_RANGE")
    return divmod(index, ROUTE_MULTIPLICITY_PER_TARGET)


def evaluate_exhaustion_work(effective_work_units: int) -> dict[str, object]:
    work = _require_int(effective_work_units, "EFFECTIVE_WORK_UNITS")
    if work < 0:
        raise FixedCardinalityError("EFFECTIVE_WORK_UNITS_NEGATIVE")
    within = work * EXHAUSTION_RATIO_NUMERATOR <= (
        TARGET_CARDINALITY * EXHAUSTION_RATIO_DENOMINATOR
    )
    return {
        "effective_work_units": work,
        "max_effective_work_units": MAX_EFFECTIVE_EXHAUSTION_WORK,
        "required_reduction_ratio": "81/7",
        "within_81_over_7_exhaustion_budget": within,
        "classification": "WITHIN_BUDGET" if within else "OUTSIDE_BUDGET",
    }


def local_reduction_meets_exhaustion_ratio(
    baseline_work_units: int,
    selected_work_units: int,
) -> bool:
    baseline = _require_int(baseline_work_units, "BASELINE_WORK_UNITS")
    selected = _require_int(selected_work_units, "SELECTED_WORK_UNITS")
    if baseline < 0 or selected <= 0:
        raise FixedCardinalityError("INVALID_LOCAL_REDUCTION_WORK")
    return baseline * EXHAUSTION_RATIO_DENOMINATOR >= (
        selected * EXHAUSTION_RATIO_NUMERATOR
    )

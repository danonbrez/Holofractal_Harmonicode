"""Pass 219 HNAN 4x4 recursive two-view gate.

This module preserves three synchronized, non-interchangeable views:

1. the row-major serialized 4x4 binary address tensor;
2. the exact x/y substitution view where 0 := y/(4*x^4), 1 := x*y;
3. the HNAN ordered 1/0 gate
   (x+y-z-w+xy+yx-zw-wz)/EmptySet.

The Jordan refinement records the exact depth-2 nilpotent zero chain while
preserving the supplied ordered closure source 0=∅=AB/P⁴∅=HNAN.

All algebraic forms are stored as immutable ordered AST tuples. No host
arithmetic evaluates the native slash, commutes ordered products, cancels the
ordered zero closure, or replaces HNAN with STATE_1 / STATE_0.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Iterable, Sequence

SCHEMA = "HHS_PASS219_HNAN_4X4_RECURSIVE_GATE_V1"
VERSION = "1.1.0"

SERIALIZED_4X4 = (
    0, 0, 0, 1,
    1, 0, 1, 1,
    1, 1, 1, 0,
    0, 1, 0, 0,
)

TENSOR_01 = (
    (0, 0, 0, 1),
    (1, 0, 1, 1),
    (1, 1, 1, 0),
    (0, 1, 0, 0),
)

STATE_0 = ("Quotient", "y", ("Product", "4", ("Power", "x", 4)))
STATE_1 = ("Product", "x", "y")

XY = ("Product", "x", "y")
YX = ("Product", "y", "x")
ZW = ("Product", "z", "w")
WZ = ("Product", "w", "z")

HNAN_CENTER_EXPRESSION = "x+y-z-w+xy+yx-zw-wz"
HNAN_NUMERATOR = (
    "Sum",
    "x",
    "y",
    ("Negate", "z"),
    ("Negate", "w"),
    XY,
    YX,
    ("Negate", ZW),
    ("Negate", WZ),
)
HNAN_GATE_10 = ("Quotient", HNAN_NUMERATOR, "EmptySet")

HNAN_ZERO_CLOSURE_SOURCE = "0=∅=AB/P⁴∅=HNAN"
M01_JORDAN_STRUCTURE = (
    "DirectSum",
    ("JordanBlock", 0, 2),
    ("Semisimple", -1),
    ("Semisimple", 2),
)
MXY_GENERIC_CHANNELS = (
    ("JordanBlock", 0, 2),
    ("Semisimple", "r-s"),
    ("Semisimple", "2(r+s)"),
)
MXY_GENERIC_CONDITIONS = ("r!=s", "r+s!=0")


class HNANGateError(ValueError):
    pass


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def serialize_4x4(matrix: Sequence[Sequence[int]]) -> tuple[int, ...]:
    rows = tuple(tuple(row) for row in matrix)
    if len(rows) != 4 or any(len(row) != 4 for row in rows):
        raise HNANGateError("HNAN tensor must be exactly 4x4")
    flat = tuple(cell for row in rows for cell in row)
    if any(isinstance(cell, bool) or cell not in (0, 1) for cell in flat):
        raise HNANGateError("HNAN binary view admits only exact 0/1 cells")
    return flat


def deserialize_4x4(serialized: Iterable[int]) -> tuple[tuple[int, ...], ...]:
    values = tuple(serialized)
    if len(values) != 16:
        raise HNANGateError("HNAN serialization must contain exactly 16 cells")
    if any(isinstance(cell, bool) or cell not in (0, 1) for cell in values):
        raise HNANGateError("HNAN serialization admits only exact 0/1 cells")
    return tuple(
        tuple(values[offset:offset + 4])
        for offset in range(0, 16, 4)
    )


def materialize_xy_view_reference(
    matrix: Sequence[Sequence[int]] = TENSOR_01,
) -> tuple[tuple[tuple[Any, ...], ...], ...]:
    rows = deserialize_4x4(serialize_4x4(matrix))
    return tuple(
        tuple(STATE_0 if cell == 0 else STATE_1 for cell in row)
        for row in rows
    )


TENSOR_XY = materialize_xy_view_reference(TENSOR_01)


def materialize_xy_view() -> tuple[tuple[tuple[Any, ...], ...], ...]:
    """Return the prevalidated immutable x/y view without rebuilding it."""
    return TENSOR_XY


def hnan_gate(lhs: int, rhs: int) -> tuple[Any, ...]:
    """Resolve the explicitly defined ordered HNAN 1/0 transition only."""
    if (
        isinstance(lhs, bool)
        or isinstance(rhs, bool)
        or (lhs, rhs) != (1, 0)
    ):
        raise HNANGateError(
            "HNAN gate is defined here only for ordered transition 1/0"
        )
    return HNAN_GATE_10


def _freeze(node: Any) -> Any:
    if isinstance(node, list):
        return tuple(_freeze(value) for value in node)
    if isinstance(node, tuple):
        return tuple(_freeze(value) for value in node)
    return node


def recursive_two_view_reference(node: Any) -> Any:
    """Recursively lift binary leaves and exact ordered Quotient[1,0]."""
    node = _freeze(node)
    if type(node) is int:
        if node == 0:
            return STATE_0
        if node == 1:
            return STATE_1
        return node
    if isinstance(node, tuple):
        if (
            len(node) == 3
            and node[0] == "Quotient"
            and node[1:] == (1, 0)
        ):
            return HNAN_GATE_10
        return tuple(
            recursive_two_view_reference(value)
            for value in node
        )
    return node


@lru_cache(maxsize=4096)
def _recursive_two_view_cached(node: Any) -> Any:
    if type(node) is int:
        if node == 0:
            return STATE_0
        if node == 1:
            return STATE_1
        return node
    if isinstance(node, tuple):
        if (
            len(node) == 3
            and node[0] == "Quotient"
            and node[1:] == (1, 0)
        ):
            return HNAN_GATE_10
        return tuple(
            _recursive_two_view_cached(value)
            for value in node
        )
    return node


def recursive_two_view(node: Any) -> Any:
    """Memoized exact structural lift for repeated recursive tensor evaluation."""
    return _recursive_two_view_cached(_freeze(node))


def _matrix_multiply(
    left: Sequence[Sequence[int]],
    right: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    rows = tuple(tuple(row) for row in left)
    rhs = tuple(tuple(row) for row in right)
    if not rows or not rhs:
        raise HNANGateError("empty matrix is not admitted")
    inner = len(rhs)
    columns = len(rhs[0])
    if any(len(row) != inner for row in rows):
        raise HNANGateError("matrix multiplication shape mismatch")
    if any(len(row) != columns for row in rhs):
        raise HNANGateError("ragged matrix is not admitted")
    return tuple(
        tuple(
            sum(rows[i][k] * rhs[k][j] for k in range(inner))
            for j in range(columns)
        )
        for i in range(len(rows))
    )


def _matrix_power(
    matrix: Sequence[Sequence[int]],
    exponent: int,
) -> tuple[tuple[int, ...], ...]:
    if isinstance(exponent, bool) or not isinstance(exponent, int) or exponent < 0:
        raise HNANGateError("matrix exponent must be a nonnegative exact integer")
    base = tuple(tuple(int(value) for value in row) for row in matrix)
    if len(base) != 4 or any(len(row) != 4 for row in base):
        raise HNANGateError("Jordan receipt expects the canonical 4x4 tensor")
    result = tuple(
        tuple(1 if i == j else 0 for j in range(4))
        for i in range(4)
    )
    for _ in range(exponent):
        result = _matrix_multiply(result, base)
    return result


def _matrix_rank_exact(matrix: Sequence[Sequence[int]]) -> int:
    rows = [
        [Fraction(value) for value in row]
        for row in matrix
    ]
    if not rows:
        return 0
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise HNANGateError("ragged matrix is not admitted")

    rank = 0
    column = 0
    while rank < len(rows) and column < width:
        pivot = next(
            (
                row_index
                for row_index in range(rank, len(rows))
                if rows[row_index][column] != 0
            ),
            None,
        )
        if pivot is None:
            column += 1
            continue

        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][column]
        rows[rank] = [value / pivot_value for value in rows[rank]]

        for row_index in range(len(rows)):
            if row_index == rank:
                continue
            factor = rows[row_index][column]
            if factor == 0:
                continue
            rows[row_index] = [
                value - factor * basis_value
                for value, basis_value in zip(
                    rows[row_index],
                    rows[rank],
                    strict=True,
                )
            ]

        rank += 1
        column += 1

    return rank


def _matrix_linear_combination(
    *terms: tuple[int, Sequence[Sequence[int]]],
) -> tuple[tuple[int, ...], ...]:
    if not terms:
        raise HNANGateError("at least one matrix term is required")
    return tuple(
        tuple(
            sum(
                coefficient * matrix[i][j]
                for coefficient, matrix in terms
            )
            for j in range(4)
        )
        for i in range(4)
    )


def _flatten_matrix(
    matrix: Sequence[Sequence[int]],
) -> tuple[int, ...]:
    return tuple(value for row in matrix for value in row)


def jordan_refinement_receipt() -> dict[str, Any]:
    """Return exact integer/rational evidence for the HNAN Jordan refinement."""
    m = TENSOR_01
    identity = _matrix_power(m, 0)
    m2 = _matrix_power(m, 2)
    m3 = _matrix_power(m, 3)
    m4 = _matrix_power(m, 4)

    rank_m = _matrix_rank_exact(m)
    rank_m2 = _matrix_rank_exact(m2)
    nullity_m = 4 - rank_m
    nullity_m2 = 4 - rank_m2

    recurrence_target = _matrix_linear_combination((1, m3), (2, m2))
    recurrence_exact = m4 == recurrence_target

    flattened = (
        _flatten_matrix(identity),
        _flatten_matrix(m),
        _flatten_matrix(m2),
        _flatten_matrix(m3),
    )
    krylov_rows = tuple(
        tuple(column[row] for column in flattened)
        for row in range(16)
    )
    krylov_rank = _matrix_rank_exact(krylov_rows)

    checks = {
        "rank_m01_3": rank_m == 3,
        "nullity_m01_1": nullity_m == 1,
        "nullity_m01_squared_2": nullity_m2 == 2,
        "degree4_recurrence_exact": recurrence_exact,
        "lower_degree_recurrence_excluded": krylov_rank == 4,
        "jordan_zero_chain_depth_2":
            nullity_m == 1 and nullity_m2 == 2,
        "minimal_polynomial_equals_characteristic":
            recurrence_exact and krylov_rank == 4,
        "zero_closure_source_preserved":
            HNAN_ZERO_CLOSURE_SOURCE == "0=∅=AB/P⁴∅=HNAN",
    }

    payload = {
        "schema": "HHS_PASS219_HNAN_JORDAN_REFINEMENT_RECEIPT_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "rank_m01": rank_m,
        "nullity_m01": nullity_m,
        "nullity_m01_squared": nullity_m2,
        "characteristic_polynomial":
            "lambda^2*(lambda-2)*(lambda+1)",
        "minimal_polynomial":
            "lambda^2*(lambda-2)*(lambda+1)",
        "jordan_structure": M01_JORDAN_STRUCTURE,
        "binary_mode_inventory": (
            ("NilpotentChain", "depth=2"),
            ("Semisimple", -1),
            ("Semisimple", 2),
        ),
        "lifted_characteristic_polynomial":
            "lambda^2*(lambda-(r-s))*(lambda-2*(r+s))",
        "generic_lift_conditions": MXY_GENERIC_CONDITIONS,
        "generic_lifted_mode_inventory": MXY_GENERIC_CHANNELS,
        "special_loci": {
            "r=s": {
                "characteristic_polynomial":
                    "lambda^3*(lambda-4r)",
                "rank_for_r_nonzero": 1,
                "nullity_for_r_nonzero": 3,
            },
            "r=-s": {
                "characteristic_polynomial":
                    "lambda^3*(lambda-2r)",
                "rank_for_r_nonzero": 2,
                "nullity_for_r_nonzero": 2,
            },
        },
        "hnan_boundary_correspondence":
            "J2(0) <-> ordered 1/0 HNAN boundary",
        "hnan_zero_closure_source": HNAN_ZERO_CLOSURE_SOURCE,
        "zero_closure_is_ordered_system_internal": True,
        "zero_closure_scalar_cancellation_authorized": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    }
    payload["receipt_sha256"] = sha256(
        _stable(payload).encode("utf-8")
    ).hexdigest()
    return payload


def invariant_receipt() -> dict[str, Any]:
    jordan = jordan_refinement_receipt()
    checks = {
        "serialized_length_16": len(SERIALIZED_4X4) == 16,
        "matrix_shape_4x4": tuple(map(len, TENSOR_01)) == (4, 4, 4, 4),
        "row_major_round_trip": serialize_4x4(TENSOR_01) == SERIALIZED_4X4,
        "zero_count_8": SERIALIZED_4X4.count(0) == 8,
        "one_count_8": SERIALIZED_4X4.count(1) == 8,
        "xy_yx_distinct": XY != YX,
        "zw_wz_distinct": ZW != WZ,
        "hnan_emptyset_denominator": HNAN_GATE_10[-1] == "EmptySet",
        "hnan_not_scalar_state_division":
            HNAN_GATE_10 != ("Quotient", STATE_1, STATE_0),
        "cached_reference_parity":
            materialize_xy_view() == materialize_xy_view_reference(),
        "jordan_refinement_pass": jordan["status"] == "PASS",
    }
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "serialized": list(SERIALIZED_4X4),
        "hnan_center_expression": HNAN_CENTER_EXPRESSION,
        "state_0": STATE_0,
        "state_1": STATE_1,
        "hnan_gate_10": HNAN_GATE_10,
        "hnan_zero_closure_source": HNAN_ZERO_CLOSURE_SOURCE,
        "jordan_refinement": jordan,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "host_scalar_division_authorized": False,
        "ordered_product_commutation_authorized": False,
    }
    payload["receipt_sha256"] = sha256(
        _stable(payload).encode("utf-8")
    ).hexdigest()
    return payload


__all__ = [
    "HNAN_CENTER_EXPRESSION",
    "HNAN_GATE_10",
    "HNAN_NUMERATOR",
    "HNAN_ZERO_CLOSURE_SOURCE",
    "M01_JORDAN_STRUCTURE",
    "MXY_GENERIC_CHANNELS",
    "MXY_GENERIC_CONDITIONS",
    "SERIALIZED_4X4",
    "STATE_0",
    "STATE_1",
    "TENSOR_01",
    "TENSOR_XY",
    "WZ",
    "XY",
    "YX",
    "ZW",
    "HNANGateError",
    "deserialize_4x4",
    "hnan_gate",
    "invariant_receipt",
    "jordan_refinement_receipt",
    "materialize_xy_view",
    "materialize_xy_view_reference",
    "recursive_two_view",
    "recursive_two_view_reference",
    "serialize_4x4",
]

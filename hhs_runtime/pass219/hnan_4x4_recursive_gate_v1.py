"""Pass 219 HNAN 4x4 recursive two-view gate.

This module preserves three synchronized, non-interchangeable views:

1. the row-major serialized 4x4 binary address tensor;
2. the exact x/y substitution view where 0 := y/(4*x^4), 1 := x*y;
3. the HNAN ordered 1/0 gate
   (x+y-z-w+xy+yx-zw-wz)/EmptySet.

All algebraic forms are stored as immutable ordered AST tuples. No host
arithmetic evaluates the native slash, commutes ordered products, or replaces
HNAN with STATE_1 / STATE_0.
"""
from __future__ import annotations

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


def invariant_receipt() -> dict[str, Any]:
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
    "SERIALIZED_4X4",
    "STATE_0",
    "STATE_1",
    "TENSOR_01",
    "TENSOR_XY",
    "WZ",
    "XY",
    "YX",
    "ZW",
    "deserialize_4x4",
    "hnan_gate",
    "invariant_receipt",
    "materialize_xy_view",
    "materialize_xy_view_reference",
    "recursive_two_view",
    "recursive_two_view_reference",
    "serialize_4x4",
]

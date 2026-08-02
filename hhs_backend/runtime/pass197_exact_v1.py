"""Exact rational, Gaussian-rational, matrix, and VM5184 primitives for Pass 197."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping

try:
    from hhs_backend.runtime.runtime_workspace_object_v1 import hash72 as _kernel_hash72
    HASH_AUTHORITY = "HHS_HASH72_KERNEL_AUTHORITY"
except Exception:
    _kernel_hash72 = None
    HASH_AUTHORITY = "STANDALONE_SHA512_VALIDATION_FALLBACK"

HASH_TRANSPORT = "CANONICAL_SHA512_LENGTH_BOUND_TO_HASH72_RING"
CELL_COUNT = 81
LANE_COUNT = 64
ADDRESS_COUNT = CELL_COUNT * LANE_COUNT
ZERO_HASH72 = "0" * 72


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def hash72(label: str, value: Any) -> str:
    canonical = canonical_json(value).encode("utf-8")
    canonical_sha512 = hashlib.sha512(canonical).hexdigest()
    if _kernel_hash72 is not None:
        return _kernel_hash72(
            label,
            {
                "schema": "HHS_PASS_197_BOUNDED_HASH72_TRANSPORT_V1",
                "canonical_sha512": canonical_sha512,
                "canonical_bytes": len(canonical),
            },
        )
    return hashlib.sha512(
        f"{label}\u241f{len(canonical)}\u241f{canonical_sha512}".encode("utf-8")
    ).hexdigest()[:72]


def exact_fraction(value: Any, *, field: str) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{field} requires an exact rational; floating point is forbidden")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        try:
            return Fraction(value)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"invalid exact rational for {field}") from exc
    if isinstance(value, Mapping):
        try:
            return Fraction(int(value["numerator"]), int(value["denominator"]))
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"invalid exact rational object for {field}") from exc
    raise ValueError(f"unsupported exact rational for {field}")


def fraction_payload(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


@dataclass(frozen=True)
class GaussianRational:
    real: Fraction = Fraction(0)
    imag: Fraction = Fraction(0)

    @staticmethod
    def coerce(value: Any) -> "GaussianRational":
        return value if isinstance(value, GaussianRational) else GaussianRational(exact_fraction(value, field="gaussian component"))

    def __add__(self, other: Any) -> "GaussianRational":
        rhs = self.coerce(other)
        return GaussianRational(self.real + rhs.real, self.imag + rhs.imag)

    __radd__ = __add__

    def __neg__(self) -> "GaussianRational":
        return GaussianRational(-self.real, -self.imag)

    def __sub__(self, other: Any) -> "GaussianRational":
        return self + (-self.coerce(other))

    def __rsub__(self, other: Any) -> "GaussianRational":
        return self.coerce(other) - self

    def __mul__(self, other: Any) -> "GaussianRational":
        rhs = self.coerce(other)
        return GaussianRational(self.real * rhs.real - self.imag * rhs.imag, self.real * rhs.imag + self.imag * rhs.real)

    __rmul__ = __mul__

    def __truediv__(self, other: Any) -> "GaussianRational":
        rhs = self.coerce(other)
        norm = rhs.real * rhs.real + rhs.imag * rhs.imag
        if norm == 0:
            raise ZeroDivisionError("singular Gaussian-rational denominator")
        return self * GaussianRational(rhs.real / norm, -rhs.imag / norm)

    def payload(self) -> dict[str, dict[str, int]]:
        return {"real": fraction_payload(self.real), "imag": fraction_payload(self.imag)}


I = GaussianRational(Fraction(0), Fraction(1))
Matrix = tuple[tuple[Fraction, ...], ...]


def matrix_identity(size: int) -> Matrix:
    return tuple(tuple(Fraction(int(i == j)) for j in range(size)) for i in range(size))


def matrix_multiply(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix dimension mismatch")
    return tuple(tuple(sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0)) for j in range(len(right[0]))) for i in range(len(left)))


def matrix_inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    if not size or any(len(row) != size for row in matrix):
        raise ValueError("matrix inverse requires a square matrix")
    rows = [list(matrix[i]) + list(matrix_identity(size)[i]) for i in range(size)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if rows[row][column]), None)
        if pivot is None:
            raise ZeroDivisionError("matrix is singular")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [value / divisor for value in rows[column]]
        for row in range(size):
            if row != column and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [a - factor * b for a, b in zip(rows[row], rows[column])]
    return tuple(tuple(row[size:]) for row in rows)


def matrix_power(matrix: Matrix, exponent: int) -> Matrix:
    if isinstance(exponent, bool) or not isinstance(exponent, int):
        raise ValueError("matrix exponent must be an exact integer")
    if exponent < 0:
        return matrix_power(matrix_inverse(matrix), -exponent)
    result, base, power = matrix_identity(len(matrix)), matrix, exponent
    while power:
        if power & 1:
            result = matrix_multiply(result, base)
        base = matrix_multiply(base, base)
        power >>= 1
    return result


M: Matrix = (
    (Fraction(1, 2), Fraction(2, 3), Fraction(3, 5)),
    (Fraction(4, 7), Fraction(5, 8), Fraction(2, 3)),
    (Fraction(7, 11), Fraction(8, 13), Fraction(3, 5)),
)
M_INVERSE = matrix_inverse(M)
COLUMN_SUMS = tuple(sum((M[i][j] for i in range(3)), Fraction(0)) for j in range(3))
INVERSE_ROW_SUMS = tuple(sum(M_INVERSE[i], Fraction(0)) for i in range(3))
EXPECTED_COLUMN_SUMS = (Fraction(263, 154), Fraction(595, 312), Fraction(28, 15))
EXPECTED_INVERSE_ROW_SUMS = (Fraction(2464, 6473), Fraction(6552, 6473), Fraction(1455, 6473))


def cell_index(i: int, j: int, k: int, l: int) -> int:
    if any(value not in range(3) for value in (i, j, k, l)):
        raise ValueError("VM81 tensor index outside [0,2]")
    return 27 * i + 9 * j + 3 * k + l


def address(cell: int, lane: int) -> int:
    if cell not in range(CELL_COUNT) or lane not in range(LANE_COUNT):
        raise ValueError("VM5184 address component out of range")
    return LANE_COUNT * cell + lane


def decode_address(state: int) -> tuple[int, int, int, int, int]:
    if state not in range(ADDRESS_COUNT):
        raise ValueError("VM5184 address out of range")
    cell, lane = divmod(state, LANE_COUNT)
    i, rem = divmod(cell, 27)
    j, rem = divmod(rem, 9)
    k, l = divmod(rem, 3)
    return i, j, k, l, lane


def original_gate(x: Fraction, y: Fraction, q: Matrix, i: int, j: int, k: int, l: int) -> GaussianRational:
    if not x or not y:
        raise ZeroDivisionError("original gate requires nonzero x and y")
    if i == j:
        left = x * (GaussianRational(M[i][j] / y) + I) * y
        right = GaussianRational(q[k][l] / x) + I
        denominator = GaussianRational(1 - 3 * x * y, INVERSE_ROW_SUMS[i] * y + COLUMN_SUMS[j] * x)
    else:
        left = GaussianRational(M[i][j] / y) + I
        right = GaussianRational(q[k][l] / x) + I
        denominator = GaussianRational(-3, COLUMN_SUMS[j] / y + INVERSE_ROW_SUMS[i] / x)
    return left * right / denominator


def compact_gate(x: Fraction, y: Fraction, q: Matrix, i: int, j: int, k: int, l: int) -> GaussianRational:
    numerator = (GaussianRational(M[i][j]) + I * y) * (GaussianRational(q[k][l]) + I * x)
    denominator = GaussianRational(int(i == j) - 3 * x * y, INVERSE_ROW_SUMS[i] * y + COLUMN_SUMS[j] * x)
    return numerator / denominator

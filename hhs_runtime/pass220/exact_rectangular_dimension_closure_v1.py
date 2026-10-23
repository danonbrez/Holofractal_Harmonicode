"""Pass 220 exact rectangular dimension-closure candidate witness.

This is a non-authoritative ingress geometry witness. It does not evaluate
NcalcMatrixPower, infer HNAN phase outputs, or mint VM81/Hash72/Hash216.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
from typing import Sequence


@dataclass(frozen=True)
class RectangularClosureWitness:
    shape_a: tuple[int, int]
    shape_b: tuple[int, int]
    cells_a: tuple[Fraction, ...]
    cells_b: tuple[Fraction, ...]
    product_capacity: int
    exact_square_root: int
    ring_width: int
    copies_per_ring: int
    ring_a: tuple[Fraction, ...]
    ring_b: tuple[Fraction, ...]
    phase_status: str = "HNAN_NOT_EVALUATED"
    admission_status: str = "CANDIDATE_ONLY"


def _rational(value: int | str | Fraction) -> Fraction:
    if isinstance(value, float):
        raise TypeError("floating point is not an exact serialization value")
    if not isinstance(value, (int, str, Fraction)):
        raise TypeError("entry must be an exact integer, fraction or rational string")
    return Fraction(value)


def _matrix(rows: Sequence[Sequence[int | str | Fraction]]) -> tuple[tuple[int, int], tuple[Fraction, ...]]:
    if not rows or not rows[0]:
        raise ValueError("matrix must be nonempty")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("ragged matrix")
    cells = tuple(_rational(v) for row in rows for v in row)
    return (len(rows), width), cells


def rectangular_dimension_closure(
    a: Sequence[Sequence[int | str | Fraction]],
    b: Sequence[Sequence[int | str | Fraction]],
    *,
    ring_width: int = 72,
    require_transpose: bool = True,
) -> RectangularClosureWitness:
    """Witness sqrt((m*n)*(n*m)) == m*n with exact ordered ring repeats.

    This computes cell-capacity geometry, not the numeric matrix product AB.
    If require_transpose=True, B must be the exact entrywise transpose of A.
    """
    shape_a, cells_a = _matrix(a)
    shape_b, cells_b = _matrix(b)
    m, n = shape_a
    if shape_b != (n, m):
        raise ValueError("B must have the transposed rectangular dimensions")
    if require_transpose:
        if any(cells_a[i*n+j] != cells_b[j*m+i]
               for i in range(m) for j in range(n)):
            raise ValueError("transpose entries mismatch")
    if isinstance(ring_width, bool) or not isinstance(ring_width, int) or ring_width <= 0:
        raise ValueError("ring width must be a positive integer")
    count = m*n
    if ring_width % count:
        raise ValueError("cell count does not evenly quantize into ring")
    capacity = count * (shape_b[0] * shape_b[1])
    root = isqrt(capacity)
    if root*root != capacity or root != count:
        raise ValueError("dimension product does not close exactly")
    copies = ring_width // count
    return RectangularClosureWitness(
        shape_a, shape_b, cells_a, cells_b, capacity, root,
        ring_width, copies, cells_a * copies, cells_b * copies
    )

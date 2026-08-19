from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

# Exact inherited scalar projections used only by this reference/oracle.
A2 = 1
B2 = 2
C2 = 3

B4 = B2 * B2
B6 = B4 * B2
C4 = C2 * C2

ZERO_L = C2 - C2
N1 = A2
N2 = B2
N3 = C2
N4 = B4
N5 = B2 + C2
N6 = B2 * C2
N7 = B4 + C2
N8 = B6
N9 = C4
N12 = C2 * B4
N36 = B4 * C4
N72 = B6 * C4
N73 = N72 + A2
N66 = N72 - N6
N5256 = N72 * N73

LO_SHU_POLYNOMIAL_PROJECTION = (
    (B4, C4, B2),
    (C2, B2 + C2, B4 + C2),
    (B6, A2, B2 * C2),
)
LO_SHU_MAGIC_SUM = C2 * (B2 + C2)

PHASE_X = 0
PHASE_Y = 1
PHASE_XY = 4
PHASE_YX = 5
ORDERED_TAG_XY = 0x5859
ORDERED_TAG_YX = 0x5958


@dataclass(frozen=True)
class QuantizationConstraintWitness:
    xy_scalar_projection: int
    primitive_b2_exponent: Fraction
    full_cycle_b2_exponent: Fraction
    u_power: int
    qr_bit: int
    qr_lane: str
    qr_phase: int


def lo_shu_lines() -> tuple[tuple[int, int, int], ...]:
    rows = LO_SHU_POLYNOMIAL_PROJECTION
    cols = tuple(tuple(rows[r][c] for r in range(3)) for c in range(3))
    diagonals = (
        (rows[0][0], rows[1][1], rows[2][2]),
        (rows[0][2], rows[1][1], rows[2][0]),
    )
    return rows + cols + diagonals


def primitive_b2_exponent(xy_scalar_projection: int = A2) -> Fraction:
    if xy_scalar_projection == ZERO_L:
        raise ZeroDivisionError("xy scalar projection must be nonzero in the metric bridge")
    return Fraction(A2, N12 * xy_scalar_projection) - A2


def full_cycle_b2_exponent(xy_scalar_projection: int = A2) -> Fraction:
    return N72 * primitive_b2_exponent(xy_scalar_projection)


def metric_closure_identity(xy_scalar_projection: int = A2) -> tuple[int, Fraction]:
    """Return the exact symbolic identity u_q^power = (b^2)^exponent."""
    return N72 * N73, full_cycle_b2_exponent(xy_scalar_projection)


def quadratic_reciprocity_bit(p: int, q: int) -> int:
    if p <= ZERO_L or q <= ZERO_L or p % B2 == ZERO_L or q % B2 == ZERO_L:
        raise ValueError("quadratic reciprocity audit inputs must be positive odd integers")
    numerator = (p - A2) * (q - A2)
    if numerator % B4 != ZERO_L:
        raise ValueError("odd reciprocity inputs must make the Lo Shu N4 quotient integral")
    return (numerator // B4) % B2


def quadratic_reciprocity_lane(p: int, q: int) -> str:
    return "xy" if quadratic_reciprocity_bit(p, q) == ZERO_L else "yx"


def quadratic_reciprocity_phase(p: int, q: int) -> int:
    return (N36 * quadratic_reciprocity_bit(p, q)) % N72


def build_witness(p: int, q: int, xy_scalar_projection: int = A2) -> QuantizationConstraintWitness:
    power, exponent = metric_closure_identity(xy_scalar_projection)
    bit = quadratic_reciprocity_bit(p, q)
    return QuantizationConstraintWitness(
        xy_scalar_projection=xy_scalar_projection,
        primitive_b2_exponent=primitive_b2_exponent(xy_scalar_projection),
        full_cycle_b2_exponent=exponent,
        u_power=power,
        qr_bit=bit,
        qr_lane="xy" if bit == ZERO_L else "yx",
        qr_phase=(N36 * bit) % N72,
    )


def reference_invariants() -> dict[str, bool]:
    lines = lo_shu_lines()
    power, exponent = metric_closure_identity(A2)
    return {
        "lo_shu_exact": LO_SHU_POLYNOMIAL_PROJECTION == ((4, 9, 2), (3, 5, 7), (8, 1, 6)),
        "lo_shu_magic": all(sum(line) == LO_SHU_MAGIC_SUM for line in lines),
        "n12": N12 == 12,
        "n36": N36 == 36,
        "n72": N72 == 72,
        "n73": N73 == 73,
        "n66": N66 == 66,
        "n5256": N5256 == 5256,
        "primitive_metric_exponent": primitive_b2_exponent(A2) == Fraction(-11, 12),
        "metric_power": power == N5256,
        "full_cycle_metric_exponent": exponent == -N66,
    }


__all__ = [
    "A2",
    "B2",
    "C2",
    "ZERO_L",
    "N6",
    "N12",
    "N36",
    "N66",
    "N72",
    "N73",
    "N5256",
    "LO_SHU_POLYNOMIAL_PROJECTION",
    "LO_SHU_MAGIC_SUM",
    "PHASE_X",
    "PHASE_Y",
    "PHASE_XY",
    "PHASE_YX",
    "ORDERED_TAG_XY",
    "ORDERED_TAG_YX",
    "QuantizationConstraintWitness",
    "lo_shu_lines",
    "primitive_b2_exponent",
    "full_cycle_b2_exponent",
    "metric_closure_identity",
    "quadratic_reciprocity_bit",
    "quadratic_reciprocity_lane",
    "quadratic_reciprocity_phase",
    "build_witness",
    "reference_invariants",
]

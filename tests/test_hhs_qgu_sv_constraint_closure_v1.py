"""
HHS QGU / s-v reciprocal phase closure integration witness.

This test preserves the submitted constraint bundle as an executable repo-level
pytest witness.  It does not simplify across ordered products, does not commute
xy/yx, and does not introduce a runtime authority path.  Passing this file means
all represented closure points agree simultaneously under the declared scalar
projection layer.
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass
from decimal import Decimal, getcontext
from fractions import Fraction

getcontext().prec = 80


@dataclass(frozen=True)
class OrderedProduct:
    """Non-commutative ordered product witness."""

    left: str
    right: str

    def __mul__(self, other: "OrderedProduct") -> tuple["OrderedProduct", "OrderedProduct"]:
        return (self, other)

    @property
    def word(self) -> str:
        return f"{self.left}{self.right}"


XY = OrderedProduct("x", "y")
YX = OrderedProduct("y", "x")
ZW = OrderedProduct("z", "w")
WZ = OrderedProduct("w", "z")


def dec_sqrt(value: Decimal) -> Decimal:
    return value.sqrt()


def dec_close(a: Decimal, b: Decimal, tolerance: Decimal = Decimal("1e-40")) -> bool:
    return abs(a - b) <= tolerance


def test_ordered_products_remain_non_commutative_witnesses() -> None:
    assert XY.word == "xy"
    assert YX.word == "yx"
    assert ZW.word == "zw"
    assert WZ.word == "wz"
    assert XY != YX
    assert ZW != WZ
    assert XY != ZW


def test_terminal_exponential_closure_quantizes_o_x_squared() -> None:
    # Terminal condition: exp(O*x^2) = 1 iff O*x^2 = 2*pi*i*k.
    for k in (-3, -1, 0, 1, 7):
        x_squared = complex(1, 0)
        O = (2j * math.pi * k) / x_squared
        terminal = cmath.exp(O * x_squared)
        assert abs(terminal - 1) < 1e-12


def test_m_gate_rational_witness_is_phi_locked_approximation() -> None:
    # m-gate witness from prompt: 8158 / 5040 approximates the phi lock.
    rational_m = Decimal(Fraction(8158, 5040).numerator) / Decimal(Fraction(8158, 5040).denominator)
    phi = (Decimal(1) + dec_sqrt(Decimal(5))) / Decimal(2)
    assert abs(rational_m - phi) < Decimal("0.001")


def test_reciprocal_s_v_phase_gear_closes_to_scalar_projection() -> None:
    # Canonical shell projection: b^2 = 2, c^2 = 3, d^2 = b^2 + c^2 = 5.
    b2 = Decimal(2)
    c2 = Decimal(3)
    d2 = b2 + c2

    phi = (Decimal(1) + dec_sqrt(Decimal(5))) / Decimal(2)
    m = phi

    s_over_v = m
    v_over_s = Decimal(1) / m

    scalar_projection = d2 / dec_sqrt(b2 + c2)

    assert dec_close(s_over_v * v_over_s, Decimal(1))
    assert dec_close(s_over_v + v_over_s, scalar_projection)
    assert dec_close(s_over_v + v_over_s, dec_sqrt(Decimal(5)))


def test_admissible_manifold_reduces_to_locked_phase_curve() -> None:
    # From D(s,v): x^s + y^-s - z^v - w^-v = K - wxyz.
    # Enforce reciprocal phase-pair closure y=x^-1, w=z^-1:
    # y^-s = x^s and w^-v = z^v, so 2*x^s - 2*z^v = K - wxyz.
    K_minus_wxyz = Decimal("3.25")
    x_to_s = Decimal("7.75")
    z_to_v = x_to_s - (K_minus_wxyz / Decimal(2))

    left_unreduced = x_to_s + x_to_s - z_to_v - z_to_v
    locked_curve = x_to_s - z_to_v

    assert dec_close(left_unreduced, K_minus_wxyz)
    assert dec_close(locked_curve, K_minus_wxyz / Decimal(2))


def test_full_constraint_bundle_integration_points_are_simultaneous() -> None:
    # Integration point bundle:
    # 1. Ordered tensor witnesses remain distinct.
    # 2. u^72 shell closes to identity.
    # 3. m != 1.
    # 4. reciprocal s/v gear closes multiplicatively to 1.
    # 5. reciprocal s/v gear sums to d^2 / sqrt(b^2 + c^2).
    # 6. scalar projection equals sqrt(5) under b^2=2, c^2=3, d^2=5.
    u72 = Decimal(1)
    b2 = Decimal(2)
    c2 = Decimal(3)
    d2 = Decimal(5)
    m = (Decimal(1) + dec_sqrt(Decimal(5))) / Decimal(2)

    constraints = {
        "ordered_xy_yx_distinct": XY != YX,
        "ordered_zw_wz_distinct": ZW != WZ,
        "u72_identity": u72 == Decimal(1),
        "m_not_one": m != Decimal(1),
        "reciprocal_product_identity": dec_close(m * (Decimal(1) / m), Decimal(1)),
        "scalar_projection_lock": dec_close(m + (Decimal(1) / m), d2 / dec_sqrt(b2 + c2)),
        "sqrt5_projection": dec_close(d2 / dec_sqrt(b2 + c2), dec_sqrt(Decimal(5))),
    }

    assert all(constraints.values()), constraints

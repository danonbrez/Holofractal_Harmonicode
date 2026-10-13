"""Pass 220 complex P rational-scale diagnostic.

Exact Gaussian rational scalar projection only.  Native HNAN scale-to-closure
claims require an admissible source->phase witness->VM81 transition receipt;
these assertions deliberately do not manufacture one.
"""
from fractions import Fraction
from itertools import product

import pytest


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def neg(a):
    return (-a[0], -a[1])


def mul(a, b):
    return (a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0])


def divide(a, b):
    denominator = b[0]*b[0] + b[1]*b[1]
    if denominator == 0:
        raise ZeroDivisionError("zero Gaussian-rational denominator")
    return ((a[0]*b[0] + a[1]*b[1])/denominator,
            (a[1]*b[0] - a[0]*b[1])/denominator)


ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))
BASE = [
    (Fraction(0), Fraction(1, 4)),
    (Fraction(1, 3), Fraction(1, 4)),
    (Fraction(-1, 2), Fraction(1, 3)),
    (Fraction(0), Fraction(1)),
]
SCALES = [Fraction(1, 2), Fraction(1), Fraction(2), Fraction(3),
          Fraction(4), Fraction(6), Fraction(17, 5), Fraction(1000)]


@pytest.mark.parametrize("base,scale", list(product(BASE, SCALES)))
def test_complex_centered_rational_scale_closure_is_exact(base, scale):
    P = mul(base, (scale, Fraction(0)))
    p, q = add(P, neg(ONE)), add(P, ONE)
    # Three exact scalar-projection witnesses, without floats or order changes.
    assert add(mul(P, P), neg(mul(p, q))) == ONE
    numerator = mul(add(q, neg(p)), P)
    assert divide(numerator, add(p, q)) == ONE
    assert mul(divide(p, q), divide(q, p)) == ONE
    # Pn/P is kept as an explicit quotient operation for the witness,
    # not used to rewrite the native ordered tensor AST.
    assert divide(P, base) == (scale, Fraction(0))


def test_scalar_projection_does_not_claim_scale_threshold():
    # The 32 exact samples all close at *every* tested nonzero scale.
    # A first-closure threshold therefore cannot be inferred here.
    for base, scale in product(BASE, SCALES):
        P = mul(base, (scale, Fraction(0)))
        p, q = add(P, neg(ONE)), add(P, ONE)
        assert add(mul(P, P), neg(mul(p, q))) == ONE


def test_denominator_boundaries_stay_explicit():
    for P in (neg(ONE), ZERO, ONE):
        p, q = add(P, neg(ONE)), add(P, ONE)
        assert add(mul(P, P), neg(mul(p, q))) == ONE
        if P == neg(ONE):
            with pytest.raises(ZeroDivisionError):
                divide(p, q)
        elif P == ZERO:
            with pytest.raises(ZeroDivisionError):
                divide(mul(add(q, neg(p)), P), add(p, q))
        else:
            with pytest.raises(ZeroDivisionError):
                divide(q, p)

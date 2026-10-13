"""Pass 220 ordered weighted reciprocal / HNAN residual conformance.

Structural witness only: equality inside an ordered channel is not a Python
boolean or scalar numerator, and the quotient denominator is a typed equality
boundary. This module does not promote candidate evidence into VM81 authority.
"""
from fractions import Fraction

from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import (
    HNAN_CENTER_EXPRESSION,
    HNAN_LO_SHU_TENSOR_SOURCE,
    HNAN_TERMINAL_SOURCE,
    hnan_loshu_resolution_receipt,
)

# Each node is an immutable ordered AST; P and its dependent p/q are untouched.
XY_RECIP = ("Product", ("Quotient", "x", "y"), ("Quotient", "y", "x"))
ZW_RECIP = ("Product", ("Quotient", "z", "w"), ("Quotient", "w", "z"))
XY_BOUND = ("Eq", XY_RECIP, ("Quotient", ("Product", "x", "y"), ("Power", "z", 4)))
ZW_BOUND = ("Eq", ZW_RECIP, ("Quotient", ("Product", "z", "w"), ("Power", "x", 4)))
A2 = ("Power", "a", 2)
B2 = ("Power", "b", 2)
C2 = ("Power", "c", 2)
NUMERATOR = ("Eq", ("Sum", ("Product", A2, XY_BOUND),
                         ("Product", A2, ZW_BOUND)),
             ("Product", B2, ("Power", "x", 2), ("Power", "z", 2)))
DENOMINATOR = ("Eq", ("Sum", ("Product", "x", "y"),
                              ("Product", "z", "w")), ("Subtract", C2, A2))
RIGHT = ("Sum", ("Quotient", ("Subtract", C2, B2), A2),
         "x", "y", ("Negate", "z"), ("Negate", "w"),
         ("Product", "x", "y"), ("Power", "y", 2),
         ("Negate", ("Product", "z", "w")),
         ("Negate", ("Power", "w", 2)))
SOURCE = ("Eq", ("Quotient", NUMERATOR, DENOMINATOR), RIGHT)
# Ordered residual relative to the inherited center: right-minus-center is
# a comparison constructor; no symbolic simplifier may reorder expressions.
RESIDUAL_SOURCE = "1+y^2-yx-w^2+wz"


def test_source_is_nested_ordered_equality_not_boolean_arithmetic():
    assert SOURCE[0] == "Eq"
    assert SOURCE[1][0] == "Quotient"
    assert SOURCE[1][1] is NUMERATOR
    assert SOURCE[1][2] is DENOMINATOR
    assert NUMERATOR[1][1][2] is XY_BOUND
    assert NUMERATOR[1][2][2] is ZW_BOUND
    assert NUMERATOR[2][1] is B2
    assert DENOMINATOR[1][1] == ("Product", "x", "y")
    assert DENOMINATOR[1][2] == ("Product", "z", "w")
    assert RIGHT[-1] == ("Negate", ("Power", "w", 2))


def test_exact_canonical_square_positions_and_residual_text():
    a2, b2, c2 = Fraction(1), Fraction(2), Fraction(3)
    assert c2 - a2 == b2
    assert (c2 - b2) / a2 == 1
    assert RESIDUAL_SOURCE == "1+y^2-yx-w^2+wz"
    assert HNAN_CENTER_EXPRESSION == "x+y-z-w+xy+yx-zw-wz"
    assert HNAN_LO_SHU_TENSOR_SOURCE[1][1] == HNAN_CENTER_EXPRESSION
    assert RIGHT != HNAN_CENTER_EXPRESSION


def test_inherited_hnan_receipt_and_epsilon_survive():
    receipt = hnan_loshu_resolution_receipt()
    assert receipt["status"] == "PASS"
    assert receipt["center_expression"] == HNAN_CENTER_EXPRESSION
    assert receipt["terminal_source"] == HNAN_TERMINAL_SOURCE == "xy+epsilon"
    assert receipt["checks"]["xy_yx_distinct"]
    assert receipt["checks"]["zw_wz_distinct"]


def test_swapped_phase_channels_change_source():
    flipped = ("Eq", ("Quotient", ("Eq", ("Sum",
        ("Product", A2, ZW_BOUND), ("Product", A2, XY_BOUND)),
        NUMERATOR[2]), DENOMINATOR), RIGHT)
    assert flipped != SOURCE

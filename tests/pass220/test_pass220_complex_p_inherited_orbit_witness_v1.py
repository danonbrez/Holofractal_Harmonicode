"""Exact inherited nine-step orbit; complex P remains typed provenance.

This verifies an actual I025 executable finite permutation cycle, NOT that
complex P modifies its transition or that canonical VM81 has signed a state.
"""
from fractions import Fraction
import pytest

from hhs_runtime.hhs_pass220_schrodinger_firing_order_v1 import (
    MACROCYCLE_ORDER, shift_permutation, permutation_power,
    permutation_unitary_exact,
)
from tests.pass220.test_pass220_complex_p_rational_scaling_v1 import (
    BASE, SCALES, ONE, add, neg, mul,
)

PERMUTATION = shift_permutation(MACROCYCLE_ORDER, 1)
IDENTITY = tuple(range(1, MACROCYCLE_ORDER + 1))


def test_inherited_exact_transition_first_closes_at_nine():
    assert permutation_unitary_exact(PERMUTATION)
    trajectory = tuple(permutation_power(PERMUTATION, tick) for tick in range(10))
    assert trajectory[0] == trajectory[9] == IDENTITY
    assert len(set(trajectory[:9])) == 9
    assert all(state != IDENTITY for state in trajectory[1:9])


@pytest.mark.parametrize("base", BASE)
@pytest.mark.parametrize("scale", SCALES)
def test_scaled_complex_p_preserves_exact_witness_without_false_binding(base, scale):
    P = mul(base, (scale, Fraction(0)))
    p, q = add(P, neg(ONE)), add(P, ONE)
    assert add(mul(P,P), neg(mul(p,q))) == ONE
    # I025 orbit order is independently established, not inferred from P.
    assert permutation_power(PERMUTATION, MACROCYCLE_ORDER) == IDENTITY
    assert all(permutation_power(PERMUTATION, k) != IDENTITY for k in range(1, 9))

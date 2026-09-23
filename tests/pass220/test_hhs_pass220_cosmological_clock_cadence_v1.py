from fractions import Fraction

import pytest

from hhs_runtime.hhs_pass220_cosmological_clock_cadence_v1 import (
    PHASE_ORBIT,
    Pass220I022ClockError,
    cadence_observables,
    clock_contract_descriptor,
    closure_duration,
    dot_h_p,
    full_i022_witness,
    h_p,
    make_transition,
    sigma_formula,
    sigma_lookup,
    variable_cadence_closed_form,
    w_p,
)


def test_phase_orbit_is_exact_order_nine_and_lookup_matches_formula():
    assert PHASE_ORBIT == (8, 24, 40, 56, 72, 16, 32, 48, 64)
    assert len(set(PHASE_ORBIT)) == 9
    for n in range(5184):
        assert sigma_lookup(n) == sigma_formula(n)
        assert sigma_lookup(n + 9) == sigma_lookup(n)


def test_closure_duration_uses_exact_dependency_max_not_host_time():
    theta = closure_duration(
        (Fraction(1, 9), Fraction(5, 9), Fraction(2, 9)),
        Fraction(1, 9),
    )
    assert theta == Fraction(2, 3)


def test_clock_rejects_inexact_or_invalid_duration_inputs():
    with pytest.raises(Pass220I022ClockError):
        closure_duration((0.5,), Fraction(1, 9))
    with pytest.raises(Pass220I022ClockError):
        closure_duration((Fraction(-1, 9),), Fraction(1, 9))
    with pytest.raises(Pass220I022ClockError):
        make_transition(0, Fraction(1), Fraction(0))
    with pytest.raises(Pass220I022ClockError):
        h_p(make_transition(0, 1, 1), 0)


def test_h_p_is_exact_rational_projection():
    sample = make_transition(3, Fraction(5, 7), Fraction(11, 13))
    assert sample.sigma == 56
    assert h_p(sample, Fraction(17, 19)) == Fraction(1235, 1309)


def test_constant_increment_and_constant_cadence_close_to_w_minus_one():
    previous = make_transition(0, Fraction(7, 13), Fraction(5, 17))
    current = make_transition(1, Fraction(7, 13), Fraction(5, 17))
    tau = Fraction(19, 23)
    assert dot_h_p(previous, current, tau) == 0
    assert w_p(previous, current, tau) == -1
    obs = cadence_observables(previous, current, tau)
    assert obs["dot_h_p"] == 0
    assert obs["w_p"] == -1
    assert obs["a_p"] == obs["h_p"] * obs["h_p"]


def test_variable_cadence_matches_wolfram_closed_form_and_tau_cancels():
    previous = make_transition(0, Fraction(11, 7), Fraction(2, 5))
    current = make_transition(1, Fraction(11, 7), Fraction(3, 5))
    expected = variable_cadence_closed_form(
        Fraction(11, 7), previous.theta, current.theta
    )
    assert w_p(previous, current, Fraction(1)) == expected
    assert w_p(previous, current, Fraction(101, 37)) == expected
    assert expected != -1


def test_derivative_requires_adjacent_admitted_transition_indices():
    previous = make_transition(0, 1, 1)
    nonadjacent = make_transition(2, 1, 1)
    with pytest.raises(Pass220I022ClockError):
        dot_h_p(previous, nonadjacent, 1)


def test_g72_remains_typed_unresolved_and_projection_has_no_authority():
    descriptor = clock_contract_descriptor()
    assert descriptor["g72_operator"] == "G72"
    assert descriptor["g72_identity"] == "G72^72==2"
    assert descriptor["g72_scalar_evaluation_allowed"] is False
    assert descriptor["host_wall_clock_authority"] is False
    assert descriptor["floating_point_authority"] is False
    assert descriptor["projection_only"] is True
    assert descriptor["canonical_admission_authority"] is False


def test_full_i022_witness_is_closed_and_deterministic():
    first = full_i022_witness()
    second = full_i022_witness()
    assert first == second
    assert first["phase_lookup_formula_equivalent_first_5184"] is True
    assert first["constant_cadence_dot_h_p"] == "0/1"
    assert first["constant_cadence_w_p"] == "-1/1"
    assert first["variable_cadence_w_p"] == "-1/9"
    assert first["variable_cadence_matches_closed_form"] is True
    assert first["closed"] is True

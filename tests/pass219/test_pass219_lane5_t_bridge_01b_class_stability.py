from __future__ import annotations

from fractions import Fraction

import pytest

from hhs_runtime.pass219.lane5_t_bridge_01b_class_stability import (
    TBridge01BError,
    class_stability_witness,
    exact_halving_envelope,
    self_test,
)


def test_exact_halving_envelope_contracts_by_two_to_the_order() -> None:
    receipt = exact_halving_envelope(
        h=Fraction(1, 4),
        p=2,
        envelope_constant=Fraction(3, 2),
    )
    assert receipt["exact"] is True
    assert receipt["contraction_ratio"] == {
        "numerator": 1,
        "denominator": 4,
    }
    assert receipt["expected_ratio"] == receipt["contraction_ratio"]
    assert receipt["actual_residue_monotonicity_inferred"] is False


def test_sign_class_is_stable_under_halving_inside_relative_remainder_sector() -> None:
    receipt = class_stability_witness(
        h=Fraction(1, 4),
        p=2,
        leading_coefficient=Fraction(3, 5),
        relative_remainder_h=Fraction(1, 4),
        relative_remainder_half=Fraction(-1, 4),
        envelope_constant=Fraction(1),
    )

    assert receipt["status"] == "PASS"
    assert all(receipt["checks"].values())
    assert receipt["sgn3_epsilon_h"] == 1
    assert receipt["sgn3_epsilon_half"] == 1
    assert receipt["sgn3_leading_coefficient"] == 1
    assert receipt["workload_interval_certificate"] == "OPEN"
    assert receipt["global_actual_epsilon_monotonicity_claimed"] is False
    assert receipt["monotone_envelope_claimed"] is True
    assert receipt["canonical_runtime_mutation_authority"] is False


def test_negative_class_is_also_stable() -> None:
    receipt = class_stability_witness(
        h=Fraction(3, 10),
        p=3,
        leading_coefficient=Fraction(-7, 9),
        relative_remainder_h=Fraction(-1, 3),
        relative_remainder_half=Fraction(1, 5),
        envelope_constant=Fraction(2),
    )
    assert receipt["status"] == "PASS"
    assert receipt["sgn3_epsilon_h"] == -1
    assert receipt["sgn3_epsilon_half"] == -1


def test_zero_or_remainder_boundary_fails_closed() -> None:
    with pytest.raises(TBridge01BError, match="nonzero leading coefficient"):
        class_stability_witness(
            h=1,
            p=1,
            leading_coefficient=0,
            relative_remainder_h=0,
            relative_remainder_half=0,
            envelope_constant=1,
        )

    with pytest.raises(TBridge01BError, match=r"must be < 1"):
        class_stability_witness(
            h=1,
            p=1,
            leading_coefficient=1,
            relative_remainder_h=1,
            relative_remainder_half=0,
            envelope_constant=2,
        )


def test_insufficient_envelope_fails_closed() -> None:
    with pytest.raises(TBridge01BError, match="does not dominate"):
        class_stability_witness(
            h=Fraction(1, 4),
            p=2,
            leading_coefficient=1,
            relative_remainder_h=Fraction(3, 4),
            relative_remainder_half=Fraction(1, 2),
            envelope_constant=1,
        )


def test_self_test() -> None:
    assert self_test()["status"] == "PASS"

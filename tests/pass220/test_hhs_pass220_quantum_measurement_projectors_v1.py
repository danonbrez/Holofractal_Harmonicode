from fractions import Fraction

import pytest

from hhs_runtime.hhs_pass220_quantum_measurement_projectors_v1 import (
    Cyclotomic72,
    Pass220I026MeasurementError,
    basis_state,
    collapse_candidate,
    fourier_mode,
    inner_product,
    measurement_contract_descriptor,
    measurement_weights,
    phase72,
    project_state,
    projector_weight_numerator,
    state_add,
    state_norm2,
    zero_state,
)


STATE_SHA = "a" * 64
ADMISSION_SHA = "b" * 64


def test_cyclotomic_72_exact_field_relations():
    z = phase72(1)
    one = Cyclotomic72.one()
    minus_one = Cyclotomic72.rational(-1)

    assert phase72(72) == one
    assert z ** 72 == one
    assert phase72(36) == minus_one
    assert phase72(18) * phase72(18) == minus_one
    assert phase72(18) ** 4 == one

    # Phi_72(z)=z^24-z^12+1=0.
    assert (
        phase72(24)
        - phase72(12)
        + Cyclotomic72.one()
        == Cyclotomic72.zero()
    )


def test_conjugation_is_exact_inverse_on_phases():
    for exponent in range(72):
        value = phase72(exponent)
        assert value.conjugate() == phase72(-exponent)
        assert value * value.conjugate() == Cyclotomic72.one()


def test_basis_state_has_uniform_exact_fourier_weights():
    state = basis_state(0)
    receipt = measurement_weights(
        state,
        source_state_receipt_sha256=STATE_SHA,
    )
    assert receipt["weights_complete_exactly"] is True
    assert receipt["total_norm"] == Cyclotomic72.one().as_data()

    expected = Cyclotomic72.rational(Fraction(1, 9)).as_data()
    assert [
        outcome["weight_numerator"]
        for outcome in receipt["outcomes"]
    ] == [expected] * 9


def test_fourier_mode_is_sharp_projective_measurement():
    for selected in range(9):
        state = fourier_mode(selected)
        total = state_norm2(state)
        assert total == Cyclotomic72.rational(9)

        for outcome in range(9):
            numerator = projector_weight_numerator(state, outcome)
            if outcome == selected:
                assert numerator == total
                assert project_state(state, outcome) == state
            else:
                assert numerator == Cyclotomic72.zero()
                assert project_state(state, outcome) == zero_state()


def test_projector_completeness_on_nontrivial_cyclotomic_state():
    state = state_add(
        basis_state(0),
        tuple(
            phase72(index + 1) * amplitude
            for index, amplitude in enumerate(basis_state(3))
        ),
    )
    norm = state_norm2(state)
    total = Cyclotomic72.zero()
    for outcome in range(9):
        total = total + projector_weight_numerator(state, outcome)
    assert total == norm

    receipt = measurement_weights(
        state,
        source_state_receipt_sha256=STATE_SHA,
    )
    assert receipt["weights_complete_exactly"] is True


def test_inner_product_conjugate_symmetry():
    left = state_add(basis_state(0), basis_state(2))
    right = state_add(
        basis_state(1),
        tuple(
            phase72(8) * amplitude
            for amplitude in basis_state(2)
        ),
    )
    assert inner_product(left, right).conjugate() == inner_product(
        right, left
    )


def test_collapse_candidate_is_repeatable_and_exclusive():
    state = basis_state(0)
    candidate = collapse_candidate(
        state,
        4,
        source_state_receipt_sha256=STATE_SHA,
        admission_witness_sha256=ADMISSION_SHA,
    )
    assert candidate["outcome"] == 4
    assert candidate["projector_repeatable"] is True
    assert candidate["orthogonal_outcomes_excluded"] == [
        0, 1, 2, 3, 5, 6, 7, 8
    ]
    assert candidate["canonical_state_mutated"] is False
    assert candidate["canonical_admission_authority"] is False
    assert candidate["lo_shu_admission_binding_closed"] is False
    assert candidate["admission_witness_semantics_verified"] is False


def test_zero_weight_outcome_cannot_form_collapse_candidate():
    state = fourier_mode(0)
    with pytest.raises(
        Pass220I026MeasurementError,
        match="zero-weight outcome",
    ):
        collapse_candidate(
            state,
            1,
            source_state_receipt_sha256=STATE_SHA,
            admission_witness_sha256=ADMISSION_SHA,
        )


def test_zero_state_has_no_normalized_measurement_weights():
    with pytest.raises(
        Pass220I026MeasurementError,
        match="zero state",
    ):
        measurement_weights(
            zero_state(),
            source_state_receipt_sha256=STATE_SHA,
        )


def test_outcome_and_receipt_validation_fail_closed():
    with pytest.raises(Pass220I026MeasurementError):
        fourier_mode(-1)
    with pytest.raises(Pass220I026MeasurementError):
        fourier_mode(9)
    with pytest.raises(Pass220I026MeasurementError):
        basis_state(True)
    with pytest.raises(Pass220I026MeasurementError):
        collapse_candidate(
            basis_state(0),
            9,
            source_state_receipt_sha256=STATE_SHA,
            admission_witness_sha256=ADMISSION_SHA,
        )
    with pytest.raises(Pass220I026MeasurementError):
        measurement_weights(
            basis_state(0),
            source_state_receipt_sha256="bad",
        )


def test_measurement_receipt_is_bit_deterministic():
    state = state_add(basis_state(0), basis_state(5))
    first = measurement_weights(
        state,
        source_state_receipt_sha256=STATE_SHA,
    )
    second = measurement_weights(
        state,
        source_state_receipt_sha256=STATE_SHA,
    )
    assert first == second
    assert first["receipt_sha256"] == second["receipt_sha256"]


def test_contract_closes_weight_algebra_but_not_selection_authority():
    descriptor = measurement_contract_descriptor()
    assert descriptor["state_space"] == "Q(zeta72)^9"
    assert descriptor["cyclotomic_polynomial"] == "x^24-x^12+1"
    assert descriptor["born_weight_algebra_closed"] is True
    assert descriptor["stochastic_born_frequency_law_closed"] is False
    assert descriptor["lo_shu_admission_binding_closed"] is False
    assert descriptor["canonical_admission_authority"] is False
    assert descriptor["random_sampling_authority"] is False
    assert descriptor["floating_point_authority"] is False
    assert descriptor["projection_only"] is True

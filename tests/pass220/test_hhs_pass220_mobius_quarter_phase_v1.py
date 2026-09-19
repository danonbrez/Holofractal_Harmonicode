from fractions import Fraction

import pytest

from hhs_runtime.hhs_pass220_mobius_quarter_phase_v1 import (
    LEMMA,
    PHASE_POSITIONS,
    Pass220MobiusError,
    Qsqrt5,
    composed_i011_witness,
    golden_unit_witness,
    harmonic_closure,
    harmonic_involution_witness,
    harmonic_pair_from_lambda,
    harmonic_partner,
    mobius_matrix_power4,
    mobius_orbit4,
    mobius_rho,
    mobius_rho_inverse,
    norm_polynomial_m,
    norm_polynomial_rho,
    norm_transform_identity,
    phase_cycle_witness,
    vm81_harmonic_coherence,
)


def test_mobius_pair_is_exactly_invertible():
    m = Fraction(3, 1)
    rho = mobius_rho(m)
    assert rho == Fraction(1, 2)
    assert mobius_rho_inverse(rho) == m


def test_mobius_half_cycle_is_negative_reciprocal():
    orbit = mobius_orbit4(Fraction(3, 1))
    assert orbit == (
        Fraction(3, 1),
        Fraction(1, 2),
        Fraction(-1, 3),
        Fraction(-2, 1),
        Fraction(3, 1),
    )
    assert orbit[2] == -1 / orbit[0]


def test_mobius_matrix_is_projective_order_four():
    witness = mobius_matrix_power4()
    assert witness["matrix"] == [[1, -1], [1, 1]]
    assert witness["matrix_squared"] == [[0, -2], [2, 0]]
    assert witness["matrix_fourth"] == [[-4, 0], [0, -4]]
    assert witness["projective_identity"] is True


def test_phase_cycle_maps_exactly_to_0_18_36_54_72():
    witness = phase_cycle_witness(Fraction(2, 1))
    assert PHASE_POSITIONS == (0, 18, 36, 54, 72)
    assert witness["half_cycle_is_negative_reciprocal"] is True
    assert witness["full_cycle_closed"] is True
    assert witness["phase_values"]["0"] == {"numerator": 2, "denominator": 1}
    assert witness["phase_values"]["36"] == {"numerator": -1, "denominator": 2}
    assert witness["phase_values"]["72"] == witness["phase_values"]["0"]


def test_harmonic_map_is_an_involution_with_unique_symmetric_example_two():
    assert harmonic_partner(Fraction(2, 1)) == 2
    assert harmonic_partner(Fraction(3, 1)) == Fraction(3, 2)
    assert harmonic_partner(Fraction(3, 2)) == 3
    witness = harmonic_involution_witness(Fraction(3, 1))
    assert witness["involution"] is True
    assert witness["fixed_point_if_symmetric"] is False


def test_harmonic_closure_accepts_symmetric_and_generic_branches():
    assert harmonic_closure(Fraction(2), Fraction(2))
    assert harmonic_closure(Fraction(3), Fraction(3, 2))
    assert not harmonic_closure(Fraction(2), Fraction(3))
    assert not harmonic_closure(Fraction(0), Fraction(2))


def test_translated_reciprocal_parameterization_is_exact():
    assert harmonic_pair_from_lambda(Fraction(1)) == (Fraction(2), Fraction(2))
    assert harmonic_pair_from_lambda(Fraction(2)) == (Fraction(3), Fraction(3, 2))
    with pytest.raises(Pass220MobiusError):
        harmonic_pair_from_lambda(Fraction(0))


def test_golden_unit_identity_is_exact_in_qsqrt5():
    witness = golden_unit_witness()
    assert witness["phi_squared_equals_phi_plus_one"] is True
    phi = Qsqrt5(Fraction(1, 2), Fraction(1, 2))
    one = Qsqrt5(1, 0)
    assert phi * phi == phi + one


def test_norm_polynomials_and_mobius_transform_agree_exactly():
    rho = Fraction(1, 3)
    witness = norm_transform_identity(rho)
    assert witness["identity_holds"] is True
    assert witness["left"] == witness["right"]
    m = mobius_rho_inverse(rho)
    assert (1 - rho) ** 4 * norm_polynomial_m(m) == 4 * norm_polynomial_rho(rho)


def test_vm81_harmonic_coherence_and_fold_passes_nine_local_nuclei():
    pairs = [(Fraction(2), Fraction(2))] * 9
    witness = vm81_harmonic_coherence(pairs)
    assert witness["nucleus_count"] == 9
    assert witness["vm81_cells"] == 81
    assert witness["admitted"] is True
    assert witness["reason_code"] == "ADMIT_LOCAL_HARMONIC_AND_FOLD"
    assert all(item["harmonic_closed"] for item in witness["nuclei"])


def test_vm81_fold_rejects_one_incoherent_nucleus():
    pairs = [(Fraction(2), Fraction(2))] * 8 + [(Fraction(2), Fraction(3))]
    witness = vm81_harmonic_coherence(pairs)
    assert witness["admitted"] is False
    assert witness["reason_code"] == "REJECT_HARMONIC_INCOHERENCE"


def test_singular_and_float_paths_fail_closed_and_composed_receipt_is_projection_only():
    with pytest.raises(Pass220MobiusError):
        mobius_rho(-1)
    with pytest.raises(Pass220MobiusError):
        mobius_orbit4(1)
    with pytest.raises(Pass220MobiusError):
        mobius_rho(3.0)
    with pytest.raises(Pass220MobiusError):
        harmonic_partner(1)
    with pytest.raises(Pass220MobiusError):
        vm81_harmonic_coherence([(2, 2)] * 8)

    witness = composed_i011_witness(Fraction(3), [(Fraction(2), Fraction(2))] * 9)
    assert witness["lemma"] == LEMMA
    assert witness["admitted_projection"] is True
    assert witness["floating_point_authority"] is False
    assert witness["projection_only"] is True
    assert witness["canonical_admission_authority"] is False

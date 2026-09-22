from fractions import Fraction

import pytest

from hhs_runtime.hhs_pass220_schrodinger_firing_order_v1 import (
    FULL_ORBIT_CYCLE_COUNT,
    MACROCYCLE_ORDER,
    Phase72,
    Pass220I025QuantumError,
    characteristic_polynomial_from_cycles,
    cyclotomic_9_factor_product,
    exact_energy_levels,
    firing_order,
    full_orbit_permutation,
    full_orbit_receipt,
    macrocycle_permutation,
    permutation_cycles,
    permutation_power,
    permutation_unitary_exact,
    quantum_contract_descriptor,
    sigma,
)


def test_firing_order_and_period_are_exact():
    assert firing_order() == (
        8, 24, 40, 56, 72, 16, 32, 48, 64
    )
    for n in range(72):
        assert sigma(n + 9) == sigma(n)


def test_macrocycle_is_exact_unitary_nine_cycle():
    u9 = macrocycle_permutation()
    assert permutation_unitary_exact(u9) is True
    assert permutation_power(u9, 9) == tuple(range(1, 10))
    assert tuple(
        sorted(len(c) for c in permutation_cycles(u9))
    ) == (9,)


def test_full_shift_by_16_is_eight_disjoint_nine_cycles():
    u72 = full_orbit_permutation()
    cycles = permutation_cycles(u72)
    lengths = tuple(sorted(len(c) for c in cycles))
    assert permutation_unitary_exact(u72) is True
    assert permutation_power(u72, 9) == tuple(range(1, 73))
    assert lengths == (9,) * 8
    assert len(cycles) == FULL_ORBIT_CYCLE_COUNT


def test_full_orbit_contains_canonical_firing_cycle():
    cycles = permutation_cycles(full_orbit_permutation())
    expected = (8, 24, 40, 56, 72, 16, 32, 48, 64)
    assert expected in cycles


def test_characteristic_polynomial_is_exact_cyclotomic_product():
    cp9 = characteristic_polynomial_from_cycles((9,))
    expected9 = cyclotomic_9_factor_product()
    assert cp9 == expected9
    assert cp9[0] == -1
    assert cp9[-1] == 1
    assert len(cp9) == 10

    cp72 = characteristic_polynomial_from_cycles((9,) * 8)
    assert len(cp72) == 73
    # Every 9-cycle contributes one copy of every ninth-root eigenvalue.
    assert cp72[0] == 1
    assert cp72[-1] == 1


def test_cyclotomic_phase_embeddings_are_exact_exponents():
    z = Phase72(1)
    assert z ** 72 == Phase72(0)
    assert z ** 8 == Phase72(8)
    i72 = Phase72(18)
    assert i72 ** 2 == Phase72(36)
    assert i72 ** 4 == Phase72(0)
    assert i72 ** 2 != Phase72(0)


def test_positive_energy_branch_uses_negative_eigenphase_sign():
    levels = exact_energy_levels()
    assert len(levels) == MACROCYCLE_ORDER
    for k, level in enumerate(levels):
        assert level.k == k
        assert level.turn_fraction == Fraction(k, 9)
        assert level.phase == Phase72(-8 * k)
        assert level.degeneracy == 8
    assert levels[0].exact_text == "0"
    assert levels[1].exact_text == (
        "u72*(2*pi*1/9)/(tau*theta)"
    )


def test_receipt_closes_and_is_bit_deterministic():
    first = full_orbit_receipt()
    second = full_orbit_receipt()
    assert first == second
    assert first["status"] == "PASS"
    assert first["pass_count"] == first["check_count"]
    assert first["full_orbit_cycle_lengths"] == (9,) * 8
    assert first["receipt_sha256"] == second["receipt_sha256"]


def test_receipt_records_logarithm_branch_and_gate_boundary():
    receipt = full_orbit_receipt()
    assert receipt["hamiltonian_branch"] == (
        "NONNEGATIVE_K_0_TO_8"
    )
    assert (
        receipt["single_U_has_unique_logarithm_without_branch"]
        is False
    )
    assert (
        receipt["finite_difference_gate_exact_log_hamiltonian"]
        is False
    )
    assert "ExpSym" in receipt["exact_committed_node_gate"]


def test_contract_does_not_conflate_finite_difference_with_exact_h():
    descriptor = quantum_contract_descriptor()
    assert descriptor["branch_required_for_unique_energy_labels"] is True
    assert descriptor["eigenphase_for_positive_branch"] == "zeta9^(-k)"
    assert descriptor["level_degeneracy"] == 8
    assert descriptor[
        "finite_difference_gate_is_exact_log_generator"
    ] is False
    assert descriptor["floating_point_authority"] is False
    assert descriptor["numerical_eigensolver_authority"] is False


def test_invalid_phase_and_permutation_inputs_fail_closed():
    with pytest.raises(Pass220I025QuantumError):
        Phase72(Fraction(1, 2))
    with pytest.raises(Pass220I025QuantumError):
        permutation_power((1, 1), 2)
    with pytest.raises(Pass220I025QuantumError):
        characteristic_polynomial_from_cycles((0,))

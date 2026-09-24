from __future__ import annotations

from fractions import Fraction

import pytest

from hhs_runtime.pass219.lane5_poincare_integral_bridge import (
    PoincareBridgeError,
    canonical_omega,
    carried_kick_drift,
    drift_matrix,
    is_symplectic,
    kick_matrix,
    poincare_bridge_receipt,
    reverse_drift_kick,
    simultaneous_old_state_euler,
    symplectic_defect,
    volume_only_witness,
)


def test_canonical_omega_exact() -> None:
    assert canonical_omega(2) == (
        (0, 0, 1, 0),
        (0, 0, 0, 1),
        (-1, 0, 0, 0),
        (0, -1, 0, 0),
    )


def test_kick_drift_and_compositions_are_symplectic_exactly() -> None:
    h = Fraction(1, 4)
    inverse_mass = ((1, 0), (0, 1))
    hessian = ((2, 1), (1, 3))

    kick = kick_matrix(h, hessian)
    drift = drift_matrix(h, inverse_mass)
    carried = carried_kick_drift(h, inverse_mass, hessian)
    reverse = reverse_drift_kick(h, inverse_mass, hessian)

    assert is_symplectic(kick)
    assert is_symplectic(drift)
    assert is_symplectic(carried)
    assert is_symplectic(reverse)

    assert carried != reverse
    assert symplectic_defect(carried) == (
        (0, 0, 0, 0),
        (0, 0, 0, 0),
        (0, 0, 0, 0),
        (0, 0, 0, 0),
    )


def test_simultaneous_old_state_euler_is_not_symplectic() -> None:
    explicit = simultaneous_old_state_euler(
        Fraction(1, 4),
        ((1, 0), (0, 1)),
        ((2, 1), (1, 3)),
    )
    assert not is_symplectic(explicit)


def test_volume_preservation_is_strictly_weaker_than_symplecticity() -> None:
    witness = volume_only_witness()
    assert not is_symplectic(witness)


def test_receipt_closes_poincare_invariant_and_keeps_energy_separate() -> None:
    receipt = poincare_bridge_receipt(
        h=Fraction(1, 4),
        inverse_mass=((1, 0), (0, 1)),
        hessian=((2, 1), (1, 3)),
    )

    assert receipt["status"] == "PASS"
    assert all(receipt["checks"].values())

    assert receipt["poincare_integral_invariant"] == (
        "Phi^*(sum_i dq_i wedge dp_i)=sum_i dq_i wedge dp_i"
    )
    assert receipt["four_d_projection_reading"] == (
        "oriented A1+A2 invariant; individual Ai may exchange"
    )
    assert receipt["volume_only_is_insufficient"] is True
    assert receipt["both_sequential_orders_symplectic"] is True
    assert receipt["simultaneous_old_state_explicit_symplectic"] is False
    assert receipt["exact_energy_conservation_claimed"] is False
    assert receipt["t_bridge_01b_energy_band_class_stability"] == "OPEN"
    assert receipt["canonical_runtime_mutation_authority"] is False


def test_invalid_symplectic_inputs_fail_closed() -> None:
    with pytest.raises(PoincareBridgeError, match="positive exact integer"):
        canonical_omega(0)

    with pytest.raises(PoincareBridgeError, match="must be symmetric"):
        carried_kick_drift(
            Fraction(1, 4),
            ((1, 2), (0, 1)),
            ((1, 0), (0, 1)),
        )

    with pytest.raises(PoincareBridgeError, match="exactly 2x2"):
        carried_kick_drift(
            Fraction(1, 4),
            ((1,),),
            ((1, 0), (0, 1)),
        )

"""Exact phase-root and projector witnesses: no floating-point authority."""
import pytest

from hhs_runtime.pass220.ers_qutrit_exact_phase_witness_v2 import (
    exact_qutrit_projector, phase_address, phase_root_witness,
)


def test_72_root_closure_and_branch_polarities():
    witnesses = [phase_root_witness(k) for k in range(72)]
    assert all(w["u72_exponent_mod72"] == 0 for w in witnesses)
    assert witnesses[1]["primitive_root"] is True
    assert witnesses[1]["u36_sign"] == -1
    assert witnesses[1]["u_minus180_exponent_mod72"] == 36
    assert witnesses[1]["u_minus180_equals_one"] is False
    assert witnesses[2]["primitive_root"] is False
    assert witnesses[2]["u36_sign"] == 1
    assert witnesses[0]["u_minus180_equals_one"] is True
    assert all(w["vm81_admission"] is False for w in witnesses)


def test_unique_addressed_polarity_sectors():
    all_addresses = [
        phase_address(k, sector)["linear_address"]
        for sector in range(4) for k in range(72)
    ]
    assert len(all_addresses) == 288
    assert sorted(all_addresses) == list(range(288))


@pytest.mark.parametrize("index", [-1, 72, 1.0, True, "1"])
def test_reject_invalid_root_indices(index):
    with pytest.raises(ValueError):
        phase_root_witness(index)


@pytest.mark.parametrize("sector", [-1, 4, 1.0, False])
def test_reject_invalid_polarity_sectors(sector):
    with pytest.raises(ValueError):
        phase_address(0, sector)


def test_exact_z3_projector_no_complex_float():
    witness = exact_qutrit_projector()
    assert witness["Z3_diagonal_root_exponents"] == (0, 24, 48)
    assert witness["Z3_projector_numerators"] == ((3, 0), (0, 0), (0, 0))
    assert witness["Pi_collapse"] == ((1,0,0), (0,0,0), (0,0,0))
    assert witness["Pi_squared_equals_Pi"] is True
    assert witness["projector_nonzero_norm_required"] is True
    assert witness["vm81_admission"] is False

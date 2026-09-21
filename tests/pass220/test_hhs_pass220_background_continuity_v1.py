from fractions import Fraction

import pytest

from hhs_runtime.hhs_pass220_background_continuity_v1 import (
    BARYON_EXPONENT,
    CURVATURE_EXPONENT,
    DARK_EXPONENT,
    RADIATION_EXPONENT,
    Pass220I024BackgroundError,
    background_contract_descriptor,
    background_h2,
    build_background_driven_trajectory,
    derive_background_transfer_receipts,
    initial_background_state,
    make_background_anchors,
    make_phase_input,
)
from hhs_runtime.hhs_pass220_exact_friedmann_transfer_v1 import (
    ExactExpr,
    exact_data,
)


ANCHOR_SHA = "a" * 64
PHASE_A = "b" * 64
PHASE_B = "c" * 64
PHASE_C = "d" * 64


def _anchors(**overrides):
    values = {
        "rho_b_ref": Fraction(1),
        "rho_r_ref": Fraction(2),
        "rho_d_ref": Fraction(3),
        "gravity_coupling": Fraction(1),
        "curvature_sign": 0,
        "anchor_receipt_sha256": ANCHOR_SHA,
    }
    values.update(overrides)
    return make_background_anchors(**values)


def _phases():
    return (
        make_phase_input(0, Fraction(1), Fraction(1), PHASE_A),
        make_phase_input(1, Fraction(1), Fraction(1), PHASE_B),
        make_phase_input(2, Fraction(1), Fraction(1), PHASE_C),
    )


def test_reference_background_is_finite_anchor_not_function():
    anchors = _anchors()
    state = initial_background_state(anchors, c0=1)
    assert state.rho_b == 1
    assert state.rho_r == 2
    assert state.rho_d == 3
    assert state.curvature_h2 == 0
    assert background_h2(state, anchors) == 6


def test_curvature_reference_is_derived_from_sign_and_exact_c0():
    closed = initial_background_state(
        _anchors(curvature_sign=1),
        c0=Fraction(5, 2),
    )
    open_state = initial_background_state(
        _anchors(curvature_sign=-1),
        c0=Fraction(5, 2),
    )
    assert closed.curvature_h2 == Fraction(-25, 4)
    assert open_state.curvature_h2 == Fraction(25, 4)


def test_anchor_validation_is_fail_closed():
    with pytest.raises(Pass220I024BackgroundError):
        _anchors(rho_b_ref=Fraction(-1))
    with pytest.raises(Pass220I024BackgroundError):
        _anchors(gravity_coupling=0)
    with pytest.raises(Pass220I024BackgroundError):
        _anchors(curvature_sign=2)
    with pytest.raises(Pass220I024BackgroundError):
        _anchors(anchor_receipt_sha256="bad")


def test_first_transfer_background_is_exact_rational_anchor_sum():
    transfers, witness = derive_background_transfer_receipts(
        _phases()[:1],
        _anchors(),
        tau=1,
        c0=1,
    )
    assert len(transfers) == 1
    assert transfers[0].background_h2 == 6
    assert witness["continuity_exponents"] == {
        "baryon": BARYON_EXPONENT,
        "dark": DARK_EXPONENT,
        "radiation": RADIATION_EXPONENT,
        "curvature": CURVATURE_EXPONENT,
    }


def test_later_background_is_generated_symbolically_from_prior_step():
    transfers, witness = derive_background_transfer_receipts(
        _phases()[:2],
        _anchors(),
        tau=1,
        c0=1,
    )
    assert transfers[0].background_h2 == 6
    assert isinstance(transfers[1].background_h2, ExactExpr)
    encoded = exact_data(transfers[1].background_h2)
    assert "exp" in repr(encoded)
    assert witness["continuity_receipts"][0] != witness[
        "continuity_receipts"
    ][1]
    assert transfers[0].source_receipt_sha256 != (
        transfers[1].source_receipt_sha256
    )


def test_zero_background_reduces_to_phase_only_i023_path():
    anchors = _anchors(
        rho_b_ref=0,
        rho_r_ref=0,
        rho_d_ref=0,
        gravity_coupling=1,
        curvature_sign=0,
    )
    transfers, _ = derive_background_transfer_receipts(
        _phases()[:2],
        anchors,
        tau=Fraction(7, 11),
        c0=1,
    )
    assert transfers[0].background_h2 == 0
    assert transfers[1].background_h2 == 0


def test_background_driven_trajectory_accepts_symbolic_background_receipts():
    result = build_background_driven_trajectory(
        _phases()[:2],
        _anchors(),
        tau=1,
        c0=1,
    )
    trajectory = result["trajectory"]
    assert trajectory["receipt_count"] == 2
    assert trajectory["nodes"][0]["total_h2"] == "7/1"
    assert trajectory["nodes"][1]["total_h2"] is None
    assert trajectory["nodes"][1]["total_h2_exact"]["op"] == "add"
    assert result["free_background_function_authority"] is False


def test_replay_is_bit_deterministic():
    kwargs = {
        "phases": _phases(),
        "anchors": _anchors(),
        "tau": Fraction(13, 17),
        "c0": 299792458,
    }
    first = build_background_driven_trajectory(**kwargs)
    second = build_background_driven_trajectory(**kwargs)
    assert first == second
    assert first["receipt_sha256"] == second["receipt_sha256"]


def test_phase_inputs_must_be_contiguous():
    phases = (
        make_phase_input(0, 1, 1, PHASE_A),
        make_phase_input(2, 1, 1, PHASE_B),
    )
    with pytest.raises(Pass220I024BackgroundError):
        derive_background_transfer_receipts(
            phases,
            _anchors(),
            tau=1,
            c0=1,
        )


def test_contract_forbids_free_background_and_inverse_authority():
    descriptor = background_contract_descriptor()
    assert "rho_b,n+1" in descriptor["baryon_continuity"]
    assert "rho_D,n+1" in descriptor["dark_continuity"]
    assert "rho_r,n+1" in descriptor["radiation_continuity"]
    assert descriptor["curvature_reference"] == (
        "K_ref=-k*c0^2 at a_ref=1"
    )
    assert descriptor["free_background_function_authority"] is False
    assert descriptor["host_wall_clock_authority"] is False
    assert descriptor["floating_point_authority"] is False
    assert descriptor["inverse_hz_state_authority"] is False
    assert descriptor["projection_only"] is True

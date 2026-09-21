from fractions import Fraction

import pytest

from hhs_runtime.hhs_pass220_exact_friedmann_transfer_v1 import (
    ExactExpr,
    Pass220I023TransferError,
    build_exact_trajectory,
    interval_log_scale_increment,
    make_transfer_receipt,
    phase_only_increment,
    total_h2,
    transfer_contract_descriptor,
)


SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64


def _r(n, lam=1, theta=1, background=0, sha=SHA_A):
    return make_transfer_receipt(
        n,
        Fraction(lam),
        Fraction(theta),
        Fraction(background),
        sha,
    )


def test_receipt_requires_canonical_phase_and_sha():
    receipt = _r(0)
    assert receipt.sigma == 8
    with pytest.raises(Pass220I023TransferError):
        make_transfer_receipt(0, 1, 1, 0, "not-a-sha")


def test_phase_h_and_total_h2_are_exact_rational():
    receipt = _r(
        0,
        lam=Fraction(3, 5),
        theta=Fraction(7, 11),
        background=Fraction(2, 9),
    )
    phase, h2 = total_h2(receipt, Fraction(13, 17))
    assert phase == Fraction(561, 455)
    assert h2 == Fraction(1590161, 828100)


def test_phase_only_log_scale_increment_is_tau_free_when_square_is_exact():
    receipt = _r(
        0,
        lam=Fraction(7, 13),
        theta=Fraction(5, 17),
        background=0,
    )
    assert phase_only_increment(
        receipt, Fraction(19, 23)
    ) == Fraction(7, 13)
    assert phase_only_increment(
        receipt, Fraction(101, 37)
    ) == Fraction(7, 13)


def test_non_square_friedmann_hubble_stays_symbolic():
    receipt = _r(0, lam=1, theta=1, background=1)
    inc = interval_log_scale_increment(receipt, 1)
    assert isinstance(inc, ExactExpr)
    assert "sqrt" in repr(inc)


def test_trajectory_is_deterministic_and_present_normalized():
    receipts = [
        _r(
            0,
            lam=Fraction(1, 9),
            theta=1,
            background=0,
            sha=SHA_A,
        ),
        _r(
            1,
            lam=Fraction(2, 9),
            theta=1,
            background=0,
            sha=SHA_B,
        ),
        _r(
            2,
            lam=Fraction(1, 3),
            theta=1,
            background=0,
            sha=SHA_C,
        ),
    ]
    first = build_exact_trajectory(
        receipts,
        tau=Fraction(5, 7),
        c0=299792458,
        curvature_sign=0,
    )
    second = build_exact_trajectory(
        receipts,
        tau=Fraction(5, 7),
        c0=299792458,
        curvature_sign=0,
    )
    assert first == second
    assert first["receipt_sha256"] == second["receipt_sha256"]
    assert first["nodes"][-1]["normalized_log_scale"] == {"q": [0, 1]}
    assert first["nodes"][-1]["one_plus_z"] == {"q": [1, 1]}
    assert first["nodes"][-1]["comoving_distance_to_present"] == {
        "q": [0, 1]
    }


def test_phase_only_trajectory_shape_does_not_change_with_tau():
    receipts = [
        _r(
            0,
            lam=Fraction(1, 9),
            theta=Fraction(2, 3),
            background=0,
            sha=SHA_A,
        ),
        _r(
            1,
            lam=Fraction(2, 9),
            theta=Fraction(5, 7),
            background=0,
            sha=SHA_B,
        ),
    ]
    a = build_exact_trajectory(
        receipts, tau=Fraction(1), c0=1
    )
    b = build_exact_trajectory(
        receipts, tau=Fraction(11, 5), c0=1
    )
    logs_a = [
        node["normalized_log_scale"] for node in a["nodes"]
    ]
    logs_b = [
        node["normalized_log_scale"] for node in b["nodes"]
    ]
    z_a = [node["one_plus_z"] for node in a["nodes"]]
    z_b = [node["one_plus_z"] for node in b["nodes"]]
    assert logs_a == logs_b
    assert z_a == z_b
    assert (
        a["nodes"][1]["physical_time"]
        != b["nodes"][1]["physical_time"]
    )


def test_background_sector_can_retain_symbolic_positive_root():
    receipts = [
        _r(0, lam=1, theta=1, background=1, sha=SHA_A),
        _r(
            1,
            lam=1,
            theta=1,
            background=Fraction(2),
            sha=SHA_B,
        ),
    ]
    result = build_exact_trajectory(receipts, tau=1, c0=1)
    assert result["nodes"][0]["total_h2"] == "2/1"
    assert result["nodes"][0]["hubble"]["op"] == "sqrt"


def test_negative_total_h2_fails_closed():
    receipt = _r(0, lam=1, theta=1, background=-2)
    with pytest.raises(Pass220I023TransferError):
        total_h2(receipt, 1)


def test_receipts_must_be_contiguous_and_canonical():
    bad = [
        _r(0, sha=SHA_A),
        _r(2, sha=SHA_B),
    ]
    with pytest.raises(Pass220I023TransferError):
        build_exact_trajectory(bad, tau=1, c0=1)


def test_contract_is_projection_only_no_inverse_or_float_authority():
    descriptor = transfer_contract_descriptor()
    assert descriptor["interpolation"] == "ZERO_ORDER_HOLD"
    assert descriptor["symbolic_exp_required"] is True
    assert descriptor["symbolic_sqrt_required"] is True
    assert descriptor["trapezoid_is_canonical"] is False
    assert descriptor["host_wall_clock_authority"] is False
    assert descriptor["floating_point_authority"] is False
    assert descriptor["projection_only"] is True
    assert descriptor["canonical_admission_authority"] is False
    assert descriptor["inverse_hz_state_authority"] is False

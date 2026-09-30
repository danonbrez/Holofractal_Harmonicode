from __future__ import annotations

import pytest

from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import (
    HNAN_EPSILON,
    HNAN_GATE_10,
    HNAN_LO_SHU_TENSOR,
    HNAN_NUMERATOR,
    HNAN_TERMINAL_XY_EPSILON,
    PHASE_RING,
    QGU_CQ2,
    QGU_DQ4,
    QGU_DELTA,
    QGU_DELTA_SOURCE,
    QGU_HNAN_GATE_10,
    QGU_HNAN_TERMINAL,
    QGU_HNAN_TERMINAL_SOURCE,
    QGU_TRANSPORTED_LO_SHU_TENSOR,
    QGU_TRANSPORT_KERNEL,
    QGU_TRANSPORT_KERNEL_SOURCE,
    WZ,
    XY,
    YX,
    ZW,
    HNANGateError,
    hnan_loshu_resolution_receipt,
    invariant_receipt,
    qgu_hnan_transport_receipt,
    qgu_inverse_transport_phase,
    qgu_phase_delta,
    qgu_transport_phase,
)


def test_qgu_kernel_and_additive_delta_are_exact_distinct_views():
    assert PHASE_RING == 72
    assert QGU_CQ2 == ("Product", "c", ("Power", "q", 2))
    assert QGU_DQ4 == ("Product", "d", ("Power", "q", 4))
    assert QGU_DELTA == ("Mod", ("Sum", QGU_CQ2, QGU_DQ4), 72)
    assert QGU_TRANSPORT_KERNEL == (
        "Quotient",
        ("Sum", XY, QGU_CQ2, QGU_DQ4),
        ("Sum", XY, QGU_CQ2),
    )
    assert QGU_TRANSPORT_KERNEL_SOURCE == (
        "R_K^QGU(q)=(xy+cq^2+dq^4)/(xy+cq^2)"
    )
    assert QGU_DELTA_SOURCE == "delta=(c*q^2+d*q^4) mod 72"


def test_qgu_transport_wraps_complete_ordered_xyzw_tensor_without_rewrite():
    expected = tuple(
        tuple(("PhaseTransportMod72", cell, QGU_DELTA) for cell in row)
        for row in HNAN_LO_SHU_TENSOR
    )
    assert QGU_TRANSPORTED_LO_SHU_TENSOR == expected
    assert QGU_TRANSPORTED_LO_SHU_TENSOR[1][1] == (
        "PhaseTransportMod72",
        HNAN_NUMERATOR,
        QGU_DELTA,
    )
    assert QGU_TRANSPORTED_LO_SHU_TENSOR[0][0][1] == XY
    assert QGU_TRANSPORTED_LO_SHU_TENSOR[0][2][1] == YX
    assert QGU_TRANSPORTED_LO_SHU_TENSOR[2][0][1] == WZ
    assert QGU_TRANSPORTED_LO_SHU_TENSOR[2][2][1] == ZW
    assert XY != YX
    assert ZW != WZ


def test_qgu_hnan_transport_preserves_emptyset_and_epsilon_boundary():
    assert QGU_HNAN_GATE_10 == (
        "PhaseTransportMod72",
        HNAN_GATE_10,
        QGU_DELTA,
    )
    assert QGU_HNAN_GATE_10[1][-1] == "EmptySet"
    assert QGU_HNAN_TERMINAL == (
        "PhaseTransportMod72",
        HNAN_TERMINAL_XY_EPSILON,
        QGU_DELTA,
    )
    assert QGU_HNAN_TERMINAL[1] == ("Sum", XY, HNAN_EPSILON)
    assert QGU_HNAN_TERMINAL[1] != XY
    assert QGU_HNAN_TERMINAL_SOURCE == (
        "PhaseTransportMod72(xy+epsilon,(c*q^2+d*q^4) mod 72)"
    )


@pytest.mark.parametrize(
    ("q", "c", "d"),
    [
        (0, 0, 0),
        (1, 1, 1),
        (5, 3, 7),
        (71, 17, 29),
        (-5, 3, 7),
    ],
)
def test_qgu_phase_delta_is_exact_mod72_and_q_periodic(q: int, c: int, d: int):
    expected = (c * q**2 + d * q**4) % 72
    assert qgu_phase_delta(q, c, d) == expected
    assert qgu_phase_delta(q + 72, c, d) == expected
    assert 0 <= expected < 72


@pytest.mark.parametrize("phase", [0, 1, 35, 71, 72, 145, -1])
def test_qgu_additive_phase_transport_is_reversible(phase: int):
    moved = qgu_transport_phase(phase, 5, 3, 7)
    restored = qgu_inverse_transport_phase(moved, 5, 3, 7)
    assert restored == phase % 72


@pytest.mark.parametrize(
    "args",
    [
        (True, 1, 1),
        (1.0, 1, 1),
        (1, False, 1),
        (1, 1, "1"),
    ],
)
def test_qgu_delta_rejects_non_exact_integer_inputs(args):
    with pytest.raises(HNANGateError):
        qgu_phase_delta(*args)


def test_qgu_hnan_receipts_are_fail_closed_and_aggregated():
    qgu = qgu_hnan_transport_receipt()
    loshu = hnan_loshu_resolution_receipt()
    total = invariant_receipt()

    assert qgu["status"] == "PASS"
    assert all(qgu["checks"].values())
    assert qgu["ratio_kernel_scalar_cancellation_authorized"] is False
    assert qgu["ordered_product_commutation_authorized"] is False
    assert qgu["epsilon_elision_authorized"] is False
    assert qgu["host_float_authority"] is False

    assert loshu["status"] == "PASS"
    assert loshu["checks"]["qgu_transport_pass"] is True
    assert loshu["qgu_transport_required"] is True

    assert total["status"] == "PASS"
    assert total["checks"]["hnan_qgu_transport_pass"] is True
    assert total["hnan_qgu_transport"]["status"] == "PASS"

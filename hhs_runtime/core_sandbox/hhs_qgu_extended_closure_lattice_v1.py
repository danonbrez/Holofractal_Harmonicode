from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict


EXTENDED_QGU_LATTICE = "QGU_EXTENDED_METRIC_PHASE_TORSION_LOSHU_LATTICE"


def F(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        raise ValueError("bool is not an admissible lattice scalar")
    if isinstance(value, dict) and "num" in value and "den" in value:
        return Fraction(value["num"], value["den"])
    return Fraction(value)


def frac(value: Fraction) -> Dict[str, int]:
    return {"num": value.numerator, "den": value.denominator}


def evaluate_extended_qgu_lattice(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extended QGU closure lattice.

    K_ext = (S^3 - 2)
            (xy_phase - b^-2)
            (xy_phase + c*S^2)
            (u^12 - 2)

    with independent torsion side condition:
        xy_torsion = 1
        yx_torsion = -1

    Scalar projection is secondary. The phase carrier and torsion carrier are
    not collapsed into one raw equality.
    """
    S = F(payload["S"])
    b2 = F(payload["b2"])
    xy_phase = F(payload["xy_phase"])
    c = F(payload["c"])
    u = F(payload["u"])
    xy_torsion = F(payload.get("xy_torsion", 1))
    yx_torsion = F(payload.get("yx_torsion", -1))

    if b2 == 0:
        raise ZeroDivisionError("b2 cannot be zero in xy_phase=b^-2 branch")

    metric_anchor = S**3 - 2
    phase_transport = xy_phase - Fraction(1, b2)
    balanced_closure = xy_phase + c * (S**2)
    loshu_return = u**12 - 2
    torsion_xy = xy_torsion - 1
    torsion_yx = yx_torsion + 1

    coupled_kernel = metric_anchor * phase_transport * balanced_closure * loshu_return
    fully_coupled = all(v == 0 for v in (metric_anchor, phase_transport, balanced_closure, loshu_return, torsion_xy, torsion_yx))

    witness = {
        "constraint": EXTENDED_QGU_LATTICE,
        "metric_anchor_S3_minus_2": frac(metric_anchor),
        "phase_transport_xy_phase_minus_b_inv2": frac(phase_transport),
        "balanced_closure_xy_phase_plus_cS2": frac(balanced_closure),
        "loshu_return_u12_minus_2": frac(loshu_return),
        "torsion_xy_minus_1": frac(torsion_xy),
        "torsion_yx_plus_1": frac(torsion_yx),
        "coupled_kernel_product": frac(coupled_kernel),
        "branch_semantics": {
            "xy_phase": "Genesis phase-transport carrier; xy_phase=b^-2",
            "xy_torsion": "oriented torsion carrier; xy_torsion=1",
            "yx_torsion": "oriented torsion reversal; yx_torsion=-1",
            "rule": "do not collapse xy_phase and xy_torsion without an explicit projection gate",
        },
    }
    return {
        "ok": fully_coupled,
        "locked": fully_coupled,
        "status": "LOCKED" if fully_coupled else "QUARANTINED",
        "projection_status": "FULL_EXTENDED_LATTICE_CLOSURE" if fully_coupled else "EXTENDED_LATTICE_RESIDUAL",
        "audit_value": Fraction(0) if fully_coupled else coupled_kernel,
        "witness": witness,
    }


def genesis_branch_payload() -> Dict[str, Any]:
    # Exact rational witness for branch carriers. S and u are algebraic roots in
    # the formal kernel; callers may pass root-symbol witnesses at higher layers.
    return {
        "S": 1,
        "b2": 2,
        "xy_phase": Fraction(1, 2),
        "c": Fraction(-1, 2),
        "u": 1,
        "xy_torsion": 1,
        "yx_torsion": -1,
    }

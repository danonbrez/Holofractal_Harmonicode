from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict

from hhs_runtime.core_sandbox.hhs_qgu_metric_harmonic_operator_v1 import qgu_metric_harmonic_operator


QGU_POLYNOMIAL_CONSTRAINT = "QGU_POLYNOMIAL_METRIC_HARMONIC_CONSTRAINT"


def _f(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, dict) and "num" in value and "den" in value:
        return Fraction(value["num"], value["den"])
    return Fraction(value)


def qgu_polynomial_constraint(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Polynomial binding for QGU.

    Converts the quotient equation into polynomial witnesses:
      B = xy + c*S^2
      left = t(t^2-1)((1-m^(yx-1))/(m-1))
      regular: left*R_K*B - (B + d*S^4) = 0
      closure: B = 0 is accepted as balanced zero closure.
    """
    qgu = qgu_metric_harmonic_operator(payload)
    if qgu.get("status") != "LOCKED":
        return {"ok": False, "locked": False, "status": "QUARANTINED", "reason": "qgu did not lock", "audit_value": Fraction(0), "qgu": qgu}

    w = qgu["witness"]
    S = _f(w["ds2"])
    B = _f(w["balance"])
    left = _f(w["left_generator"])
    projection = qgu.get("projection_status")

    if projection == "BALANCED_ZERO_CLOSURE":
        return {
            "ok": True,
            "locked": True,
            "status": "LOCKED",
            "constraint": QGU_POLYNOMIAL_CONSTRAINT,
            "projection_status": projection,
            "balance_polynomial": {"num": B.numerator, "den": B.denominator},
            "residual_polynomial": None,
            "audit_value": Fraction(0),
            "qgu": qgu,
        }

    d = _f(payload["d"])
    S2 = S * S
    S4 = S2 * S2
    R = _f(w["solved_R_K_QGU"])
    residual = left * R * B - (B + d * S4)
    locked = residual == 0
    return {
        "ok": locked,
        "locked": locked,
        "status": "LOCKED" if locked else "QUARANTINED",
        "constraint": QGU_POLYNOMIAL_CONSTRAINT,
        "projection_status": projection,
        "balance_polynomial": {"num": B.numerator, "den": B.denominator},
        "residual_polynomial": {"num": residual.numerator, "den": residual.denominator},
        "audit_value": residual,
        "qgu": qgu,
    }

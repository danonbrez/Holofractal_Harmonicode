from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import canonicalize_for_hash72, security_hash72_v44


FINAL_KERNEL_NAME = "HHS_QGU_FINAL_UNIFIED_KERNEL"


def F(v: Any) -> Fraction:
    if isinstance(v, Fraction):
        return v
    if isinstance(v, dict) and "num" in v and "den" in v:
        return Fraction(v["num"], v["den"])
    return Fraction(v)


def qgu_final_kernel(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Final unified kernel enforcing:
      (ds^2)^3 = 2
      xy_phase = b^-2
      xy_phase + c(ds^2)^2 = 0
      u^12 = 2
      xy = u^0, yx = u^36 (noncommutative)
    """

    S = F(payload["S"])
    b2 = F(payload["b2"])
    xy_phase = F(payload["xy_phase"])
    c = F(payload["c"])
    u = F(payload["u"])
    xy = F(payload.get("xy", 1))
    yx = F(payload.get("yx", -1))

    # Metric constraint
    k_metric = S**3 - 2

    # Phase transport
    k_phase = xy_phase - Fraction(1, b2)

    # Closure
    k_closure = xy_phase + c * (S**2)

    # Lo Shu / u^12
    k_loshu = u**12 - 2

    # Octonion torsion (noncommutative constraint encoded as sign/orientation)
    k_xy = xy - 1
    k_yx = yx + 1

    locked = all(v == 0 for v in (k_metric, k_phase, k_closure, k_loshu, k_xy, k_yx))

    witness = {
        "kernel": FINAL_KERNEL_NAME,
        "metric": str(k_metric),
        "phase": str(k_phase),
        "closure": str(k_closure),
        "loshu": str(k_loshu),
        "xy": str(k_xy),
        "yx": str(k_yx),
    }

    return {
        "ok": locked,
        "locked": locked,
        "status": "LOCKED" if locked else "QUARANTINED",
        "audit_value": 0 if locked else 1,
        "witness": canonicalize_for_hash72(witness),
        "hash72": security_hash72_v44(witness, domain="HHS_QGU_FINAL_KERNEL"),
    }

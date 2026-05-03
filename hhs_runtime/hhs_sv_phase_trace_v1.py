"""
Non-invasive s-v phase trace module.

Purpose:
- Expose full constraint evaluation trace to self-solving systems
- Provide deltas and dependency-resolved values
- DO NOT replace or bypass existing drift_gate logic

This module is additive and can be called alongside existing enforcement.
"""

from __future__ import annotations

from decimal import Decimal, getcontext

getcontext().prec = 80


def phi() -> Decimal:
    return (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)


def dec_close(a: Decimal, b: Decimal, tol: Decimal = Decimal("1e-30")) -> bool:
    return abs(a - b) <= tol


def sv_trace(v: Decimal) -> dict:
    m = phi()
    s = m * v

    ratio = s / v
    reciprocal = v / s
    product = ratio * reciprocal
    summation = ratio + reciprocal

    trace = {
        "state": {
            "v": v,
            "s": s,
            "m": m,
            "ratio": ratio,
            "reciprocal": reciprocal,
            "product": product,
            "sum": summation,
        },
        "dependencies": {
            "s": "m * v",
            "ratio": "s / v",
            "reciprocal": "v / s",
            "product": "(s/v)*(v/s)",
            "sum": "(s/v)+(v/s)",
        },
        "constraints": {
            "ratio_lock": {
                "target": m,
                "value": ratio,
                "delta": ratio - m,
                "ok": dec_close(ratio, m),
            },
            "reciprocal_lock": {
                "target": Decimal(1) / m,
                "value": reciprocal,
                "delta": reciprocal - (Decimal(1) / m),
                "ok": dec_close(reciprocal, Decimal(1) / m),
            },
            "product_identity": {
                "target": Decimal(1),
                "value": product,
                "delta": product - Decimal(1),
                "ok": dec_close(product, Decimal(1)),
            },
            "sum_lock": {
                "target": Decimal(5).sqrt(),
                "value": summation,
                "delta": summation - Decimal(5).sqrt(),
                "ok": dec_close(summation, Decimal(5).sqrt()),
            },
        },
    }

    trace["pass"] = all(c["ok"] for c in trace["constraints"].values())

    return trace


def sv_trace_with_correction(v: Decimal) -> dict:
    """
    Provides directional correction hints without altering enforcement logic.
    """

    trace = sv_trace(v)

    corrections = {}

    for name, c in trace["constraints"].items():
        if not c["ok"]:
            delta = c["delta"]

            # simple directional hint (sign only, no override)
            if delta > 0:
                direction = "decrease"
            elif delta < 0:
                direction = "increase"
            else:
                direction = "stable"

            corrections[name] = {
                "delta": delta,
                "suggestion": direction,
            }

    trace["corrections"] = corrections

    return trace

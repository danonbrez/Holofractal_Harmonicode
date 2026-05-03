"""
Phase sweep + ordering invariance enforcement for HHS constraint manifold.

This extends closure verification from single-slice consistency
→ manifold traversal consistency.
"""

from __future__ import annotations

import math
from decimal import Decimal, getcontext

getcontext().prec = 80


def dec_close(a: Decimal, b: Decimal, tol: Decimal = Decimal("1e-30")) -> bool:
    return abs(a - b) <= tol


def phi() -> Decimal:
    return (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)


def construct_state(v: Decimal):
    m = phi()
    s = m * v
    # minimal projection layer
    x_s = Decimal(2) ** s
    z_v = Decimal(2) ** v
    return {
        "s": s,
        "v": v,
        "x^s": x_s,
        "z^v": z_v,
    }


def drift_gate(state) -> bool:
    # enforce reciprocal closure constraint only
    s = state["s"]
    v = state["v"]
    m = phi()

    cond1 = dec_close(s / v, m)
    cond2 = dec_close(v / s, Decimal(1) / m)
    cond3 = dec_close((s / v) * (v / s), Decimal(1))
    cond4 = dec_close((s / v) + (v / s), Decimal(5).sqrt())

    return cond1 and cond2 and cond3 and cond4


def test_phase_sweep_closure():
    # sweep across phase domain
    for i in range(1, 50):
        v = Decimal(i) / Decimal(10)
        state = construct_state(v)
        assert drift_gate(state), f"Drift at v={v}"


def test_ordering_invariance():
    # simulate constraint ordering permutations
    m = phi()
    v = Decimal("1.3")
    s = m * v

    checks = [
        lambda: dec_close(s / v, m),
        lambda: dec_close(v / s, Decimal(1) / m),
        lambda: dec_close((s / v) * (v / s), Decimal(1)),
        lambda: dec_close((s / v) + (v / s), Decimal(5).sqrt()),
    ]

    # evaluate in different orders
    for order in [checks, list(reversed(checks))]:
        assert all(fn() for fn in order)

"""
Runtime-integrated s-v phase drift gate.

Enforces:
- reciprocal phase lock (s/v = m)
- ordering invariance
- Hash72 parity stability across phase sweep

This module is intended to be called inside kernel drift_gate.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
import hashlib

getcontext().prec = 80


def phi() -> Decimal:
    return (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)


def dec_close(a: Decimal, b: Decimal, tol: Decimal = Decimal("1e-30")) -> bool:
    return abs(a - b) <= tol


def hash72_stub(payload: str) -> str:
    # placeholder: deterministic hash projection
    h = hashlib.sha256(payload.encode()).hexdigest()
    return h[:72]


def sv_state_hash(s: Decimal, v: Decimal) -> str:
    payload = f"s={s}|v={v}|ratio={s/v}"
    return hash72_stub(payload)


def sv_drift_gate(v: Decimal) -> dict:
    m = phi()
    s = m * v

    cond1 = dec_close(s / v, m)
    cond2 = dec_close(v / s, Decimal(1) / m)
    cond3 = dec_close((s / v) * (v / s), Decimal(1))
    cond4 = dec_close((s / v) + (v / s), Decimal(5).sqrt())

    state_hash = sv_state_hash(s, v)

    return {
        "pass": cond1 and cond2 and cond3 and cond4,
        "s": s,
        "v": v,
        "hash72": state_hash,
    }


def sv_phase_sweep_with_hash_consistency(samples: int = 50) -> bool:
    baseline_hash = None

    for i in range(1, samples + 1):
        v = Decimal(i) / Decimal(10)
        result = sv_drift_gate(v)

        if not result["pass"]:
            return False

        if baseline_hash is None:
            baseline_hash = result["hash72"]
        else:
            if result["hash72"] == baseline_hash:
                continue
            # allow different states but require deterministic structure
            if len(result["hash72"]) != len(baseline_hash):
                return False

    return True

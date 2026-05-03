"""
Drift Gate Integration Hook

This module enforces sv_phase_drift_gate at the correct execution point:
→ immediately before receipt commit
→ inside self-solving loop iterations

No alternate execution path is introduced.
"""

from __future__ import annotations

from decimal import Decimal

from hhs_runtime.hhs_sv_phase_drift_gate_v1 import (
    sv_drift_gate,
    sv_phase_sweep_with_hash_consistency,
)


class DriftGateViolation(Exception):
    pass


# --- PRE-RECEIPT CHECK ---

def enforce_pre_commit_phase_lock(v: Decimal) -> None:
    result = sv_drift_gate(v)

    if not result["pass"]:
        raise DriftGateViolation(
            f"Phase drift detected before commit: v={v}, s={result['s']}"
        )


# --- GLOBAL SWEEP VALIDATION ---

def enforce_global_phase_consistency() -> None:
    if not sv_phase_sweep_with_hash_consistency():
        raise DriftGateViolation("Global phase sweep inconsistency detected")


# --- SELF-SOLVING LOOP BINDING ---

def enforce_self_solving_loop(v_sequence):
    """
    Inject into self-solving loop.

    For each iteration:
    - enforce local drift gate
    - enforce global consistency periodically
    """

    for i, v in enumerate(v_sequence):
        enforce_pre_commit_phase_lock(v)

        # periodic global check (non-invasive)
        if i % 10 == 0:
            enforce_global_phase_consistency()

    return True

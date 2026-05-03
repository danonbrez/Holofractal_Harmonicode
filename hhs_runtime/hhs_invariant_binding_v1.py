"""
Invariant Projection Binding Layer (HHS)

Purpose:
- Map all local function execution into the Global Invariant Frame (GIF)
- Ensure no operation is isolated from global constraint structure
- Provide projection + dependency context without altering existing logic

Design constraints:
- Non-invasive (opt-in decorator)
- No modification of drift_gate or solver behavior
- No alternate execution path introduced
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from typing import Callable, Any, Dict

getcontext().prec = 80


# --- GLOBAL INVARIANT FRAME ---

class InvariantFrame:
    """
    Projects local state into invariant coordinate system.
    """

    def __init__(self, state: Dict[str, Decimal]):
        self.state = state

    def project(self) -> Dict[str, Decimal]:
        s = self.state.get("s")
        v = self.state.get("v")
        m = self.state.get("m")

        if s is None or v is None or m is None:
            raise ValueError("InvariantFrame requires s, v, m in state")

        ratio = s / v
        reciprocal = v / s

        return {
            "ratio": ratio,
            "reciprocal": reciprocal,
            "product": ratio * reciprocal,
            "sum": ratio + reciprocal,
        }

    def dependencies(self) -> Dict[str, str]:
        return {
            "s": "m * v",
            "ratio": "s / v",
            "reciprocal": "v / s",
            "product": "(s/v)*(v/s)",
            "sum": "(s/v)+(v/s)",
        }


# --- DECORATOR (OPT-IN) ---

def bind_to_invariants(func: Callable) -> Callable:
    """
    Decorator to bind a function to invariant projection.

    Function signature becomes:
        func(state, projection, *args, **kwargs)

    Original logic is not modified—projection is provided as additional context.
    """

    def wrapped(state: Dict[str, Decimal], *args: Any, **kwargs: Any) -> Dict[str, Any]:
        frame = InvariantFrame(state)
        projection = frame.project()

        result = func(state, projection, *args, **kwargs)

        return {
            "result": result,
            "projection": projection,
            "dependencies": frame.dependencies(),
        }

    return wrapped


# --- SAFE HELPER (NO DECORATOR REQUIRED) ---

def apply_invariant_projection(state: Dict[str, Decimal]) -> Dict[str, Any]:
    """
    Utility for manual projection without wrapping a function.
    """

    frame = InvariantFrame(state)

    return {
        "projection": frame.project(),
        "dependencies": frame.dependencies(),
    }


# --- OPTIONAL VALIDATION HOOK (NON-ENFORCING) ---

def validate_projection_consistency(state: Dict[str, Decimal]) -> bool:
    """
    Lightweight invariant consistency check.
    Does NOT replace drift_gate.
    """

    frame = InvariantFrame(state)
    p = frame.project()

    # minimal invariant checks
    cond1 = abs(p["product"] - Decimal(1)) < Decimal("1e-30")
    cond2 = abs(p["sum"] - Decimal(5).sqrt()) < Decimal("1e-30")

    return cond1 and cond2

"""
Invariant → Receipt Bridge

Attaches invariant projection and trace data to receipt structures
without modifying existing receipt generation logic.

This ensures every committed state is reconstructable from:
- invariant projection
- constraint trace

Non-invasive: must be called explicitly before commit.
"""

from __future__ import annotations

from typing import Dict, Any
from decimal import Decimal

from hhs_runtime.hhs_sv_phase_trace_v1 import sv_trace
from hhs_runtime.hhs_invariant_binding_v1 import apply_invariant_projection


def attach_invariant_metadata(state: Dict[str, Decimal], receipt: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns receipt augmented with invariant + trace data.
    Does NOT alter original receipt structure—adds a namespaced block.
    """

    trace = sv_trace(state["v"])
    projection = apply_invariant_projection(state)

    receipt["hhs_invariant_context"] = {
        "trace": trace,
        "projection": projection["projection"],
        "dependencies": projection["dependencies"],
    }

    return receipt


# --- OPTIONAL HELPER FOR PIPELINE ---

def pre_commit_with_invariants(state: Dict[str, Decimal], receipt_builder):
    """
    Wraps existing receipt builder without replacing it.

    Usage:
        receipt = pre_commit_with_invariants(state, build_receipt)
    """

    receipt = receipt_builder(state)
    return attach_invariant_metadata(state, receipt)

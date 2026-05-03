"""
Constraint Branch Router (HHS)

Routes non-closed constraint states into verbatim blockchain branches
instead of halting execution.

This preserves all divergence as structured data.
"""

from __future__ import annotations

from typing import Dict, Any, Callable

from hhs_runtime.hhs_recursive_global_constraint_bundle_v1 import (
    build_recursive_global_constraint_report,
)
from hhs_runtime.hhs_invariant_receipt_bridge_v1 import (
    pre_commit_with_invariants,
)


# --- VERBATIM ENCODER (minimal, non-lossy placeholder) ---

def encode_verbatim_block(state: Dict[str, Any], report: Dict[str, Any]) -> str:
    """
    Produces a deterministic markdown representation of divergence.
    This is a reversible structural encoding (no summarization).
    """

    lines = []

    lines.append("# HHS Verbatim Branch Block")
    lines.append("")

    lines.append("## State")
    for k, v in state.items():
        lines.append(f"- {k} = {v}")

    lines.append("")
    lines.append("## Constraints")

    for c in report.get("constraints", []):
        if not c.get("ok", False):
            lines.append(f"- {c['name']}: {c['lhs']} {c['relation']} {c['rhs']} (FAIL)")
        else:
            lines.append(f"- {c['name']}: {c['lhs']} {c['relation']} {c['rhs']} (PASS)")

    lines.append("")
    lines.append("## Global Invariants")
    for k, v in report.get("global_invariants", {}).items():
        lines.append(f"- {k}: {v}")

    return "\n".join(lines)


# --- BRANCH COMMIT ---

def commit_verbatim_branch(
    state: Dict[str, Any],
    report: Dict[str, Any],
    receipt_builder: Callable[[Dict[str, Any]], Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Creates a branch receipt preserving divergence.
    Does not modify canonical Hash72 identity.
    """

    receipt = receipt_builder(state)

    receipt.setdefault("verbatim_branches", [])

    branch_block = encode_verbatim_block(state, report)

    receipt["verbatim_branches"].append(
        {
            "type": "constraint_divergence",
            "trace": report,
            "verbatim_block": branch_block,
        }
    )

    return receipt


# --- ROUTER ---

def route_constraint_outcome(
    state: Dict[str, Any],
    receipt_builder: Callable[[Dict[str, Any]], Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Main routing function.

    - Closed state → canonical commit path
    - Non-closed state → verbatim branch commit
    """

    report = build_recursive_global_constraint_report()

    if report["pass"]:
        return pre_commit_with_invariants(state, receipt_builder)

    return commit_verbatim_branch(state, report, receipt_builder)

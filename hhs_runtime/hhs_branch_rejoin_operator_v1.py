from decimal import Decimal

from hhs_runtime.hhs_sv_phase_trace_v1 import sv_trace_with_correction
from hhs_runtime.hhs_recursive_global_constraint_bundle_v1 import build_recursive_global_constraint_report
from hhs_runtime.hhs_invariant_receipt_bridge_v1 import pre_commit_with_invariants
from hhs_runtime.hhs_adaptive_correction_memory_v1 import (
    record_iteration,
)


def apply_phase_vector_correction(state, corrections):
    v = Decimal(state.get("v", 1))

    # golden ratio coupling (s = m*v)
    m = Decimal("1.6180339887498948482")
    s = m * v

    for name, c in corrections.items():
        direction = c.get("suggestion")

        if direction == "increase":
            v += Decimal("0.01")
            s = m * v
        elif direction == "decrease":
            v -= Decimal("0.01")
            s = m * v

    state["v"] = v
    state["s"] = s
    return state


def attempt_branch_rejoin(state, receipt_builder, max_iterations=10):
    current = dict(state)

    for _ in range(max_iterations):
        trace = sv_trace_with_correction(Decimal(current.get("v", 1)))

        if trace["pass"]:
            report = build_recursive_global_constraint_report()

            if report["pass"]:
                record_iteration(trace, success=True)
                return pre_commit_with_invariants(current, receipt_builder)

        current = apply_phase_vector_correction(current, trace.get("corrections", {}))
        record_iteration(trace, success=False)

    receipt = receipt_builder(current)
    receipt["rejoin_attempt"] = {
        "status": "failed",
        "state": current,
        "trace": trace
    }

    return receipt


def rejoin_from_branch(branch_state, receipt_builder):
    return attempt_branch_rejoin(branch_state, receipt_builder)

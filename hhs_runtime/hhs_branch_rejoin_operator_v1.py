from decimal import Decimal

from hhs_runtime.hhs_sv_phase_trace_v1 import sv_trace_with_correction
from hhs_runtime.hhs_recursive_global_constraint_bundle_v1 import build_recursive_global_constraint_report
from hhs_runtime.hhs_invariant_receipt_bridge_v1 import pre_commit_with_invariants
from hhs_runtime.hhs_adaptive_correction_memory_v1 import (
    apply_adaptive_correction,
    record_iteration,
)


def attempt_branch_rejoin(state, receipt_builder, max_iterations=10):
    current = dict(state)

    for _ in range(max_iterations):
        trace = sv_trace_with_correction(Decimal(current.get("v", 1)))

        # phase closure reached
        if trace["pass"]:
            report = build_recursive_global_constraint_report()

            # full system closure reached
            if report["pass"]:
                record_iteration(trace, success=True)
                return pre_commit_with_invariants(current, receipt_builder)

        # otherwise adjust toward closure using adaptive memory
        current = apply_adaptive_correction(current, trace.get("corrections", {}))
        record_iteration(trace, success=False)

    # failed to rejoin → remain in branch
    receipt = receipt_builder(current)
    receipt["rejoin_attempt"] = {
        "status": "failed",
        "state": current,
        "trace": trace
    }

    return receipt


def rejoin_from_branch(branch_state, receipt_builder):
    return attempt_branch_rejoin(branch_state, receipt_builder)

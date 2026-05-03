from decimal import Decimal

from hhs_runtime.hhs_sv_phase_trace_v1 import sv_trace_with_correction
from hhs_runtime.hhs_recursive_global_constraint_bundle_v1 import build_recursive_global_constraint_report
from hhs_runtime.hhs_invariant_receipt_bridge_v1 import pre_commit_with_invariants
from hhs_runtime.hhs_adaptive_correction_memory_v1 import (
    record_iteration,
)


def apply_tensor_phase_correction(state, corrections):
    v = Decimal(state.get("v", 1))
    x = Decimal(state.get("x", 1))
    y = Decimal(state.get("y", -1))
    z = Decimal(state.get("z", 1))
    w = Decimal(state.get("w", -1))

    # golden ratio coupling
    m = Decimal("1.6180339887498948482")
    s = m * v

    for name, c in corrections.items():
        direction = c.get("suggestion")

        if direction == "increase":
            v += Decimal("0.01")
            x += Decimal("0.005")
            z += Decimal("0.005")
        elif direction == "decrease":
            v -= Decimal("0.01")
            y -= Decimal("0.005")
            w -= Decimal("0.005")

        # maintain coupling
        s = m * v

    state.update({
        "v": v,
        "s": s,
        "x": x,
        "y": y,
        "z": z,
        "w": w,
    })

    return state


def attempt_branch_rejoin(state, receipt_builder, max_iterations=10):
    current = dict(state)

    for _ in range(max_iterations):
        trace = sv_trace_with_correction(Decimal(current.get("v", 1)))

        if trace["pass"]:
            report = build_recursive_global_constraint_bundle_report = build_recursive_global_constraint_report()

            if report["pass"]:
                record_iteration(trace, success=True)
                return pre_commit_with_invariants(current, receipt_builder)

        current = apply_tensor_phase_correction(current, trace.get("corrections", {}))
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

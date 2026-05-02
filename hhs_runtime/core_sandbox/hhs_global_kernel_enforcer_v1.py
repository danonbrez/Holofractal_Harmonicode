from __future__ import annotations

from typing import Any, Dict

from hhs_runtime.core_sandbox.hhs_qgu_final_unified_kernel_v1 import qgu_final_kernel


GLOBAL_KERNEL_ENFORCER = "HHS_GLOBAL_KERNEL_ENFORCER"


def enforce_global_kernel(operation: Dict[str, Any], kernel_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forces ALL operations through the final unified kernel.

    operation: arbitrary operation request
    kernel_payload: required fields for qgu_final_kernel

    Returns:
        LOCKED → operation allowed
        QUARANTINED → operation blocked
    """

    kernel_result = qgu_final_kernel(kernel_payload)

    if not kernel_result.get("locked"):
        return {
            "ok": False,
            "status": "QUARANTINED",
            "reason": "global_kernel_rejection",
            "kernel": kernel_result,
            "operation": operation,
        }

    return {
        "ok": True,
        "status": "LOCKED",
        "kernel": kernel_result,
        "operation": operation,
    }

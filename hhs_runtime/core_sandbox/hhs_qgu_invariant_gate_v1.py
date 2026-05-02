from __future__ import annotations

from typing import Any, Dict

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import KernelGateAdapter, canonicalize_for_hash72


QGU_OPERATION_NAME = "QGU_METRIC_HARMONIC"
QGU_INVARIANT_NAME = "QGU_METRIC_HARMONIC_CLOSURE"
QGU_VALID_PROJECTIONS = {"BALANCED_ZERO_CLOSURE", "REGULAR_RESPONSE"}


def is_qgu_closure_witness(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    witness = value.get("witness")
    if not isinstance(witness, dict):
        return False
    guards = witness.get("guards", {})
    return (
        value.get("status") == "LOCKED"
        and value.get("projection_status") in QGU_VALID_PROJECTIONS
        and guards.get("exact_fraction_arithmetic") is True
        and guards.get("ordered_yx_preserved") is True
    )


def audit_qgu_closure(value: Any, *, phase: int = 0) -> Dict[str, Any]:
    if not is_qgu_closure_witness(value):
        return {
            "status": "QUARANTINED",
            "locked": False,
            "phase": phase % 72,
            "reason": "qgu_closure_witness_missing_or_invalid",
        }
    witness = value["witness"]
    return {
        "status": "LOCKED",
        "locked": True,
        "phase": phase % 72,
        "reason": "",
        "invariant": QGU_INVARIANT_NAME,
        "projection_status": value.get("projection_status"),
        "balance": witness.get("balance"),
        "ds2": witness.get("ds2"),
    }


class QGUInvariantKernelGateAdapter(KernelGateAdapter):
    def audit_value(self, value: Any, *, phase: int = 0) -> Dict[str, Any]:
        if isinstance(value, dict) and ("projection_status" in value or "witness" in value):
            audit = audit_qgu_closure(value, phase=phase)
            return {
                "status": audit["status"],
                "locked": audit["locked"],
                "witness": canonicalize_for_hash72(audit),
                "vars": canonicalize_for_hash72({
                    "qgu_invariant": QGU_INVARIANT_NAME,
                    "qgu_projection_status": audit.get("projection_status"),
                    "qgu_balance": audit.get("balance"),
                    "qgu_ds2": audit.get("ds2"),
                }) if audit["locked"] else {},
            }
        return super().audit_value(value, phase=phase)

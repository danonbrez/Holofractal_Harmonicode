from __future__ import annotations

from typing import Any, Dict

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import canonicalize_for_hash72
from hhs_runtime.core_sandbox.hhs_octonion_digital_dna_u72_table_v1 import multiply_basis


OCTONION_MODALITY = "OCTONION_DNA_PHASE"


def octonion_kernel_projection(operation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Projects an operation into octonion DNA phase space.

    Expected input:
      {"left": "x", "right": "y"}
    """
    left = operation.get("left")
    right = operation.get("right")

    if left is None or right is None:
        return {
            "status": "QUARANTINED",
            "reason": "missing_octonion_operands",
            "modality": OCTONION_MODALITY,
        }

    witness = multiply_basis(left, right)

    return {
        "status": "LOCKED" if witness["closure"] else "QUARANTINED",
        "modality": OCTONION_MODALITY,
        "phase_index": witness["phase_index"],
        "loshu_cell": witness["loshu_cell"],
        "closure": witness["closure"],
        "witness": canonicalize_for_hash72(witness),
    }


def octonion_kernel_gate(operation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Kernel gate enforcing octonion phase closure as a required modality.
    """
    projection = octonion_kernel_projection(operation)

    if projection.get("status") != "LOCKED":
        return {
            "ok": False,
            "locked": False,
            "status": "QUARANTINED",
            "reason": "octonion_phase_not_closed",
            "octonion": projection,
        }

    return {
        "ok": True,
        "locked": True,
        "status": "LOCKED",
        "octonion": projection,
    }

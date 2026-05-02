from __future__ import annotations

from typing import Any, Dict

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import canonicalize_for_hash72, security_hash72_v44
from hhs_runtime.core_sandbox.hhs_qgu_metric_harmonic_operator_v1 import qgu_metric_harmonic_operator
from hhs_runtime.core_sandbox.hhs_qgu_polynomial_constraint_v1 import qgu_polynomial_constraint
from hhs_runtime.core_sandbox.hhs_qgu_extended_closure_lattice_v1 import evaluate_extended_qgu_lattice
from hhs_runtime.core_sandbox.hhs_multimodal_phase_required_gate_v1 import audit_required_multimodal_phase


REDUNDANT_QGU_MODALITY = "QGU_REDUNDANT_PRIMITIVE_MODALITY"


def qgu_redundant_primitive_modality(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redundant primitive modality witness for QGU closure.

    This is NOT a bypass and NOT a simplification. It recomputes the required
    QGU layers and only locks when every existing layer agrees:
      1. metric-harmonic QGU operator
      2. polynomial QGU constraint
      3. extended metric/phase/torsion/LoShu lattice
      4. mandatory multimodal phase receipt

    The output is an additional modality witness that can be consumed by the
    runtime; it does not authorize execution by itself.
    """
    qgu_payload = payload["qgu"]
    lattice_payload = payload["extended_lattice"]
    multimodal_receipt = payload["multimodal_phase_lock"]

    qgu = qgu_metric_harmonic_operator(qgu_payload)
    poly = qgu_polynomial_constraint(qgu_payload)
    lattice = evaluate_extended_qgu_lattice(lattice_payload)
    multimodal = audit_required_multimodal_phase(multimodal_receipt, phase=0)

    locked = (
        qgu.get("status") == "LOCKED"
        and poly.get("status") == "LOCKED"
        and lattice.get("status") == "LOCKED"
        and multimodal.get("status") == "LOCKED"
    )

    witness_core = {
        "modality": REDUNDANT_QGU_MODALITY,
        "locked": locked,
        "qgu_status": qgu.get("status"),
        "qgu_projection_status": qgu.get("projection_status"),
        "polynomial_status": poly.get("status"),
        "polynomial_projection_status": poly.get("projection_status"),
        "extended_lattice_status": lattice.get("status"),
        "extended_lattice_projection_status": lattice.get("projection_status"),
        "multimodal_status": multimodal.get("status"),
        "required_modalities": multimodal.get("required_modalities"),
        "present_modalities": multimodal.get("present_modalities"),
        "rule": "redundant witness only; does not bypass mandatory gates",
    }
    witness_hash72 = security_hash72_v44(witness_core, domain="HHS_QGU_REDUNDANT_PRIMITIVE_MODALITY")

    return {
        "ok": locked,
        "locked": locked,
        "status": "LOCKED" if locked else "QUARANTINED",
        "modality": REDUNDANT_QGU_MODALITY,
        "audit_value": 0 if locked else 1,
        "witness_hash72": witness_hash72,
        "witness": canonicalize_for_hash72(witness_core),
        "layers": canonicalize_for_hash72({
            "qgu": qgu,
            "polynomial": poly,
            "extended_lattice": lattice,
            "multimodal": multimodal,
        }),
    }

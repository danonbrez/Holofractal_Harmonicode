from __future__ import annotations

from typing import Any, Dict, Mapping

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import canonicalize_for_hash72, security_hash72_v44
from hhs_runtime.core_sandbox.hhs_qgu_redundant_primitive_modality_v1 import qgu_redundant_primitive_modality


QGU_AGREEMENT_AUDIT = "QGU_MODALITY_AGREEMENT_AUDIT"


def _layer_status(layer: Any) -> str:
    if isinstance(layer, Mapping):
        return str(layer.get("status", "UNKNOWN"))
    return "MISSING"


def qgu_agreement_audit(payload: Dict[str, Any]) -> Dict[str, Any]:
    primitive = qgu_redundant_primitive_modality(payload)
    layers = primitive.get("layers", {}) if isinstance(primitive, Mapping) else {}
    if not isinstance(layers, Mapping):
        layers = {}

    summary = {
        "qgu": _layer_status(layers.get("qgu")),
        "polynomial": _layer_status(layers.get("polynomial")),
        "extended_lattice": _layer_status(layers.get("extended_lattice")),
        "multimodal": _layer_status(layers.get("multimodal")),
    }
    differences = [name for name, status in summary.items() if status != "LOCKED"]
    locked = primitive.get("locked") is True and not differences
    trace = {
        "audit": QGU_AGREEMENT_AUDIT,
        "locked": locked,
        "layer_status": summary,
        "differences": differences,
        "rule": "nonmatching modality layers do not propagate",
    }
    return {
        "ok": locked,
        "locked": locked,
        "status": "LOCKED" if locked else "QUARANTINED",
        "quarantine": not locked,
        "reason": "" if locked else "qgu_modality_layers_do_not_agree",
        "audit_value": 0 if locked else 1,
        "trace_hash72": security_hash72_v44(trace, domain="HHS_QGU_AGREEMENT_TRACE"),
        "learning_trace": canonicalize_for_hash72(trace),
        "primitive": canonicalize_for_hash72(primitive),
    }

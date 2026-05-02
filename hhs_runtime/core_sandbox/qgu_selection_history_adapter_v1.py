from __future__ import annotations

from fractions import Fraction
from typing import Any

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import security_hash72_v44


def qgu_learning_weights_to_history(weights: dict[str, str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key in sorted(weights):
        raw = weights[key]
        try:
            value = Fraction(raw)
        except Exception:
            value = Fraction(0)
        if value > 0:
            status = "APPLIED"
        elif value < 0:
            status = "QUARANTINED"
        else:
            status = "VALID"
        out.append({
            "canonical_hash72": security_hash72_v44({"qgu_key": key}, domain="QGU_HISTORY_KEY"),
            "operator_hash72": security_hash72_v44({"qgu_operator": key}, domain="QGU_HISTORY_OPERATOR"),
            "status": status,
            "replay_valid": True,
            "qgu_learning_key": key,
            "qgu_learning_weight": raw,
        })
    return out


def merge_qgu_history(existing: list[dict[str, Any]] | None, weights: dict[str, str]) -> list[dict[str, Any]]:
    merged = list(existing or [])
    merged.extend(qgu_learning_weights_to_history(weights))
    return merged

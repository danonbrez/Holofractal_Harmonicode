from __future__ import annotations

from fractions import Fraction
from typing import Any

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import security_hash72_v44


LO_SHU_RING = (4, 9, 2, 3, 5, 7, 8, 1, 6)
PHASE_RING = 72


def loshu_phase_index(phase: int) -> int:
    return int(phase) % len(LO_SHU_RING)


def u72_phase_weight(phase: int) -> Fraction:
    """Return bounded advisory weight for a u^72 phase position."""
    p = int(phase) % PHASE_RING
    cell = LO_SHU_RING[loshu_phase_index(p)]
    # Center 5 is neutral. Distance from 5 creates bounded advisory curvature.
    return Fraction(cell - 5, 72)


def qgu_phase_history_entry(operator_key: str, phase: int) -> dict[str, Any]:
    weight = u72_phase_weight(phase)
    status = "APPLIED" if weight > 0 else "QUARANTINED" if weight < 0 else "VALID"
    phase_payload = {
        "operator_key": operator_key,
        "phase": int(phase) % PHASE_RING,
        "loshu_cell": LO_SHU_RING[loshu_phase_index(phase)],
        "weight": f"{weight.numerator}/{weight.denominator}",
    }
    return {
        "canonical_hash72": security_hash72_v44(phase_payload, domain="QGU_PHASE_SELECTION_KEY"),
        "operator_hash72": security_hash72_v44({"operator_key": operator_key}, domain="QGU_PHASE_SELECTION_OPERATOR"),
        "status": status,
        "replay_valid": True,
        "qgu_phase_selection": phase_payload,
    }


def qgu_phase_history(operator_keys: list[str], phase: int) -> list[dict[str, Any]]:
    return [qgu_phase_history_entry(key, phase) for key in operator_keys]


def merge_qgu_phase_history(existing: list[dict[str, Any]] | None, operator_keys: list[str], phase: int) -> list[dict[str, Any]]:
    merged = list(existing or [])
    merged.extend(qgu_phase_history(operator_keys, phase))
    return merged

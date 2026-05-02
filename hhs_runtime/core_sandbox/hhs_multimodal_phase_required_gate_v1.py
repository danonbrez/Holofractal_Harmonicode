from __future__ import annotations

from typing import Any, Mapping


REQUIRED_MODALITIES = ("AUDIO", "HARMONICODE", "XYZW", "HASH72")


def _present_modalities(receipt: Mapping[str, Any]) -> set[str]:
    out: set[str] = set()
    for item in receipt.get("witnesses", []):
        if not isinstance(item, Mapping):
            continue
        obs = item.get("observation", {})
        if isinstance(obs, Mapping) and obs.get("modality"):
            out.add(str(obs["modality"]).upper())
        elif item.get("modality"):
            out.add(str(item["modality"]).upper())
    return out


def _invariants_locked(receipt: Mapping[str, Any]) -> bool:
    gate = receipt.get("invariant_gate", {})
    if not isinstance(gate, Mapping):
        return False
    details = gate.get("details", {})
    if isinstance(details, Mapping):
        return all(bool(details.get(k)) for k in ("Δe=0", "Ψ=0", "Θ15=true", "Ω=true"))
    return all(bool(gate.get(k)) for k in ("delta_e_zero", "psi_zero", "theta15_true", "omega_true"))


def audit_required_multimodal_phase(receipt: Any, *, phase: int = 0) -> dict[str, Any]:
    if not isinstance(receipt, Mapping):
        return {"status": "QUARANTINED", "locked": False, "phase": phase % 72, "reason": "missing_multimodal_receipt"}
    present = _present_modalities(receipt)
    missing = [m for m in REQUIRED_MODALITIES if m not in present]
    locked = (
        str(receipt.get("status", "")).upper() == "LOCKED"
        and bool(receipt.get("mandatory_present"))
        and not missing
        and bool(receipt.get("temporal_ok"))
        and bool(receipt.get("phase_locked"))
        and _invariants_locked(receipt)
    )
    return {
        "status": "LOCKED" if locked else "QUARANTINED",
        "locked": locked,
        "phase": phase % 72,
        "required_modalities": list(REQUIRED_MODALITIES),
        "present_modalities": sorted(present),
        "missing_modalities": missing,
        "reason": "" if locked else "required_multimodal_phase_lock_failed",
    }

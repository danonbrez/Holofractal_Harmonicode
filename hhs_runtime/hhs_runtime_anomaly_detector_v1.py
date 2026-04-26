"""
HHS Runtime Anomaly Detector v1
===============================

Read-only anomaly classification for runtime snapshots.

Adds targeted anomaly metadata and predictive drift detection:
- affected modalities
- affected phase indices
- drift risk score
- predicted failure horizon class

This module never mutates state. It emits alert records for GUI visualization
and stream batching.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class RuntimeAlert:
    code: str
    severity: AlertSeverity
    message: str
    subject_hash72: str | None
    alert_hash72: str
    affected_modalities: List[str]
    affected_phase_indices: List[int]
    drift_risk: int
    predicted_horizon: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


def _alert(
    code: str,
    severity: AlertSeverity,
    message: str,
    subject: Any = None,
    *,
    affected_modalities: List[str] | None = None,
    affected_phase_indices: List[int] | None = None,
    drift_risk: int = 0,
    predicted_horizon: str = "NONE",
) -> RuntimeAlert:
    subject_hash = hash72_digest(("runtime_alert_subject_v1", subject), width=18) if subject is not None else None
    alert_hash = hash72_digest(("runtime_alert_v1", code, severity.value, message, subject_hash, affected_modalities or [], affected_phase_indices or [], drift_risk, predicted_horizon), width=24)
    return RuntimeAlert(code, severity, message, subject_hash, alert_hash, affected_modalities or [], affected_phase_indices or [], drift_risk, predicted_horizon)


def _witnesses(phase: Dict[str, Any]) -> List[Dict[str, Any]]:
    return list(phase.get("witnesses", []) or [])


def _modality_of(w: Dict[str, Any]) -> str:
    obs = w.get("observation", {}) if isinstance(w.get("observation"), dict) else {}
    return str(obs.get("modality") or w.get("modality") or "UNKNOWN")


def _phase_index_of(w: Dict[str, Any]) -> int:
    try:
        return int(w.get("phase_index", 0))
    except Exception:
        return 0


def _phase_distance(a: int, b: int, ring: int = 72) -> int:
    delta = abs((a - b) % ring)
    return min(delta, ring - delta)


def predict_drift(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    phase = snapshot.get("phase", {})
    loop = snapshot.get("operatorLoop", {})
    witnesses = _witnesses(phase)
    anchor = int(phase.get("anchor_phase_index", 0) or 0)
    distances = [_phase_distance(anchor, _phase_index_of(w)) for w in witnesses]
    max_distance = max(distances) if distances else 0
    temporal_bad = sum(1 for w in witnesses if str(w.get("temporal_status")) != "ADMISSIBLE")
    loop_phase_bad = sum(1 for p in loop.get("phase_agent_proposals", []) or [] if not p.get("phase_ok", True))
    missing = len(phase.get("missing_mandatory", []) or [])
    risk = min(100, max_distance * 20 + temporal_bad * 25 + loop_phase_bad * 15 + missing * 35)
    horizon = "IMMEDIATE" if risk >= 75 else "NEAR" if risk >= 45 else "WATCH" if risk >= 20 else "STABLE"
    return {
        "risk": risk,
        "horizon": horizon,
        "max_phase_distance": max_distance,
        "temporal_bad": temporal_bad,
        "loop_phase_bad": loop_phase_bad,
        "missing_mandatory_count": missing,
        "affected_phase_indices": sorted({_phase_index_of(w) for w in witnesses if _phase_distance(anchor, _phase_index_of(w)) > 1}),
        "affected_modalities": sorted({_modality_of(w) for w in witnesses if _phase_distance(anchor, _phase_index_of(w)) > 1 or str(w.get("temporal_status")) != "ADMISSIBLE"}),
    }


def detect_runtime_anomalies(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    phase = snapshot.get("phase", {})
    loop = snapshot.get("operatorLoop", {})
    alerts: List[RuntimeAlert] = []
    witnesses = _witnesses(phase)
    drift = predict_drift(snapshot)

    if phase.get("mandatory_present") is not True:
        missing = [str(x) for x in phase.get("missing_mandatory", [])]
        alerts.append(_alert("MISSING_MANDATORY_WITNESS", AlertSeverity.CRITICAL, f"Missing mandatory witnesses: {missing}", missing, affected_modalities=missing, drift_risk=100, predicted_horizon="IMMEDIATE"))
    if phase.get("phase_locked") is not True:
        affected_indices = drift["affected_phase_indices"] or sorted({_phase_index_of(w) for w in witnesses})
        affected_modalities = drift["affected_modalities"] or sorted({_modality_of(w) for w in witnesses})
        alerts.append(_alert("PHASE_UNLOCKED", AlertSeverity.CRITICAL, "Mandatory witnesses are not phase locked.", phase.get("receipt_hash72"), affected_modalities=affected_modalities, affected_phase_indices=affected_indices, drift_risk=max(75, drift["risk"]), predicted_horizon="IMMEDIATE"))
    if phase.get("temporal_ok") is not True:
        bad = [w for w in witnesses if str(w.get("temporal_status")) != "ADMISSIBLE"]
        alerts.append(_alert("TEMPORAL_VIOLATION", AlertSeverity.CRITICAL, "One or more witnesses failed temporal admissibility.", phase.get("receipt_hash72"), affected_modalities=[_modality_of(w) for w in bad], affected_phase_indices=[_phase_index_of(w) for w in bad], drift_risk=max(70, drift["risk"]), predicted_horizon="IMMEDIATE"))
    if str(phase.get("status")) != "LOCKED":
        alerts.append(_alert("PHASE_STATUS_NOT_LOCKED", AlertSeverity.WARN, f"Phase status is {phase.get('status')}", phase.get("receipt_hash72"), affected_phase_indices=drift["affected_phase_indices"], affected_modalities=drift["affected_modalities"], drift_risk=drift["risk"], predicted_horizon=drift["horizon"]))

    if str(loop.get("status")) != "EXECUTED":
        alerts.append(_alert("OPERATOR_LOOP_NOT_EXECUTED", AlertSeverity.CRITICAL, f"Operator loop status is {loop.get('status')}", loop.get("receipt_hash72"), drift_risk=80, predicted_horizon="IMMEDIATE"))
    if loop.get("external_phase_anchor_used") is not True:
        alerts.append(_alert("EXTERNAL_PHASE_NOT_USED", AlertSeverity.WARN, "Operator loop did not use realtime phase anchor.", loop.get("receipt_hash72"), drift_risk=max(30, drift["risk"]), predicted_horizon="WATCH"))

    if drift["risk"] >= 45 and not any(a.code.startswith("PREDICTIVE") for a in alerts):
        severity = AlertSeverity.CRITICAL if drift["risk"] >= 75 else AlertSeverity.WARN
        alerts.append(_alert("PREDICTIVE_DRIFT_RISK", severity, f"Predicted drift risk {drift['risk']} ({drift['horizon']}).", drift, affected_modalities=drift["affected_modalities"], affected_phase_indices=drift["affected_phase_indices"], drift_risk=drift["risk"], predicted_horizon=drift["horizon"]))

    for key in ["replay_receipt", "feedback_replay_receipt", "loop_replay_receipt"]:
        receipt = loop.get(key) or phase.get(key)
        if isinstance(receipt, dict) and receipt.get("invalid", 0) != 0:
            alerts.append(_alert("REPLAY_INVALID", AlertSeverity.CRITICAL, f"Replay invalid marker found in {key}.", receipt, drift_risk=100, predicted_horizon="IMMEDIATE"))

    critical = sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL)
    warn = sum(1 for a in alerts if a.severity == AlertSeverity.WARN)
    status = "CRITICAL" if critical else "WARN" if warn else "CLEAR"
    summary_hash = hash72_digest(("runtime_anomaly_summary_v1", [a.alert_hash72 for a in alerts], status, drift), width=24)
    return {
        "status": status,
        "critical": critical,
        "warn": warn,
        "info": sum(1 for a in alerts if a.severity == AlertSeverity.INFO),
        "alerts": [a.to_dict() for a in alerts],
        "drift_prediction": drift,
        "summary_hash72": summary_hash,
    }

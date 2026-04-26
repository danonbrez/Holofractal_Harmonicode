"""
HHS Runtime Anomaly Detector v1
===============================

Read-only anomaly classification for runtime snapshots.

Detects:
- missing mandatory modality witnesses
- phase not locked
- temporal violation
- operator loop not executed
- external phase anchor not used
- replay invalid markers when present

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

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


def _alert(code: str, severity: AlertSeverity, message: str, subject: Any = None) -> RuntimeAlert:
    subject_hash = hash72_digest(("runtime_alert_subject_v1", subject), width=18) if subject is not None else None
    alert_hash = hash72_digest(("runtime_alert_v1", code, severity.value, message, subject_hash), width=24)
    return RuntimeAlert(code, severity, message, subject_hash, alert_hash)


def detect_runtime_anomalies(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    phase = snapshot.get("phase", {})
    loop = snapshot.get("operatorLoop", {})
    alerts: List[RuntimeAlert] = []

    if phase.get("mandatory_present") is not True:
        alerts.append(_alert("MISSING_MANDATORY_WITNESS", AlertSeverity.CRITICAL, f"Missing mandatory witnesses: {phase.get('missing_mandatory', [])}", phase.get("missing_mandatory")))
    if phase.get("phase_locked") is not True:
        alerts.append(_alert("PHASE_UNLOCKED", AlertSeverity.CRITICAL, "Mandatory witnesses are not phase locked.", phase.get("receipt_hash72")))
    if phase.get("temporal_ok") is not True:
        alerts.append(_alert("TEMPORAL_VIOLATION", AlertSeverity.CRITICAL, "One or more witnesses failed temporal admissibility.", phase.get("receipt_hash72")))
    if str(phase.get("status")) != "LOCKED":
        alerts.append(_alert("PHASE_STATUS_NOT_LOCKED", AlertSeverity.WARN, f"Phase status is {phase.get('status')}", phase.get("receipt_hash72")))

    if str(loop.get("status")) != "EXECUTED":
        alerts.append(_alert("OPERATOR_LOOP_NOT_EXECUTED", AlertSeverity.CRITICAL, f"Operator loop status is {loop.get('status')}", loop.get("receipt_hash72")))
    if loop.get("external_phase_anchor_used") is not True:
        alerts.append(_alert("EXTERNAL_PHASE_NOT_USED", AlertSeverity.WARN, "Operator loop did not use realtime phase anchor.", loop.get("receipt_hash72")))

    for key in ["replay_receipt", "feedback_replay_receipt", "loop_replay_receipt"]:
        receipt = loop.get(key) or phase.get(key)
        if isinstance(receipt, dict) and receipt.get("invalid", 0) != 0:
            alerts.append(_alert("REPLAY_INVALID", AlertSeverity.CRITICAL, f"Replay invalid marker found in {key}.", receipt))

    critical = sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL)
    warn = sum(1 for a in alerts if a.severity == AlertSeverity.WARN)
    status = "CRITICAL" if critical else "WARN" if warn else "CLEAR"
    summary_hash = hash72_digest(("runtime_anomaly_summary_v1", [a.alert_hash72 for a in alerts], status), width=24)
    return {
        "status": status,
        "critical": critical,
        "warn": warn,
        "info": sum(1 for a in alerts if a.severity == AlertSeverity.INFO),
        "alerts": [a.to_dict() for a in alerts],
        "summary_hash72": summary_hash,
    }

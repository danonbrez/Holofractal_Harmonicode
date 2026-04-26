"""
HHS Phase Stabilization Feedback Loop v1
=======================================

Bounded correction layer for runtime anomalies.

Pipeline:
    detect -> suggest -> re-lock probe

Important: suggestions are proposal records only. This module does not mutate
kernel state or bypass the realtime phase lock / shell / replay path.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


class CorrectionKind(str, Enum):
    RESTORE_MANDATORY_WITNESS = "RESTORE_MANDATORY_WITNESS"
    REALIGN_PHASE_TO_ANCHOR = "REALIGN_PHASE_TO_ANCHOR"
    REFRESH_TEMPORAL_WINDOW = "REFRESH_TEMPORAL_WINDOW"
    REQUIRE_EXTERNAL_PHASE_ANCHOR = "REQUIRE_EXTERNAL_PHASE_ANCHOR"
    REPLAY_LEDGER_REVERIFY = "REPLAY_LEDGER_REVERIFY"
    HOLD_STATE = "HOLD_STATE"


@dataclass(frozen=True)
class CorrectiveOperatorSuggestion:
    kind: CorrectionKind
    priority: int
    target_modalities: List[str]
    target_phase_indices: List[int]
    reason: str
    proposed_patch: Dict[str, Any]
    suggestion_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


@dataclass(frozen=True)
class StabilizationProbeReceipt:
    input_summary_hash72: str
    suggestion_hashes: List[str]
    expected_relock_possible: bool
    relock_strategy: str
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _suggestion(kind: CorrectionKind, priority: int, modalities: List[str], indices: List[int], reason: str, patch: Dict[str, Any]) -> CorrectiveOperatorSuggestion:
    h = hash72_digest(("corrective_operator_suggestion_v1", kind.value, priority, modalities, indices, reason, patch), width=24)
    return CorrectiveOperatorSuggestion(kind, priority, modalities, indices, reason, patch, h)


def propose_corrective_operators(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    anomalies = snapshot.get("anomalies", {})
    alerts = anomalies.get("alerts", []) or []
    suggestions: List[CorrectiveOperatorSuggestion] = []

    for alert in alerts:
        code = alert.get("code")
        modalities = [str(x) for x in alert.get("affected_modalities", [])]
        indices = [int(x) for x in alert.get("affected_phase_indices", [])]
        if code == "MISSING_MANDATORY_WITNESS":
            suggestions.append(_suggestion(CorrectionKind.RESTORE_MANDATORY_WITNESS, 100, modalities, indices, "Restore all missing mandatory witnesses before state mutation.", {"op": "HOLD", "requires": modalities}))
        elif code == "PHASE_UNLOCKED" or code == "PREDICTIVE_DRIFT_RISK":
            suggestions.append(_suggestion(CorrectionKind.REALIGN_PHASE_TO_ANCHOR, 80, modalities, indices, "Recompute live phase anchor and reject out-of-band support witnesses.", {"op": "RELOCK_PHASE", "target_phase_indices": indices}))
        elif code == "TEMPORAL_VIOLATION":
            suggestions.append(_suggestion(CorrectionKind.REFRESH_TEMPORAL_WINDOW, 90, modalities, indices, "Refresh expired or late modality packets inside QGU window.", {"op": "REFRESH_WINDOW", "target_modalities": modalities}))
        elif code == "EXTERNAL_PHASE_NOT_USED":
            suggestions.append(_suggestion(CorrectionKind.REQUIRE_EXTERNAL_PHASE_ANCHOR, 70, modalities, indices, "Bind operator loop to realtime phase lock receipt before execution.", {"op": "REQUIRE_EXTERNAL_ANCHOR"}))
        elif code == "REPLAY_INVALID":
            suggestions.append(_suggestion(CorrectionKind.REPLAY_LEDGER_REVERIFY, 100, modalities, indices, "Stop execution and reverify receipt chain from genesis.", {"op": "REVERIFY_REPLAY"}))

    if not suggestions and anomalies.get("status") == "CLEAR":
        suggestions.append(_suggestion(CorrectionKind.HOLD_STATE, 1, [], [], "No correction needed; hold locked state.", {"op": "HOLD"}))

    probe = stabilization_probe(snapshot, suggestions)
    return {
        "suggestions": [s.to_dict() for s in suggestions],
        "probe": probe.to_dict(),
        "summary_hash72": hash72_digest(("corrective_operator_suggestions_summary_v1", [s.suggestion_hash72 for s in suggestions], probe.receipt_hash72), width=24),
    }


def stabilization_probe(snapshot: Dict[str, Any], suggestions: List[CorrectiveOperatorSuggestion]) -> StabilizationProbeReceipt:
    anomalies = snapshot.get("anomalies", {})
    critical = int(anomalies.get("critical", 0) or 0)
    has_replay_invalid = any(s.kind == CorrectionKind.REPLAY_LEDGER_REVERIFY for s in suggestions)
    expected = critical == 0 or (suggestions and not has_replay_invalid)
    strategy = "HOLD_LOCK" if not suggestions or suggestions[0].kind == CorrectionKind.HOLD_STATE else "DETECT_SUGGEST_RELOCK"
    input_hash = hash72_digest(("stabilization_input_summary_v1", anomalies, snapshot.get("phase", {}).get("receipt_hash72"), snapshot.get("operatorLoop", {}).get("receipt_hash72")), width=24)
    receipt = hash72_digest(("stabilization_probe_receipt_v1", input_hash, [s.suggestion_hash72 for s in suggestions], expected, strategy), width=24)
    return StabilizationProbeReceipt(input_hash, [s.suggestion_hash72 for s in suggestions], expected, strategy, receipt)

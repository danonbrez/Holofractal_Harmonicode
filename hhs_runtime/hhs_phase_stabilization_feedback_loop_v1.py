"""
HHS Phase Stabilization Feedback Loop v1
=======================================

Bounded correction layer for runtime anomalies.

Pipeline:
    detect -> suggest -> probe -> approve -> re-lock -> verify

Important: suggestions are proposal records only until their suggestion_hash72
appears in an explicit approval set. Execution is still bounded: no direct kernel
mutation, no bypass of phase lock, and no success without replayable receipts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Sequence

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


class CorrectionKind(str, Enum):
    RESTORE_MANDATORY_WITNESS = "RESTORE_MANDATORY_WITNESS"
    REALIGN_PHASE_TO_ANCHOR = "REALIGN_PHASE_TO_ANCHOR"
    REFRESH_TEMPORAL_WINDOW = "REFRESH_TEMPORAL_WINDOW"
    REQUIRE_EXTERNAL_PHASE_ANCHOR = "REQUIRE_EXTERNAL_PHASE_ANCHOR"
    REPLAY_LEDGER_REVERIFY = "REPLAY_LEDGER_REVERIFY"
    HOLD_STATE = "HOLD_STATE"


class CorrectionExecutionStatus(str, Enum):
    APPLIED = "APPLIED"
    HELD = "HELD"
    REJECTED_UNAPPROVED = "REJECTED_UNAPPROVED"
    RELOCK_FAILED = "RELOCK_FAILED"
    REPLAY_BLOCKED = "REPLAY_BLOCKED"


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


@dataclass(frozen=True)
class CorrectionExecutionReceipt:
    suggestion_hash72: str
    approved: bool
    status: CorrectionExecutionStatus
    relock_receipt_hash72: str | None
    verification_hash72: str | None
    reason: str
    execution_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


def _suggestion(kind: CorrectionKind, priority: int, modalities: List[str], indices: List[int], reason: str, patch: Dict[str, Any]) -> CorrectiveOperatorSuggestion:
    h = hash72_digest(("corrective_operator_suggestion_v1", kind.value, priority, modalities, indices, reason, patch), width=24)
    return CorrectiveOperatorSuggestion(kind, priority, modalities, indices, reason, patch, h)


def _hydrate_suggestion(raw: Dict[str, Any]) -> CorrectiveOperatorSuggestion:
    return CorrectiveOperatorSuggestion(
        kind=CorrectionKind(raw["kind"]),
        priority=int(raw["priority"]),
        target_modalities=[str(x) for x in raw.get("target_modalities", [])],
        target_phase_indices=[int(x) for x in raw.get("target_phase_indices", [])],
        reason=str(raw.get("reason", "")),
        proposed_patch=dict(raw.get("proposed_patch", {})),
        suggestion_hash72=str(raw["suggestion_hash72"]),
    )


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


def execute_approved_corrections(
    snapshot: Dict[str, Any],
    approved_suggestion_hashes: Sequence[str],
    *,
    relock_fn: Callable[[CorrectiveOperatorSuggestion], Dict[str, Any]] | None = None,
    verify_fn: Callable[[CorrectiveOperatorSuggestion, Dict[str, Any]], Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """Execute only explicitly approved correction suggestions.

    relock_fn and verify_fn are injectable so runtime APIs can bind the execution
    to their certified realtime phase lock and replay stack. Without callbacks,
    this function holds state and emits receipts, but does not claim correction.
    """
    corrections = snapshot.get("corrections") or propose_corrective_operators(snapshot)
    suggestions = [_hydrate_suggestion(s) for s in corrections.get("suggestions", [])]
    approved = set(str(x) for x in approved_suggestion_hashes)
    receipts: List[CorrectionExecutionReceipt] = []

    for suggestion in suggestions:
        is_approved = suggestion.suggestion_hash72 in approved
        if not is_approved:
            status = CorrectionExecutionStatus.REJECTED_UNAPPROVED
            relock_hash = None
            verify_hash = None
            reason = "Suggestion hash not present in explicit approval set."
        elif suggestion.kind == CorrectionKind.HOLD_STATE:
            status = CorrectionExecutionStatus.HELD
            relock_hash = snapshot.get("phase", {}).get("receipt_hash72")
            verify_hash = hash72_digest(("hold_state_verification_v1", relock_hash, suggestion.suggestion_hash72), width=24)
            reason = "Locked state held; no correction mutation needed."
        elif suggestion.kind == CorrectionKind.REPLAY_LEDGER_REVERIFY:
            status = CorrectionExecutionStatus.REPLAY_BLOCKED
            relock_hash = None
            verify_hash = None
            reason = "Replay invalid requires manual genesis-chain verification before correction."
        else:
            relock = relock_fn(suggestion) if relock_fn else {}
            relock_hash = relock.get("receipt_hash72")
            relock_ok = relock.get("status") == "LOCKED" and relock.get("phase_locked") is True and relock.get("temporal_ok") is True
            if not relock_ok:
                status = CorrectionExecutionStatus.RELOCK_FAILED
                verify_hash = None
                reason = "Correction attempted but re-lock did not produce LOCKED phase receipt."
            else:
                verification = verify_fn(suggestion, relock) if verify_fn else {"ok": False, "reason": "No verification callback supplied."}
                ok = bool(verification.get("ok"))
                status = CorrectionExecutionStatus.APPLIED if ok else CorrectionExecutionStatus.RELOCK_FAILED
                verify_hash = verification.get("verification_hash72") or hash72_digest(("correction_verification_v1", suggestion.to_dict(), relock, verification), width=24)
                reason = "Correction approved, re-locked, and verified." if ok else str(verification.get("reason", "Verification failed."))
        execution_hash = hash72_digest(("correction_execution_receipt_v1", suggestion.suggestion_hash72, is_approved, status.value, relock_hash, verify_hash, reason), width=24)
        receipts.append(CorrectionExecutionReceipt(suggestion.suggestion_hash72, is_approved, status, relock_hash, verify_hash, reason, execution_hash))

    summary_hash = hash72_digest(("approved_correction_execution_summary_v1", [r.execution_hash72 for r in receipts], sorted(approved)), width=24)
    return {
        "approved_suggestion_hashes": sorted(approved),
        "executions": [r.to_dict() for r in receipts],
        "summary_hash72": summary_hash,
    }

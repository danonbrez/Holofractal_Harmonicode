"""
HHS Phase Stabilization Feedback Loop v1
=======================================

Bounded correction layer for runtime anomalies.

Pipeline:
    detect -> suggest -> probe -> approve -> adaptive consensus -> re-lock -> verify -> learn

Learning is bounded: successful correction receipts can tune future agent
weights only inside fixed caps. No learned weight can bypass approval, risk,
phase lock, replay, or verification gates.
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
    REJECTED_NO_CONSENSUS = "REJECTED_NO_CONSENSUS"
    RELOCK_FAILED = "RELOCK_FAILED"
    REPLAY_BLOCKED = "REPLAY_BLOCKED"


BASE_AGENT_WEIGHTS = {"LOGIC_AGENT": 5, "AUDIT_AGENT": 6, "PROCESS_AGENT": 3, "SYNTHESIS_AGENT": 4, "STYLE_AGENT": 1}
AGENT_WEIGHT_CAPS = {"LOGIC_AGENT": (4, 7), "AUDIT_AGENT": (6, 8), "PROCESS_AGENT": (2, 5), "SYNTHESIS_AGENT": (3, 6), "STYLE_AGENT": (1, 2)}


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
class AdaptiveWeightReceipt:
    agent_weights: Dict[str, int]
    source_feedback_hashes: List[str]
    capped: bool
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CorrectionConsensusReceipt:
    suggestion_hash72: str
    weighted_vote: int
    weighted_total: int
    risk_score: int
    passed: bool
    supporting_agents: List[str]
    agent_weights: Dict[str, int]
    adaptive_weight_receipt_hash72: str | None
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CorrectionExecutionReceipt:
    suggestion_hash72: str
    approved: bool
    consensus_passed: bool
    consensus_receipt_hash72: str | None
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
    return CorrectiveOperatorSuggestion(CorrectionKind(raw["kind"]), int(raw["priority"]), [str(x) for x in raw.get("target_modalities", [])], [int(x) for x in raw.get("target_phase_indices", [])], str(raw.get("reason", "")), dict(raw.get("proposed_patch", {})), str(raw["suggestion_hash72"]))


def _clamp_weight(agent: str, value: int) -> int:
    lo, hi = AGENT_WEIGHT_CAPS[agent]
    return max(lo, min(hi, value))


def adaptive_weights_from_feedback(feedback_records: Sequence[Dict[str, Any]] | None = None) -> AdaptiveWeightReceipt:
    weights = dict(BASE_AGENT_WEIGHTS)
    feedback_hashes: List[str] = []
    capped = False
    for record in feedback_records or []:
        feedback_hash = str(record.get("summary_hash72") or record.get("execution_hash72") or hash72_digest(("unknown_feedback", record), width=18))
        feedback_hashes.append(feedback_hash)
        for execution in record.get("executions", []) or []:
            status = execution.get("status")
            consensus_hash = execution.get("consensus_receipt_hash72")
            if status == "APPLIED":
                # Conservative reinforcement: execution success strengthens process/synthesis slightly.
                weights["PROCESS_AGENT"] += 1
                weights["SYNTHESIS_AGENT"] += 1
            elif status in {"RELOCK_FAILED", "REJECTED_NO_CONSENSUS"}:
                # Failed corrections increase audit pressure and reduce risky synthesis influence.
                weights["AUDIT_AGENT"] += 1
                weights["SYNTHESIS_AGENT"] -= 1
            elif status == "REPLAY_BLOCKED":
                weights["AUDIT_AGENT"] += 1
                weights["LOGIC_AGENT"] += 1
    clamped = {}
    for agent, value in weights.items():
        c = _clamp_weight(agent, value)
        capped = capped or c != value
        clamped[agent] = c
    receipt = hash72_digest(("adaptive_weight_receipt_v1", clamped, feedback_hashes, capped), width=24)
    return AdaptiveWeightReceipt(clamped, feedback_hashes, capped, receipt)


def correction_consensus(snapshot: Dict[str, Any], suggestion: CorrectiveOperatorSuggestion, adaptive_weights: AdaptiveWeightReceipt | None = None) -> CorrectionConsensusReceipt:
    anomalies = snapshot.get("anomalies", {})
    critical = int(anomalies.get("critical", 0) or 0)
    replay_invalid = any(a.get("code") == "REPLAY_INVALID" for a in anomalies.get("alerts", []) or [])
    agents = dict(adaptive_weights.agent_weights if adaptive_weights else BASE_AGENT_WEIGHTS)
    weighted_total = sum(agents.values())
    supporting: List[str] = []

    if suggestion.kind in {CorrectionKind.RESTORE_MANDATORY_WITNESS, CorrectionKind.REQUIRE_EXTERNAL_PHASE_ANCHOR, CorrectionKind.REPLAY_LEDGER_REVERIFY, CorrectionKind.HOLD_STATE}:
        supporting.append("LOGIC_AGENT")
    if suggestion.kind != CorrectionKind.REPLAY_LEDGER_REVERIFY or replay_invalid:
        supporting.append("AUDIT_AGENT")
    if suggestion.kind in {CorrectionKind.REFRESH_TEMPORAL_WINDOW, CorrectionKind.RESTORE_MANDATORY_WITNESS, CorrectionKind.HOLD_STATE}:
        supporting.append("PROCESS_AGENT")
    if suggestion.kind in {CorrectionKind.REALIGN_PHASE_TO_ANCHOR, CorrectionKind.REQUIRE_EXTERNAL_PHASE_ANCHOR, CorrectionKind.HOLD_STATE}:
        supporting.append("SYNTHESIS_AGENT")
    if suggestion.kind == CorrectionKind.HOLD_STATE:
        supporting.append("STYLE_AGENT")

    risk = 0
    if replay_invalid and suggestion.kind != CorrectionKind.REPLAY_LEDGER_REVERIFY:
        risk += 100
    if critical > 0 and suggestion.kind == CorrectionKind.HOLD_STATE:
        risk += 80
    if suggestion.kind == CorrectionKind.REPLAY_LEDGER_REVERIFY:
        risk += 100

    vote = sum(agents[a] for a in set(supporting))
    passed = vote * 3 >= weighted_total * 2 and risk == 0
    adaptive_hash = adaptive_weights.receipt_hash72 if adaptive_weights else None
    receipt = hash72_digest(("correction_consensus_receipt_v1", suggestion.to_dict(), vote, weighted_total, risk, passed, sorted(set(supporting)), agents, adaptive_hash), width=24)
    return CorrectionConsensusReceipt(suggestion.suggestion_hash72, vote, weighted_total, risk, passed, sorted(set(supporting)), agents, adaptive_hash, receipt)


def propose_corrective_operators(snapshot: Dict[str, Any], feedback_records: Sequence[Dict[str, Any]] | None = None) -> Dict[str, Any]:
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
    adaptive = adaptive_weights_from_feedback(feedback_records)
    consensus = [correction_consensus(snapshot, s, adaptive).to_dict() for s in suggestions]
    return {"suggestions": [s.to_dict() for s in suggestions], "adaptiveWeights": adaptive.to_dict(), "consensus": consensus, "probe": probe.to_dict(), "summary_hash72": hash72_digest(("corrective_operator_suggestions_summary_v1", [s.suggestion_hash72 for s in suggestions], [c["receipt_hash72"] for c in consensus], adaptive.receipt_hash72, probe.receipt_hash72), width=24)}


def stabilization_probe(snapshot: Dict[str, Any], suggestions: List[CorrectiveOperatorSuggestion]) -> StabilizationProbeReceipt:
    anomalies = snapshot.get("anomalies", {})
    critical = int(anomalies.get("critical", 0) or 0)
    has_replay_invalid = any(s.kind == CorrectionKind.REPLAY_LEDGER_REVERIFY for s in suggestions)
    expected = critical == 0 or (suggestions and not has_replay_invalid)
    strategy = "HOLD_LOCK" if not suggestions or suggestions[0].kind == CorrectionKind.HOLD_STATE else "DETECT_SUGGEST_RELOCK"
    input_hash = hash72_digest(("stabilization_input_summary_v1", anomalies, snapshot.get("phase", {}).get("receipt_hash72"), snapshot.get("operatorLoop", {}).get("receipt_hash72")), width=24)
    receipt = hash72_digest(("stabilization_probe_receipt_v1", input_hash, [s.suggestion_hash72 for s in suggestions], expected, strategy), width=24)
    return StabilizationProbeReceipt(input_hash, [s.suggestion_hash72 for s in suggestions], expected, strategy, receipt)


def execute_approved_corrections(snapshot: Dict[str, Any], approved_suggestion_hashes: Sequence[str], *, relock_fn: Callable[[CorrectiveOperatorSuggestion], Dict[str, Any]] | None = None, verify_fn: Callable[[CorrectiveOperatorSuggestion, Dict[str, Any]], Dict[str, Any]] | None = None, feedback_records: Sequence[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    corrections = snapshot.get("corrections") or propose_corrective_operators(snapshot, feedback_records)
    suggestions = [_hydrate_suggestion(s) for s in corrections.get("suggestions", [])]
    approved = set(str(x) for x in approved_suggestion_hashes)
    adaptive = adaptive_weights_from_feedback(feedback_records)
    receipts: List[CorrectionExecutionReceipt] = []
    consensus_receipts: List[CorrectionConsensusReceipt] = []

    for suggestion in suggestions:
        is_approved = suggestion.suggestion_hash72 in approved
        consensus = correction_consensus(snapshot, suggestion, adaptive)
        consensus_receipts.append(consensus)
        if not is_approved:
            status, relock_hash, verify_hash, reason = CorrectionExecutionStatus.REJECTED_UNAPPROVED, None, None, "Suggestion hash not present in explicit approval set."
        elif not consensus.passed:
            status, relock_hash, verify_hash, reason = CorrectionExecutionStatus.REJECTED_NO_CONSENSUS, None, None, "Human approval present, but adaptive multi-agent correction consensus failed."
        elif suggestion.kind == CorrectionKind.HOLD_STATE:
            status = CorrectionExecutionStatus.HELD
            relock_hash = snapshot.get("phase", {}).get("receipt_hash72")
            verify_hash = hash72_digest(("hold_state_verification_v1", relock_hash, suggestion.suggestion_hash72), width=24)
            reason = "Locked state held; no correction mutation needed."
        elif suggestion.kind == CorrectionKind.REPLAY_LEDGER_REVERIFY:
            status, relock_hash, verify_hash, reason = CorrectionExecutionStatus.REPLAY_BLOCKED, None, None, "Replay invalid requires manual genesis-chain verification before correction."
        else:
            relock = relock_fn(suggestion) if relock_fn else {}
            relock_hash = relock.get("receipt_hash72")
            relock_ok = relock.get("status") == "LOCKED" and relock.get("phase_locked") is True and relock.get("temporal_ok") is True
            if not relock_ok:
                status, verify_hash, reason = CorrectionExecutionStatus.RELOCK_FAILED, None, "Correction attempted but re-lock did not produce LOCKED phase receipt."
            else:
                verification = verify_fn(suggestion, relock) if verify_fn else {"ok": False, "reason": "No verification callback supplied."}
                ok = bool(verification.get("ok"))
                status = CorrectionExecutionStatus.APPLIED if ok else CorrectionExecutionStatus.RELOCK_FAILED
                verify_hash = verification.get("verification_hash72") or hash72_digest(("correction_verification_v1", suggestion.to_dict(), relock, verification), width=24)
                reason = "Correction approved, adaptive consensus-passed, re-locked, and verified." if ok else str(verification.get("reason", "Verification failed."))
        execution_hash = hash72_digest(("correction_execution_receipt_v1", suggestion.suggestion_hash72, is_approved, consensus.receipt_hash72, consensus.passed, status.value, relock_hash, verify_hash, reason), width=24)
        receipts.append(CorrectionExecutionReceipt(suggestion.suggestion_hash72, is_approved, consensus.passed, consensus.receipt_hash72, status, relock_hash, verify_hash, reason, execution_hash))

    summary_hash = hash72_digest(("approved_correction_execution_summary_v1", [r.execution_hash72 for r in receipts], [c.receipt_hash72 for c in consensus_receipts], adaptive.receipt_hash72, sorted(approved)), width=24)
    return {"approved_suggestion_hashes": sorted(approved), "adaptiveWeights": adaptive.to_dict(), "consensus": [c.to_dict() for c in consensus_receipts], "executions": [r.to_dict() for r in receipts], "summary_hash72": summary_hash}

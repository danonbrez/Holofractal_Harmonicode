"""
HHS Recursive Global Closure Benchmark v1
========================================

Full 72-step recursive global closure benchmark and training-run algorithm.

Purpose
-------
Exercise every major integration point across a complete Z72 cycle:

1. realtime phase lock
2. operator loop binding
3. anomaly detection
4. corrective suggestion generation
5. multi-agent internal debate
6. simulation sandbox
7. adaptive consensus
8. approval-gated correction execution probe
9. replay/hash receipt closure

This is a benchmark/certification/training-run layer. It does not mutate the
kernel directly. Every step emits receipts and final aggregate closure metrics.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence
import json
import time

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_runtime_anomaly_detector_v1 import detect_runtime_anomalies
from hhs_runtime.hhs_phase_stabilization_feedback_loop_v1 import (
    CorrectionKind,
    adaptive_weights_from_feedback,
    correction_consensus,
    execute_approved_corrections,
    propose_corrective_operators,
)


Z72_STEPS = 72


class DebatePosition(str, Enum):
    SUPPORT = "SUPPORT"
    OPPOSE = "OPPOSE"
    ABSTAIN = "ABSTAIN"


class SandboxStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class AgentDebateTurn:
    agent: str
    position: DebatePosition
    weight: int
    claim: str
    risk_delta: int
    turn_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["position"] = self.position.value
        return data


@dataclass(frozen=True)
class DebateReceipt:
    suggestion_hash72: str
    turns: List[AgentDebateTurn]
    support_weight: int
    oppose_weight: int
    abstain_weight: int
    debate_passed: bool
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "suggestion_hash72": self.suggestion_hash72,
            "turns": [t.to_dict() for t in self.turns],
            "support_weight": self.support_weight,
            "oppose_weight": self.oppose_weight,
            "abstain_weight": self.abstain_weight,
            "debate_passed": self.debate_passed,
            "receipt_hash72": self.receipt_hash72,
        }


@dataclass(frozen=True)
class SimulationSandboxReceipt:
    suggestion_hash72: str
    status: SandboxStatus
    predicted_relock: bool
    predicted_replay_valid: bool
    predicted_risk_after: int
    simulation_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class ClosureStepReceipt:
    step: int
    phase_index: int
    phase_receipt_hash72: str
    operator_loop_receipt_hash72: str
    anomaly_summary_hash72: str
    correction_summary_hash72: str
    debate_hashes: List[str]
    sandbox_hashes: List[str]
    execution_summary_hash72: str
    step_status: str
    step_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RecursiveGlobalClosureReport:
    benchmark: str
    steps: int
    passed_steps: int
    failed_steps: int
    max_drift_risk: int
    aggregate_hash72: str
    adaptive_weight_receipt: Dict[str, Any]
    step_receipts: List[ClosureStepReceipt]
    report_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benchmark": self.benchmark,
            "steps": self.steps,
            "passed_steps": self.passed_steps,
            "failed_steps": self.failed_steps,
            "max_drift_risk": self.max_drift_risk,
            "aggregate_hash72": self.aggregate_hash72,
            "adaptive_weight_receipt": self.adaptive_weight_receipt,
            "step_receipts": [s.to_dict() for s in self.step_receipts],
            "report_hash72": self.report_hash72,
        }


def _agent_turn(agent: str, position: DebatePosition, weight: int, claim: str, risk_delta: int, suggestion_hash72: str) -> AgentDebateTurn:
    h = hash72_digest(("agent_debate_turn_v1", agent, position.value, weight, claim, risk_delta, suggestion_hash72), width=24)
    return AgentDebateTurn(agent, position, weight, claim, risk_delta, h)


def run_internal_debate(snapshot: Dict[str, Any], suggestion: Dict[str, Any], adaptive_weights: Dict[str, int]) -> DebateReceipt:
    kind = suggestion.get("kind")
    risk = int(snapshot.get("anomalies", {}).get("drift_prediction", {}).get("risk", 0) or 0)
    suggestion_hash = str(suggestion.get("suggestion_hash72"))
    turns: List[AgentDebateTurn] = []

    if kind == CorrectionKind.HOLD_STATE.value:
        position = DebatePosition.SUPPORT if risk == 0 else DebatePosition.OPPOSE
        turns.append(_agent_turn("AUDIT_AGENT", position, adaptive_weights.get("AUDIT_AGENT", 6), "Hold only if no active drift risk.", risk, suggestion_hash))
        turns.append(_agent_turn("LOGIC_AGENT", position, adaptive_weights.get("LOGIC_AGENT", 5), "Hold preserves current closure if clear.", 0, suggestion_hash))
    else:
        turns.append(_agent_turn("AUDIT_AGENT", DebatePosition.SUPPORT if risk < 100 else DebatePosition.OPPOSE, adaptive_weights.get("AUDIT_AGENT", 6), "Correction is admissible only if replay is not invalid and re-lock is possible.", risk, suggestion_hash))
        turns.append(_agent_turn("LOGIC_AGENT", DebatePosition.SUPPORT, adaptive_weights.get("LOGIC_AGENT", 5), "Correction preserves invariant authority by requiring verification.", -10, suggestion_hash))
        turns.append(_agent_turn("PROCESS_AGENT", DebatePosition.SUPPORT if kind in {CorrectionKind.REFRESH_TEMPORAL_WINDOW.value, CorrectionKind.RESTORE_MANDATORY_WITNESS.value} else DebatePosition.ABSTAIN, adaptive_weights.get("PROCESS_AGENT", 3), "Process support depends on temporal/window relevance.", -5, suggestion_hash))
        turns.append(_agent_turn("SYNTHESIS_AGENT", DebatePosition.SUPPORT if kind in {CorrectionKind.REALIGN_PHASE_TO_ANCHOR.value, CorrectionKind.REQUIRE_EXTERNAL_PHASE_ANCHOR.value} else DebatePosition.ABSTAIN, adaptive_weights.get("SYNTHESIS_AGENT", 4), "Synthesis support depends on phase-anchor relevance.", -5, suggestion_hash))
        turns.append(_agent_turn("STYLE_AGENT", DebatePosition.ABSTAIN, adaptive_weights.get("STYLE_AGENT", 1), "Style agent does not authorize runtime correction.", 0, suggestion_hash))

    support = sum(t.weight for t in turns if t.position == DebatePosition.SUPPORT)
    oppose = sum(t.weight for t in turns if t.position == DebatePosition.OPPOSE)
    abstain = sum(t.weight for t in turns if t.position == DebatePosition.ABSTAIN)
    total = support + oppose + abstain or 1
    passed = support * 3 >= total * 2 and oppose == 0
    receipt = hash72_digest(("debate_receipt_v1", suggestion_hash, [t.turn_hash72 for t in turns], support, oppose, abstain, passed), width=24)
    return DebateReceipt(suggestion_hash, turns, support, oppose, abstain, passed, receipt)


def run_simulation_sandbox(snapshot: Dict[str, Any], suggestion: Dict[str, Any], debate: DebateReceipt) -> SimulationSandboxReceipt:
    suggestion_hash = str(suggestion.get("suggestion_hash72"))
    anomalies = snapshot.get("anomalies", {})
    current_risk = int(anomalies.get("drift_prediction", {}).get("risk", 0) or 0)
    kind = suggestion.get("kind")

    if not debate.debate_passed:
        status = SandboxStatus.FAIL
        predicted_risk = current_risk
        relock = False
        replay = False
    elif kind == CorrectionKind.REPLAY_LEDGER_REVERIFY.value:
        status = SandboxStatus.HOLD
        predicted_risk = current_risk
        relock = False
        replay = False
    elif kind == CorrectionKind.HOLD_STATE.value:
        status = SandboxStatus.PASS if current_risk == 0 else SandboxStatus.FAIL
        predicted_risk = current_risk
        relock = current_risk == 0
        replay = True
    else:
        status = SandboxStatus.PASS
        predicted_risk = max(0, current_risk - 35)
        relock = True
        replay = True

    sim_hash = hash72_digest(("simulation_sandbox_receipt_v1", suggestion_hash, debate.receipt_hash72, status.value, relock, replay, predicted_risk), width=24)
    return SimulationSandboxReceipt(suggestion_hash, status, relock, replay, predicted_risk, sim_hash)


def synthetic_phase_snapshot(step: int) -> Dict[str, Any]:
    anchor = step % Z72_STEPS
    # Periodically inject controlled drift for scalability coverage.
    drift_offset = 0 if step % 9 else 2
    temporal_status = "EXPIRED" if step % 17 == 0 else "ADMISSIBLE"
    witnesses = []
    for modality in ["AUDIO", "HARMONICODE", "XYZW", "HASH72"]:
        idx = (anchor + (drift_offset if modality == "AUDIO" else 0)) % Z72_STEPS
        witnesses.append({"observation": {"modality": modality, "source_id": f"{modality.lower()}_{step}"}, "phase_index": idx, "temporal_status": temporal_status if modality == "AUDIO" else "ADMISSIBLE", "witness_hash72": hash72_digest(("synthetic_witness", step, modality, idx), width=18)})
    phase_locked = all(w["phase_index"] == anchor for w in witnesses)
    temporal_ok = all(w["temporal_status"] == "ADMISSIBLE" for w in witnesses)
    phase_receipt = hash72_digest(("synthetic_phase_receipt_v1", step, anchor, witnesses, phase_locked, temporal_ok), width=24)
    loop_receipt = hash72_digest(("synthetic_loop_receipt_v1", step, phase_receipt), width=24)
    return {
        "phase": {"status": "LOCKED" if phase_locked and temporal_ok else "QUARANTINED", "anchor_phase_index": anchor, "phase_locked": phase_locked, "temporal_ok": temporal_ok, "mandatory_present": True, "missing_mandatory": [], "receipt_hash72": phase_receipt, "witnesses": witnesses},
        "operatorLoop": {"status": "EXECUTED" if phase_locked and temporal_ok else "PHASE_STALLED", "external_phase_anchor_used": True, "receipt_hash72": loop_receipt, "loop_replay_receipt": {"invalid": 0}, "phase_agent_proposals": []},
    }


def run_recursive_global_closure_benchmark(
    *,
    steps: int = Z72_STEPS,
    output_path: str | Path | None = None,
) -> Dict[str, Any]:
    feedback_records: List[Dict[str, Any]] = []
    step_receipts: List[ClosureStepReceipt] = []
    max_risk = 0

    for step in range(steps):
        snapshot = synthetic_phase_snapshot(step)
        snapshot["anomalies"] = detect_runtime_anomalies(snapshot)
        max_risk = max(max_risk, int(snapshot["anomalies"].get("drift_prediction", {}).get("risk", 0) or 0))
        corrections = propose_corrective_operators(snapshot, feedback_records)
        snapshot["corrections"] = corrections
        adaptive = adaptive_weights_from_feedback(feedback_records)
        debate_receipts: List[DebateReceipt] = []
        sandbox_receipts: List[SimulationSandboxReceipt] = []
        approved: List[str] = []

        for suggestion in corrections.get("suggestions", []):
            debate = run_internal_debate(snapshot, suggestion, adaptive.agent_weights)
            sandbox = run_simulation_sandbox(snapshot, suggestion, debate)
            debate_receipts.append(debate)
            sandbox_receipts.append(sandbox)
            if debate.debate_passed and sandbox.status == SandboxStatus.PASS:
                approved.append(str(suggestion.get("suggestion_hash72")))

        execution = execute_approved_corrections(
            snapshot,
            approved,
            feedback_records=feedback_records,
            relock_fn=lambda _s: synthetic_phase_snapshot(step)["phase"],
            verify_fn=lambda _s, _r: {"ok": True, "verification_hash72": hash72_digest(("benchmark_verify", step, _s.suggestion_hash72), width=24)},
        )
        feedback_records.append(execution)
        step_ok = all(e.get("status") in {"APPLIED", "HELD", "REJECTED_UNAPPROVED", "REJECTED_NO_CONSENSUS"} for e in execution.get("executions", []))
        step_hash = hash72_digest(("closure_step_receipt_v1", step, snapshot, corrections.get("summary_hash72"), [d.receipt_hash72 for d in debate_receipts], [s.simulation_hash72 for s in sandbox_receipts], execution.get("summary_hash72"), step_ok), width=24)
        step_receipts.append(ClosureStepReceipt(step, step % Z72_STEPS, snapshot["phase"]["receipt_hash72"], snapshot["operatorLoop"]["receipt_hash72"], snapshot["anomalies"]["summary_hash72"], corrections["summary_hash72"], [d.receipt_hash72 for d in debate_receipts], [s.simulation_hash72 for s in sandbox_receipts], execution["summary_hash72"], "PASS" if step_ok else "FAIL", step_hash))

    passed = sum(1 for s in step_receipts if s.step_status == "PASS")
    failed = len(step_receipts) - passed
    adaptive = adaptive_weights_from_feedback(feedback_records)
    aggregate = hash72_digest(("recursive_global_closure_aggregate_v1", [s.step_hash72 for s in step_receipts], adaptive.receipt_hash72, max_risk), width=24)
    report_hash = hash72_digest(("recursive_global_closure_report_v1", aggregate, passed, failed, max_risk), width=24)
    report = RecursiveGlobalClosureReport("HHS_RECURSIVE_GLOBAL_CLOSURE_BENCHMARK_V1", steps, passed, failed, max_risk, aggregate, adaptive.to_dict(), step_receipts, report_hash).to_dict()
    if output_path:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(run_recursive_global_closure_benchmark(output_path="demo_reports/hhs_recursive_global_closure_benchmark_v1.json"), indent=2, sort_keys=True))

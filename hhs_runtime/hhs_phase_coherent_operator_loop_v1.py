"""
HHS Phase-Coherent Operator Loop v1
===================================

Phase-aware consensus + bounded self-improvement loop for operator orchestration.

This version supports an external realtime phase anchor produced by
hhs_realtime_multimodal_phase_integration_v1. When present, the external anchor
is authoritative over the internal AUDIT_AGENT anchor.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_multi_agent_operator_orchestrator_v1 import (
    AgentOperatorProposal,
    ChainConsensusCandidate,
    OperatorAgentSpec,
    OrchestratorStatus,
    build_consensus_candidates,
    default_operator_agents,
    propose_chain,
)
from hhs_runtime.hhs_operator_execution_layer_v1 import build_operator_registry, execute_operator_chain
from hhs_runtime.hhs_operator_selection_engine_v1 import OperatorSelectionGoal
from hhs_runtime.hhs_self_modifying_agents_v1 import EthicalInvariantReceipt, ModificationStatus

PHASE_RING = 72
AGENT_PHASE_TOLERANCE = 1
CONSENSUS_THRESHOLD_NUM = 2
CONSENSUS_THRESHOLD_DEN = 3


class PhaseLoopStatus(str, Enum):
    EXECUTED = "EXECUTED"
    PHASE_STALLED = "PHASE_STALLED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class PhaseWitness:
    subject_hash72: str
    phase_index: int
    phase_hash72: str
    witness_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseAgentProposal:
    proposal: AgentOperatorProposal
    phase_witness: PhaseWitness
    phase_distance_from_anchor: int | None
    phase_ok: bool
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal": self.proposal.to_dict(),
            "phase_witness": self.phase_witness.to_dict(),
            "phase_distance_from_anchor": self.phase_distance_from_anchor,
            "phase_ok": self.phase_ok,
            "receipt_hash72": self.receipt_hash72,
        }


@dataclass(frozen=True)
class FeedbackRecord:
    chain_hash72: str
    operator_hashes: List[str]
    status: str
    replay_valid: bool
    phase_valid: bool
    delta: int
    feedback_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseCoherentLoopReceipt:
    module: str
    input_hash72: str
    goal: OperatorSelectionGoal
    phase_anchor: PhaseWitness | None
    external_phase_anchor_used: bool
    phase_agent_proposals: List[PhaseAgentProposal]
    consensus_candidates: List[ChainConsensusCandidate]
    selected_candidate: ChainConsensusCandidate | None
    feedback_records: List[FeedbackRecord]
    invariant_gate: EthicalInvariantReceipt
    status: PhaseLoopStatus
    quarantine_hash72: str | None
    execution_receipt: Dict[str, Any] | None
    feedback_ledger_commit: Dict[str, Any]
    feedback_replay_receipt: Dict[str, Any]
    loop_ledger_commit: Dict[str, Any]
    loop_replay_receipt: Dict[str, Any]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module": self.module,
            "input_hash72": self.input_hash72,
            "goal": self.goal.to_dict(),
            "phase_anchor": self.phase_anchor.to_dict() if self.phase_anchor else None,
            "external_phase_anchor_used": self.external_phase_anchor_used,
            "phase_agent_proposals": [p.to_dict() for p in self.phase_agent_proposals],
            "consensus_candidates": [c.to_dict() for c in self.consensus_candidates],
            "selected_candidate": self.selected_candidate.to_dict() if self.selected_candidate else None,
            "feedback_records": [f.to_dict() for f in self.feedback_records],
            "invariant_gate": self.invariant_gate.to_dict(),
            "status": self.status.value,
            "quarantine_hash72": self.quarantine_hash72,
            "execution_receipt": self.execution_receipt,
            "feedback_ledger_commit": self.feedback_ledger_commit,
            "feedback_replay_receipt": self.feedback_replay_receipt,
            "loop_ledger_commit": self.loop_ledger_commit,
            "loop_replay_receipt": self.loop_replay_receipt,
            "receipt_hash72": self.receipt_hash72,
        }


def theta15_true() -> bool:
    return (
        all(sum(row) == 15 for row in LO_SHU_3X3)
        and all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
        and sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
        and sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    )


def phase_index_from_hash(value: str) -> int:
    acc = 0
    for ch in value:
        acc = (acc * 131 + ord(ch)) % PHASE_RING
    return acc


def phase_distance(a: int, b: int) -> int:
    delta = abs((a - b) % PHASE_RING)
    return min(delta, PHASE_RING - delta)


def make_phase_witness(subject_hash72: str, salt: str = "") -> PhaseWitness:
    phase_hash = hash72_digest(("phase_witness_v1", subject_hash72, salt), width=24)
    phase_index = phase_index_from_hash(phase_hash)
    witness_hash = hash72_digest(("phase_witness_receipt_v1", subject_hash72, phase_index, phase_hash), width=24)
    return PhaseWitness(subject_hash72, phase_index, phase_hash, witness_hash)


def external_anchor_from_live_phase(phase_lock_receipt: Dict[str, Any] | None) -> PhaseWitness | None:
    if not phase_lock_receipt or phase_lock_receipt.get("status") != "LOCKED":
        return None
    subject = str(phase_lock_receipt.get("receipt_hash72") or phase_lock_receipt.get("anchor_phase_hash72"))
    phase_hash = str(phase_lock_receipt.get("anchor_phase_hash72"))
    phase_index = int(phase_lock_receipt.get("anchor_phase_index"))
    witness_hash = hash72_digest(("external_live_phase_anchor_v1", subject, phase_index, phase_hash), width=24)
    return PhaseWitness(subject, phase_index, phase_hash, witness_hash)


def load_feedback_history(path: str | Path) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    return [block.get("payload", {}) for block in data.get("blocks", []) if isinstance(block.get("payload", {}), dict)]


def history_for_selection(feedback_history: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in feedback_history:
        for op_hash in item.get("operator_hashes", []):
            out.append({"operator_hash72": op_hash, "status": "APPLIED" if item.get("delta", 0) > 0 else "QUARANTINED", "replay_valid": item.get("replay_valid")})
    return out


def phase_wrap_proposals(proposals: Sequence[AgentOperatorProposal], external_anchor: PhaseWitness | None = None) -> List[PhaseAgentProposal]:
    anchor_witness = external_anchor
    raw: List[tuple[AgentOperatorProposal, PhaseWitness]] = []
    for proposal in proposals:
        chain = hash72_digest(("proposal_chain_phase_subject_v1", [op.registry_hash72 for op in proposal.selected_operators]), width=24)
        witness = make_phase_witness(chain, salt=proposal.agent.name)
        raw.append((proposal, witness))
        if anchor_witness is None and proposal.agent.kind.value == "AUDIT_AGENT":
            anchor_witness = witness
    if anchor_witness is None and raw:
        anchor_witness = raw[0][1]
    out: List[PhaseAgentProposal] = []
    for proposal, witness in raw:
        distance = phase_distance(anchor_witness.phase_index, witness.phase_index) if anchor_witness else None
        ok = distance is not None and distance <= AGENT_PHASE_TOLERANCE
        receipt = hash72_digest(("phase_agent_proposal_v1", proposal.proposal_hash72, witness.witness_hash72, anchor_witness.witness_hash72 if anchor_witness else None, distance, ok), width=24)
        out.append(PhaseAgentProposal(proposal, witness, distance, ok, receipt))
    return out


def phase_filtered_consensus(phase_proposals: Sequence[PhaseAgentProposal]) -> List[ChainConsensusCandidate]:
    return build_consensus_candidates([p.proposal for p in phase_proposals if p.phase_ok], CONSENSUS_THRESHOLD_NUM, CONSENSUS_THRESHOLD_DEN)


def invariant_gate_for_phase_loop(input_text: str, goal: OperatorSelectionGoal, selected: ChainConsensusCandidate | None, phase_proposals: Sequence[PhaseAgentProposal], external_anchor_used: bool) -> EthicalInvariantReceipt:
    delta_e_zero = bool(input_text.strip()) and bool(phase_proposals)
    psi_zero = selected is not None and selected.status == OrchestratorStatus.EXECUTED and any(p.phase_ok for p in phase_proposals)
    theta = theta15_true()
    omega_true = bool(hash72_digest(("phase_coherent_loop_closure_v1", input_text, goal.to_dict(), selected.receipt_hash72 if selected else None, [p.receipt_hash72 for p in phase_proposals], external_anchor_used), width=24))
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {"Δe=0": delta_e_zero, "Ψ=0": psi_zero, "Θ15=true": theta, "Ω=true": omega_true, "phase_ok_count": sum(1 for p in phase_proposals if p.phase_ok), "selected_chain": selected.chain_hash72 if selected else None, "external_phase_anchor_used": external_anchor_used}
    receipt = hash72_digest(("phase_coherent_loop_gate_v1", details, status.value), width=24)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


def make_feedback_records(selected: ChainConsensusCandidate | None, execution: Dict[str, Any] | None, phase_valid: bool) -> List[FeedbackRecord]:
    if selected is None:
        return []
    replay_valid = bool(execution and execution.get("replay_receipt", {}).get("invalid") == 0)
    applied = bool(execution and execution.get("status") == "APPLIED" and replay_valid and phase_valid)
    delta = 2 if applied else -3
    status = "APPLIED" if applied else "QUARANTINED"
    op_hashes = [op.registry_hash72 for op in selected.selected_operators]
    feedback_hash = hash72_digest(("operator_feedback_record_v1", selected.chain_hash72, op_hashes, status, replay_valid, phase_valid, delta), width=24)
    return [FeedbackRecord(selected.chain_hash72, op_hashes, status, replay_valid, phase_valid, delta, feedback_hash)]


def run_phase_coherent_operator_loop(input_text: str, canonical_blocks: Sequence[Dict[str, Any] | Any], goal: OperatorSelectionGoal, *, agents: Sequence[OperatorAgentSpec] | None = None, live_phase_lock_receipt: Dict[str, Any] | None = None, feedback_ledger_path: str | Path = "demo_reports/hhs_operator_feedback_ledger_v1.json", loop_ledger_path: str | Path = "demo_reports/hhs_phase_coherent_operator_loop_ledger_v1.json", execution_ledger_path: str | Path = "demo_reports/hhs_phase_coherent_operator_execution_ledger_v1.json") -> PhaseCoherentLoopReceipt:
    registry = build_operator_registry(canonical_blocks)
    selection_history = history_for_selection(load_feedback_history(feedback_ledger_path))
    agent_specs = list(agents or default_operator_agents())
    proposals = [propose_chain(agent, registry, input_text, goal, selection_history) for agent in agent_specs]
    external_anchor = external_anchor_from_live_phase(live_phase_lock_receipt)
    phase_proposals = phase_wrap_proposals(proposals, external_anchor=external_anchor)
    anchor = external_anchor or next((p.phase_witness for p in phase_proposals if p.proposal.agent.kind.value == "AUDIT_AGENT"), phase_proposals[0].phase_witness if phase_proposals else None)
    external_used = external_anchor is not None
    candidates = phase_filtered_consensus(phase_proposals)
    selected = next((c for c in candidates if c.status == OrchestratorStatus.EXECUTED), None)
    gate = invariant_gate_for_phase_loop(input_text, goal, selected, phase_proposals, external_used)
    if gate.status == ModificationStatus.APPLIED and selected is not None:
        execution = execute_operator_chain(input_text, selected.selected_operators, ledger_path=execution_ledger_path).to_dict()
        status = PhaseLoopStatus.EXECUTED
        quarantine = None
    else:
        execution = None
        status = PhaseLoopStatus.PHASE_STALLED if any(not p.phase_ok for p in phase_proposals) else PhaseLoopStatus.QUARANTINED
        quarantine = hash72_digest(("phase_coherent_loop_quarantine_v1", input_text, goal.to_dict(), [p.receipt_hash72 for p in phase_proposals], gate.to_dict(), external_used), width=24)
    phase_valid = status == PhaseLoopStatus.EXECUTED and all(p.phase_ok for p in phase_proposals if p.proposal.agent.name in (selected.supporting_agents if selected else []))
    feedback = make_feedback_records(selected, execution, phase_valid)
    feedback_ledger = MemoryLedger(feedback_ledger_path)
    feedback_commit = feedback_ledger.append_payloads("operator_feedback_record_v1", [f.to_dict() for f in feedback])
    feedback_replay = replay_ledger(feedback_ledger_path)
    payload = {
        "input_hash72": hash72_digest(("phase_coherent_operator_input_v1", input_text), width=24),
        "goal": goal.to_dict(),
        "phase_anchor": anchor.to_dict() if anchor else None,
        "external_phase_anchor_used": external_used,
        "live_phase_lock_receipt_hash72": live_phase_lock_receipt.get("receipt_hash72") if live_phase_lock_receipt else None,
        "phase_proposal_hashes": [p.receipt_hash72 for p in phase_proposals],
        "candidate_hashes": [c.receipt_hash72 for c in candidates],
        "selected_chain_hash72": selected.chain_hash72 if selected else None,
        "feedback_hashes": [f.feedback_hash72 for f in feedback],
        "invariant_gate": gate.to_dict(),
        "status": status.value,
        "quarantine_hash72": quarantine,
        "execution_receipt_hash72": execution.get("receipt_hash72") if execution else None,
    }
    loop_ledger = MemoryLedger(loop_ledger_path)
    loop_commit = loop_ledger.append_payloads("phase_coherent_operator_loop_receipt_v1", [payload])
    loop_replay = replay_ledger(loop_ledger_path)
    receipt = hash72_digest(("phase_coherent_operator_loop_receipt_v1", payload, feedback_commit.receipt_hash72, feedback_replay.receipt_hash72, loop_commit.receipt_hash72, loop_replay.receipt_hash72), width=24)
    return PhaseCoherentLoopReceipt("hhs_phase_coherent_operator_loop_v1", payload["input_hash72"], goal, anchor, external_used, phase_proposals, candidates, selected, feedback, gate, status, quarantine, execution, feedback_commit.to_dict(), feedback_replay.to_dict(), loop_commit.to_dict(), loop_replay.to_dict(), receipt)


def demo() -> Dict[str, Any]:
    from hhs_runtime.hhs_drive_alignment_corpus_ingestor_v2 import ingest_drive_corpus_artifacts
    sample = {"id": "phase_loop_demo", "title": "Phase Loop Demo Corpus", "text": """
# HHS Alignment Axiom
Statement: Preserve Δe=0, Ψ=0, Θ15=true, Ω=true while translating claims.
# Style Operator — Recursive Harmonic Prose
Write with recursive rhythm, controlled repetition, and semantic return. Apply the style without changing the claim.
# Writing Process — Draft Audit Compress Re-expand
Step 1: draft. Step 2: audit for semantic drift. Step 3: compress into an operator. Step 4: re-expand as clear prose.
# Operator Spec — Meaning Preservation
The operator must preserve meaning while transforming medium and style.
"""}
    ingest_drive_corpus_artifacts([sample], ledger_path="demo_reports/hhs_phase_loop_demo_corpus_v1.json")
    blocks = [block["payload"] for block in json.loads(Path("demo_reports/hhs_phase_loop_demo_corpus_v1.json").read_text(encoding="utf-8"))["blocks"]]
    goal = OperatorSelectionGoal("explain a technical alignment claim with harmonic recursive style and process audit", ["LOGIC", "STYLE", "PROCESS"], ["AXIOM", "STYLE_OPERATOR", "WRITING_PROCESS"], 4, True, True, True)
    return run_phase_coherent_operator_loop("The system must preserve meaning while changing form.", blocks, goal).to_dict()


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))

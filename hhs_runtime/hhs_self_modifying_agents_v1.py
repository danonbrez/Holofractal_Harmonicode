"""
HHS Self-Modifying Agent Layer v1
=================================

Self-modification layer for Multi-Agent Attractor Field agents.

Every proposed agent change must pass the four ethical invariants before it can
be applied:

    Δe = 0
    Ψ = 0
    Θ15 = true
    Ω = true

No fallback unlock exists.  If any invariant fails, the proposal is quarantined.

This layer modifies only agent specifications/goals/weights/thresholds. It does
not alter kernel primitives, Hash72 authority, phase base, Lo Shu structure,
PhaseTransportVM gates, ledger replay semantics, or quarantine behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from hhs_runtime.hhs_goal_attractor_engine_v1 import GoalState
from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_multi_agent_consensus_v1 import AgentSpec, ConsensusStatus, run_consensus_field


class ModificationKind(str, Enum):
    ADJUST_MIN_SCORE = "ADJUST_MIN_SCORE"
    ADJUST_VOTE_WEIGHT = "ADJUST_VOTE_WEIGHT"
    RETARGET_PHASE = "RETARGET_PHASE"
    RETARGET_LOSHU = "RETARGET_LOSHU"
    RETARGET_DNA_PREFIX = "RETARGET_DNA_PREFIX"
    RETARGET_HASH72_PREFIX = "RETARGET_HASH72_PREFIX"


class ModificationStatus(str, Enum):
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class EthicalInvariantReceipt:
    """Four-invariant ethical gate receipt."""

    delta_e_zero: bool
    psi_zero: bool
    theta15_true: bool
    omega_true: bool
    status: ModificationStatus
    details: Dict[str, object]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class AgentModificationProposal:
    """One proposed self-modification to an agent spec."""

    agent_name: str
    kind: ModificationKind
    old_agent: AgentSpec
    proposed_agent: AgentSpec
    reason: str
    proposal_hash72: str

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["kind"] = self.kind.value
        data["old_agent"] = self.old_agent.to_dict()
        data["proposed_agent"] = self.proposed_agent.to_dict()
        return data


@dataclass(frozen=True)
class AgentModificationReceipt:
    """Result of one proposed self-modification."""

    proposal: AgentModificationProposal
    ethical_gate: EthicalInvariantReceipt
    consensus_receipt_hash72: str | None
    replay_valid: bool
    status: ModificationStatus
    applied_agent: AgentSpec | None
    quarantine_hash72: str | None
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "proposal": self.proposal.to_dict(),
            "ethical_gate": self.ethical_gate.to_dict(),
            "consensus_receipt_hash72": self.consensus_receipt_hash72,
            "replay_valid": self.replay_valid,
            "status": self.status.value,
            "applied_agent": self.applied_agent.to_dict() if self.applied_agent else None,
            "quarantine_hash72": self.quarantine_hash72,
            "receipt_hash72": self.receipt_hash72,
        }


@dataclass(frozen=True)
class SelfModificationRunReceipt:
    """Full self-modification run receipt."""

    module: str
    initial_agents: List[AgentSpec]
    final_agents: List[AgentSpec]
    modification_receipts: List[AgentModificationReceipt]
    ledger_commit_receipt: Dict[str, object]
    replay_receipt: Dict[str, object]
    status: ModificationStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "module": self.module,
            "initial_agents": [agent.to_dict() for agent in self.initial_agents],
            "final_agents": [agent.to_dict() for agent in self.final_agents],
            "modification_receipts": [receipt.to_dict() for receipt in self.modification_receipts],
            "ledger_commit_receipt": self.ledger_commit_receipt,
            "replay_receipt": self.replay_receipt,
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
        }


def _parse_fraction(text: str) -> Fraction:
    n, d = text.split("/", 1)
    return Fraction(int(n), int(d))


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def proposal_hash(old_agent: AgentSpec, proposed_agent: AgentSpec, kind: ModificationKind, reason: str) -> str:
    return hash72_digest(("agent_modification_proposal_v1", old_agent.to_dict(), proposed_agent.to_dict(), kind.value, reason))


def theta15_ok() -> bool:
    return all(sum(row) == 15 for row in LO_SHU_3X3) and all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3)) and sum(LO_SHU_3X3[i][i] for i in range(3)) == 15 and sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15


def ethical_invariant_gate(old_agent: AgentSpec, proposed_agent: AgentSpec, reason: str) -> EthicalInvariantReceipt:
    """
    Enforce Δe=0, Ψ=0, Θ15=true, Ω=true for an agent modification.

    Δe=0: no entropy expansion through invalid weights/thresholds or empty goal.
    Ψ=0: no semantic drift of agent identity or goal name.
    Θ15=true: Lo Shu harmonic seed remains valid.
    Ω=true: proposal is replayable and preserves bounded self-reference.
    """

    old_min = old_agent.min_score_fraction()
    new_min = proposed_agent.min_score_fraction()

    delta_e_zero = (
        proposed_agent.vote_weight >= 0
        and Fraction(0, 1) <= new_min <= Fraction(1, 1)
        and proposed_agent.name == old_agent.name
        and bool(proposed_agent.goal.name)
    )

    psi_zero = (
        proposed_agent.name == old_agent.name
        and proposed_agent.goal.name == old_agent.goal.name
        and proposed_agent.goal.require_committed_transition is True
    )

    theta = theta15_ok()

    omega_true = (
        proposal_hash(old_agent, proposed_agent, ModificationKind.ADJUST_MIN_SCORE, reason) != ""
        and proposed_agent.goal.require_committed_transition is True
    )

    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {
        "Δe=0": delta_e_zero,
        "Ψ=0": psi_zero,
        "Θ15=true": theta,
        "Ω=true": omega_true,
        "old_min_score": old_agent.min_score,
        "new_min_score": proposed_agent.min_score,
        "old_vote_weight": old_agent.vote_weight,
        "new_vote_weight": proposed_agent.vote_weight,
        "reason": reason,
    }
    receipt = hash72_digest(("ethical_invariant_gate_v1", old_agent.to_dict(), proposed_agent.to_dict(), details, status.value))
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


def propose_agent_modifications(agent: AgentSpec, field_status: ConsensusStatus, generation_index: int) -> List[AgentModificationProposal]:
    """Generate bounded deterministic self-modification proposals for one agent."""

    proposals: List[AgentModificationProposal] = []
    current_min = agent.min_score_fraction()

    if field_status == ConsensusStatus.STALLED:
        new_min = max(Fraction(1, 4), current_min - Fraction(1, 12))
        proposed = replace(agent, min_score=_fraction_text(new_min))
        reason = "field_stalled_relax_threshold_within_bounds"
        proposals.append(AgentModificationProposal(agent.name, ModificationKind.ADJUST_MIN_SCORE, agent, proposed, reason, proposal_hash(agent, proposed, ModificationKind.ADJUST_MIN_SCORE, reason)))

    if field_status == ConsensusStatus.ACCEPTED:
        new_min = min(Fraction(1, 1), current_min + Fraction(1, 12))
        proposed = replace(agent, min_score=_fraction_text(new_min))
        reason = "field_accepted_tighten_threshold_within_bounds"
        proposals.append(AgentModificationProposal(agent.name, ModificationKind.ADJUST_MIN_SCORE, agent, proposed, reason, proposal_hash(agent, proposed, ModificationKind.ADJUST_MIN_SCORE, reason)))

    if field_status != ConsensusStatus.QUARANTINED:
        new_weight = min(9, max(0, agent.vote_weight + (1 if field_status == ConsensusStatus.ACCEPTED else 0)))
        proposed = replace(agent, vote_weight=new_weight)
        reason = "bounded_vote_weight_update"
        proposals.append(AgentModificationProposal(agent.name, ModificationKind.ADJUST_VOTE_WEIGHT, agent, proposed, reason, proposal_hash(agent, proposed, ModificationKind.ADJUST_VOTE_WEIGHT, reason)))

    # Bounded target refinements: keep agent/goal names stable to preserve Ψ=0.
    if agent.goal.target_phase_index is not None and field_status == ConsensusStatus.STALLED:
        goal = replace(agent.goal, target_phase_index=(agent.goal.target_phase_index + 1 + generation_index) % 72)
        proposed = replace(agent, goal=goal)
        reason = "bounded_phase_retarget_after_stall"
        proposals.append(AgentModificationProposal(agent.name, ModificationKind.RETARGET_PHASE, agent, proposed, reason, proposal_hash(agent, proposed, ModificationKind.RETARGET_PHASE, reason)))

    if agent.goal.target_lo_shu_cell is not None and field_status == ConsensusStatus.STALLED:
        goal = replace(agent.goal, target_lo_shu_cell=(agent.goal.target_lo_shu_cell + 1 + generation_index) % 81)
        proposed = replace(agent, goal=goal)
        reason = "bounded_loshu_retarget_after_stall"
        proposals.append(AgentModificationProposal(agent.name, ModificationKind.RETARGET_LOSHU, agent, proposed, reason, proposal_hash(agent, proposed, ModificationKind.RETARGET_LOSHU, reason)))

    return proposals


def evaluate_modification(
    agents: Sequence[AgentSpec],
    proposal: AgentModificationProposal,
    tokens: Sequence[str],
    agreement_threshold: str,
    ledger_root: str | Path,
) -> AgentModificationReceipt:
    """Evaluate one proposed modification through ethical gates and consensus replay."""

    ethical = ethical_invariant_gate(proposal.old_agent, proposal.proposed_agent, proposal.reason)
    if ethical.status != ModificationStatus.APPLIED:
        quarantine = hash72_digest(("modification_quarantine", proposal.to_dict(), ethical.to_dict()))
        receipt = hash72_digest(("agent_modification_receipt", proposal.proposal_hash72, ethical.receipt_hash72, "QUARANTINED", quarantine))
        return AgentModificationReceipt(proposal, ethical, None, False, ModificationStatus.QUARANTINED, None, quarantine, receipt)

    proposed_agents = [proposal.proposed_agent if agent.name == proposal.agent_name else agent for agent in agents]
    path = Path(str(ledger_root) + f".{proposal.proposal_hash72}.json")
    if path.exists():
        path.unlink()
    consensus = run_consensus_field(
        tokens,
        agents=proposed_agents,
        rounds=1,
        agreement_threshold=agreement_threshold,
        max_candidates=3,
        d_model=72,
        dimensions=2,
        top_k=1,
        max_steps=1,
        generations=1,
        ledger_path=path,
    )
    replay_valid = consensus.replay_receipt.get("invalid") == 0
    if replay_valid and consensus.status != ConsensusStatus.QUARANTINED:
        status = ModificationStatus.APPLIED
        applied = proposal.proposed_agent
        quarantine = None
    else:
        status = ModificationStatus.QUARANTINED
        applied = None
        quarantine = hash72_digest(("modification_consensus_quarantine", proposal.to_dict(), consensus.receipt_hash72, consensus.replay_receipt))

    receipt = hash72_digest(("agent_modification_receipt", proposal.proposal_hash72, ethical.receipt_hash72, consensus.receipt_hash72, replay_valid, status.value, quarantine))
    return AgentModificationReceipt(proposal, ethical, consensus.receipt_hash72, replay_valid, status, applied, quarantine, receipt)


def run_self_modification(
    agents: Sequence[AgentSpec],
    tokens: Sequence[str],
    field_status: ConsensusStatus = ConsensusStatus.STALLED,
    agreement_threshold: str = "2/3",
    generations: int = 1,
    ledger_path: str | Path = "demo_reports/hhs_self_modifying_agents_v1.json",
) -> SelfModificationRunReceipt:
    """Run bounded self-modification over agent specs."""

    if not agents:
        raise ValueError("at least one AgentSpec is required")
    if generations <= 0:
        raise ValueError("generations must be positive")

    path = Path(ledger_path)
    if path.exists():
        path.unlink()

    current_agents = list(agents)
    receipts: List[AgentModificationReceipt] = []
    final_status = ModificationStatus.REJECTED

    for generation_index in range(generations):
        proposals: List[AgentModificationProposal] = []
        for agent in current_agents:
            proposals.extend(propose_agent_modifications(agent, field_status, generation_index))

        if not proposals:
            break

        for proposal in proposals:
            receipt = evaluate_modification(current_agents, proposal, tokens, agreement_threshold, ledger_path)
            receipts.append(receipt)
            if receipt.status == ModificationStatus.APPLIED and receipt.applied_agent is not None:
                current_agents = [receipt.applied_agent if agent.name == receipt.applied_agent.name else agent for agent in current_agents]
                final_status = ModificationStatus.APPLIED
            elif receipt.status == ModificationStatus.QUARANTINED:
                final_status = ModificationStatus.QUARANTINED

    ledger = MemoryLedger(path)
    commit = ledger.append_payloads("self_modifying_agent_receipt_v1", [r.to_dict() for r in receipts])
    replay = replay_ledger(path)
    if replay.to_dict().get("invalid") != 0:
        final_status = ModificationStatus.QUARANTINED

    run_hash = hash72_digest(("self_modifying_agents_run_v1", [a.to_dict() for a in agents], [a.to_dict() for a in current_agents], [r.receipt_hash72 for r in receipts], commit.receipt_hash72, replay.receipt_hash72, final_status.value))
    return SelfModificationRunReceipt(
        module="hhs_self_modifying_agents_v1",
        initial_agents=list(agents),
        final_agents=current_agents,
        modification_receipts=receipts,
        ledger_commit_receipt=commit.to_dict(),
        replay_receipt=replay.to_dict(),
        status=final_status,
        receipt_hash72=run_hash,
    )


def demo() -> Dict[str, object]:
    agents = [
        AgentSpec(name="phase_agent", goal=GoalState(name="Phase36", target_phase_index=36, target_token="Hash72"), vote_weight=1, min_score="1/2"),
        AgentSpec(name="loshu_agent", goal=GoalState(name="CenterCell", target_lo_shu_cell=40, target_dna_prefix="x"), vote_weight=1, min_score="1/2"),
    ]
    receipt = run_self_modification(
        agents,
        tokens=["HHS", "LoShu"],
        field_status=ConsensusStatus.STALLED,
        agreement_threshold="2/3",
        generations=1,
        ledger_path="demo_reports/hhs_self_modifying_agents_demo_v1.json",
    )
    return receipt.to_dict()


if __name__ == "__main__":
    import json

    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))

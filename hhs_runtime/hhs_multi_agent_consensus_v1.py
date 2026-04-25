"""
HHS Multi-Agent Attractor Field + Consensus Engine v1
=====================================================

Distributed attractor layer over the HHS evolution stack.

Each agent owns a goal surface and evaluates candidate token states through the
same invariant pipeline. Consensus accepts only candidates that are replay-valid,
not quarantined, and satisfy a field-level agreement threshold.

Pipeline:

    agents -> candidate pool -> per-agent evolution/attractor scoring
    -> consensus vote -> accepted field state or quarantine/stall
    -> ledger append -> replay validation

No agent can bypass the existing kernel path: every candidate is evaluated via
Token Mutation / Attractor / PhaseTransportVM / Ledger / Replay.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from hhs_runtime.hhs_goal_attractor_engine_v1 import GoalState
from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_token_mutation_evolution_v1 import (
    BranchStatus,
    EvolutionRunReceipt,
    generate_candidates,
    run_evolution,
)


class ConsensusStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    STALLED = "STALLED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class AgentSpec:
    """One attractor-field agent."""

    name: str
    goal: GoalState
    vote_weight: int = 1
    min_score: str = "1/2"

    def min_score_fraction(self) -> Fraction:
        n, d = self.min_score.split("/", 1)
        return Fraction(int(n), int(d))

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AgentEvaluationReceipt:
    """One agent's evaluation of one field candidate."""

    agent_name: str
    candidate_tokens: Tuple[str, ...]
    evolution_receipt_hash72: str
    final_tokens: Tuple[str, ...]
    best_score: Fraction
    vote_weight: int
    vote_accept: bool
    replay_valid: bool
    status: ConsensusStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "agent_name": self.agent_name,
            "candidate_tokens": list(self.candidate_tokens),
            "evolution_receipt_hash72": self.evolution_receipt_hash72,
            "final_tokens": list(self.final_tokens),
            "best_score": f"{self.best_score.numerator}/{self.best_score.denominator}",
            "vote_weight": self.vote_weight,
            "vote_accept": self.vote_accept,
            "replay_valid": self.replay_valid,
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
        }


@dataclass(frozen=True)
class ConsensusCandidateReceipt:
    """Consensus receipt for a candidate across all agents."""

    candidate_tokens: Tuple[str, ...]
    agent_evaluations: List[AgentEvaluationReceipt]
    weighted_accept: int
    weighted_total: int
    agreement: Fraction
    status: ConsensusStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "candidate_tokens": list(self.candidate_tokens),
            "agent_evaluations": [ev.to_dict() for ev in self.agent_evaluations],
            "weighted_accept": self.weighted_accept,
            "weighted_total": self.weighted_total,
            "agreement": f"{self.agreement.numerator}/{self.agreement.denominator}",
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
        }


@dataclass(frozen=True)
class ConsensusRoundReceipt:
    """One multi-agent consensus round."""

    round_index: int
    parent_tokens: Tuple[str, ...]
    candidates: List[ConsensusCandidateReceipt]
    selected_tokens: Tuple[str, ...]
    status: ConsensusStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "round_index": self.round_index,
            "parent_tokens": list(self.parent_tokens),
            "candidates": [c.to_dict() for c in self.candidates],
            "selected_tokens": list(self.selected_tokens),
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
        }


@dataclass(frozen=True)
class ConsensusRunReceipt:
    """Full multi-agent field run receipt."""

    module: str
    agents: List[AgentSpec]
    initial_tokens: Tuple[str, ...]
    final_tokens: Tuple[str, ...]
    rounds: List[ConsensusRoundReceipt]
    agreement_threshold: str
    ledger_commit_receipt: Dict[str, object]
    replay_receipt: Dict[str, object]
    status: ConsensusStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "module": self.module,
            "agents": [a.to_dict() for a in self.agents],
            "initial_tokens": list(self.initial_tokens),
            "final_tokens": list(self.final_tokens),
            "rounds": [r.to_dict() for r in self.rounds],
            "agreement_threshold": self.agreement_threshold,
            "ledger_commit_receipt": self.ledger_commit_receipt,
            "replay_receipt": self.replay_receipt,
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
        }


def _best_generation_score(evolution: EvolutionRunReceipt) -> Fraction:
    best = Fraction(0, 1)
    for generation in evolution.generations:
        if generation.selected_score > best:
            best = generation.selected_score
    return best


def _replay_valid(evolution: EvolutionRunReceipt) -> bool:
    return evolution.replay_receipt.get("invalid") == 0


def evaluate_agent_candidate(
    agent: AgentSpec,
    candidate_tokens: Sequence[str],
    round_index: int,
    candidate_index: int,
    d_model: int,
    dimensions: int,
    top_k: int,
    max_steps: int,
    generations: int,
    ledger_root: str | Path,
) -> AgentEvaluationReceipt:
    """Evaluate one candidate under one agent through the existing evolution stack."""

    safe_agent = hash72_digest((agent.name,), width=6)
    ledger_path = Path(str(ledger_root) + f".r{round_index}.c{candidate_index}.{safe_agent}.json")
    if ledger_path.exists():
        ledger_path.unlink()

    evolution = run_evolution(
        candidate_tokens,
        goal=agent.goal,
        generations=generations,
        d_model=d_model,
        dimensions=dimensions,
        top_k=top_k,
        max_steps=max_steps,
        max_candidates=6,
        ledger_path=ledger_path,
    )
    best_score = _best_generation_score(evolution)
    replay_ok = _replay_valid(evolution)
    vote_accept = replay_ok and evolution.status != BranchStatus.QUARANTINED and best_score >= agent.min_score_fraction()
    if not replay_ok or evolution.status == BranchStatus.QUARANTINED:
        status = ConsensusStatus.QUARANTINED
    elif vote_accept:
        status = ConsensusStatus.ACCEPTED
    else:
        status = ConsensusStatus.REJECTED

    receipt = hash72_digest(
        (
            "agent_evaluation_v1",
            agent.to_dict(),
            tuple(candidate_tokens),
            evolution.receipt_hash72,
            tuple(evolution.final_tokens),
            best_score,
            replay_ok,
            vote_accept,
            status.value,
        )
    )
    return AgentEvaluationReceipt(
        agent_name=agent.name,
        candidate_tokens=tuple(candidate_tokens),
        evolution_receipt_hash72=evolution.receipt_hash72,
        final_tokens=evolution.final_tokens,
        best_score=best_score,
        vote_weight=agent.vote_weight,
        vote_accept=vote_accept,
        replay_valid=replay_ok,
        status=status,
        receipt_hash72=receipt,
    )


def consensus_for_candidate(
    agents: Sequence[AgentSpec],
    candidate_tokens: Sequence[str],
    round_index: int,
    candidate_index: int,
    agreement_threshold: Fraction,
    d_model: int,
    dimensions: int,
    top_k: int,
    max_steps: int,
    generations: int,
    ledger_root: str | Path,
) -> ConsensusCandidateReceipt:
    """Run all agent votes for one candidate and compute field agreement."""

    evaluations = [
        evaluate_agent_candidate(
            agent,
            candidate_tokens,
            round_index=round_index,
            candidate_index=candidate_index,
            d_model=d_model,
            dimensions=dimensions,
            top_k=top_k,
            max_steps=max_steps,
            generations=generations,
            ledger_root=ledger_root,
        )
        for agent in agents
    ]
    weighted_total = sum(max(0, ev.vote_weight) for ev in evaluations) or 1
    weighted_accept = sum(ev.vote_weight for ev in evaluations if ev.vote_accept)
    agreement = Fraction(weighted_accept, weighted_total)

    if any(ev.status == ConsensusStatus.QUARANTINED for ev in evaluations):
        status = ConsensusStatus.QUARANTINED
    elif agreement >= agreement_threshold:
        status = ConsensusStatus.ACCEPTED
    else:
        status = ConsensusStatus.REJECTED

    receipt = hash72_digest(
        (
            "consensus_candidate_v1",
            tuple(candidate_tokens),
            [ev.receipt_hash72 for ev in evaluations],
            weighted_accept,
            weighted_total,
            agreement,
            status.value,
        )
    )
    return ConsensusCandidateReceipt(
        candidate_tokens=tuple(candidate_tokens),
        agent_evaluations=evaluations,
        weighted_accept=weighted_accept,
        weighted_total=weighted_total,
        agreement=agreement,
        status=status,
        receipt_hash72=receipt,
    )


def run_consensus_round(
    tokens: Sequence[str],
    agents: Sequence[AgentSpec],
    round_index: int,
    agreement_threshold: Fraction,
    max_candidates: int,
    d_model: int,
    dimensions: int,
    top_k: int,
    max_steps: int,
    generations: int,
    ledger_root: str | Path,
) -> ConsensusRoundReceipt:
    """Generate candidates, evaluate all agents, select consensus winner."""

    generated = generate_candidates(tokens, generation=round_index, max_candidates=max_candidates)
    candidate_token_sets: List[Tuple[str, ...]] = [tuple(tokens)] + [c.mutated_tokens for c in generated]

    candidate_receipts = [
        consensus_for_candidate(
            agents,
            candidate,
            round_index=round_index,
            candidate_index=index,
            agreement_threshold=agreement_threshold,
            d_model=d_model,
            dimensions=dimensions,
            top_k=top_k,
            max_steps=max_steps,
            generations=generations,
            ledger_root=ledger_root,
        )
        for index, candidate in enumerate(candidate_token_sets)
    ]

    accepted = [c for c in candidate_receipts if c.status == ConsensusStatus.ACCEPTED]
    if accepted:
        accepted.sort(key=lambda c: (c.agreement, c.receipt_hash72), reverse=True)
        selected = accepted[0]
        selected_tokens = selected.candidate_tokens
        status = ConsensusStatus.ACCEPTED
    elif any(c.status == ConsensusStatus.QUARANTINED for c in candidate_receipts):
        selected_tokens = tuple(tokens)
        status = ConsensusStatus.QUARANTINED
    else:
        selected_tokens = tuple(tokens)
        status = ConsensusStatus.STALLED

    receipt = hash72_digest(
        (
            "consensus_round_v1",
            round_index,
            tuple(tokens),
            [c.receipt_hash72 for c in candidate_receipts],
            selected_tokens,
            status.value,
        )
    )
    return ConsensusRoundReceipt(
        round_index=round_index,
        parent_tokens=tuple(tokens),
        candidates=candidate_receipts,
        selected_tokens=selected_tokens,
        status=status,
        receipt_hash72=receipt,
    )


def run_consensus_field(
    tokens: Sequence[str],
    agents: Sequence[AgentSpec],
    rounds: int = 2,
    agreement_threshold: str = "2/3",
    max_candidates: int = 6,
    d_model: int = 72,
    dimensions: int = 3,
    top_k: int = 2,
    max_steps: int = 2,
    generations: int = 1,
    ledger_path: str | Path = "demo_reports/hhs_multi_agent_consensus_v1.json",
) -> ConsensusRunReceipt:
    """Run multi-agent attractor-field consensus."""

    if not agents:
        raise ValueError("at least one AgentSpec is required")
    if rounds <= 0:
        raise ValueError("rounds must be positive")

    threshold_num, threshold_den = agreement_threshold.split("/", 1)
    threshold = Fraction(int(threshold_num), int(threshold_den))

    path = Path(ledger_path)
    if path.exists():
        path.unlink()

    current = tuple(tokens) if tokens else ("HHS",)
    round_receipts: List[ConsensusRoundReceipt] = []
    final_status = ConsensusStatus.STALLED

    for round_index in range(rounds):
        round_receipt = run_consensus_round(
            current,
            agents=agents,
            round_index=round_index,
            agreement_threshold=threshold,
            max_candidates=max_candidates,
            d_model=d_model,
            dimensions=dimensions,
            top_k=top_k,
            max_steps=max_steps,
            generations=generations,
            ledger_root=ledger_path,
        )
        round_receipts.append(round_receipt)
        final_status = round_receipt.status
        current = round_receipt.selected_tokens
        if round_receipt.status in (ConsensusStatus.STALLED, ConsensusStatus.QUARANTINED):
            break

    ledger = MemoryLedger(path)
    commit = ledger.append_payloads("multi_agent_consensus_round_v1", [r.to_dict() for r in round_receipts])
    replay = replay_ledger(path)
    run_hash = hash72_digest(
        (
            "multi_agent_consensus_run_v1",
            [a.to_dict() for a in agents],
            tuple(tokens),
            current,
            [r.receipt_hash72 for r in round_receipts],
            agreement_threshold,
            commit.receipt_hash72,
            replay.receipt_hash72,
            final_status.value,
        )
    )
    return ConsensusRunReceipt(
        module="hhs_multi_agent_consensus_v1",
        agents=list(agents),
        initial_tokens=tuple(tokens),
        final_tokens=current,
        rounds=round_receipts,
        agreement_threshold=agreement_threshold,
        ledger_commit_receipt=commit.to_dict(),
        replay_receipt=replay.to_dict(),
        status=final_status,
        receipt_hash72=run_hash,
    )


def demo() -> Dict[str, object]:
    agents = [
        AgentSpec(
            name="phase_agent",
            goal=GoalState(name="Phase36", target_phase_index=36, target_token="Hash72"),
            vote_weight=1,
            min_score="1/2",
        ),
        AgentSpec(
            name="loshu_agent",
            goal=GoalState(name="CenterCell", target_lo_shu_cell=40, target_dna_prefix="x"),
            vote_weight=1,
            min_score="1/2",
        ),
        AgentSpec(
            name="hash_agent",
            goal=GoalState(name="HashToken", target_token="Hash72", target_hash72_prefix="H"),
            vote_weight=1,
            min_score="1/3",
        ),
    ]
    receipt = run_consensus_field(
        ["HHS", "LoShu"],
        agents=agents,
        rounds=1,
        agreement_threshold="2/3",
        max_candidates=4,
        d_model=72,
        dimensions=2,
        top_k=1,
        max_steps=1,
        generations=1,
        ledger_path="demo_reports/hhs_multi_agent_consensus_demo_v1.json",
    )
    return receipt.to_dict()


if __name__ == "__main__":
    import json

    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))

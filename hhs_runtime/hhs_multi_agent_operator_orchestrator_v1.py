"""
HHS Multi-Agent Operator Orchestrator v1
=======================================

Specialist-agent consensus layer for operator selection and execution.

Purpose
-------
Instead of a single selector choosing the operator chain, multiple bounded agents
propose chains from different perspectives:

- LOGIC_AGENT      : axioms, theorem/proof/operator fit
- STYLE_AGENT      : style operators and expression constraints
- PROCESS_AGENT    : workflow/process/template structure
- SYNTHESIS_AGENT  : mixed domain composition
- AUDIT_AGENT      : invariant/replay/quarantine risk

The orchestrator scores proposed chains, requires consensus, then executes only
the selected chain through hhs_operator_execution_layer_v1.

No agent can mutate kernel/state directly. Agents only propose operator chains;
execution remains deterministic and receipt-bound.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple
import json

from hhs_runtime.hhs_drive_alignment_corpus_ingestor_v2 import HHSBlockDomain, HHSBlockKind
from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_operator_execution_layer_v1 import (
    RegisteredOperator,
    build_operator_registry,
    execute_operator_chain,
)
from hhs_runtime.hhs_operator_selection_engine_v1 import (
    OperatorSelectionGoal,
    score_operator,
)
from hhs_runtime.hhs_self_modifying_agents_v1 import EthicalInvariantReceipt, ModificationStatus


class OrchestratorStatus(str, Enum):
    EXECUTED = "EXECUTED"
    STALLED = "STALLED"
    QUARANTINED = "QUARANTINED"


class OperatorAgentKind(str, Enum):
    LOGIC_AGENT = "LOGIC_AGENT"
    STYLE_AGENT = "STYLE_AGENT"
    PROCESS_AGENT = "PROCESS_AGENT"
    SYNTHESIS_AGENT = "SYNTHESIS_AGENT"
    AUDIT_AGENT = "AUDIT_AGENT"


@dataclass(frozen=True)
class OperatorAgentSpec:
    name: str
    kind: OperatorAgentKind
    preferred_domains: List[str]
    preferred_kinds: List[str]
    vote_weight: int
    max_chain_length: int

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


@dataclass(frozen=True)
class AgentOperatorProposal:
    agent: OperatorAgentSpec
    selected_operators: List[RegisteredOperator]
    local_score: int
    risk_score: int
    proposal_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent.to_dict(),
            "selected_operators": [op.to_dict() for op in self.selected_operators],
            "local_score": self.local_score,
            "risk_score": self.risk_score,
            "proposal_hash72": self.proposal_hash72,
        }


@dataclass(frozen=True)
class ChainConsensusCandidate:
    chain_hash72: str
    selected_operators: List[RegisteredOperator]
    supporting_agents: List[str]
    weighted_vote: int
    weighted_total: int
    agreement_num: int
    agreement_den: int
    audit_risk: int
    status: OrchestratorStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain_hash72": self.chain_hash72,
            "selected_operators": [op.to_dict() for op in self.selected_operators],
            "supporting_agents": self.supporting_agents,
            "weighted_vote": self.weighted_vote,
            "weighted_total": self.weighted_total,
            "agreement": f"{self.agreement_num}/{self.agreement_den}",
            "audit_risk": self.audit_risk,
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
        }


@dataclass(frozen=True)
class MultiAgentOrchestrationReceipt:
    module: str
    input_hash72: str
    goal: OperatorSelectionGoal
    agents: List[OperatorAgentSpec]
    proposals: List[AgentOperatorProposal]
    candidates: List[ChainConsensusCandidate]
    selected_candidate: ChainConsensusCandidate | None
    invariant_gate: EthicalInvariantReceipt
    status: OrchestratorStatus
    quarantine_hash72: str | None
    execution_receipt: Dict[str, Any] | None
    ledger_commit_receipt: Dict[str, Any]
    replay_receipt: Dict[str, Any]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module": self.module,
            "input_hash72": self.input_hash72,
            "goal": self.goal.to_dict(),
            "agents": [a.to_dict() for a in self.agents],
            "proposals": [p.to_dict() for p in self.proposals],
            "candidates": [c.to_dict() for c in self.candidates],
            "selected_candidate": self.selected_candidate.to_dict() if self.selected_candidate else None,
            "invariant_gate": self.invariant_gate.to_dict(),
            "status": self.status.value,
            "quarantine_hash72": self.quarantine_hash72,
            "execution_receipt": self.execution_receipt,
            "ledger_commit_receipt": self.ledger_commit_receipt,
            "replay_receipt": self.replay_receipt,
            "receipt_hash72": self.receipt_hash72,
        }


def default_operator_agents() -> List[OperatorAgentSpec]:
    return [
        OperatorAgentSpec("logic_agent", OperatorAgentKind.LOGIC_AGENT, ["LOGIC", "MIXED"], ["AXIOM", "THEOREM", "LEMMA", "OPERATOR", "PROOF", "SPEC"], 5, 3),
        OperatorAgentSpec("style_agent", OperatorAgentKind.STYLE_AGENT, ["STYLE", "MIXED"], ["STYLE_OPERATOR", "STYLE_CONSTRAINT", "CREATIVE_EXAMPLE"], 3, 3),
        OperatorAgentSpec("process_agent", OperatorAgentKind.PROCESS_AGENT, ["PROCESS", "TEMPLATE", "GENERATOR", "EXERCISE", "MIXED"], ["WRITING_PROCESS", "TEMPLATE", "GENERATOR", "EXERCISE"], 3, 3),
        OperatorAgentSpec("synthesis_agent", OperatorAgentKind.SYNTHESIS_AGENT, ["LOGIC", "STYLE", "PROCESS", "MIXED"], ["AXIOM", "STYLE_OPERATOR", "WRITING_PROCESS", "OPERATOR"], 4, 4),
        OperatorAgentSpec("audit_agent", OperatorAgentKind.AUDIT_AGENT, ["LOGIC", "PROCESS", "MIXED"], ["PROOF", "SPEC", "OPERATOR", "WRITING_PROCESS"], 6, 3),
    ]


def theta15_true() -> bool:
    return (
        all(sum(row) == 15 for row in LO_SHU_3X3)
        and all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
        and sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
        and sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    )


def chain_hash(operators: Sequence[RegisteredOperator]) -> str:
    return hash72_digest(("operator_chain_v1", [op.registry_hash72 for op in operators]), width=24)


def _ordered_chain(operators: Sequence[RegisteredOperator], limit: int) -> List[RegisteredOperator]:
    order = {"LOGIC": 0, "PROCESS": 1, "STYLE": 2, "TEMPLATE": 3, "GENERATOR": 4, "EXERCISE": 5, "MIXED": 6}
    unique: Dict[str, RegisteredOperator] = {}
    for op in operators:
        unique[op.registry_hash72] = op
    out = list(unique.values())
    out.sort(key=lambda op: (order.get(op.domain, 9), op.registry_hash72))
    return out[:limit]


def _risk_score(operators: Sequence[RegisteredOperator]) -> int:
    risk = 0
    for op in operators:
        text = " ".join(op.rule_summary).lower()
        if "bypass" in text or "ignore all constraints" in text:
            risk += 10
        if op.kind in {"PROOF", "SPEC", "OPERATOR", "WRITING_PROCESS"}:
            risk -= 1
    return max(0, risk)


def propose_chain(agent: OperatorAgentSpec, registry: Sequence[RegisteredOperator], input_text: str, goal: OperatorSelectionGoal, history: Sequence[Dict[str, Any]] | None = None) -> AgentOperatorProposal:
    local_goal = OperatorSelectionGoal(
        intent=goal.intent,
        preferred_domains=agent.preferred_domains,
        preferred_kinds=agent.preferred_kinds,
        max_chain_length=agent.max_chain_length,
        require_logic=agent.kind in {OperatorAgentKind.LOGIC_AGENT, OperatorAgentKind.AUDIT_AGENT},
        require_style=agent.kind == OperatorAgentKind.STYLE_AGENT,
        require_process=agent.kind == OperatorAgentKind.PROCESS_AGENT,
    )
    scores = [score_operator(op, input_text, local_goal, history) for op in registry]
    scores.sort(key=lambda s: (s.total_score, s.tie_break_hash72), reverse=True)
    selected = _ordered_chain([s.operator for s in scores if s.total_score > 0], agent.max_chain_length)
    local_score = sum(s.total_score for s in scores if s.operator in selected)
    risk = _risk_score(selected)
    h = hash72_digest(("agent_operator_proposal_v1", agent.to_dict(), [op.registry_hash72 for op in selected], local_score, risk), width=24)
    return AgentOperatorProposal(agent, selected, local_score, risk, h)


def build_consensus_candidates(proposals: Sequence[AgentOperatorProposal], agreement_threshold_num: int = 2, agreement_threshold_den: int = 3) -> List[ChainConsensusCandidate]:
    weighted_total = sum(max(0, p.agent.vote_weight) for p in proposals) or 1
    grouped: Dict[str, List[AgentOperatorProposal]] = {}
    chain_ops: Dict[str, List[RegisteredOperator]] = {}
    for proposal in proposals:
        h = chain_hash(proposal.selected_operators)
        grouped.setdefault(h, []).append(proposal)
        chain_ops[h] = proposal.selected_operators
    candidates: List[ChainConsensusCandidate] = []
    for h, supporters in grouped.items():
        vote = sum(max(0, p.agent.vote_weight) for p in supporters)
        risk = max((p.risk_score for p in supporters), default=0)
        accepted = vote * agreement_threshold_den >= agreement_threshold_num * weighted_total and risk == 0 and bool(chain_ops[h])
        status = OrchestratorStatus.EXECUTED if accepted else OrchestratorStatus.STALLED
        receipt = hash72_digest(("chain_consensus_candidate_v1", h, [p.proposal_hash72 for p in supporters], vote, weighted_total, risk, status.value), width=24)
        candidates.append(ChainConsensusCandidate(h, chain_ops[h], [p.agent.name for p in supporters], vote, weighted_total, vote, weighted_total, risk, status, receipt))
    candidates.sort(key=lambda c: (c.status == OrchestratorStatus.EXECUTED, c.weighted_vote, c.receipt_hash72), reverse=True)
    return candidates


def invariant_gate_for_orchestration(input_text: str, goal: OperatorSelectionGoal, selected: ChainConsensusCandidate | None) -> EthicalInvariantReceipt:
    delta_e_zero = bool(input_text.strip()) and goal.max_chain_length > 0
    psi_zero = selected is not None and selected.status == OrchestratorStatus.EXECUTED and bool(selected.selected_operators)
    theta = theta15_true()
    omega_true = bool(hash72_digest(("multi_agent_operator_orchestration_closure_v1", input_text, goal.to_dict(), selected.receipt_hash72 if selected else None), width=24))
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {"Δe=0": delta_e_zero, "Ψ=0": psi_zero, "Θ15=true": theta, "Ω=true": omega_true, "selected_chain": selected.chain_hash72 if selected else None}
    receipt = hash72_digest(("multi_agent_operator_orchestration_gate_v1", details, status.value), width=24)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


def orchestrate_operator_execution(
    input_text: str,
    canonical_blocks: Sequence[Dict[str, Any] | Any],
    goal: OperatorSelectionGoal,
    *,
    agents: Sequence[OperatorAgentSpec] | None = None,
    history: Sequence[Dict[str, Any]] | None = None,
    orchestration_ledger_path: str | Path = "demo_reports/hhs_multi_agent_operator_orchestration_ledger_v1.json",
    execution_ledger_path: str | Path = "demo_reports/hhs_multi_agent_operator_execution_ledger_v1.json",
) -> MultiAgentOrchestrationReceipt:
    registry = build_operator_registry(canonical_blocks)
    agent_specs = list(agents or default_operator_agents())
    proposals = [propose_chain(agent, registry, input_text, goal, history) for agent in agent_specs]
    candidates = build_consensus_candidates(proposals)
    selected = next((c for c in candidates if c.status == OrchestratorStatus.EXECUTED), None)
    gate = invariant_gate_for_orchestration(input_text, goal, selected)
    if gate.status == ModificationStatus.APPLIED and selected is not None:
        execution = execute_operator_chain(input_text, selected.selected_operators, ledger_path=execution_ledger_path).to_dict()
        status = OrchestratorStatus.EXECUTED
        quarantine = None
    else:
        execution = None
        status = OrchestratorStatus.QUARANTINED if proposals else OrchestratorStatus.STALLED
        quarantine = hash72_digest(("multi_agent_operator_orchestration_quarantine_v1", input_text, goal.to_dict(), [p.proposal_hash72 for p in proposals], gate.to_dict()), width=24)

    payload = {
        "input_hash72": hash72_digest(("multi_agent_operator_input_v1", input_text), width=24),
        "goal": goal.to_dict(),
        "agent_hashes": [hash72_digest(("operator_agent_spec", a.to_dict()), width=18) for a in agent_specs],
        "proposal_hashes": [p.proposal_hash72 for p in proposals],
        "candidate_hashes": [c.receipt_hash72 for c in candidates],
        "selected_chain_hash72": selected.chain_hash72 if selected else None,
        "invariant_gate": gate.to_dict(),
        "status": status.value,
        "quarantine_hash72": quarantine,
        "execution_receipt_hash72": execution.get("receipt_hash72") if execution else None,
    }
    ledger = MemoryLedger(orchestration_ledger_path)
    commit = ledger.append_payloads("multi_agent_operator_orchestration_receipt_v1", [payload])
    replay = replay_ledger(orchestration_ledger_path)
    receipt = hash72_digest(("multi_agent_operator_orchestration_receipt_v1", payload, commit.receipt_hash72, replay.receipt_hash72), width=24)
    return MultiAgentOrchestrationReceipt(
        module="hhs_multi_agent_operator_orchestrator_v1",
        input_hash72=payload["input_hash72"],
        goal=goal,
        agents=agent_specs,
        proposals=proposals,
        candidates=candidates,
        selected_candidate=selected,
        invariant_gate=gate,
        status=status,
        quarantine_hash72=quarantine,
        execution_receipt=execution,
        ledger_commit_receipt=commit.to_dict(),
        replay_receipt=replay.to_dict(),
        receipt_hash72=receipt,
    )


def demo() -> Dict[str, Any]:
    from hhs_runtime.hhs_drive_alignment_corpus_ingestor_v2 import ingest_drive_corpus_artifacts

    sample = {
        "id": "orchestration_demo",
        "title": "Orchestration Demo Corpus",
        "text": """
# HHS Alignment Axiom
Statement: Preserve Δe=0, Ψ=0, Θ15=true, Ω=true while translating claims.

# Style Operator — Recursive Harmonic Prose
Write with recursive rhythm, controlled repetition, and semantic return. Apply the style without changing the claim.

# Writing Process — Draft Audit Compress Re-expand
Step 1: draft. Step 2: audit for semantic drift. Step 3: compress into an operator. Step 4: re-expand as clear prose.

# Operator Spec — Meaning Preservation
The operator must preserve meaning while transforming medium and style.
""",
    }
    ingest_drive_corpus_artifacts([sample], ledger_path="demo_reports/hhs_multi_agent_orchestration_demo_corpus_v1.json")
    ledger_data = json.loads(Path("demo_reports/hhs_multi_agent_orchestration_demo_corpus_v1.json").read_text(encoding="utf-8"))
    blocks = [block["payload"] for block in ledger_data["blocks"]]
    goal = OperatorSelectionGoal(
        intent="explain a technical alignment claim with harmonic recursive style and process audit",
        preferred_domains=["LOGIC", "STYLE", "PROCESS"],
        preferred_kinds=["AXIOM", "STYLE_OPERATOR", "WRITING_PROCESS"],
        max_chain_length=4,
        require_logic=True,
        require_style=True,
        require_process=True,
    )
    return orchestrate_operator_execution("The system must preserve meaning while changing form.", blocks, goal, orchestration_ledger_path="demo_reports/hhs_multi_agent_orchestration_demo_v1.json", execution_ledger_path="demo_reports/hhs_multi_agent_orchestration_execution_demo_v1.json").to_dict()


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))

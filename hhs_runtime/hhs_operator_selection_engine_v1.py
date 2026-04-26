"""
HHS Operator Selection Engine v1
================================

Autonomous selection layer for HHS operator execution.

Purpose
-------
Given an input artifact, goal, and canonical HHS corpus blocks, select the best
logic/style/process/operator chain and execute it through the deterministic
operator execution layer.

Selection signals
-----------------
- domain fit
- kind fit
- keyword relevance
- operator signature fit
- source/title fit
- optional historical success feedback
- phase-stable deterministic tie-breaking via Hash72

No selected operator can mutate kernel/state directly.  The selected chain is
passed to hhs_operator_execution_layer_v1, which emits a Hash72 receipt and
ledger replay proof.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Sequence
import json
import re

from hhs_runtime.hhs_drive_alignment_corpus_ingestor_v2 import HHSBlockDomain, HHSBlockKind
from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_operator_execution_layer_v1 import (
    RegisteredOperator,
    build_operator_registry,
    execute_operator_chain,
)
from hhs_runtime.hhs_self_modifying_agents_v1 import EthicalInvariantReceipt, ModificationStatus


class SelectionStatus(str, Enum):
    SELECTED = "SELECTED"
    NO_MATCH = "NO_MATCH"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class OperatorSelectionGoal:
    intent: str
    preferred_domains: List[str]
    preferred_kinds: List[str]
    max_chain_length: int = 4
    require_logic: bool = True
    require_style: bool = False
    require_process: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OperatorScore:
    operator: RegisteredOperator
    domain_score: int
    kind_score: int
    keyword_score: int
    signature_score: int
    history_score: int
    tie_break_hash72: str
    total_score: int
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operator": self.operator.to_dict(),
            "domain_score": self.domain_score,
            "kind_score": self.kind_score,
            "keyword_score": self.keyword_score,
            "signature_score": self.signature_score,
            "history_score": self.history_score,
            "tie_break_hash72": self.tie_break_hash72,
            "total_score": self.total_score,
            "receipt_hash72": self.receipt_hash72,
        }


@dataclass(frozen=True)
class OperatorSelectionReceipt:
    module: str
    input_hash72: str
    goal: OperatorSelectionGoal
    registry_count: int
    scored_count: int
    selected_operators: List[RegisteredOperator]
    scores: List[OperatorScore]
    invariant_gate: EthicalInvariantReceipt
    status: SelectionStatus
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
            "registry_count": self.registry_count,
            "scored_count": self.scored_count,
            "selected_operators": [op.to_dict() for op in self.selected_operators],
            "scores": [score.to_dict() for score in self.scores],
            "invariant_gate": self.invariant_gate.to_dict(),
            "status": self.status.value,
            "quarantine_hash72": self.quarantine_hash72,
            "execution_receipt": self.execution_receipt,
            "ledger_commit_receipt": self.ledger_commit_receipt,
            "replay_receipt": self.replay_receipt,
            "receipt_hash72": self.receipt_hash72,
        }


def theta15_true() -> bool:
    return (
        all(sum(row) == 15 for row in LO_SHU_3X3)
        and all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
        and sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
        and sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    )


def tokenize_query(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[A-Za-z0-9_ΔΨΩΘ]+", text) if len(t) >= 2}


def history_score_for_operator(op: RegisteredOperator, history: Sequence[Dict[str, Any]] | None = None) -> int:
    score = 0
    for item in history or []:
        if item.get("operator_hash72") != op.registry_hash72 and item.get("canonical_hash72") != op.canonical_hash72:
            continue
        if item.get("status") in {"APPLIED", "ACCEPTED", "VALID"}:
            score += 3
        if item.get("status") in {"QUARANTINED", "INVALID"}:
            score -= 5
        if item.get("replay_valid") is True:
            score += 2
        if item.get("replay_valid") is False:
            score -= 3
    return score


def score_operator(op: RegisteredOperator, input_text: str, goal: OperatorSelectionGoal, history: Sequence[Dict[str, Any]] | None = None) -> OperatorScore:
    goal_tokens = tokenize_query(goal.intent)
    input_tokens = tokenize_query(input_text)
    op_text = " ".join([op.title, op.operator_signature, op.applicability_domain, op.source_title, " ".join(op.rule_summary)])
    op_tokens = tokenize_query(op_text)

    preferred_domains = {d.upper() for d in goal.preferred_domains}
    preferred_kinds = {k.upper() for k in goal.preferred_kinds}
    domain_score = 20 if op.domain.upper() in preferred_domains else 0
    kind_score = 12 if op.kind.upper() in preferred_kinds else 0
    keyword_score = 2 * len((goal_tokens | input_tokens) & op_tokens)
    signature_score = 6 if any(tok in op.operator_signature.lower() for tok in goal_tokens) else 0
    hist = history_score_for_operator(op, history)
    tie = hash72_digest(("operator_selection_tie_v1", op.registry_hash72, input_text, goal.to_dict()), width=18)
    total = domain_score + kind_score + keyword_score + signature_score + hist
    receipt = hash72_digest(("operator_score_v1", op.registry_hash72, domain_score, kind_score, keyword_score, signature_score, hist, total, tie), width=24)
    return OperatorScore(op, domain_score, kind_score, keyword_score, signature_score, hist, tie, total, receipt)


def _domain_present(selected: Sequence[RegisteredOperator], domain: str) -> bool:
    return any(op.domain.upper() == domain.upper() for op in selected)


def select_operator_chain(registry: Sequence[RegisteredOperator], input_text: str, goal: OperatorSelectionGoal, history: Sequence[Dict[str, Any]] | None = None) -> tuple[List[RegisteredOperator], List[OperatorScore]]:
    scores = [score_operator(op, input_text, goal, history) for op in registry]
    scores.sort(key=lambda s: (s.total_score, s.tie_break_hash72), reverse=True)
    selected: List[RegisteredOperator] = []

    # First satisfy hard domain requirements, then fill by global score.
    required_domains: List[str] = []
    if goal.require_logic:
        required_domains.append(HHSBlockDomain.LOGIC.value)
    if goal.require_style:
        required_domains.append(HHSBlockDomain.STYLE.value)
    if goal.require_process:
        required_domains.append(HHSBlockDomain.PROCESS.value)

    for domain in required_domains:
        for score in scores:
            if score.operator in selected:
                continue
            if score.operator.domain == domain:
                selected.append(score.operator)
                break

    for score in scores:
        if len(selected) >= goal.max_chain_length:
            break
        if score.operator not in selected and score.total_score > 0:
            selected.append(score.operator)

    # Stable order: logic -> process -> style -> template/generator/exercise -> rest.
    order = {"LOGIC": 0, "PROCESS": 1, "STYLE": 2, "TEMPLATE": 3, "GENERATOR": 4, "EXERCISE": 5, "MIXED": 6}
    selected.sort(key=lambda op: (order.get(op.domain, 9), op.registry_hash72))
    return selected, scores


def invariant_gate_for_selection(input_text: str, goal: OperatorSelectionGoal, selected: Sequence[RegisteredOperator]) -> EthicalInvariantReceipt:
    delta_e_zero = bool(input_text.strip()) and goal.max_chain_length > 0 and len(selected) <= goal.max_chain_length
    psi_zero = bool(selected) and (not goal.require_logic or _domain_present(selected, HHSBlockDomain.LOGIC.value))
    if goal.require_style:
        psi_zero = psi_zero and _domain_present(selected, HHSBlockDomain.STYLE.value)
    if goal.require_process:
        psi_zero = psi_zero and _domain_present(selected, HHSBlockDomain.PROCESS.value)
    theta = theta15_true()
    omega_true = bool(hash72_digest(("operator_selection_closure_v1", input_text, goal.to_dict(), [op.registry_hash72 for op in selected]), width=24))
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {"Δe=0": delta_e_zero, "Ψ=0": psi_zero, "Θ15=true": theta, "Ω=true": omega_true, "selected_count": len(selected), "required_logic": goal.require_logic, "required_style": goal.require_style, "required_process": goal.require_process}
    receipt = hash72_digest(("operator_selection_invariant_gate_v1", details, status.value), width=24)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


def select_and_execute(
    input_text: str,
    canonical_blocks: Sequence[Dict[str, Any] | Any],
    goal: OperatorSelectionGoal,
    *,
    history: Sequence[Dict[str, Any]] | None = None,
    selection_ledger_path: str | Path = "demo_reports/hhs_operator_selection_ledger_v1.json",
    execution_ledger_path: str | Path = "demo_reports/hhs_operator_execution_ledger_v1.json",
) -> OperatorSelectionReceipt:
    registry = build_operator_registry(canonical_blocks)
    selected, scores = select_operator_chain(registry, input_text, goal, history)
    gate = invariant_gate_for_selection(input_text, goal, selected)
    if gate.status == ModificationStatus.APPLIED:
        execution = execute_operator_chain(input_text, selected, ledger_path=execution_ledger_path).to_dict()
        status = SelectionStatus.SELECTED
        quarantine = None
    elif not selected:
        execution = None
        status = SelectionStatus.NO_MATCH
        quarantine = None
    else:
        execution = None
        status = SelectionStatus.QUARANTINED
        quarantine = hash72_digest(("operator_selection_quarantine_v1", input_text, goal.to_dict(), [op.registry_hash72 for op in selected], gate.to_dict()), width=24)

    payload = {
        "input_hash72": hash72_digest(("operator_selection_input_v1", input_text), width=24),
        "goal": goal.to_dict(),
        "registry_count": len(registry),
        "selected": [op.to_dict() for op in selected],
        "score_receipts": [s.receipt_hash72 for s in scores],
        "invariant_gate": gate.to_dict(),
        "status": status.value,
        "quarantine_hash72": quarantine,
        "execution_receipt_hash72": execution.get("receipt_hash72") if execution else None,
    }
    ledger = MemoryLedger(selection_ledger_path)
    commit = ledger.append_payloads("operator_selection_receipt_v1", [payload])
    replay = replay_ledger(selection_ledger_path)
    receipt_hash = hash72_digest(("operator_selection_receipt_v1", payload, commit.receipt_hash72, replay.receipt_hash72), width=24)
    return OperatorSelectionReceipt(
        module="hhs_operator_selection_engine_v1",
        input_hash72=payload["input_hash72"],
        goal=goal,
        registry_count=len(registry),
        scored_count=len(scores),
        selected_operators=selected,
        scores=scores,
        invariant_gate=gate,
        status=status,
        quarantine_hash72=quarantine,
        execution_receipt=execution,
        ledger_commit_receipt=commit.to_dict(),
        replay_receipt=replay.to_dict(),
        receipt_hash72=receipt_hash,
    )


def demo() -> Dict[str, Any]:
    from hhs_runtime.hhs_drive_alignment_corpus_ingestor_v2 import ingest_drive_corpus_artifacts

    sample = {
        "id": "selection_demo",
        "title": "Selection Demo Corpus",
        "text": """
# HHS Alignment Axiom
Statement: Preserve Δe=0, Ψ=0, Θ15=true, Ω=true while translating claims.

# Style Operator — Recursive Harmonic Prose
Write with recursive rhythm, controlled repetition, and semantic return. Apply the style without changing the claim.

# Writing Process — Draft Audit Compress Re-expand
Step 1: draft. Step 2: audit for semantic drift. Step 3: compress into an operator. Step 4: re-expand as clear prose.
""",
    }
    ingest_drive_corpus_artifacts([sample], ledger_path="demo_reports/hhs_operator_selection_demo_corpus_v1.json")
    ledger_data = json.loads(Path("demo_reports/hhs_operator_selection_demo_corpus_v1.json").read_text(encoding="utf-8"))
    blocks = [block["payload"] for block in ledger_data["blocks"]]
    goal = OperatorSelectionGoal(
        intent="explain a technical alignment claim with harmonic recursive style and process audit",
        preferred_domains=["LOGIC", "STYLE", "PROCESS"],
        preferred_kinds=["AXIOM", "STYLE_OPERATOR", "WRITING_PROCESS"],
        max_chain_length=3,
        require_logic=True,
        require_style=True,
        require_process=True,
    )
    return select_and_execute("The system must preserve meaning while changing form.", blocks, goal, selection_ledger_path="demo_reports/hhs_operator_selection_demo_v1.json", execution_ledger_path="demo_reports/hhs_operator_selection_execution_demo_v1.json").to_dict()


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))

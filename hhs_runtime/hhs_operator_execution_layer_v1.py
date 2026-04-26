"""
HHS Operator Execution Layer v1
===============================

Active runtime layer for canonical HHS corpus blocks.

Purpose
-------
Convert canonical corpus blocks from the Drive alignment/creative ingestor into
reusable deterministic transformations.

This is intentionally not an LLM generator.  It is a Hash72-receipted operator
application engine that composes:

    logic block + style block + process block

into an invariant-preserving transformation trace.

Pipeline
--------
    CanonicalHHSBlock records
    -> operator registry
    -> operator selection by domain/kind/signature
    -> deterministic application to content
    -> invariant gate Δe=0, Ψ=0, Θ15=true, Ω=true
    -> append-only execution ledger + replay receipt

No operator may mutate kernel/state directly.  It emits transformed artifacts and
receipts only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Sequence
import json
import re

from hhs_runtime.hhs_drive_alignment_corpus_ingestor_v2 import (
    CanonicalHHSBlock,
    HHSBlockDomain,
    HHSBlockKind,
    HHSIngestStatus,
)
from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_self_modifying_agents_v1 import EthicalInvariantReceipt, ModificationStatus


class OperatorExecutionStatus(str, Enum):
    APPLIED = "APPLIED"
    QUARANTINED = "QUARANTINED"
    NO_MATCH = "NO_MATCH"


@dataclass(frozen=True)
class RegisteredOperator:
    canonical_hash72: str
    domain: str
    kind: str
    title: str
    operator_signature: str
    applicability_domain: str
    body_hash72: str
    rule_summary: List[str]
    source_title: str
    registry_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OperatorApplication:
    operator: RegisteredOperator
    input_hash72: str
    output_text: str
    output_hash72: str
    transform_notes: List[str]
    application_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OperatorExecutionReceipt:
    module: str
    input_text: str
    input_hash72: str
    applications: List[OperatorApplication]
    final_output: str
    final_output_hash72: str
    invariant_gate: EthicalInvariantReceipt
    status: OperatorExecutionStatus
    quarantine_hash72: str | None
    ledger_commit_receipt: Dict[str, Any]
    replay_receipt: Dict[str, Any]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module": self.module,
            "input_text": self.input_text,
            "input_hash72": self.input_hash72,
            "applications": [app.to_dict() for app in self.applications],
            "final_output": self.final_output,
            "final_output_hash72": self.final_output_hash72,
            "invariant_gate": self.invariant_gate.to_dict(),
            "status": self.status.value,
            "quarantine_hash72": self.quarantine_hash72,
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


def _extract_rule_summary(text: str, limit: int = 8) -> List[str]:
    lines = [line.strip(" -\t") for line in text.splitlines() if line.strip()]
    candidates: List[str] = []
    for line in lines:
        lower = line.lower()
        if any(marker in lower for marker in ["must", "should", "apply", "write", "step", "constraint", "invariant", "style", "process", "operator", "rule"]):
            candidates.append(line[:240])
    if not candidates:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        candidates = [s[:240] for s in sentences if s.strip()]
    return candidates[:limit]


def _block_to_operator(block: CanonicalHHSBlock) -> RegisteredOperator | None:
    if block.status != HHSIngestStatus.ACCEPTED:
        return None
    c = block.candidate
    rules = _extract_rule_summary(c.body)
    registry_hash = hash72_digest(("registered_hhs_operator_v1", block.canonical_hash72, c.domain.value, c.kind.value, c.operator_signature, c.body_hash72, rules), width=24)
    return RegisteredOperator(
        canonical_hash72=block.canonical_hash72,
        domain=c.domain.value,
        kind=c.kind.value,
        title=c.title,
        operator_signature=c.operator_signature,
        applicability_domain=c.applicability_domain,
        body_hash72=c.body_hash72,
        rule_summary=rules,
        source_title=c.source_title,
        registry_hash72=registry_hash,
    )


def build_operator_registry(blocks: Sequence[CanonicalHHSBlock | Dict[str, Any]]) -> List[RegisteredOperator]:
    registry: List[RegisteredOperator] = []
    for raw in blocks:
        block = _coerce_block(raw)
        op = _block_to_operator(block)
        if op is not None:
            registry.append(op)
    return registry


def _coerce_block(raw: CanonicalHHSBlock | Dict[str, Any]) -> CanonicalHHSBlock:
    if isinstance(raw, CanonicalHHSBlock):
        return raw
    # Rehydrate enough of the dataclass shape for registry construction.
    from hhs_runtime.hhs_drive_alignment_corpus_ingestor_v2 import (
        CanonicalHHSBlock as CHB,
        CreativeCoherenceReceipt,
        DriveSourceArtifact,
        HHSCandidateBlock,
    )

    cand = raw["candidate"]
    candidate = HHSCandidateBlock(
        source_id=cand["source_id"],
        source_title=cand["source_title"],
        ordinal=int(cand["ordinal"]),
        domain=HHSBlockDomain(cand["domain"]),
        kind=HHSBlockKind(cand["kind"]),
        title=cand["title"],
        body=cand["body"],
        relevance_score=int(cand["relevance_score"]),
        operator_signature=cand["operator_signature"],
        applicability_domain=cand["applicability_domain"],
        source_hash72=cand["source_hash72"],
        body_hash72=cand["body_hash72"],
        block_hash72=cand["block_hash72"],
    )
    inv = raw["invariant_gate"]
    invariant = EthicalInvariantReceipt(
        delta_e_zero=bool(inv["delta_e_zero"]),
        psi_zero=bool(inv["psi_zero"]),
        theta15_true=bool(inv["theta15_true"]),
        omega_true=bool(inv["omega_true"]),
        status=ModificationStatus(inv["status"]),
        details=dict(inv["details"]),
        receipt_hash72=inv["receipt_hash72"],
    )
    creative_raw = raw.get("creative_gate")
    creative = None
    if creative_raw:
        creative = CreativeCoherenceReceipt(
            structural_consistency=bool(creative_raw["structural_consistency"]),
            reusable_operator=bool(creative_raw["reusable_operator"]),
            transformable=bool(creative_raw["transformable"]),
            non_drift=bool(creative_raw["non_drift"]),
            status=ModificationStatus(creative_raw["status"]),
            details=dict(creative_raw["details"]),
            receipt_hash72=creative_raw["receipt_hash72"],
        )
    return CHB(candidate, invariant, creative, HHSIngestStatus(raw["status"]), raw["canonical_hash72"], raw.get("quarantine_hash72"))


def select_operators(registry: Sequence[RegisteredOperator], domains: Sequence[str] | None = None, kinds: Sequence[str] | None = None, limit: int = 6) -> List[RegisteredOperator]:
    domains_set = {d.upper() for d in domains} if domains else None
    kinds_set = {k.upper() for k in kinds} if kinds else None
    selected: List[RegisteredOperator] = []
    for op in registry:
        if domains_set and op.domain.upper() not in domains_set:
            continue
        if kinds_set and op.kind.upper() not in kinds_set:
            continue
        selected.append(op)
    return selected[:limit]


def _apply_logic_operator(text: str, op: RegisteredOperator) -> tuple[str, List[str]]:
    notes = ["logic operator applied as invariant-preserving frame"]
    header = f"[LOGIC:{op.title}]"
    rule_text = " | ".join(op.rule_summary[:3])
    output = f"{header}\nInvariant frame: {rule_text}\n\n{text}"
    return output, notes


def _apply_style_operator(text: str, op: RegisteredOperator) -> tuple[str, List[str]]:
    notes = ["style operator applied without changing claim content"]
    rules = "; ".join(op.rule_summary[:4])
    output = (
        f"[STYLE:{op.title}]\n"
        f"Style constraints: {rules}\n\n"
        f"{text}\n\n"
        f"Style audit: preserve meaning, increase rhythmic coherence, avoid semantic drift."
    )
    return output, notes


def _apply_process_operator(text: str, op: RegisteredOperator) -> tuple[str, List[str]]:
    notes = ["process operator applied as staged transformation trace"]
    steps = op.rule_summary[:5] or ["draft", "audit", "compress", "re-expand"]
    numbered = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(steps))
    output = f"[PROCESS:{op.title}]\nProcess trace:\n{numbered}\n\nWorking artifact:\n{text}"
    return output, notes


def _apply_template_or_generator(text: str, op: RegisteredOperator) -> tuple[str, List[str]]:
    notes = ["template/generator operator applied as structured wrapper"]
    output = f"[{op.kind}:{op.title}]\nSeed:\n{text}\n\nGenerated structure constraints:\n" + "\n".join(f"- {r}" for r in op.rule_summary[:6])
    return output, notes


def apply_operator(text: str, op: RegisteredOperator) -> OperatorApplication:
    input_hash = hash72_digest(("operator_input_v1", text), width=24)
    if op.domain == HHSBlockDomain.LOGIC.value or op.kind in {HHSBlockKind.AXIOM.value, HHSBlockKind.THEOREM.value, HHSBlockKind.OPERATOR.value, HHSBlockKind.PROOF.value}:
        output, notes = _apply_logic_operator(text, op)
    elif op.domain == HHSBlockDomain.STYLE.value or op.kind in {HHSBlockKind.STYLE_OPERATOR.value, HHSBlockKind.STYLE_CONSTRAINT.value, HHSBlockKind.CREATIVE_EXAMPLE.value}:
        output, notes = _apply_style_operator(text, op)
    elif op.domain == HHSBlockDomain.PROCESS.value or op.kind == HHSBlockKind.WRITING_PROCESS.value:
        output, notes = _apply_process_operator(text, op)
    else:
        output, notes = _apply_template_or_generator(text, op)
    output_hash = hash72_digest(("operator_output_v1", output), width=24)
    app_hash = hash72_digest(("operator_application_v1", op.registry_hash72, input_hash, output_hash, notes), width=24)
    return OperatorApplication(op, input_hash, output, output_hash, notes, app_hash)


def invariant_gate_for_execution(input_text: str, final_output: str, applications: Sequence[OperatorApplication]) -> EthicalInvariantReceipt:
    delta_e_zero = bool(input_text.strip()) and bool(final_output.strip()) and len(final_output) < max(4096, len(input_text) * 20)
    psi_zero = bool(applications) and input_text.strip() in final_output
    theta = theta15_true()
    omega_true = bool(hash72_digest(("operator_execution_closure_v1", input_text, final_output, [a.application_hash72 for a in applications]), width=24))
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {"Δe=0": delta_e_zero, "Ψ=0": psi_zero, "Θ15=true": theta, "Ω=true": omega_true, "application_count": len(applications)}
    receipt = hash72_digest(("operator_execution_invariant_gate_v1", details, status.value), width=24)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


def execute_operator_chain(input_text: str, operators: Sequence[RegisteredOperator], *, ledger_path: str | Path = "demo_reports/hhs_operator_execution_ledger_v1.json") -> OperatorExecutionReceipt:
    applications: List[OperatorApplication] = []
    current = input_text
    for op in operators:
        app = apply_operator(current, op)
        applications.append(app)
        current = app.output_text
    final_hash = hash72_digest(("operator_execution_final_output_v1", current), width=24)
    gate = invariant_gate_for_execution(input_text, current, applications)
    status = OperatorExecutionStatus.APPLIED if gate.status == ModificationStatus.APPLIED else OperatorExecutionStatus.QUARANTINED
    quarantine = None if status == OperatorExecutionStatus.APPLIED else hash72_digest(("operator_execution_quarantine_v1", input_text, current, gate.to_dict()), width=24)
    ledger = MemoryLedger(ledger_path)
    payload = {"input_hash72": hash72_digest(("operator_input_v1", input_text), width=24), "applications": [a.to_dict() for a in applications], "final_output_hash72": final_hash, "invariant_gate": gate.to_dict(), "status": status.value, "quarantine_hash72": quarantine}
    commit = ledger.append_payloads("operator_execution_receipt_v1", [payload])
    replay = replay_ledger(ledger_path)
    receipt = hash72_digest(("operator_execution_receipt_v1", payload, commit.receipt_hash72, replay.receipt_hash72), width=24)
    return OperatorExecutionReceipt("hhs_operator_execution_layer_v1", input_text, payload["input_hash72"], applications, current, final_hash, gate, status, quarantine, commit.to_dict(), replay.to_dict(), receipt)


def execute_from_canonical_blocks(input_text: str, blocks: Sequence[CanonicalHHSBlock | Dict[str, Any]], *, domains: Sequence[str] | None = None, kinds: Sequence[str] | None = None, ledger_path: str | Path = "demo_reports/hhs_operator_execution_ledger_v1.json") -> OperatorExecutionReceipt:
    registry = build_operator_registry(blocks)
    selected = select_operators(registry, domains=domains, kinds=kinds)
    if not selected:
        empty_gate = invariant_gate_for_execution(input_text, input_text, [])
        ledger = MemoryLedger(ledger_path)
        payload = {"input_text": input_text, "status": OperatorExecutionStatus.NO_MATCH.value, "invariant_gate": empty_gate.to_dict()}
        commit = ledger.append_payloads("operator_execution_no_match_v1", [payload])
        replay = replay_ledger(ledger_path)
        receipt = hash72_digest(("operator_execution_no_match_v1", payload, commit.receipt_hash72, replay.receipt_hash72), width=24)
        return OperatorExecutionReceipt("hhs_operator_execution_layer_v1", input_text, hash72_digest(("operator_input_v1", input_text), width=24), [], input_text, hash72_digest(("operator_execution_final_output_v1", input_text), width=24), empty_gate, OperatorExecutionStatus.NO_MATCH, None, commit.to_dict(), replay.to_dict(), receipt)
    return execute_operator_chain(input_text, selected, ledger_path=ledger_path)


def demo() -> Dict[str, Any]:
    from hhs_runtime.hhs_drive_alignment_corpus_ingestor_v2 import ingest_drive_corpus_artifacts

    sample = {
        "id": "operator_demo",
        "title": "Operator Demo Corpus",
        "text": """
# HHS Alignment Axiom
Statement: Preserve Δe=0, Ψ=0, Θ15=true, Ω=true while translating claims.

# Style Operator — Recursive Harmonic Prose
Write with recursive rhythm, controlled repetition, and semantic return. Apply the style without changing the claim.

# Writing Process — Draft Audit Compress Re-expand
Step 1: draft. Step 2: audit for semantic drift. Step 3: compress into an operator. Step 4: re-expand as clear prose.
""",
    }
    ingest = ingest_drive_corpus_artifacts([sample], ledger_path="demo_reports/hhs_operator_demo_corpus_ledger_v1.json")
    ledger_data = json.loads(Path("demo_reports/hhs_operator_demo_corpus_ledger_v1.json").read_text(encoding="utf-8"))
    blocks = [block["payload"] for block in ledger_data["blocks"]]
    return execute_from_canonical_blocks("The system must preserve meaning while changing form.", blocks, ledger_path="demo_reports/hhs_operator_execution_demo_v1.json").to_dict()


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))

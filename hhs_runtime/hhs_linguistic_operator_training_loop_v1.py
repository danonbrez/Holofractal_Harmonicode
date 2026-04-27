"""
HHS Linguistic Operator Training Loop v1
========================================

Binds adaptive ERS temporal-shell carriers to natural-language transformation
operators and emits deterministic feedback records for shell learning.

Carrier mapping
---------------
    x  -> syntactic transformations
    y  -> semantic transformations
    xy -> structural / logical transformations

Purpose
-------
Use the same HHS temporal shell substrate that drives symbolic exploration to
train language reasoning and translation operators.

Pipeline:
    temporal shells
    -> carrier-bound linguistic operators
    -> candidate transformations
    -> invariant-style scoring
    -> feedback records
    -> adaptive shell weighting

This module does not call an LLM. It produces deterministic operator candidates
and feedback receipts suitable for later AI-agent integration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence
import json
import re

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_entangled_reciprocal_seesaw_temporal_shell_v1 import TemporalShellRun, generate_temporal_shells


class LinguisticCarrier(str, Enum):
    SYNTAX = "x"
    SEMANTICS = "y"
    STRUCTURE_LOGIC = "xy"


class LinguisticOperatorKind(str, Enum):
    SYNTAX_NORMALIZE = "SYNTAX_NORMALIZE"
    SEMANTIC_PRESERVE = "SEMANTIC_PRESERVE"
    STRUCTURE_VALIDATE = "STRUCTURE_VALIDATE"


class TrainingStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    HELD = "HELD"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class LinguisticOperator:
    carrier: str
    kind: LinguisticOperatorKind
    description: str
    operator_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


@dataclass(frozen=True)
class LinguisticTrainingStep:
    index: int
    carrier: str
    phase_index: int
    operator_kind: str
    input_text: str
    output_text: str
    syntax_score: int
    semantic_score: int
    structure_score: int
    total_score: int
    status: TrainingStatus
    step_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class LinguisticTrainingRun:
    seed_hash72: str
    input_hash72: str
    shell_receipt_hash72: str
    steps: List[LinguisticTrainingStep]
    accepted: int
    rejected: int
    feedback_records: List[Dict[str, Any]]
    aggregate_hash72: str
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed_hash72": self.seed_hash72,
            "input_hash72": self.input_hash72,
            "shell_receipt_hash72": self.shell_receipt_hash72,
            "steps": [s.to_dict() for s in self.steps],
            "accepted": self.accepted,
            "rejected": self.rejected,
            "feedback_records": self.feedback_records,
            "aggregate_hash72": self.aggregate_hash72,
            "receipt_hash72": self.receipt_hash72,
        }


def carrier_operator(carrier: str) -> LinguisticOperator:
    if carrier == LinguisticCarrier.SYNTAX.value:
        kind = LinguisticOperatorKind.SYNTAX_NORMALIZE
        desc = "Normalize punctuation, spacing, casing, and syntactic segmentation without changing meaning."
    elif carrier == LinguisticCarrier.SEMANTICS.value:
        kind = LinguisticOperatorKind.SEMANTIC_PRESERVE
        desc = "Preserve semantic anchors, key terms, definitions, and referential continuity."
    else:
        kind = LinguisticOperatorKind.STRUCTURE_VALIDATE
        desc = "Validate logical structure, implication order, invariants, and constraint relationships."
    op_hash = hash72_digest(("linguistic_operator_v1", carrier, kind.value, desc), width=24)
    return LinguisticOperator(carrier, kind, desc, op_hash)


def _syntax_normalize(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text


def _semantic_preserve(text: str) -> str:
    # Deterministic semantic anchor wrapping. This is not paraphrase; it marks
    # anchors for downstream agent/LLM passes.
    anchors = ["Δe", "Ψ", "Θ15", "Ω", "HARMONICODE", "Hash72", "xy", "yx", "u^72"]
    out = text
    for anchor in anchors:
        out = out.replace(anchor, f"⟦{anchor}⟧") if anchor in out and f"⟦{anchor}⟧" not in out else out
    return out


def _structure_validate(text: str) -> str:
    equality_count = text.count("=") + text.count("==")
    neq_count = text.count("≠") + text.count("!=")
    return f"STRUCTURE{{eq={equality_count},neq={neq_count}}} :: {text}"


def apply_linguistic_operator(text: str, operator: LinguisticOperator) -> str:
    if operator.kind == LinguisticOperatorKind.SYNTAX_NORMALIZE:
        return _syntax_normalize(text)
    if operator.kind == LinguisticOperatorKind.SEMANTIC_PRESERVE:
        return _semantic_preserve(text)
    return _structure_validate(text)


def _score_step(input_text: str, output_text: str, operator: LinguisticOperator) -> tuple[int, int, int, int, TrainingStatus]:
    syntax_score = 100 if "  " not in output_text and output_text.strip() == output_text else 70
    anchors = ["Δe", "Ψ", "Θ15", "Ω", "xy", "yx", "u^72"]
    preserved = sum(1 for a in anchors if (a not in input_text) or (a in output_text))
    semantic_score = int((preserved / len(anchors)) * 100)
    structure_score = 100
    if "xy" in input_text and "yx" in input_text and output_text.find("xy") > output_text.find("yx") >= 0:
        structure_score = 85
    if "STRUCTURE{" in output_text:
        structure_score = 100
    total = int(syntax_score * 0.25 + semantic_score * 0.45 + structure_score * 0.30)
    status = TrainingStatus.ACCEPTED if total >= 80 else TrainingStatus.HELD if total >= 65 else TrainingStatus.REJECTED
    return syntax_score, semantic_score, structure_score, total, status


def run_linguistic_training_loop(input_text: str, *, seed: str = "HHS_LANGUAGE_SEED", cycles: int = 1, feedback_records: Sequence[Dict[str, Any]] | None = None, max_steps: int = 72) -> LinguisticTrainingRun:
    shells: TemporalShellRun = generate_temporal_shells(seed, cycles=cycles, feedback_records=feedback_records)
    current = input_text
    steps: List[LinguisticTrainingStep] = []
    feedback: List[Dict[str, Any]] = []

    for shell in shells.steps[:max_steps]:
        operator = carrier_operator(shell.carrier)
        output = apply_linguistic_operator(current, operator)
        syntax, semantic, structure, total, status = _score_step(current, output, operator)
        step_hash = hash72_digest(("linguistic_training_step_v1", shell.shell_hash72, operator.to_dict(), current, output, syntax, semantic, structure, total, status.value), width=24)
        step = LinguisticTrainingStep(shell.index, shell.carrier, shell.phase_index, operator.kind.value, current, output, syntax, semantic, structure, total, status, step_hash)
        steps.append(step)
        feedback.append({
            "summary_hash72": step_hash,
            "phases": [shell.phase_index],
            "carrier": shell.carrier,
            "status": "STAGED" if status == TrainingStatus.ACCEPTED else "QUARANTINED" if status == TrainingStatus.REJECTED else "HELD",
            "score": total,
            "operator_kind": operator.kind.value,
        })
        if status != TrainingStatus.REJECTED:
            current = output

    accepted = sum(1 for s in steps if s.status == TrainingStatus.ACCEPTED)
    rejected = sum(1 for s in steps if s.status == TrainingStatus.REJECTED)
    seed_hash = hash72_digest(("linguistic_training_seed_v1", seed, cycles), width=24)
    input_hash = hash72_digest(("linguistic_training_input_v1", input_text), width=24)
    aggregate = hash72_digest(("linguistic_training_aggregate_v1", seed_hash, input_hash, shells.receipt_hash72, [s.step_hash72 for s in steps], feedback), width=24)
    receipt = hash72_digest(("linguistic_training_run_receipt_v1", aggregate, accepted, rejected), width=24)
    return LinguisticTrainingRun(seed_hash, input_hash, shells.receipt_hash72, steps, accepted, rejected, feedback, aggregate, receipt)


def main() -> None:
    sample = "HARMONICODE preserves Δe=0, Ψ=0, Θ15=true, Ω=true while xy≠yx and u^72=Ω."
    print(json.dumps(run_linguistic_training_loop(sample, max_steps=9).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

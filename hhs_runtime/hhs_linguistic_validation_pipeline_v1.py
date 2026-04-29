"""
HHS Linguistic Validation Pipeline v1
=====================================

Additive preflight layer for the language-learning stack.

This module wires the deterministic grammar rule enforcer and WordNet relation
enforcer into the existing linguistic operator training loop without replacing
or changing the training-loop carrier logic.

Pipeline:
    source text
    -> optional grammar enforcement receipt
    -> optional WordNet relation validation receipt
    -> feedback records
    -> run_linguistic_training_loop(..., feedback_records=...)

No external side effects are performed. All receipts remain Hash72-addressed
compiler/interpreter artifacts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.hhs_grammar_rule_enforcer_v1 import (
    GrammarEnforcementReceipt,
    enforce_grammar_rules,
    load_grammar_rules,
)
from hhs_runtime.hhs_linguistic_operator_training_loop_v1 import LinguisticTrainingRun, run_linguistic_training_loop
from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import (
    WordRelationValidationReceipt,
    default_wordnet_paths,
    load_wordnet_relations,
    validate_word_relations,
    validate_wordnet_files,
)


@dataclass(frozen=True)
class LinguisticValidationPipelineReceipt:
    input_text: str
    preflight_text: str
    grammar_status: str
    wordnet_status: str
    grammar_receipt: Dict[str, Any] | None
    wordnet_receipt: Dict[str, Any] | None
    wordnet_file_status: Dict[str, Any]
    preflight_feedback_records: List[Dict[str, Any]]
    training_run: Dict[str, Any]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _grammar_feedback(receipt: GrammarEnforcementReceipt) -> Dict[str, Any]:
    score = 100 if receipt.applied_count == 0 else 95
    return {
        "summary_hash72": receipt.receipt_hash72,
        "phases": [],
        "carrier": "x",
        "status": "STAGED",
        "score": score,
        "operator_kind": "GRAMMAR_RULE_ENFORCE",
        "rules_loaded": receipt.rules_loaded,
        "applied_count": receipt.applied_count,
    }


def _wordnet_feedback(receipt: WordRelationValidationReceipt) -> Dict[str, Any]:
    total = max(1, receipt.known_count + receipt.unknown_count)
    score = int((receipt.known_count / total) * 100)
    return {
        "summary_hash72": receipt.receipt_hash72,
        "phases": [],
        "carrier": "y",
        "status": "STAGED" if receipt.known_count else "HELD",
        "score": score,
        "operator_kind": "WORD_RELATION_VALIDATE",
        "known_count": receipt.known_count,
        "unknown_count": receipt.unknown_count,
    }


def _missing_wordnet_feedback(file_status: Dict[str, Any]) -> Dict[str, Any]:
    h = hash72_digest(("hhs_wordnet_file_status_v1", file_status), width=24)
    return {
        "summary_hash72": h,
        "phases": [],
        "carrier": "y",
        "status": "HELD",
        "score": 0,
        "operator_kind": "WORDNET_FILE_VALIDATE",
        "file_status": file_status.get("status", "UNKNOWN"),
        "missing": file_status.get("missing", []),
    }


def run_linguistic_validation_pipeline(
    input_text: str,
    *,
    grammar_csv_path: str | Path | None = None,
    wordnet_paths: Sequence[str | Path] | None = None,
    require_wordnet: bool = False,
    seed: str = "HHS_LANGUAGE_SEED",
    cycles: int = 1,
    max_steps: int = 72,
) -> LinguisticValidationPipelineReceipt:
    """Run grammar/WordNet preflight before the existing training loop.

    The function is fail-soft for optional resources by default. Set
    require_wordnet=True to require the complete WordNet CSV set and fail closed
    when files are missing.
    """

    preflight_text = input_text
    feedback: List[Dict[str, Any]] = []

    grammar_receipt: GrammarEnforcementReceipt | None = None
    grammar_status = "SKIPPED"
    if grammar_csv_path is not None:
        rules = load_grammar_rules(grammar_csv_path)
        grammar_receipt = enforce_grammar_rules(preflight_text, rules)
        preflight_text = grammar_receipt.output_text
        grammar_status = "READY"
        feedback.append(_grammar_feedback(grammar_receipt))

    resolved_wordnet_paths = list(wordnet_paths) if wordnet_paths is not None else default_wordnet_paths()
    wordnet_file_status = validate_wordnet_files(resolved_wordnet_paths)
    wordnet_receipt: WordRelationValidationReceipt | None = None
    wordnet_status = wordnet_file_status["status"]
    if wordnet_file_status["status"] == "READY":
        relation_db = load_wordnet_relations(resolved_wordnet_paths, require_all=True)
        wordnet_receipt = validate_word_relations(preflight_text, relation_db)
        feedback.append(_wordnet_feedback(wordnet_receipt))
    elif require_wordnet:
        raise FileNotFoundError(json.dumps(wordnet_file_status, indent=2, sort_keys=True))
    else:
        feedback.append(_missing_wordnet_feedback(wordnet_file_status))

    training_run: LinguisticTrainingRun = run_linguistic_training_loop(
        preflight_text,
        seed=seed,
        cycles=cycles,
        feedback_records=feedback,
        max_steps=max_steps,
    )

    receipt_hash72 = hash72_digest(
        (
            "hhs_linguistic_validation_pipeline_receipt_v1",
            input_text,
            preflight_text,
            grammar_receipt.to_dict() if grammar_receipt else None,
            wordnet_receipt.to_dict() if wordnet_receipt else None,
            wordnet_file_status,
            feedback,
            training_run.receipt_hash72,
        ),
        width=24,
    )

    return LinguisticValidationPipelineReceipt(
        input_text=input_text,
        preflight_text=preflight_text,
        grammar_status=grammar_status,
        wordnet_status=wordnet_status,
        grammar_receipt=grammar_receipt.to_dict() if grammar_receipt else None,
        wordnet_receipt=wordnet_receipt.to_dict() if wordnet_receipt else None,
        wordnet_file_status=wordnet_file_status,
        preflight_feedback_records=feedback,
        training_run=training_run.to_dict(),
        receipt_hash72=receipt_hash72,
    )


def main() -> None:
    sample = "The symbolic system preserves valid meaning while HARMONICODE keeps xy≠yx."
    receipt = run_linguistic_validation_pipeline(sample, max_steps=9)
    print(json.dumps(receipt.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

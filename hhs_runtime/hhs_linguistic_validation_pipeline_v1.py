"""
HHS Linguistic Validation Pipeline v1
=====================================

Additive runtime validation layer for the language-learning stack.

This module wires the deterministic grammar rule enforcer and WordNet relation
enforcer into the existing linguistic operator training loop without replacing
or changing the training-loop carrier logic.

Pipeline:
    source text
    -> CSV auto-discovery
    -> optional grammar enforcement receipt
    -> optional WordNet relation validation receipt
    -> runtime gate receipt
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
    WORDNET_CSV_FILENAMES,
    WordRelationValidationReceipt,
    default_wordnet_paths,
    load_wordnet_relations,
    repo_root,
    validate_word_relations,
    validate_wordnet_files,
)


GRAMMAR_CSV_CANDIDATE_FILENAMES = [
    "GrammarRules.csv",
    "grammar_rules.csv",
    "HHSGrammarRules.csv",
    "hhs_grammar_rules.csv",
    "EnglishGrammarRules.csv",
    "english_grammar_rules.csv",
]


@dataclass(frozen=True)
class CsvDiscoveryReceipt:
    repo_root: str
    grammar_csv_path: str | None
    grammar_candidates: List[str]
    wordnet_directory: str
    wordnet_file_status: Dict[str, Any]
    status: str
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeLanguageGateReceipt:
    status: str
    grammar_required: bool
    wordnet_required: bool
    min_wordnet_known_ratio: float
    grammar_status: str
    wordnet_status: str
    wordnet_known_ratio: float
    failures: List[str]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LinguisticValidationPipelineReceipt:
    input_text: str
    preflight_text: str
    grammar_status: str
    wordnet_status: str
    csv_discovery: Dict[str, Any]
    runtime_gate: Dict[str, Any]
    grammar_receipt: Dict[str, Any] | None
    wordnet_receipt: Dict[str, Any] | None
    wordnet_file_status: Dict[str, Any]
    preflight_feedback_records: List[Dict[str, Any]]
    training_run: Dict[str, Any]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def discover_csv_inputs(
    *,
    root: str | Path | None = None,
    grammar_csv_path: str | Path | None = None,
    wordnet_paths: Sequence[str | Path] | None = None,
) -> CsvDiscoveryReceipt:
    """Discover grammar and WordNet CSV inputs from canonical repo locations."""

    base = Path(root) if root is not None else repo_root()

    grammar_candidates: List[Path] = []
    if grammar_csv_path is not None:
        grammar_candidates.append(Path(grammar_csv_path))
    for folder in [base / "data" / "grammar", base / "data", base / "hhs_runtime"]:
        for name in GRAMMAR_CSV_CANDIDATE_FILENAMES:
            grammar_candidates.append(folder / name)

    selected_grammar = next((p for p in grammar_candidates if p.exists()), None)

    resolved_wordnet_paths = list(wordnet_paths) if wordnet_paths is not None else default_wordnet_paths()
    wordnet_file_status = validate_wordnet_files(resolved_wordnet_paths)
    wordnet_directory = wordnet_file_status.get("directory", str(Path(resolved_wordnet_paths[0]).parent if resolved_wordnet_paths else base / "data" / "wordnet"))

    status = "READY" if wordnet_file_status["status"] == "READY" else "PARTIAL"
    receipt_hash72 = hash72_digest(
        (
            "hhs_csv_discovery_receipt_v1",
            str(base),
            str(selected_grammar) if selected_grammar else None,
            [str(p) for p in grammar_candidates],
            wordnet_directory,
            wordnet_file_status,
            status,
        ),
        width=24,
    )
    return CsvDiscoveryReceipt(
        repo_root=str(base),
        grammar_csv_path=str(selected_grammar) if selected_grammar else None,
        grammar_candidates=[str(p) for p in grammar_candidates],
        wordnet_directory=wordnet_directory,
        wordnet_file_status=wordnet_file_status,
        status=status,
        receipt_hash72=receipt_hash72,
    )


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


def enforce_runtime_language_gate(
    *,
    grammar_status: str,
    wordnet_status: str,
    wordnet_receipt: WordRelationValidationReceipt | None,
    grammar_required: bool = False,
    wordnet_required: bool = False,
    min_wordnet_known_ratio: float = 0.0,
) -> RuntimeLanguageGateReceipt:
    """Fail-closed runtime gate for accepted language-state transitions."""

    failures: List[str] = []
    if grammar_required and grammar_status != "READY":
        failures.append("GRAMMAR_REQUIRED_NOT_READY")
    if wordnet_required and wordnet_status != "READY":
        failures.append("WORDNET_REQUIRED_NOT_READY")

    if wordnet_receipt is None:
        known_ratio = 0.0
    else:
        total = max(1, wordnet_receipt.known_count + wordnet_receipt.unknown_count)
        known_ratio = wordnet_receipt.known_count / total

    if wordnet_status == "READY" and known_ratio < min_wordnet_known_ratio:
        failures.append("WORDNET_KNOWN_RATIO_BELOW_THRESHOLD")

    status = "ACCEPTED" if not failures else "REJECTED"
    receipt_hash72 = hash72_digest(
        (
            "hhs_runtime_language_gate_receipt_v1",
            status,
            grammar_required,
            wordnet_required,
            min_wordnet_known_ratio,
            grammar_status,
            wordnet_status,
            known_ratio,
            failures,
        ),
        width=24,
    )
    return RuntimeLanguageGateReceipt(
        status=status,
        grammar_required=grammar_required,
        wordnet_required=wordnet_required,
        min_wordnet_known_ratio=min_wordnet_known_ratio,
        grammar_status=grammar_status,
        wordnet_status=wordnet_status,
        wordnet_known_ratio=known_ratio,
        failures=failures,
        receipt_hash72=receipt_hash72,
    )


def run_linguistic_validation_pipeline(
    input_text: str,
    *,
    grammar_csv_path: str | Path | None = None,
    wordnet_paths: Sequence[str | Path] | None = None,
    require_grammar: bool = False,
    require_wordnet: bool = False,
    enforce_runtime_gate: bool = False,
    min_wordnet_known_ratio: float = 0.0,
    seed: str = "HHS_LANGUAGE_SEED",
    cycles: int = 1,
    max_steps: int = 72,
) -> LinguisticValidationPipelineReceipt:
    """Run grammar/WordNet runtime validation before the existing training loop.

    By default this remains fail-soft for optional resources. Set
    enforce_runtime_gate=True with require_grammar / require_wordnet / threshold
    values to fail closed before training-loop acceptance.
    """

    discovery = discover_csv_inputs(grammar_csv_path=grammar_csv_path, wordnet_paths=wordnet_paths)
    selected_grammar = grammar_csv_path or discovery.grammar_csv_path

    preflight_text = input_text
    feedback: List[Dict[str, Any]] = []

    grammar_receipt: GrammarEnforcementReceipt | None = None
    grammar_status = "SKIPPED"
    if selected_grammar is not None:
        rules = load_grammar_rules(selected_grammar)
        grammar_receipt = enforce_grammar_rules(preflight_text, rules)
        preflight_text = grammar_receipt.output_text
        grammar_status = "READY"
        feedback.append(_grammar_feedback(grammar_receipt))
    elif require_grammar:
        grammar_status = "MISSING_FILES"

    resolved_wordnet_paths = list(wordnet_paths) if wordnet_paths is not None else default_wordnet_paths()
    wordnet_file_status = validate_wordnet_files(resolved_wordnet_paths)
    wordnet_receipt: WordRelationValidationReceipt | None = None
    wordnet_status = wordnet_file_status["status"]
    if wordnet_file_status["status"] == "READY":
        relation_db = load_wordnet_relations(resolved_wordnet_paths, require_all=True)
        wordnet_receipt = validate_word_relations(preflight_text, relation_db)
        feedback.append(_wordnet_feedback(wordnet_receipt))
    elif require_wordnet and not enforce_runtime_gate:
        raise FileNotFoundError(json.dumps(wordnet_file_status, indent=2, sort_keys=True))
    else:
        feedback.append(_missing_wordnet_feedback(wordnet_file_status))

    runtime_gate = enforce_runtime_language_gate(
        grammar_status=grammar_status,
        wordnet_status=wordnet_status,
        wordnet_receipt=wordnet_receipt,
        grammar_required=require_grammar,
        wordnet_required=require_wordnet,
        min_wordnet_known_ratio=min_wordnet_known_ratio,
    )

    if enforce_runtime_gate and runtime_gate.status != "ACCEPTED":
        training_run_dict: Dict[str, Any] = {
            "status": "HELD_BY_RUNTIME_LANGUAGE_GATE",
            "reason": runtime_gate.failures,
            "receipt_hash72": runtime_gate.receipt_hash72,
        }
    else:
        training_run: LinguisticTrainingRun = run_linguistic_training_loop(
            preflight_text,
            seed=seed,
            cycles=cycles,
            feedback_records=feedback,
            max_steps=max_steps,
        )
        training_run_dict = training_run.to_dict()

    receipt_hash72 = hash72_digest(
        (
            "hhs_linguistic_validation_pipeline_receipt_v1",
            input_text,
            preflight_text,
            grammar_receipt.to_dict() if grammar_receipt else None,
            wordnet_receipt.to_dict() if wordnet_receipt else None,
            wordnet_file_status,
            discovery.to_dict(),
            runtime_gate.to_dict(),
            feedback,
            training_run_dict.get("receipt_hash72"),
        ),
        width=24,
    )

    return LinguisticValidationPipelineReceipt(
        input_text=input_text,
        preflight_text=preflight_text,
        grammar_status=grammar_status,
        wordnet_status=wordnet_status,
        csv_discovery=discovery.to_dict(),
        runtime_gate=runtime_gate.to_dict(),
        grammar_receipt=grammar_receipt.to_dict() if grammar_receipt else None,
        wordnet_receipt=wordnet_receipt.to_dict() if wordnet_receipt else None,
        wordnet_file_status=wordnet_file_status,
        preflight_feedback_records=feedback,
        training_run=training_run_dict,
        receipt_hash72=receipt_hash72,
    )


def validate_repo_language_runtime(
    *,
    require_grammar: bool = False,
    require_wordnet: bool = True,
    min_wordnet_known_ratio: float = 0.0,
    sample_text: str = "The symbolic system preserves valid meaning while HARMONICODE keeps xy≠yx.",
) -> Dict[str, Any]:
    """Repository-level validator for CLI and CI smoke checks."""

    discovery = discover_csv_inputs()
    receipt = run_linguistic_validation_pipeline(
        sample_text,
        grammar_csv_path=discovery.grammar_csv_path,
        require_grammar=require_grammar,
        require_wordnet=require_wordnet,
        enforce_runtime_gate=True,
        min_wordnet_known_ratio=min_wordnet_known_ratio,
        max_steps=9,
    )
    status = receipt.runtime_gate["status"]
    validator_hash72 = hash72_digest(("hhs_repo_language_runtime_validator_v1", discovery.to_dict(), receipt.to_dict(), status), width=24)
    return {
        "status": status,
        "csv_discovery": discovery.to_dict(),
        "runtime_gate": receipt.runtime_gate,
        "pipeline_receipt_hash72": receipt.receipt_hash72,
        "validator_hash72": validator_hash72,
        "required_wordnet_files": WORDNET_CSV_FILENAMES,
    }


def main() -> None:
    sample = "The symbolic system preserves valid meaning while HARMONICODE keeps xy≠yx."
    receipt = run_linguistic_validation_pipeline(sample, max_steps=9)
    print(json.dumps(receipt.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

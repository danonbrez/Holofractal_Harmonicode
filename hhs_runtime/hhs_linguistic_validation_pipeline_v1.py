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

from hhs_runtime.hhs_pass118_symbolic_harmonicode_runtime_v1 import PROGRAM_SCHEMA
from hhs_runtime.hhs_pass119_language_model_nonreplacement_integration_v1 import (
    LanguageModelIntegrationEngine,
    Pass119Error,
)
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


@dataclass(frozen=True)
class NLGOptimizationProfile:
    require_grammar: bool
    require_wordnet: bool
    min_wordnet_known_ratio: float
    max_steps: int
    max_propositions: int
    max_candidates: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NLGOptimizationEvaluation:
    profile: Dict[str, Any]
    runtime_gate_acceptance_rate: float
    average_wordnet_known_ratio: float
    projection_admission_rate: float
    rejection_code_incidence: int
    overall_acceptance_rate: float
    evaluation_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NLGOptimizationSweepReceipt:
    workload_class: str
    target_min_acceptance: float
    prompt_count: int
    evaluations: List[Dict[str, Any]]
    selected_profile: Dict[str, Any]
    status: str
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


DEFAULT_NLG_WORKLOAD_CLASS = "NLG_BALANCED_STRICT_V1"
DEFAULT_NLG_OPTIMAL_PROFILE = NLGOptimizationProfile(
    require_grammar=False,
    require_wordnet=True,
    min_wordnet_known_ratio=0.8,
    max_steps=9,
    max_propositions=64,
    max_candidates=8,
)


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


def _pass119_program_for_nlg() -> Dict[str, Any]:
    return {
        "schema": PROGRAM_SCHEMA,
        "program_id": "pass119:nlg-opt",
        "scope": "nlg-optimization",
        "symbols": [
            {"name": "x", "type": "RATIONAL", "value": {"node": "literal", "kind": "RATIONAL", "value": "9/8"}},
            {"name": "y", "type": "RATIONAL", "value": {"node": "literal", "kind": "RATIONAL", "value": "8/9"}},
        ],
        "operations": [
            {"kind": "bind", "name": "product", "expression": {"node": "call", "op": "multiply", "args": [{"node": "symbol", "name": "x"}, {"node": "symbol", "name": "y"}]}},
            {"kind": "assert", "expression": {"node": "call", "op": "equal", "args": [{"node": "symbol", "name": "product"}, {"node": "literal", "kind": "INTEGER", "value": 1}]}},
        ],
    }


def _pass119_stress_cases() -> List[Dict[str, Any]]:
    return [
        {"text": "No token is false.", "ambiguities": []},
        {"text": "Every relation remains in scope.", "ambiguities": []},
        {"text": "The outcome may be uncertain.", "ambiguities": []},
        {"text": "bank", "ambiguities": [{"source_span": [0, 4], "candidate_meanings": ["financial institution", "river edge"]}]},
    ]


def _evaluate_pass119_profile(*, max_propositions: int, max_candidates: int) -> Dict[str, Any]:
    engine = LanguageModelIntegrationEngine(max_propositions=max_propositions, max_candidates=max_candidates)
    vector = {k: True for k in ("reference_identity", "predicate_identity", "negation", "scope", "modality", "temporality", "uncertainty", "authority")}
    admitted = 0
    rejections = 0
    total = 0
    for case in _pass119_stress_cases():
        total += 1
        try:
            text = case["text"]
            preserved = engine.preserve_input(text)
            propositions = engine.extract_propositions(
                preserved,
                [{"start": 0, "end": len(preserved["verbatim_text"])}],
                ambiguities=case.get("ambiguities", []),
            )
            resolved = [item["ambiguity_root_hash72"] for item in propositions.get("ambiguities", [])]
            proposal = engine.create_model_proposal(
                source_input_root_hash72=preserved["input_root_hash72"],
                model_identity="nlg-optimizer-model",
                candidate_interpretations=[{"meaning": "preserve explicit linguistic meaning"}],
                candidate_programs=[_pass119_program_for_nlg()],
                uncertainty={"known": ["translation contract"], "unknown": []},
            )
            translation = engine.admit_translation(
                proposition_set=propositions,
                proposal=proposal,
                selected_program_index=0,
                meaning_preservation_vector=vector,
                resolved_ambiguity_roots=resolved,
            )
            interaction = engine.execute_admitted_translation(
                translation,
                authority_root_hash72="hhs_nlg_optimizer_authority_v1",
            )
            authoritative = engine.authoritative_result_object(interaction)
            candidate = engine.generate_projection_candidate(
                interaction=interaction,
                model_proposal_root_hash72=proposal["proposal_root_hash72"],
                text="Authoritative runtime-aligned projection.",
                represented_status=authoritative["status"],
                represented_outputs=authoritative["outputs"],
                uncertainty={"known": ["runtime result"], "unknown": []},
            )
            projection = engine.validate_projection(interaction, candidate)
            if projection["projection_status"] == "LANGUAGE_PROJECTION_ADMITTED":
                admitted += 1
        except Pass119Error:
            rejections += 1
    return {
        "projection_admission_rate": (admitted / total) if total else 0.0,
        "rejection_code_incidence": rejections,
        "pass119_prompt_count": total,
    }


def optimize_nlg_workload_profile(
    *,
    workload_class: str = DEFAULT_NLG_WORKLOAD_CLASS,
    prompts: Sequence[str] | None = None,
    require_grammar_options: Sequence[bool] = (False, True),
    require_wordnet_options: Sequence[bool] = (True, False),
    min_wordnet_known_ratio_options: Sequence[float] = (0.0, 0.5, 0.8, 0.95),
    max_steps_options: Sequence[int] = (9, 18, 36, 72),
    max_propositions_options: Sequence[int] = (64, 128, 512),
    max_candidates_options: Sequence[int] = (8, 16, 64),
    target_min_acceptance: float = 0.95,
) -> NLGOptimizationSweepReceipt:
    prompt_set = list(prompts) if prompts is not None else [
        "No token is false.",
        "Every relation remains in scope.",
        "The outcome may be uncertain.",
        "The valid meaning remains preserved.",
    ]

    evaluations: List[NLGOptimizationEvaluation] = []
    for require_grammar in require_grammar_options:
        for require_wordnet in require_wordnet_options:
            for min_known in min_wordnet_known_ratio_options:
                for max_steps in max_steps_options:
                    for max_propositions in max_propositions_options:
                        for max_candidates in max_candidates_options:
                            accepted = 0
                            known_ratios: List[float] = []
                            for prompt in prompt_set:
                                receipt = run_linguistic_validation_pipeline(
                                    prompt,
                                    require_grammar=require_grammar,
                                    require_wordnet=require_wordnet,
                                    enforce_runtime_gate=True,
                                    min_wordnet_known_ratio=min_known,
                                    max_steps=max_steps,
                                )
                                gate = receipt.runtime_gate
                                if gate["status"] == "ACCEPTED":
                                    accepted += 1
                                known_ratios.append(float(gate["wordnet_known_ratio"]))
                            pipeline_rate = accepted / len(prompt_set) if prompt_set else 0.0
                            avg_known = sum(known_ratios) / len(known_ratios) if known_ratios else 0.0
                            pass119_eval = _evaluate_pass119_profile(
                                max_propositions=max_propositions,
                                max_candidates=max_candidates,
                            )
                            projection_rate = pass119_eval["projection_admission_rate"]
                            rejection_count = pass119_eval["rejection_code_incidence"]
                            overall_rate = min(pipeline_rate, projection_rate)
                            profile = NLGOptimizationProfile(
                                require_grammar=require_grammar,
                                require_wordnet=require_wordnet,
                                min_wordnet_known_ratio=min_known,
                                max_steps=max_steps,
                                max_propositions=max_propositions,
                                max_candidates=max_candidates,
                            )
                            evaluation_payload = {
                                "profile": profile.to_dict(),
                                "runtime_gate_acceptance_rate": pipeline_rate,
                                "average_wordnet_known_ratio": avg_known,
                                "projection_admission_rate": projection_rate,
                                "rejection_code_incidence": rejection_count,
                                "overall_acceptance_rate": overall_rate,
                            }
                            evaluation_hash = hash72_digest(("hhs_nlg_optimization_evaluation_v1", evaluation_payload), width=24)
                            evaluations.append(
                                NLGOptimizationEvaluation(
                                    profile=profile.to_dict(),
                                    runtime_gate_acceptance_rate=pipeline_rate,
                                    average_wordnet_known_ratio=avg_known,
                                    projection_admission_rate=projection_rate,
                                    rejection_code_incidence=rejection_count,
                                    overall_acceptance_rate=overall_rate,
                                    evaluation_hash72=evaluation_hash,
                                )
                            )

    strict_candidates = [
        e
        for e in evaluations
        if e.rejection_code_incidence == 0 and e.overall_acceptance_rate >= target_min_acceptance
    ]

    def _strictness_key(item: NLGOptimizationEvaluation) -> tuple[float, ...]:
        profile = item.profile
        return (
            float(bool(profile["require_grammar"])),
            float(bool(profile["require_wordnet"])),
            float(profile["min_wordnet_known_ratio"]),
            float(-int(profile["max_steps"])),
            float(-int(profile["max_propositions"])),
            float(-int(profile["max_candidates"])),
        )

    if strict_candidates:
        selected_eval = max(strict_candidates, key=_strictness_key)
        status = "LOCKED_OPTIMAL_PROFILE"
    else:
        selected_eval = max(
            evaluations,
            key=lambda item: (
                float(item.rejection_code_incidence == 0),
                item.overall_acceptance_rate,
                item.runtime_gate_acceptance_rate,
                item.projection_admission_rate,
                *_strictness_key(item),
            ),
        )
        status = "DEGRADED_PROFILE_FALLBACK"

    receipt_payload = {
        "workload_class": workload_class,
        "target_min_acceptance": target_min_acceptance,
        "prompt_count": len(prompt_set),
        "status": status,
        "selected_profile": selected_eval.profile,
        "evaluation_hashes": [e.evaluation_hash72 for e in evaluations],
    }
    receipt_hash = hash72_digest(("hhs_nlg_optimization_sweep_receipt_v1", receipt_payload), width=24)
    return NLGOptimizationSweepReceipt(
        workload_class=workload_class,
        target_min_acceptance=target_min_acceptance,
        prompt_count=len(prompt_set),
        evaluations=[e.to_dict() for e in evaluations],
        selected_profile=selected_eval.profile,
        status=status,
        receipt_hash72=receipt_hash,
    )


def run_default_nlg_workload_validation(
    text: str,
    *,
    profile: NLGOptimizationProfile = DEFAULT_NLG_OPTIMAL_PROFILE,
) -> LinguisticValidationPipelineReceipt:
    return run_linguistic_validation_pipeline(
        text,
        require_grammar=profile.require_grammar,
        require_wordnet=profile.require_wordnet,
        enforce_runtime_gate=True,
        min_wordnet_known_ratio=profile.min_wordnet_known_ratio,
        max_steps=profile.max_steps,
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
    receipt = run_default_nlg_workload_validation(sample)
    print(json.dumps(receipt.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

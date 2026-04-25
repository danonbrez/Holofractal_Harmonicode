"""
HHS Fuzz Result Learning Analyzer v1
====================================

Turns adversarial fuzz results into agentic learning signals.

Input sources:
- pytest-json-report style output
- simplified test result JSON
- manually pasted failure summaries converted to JSON

Pipeline:
    fuzz results
    -> classify failure/success/quarantine behavior
    -> identify patch targets
    -> generate learned defensive rules
    -> store in adaptive learning database
    -> emit patch recommendations

This module does not execute tests. It analyzes results produced elsewhere.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.hhs_adaptive_learning_layer_v1 import (
    AdaptiveLearningDatabase,
    LearnedRule,
    LearningRecord,
    LearningStatus,
    RuleUpdateKind,
    _make_rule,
    invariant_gate_for_learning,
)
from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_recursive_symbol_kernel_v1 import (
    AddressRelation,
    GlobalSymbolCache,
    OrthogonalChain,
    SymbolEntityType,
)
from hhs_runtime.hhs_self_modifying_agents_v1 import ModificationStatus


class FuzzOutcome(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    XFAILED = "XFAILED"
    XPASSED = "XPASSED"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


class PatchPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass(frozen=True)
class FuzzTestSignal:
    test_name: str
    outcome: FuzzOutcome
    file: str
    line: int | None
    duration: float | None
    message: str
    category: str
    signal_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["outcome"] = self.outcome.value
        return data


@dataclass(frozen=True)
class PatchRecommendation:
    target: str
    priority: PatchPriority
    reason: str
    evidence: List[str]
    recommendation_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["priority"] = self.priority.value
        return data


@dataclass(frozen=True)
class FuzzLearningAnalysis:
    source_hash72: str
    signals: List[FuzzTestSignal]
    recommendations: List[PatchRecommendation]
    learned_rules: List[LearnedRule]
    learning_record_hash72: str
    ledger_commit_receipt: Dict[str, Any]
    replay_receipt: Dict[str, Any]
    report_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_hash72": self.source_hash72,
            "signals": [s.to_dict() for s in self.signals],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "learned_rules": [r.to_dict() for r in self.learned_rules],
            "learning_record_hash72": self.learning_record_hash72,
            "ledger_commit_receipt": self.ledger_commit_receipt,
            "replay_receipt": self.replay_receipt,
            "report_hash72": self.report_hash72,
        }


def normalize_outcome(raw: str) -> FuzzOutcome:
    s = str(raw or "").upper()
    if s in {"PASSED", "PASS"}:
        return FuzzOutcome.PASSED
    if s in {"FAILED", "FAIL"}:
        return FuzzOutcome.FAILED
    if s in {"XFAILED", "XFAIL"}:
        return FuzzOutcome.XFAILED
    if s in {"XPASSED", "XPASS"}:
        return FuzzOutcome.XPASSED
    if s in {"ERROR", "BROKEN"}:
        return FuzzOutcome.ERROR
    if s in {"SKIPPED", "SKIP"}:
        return FuzzOutcome.SKIPPED
    return FuzzOutcome.ERROR


def classify_category(name: str, message: str) -> str:
    text = f"{name} {message}".lower()
    if "cross_modal" in text or "shell" in text:
        return "cross_modal_shell"
    if "manifest" in text:
        return "kernel_manifest"
    if "state" in text or "patch" in text:
        return "state_layer"
    if "ledger" in text or "manifold" in text:
        return "manifold_ledger"
    if "armor" in text or "lockdown" in text:
        return "security_armor"
    if "runtime" in text or "operation" in text:
        return "runtime_boundary"
    return "general_security"


def extract_tests(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    # pytest-json-report format: {"tests": [{"nodeid": ..., "outcome": ...}]}
    if isinstance(report.get("tests"), list):
        return report["tests"]
    # simplified format: {"results": [...]}
    if isinstance(report.get("results"), list):
        return report["results"]
    # single failure dict
    if "test_name" in report or "nodeid" in report:
        return [report]
    return []


def signal_from_test(item: Dict[str, Any]) -> FuzzTestSignal:
    name = str(item.get("nodeid") or item.get("test_name") or item.get("name") or "unknown_test")
    outcome = normalize_outcome(str(item.get("outcome") or item.get("status") or item.get("result")))
    file = str(item.get("file") or name.split("::")[0])
    line = item.get("line")
    try:
        line_i = int(line) if line is not None else None
    except Exception:
        line_i = None
    duration = item.get("duration")
    try:
        duration_f = float(duration) if duration is not None else None
    except Exception:
        duration_f = None
    call = item.get("call", {}) if isinstance(item.get("call"), dict) else {}
    message = str(item.get("message") or call.get("longrepr") or item.get("longrepr") or "")
    category = classify_category(name, message)
    h = hash72_digest(("fuzz_test_signal_v1", name, outcome.value, file, line_i, duration_f, message, category), width=18)
    return FuzzTestSignal(name, outcome, file, line_i, duration_f, message, category, h)


def recommend_from_signals(signals: Sequence[FuzzTestSignal]) -> List[PatchRecommendation]:
    recs: List[PatchRecommendation] = []
    by_category: Dict[str, List[FuzzTestSignal]] = {}
    for signal in signals:
        by_category.setdefault(signal.category, []).append(signal)

    for category, items in sorted(by_category.items()):
        failing = [s for s in items if s.outcome in {FuzzOutcome.FAILED, FuzzOutcome.ERROR, FuzzOutcome.XPASSED}]
        expected = [s for s in items if s.outcome == FuzzOutcome.XFAILED]
        if failing:
            priority = PatchPriority.CRITICAL if category in {"cross_modal_shell", "kernel_manifest", "state_layer"} else PatchPriority.HIGH
            reason = f"{len(failing)} adversarial test(s) failed in {category}; patch required before release."
            target = category
            evidence = [s.signal_hash72 for s in failing]
        elif expected:
            priority = PatchPriority.MEDIUM
            reason = f"{len(expected)} expected-fail hardening target(s) remain in {category}."
            target = category
            evidence = [s.signal_hash72 for s in expected]
        else:
            priority = PatchPriority.INFO
            reason = f"All observed adversarial tests passed or skipped in {category}."
            target = category
            evidence = [s.signal_hash72 for s in items]
        h = hash72_digest(("patch_recommendation_v1", target, priority.value, reason, evidence), width=18)
        recs.append(PatchRecommendation(target, priority, reason, evidence, h))
    return recs


def learned_rules_from_analysis(signals: Sequence[FuzzTestSignal], recs: Sequence[PatchRecommendation]) -> List[LearnedRule]:
    rules: List[LearnedRule] = []
    for rec in recs:
        if rec.priority in {PatchPriority.CRITICAL, PatchPriority.HIGH}:
            rules.append(_make_rule(len(rules), RuleUpdateKind.PENALIZE_ACTION, f"security_failure:{rec.target}", Fraction(-1, 6), rec.evidence, Fraction(1, 1)))
            rules.append(_make_rule(len(rules), RuleUpdateKind.REINFORCE_ACTION, f"quarantine_required:{rec.target}", Fraction(1, 6), rec.evidence, Fraction(1, 1)))
        elif rec.priority == PatchPriority.MEDIUM:
            rules.append(_make_rule(len(rules), RuleUpdateKind.PENALIZE_PREDICATE, f"hardening_gap:{rec.target}", Fraction(-1, 12), rec.evidence, Fraction(1, 2)))
        elif rec.priority == PatchPriority.INFO:
            rules.append(_make_rule(len(rules), RuleUpdateKind.REINFORCE_PREDICATE, f"passed_boundary:{rec.target}", Fraction(1, 24), rec.evidence, Fraction(1, 3)))
    return rules


def build_learning_record_from_fuzz(source_hash: str, rules: Sequence[LearnedRule]) -> LearningRecord:
    # Reuse adaptive learning gate with synthetic score anchors represented as support hashes.
    class _Score:
        def __init__(self, h: str):
            self.score_hash72 = h
        def to_dict(self):
            return {"score_hash72": self.score_hash72, "source": "fuzz_analysis"}
    synthetic_scores = [_Score(s) for rule in rules for s in rule.support]
    if not synthetic_scores:
        synthetic_scores = [_Score(hash72_digest(("empty_fuzz_learning", source_hash), width=18))]
    gate = invariant_gate_for_learning(source_hash, synthetic_scores, rules)
    status = LearningStatus.COMMITTED if gate.status == ModificationStatus.APPLIED and rules else LearningStatus.UNCHANGED
    quarantine = None if status != LearningStatus.QUARANTINED else hash72_digest(("fuzz_learning_quarantine", source_hash, gate.to_dict()), width=18)
    h = hash72_digest(("fuzz_learning_record_v1", source_hash, [r.to_dict() for r in rules], gate.receipt_hash72, status.value), width=18)
    return LearningRecord(source_hash, [], list(rules), gate, status, h, quarantine)


def analyze_fuzz_report(
    report: Dict[str, Any],
    *,
    learning_database_path: str | Path = "demo_reports/hhs_adaptive_learning_db_v1.json",
    symbol_cache_path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json",
    ledger_path: str | Path = "demo_reports/hhs_fuzz_learning_ledger_v1.json",
) -> FuzzLearningAnalysis:
    source_hash = hash72_digest(("fuzz_report_source_v1", report), width=18)
    signals = [signal_from_test(item) for item in extract_tests(report)]
    recommendations = recommend_from_signals(signals)
    rules = learned_rules_from_analysis(signals, recommendations)
    learning_record = build_learning_record_from_fuzz(source_hash, rules)

    db = AdaptiveLearningDatabase(learning_database_path)
    db.append_record(learning_record)

    cache = GlobalSymbolCache(symbol_cache_path)
    if learning_record.status == LearningStatus.COMMITTED:
        cache.append_record(
            SymbolEntityType.MEMORY,
            f"fuzz_learning:{source_hash}",
            "memory_record",
            learning_record.to_dict(),
            [OrthogonalChain.MEMORY_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
            relation=AddressRelation(by_symbol=None, from_symbol=None, through_symbol=None, to_symbol=None),
        )

    ledger = MemoryLedger(ledger_path)
    commit = ledger.append_payloads("fuzz_learning_analysis_v1", [s.to_dict() for s in signals] + [r.to_dict() for r in recommendations] + [learning_record.to_dict()])
    replay = replay_ledger(ledger_path)
    report_hash = hash72_digest(("fuzz_learning_analysis_report_v1", source_hash, [s.signal_hash72 for s in signals], [r.recommendation_hash72 for r in recommendations], learning_record.learning_hash72, commit.receipt_hash72, replay.receipt_hash72), width=18)
    return FuzzLearningAnalysis(source_hash, signals, recommendations, rules, learning_record.learning_hash72, commit.to_dict(), replay.to_dict(), report_hash)


def analyze_fuzz_report_file(path: str | Path, **kwargs: Any) -> FuzzLearningAnalysis:
    return analyze_fuzz_report(json.loads(Path(path).read_text(encoding="utf-8")), **kwargs)


def demo() -> Dict[str, Any]:
    report = {
        "tests": [
            {"nodeid": "test_cross_modal_disagreement_quarantines", "outcome": "passed"},
            {"nodeid": "test_web_shell_should_reject_kernel_namespace_patch_even_with_consensus", "outcome": "xfailed", "message": "path allowlist hardening gap"},
            {"nodeid": "test_manifest_tamper_fails_closed", "outcome": "passed"},
        ]
    }
    return analyze_fuzz_report(report, learning_database_path="demo_reports/hhs_fuzz_learning_demo_db_v1.json").to_dict()


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))

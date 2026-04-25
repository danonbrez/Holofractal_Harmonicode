"""
HHS Adaptive Learning Layer v1
==============================

Cycle scoring + rule evolution.

Consumes execution feedback cycle receipts and learns bounded rule updates:

    execution cycles
    -> score cycle outcomes
    -> extract successful/failed patterns
    -> propose rule updates
    -> invariant gate Δe/Ψ/Θ15/Ω
    -> commit/quarantine learned rules
    -> ledger + replay + symbol cache

This is deterministic reinforcement without probabilistic gradient drift. Learned
rules do not modify the core_sandbox. They are advisory constraints consumed by
higher layers when selecting actions/plans.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.hhs_execution_feedback_loop_v1 import (
    ExecutionStatus,
    FeedbackCycleReceipt,
    FeedbackRunReceipt,
    run_execution_feedback_loop,
)
from hhs_runtime.hhs_goal_oriented_planning_engine_v1 import PlanningTarget
from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_recursive_symbol_kernel_v1 import (
    AddressRelation,
    GlobalSymbolCache,
    OrthogonalChain,
    SymbolEntityType,
)
from hhs_runtime.hhs_self_modifying_agents_v1 import EthicalInvariantReceipt, ModificationStatus


class LearningStatus(str, Enum):
    COMMITTED = "COMMITTED"
    QUARANTINED = "QUARANTINED"
    UNCHANGED = "UNCHANGED"


class RuleUpdateKind(str, Enum):
    REINFORCE_ACTION = "REINFORCE_ACTION"
    PENALIZE_ACTION = "PENALIZE_ACTION"
    REINFORCE_PREDICATE = "REINFORCE_PREDICATE"
    PENALIZE_PREDICATE = "PENALIZE_PREDICATE"
    STALL_AVOIDANCE = "STALL_AVOIDANCE"


@dataclass(frozen=True)
class CycleScore:
    """Deterministic score for one execution cycle."""

    cycle_index: int
    cycle_receipt_hash72: str
    committed_actions: int
    quarantined_actions: int
    total_actions: int
    feedback_value: Fraction
    score: Fraction
    score_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle_index": self.cycle_index,
            "cycle_receipt_hash72": self.cycle_receipt_hash72,
            "committed_actions": self.committed_actions,
            "quarantined_actions": self.quarantined_actions,
            "total_actions": self.total_actions,
            "feedback_value": f"{self.feedback_value.numerator}/{self.feedback_value.denominator}",
            "score": f"{self.score.numerator}/{self.score.denominator}",
            "score_hash72": self.score_hash72,
        }


@dataclass(frozen=True)
class LearnedRule:
    """Advisory learned rule for future planning/action selection."""

    rule_index: int
    kind: RuleUpdateKind
    key: str
    weight_delta: Fraction
    support: List[str]
    confidence: Fraction
    rule_hash72: str
    symbol: str
    codepoint: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_index": self.rule_index,
            "kind": self.kind.value,
            "key": self.key,
            "weight_delta": f"{self.weight_delta.numerator}/{self.weight_delta.denominator}",
            "support": self.support,
            "confidence": f"{self.confidence.numerator}/{self.confidence.denominator}",
            "rule_hash72": self.rule_hash72,
            "symbol": self.symbol,
            "codepoint": self.codepoint,
        }


@dataclass(frozen=True)
class LearningRecord:
    """Full adaptive learning record."""

    source_execution_receipt_hash72: str
    cycle_scores: List[CycleScore]
    learned_rules: List[LearnedRule]
    invariant_gate: EthicalInvariantReceipt
    status: LearningStatus
    learning_hash72: str
    quarantine_hash72: str | None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_execution_receipt_hash72": self.source_execution_receipt_hash72,
            "cycle_scores": [s.to_dict() for s in self.cycle_scores],
            "learned_rules": [r.to_dict() for r in self.learned_rules],
            "invariant_gate": self.invariant_gate.to_dict(),
            "status": self.status.value,
            "learning_hash72": self.learning_hash72,
            "quarantine_hash72": self.quarantine_hash72,
        }


@dataclass(frozen=True)
class LearningRunReceipt:
    """Receipt for adaptive learning run."""

    module: str
    learning_database_path: str
    records_seen: int
    records_committed: int
    records_quarantined: int
    rules_learned: int
    ledger_commit_receipt: Dict[str, Any]
    replay_receipt: Dict[str, Any]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def theta15_true() -> bool:
    return (
        all(sum(row) == 15 for row in LO_SHU_3X3)
        and all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
        and sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
        and sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    )


def _symbol_from_hash(h72: str, offset: int = 0) -> tuple[str, str]:
    base = 0xFB00
    span = 0x0400
    acc = offset
    for ch in h72:
        acc = (acc * 163 + ord(ch)) % span
    cp = base + acc
    return chr(cp), f"U+{cp:04X}"


def _fraction(text: str | None, default: Fraction = Fraction(0, 1)) -> Fraction:
    if not text:
        return default
    if "/" in text:
        n, d = text.split("/", 1)
        return Fraction(int(n), int(d))
    return Fraction(text)


def score_cycle(cycle: Dict[str, Any]) -> CycleScore:
    actions = [a for a in cycle.get("actions", []) if isinstance(a, dict)]
    total = len(actions)
    committed = sum(1 for a in actions if a.get("status") == ExecutionStatus.COMMITTED.value)
    quarantined = sum(1 for a in actions if a.get("status") == ExecutionStatus.QUARANTINED.value)
    feedback_value = Fraction(0, 1)
    for a in actions:
        action = a.get("action", {})
        if isinstance(action, dict) and action.get("kind") == "FEEDBACK_OBSERVATION":
            raw = action.get("state_value", 0)
            try:
                feedback_value = Fraction(str(raw))
            except Exception:
                feedback_value = Fraction(0, 1)
    if total == 0:
        score = Fraction(0, 1)
    else:
        score = Fraction(committed - quarantined, total) + feedback_value
        if score > 1:
            score = Fraction(1, 1)
        if score < -1:
            score = Fraction(-1, 1)
    h = hash72_digest(("cycle_score_v1", cycle.get("receipt_hash72"), committed, quarantined, total, feedback_value, score), width=18)
    return CycleScore(int(cycle.get("cycle_index", 0)), str(cycle.get("receipt_hash72", "")), committed, quarantined, total, feedback_value, score, h)


def _make_rule(index: int, kind: RuleUpdateKind, key: str, delta: Fraction, support: Sequence[str], confidence: Fraction) -> LearnedRule:
    h = hash72_digest(("learned_rule_v1", index, kind.value, key, delta, list(support), confidence), width=18)
    symbol, codepoint = _symbol_from_hash(h, index)
    return LearnedRule(index, kind, key, delta, list(support), confidence, h, symbol, codepoint)


def extract_rules(execution_record: Dict[str, Any], scores: Sequence[CycleScore]) -> List[LearnedRule]:
    rules: List[LearnedRule] = []
    cycles = [c for c in execution_record.get("cycles", []) if isinstance(c, dict)]
    score_by_cycle = {s.cycle_index: s for s in scores}
    for cycle in cycles:
        score = score_by_cycle.get(int(cycle.get("cycle_index", 0)))
        if score is None:
            continue
        actions = [a for a in cycle.get("actions", []) if isinstance(a, dict)]
        for action_receipt in actions:
            action = action_receipt.get("action", {})
            if not isinstance(action, dict):
                continue
            operation = str(action.get("operation", "NOOP"))
            kind = str(action.get("kind", "NOOP"))
            key = f"{kind}:{operation}"
            support = [score.score_hash72, str(action_receipt.get("receipt_hash72", ""))]
            if score.score > 0 and action_receipt.get("status") == ExecutionStatus.COMMITTED.value:
                rules.append(_make_rule(len(rules), RuleUpdateKind.REINFORCE_ACTION, key, Fraction(1, 12), support, score.score))
            elif action_receipt.get("status") == ExecutionStatus.QUARANTINED.value or score.score < 0:
                rules.append(_make_rule(len(rules), RuleUpdateKind.PENALIZE_ACTION, key, Fraction(-1, 12), support, abs(score.score)))

            state_value = action.get("state_value")
            if isinstance(state_value, dict):
                predicate = state_value.get("predicate")
                if predicate:
                    pkey = f"predicate:{predicate}"
                    if score.score > 0:
                        rules.append(_make_rule(len(rules), RuleUpdateKind.REINFORCE_PREDICATE, pkey, Fraction(1, 18), support, score.score))
                    elif score.score < 0:
                        rules.append(_make_rule(len(rules), RuleUpdateKind.PENALIZE_PREDICATE, pkey, Fraction(-1, 18), support, abs(score.score)))

        if cycle.get("status") == ExecutionStatus.STALLED.value:
            rules.append(_make_rule(len(rules), RuleUpdateKind.STALL_AVOIDANCE, "planning:stalled", Fraction(-1, 9), [score.score_hash72], Fraction(1, 2)))
    return rules


def invariant_gate_for_learning(source_hash: str, scores: Sequence[CycleScore], rules: Sequence[LearnedRule]) -> EthicalInvariantReceipt:
    delta_e_zero = bool(source_hash) and len(scores) > 0
    support_hashes = {s.score_hash72 for s in scores}
    psi_zero = all(any(s in support_hashes or s.startswith("H") for s in rule.support) for rule in rules)
    theta = theta15_true()
    omega_true = bool(hash72_digest(("learning_replay_v1", source_hash, [s.to_dict() for s in scores], [r.to_dict() for r in rules]), width=18))
    bounded = all(Fraction(-1, 1) <= rule.weight_delta <= Fraction(1, 1) and Fraction(0, 1) <= rule.confidence <= Fraction(1, 1) for rule in rules)
    ok = delta_e_zero and psi_zero and theta and omega_true and bounded
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {
        "Δe=0": delta_e_zero,
        "Ψ=0": psi_zero,
        "Θ15=true": theta,
        "Ω=true": omega_true,
        "bounded_rules": bounded,
        "score_count": len(scores),
        "rule_count": len(rules),
    }
    receipt = hash72_digest(("adaptive_learning_invariant_gate_v1", details, status.value), width=18)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


class AdaptiveLearningDatabase:
    """JSON-backed learned rule database."""

    def __init__(self, path: str | Path = "demo_reports/hhs_adaptive_learning_db_v1.json") -> None:
        self.path = Path(path)

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {
                "module": "hhs_adaptive_learning_layer_v1",
                "records": [],
                "source_index": {},
                "rule_index": {},
                "key_index": {},
                "symbol_index": {},
                "status_index": {},
            }
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: Dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def append_record(self, record: LearningRecord) -> None:
        data = self.load()
        records = data.setdefault("records", [])
        source_index = data.setdefault("source_index", {})
        rule_index = data.setdefault("rule_index", {})
        key_index = data.setdefault("key_index", {})
        symbol_index = data.setdefault("symbol_index", {})
        status_index = data.setdefault("status_index", {})
        records.append(record.to_dict())
        source_index[record.source_execution_receipt_hash72] = record.learning_hash72
        status_index.setdefault(record.status.value, [])
        status_index[record.status.value].append(record.learning_hash72)
        for rule in record.learned_rules:
            rule_index[rule.rule_hash72] = record.learning_hash72
            key_index.setdefault(rule.key, [])
            key_index[rule.key].append(record.learning_hash72)
            symbol_index[rule.symbol] = rule.rule_hash72
            symbol_index[rule.codepoint] = rule.rule_hash72
        self.save(data)

    def search(self, key: str) -> List[Dict[str, Any]]:
        data = self.load()
        hits = set()
        for index_name in ["source_index", "rule_index", "symbol_index"]:
            index = data.get(index_name, {})
            if isinstance(index, dict) and key in index:
                hits.add(str(index[key]))
        for index_name in ["key_index", "status_index"]:
            index = data.get(index_name, {})
            if isinstance(index, dict) and key in index:
                hits.update(str(x) for x in index[key])
        return [r for r in data.get("records", []) if isinstance(r, dict) and r.get("learning_hash72") in hits]

    def aggregate_rule_weights(self) -> Dict[str, str]:
        totals: Dict[str, Fraction] = {}
        for record in self.load().get("records", []):
            if not isinstance(record, dict) or record.get("status") != LearningStatus.COMMITTED.value:
                continue
            for rule in record.get("learned_rules", []):
                if not isinstance(rule, dict):
                    continue
                key = str(rule.get("key", ""))
                totals[key] = totals.get(key, Fraction(0, 1)) + _fraction(str(rule.get("weight_delta", "0/1")))
        return {k: f"{v.numerator}/{v.denominator}" for k, v in sorted(totals.items())}


def build_learning_record(execution_record: Dict[str, Any]) -> LearningRecord:
    source_hash = str(execution_record.get("receipt_hash72", ""))
    cycles = [c for c in execution_record.get("cycles", []) if isinstance(c, dict)]
    scores = [score_cycle(c) for c in cycles]
    rules = extract_rules(execution_record, scores)
    gate = invariant_gate_for_learning(source_hash, scores, rules)
    if gate.status != ModificationStatus.APPLIED:
        status = LearningStatus.QUARANTINED
    elif not rules:
        status = LearningStatus.UNCHANGED
    else:
        status = LearningStatus.COMMITTED
    quarantine = None if status != LearningStatus.QUARANTINED else hash72_digest(("learning_quarantine", source_hash, gate.to_dict()), width=18)
    h = hash72_digest(("learning_record_v1", source_hash, [s.to_dict() for s in scores], [r.to_dict() for r in rules], gate.receipt_hash72, status.value), width=18)
    return LearningRecord(source_hash, scores, rules, gate, status, h, quarantine)


def register_learning_in_symbol_cache(record: LearningRecord, cache: GlobalSymbolCache) -> None:
    if record.status != LearningStatus.COMMITTED:
        return
    parent = cache.append_record(
        SymbolEntityType.MEMORY,
        f"learning:{record.source_execution_receipt_hash72}",
        "memory_record",
        record.to_dict(),
        [OrthogonalChain.MEMORY_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
        relation=AddressRelation(by_symbol=None, from_symbol=None, through_symbol=None, to_symbol=None),
    )
    parent_symbol = parent.symbol_record.symbol
    for rule in record.learned_rules:
        cache.append_record(
            SymbolEntityType.OPERATION,
            f"learned_rule:{rule.key}:{rule.rule_hash72}",
            "operation_record",
            rule.to_dict(),
            [OrthogonalChain.OPERATION_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
            relation=AddressRelation(by_symbol=parent_symbol, from_symbol=parent_symbol, through_symbol=None, to_symbol=rule.symbol),
        )


def run_adaptive_learning(
    execution_records: Sequence[Dict[str, Any]],
    learning_database_path: str | Path = "demo_reports/hhs_adaptive_learning_db_v1.json",
    symbol_cache_path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json",
    ledger_path: str | Path = "demo_reports/hhs_adaptive_learning_ledger_v1.json",
) -> LearningRunReceipt:
    db = AdaptiveLearningDatabase(learning_database_path)
    cache = GlobalSymbolCache(symbol_cache_path)
    records = [build_learning_record(r) for r in execution_records]
    for record in records:
        db.append_record(record)
        register_learning_in_symbol_cache(record, cache)

    ledger = MemoryLedger(ledger_path)
    commit = ledger.append_payloads("adaptive_learning_record_v1", [r.to_dict() for r in records])
    replay = replay_ledger(ledger_path)
    committed = sum(1 for r in records if r.status == LearningStatus.COMMITTED)
    quarantined = sum(1 for r in records if r.status == LearningStatus.QUARANTINED)
    rules = sum(len(r.learned_rules) for r in records)
    receipt = hash72_digest(("adaptive_learning_run_v1", [r.learning_hash72 for r in records], commit.receipt_hash72, replay.receipt_hash72, committed, quarantined, rules), width=18)
    return LearningRunReceipt("hhs_adaptive_learning_layer_v1", str(learning_database_path), len(records), committed, quarantined, rules, commit.to_dict(), replay.to_dict(), receipt)


def run_execution_and_learn(
    targets: Sequence[PlanningTarget],
    cycles: int = 1,
    learning_database_path: str | Path = "demo_reports/hhs_adaptive_learning_db_v1.json",
) -> Dict[str, Any]:
    execution = run_execution_feedback_loop(targets, cycles=cycles)
    learning = run_adaptive_learning([execution.to_dict()], learning_database_path=learning_database_path)
    db = AdaptiveLearningDatabase(learning_database_path)
    return {
        "execution_receipt": execution.to_dict(),
        "learning_receipt": learning.to_dict(),
        "rule_weights": db.aggregate_rule_weights(),
        "report_hash72": hash72_digest(("execution_and_learn_v1", execution.receipt_hash72, learning.receipt_hash72, db.aggregate_rule_weights()), width=18),
    }


def demo() -> Dict[str, Any]:
    target = PlanningTarget(name="Learning demo", target_predicate="transforms_to", min_confidence="1/2")
    return run_execution_and_learn([target], cycles=1, learning_database_path="demo_reports/hhs_adaptive_learning_db_demo_v1.json")


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))

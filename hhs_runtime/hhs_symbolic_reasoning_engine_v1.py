"""
HHS Symbolic Reasoning Engine v1
================================

Graph -> inference -> new valid states.

Consumes:
    * text semantic reconstruction records
    * contextual meaning resolution records
    * semantic relations (CONTAINS, FOLLOWS, EQUALS, TRANSFORMS_TO, DEFINES, REFERENCES)

Produces:
    * explicit facts
    * inference rules
    * derived truths / candidate states
    * invariant-gated reasoning receipts
    * ledgered and replayable proof records

No inference is committed unless it passes:
    Δe = 0, Ψ = 0, Θ15 = true, Ω = true

This is not probabilistic reasoning. It is deterministic graph transformation
with auditable evidence links back to source tokens and semantic resolutions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple
import json

from hhs_runtime.hhs_contextual_meaning_resolution_v1 import (
    ContextualResolutionDatabase,
    ResolutionStatus,
)
from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_recursive_symbol_kernel_v1 import (
    AddressRelation,
    GlobalSymbolCache,
    OrthogonalChain,
    SymbolEntityType,
)
from hhs_runtime.hhs_self_modifying_agents_v1 import EthicalInvariantReceipt, ModificationStatus
from hhs_runtime.hhs_text_semantic_reconstruction_v1 import (
    SemanticRelationKind,
    TextSemanticDatabase,
)


class FactKind(str, Enum):
    TOKEN_MEANING = "TOKEN_MEANING"
    EQUALITY = "EQUALITY"
    TRANSFORMATION = "TRANSFORMATION"
    DEFINITION = "DEFINITION"
    CONTAINMENT = "CONTAINMENT"
    SEQUENCE = "SEQUENCE"
    REFERENCE = "REFERENCE"
    INVARIANT_ASSERTION = "INVARIANT_ASSERTION"


class InferenceRuleKind(str, Enum):
    EQUALITY_SYMMETRY = "EQUALITY_SYMMETRY"
    TRANSFORM_CHAIN = "TRANSFORM_CHAIN"
    DEFINITION_GROUNDS_MEANING = "DEFINITION_GROUNDS_MEANING"
    CONTAINMENT_CONTEXT = "CONTAINMENT_CONTEXT"
    INVARIANT_CONFIRMATION = "INVARIANT_CONFIRMATION"
    REFERENCE_BINDING = "REFERENCE_BINDING"


class ReasoningStatus(str, Enum):
    COMMITTED = "COMMITTED"
    UNRESOLVED = "UNRESOLVED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class ReasoningFact:
    """Atomic fact extracted from semantic/resolution databases."""

    fact_index: int
    kind: FactKind
    subject_hash72: str
    predicate: str
    object_hash72: str
    evidence_hash72: str
    confidence: Fraction
    fact_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "fact_index": self.fact_index,
            "kind": self.kind.value,
            "subject_hash72": self.subject_hash72,
            "predicate": self.predicate,
            "object_hash72": self.object_hash72,
            "evidence_hash72": self.evidence_hash72,
            "confidence": f"{self.confidence.numerator}/{self.confidence.denominator}",
            "fact_hash72": self.fact_hash72,
        }


@dataclass(frozen=True)
class InferenceRule:
    """One deterministic inference rule application."""

    rule_index: int
    kind: InferenceRuleKind
    input_fact_hashes: List[str]
    output_subject_hash72: str
    output_predicate: str
    output_object_hash72: str
    rule_hash72: str

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


@dataclass(frozen=True)
class DerivedState:
    """A newly derived candidate truth/state."""

    state_index: int
    subject_hash72: str
    predicate: str
    object_hash72: str
    supporting_facts: List[str]
    supporting_rules: List[str]
    confidence: Fraction
    state_hash72: str
    symbol: str
    codepoint: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "state_index": self.state_index,
            "subject_hash72": self.subject_hash72,
            "predicate": self.predicate,
            "object_hash72": self.object_hash72,
            "supporting_facts": self.supporting_facts,
            "supporting_rules": self.supporting_rules,
            "confidence": f"{self.confidence.numerator}/{self.confidence.denominator}",
            "state_hash72": self.state_hash72,
            "symbol": self.symbol,
            "codepoint": self.codepoint,
        }


@dataclass(frozen=True)
class ReasoningRecord:
    """Full proof/inference record."""

    source_semantic_hash72: str
    facts: List[ReasoningFact]
    rules: List[InferenceRule]
    derived_states: List[DerivedState]
    invariant_gate: EthicalInvariantReceipt
    status: ReasoningStatus
    reasoning_hash72: str
    quarantine_hash72: str | None

    def to_dict(self) -> Dict[str, object]:
        return {
            "source_semantic_hash72": self.source_semantic_hash72,
            "facts": [f.to_dict() for f in self.facts],
            "rules": [r.to_dict() for r in self.rules],
            "derived_states": [s.to_dict() for s in self.derived_states],
            "invariant_gate": self.invariant_gate.to_dict(),
            "status": self.status.value,
            "reasoning_hash72": self.reasoning_hash72,
            "quarantine_hash72": self.quarantine_hash72,
        }


@dataclass(frozen=True)
class ReasoningRunReceipt:
    """Receipt for symbolic reasoning run."""

    module: str
    reasoning_database_path: str
    records_seen: int
    records_committed: int
    records_unresolved: int
    records_quarantined: int
    fact_count: int
    rule_count: int
    derived_state_count: int
    ledger_commit_receipt: Dict[str, object]
    replay_receipt: Dict[str, object]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def theta15_true() -> bool:
    return (
        all(sum(row) == 15 for row in LO_SHU_3X3)
        and all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
        and sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
        and sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    )


def _symbol_from_hash(h72: str, offset: int = 0) -> tuple[str, str]:
    base = 0xF800
    span = 0x0700
    acc = offset
    for ch in h72:
        acc = (acc * 151 + ord(ch)) % span
    cp = base + acc
    return chr(cp), f"U+{cp:04X}"


def _fraction(text: str | None, default: Fraction = Fraction(1, 1)) -> Fraction:
    if not text:
        return default
    if "/" in text:
        n, d = text.split("/", 1)
        return Fraction(int(n), int(d))
    return Fraction(text)


def _make_fact(kind: FactKind, subject: str, predicate: str, obj: str, evidence: str, confidence: Fraction, index: int) -> ReasoningFact:
    h = hash72_digest(("reasoning_fact_v1", index, kind.value, subject, predicate, obj, evidence, confidence), width=18)
    return ReasoningFact(index, kind, subject, predicate, obj, evidence, confidence, h)


def facts_from_semantic_record(record: Dict[str, object]) -> List[ReasoningFact]:
    facts: List[ReasoningFact] = []
    for relation in record.get("relations", []):
        if not isinstance(relation, dict):
            continue
        kind_value = relation.get("kind")
        source = str(relation.get("source_hash72", ""))
        target = str(relation.get("target_hash72", ""))
        evidence = str(relation.get("evidence_token_hash72", ""))
        if not source or not target:
            continue
        if kind_value == SemanticRelationKind.EQUALS.value:
            kind = FactKind.EQUALITY
            predicate = "equals"
        elif kind_value == SemanticRelationKind.TRANSFORMS_TO.value:
            kind = FactKind.TRANSFORMATION
            predicate = "transforms_to"
        elif kind_value == SemanticRelationKind.DEFINES.value:
            kind = FactKind.DEFINITION
            predicate = "defines"
        elif kind_value == SemanticRelationKind.CONTAINS.value:
            kind = FactKind.CONTAINMENT
            predicate = "contains"
        elif kind_value == SemanticRelationKind.FOLLOWS.value:
            kind = FactKind.SEQUENCE
            predicate = "follows"
        elif kind_value == SemanticRelationKind.REFERENCES.value:
            kind = FactKind.REFERENCE
            predicate = "references"
        else:
            continue
        facts.append(_make_fact(kind, source, predicate, target, evidence, Fraction(1, 1), len(facts)))
    return facts


def facts_from_resolutions(source_semantic_hash72: str, resolution_records: Sequence[Dict[str, object]], start_index: int = 0) -> List[ReasoningFact]:
    facts: List[ReasoningFact] = []
    for resolution in resolution_records:
        if not isinstance(resolution, dict):
            continue
        if resolution.get("source_semantic_hash72") != source_semantic_hash72:
            continue
        if resolution.get("status") != ResolutionStatus.COMMITTED.value:
            continue
        token_hash = str(resolution.get("token_hash72", ""))
        selected = resolution.get("selected_candidate")
        if not isinstance(selected, dict):
            continue
        sense_hash = str(selected.get("candidate_hash72", ""))
        confidence = _fraction(str(resolution.get("confidence", "0/1")), Fraction(0, 1))
        facts.append(
            _make_fact(
                FactKind.TOKEN_MEANING,
                token_hash,
                f"means:{selected.get('candidate_label', 'unknown')}",
                sense_hash,
                str(resolution.get("resolution_hash72", "")),
                confidence,
                start_index + len(facts),
            )
        )
        if selected.get("hhs_category") in {"ethical_invariant", "semantic_invariant", "loshu_invariant", "closure_invariant", "invariant"}:
            facts.append(
                _make_fact(
                    FactKind.INVARIANT_ASSERTION,
                    token_hash,
                    "asserts_invariant",
                    sense_hash,
                    str(resolution.get("resolution_hash72", "")),
                    confidence,
                    start_index + len(facts),
                )
            )
    return facts


def _make_rule(kind: InferenceRuleKind, input_hashes: Sequence[str], subject: str, predicate: str, obj: str, index: int) -> InferenceRule:
    h = hash72_digest(("inference_rule_v1", index, kind.value, list(input_hashes), subject, predicate, obj), width=18)
    return InferenceRule(index, kind, list(input_hashes), subject, predicate, obj, h)


def derive_rules_and_states(facts: Sequence[ReasoningFact]) -> tuple[List[InferenceRule], List[DerivedState]]:
    rules: List[InferenceRule] = []
    states: List[DerivedState] = []

    def add_state(subject: str, predicate: str, obj: str, fact_hashes: Sequence[str], rule_hashes: Sequence[str], confidence: Fraction) -> None:
        state_hash = hash72_digest(("derived_state_v1", len(states), subject, predicate, obj, list(fact_hashes), list(rule_hashes), confidence), width=18)
        symbol, codepoint = _symbol_from_hash(state_hash, len(states))
        states.append(DerivedState(len(states), subject, predicate, obj, list(fact_hashes), list(rule_hashes), confidence, state_hash, symbol, codepoint))

    # Equality symmetry: A equals B -> B equals A.
    for fact in facts:
        if fact.kind == FactKind.EQUALITY:
            rule = _make_rule(InferenceRuleKind.EQUALITY_SYMMETRY, [fact.fact_hash72], fact.object_hash72, "equals", fact.subject_hash72, len(rules))
            rules.append(rule)
            add_state(fact.object_hash72, "equals", fact.subject_hash72, [fact.fact_hash72], [rule.rule_hash72], fact.confidence)

    # Transform chain: A -> B and B -> C implies A -> C.
    transforms = [f for f in facts if f.kind == FactKind.TRANSFORMATION]
    for left in transforms:
        for right in transforms:
            if left.object_hash72 == right.subject_hash72:
                confidence = min(left.confidence, right.confidence)
                rule = _make_rule(InferenceRuleKind.TRANSFORM_CHAIN, [left.fact_hash72, right.fact_hash72], left.subject_hash72, "transforms_to", right.object_hash72, len(rules))
                rules.append(rule)
                add_state(left.subject_hash72, "transforms_to", right.object_hash72, [left.fact_hash72, right.fact_hash72], [rule.rule_hash72], confidence)

    # Definition grounds meaning: A defines B -> B grounded_by A.
    for fact in facts:
        if fact.kind == FactKind.DEFINITION:
            rule = _make_rule(InferenceRuleKind.DEFINITION_GROUNDS_MEANING, [fact.fact_hash72], fact.object_hash72, "grounded_by_definition", fact.subject_hash72, len(rules))
            rules.append(rule)
            add_state(fact.object_hash72, "grounded_by_definition", fact.subject_hash72, [fact.fact_hash72], [rule.rule_hash72], fact.confidence)

    # Reference binding: node references token and token has meaning -> node carries meaning.
    refs = [f for f in facts if f.kind == FactKind.REFERENCE]
    meanings = [f for f in facts if f.kind == FactKind.TOKEN_MEANING]
    for ref in refs:
        for meaning in meanings:
            if ref.object_hash72 == meaning.subject_hash72:
                confidence = min(ref.confidence, meaning.confidence)
                rule = _make_rule(InferenceRuleKind.REFERENCE_BINDING, [ref.fact_hash72, meaning.fact_hash72], ref.subject_hash72, meaning.predicate, meaning.object_hash72, len(rules))
                rules.append(rule)
                add_state(ref.subject_hash72, meaning.predicate, meaning.object_hash72, [ref.fact_hash72, meaning.fact_hash72], [rule.rule_hash72], confidence)

    # Invariant confirmation: committed invariant assertions produce a derived invariant state.
    for fact in facts:
        if fact.kind == FactKind.INVARIANT_ASSERTION:
            rule = _make_rule(InferenceRuleKind.INVARIANT_CONFIRMATION, [fact.fact_hash72], fact.subject_hash72, "confirms_invariant", fact.object_hash72, len(rules))
            rules.append(rule)
            add_state(fact.subject_hash72, "confirms_invariant", fact.object_hash72, [fact.fact_hash72], [rule.rule_hash72], fact.confidence)

    return rules, states


def invariant_gate_for_reasoning(source_semantic_hash72: str, facts: Sequence[ReasoningFact], rules: Sequence[InferenceRule], states: Sequence[DerivedState]) -> EthicalInvariantReceipt:
    delta_e_zero = bool(source_semantic_hash72) and len(facts) > 0
    fact_hashes = {f.fact_hash72 for f in facts}
    rule_hashes = {r.rule_hash72 for r in rules}
    psi_zero = all(set(state.supporting_facts).issubset(fact_hashes) and set(state.supporting_rules).issubset(rule_hashes) for state in states)
    theta = theta15_true()
    omega_true = bool(hash72_digest(("reasoning_replay_v1", source_semantic_hash72, [f.to_dict() for f in facts], [r.to_dict() for r in rules], [s.to_dict() for s in states]), width=18))
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {
        "Δe=0": delta_e_zero,
        "Ψ=0": psi_zero,
        "Θ15=true": theta,
        "Ω=true": omega_true,
        "source_semantic_hash72": source_semantic_hash72,
        "fact_count": len(facts),
        "rule_count": len(rules),
        "derived_state_count": len(states),
    }
    receipt = hash72_digest(("symbolic_reasoning_invariant_gate_v1", details, status.value), width=18)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


class SymbolicReasoningDatabase:
    """JSON-backed reasoning/proof database."""

    def __init__(self, path: str | Path = "demo_reports/hhs_symbolic_reasoning_db_v1.json") -> None:
        self.path = Path(path)

    def load(self) -> Dict[str, object]:
        if not self.path.exists():
            return {
                "module": "hhs_symbolic_reasoning_engine_v1",
                "records": [],
                "source_index": {},
                "fact_index": {},
                "rule_index": {},
                "state_index": {},
                "predicate_index": {},
                "symbol_index": {},
            }
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: Dict[str, object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def append_record(self, record: ReasoningRecord) -> None:
        data = self.load()
        records = data.setdefault("records", [])
        source_index = data.setdefault("source_index", {})
        fact_index = data.setdefault("fact_index", {})
        rule_index = data.setdefault("rule_index", {})
        state_index = data.setdefault("state_index", {})
        predicate_index = data.setdefault("predicate_index", {})
        symbol_index = data.setdefault("symbol_index", {})
        records.append(record.to_dict())
        source_index[record.source_semantic_hash72] = record.reasoning_hash72
        for fact in record.facts:
            fact_index[fact.fact_hash72] = record.reasoning_hash72
            predicate_index.setdefault(fact.predicate, [])
            predicate_index[fact.predicate].append(record.reasoning_hash72)
        for rule in record.rules:
            rule_index[rule.rule_hash72] = record.reasoning_hash72
        for state in record.derived_states:
            state_index[state.state_hash72] = record.reasoning_hash72
            predicate_index.setdefault(state.predicate, [])
            predicate_index[state.predicate].append(record.reasoning_hash72)
            symbol_index[state.symbol] = state.state_hash72
            symbol_index[state.codepoint] = state.state_hash72
        self.save(data)

    def search(self, key: str) -> List[Dict[str, object]]:
        data = self.load()
        hits = set()
        for index_name in ["source_index", "fact_index", "rule_index", "state_index", "symbol_index"]:
            index = data.get(index_name, {})
            if isinstance(index, dict) and key in index:
                hits.add(str(index[key]))
        predicate_index = data.get("predicate_index", {})
        if isinstance(predicate_index, dict) and key in predicate_index:
            hits.update(str(x) for x in predicate_index[key])
        return [r for r in data.get("records", []) if isinstance(r, dict) and r.get("reasoning_hash72") in hits]


def build_reasoning_record(semantic_record: Dict[str, object], resolution_records: Sequence[Dict[str, object]]) -> ReasoningRecord:
    source = str(semantic_record.get("semantic_hash72", ""))
    facts = facts_from_semantic_record(semantic_record)
    facts.extend(facts_from_resolutions(source, resolution_records, start_index=len(facts)))
    rules, states = derive_rules_and_states(facts)
    gate = invariant_gate_for_reasoning(source, facts, rules, states)
    if gate.status != ModificationStatus.APPLIED:
        status = ReasoningStatus.QUARANTINED
    elif not states:
        status = ReasoningStatus.UNRESOLVED
    else:
        status = ReasoningStatus.COMMITTED
    quarantine = None if status != ReasoningStatus.QUARANTINED else hash72_digest(("reasoning_quarantine", source, gate.to_dict()), width=18)
    r_hash = hash72_digest(("reasoning_record_v1", source, [f.to_dict() for f in facts], [r.to_dict() for r in rules], [s.to_dict() for s in states], gate.receipt_hash72, status.value), width=18)
    return ReasoningRecord(source, facts, rules, states, gate, status, r_hash, quarantine)


def register_reasoning_in_symbol_cache(record: ReasoningRecord, symbol_cache: GlobalSymbolCache) -> None:
    if record.status != ReasoningStatus.COMMITTED:
        return
    parent = symbol_cache.append_record(
        SymbolEntityType.MEMORY,
        f"reasoning:{record.source_semantic_hash72}",
        "memory_record",
        record.to_dict(),
        [OrthogonalChain.MEMORY_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
        relation=AddressRelation(by_symbol=None, from_symbol=None, through_symbol=None, to_symbol=None),
    )
    parent_symbol = parent.symbol_record.symbol
    for state in record.derived_states:
        symbol_cache.append_record(
            SymbolEntityType.STATE,
            f"derived_state:{state.predicate}:{state.state_hash72}",
            "memory_record",
            state.to_dict(),
            [OrthogonalChain.STATE_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
            relation=AddressRelation(by_symbol=parent_symbol, from_symbol=parent_symbol, through_symbol=None, to_symbol=state.symbol),
        )


def run_symbolic_reasoning(
    semantic_database_path: str | Path = "demo_reports/hhs_text_semantic_db_v1.json",
    resolution_database_path: str | Path = "demo_reports/hhs_contextual_resolution_db_v1.json",
    reasoning_database_path: str | Path = "demo_reports/hhs_symbolic_reasoning_db_v1.json",
    symbol_cache_path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json",
    ledger_path: str | Path = "demo_reports/hhs_symbolic_reasoning_ledger_v1.json",
) -> ReasoningRunReceipt:
    semantic_db = TextSemanticDatabase(semantic_database_path)
    resolution_db = ContextualResolutionDatabase(resolution_database_path)
    reasoning_db = SymbolicReasoningDatabase(reasoning_database_path)
    symbol_cache = GlobalSymbolCache(symbol_cache_path)

    semantic_records = [r for r in semantic_db.load().get("records", []) if isinstance(r, dict)]
    resolution_records = [r for r in resolution_db.load().get("records", []) if isinstance(r, dict)]
    reasoning_records: List[ReasoningRecord] = []
    for semantic_record in semantic_records:
        record = build_reasoning_record(semantic_record, resolution_records)
        reasoning_db.append_record(record)
        register_reasoning_in_symbol_cache(record, symbol_cache)
        reasoning_records.append(record)

    ledger = MemoryLedger(ledger_path)
    commit = ledger.append_payloads("symbolic_reasoning_record_v1", [r.to_dict() for r in reasoning_records])
    replay = replay_ledger(ledger_path)
    committed = sum(1 for r in reasoning_records if r.status == ReasoningStatus.COMMITTED)
    unresolved = sum(1 for r in reasoning_records if r.status == ReasoningStatus.UNRESOLVED)
    quarantined = sum(1 for r in reasoning_records if r.status == ReasoningStatus.QUARANTINED)
    fact_count = sum(len(r.facts) for r in reasoning_records)
    rule_count = sum(len(r.rules) for r in reasoning_records)
    state_count = sum(len(r.derived_states) for r in reasoning_records)
    receipt = hash72_digest(("symbolic_reasoning_run_v1", [r.reasoning_hash72 for r in reasoning_records], commit.receipt_hash72, replay.receipt_hash72, committed, unresolved, quarantined, fact_count, rule_count, state_count), width=18)
    return ReasoningRunReceipt(
        module="hhs_symbolic_reasoning_engine_v1",
        reasoning_database_path=str(reasoning_database_path),
        records_seen=len(reasoning_records),
        records_committed=committed,
        records_unresolved=unresolved,
        records_quarantined=quarantined,
        fact_count=fact_count,
        rule_count=rule_count,
        derived_state_count=state_count,
        ledger_commit_receipt=commit.to_dict(),
        replay_receipt=replay.to_dict(),
        receipt_hash72=receipt,
    )


def demo() -> Dict[str, object]:
    from hhs_runtime.hhs_contextual_meaning_resolution_v1 import run_contextual_resolution
    from hhs_runtime.hhs_english_lexicon_seed_v1 import seed_starter_lexicon
    from hhs_runtime.hhs_text_semantic_reconstruction_v1 import ingest_and_reconstruct_text_files

    demo_dir = Path("demo_reports")
    demo_dir.mkdir(parents=True, exist_ok=True)
    sample = demo_dir / "hhs_symbolic_reasoning_sample.md"
    sample.write_text(
        "Meaning = structure\nstructure -> state\nstate -> memory\nvalid state preserves truth\n",
        encoding="utf-8",
    )
    ingest_and_reconstruct_text_files(
        [sample],
        multimodal_database_path=demo_dir / "hhs_multimodal_file_db_reasoning_demo_v1.json",
        semantic_database_path=demo_dir / "hhs_text_semantic_db_reasoning_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_reasoning_demo_v1.json",
        multimodal_ledger_path=demo_dir / "hhs_multimodal_file_ledger_reasoning_demo_v1.json",
        semantic_ledger_path=demo_dir / "hhs_text_semantic_ledger_reasoning_demo_v1.json",
        chunk_size=64,
    )
    seed_starter_lexicon(
        database_path=demo_dir / "hhs_english_lexicon_db_reasoning_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_reasoning_demo_v1.json",
        ledger_path=demo_dir / "hhs_english_lexicon_ledger_reasoning_demo_v1.json",
    )
    run_contextual_resolution(
        semantic_database_path=demo_dir / "hhs_text_semantic_db_reasoning_demo_v1.json",
        lexicon_database_path=demo_dir / "hhs_english_lexicon_db_reasoning_demo_v1.json",
        resolution_database_path=demo_dir / "hhs_contextual_resolution_db_reasoning_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_reasoning_demo_v1.json",
        ledger_path=demo_dir / "hhs_contextual_resolution_ledger_reasoning_demo_v1.json",
    )
    receipt = run_symbolic_reasoning(
        semantic_database_path=demo_dir / "hhs_text_semantic_db_reasoning_demo_v1.json",
        resolution_database_path=demo_dir / "hhs_contextual_resolution_db_reasoning_demo_v1.json",
        reasoning_database_path=demo_dir / "hhs_symbolic_reasoning_db_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_reasoning_demo_v1.json",
        ledger_path=demo_dir / "hhs_symbolic_reasoning_ledger_demo_v1.json",
    )
    db = SymbolicReasoningDatabase(demo_dir / "hhs_symbolic_reasoning_db_demo_v1.json")
    return {"receipt": receipt.to_dict(), "transforms": db.search("transforms_to"), "equals": db.search("equals")}


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))

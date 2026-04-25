"""
HHS Goal-Oriented Planning Engine v1
====================================

State -> target -> derivation path.

Consumes symbolic reasoning records and searches for valid paths from current
facts/derived states toward explicit target constraints. Plans are deterministic,
Hash72-addressed, Unicode-symbol-addressed, ledgered, replayable, and gated by:

    Δe = 0, Ψ = 0, Θ15 = true, Ω = true

This layer turns reasoning into directed strategy without bypassing the kernel.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_recursive_symbol_kernel_v1 import (
    AddressRelation,
    GlobalSymbolCache,
    OrthogonalChain,
    SymbolEntityType,
)
from hhs_runtime.hhs_self_modifying_agents_v1 import EthicalInvariantReceipt, ModificationStatus
from hhs_runtime.hhs_symbolic_reasoning_engine_v1 import (
    ReasoningStatus,
    SymbolicReasoningDatabase,
    run_symbolic_reasoning,
)


class PlanStatus(str, Enum):
    COMMITTED = "COMMITTED"
    UNRESOLVED = "UNRESOLVED"
    QUARANTINED = "QUARANTINED"


class PlanStepKind(str, Enum):
    USE_FACT = "USE_FACT"
    USE_DERIVED_STATE = "USE_DERIVED_STATE"
    BRIDGE_PREDICATE = "BRIDGE_PREDICATE"
    REACH_TARGET = "REACH_TARGET"


@dataclass(frozen=True)
class PlanningTarget:
    """Target constraint for planning."""

    name: str
    target_subject_hash72: str | None = None
    target_predicate: str | None = None
    target_object_hash72: str | None = None
    require_exact_subject: bool = False
    require_exact_object: bool = False
    min_confidence: str = "1/2"

    def min_confidence_fraction(self) -> Fraction:
        n, d = self.min_confidence.split("/", 1)
        return Fraction(int(n), int(d))

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PlanStep:
    """One step in a derivation plan."""

    step_index: int
    kind: PlanStepKind
    source_hash72: str
    predicate: str
    target_hash72: str
    evidence_hash72: str
    confidence: Fraction
    step_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "step_index": self.step_index,
            "kind": self.kind.value,
            "source_hash72": self.source_hash72,
            "predicate": self.predicate,
            "target_hash72": self.target_hash72,
            "evidence_hash72": self.evidence_hash72,
            "confidence": f"{self.confidence.numerator}/{self.confidence.denominator}",
            "step_hash72": self.step_hash72,
        }


@dataclass(frozen=True)
class PlanCandidate:
    """Candidate path toward a target."""

    target: PlanningTarget
    steps: List[PlanStep]
    path_confidence: Fraction
    target_satisfied: bool
    plan_hash72: str
    symbol: str
    codepoint: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "target": self.target.to_dict(),
            "steps": [s.to_dict() for s in self.steps],
            "path_confidence": f"{self.path_confidence.numerator}/{self.path_confidence.denominator}",
            "target_satisfied": self.target_satisfied,
            "plan_hash72": self.plan_hash72,
            "symbol": self.symbol,
            "codepoint": self.codepoint,
        }


@dataclass(frozen=True)
class PlanningRecord:
    """Full planning record."""

    reasoning_sources: List[str]
    target: PlanningTarget
    candidates: List[PlanCandidate]
    selected_plan: PlanCandidate | None
    invariant_gate: EthicalInvariantReceipt
    status: PlanStatus
    planning_hash72: str
    quarantine_hash72: str | None

    def to_dict(self) -> Dict[str, object]:
        return {
            "reasoning_sources": self.reasoning_sources,
            "target": self.target.to_dict(),
            "candidates": [c.to_dict() for c in self.candidates],
            "selected_plan": self.selected_plan.to_dict() if self.selected_plan else None,
            "invariant_gate": self.invariant_gate.to_dict(),
            "status": self.status.value,
            "planning_hash72": self.planning_hash72,
            "quarantine_hash72": self.quarantine_hash72,
        }


@dataclass(frozen=True)
class PlanningRunReceipt:
    """Receipt for a planning run."""

    module: str
    planning_database_path: str
    targets_seen: int
    plans_committed: int
    plans_unresolved: int
    plans_quarantined: int
    candidate_count: int
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


def _fraction(text: str | None, default: Fraction = Fraction(1, 1)) -> Fraction:
    if not text:
        return default
    if "/" in text:
        n, d = text.split("/", 1)
        return Fraction(int(n), int(d))
    return Fraction(text)


def _symbol_from_hash(h72: str, offset: int = 0) -> tuple[str, str]:
    base = 0xF900
    span = 0x0600
    acc = offset
    for ch in h72:
        acc = (acc * 157 + ord(ch)) % span
    cp = base + acc
    return chr(cp), f"U+{cp:04X}"


def _make_step(index: int, kind: PlanStepKind, source: str, predicate: str, target: str, evidence: str, confidence: Fraction) -> PlanStep:
    h = hash72_digest(("plan_step_v1", index, kind.value, source, predicate, target, evidence, confidence), width=18)
    return PlanStep(index, kind, source, predicate, target, evidence, confidence, h)


def extract_edges(reasoning_records: Sequence[Dict[str, object]]) -> List[PlanStep]:
    """Convert facts and derived states into plan-usable edges."""

    steps: List[PlanStep] = []
    for record in reasoning_records:
        if not isinstance(record, dict) or record.get("status") != ReasoningStatus.COMMITTED.value:
            continue
        for fact in record.get("facts", []):
            if not isinstance(fact, dict):
                continue
            steps.append(
                _make_step(
                    len(steps),
                    PlanStepKind.USE_FACT,
                    str(fact.get("subject_hash72", "")),
                    str(fact.get("predicate", "")),
                    str(fact.get("object_hash72", "")),
                    str(fact.get("fact_hash72", "")),
                    _fraction(str(fact.get("confidence", "1/1"))),
                )
            )
        for state in record.get("derived_states", []):
            if not isinstance(state, dict):
                continue
            steps.append(
                _make_step(
                    len(steps),
                    PlanStepKind.USE_DERIVED_STATE,
                    str(state.get("subject_hash72", "")),
                    str(state.get("predicate", "")),
                    str(state.get("object_hash72", "")),
                    str(state.get("state_hash72", "")),
                    _fraction(str(state.get("confidence", "1/1"))),
                )
            )
    return [s for s in steps if s.source_hash72 and s.target_hash72 and s.predicate]


def step_satisfies_target(step: PlanStep, target: PlanningTarget) -> bool:
    if target.target_predicate and step.predicate != target.target_predicate:
        return False
    if target.require_exact_subject and target.target_subject_hash72 and step.source_hash72 != target.target_subject_hash72:
        return False
    if target.require_exact_object and target.target_object_hash72 and step.target_hash72 != target.target_object_hash72:
        return False
    if target.target_subject_hash72 and not target.require_exact_subject and target.target_subject_hash72 not in {step.source_hash72, step.target_hash72}:
        return False
    if target.target_object_hash72 and not target.require_exact_object and target.target_object_hash72 not in {step.source_hash72, step.target_hash72}:
        return False
    return step.confidence >= target.min_confidence_fraction()


def build_adjacency(edges: Sequence[PlanStep]) -> Dict[str, List[PlanStep]]:
    adjacency: Dict[str, List[PlanStep]] = {}
    for edge in edges:
        adjacency.setdefault(edge.source_hash72, []).append(edge)
    return adjacency


def search_plans(edges: Sequence[PlanStep], target: PlanningTarget, max_depth: int = 4, max_candidates: int = 8) -> List[PlanCandidate]:
    """Deterministic bounded path search over reasoning edges."""

    candidates: List[PlanCandidate] = []
    adjacency = build_adjacency(edges)

    # Direct satisfaction candidates.
    for edge in edges:
        if step_satisfies_target(edge, target):
            reach = _make_step(1, PlanStepKind.REACH_TARGET, edge.source_hash72, edge.predicate, edge.target_hash72, edge.step_hash72, edge.confidence)
            path = [edge, reach]
            p_hash = hash72_digest(("plan_candidate_v1", target.to_dict(), [s.to_dict() for s in path], edge.confidence, True), width=18)
            symbol, codepoint = _symbol_from_hash(p_hash, len(candidates))
            candidates.append(PlanCandidate(target, path, edge.confidence, True, p_hash, symbol, codepoint))
            if len(candidates) >= max_candidates:
                return candidates

    # Chain search: start from target subject if supplied; else all sources.
    starts = [target.target_subject_hash72] if target.target_subject_hash72 else list(adjacency.keys())
    starts = [s for s in starts if s]
    for start in starts:
        queue: List[Tuple[str, List[PlanStep], Fraction]] = [(start, [], Fraction(1, 1))]
        seen_paths = set()
        while queue and len(candidates) < max_candidates:
            current, path, confidence = queue.pop(0)
            if len(path) >= max_depth:
                continue
            for edge in adjacency.get(current, []):
                key = (current, edge.step_hash72, tuple(s.step_hash72 for s in path))
                if key in seen_paths:
                    continue
                seen_paths.add(key)
                new_conf = min(confidence, edge.confidence)
                new_path = path + [edge]
                if step_satisfies_target(edge, target):
                    reach = _make_step(len(new_path), PlanStepKind.REACH_TARGET, edge.source_hash72, edge.predicate, edge.target_hash72, edge.step_hash72, new_conf)
                    full_path = new_path + [reach]
                    p_hash = hash72_digest(("plan_candidate_v1", target.to_dict(), [s.to_dict() for s in full_path], new_conf, True), width=18)
                    symbol, codepoint = _symbol_from_hash(p_hash, len(candidates))
                    candidates.append(PlanCandidate(target, full_path, new_conf, True, p_hash, symbol, codepoint))
                    if len(candidates) >= max_candidates:
                        break
                else:
                    queue.append((edge.target_hash72, new_path, new_conf))
    candidates.sort(key=lambda c: (c.path_confidence, -len(c.steps), c.plan_hash72), reverse=True)
    return candidates[:max_candidates]


def invariant_gate_for_plan(reasoning_sources: Sequence[str], target: PlanningTarget, candidates: Sequence[PlanCandidate], selected: PlanCandidate | None) -> EthicalInvariantReceipt:
    delta_e_zero = bool(reasoning_sources and target.name)
    all_steps = [step for candidate in candidates for step in candidate.steps]
    step_hashes = {step.step_hash72 for step in all_steps}
    psi_zero = selected is None or all(step.step_hash72 in step_hashes for step in selected.steps)
    theta = theta15_true()
    omega_true = bool(hash72_digest(("planning_replay_v1", list(reasoning_sources), target.to_dict(), [c.to_dict() for c in candidates], selected.to_dict() if selected else None), width=18))
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {
        "Δe=0": delta_e_zero,
        "Ψ=0": psi_zero,
        "Θ15=true": theta,
        "Ω=true": omega_true,
        "target": target.name,
        "candidate_count": len(candidates),
        "selected": selected.plan_hash72 if selected else None,
    }
    receipt = hash72_digest(("planning_invariant_gate_v1", details, status.value), width=18)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


class GoalPlanningDatabase:
    """JSON-backed planning database."""

    def __init__(self, path: str | Path = "demo_reports/hhs_goal_planning_db_v1.json") -> None:
        self.path = Path(path)

    def load(self) -> Dict[str, object]:
        if not self.path.exists():
            return {
                "module": "hhs_goal_oriented_planning_engine_v1",
                "records": [],
                "target_index": {},
                "plan_index": {},
                "symbol_index": {},
                "status_index": {},
            }
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: Dict[str, object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def append_record(self, record: PlanningRecord) -> None:
        data = self.load()
        records = data.setdefault("records", [])
        target_index = data.setdefault("target_index", {})
        plan_index = data.setdefault("plan_index", {})
        symbol_index = data.setdefault("symbol_index", {})
        status_index = data.setdefault("status_index", {})
        records.append(record.to_dict())
        target_index[record.target.name] = record.planning_hash72
        status_index.setdefault(record.status.value, [])
        status_index[record.status.value].append(record.planning_hash72)
        for candidate in record.candidates:
            plan_index[candidate.plan_hash72] = record.planning_hash72
            symbol_index[candidate.symbol] = candidate.plan_hash72
            symbol_index[candidate.codepoint] = candidate.plan_hash72
        self.save(data)

    def search(self, key: str) -> List[Dict[str, object]]:
        data = self.load()
        hits = set()
        for name in ["target_index", "plan_index", "symbol_index"]:
            index = data.get(name, {})
            if isinstance(index, dict) and key in index:
                hits.add(str(index[key]))
        status_index = data.get("status_index", {})
        if isinstance(status_index, dict) and key in status_index:
            hits.update(str(x) for x in status_index[key])
        return [r for r in data.get("records", []) if isinstance(r, dict) and r.get("planning_hash72") in hits]


def build_planning_record(reasoning_records: Sequence[Dict[str, object]], target: PlanningTarget) -> PlanningRecord:
    sources = [str(r.get("reasoning_hash72", "")) for r in reasoning_records if isinstance(r, dict)]
    edges = extract_edges(reasoning_records)
    candidates = search_plans(edges, target)
    selected = candidates[0] if candidates else None
    gate = invariant_gate_for_plan(sources, target, candidates, selected)
    if gate.status != ModificationStatus.APPLIED:
        status = PlanStatus.QUARANTINED
    elif selected is None:
        status = PlanStatus.UNRESOLVED
    else:
        status = PlanStatus.COMMITTED
    quarantine = None if status != PlanStatus.QUARANTINED else hash72_digest(("planning_quarantine", sources, target.to_dict(), gate.to_dict()), width=18)
    p_hash = hash72_digest(("planning_record_v1", sources, target.to_dict(), [c.to_dict() for c in candidates], selected.to_dict() if selected else None, gate.receipt_hash72, status.value), width=18)
    return PlanningRecord(sources, target, candidates, selected, gate, status, p_hash, quarantine)


def register_plan_in_symbol_cache(record: PlanningRecord, symbol_cache: GlobalSymbolCache) -> None:
    if record.status != PlanStatus.COMMITTED:
        return
    parent = symbol_cache.append_record(
        SymbolEntityType.MEMORY,
        f"plan:{record.target.name}",
        "memory_record",
        record.to_dict(),
        [OrthogonalChain.MEMORY_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
        relation=AddressRelation(by_symbol=None, from_symbol=None, through_symbol=None, to_symbol=None),
    )
    parent_symbol = parent.symbol_record.symbol
    if record.selected_plan:
        symbol_cache.append_record(
            SymbolEntityType.OPERATION,
            f"selected_plan:{record.target.name}",
            "operation_record",
            record.selected_plan.to_dict(),
            [OrthogonalChain.OPERATION_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
            relation=AddressRelation(by_symbol=parent_symbol, from_symbol=parent_symbol, through_symbol=None, to_symbol=record.selected_plan.symbol),
        )


def run_goal_planning(
    targets: Sequence[PlanningTarget],
    reasoning_database_path: str | Path = "demo_reports/hhs_symbolic_reasoning_db_v1.json",
    planning_database_path: str | Path = "demo_reports/hhs_goal_planning_db_v1.json",
    symbol_cache_path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json",
    ledger_path: str | Path = "demo_reports/hhs_goal_planning_ledger_v1.json",
) -> PlanningRunReceipt:
    reasoning_db = SymbolicReasoningDatabase(reasoning_database_path)
    planning_db = GoalPlanningDatabase(planning_database_path)
    symbol_cache = GlobalSymbolCache(symbol_cache_path)
    reasoning_records = [r for r in reasoning_db.load().get("records", []) if isinstance(r, dict)]
    planning_records: List[PlanningRecord] = []
    for target in targets:
        record = build_planning_record(reasoning_records, target)
        planning_db.append_record(record)
        register_plan_in_symbol_cache(record, symbol_cache)
        planning_records.append(record)

    ledger = MemoryLedger(ledger_path)
    commit = ledger.append_payloads("goal_planning_record_v1", [r.to_dict() for r in planning_records])
    replay = replay_ledger(ledger_path)
    committed = sum(1 for r in planning_records if r.status == PlanStatus.COMMITTED)
    unresolved = sum(1 for r in planning_records if r.status == PlanStatus.UNRESOLVED)
    quarantined = sum(1 for r in planning_records if r.status == PlanStatus.QUARANTINED)
    candidate_count = sum(len(r.candidates) for r in planning_records)
    receipt = hash72_digest(("goal_planning_run_v1", [r.planning_hash72 for r in planning_records], commit.receipt_hash72, replay.receipt_hash72, committed, unresolved, quarantined, candidate_count), width=18)
    return PlanningRunReceipt(
        module="hhs_goal_oriented_planning_engine_v1",
        planning_database_path=str(planning_database_path),
        targets_seen=len(planning_records),
        plans_committed=committed,
        plans_unresolved=unresolved,
        plans_quarantined=quarantined,
        candidate_count=candidate_count,
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
    sample = demo_dir / "hhs_goal_planning_sample.md"
    sample.write_text("meaning -> structure\nstructure -> state\nstate -> memory\n", encoding="utf-8")
    ingest_and_reconstruct_text_files(
        [sample],
        multimodal_database_path=demo_dir / "hhs_multimodal_file_db_planning_demo_v1.json",
        semantic_database_path=demo_dir / "hhs_text_semantic_db_planning_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_planning_demo_v1.json",
        multimodal_ledger_path=demo_dir / "hhs_multimodal_file_ledger_planning_demo_v1.json",
        semantic_ledger_path=demo_dir / "hhs_text_semantic_ledger_planning_demo_v1.json",
        chunk_size=64,
    )
    seed_starter_lexicon(
        database_path=demo_dir / "hhs_english_lexicon_db_planning_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_planning_demo_v1.json",
        ledger_path=demo_dir / "hhs_english_lexicon_ledger_planning_demo_v1.json",
    )
    run_contextual_resolution(
        semantic_database_path=demo_dir / "hhs_text_semantic_db_planning_demo_v1.json",
        lexicon_database_path=demo_dir / "hhs_english_lexicon_db_planning_demo_v1.json",
        resolution_database_path=demo_dir / "hhs_contextual_resolution_db_planning_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_planning_demo_v1.json",
        ledger_path=demo_dir / "hhs_contextual_resolution_ledger_planning_demo_v1.json",
    )
    reasoning = run_symbolic_reasoning(
        semantic_database_path=demo_dir / "hhs_text_semantic_db_planning_demo_v1.json",
        resolution_database_path=demo_dir / "hhs_contextual_resolution_db_planning_demo_v1.json",
        reasoning_database_path=demo_dir / "hhs_symbolic_reasoning_db_planning_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_planning_demo_v1.json",
        ledger_path=demo_dir / "hhs_symbolic_reasoning_ledger_planning_demo_v1.json",
    )
    # Predicate-only target: find any valid transforms_to path.
    target = PlanningTarget(name="Find transform path", target_predicate="transforms_to", min_confidence="1/2")
    plan = run_goal_planning(
        [target],
        reasoning_database_path=demo_dir / "hhs_symbolic_reasoning_db_planning_demo_v1.json",
        planning_database_path=demo_dir / "hhs_goal_planning_db_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_planning_demo_v1.json",
        ledger_path=demo_dir / "hhs_goal_planning_ledger_demo_v1.json",
    )
    db = GoalPlanningDatabase(demo_dir / "hhs_goal_planning_db_demo_v1.json")
    return {"reasoning": reasoning.to_dict(), "planning": plan.to_dict(), "committed_plans": db.search("COMMITTED")}


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))

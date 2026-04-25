"""
HHS Contextual Meaning Resolution Engine v1
===========================================

Multi-sense disambiguation layer for HHS text semantics.

This module resolves word meaning using:

    semantic reconstruction tokens/nodes
    + English lexicon entries
    + local relation graph context
    + synonym/antonym/POS/tag overlap
    + HHS category matching
    + invariant gate Δe=0, Ψ=0, Θ15=true, Ω=true

It does not guess when context is insufficient. Ambiguous/unsupported resolutions
are quarantined or marked unresolved. Committed resolutions are Hash72-addressed,
Unicode-symbol-addressed, ledgered, and replay-verifiable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple
import json

from hhs_runtime.hhs_english_lexicon_seed_v1 import EnglishLexiconDatabase, seed_starter_lexicon
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


class ResolutionStatus(str, Enum):
    COMMITTED = "COMMITTED"
    UNRESOLVED = "UNRESOLVED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class SenseCandidate:
    """One candidate sense for a token."""

    word: str
    candidate_label: str
    pos: List[str]
    synonyms: List[str]
    antonyms: List[str]
    tags: List[str]
    hhs_category: str
    entry_hash72: str | None
    score: Fraction
    evidence: List[str]
    candidate_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "word": self.word,
            "candidate_label": self.candidate_label,
            "pos": self.pos,
            "synonyms": self.synonyms,
            "antonyms": self.antonyms,
            "tags": self.tags,
            "hhs_category": self.hhs_category,
            "entry_hash72": self.entry_hash72,
            "score": f"{self.score.numerator}/{self.score.denominator}",
            "evidence": self.evidence,
            "candidate_hash72": self.candidate_hash72,
        }


@dataclass(frozen=True)
class MeaningResolution:
    """Resolved or unresolved contextual meaning for one token."""

    source_semantic_hash72: str
    token_hash72: str
    token_value: str
    context_hash72: str
    candidates: List[SenseCandidate]
    selected_candidate: SenseCandidate | None
    confidence: Fraction
    status: ResolutionStatus
    invariant_gate: EthicalInvariantReceipt
    resolution_hash72: str
    quarantine_hash72: str | None

    def to_dict(self) -> Dict[str, object]:
        return {
            "source_semantic_hash72": self.source_semantic_hash72,
            "token_hash72": self.token_hash72,
            "token_value": self.token_value,
            "context_hash72": self.context_hash72,
            "candidates": [c.to_dict() for c in self.candidates],
            "selected_candidate": self.selected_candidate.to_dict() if self.selected_candidate else None,
            "confidence": f"{self.confidence.numerator}/{self.confidence.denominator}",
            "status": self.status.value,
            "invariant_gate": self.invariant_gate.to_dict(),
            "resolution_hash72": self.resolution_hash72,
            "quarantine_hash72": self.quarantine_hash72,
        }


@dataclass(frozen=True)
class ResolutionRunReceipt:
    """Receipt for contextual resolution run."""

    module: str
    resolution_database_path: str
    semantic_records_seen: int
    resolutions_seen: int
    resolutions_committed: int
    resolutions_unresolved: int
    resolutions_quarantined: int
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


def normalize(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def fraction_from_overlap(a: Set[str], b: Set[str]) -> Fraction:
    if not a or not b:
        return Fraction(0, 1)
    return Fraction(len(a & b), len(a | b))


def token_context(record: Dict[str, object], token_hash72: str, window: int = 5) -> Dict[str, object]:
    tokens = [t for t in record.get("tokens", []) if isinstance(t, dict)]
    relations = [r for r in record.get("relations", []) if isinstance(r, dict)]
    index = next((i for i, t in enumerate(tokens) if t.get("token_hash72") == token_hash72), None)
    if index is None:
        return {"near_values": [], "near_hashes": [], "relation_kinds": [], "line_index": None}
    start = max(0, index - window)
    end = min(len(tokens), index + window + 1)
    near = tokens[start:end]
    related = [r for r in relations if r.get("source_hash72") == token_hash72 or r.get("target_hash72") == token_hash72 or r.get("evidence_token_hash72") == token_hash72]
    return {
        "near_values": [normalize(str(t.get("value", ""))) for t in near if t.get("kind") != "LINE"],
        "near_hashes": [str(t.get("token_hash72", "")) for t in near],
        "relation_kinds": [str(r.get("kind", "")) for r in related],
        "line_index": tokens[index].get("line_index"),
    }


def build_candidates(word: str, context: Dict[str, object], lexicon: EnglishLexiconDatabase) -> List[SenseCandidate]:
    expansion = lexicon.expand_word(word)
    near_values = set(v for v in context.get("near_values", []) if v)
    relation_kinds = set(normalize(v) for v in context.get("relation_kinds", []))

    candidates: List[SenseCandidate] = []
    if expansion.get("found"):
        synonyms = [normalize(v) for v in expansion.get("synonyms", [])]
        antonyms = [normalize(v) for v in expansion.get("antonyms", [])]
        tags = [normalize(v) for v in expansion.get("tags", [])]
        pos = [normalize(v) for v in expansion.get("pos", [])]
        category = normalize(str(expansion.get("hhs_category", "general")))
        evidence: List[str] = []
        score = Fraction(1, 4)  # lexical presence baseline
        syn_overlap = fraction_from_overlap(set(synonyms), near_values)
        tag_overlap = fraction_from_overlap(set(tags + [category]), near_values | relation_kinds)
        if syn_overlap:
            evidence.append("synonym_context_overlap")
        if tag_overlap:
            evidence.append("tag_or_category_context_overlap")
        if category in near_values or category in relation_kinds:
            evidence.append("category_direct_match")
            score += Fraction(1, 4)
        if set(antonyms) & near_values:
            evidence.append("antonym_conflict")
            score -= Fraction(1, 4)
        score += syn_overlap / 4 + tag_overlap / 4
        if score < 0:
            score = Fraction(0, 1)
        if score > 1:
            score = Fraction(1, 1)
        c_hash = hash72_digest(("sense_candidate_v1", word, expansion, context, score, evidence), width=18)
        candidates.append(
            SenseCandidate(
                word=normalize(word),
                candidate_label=category,
                pos=pos,
                synonyms=synonyms,
                antonyms=antonyms,
                tags=tags,
                hhs_category=category,
                entry_hash72=expansion.get("entry_hash72"),
                score=score,
                evidence=evidence,
                candidate_hash72=c_hash,
            )
        )

    # Fallback unresolved structural candidate: this is not committed unless it
    # earns enough context evidence later.
    if not candidates:
        c_hash = hash72_digest(("unknown_sense_candidate_v1", word, context), width=18)
        candidates.append(
            SenseCandidate(
                word=normalize(word),
                candidate_label="unknown",
                pos=[],
                synonyms=[],
                antonyms=[],
                tags=[],
                hhs_category="unknown",
                entry_hash72=None,
                score=Fraction(0, 1),
                evidence=["lexicon_miss"],
                candidate_hash72=c_hash,
            )
        )
    return candidates


def invariant_gate_for_resolution(token_value: str, context: Dict[str, object], selected: SenseCandidate | None, confidence: Fraction, status: ResolutionStatus) -> EthicalInvariantReceipt:
    delta_e_zero = bool(token_value and context.get("near_hashes") is not None)
    psi_zero = selected is None or selected.word == normalize(token_value) or normalize(token_value) in selected.synonyms
    theta = theta15_true()
    omega_true = bool(hash72_digest(("resolution_replay", token_value, context, selected.to_dict() if selected else None, confidence, status.value)))
    ok = delta_e_zero and psi_zero and theta and omega_true and status != ResolutionStatus.QUARANTINED
    gate_status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {
        "Δe=0": delta_e_zero,
        "Ψ=0": psi_zero,
        "Θ15=true": theta,
        "Ω=true": omega_true,
        "token": token_value,
        "confidence": f"{confidence.numerator}/{confidence.denominator}",
        "resolution_status": status.value,
    }
    receipt = hash72_digest(("contextual_resolution_invariant_gate_v1", details, selected.to_dict() if selected else None), width=18)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, gate_status, details, receipt)


class ContextualResolutionDatabase:
    """JSON-backed contextual meaning resolution database."""

    def __init__(self, path: str | Path = "demo_reports/hhs_contextual_resolution_db_v1.json") -> None:
        self.path = Path(path)

    def load(self) -> Dict[str, object]:
        if not self.path.exists():
            return {
                "module": "hhs_contextual_meaning_resolution_v1",
                "records": [],
                "token_index": {},
                "word_index": {},
                "sense_index": {},
                "status_index": {},
            }
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: Dict[str, object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def append_resolution(self, resolution: MeaningResolution) -> None:
        data = self.load()
        records = data.setdefault("records", [])
        token_index = data.setdefault("token_index", {})
        word_index = data.setdefault("word_index", {})
        sense_index = data.setdefault("sense_index", {})
        status_index = data.setdefault("status_index", {})
        records.append(resolution.to_dict())
        token_index[resolution.token_hash72] = resolution.resolution_hash72
        word_index.setdefault(normalize(resolution.token_value), [])
        word_index[normalize(resolution.token_value)].append(resolution.resolution_hash72)
        if resolution.selected_candidate:
            sense_index.setdefault(resolution.selected_candidate.candidate_label, [])
            sense_index[resolution.selected_candidate.candidate_label].append(resolution.resolution_hash72)
        status_index.setdefault(resolution.status.value, [])
        status_index[resolution.status.value].append(resolution.resolution_hash72)
        self.save(data)

    def search(self, key: str) -> List[Dict[str, object]]:
        data = self.load()
        hits = set()
        norm = normalize(key)
        for index_name in ["token_index", "word_index", "sense_index", "status_index"]:
            index = data.get(index_name, {})
            if isinstance(index, dict):
                if key in index:
                    v = index[key]
                    hits.update(v if isinstance(v, list) else [v])
                if norm in index:
                    v = index[norm]
                    hits.update(v if isinstance(v, list) else [v])
        return [r for r in data.get("records", []) if isinstance(r, dict) and r.get("resolution_hash72") in hits]


def resolve_token(record: Dict[str, object], token: Dict[str, object], lexicon: EnglishLexiconDatabase, min_commit_score: Fraction = Fraction(1, 2)) -> MeaningResolution:
    token_value = str(token.get("value", ""))
    token_hash = str(token.get("token_hash72", ""))
    context = token_context(record, token_hash)
    context_hash = hash72_digest(("token_context_v1", token_hash, context), width=18)
    candidates = build_candidates(token_value, context, lexicon)
    candidates.sort(key=lambda c: (c.score, c.candidate_hash72), reverse=True)
    selected = candidates[0] if candidates else None
    confidence = selected.score if selected else Fraction(0, 1)
    if selected and selected.hhs_category != "unknown" and confidence >= min_commit_score:
        status = ResolutionStatus.COMMITTED
    elif selected and selected.hhs_category == "unknown":
        status = ResolutionStatus.UNRESOLVED
    else:
        status = ResolutionStatus.UNRESOLVED
    gate = invariant_gate_for_resolution(token_value, context, selected, confidence, status)
    if gate.status != ModificationStatus.APPLIED:
        status = ResolutionStatus.QUARANTINED
    quarantine = None if status != ResolutionStatus.QUARANTINED else hash72_digest(("resolution_quarantine", token, context, selected.to_dict() if selected else None, gate.to_dict()), width=18)
    r_hash = hash72_digest(("meaning_resolution_v1", record.get("semantic_hash72"), token_hash, token_value, context_hash, [c.to_dict() for c in candidates], selected.to_dict() if selected else None, confidence, status.value, gate.receipt_hash72), width=18)
    return MeaningResolution(str(record.get("semantic_hash72", "")), token_hash, token_value, context_hash, candidates, selected, confidence, status, gate, r_hash, quarantine)


def resolvable_tokens(record: Dict[str, object]) -> List[Dict[str, object]]:
    out = []
    for token in record.get("tokens", []):
        if not isinstance(token, dict):
            continue
        kind = token.get("kind")
        value = str(token.get("value", ""))
        if kind in {"WORD", "HHS_TERM", "HASH72", "UNICODE"} and value.strip():
            out.append(token)
    return out


def run_contextual_resolution(
    semantic_database_path: str | Path = "demo_reports/hhs_text_semantic_db_v1.json",
    lexicon_database_path: str | Path = "demo_reports/hhs_english_lexicon_db_v1.json",
    resolution_database_path: str | Path = "demo_reports/hhs_contextual_resolution_db_v1.json",
    symbol_cache_path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json",
    ledger_path: str | Path = "demo_reports/hhs_contextual_resolution_ledger_v1.json",
    min_commit_score: Fraction = Fraction(1, 2),
    seed_lexicon_if_empty: bool = True,
) -> ResolutionRunReceipt:
    lexicon_path = Path(lexicon_database_path)
    if seed_lexicon_if_empty and not lexicon_path.exists():
        seed_starter_lexicon(database_path=lexicon_path)

    semantic_db = TextSemanticDatabase(semantic_database_path)
    lexicon = EnglishLexiconDatabase(lexicon_database_path)
    resolution_db = ContextualResolutionDatabase(resolution_database_path)
    symbol_cache = GlobalSymbolCache(symbol_cache_path)
    semantic_records = [r for r in semantic_db.load().get("records", []) if isinstance(r, dict)]
    resolutions: List[MeaningResolution] = []
    for record in semantic_records:
        for token in resolvable_tokens(record):
            resolution = resolve_token(record, token, lexicon, min_commit_score=min_commit_score)
            resolution_db.append_resolution(resolution)
            resolutions.append(resolution)
            if resolution.status == ResolutionStatus.COMMITTED:
                symbol_cache.append_record(
                    SymbolEntityType.MEMORY,
                    f"meaning:{resolution.token_value}:{resolution.resolution_hash72}",
                    "memory_record",
                    resolution.to_dict(),
                    [OrthogonalChain.MEMORY_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
                    relation=AddressRelation(by_symbol=None, from_symbol=None, through_symbol=None, to_symbol=None),
                )

    ledger = MemoryLedger(ledger_path)
    commit = ledger.append_payloads("contextual_meaning_resolution_v1", [r.to_dict() for r in resolutions])
    replay = replay_ledger(ledger_path)
    committed = sum(1 for r in resolutions if r.status == ResolutionStatus.COMMITTED)
    unresolved = sum(1 for r in resolutions if r.status == ResolutionStatus.UNRESOLVED)
    quarantined = sum(1 for r in resolutions if r.status == ResolutionStatus.QUARANTINED)
    receipt = hash72_digest(("contextual_resolution_run_v1", [r.resolution_hash72 for r in resolutions], commit.receipt_hash72, replay.receipt_hash72, committed, unresolved, quarantined), width=18)
    return ResolutionRunReceipt(
        module="hhs_contextual_meaning_resolution_v1",
        resolution_database_path=str(resolution_database_path),
        semantic_records_seen=len(semantic_records),
        resolutions_seen=len(resolutions),
        resolutions_committed=committed,
        resolutions_unresolved=unresolved,
        resolutions_quarantined=quarantined,
        ledger_commit_receipt=commit.to_dict(),
        replay_receipt=replay.to_dict(),
        receipt_hash72=receipt,
    )


def demo() -> Dict[str, object]:
    from hhs_runtime.hhs_text_semantic_reconstruction_v1 import ingest_and_reconstruct_text_files

    demo_dir = Path("demo_reports")
    demo_dir.mkdir(parents=True, exist_ok=True)
    sample = demo_dir / "hhs_contextual_resolution_sample.md"
    sample.write_text(
        "Meaning is structure. A valid state preserves truth. Invalid change must quarantine. Hash72 stores memory.\n",
        encoding="utf-8",
    )
    ingest_and_reconstruct_text_files(
        [sample],
        multimodal_database_path=demo_dir / "hhs_multimodal_file_db_resolution_demo_v1.json",
        semantic_database_path=demo_dir / "hhs_text_semantic_db_resolution_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_resolution_demo_v1.json",
        multimodal_ledger_path=demo_dir / "hhs_multimodal_file_ledger_resolution_demo_v1.json",
        semantic_ledger_path=demo_dir / "hhs_text_semantic_ledger_resolution_demo_v1.json",
        chunk_size=64,
    )
    seed_starter_lexicon(
        database_path=demo_dir / "hhs_english_lexicon_db_resolution_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_resolution_demo_v1.json",
        ledger_path=demo_dir / "hhs_english_lexicon_ledger_resolution_demo_v1.json",
    )
    receipt = run_contextual_resolution(
        semantic_database_path=demo_dir / "hhs_text_semantic_db_resolution_demo_v1.json",
        lexicon_database_path=demo_dir / "hhs_english_lexicon_db_resolution_demo_v1.json",
        resolution_database_path=demo_dir / "hhs_contextual_resolution_db_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_resolution_demo_v1.json",
        ledger_path=demo_dir / "hhs_contextual_resolution_ledger_demo_v1.json",
    )
    db = ContextualResolutionDatabase(demo_dir / "hhs_contextual_resolution_db_demo_v1.json")
    return {"receipt": receipt.to_dict(), "meaning_hits": db.search("meaning"), "valid_hits": db.search("valid")}


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))

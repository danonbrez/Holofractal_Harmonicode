"""
HHS English Lexicon Seed v1
===========================

Natural-language understanding seed substrate for HHS.

The goal is to avoid starting cold: common English words can be loaded with
synonyms, antonyms, parts of speech, examples, semantic tags, and HHS mappings.
Each lexical entry is Hash72-addressed, Unicode-symbol-addressable, searchable,
and ledger/replay-backed.

This module includes:

* schema for 5000-word lexicon entries
* deterministic starter seed for core HHS/NLU terms
* CSV/JSON import hooks for a full 5000-word corpus
* lookup by word, synonym, antonym, POS, tag, symbol, or Hash72
* expansion API for semantic reconstruction layers
* invariant gate Δe=0, Ψ=0, Θ15=true, Ω=true before commit

The full 5000-word dataset should be stored as data, not hard-coded into the
runtime module.  Supported import formats:

CSV columns:
    word,pos,synonyms,antonyms,examples,tags,hhs_category

JSON shape:
    [{"word": "...", "pos": ["noun"], "synonyms": [...], ...}]
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence
import csv
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


class LexiconStatus(str, Enum):
    COMMITTED = "COMMITTED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class LexiconEntry:
    """One natural-language lexical seed entry."""

    word: str
    pos: List[str]
    synonyms: List[str]
    antonyms: List[str]
    examples: List[str]
    tags: List[str]
    hhs_category: str
    entry_hash72: str
    symbol: str
    codepoint: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class LexiconRecord:
    """Stored lexical entry plus invariant receipt."""

    entry: LexiconEntry
    invariant_gate: EthicalInvariantReceipt
    status: LexiconStatus
    quarantine_hash72: str | None
    record_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "entry": self.entry.to_dict(),
            "invariant_gate": self.invariant_gate.to_dict(),
            "status": self.status.value,
            "quarantine_hash72": self.quarantine_hash72,
            "record_hash72": self.record_hash72,
        }


@dataclass(frozen=True)
class LexiconImportReceipt:
    """Receipt for lexicon seed/import operation."""

    module: str
    database_path: str
    entries_seen: int
    entries_committed: int
    entries_quarantined: int
    index_terms: int
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


def _normalize_word(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _clean_list(values: Iterable[str]) -> List[str]:
    cleaned = []
    seen = set()
    for value in values:
        item = _normalize_word(str(value))
        if item and item not in seen:
            cleaned.append(item)
            seen.add(item)
    return cleaned


def _split_field(value: object) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return _clean_list(str(v) for v in value)
    text = str(value).strip()
    if not text:
        return []
    # Accept semicolon, pipe, or comma-separated fields.
    for sep in [";", "|", ","]:
        if sep in text:
            return _clean_list(part for part in text.split(sep))
    return _clean_list([text])


def _symbol_from_hash(h72: str, offset: int = 0) -> tuple[str, str]:
    base = 0xFA00
    span = 0x0500
    acc = offset
    for ch in h72:
        acc = (acc * 149 + ord(ch)) % span
    cp = base + acc
    return chr(cp), f"U+{cp:04X}"


def make_entry(
    word: str,
    pos: Sequence[str] | None = None,
    synonyms: Sequence[str] | None = None,
    antonyms: Sequence[str] | None = None,
    examples: Sequence[str] | None = None,
    tags: Sequence[str] | None = None,
    hhs_category: str = "general",
) -> LexiconEntry:
    normalized = _normalize_word(word)
    pos_list = _clean_list(pos or [])
    synonym_list = _clean_list(synonyms or [])
    antonym_list = _clean_list(antonyms or [])
    example_list = [str(e).strip() for e in (examples or []) if str(e).strip()]
    tag_list = _clean_list(tags or [])
    category = _normalize_word(hhs_category or "general") or "general"
    entry_hash = hash72_digest(
        (
            "lexicon_entry_v1",
            normalized,
            pos_list,
            synonym_list,
            antonym_list,
            example_list,
            tag_list,
            category,
        ),
        width=18,
    )
    symbol, codepoint = _symbol_from_hash(entry_hash)
    return LexiconEntry(
        word=normalized,
        pos=pos_list,
        synonyms=synonym_list,
        antonyms=antonym_list,
        examples=example_list,
        tags=tag_list,
        hhs_category=category,
        entry_hash72=entry_hash,
        symbol=symbol,
        codepoint=codepoint,
    )


def invariant_gate_for_entry(entry: LexiconEntry) -> EthicalInvariantReceipt:
    delta_e_zero = bool(entry.word and entry.entry_hash72 and entry.pos)
    # Semantic drift gate: synonyms/antonyms cannot contain the word itself, and
    # antonyms/synonyms should not overlap in the same entry.
    synonym_set = set(entry.synonyms)
    antonym_set = set(entry.antonyms)
    psi_zero = entry.word not in synonym_set and entry.word not in antonym_set and synonym_set.isdisjoint(antonym_set)
    theta = theta15_true()
    omega_true = bool(entry.symbol and entry.codepoint and hash72_digest((entry.to_dict(),)))
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {
        "Δe=0": delta_e_zero,
        "Ψ=0": psi_zero,
        "Θ15=true": theta,
        "Ω=true": omega_true,
        "word": entry.word,
        "pos": entry.pos,
        "synonym_count": len(entry.synonyms),
        "antonym_count": len(entry.antonyms),
    }
    receipt = hash72_digest(("lexicon_invariant_gate_v1", entry.to_dict(), details, status.value), width=18)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


class EnglishLexiconDatabase:
    """JSON-backed searchable English lexicon seed database."""

    def __init__(self, path: str | Path = "demo_reports/hhs_english_lexicon_db_v1.json") -> None:
        self.path = Path(path)

    def load(self) -> Dict[str, object]:
        if not self.path.exists():
            return {
                "module": "hhs_english_lexicon_seed_v1",
                "records": [],
                "word_index": {},
                "synonym_index": {},
                "antonym_index": {},
                "pos_index": {},
                "tag_index": {},
                "symbol_index": {},
                "hash_index": {},
            }
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: Dict[str, object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def append_record(self, record: LexiconRecord) -> None:
        data = self.load()
        records = data.setdefault("records", [])
        word_index = data.setdefault("word_index", {})
        synonym_index = data.setdefault("synonym_index", {})
        antonym_index = data.setdefault("antonym_index", {})
        pos_index = data.setdefault("pos_index", {})
        tag_index = data.setdefault("tag_index", {})
        symbol_index = data.setdefault("symbol_index", {})
        hash_index = data.setdefault("hash_index", {})

        records.append(record.to_dict())
        entry = record.entry
        word_index[entry.word] = record.record_hash72
        hash_index[entry.entry_hash72] = record.record_hash72
        symbol_index[entry.symbol] = record.record_hash72
        symbol_index[entry.codepoint] = record.record_hash72
        for synonym in entry.synonyms:
            synonym_index.setdefault(synonym, [])
            synonym_index[synonym].append(record.record_hash72)
        for antonym in entry.antonyms:
            antonym_index.setdefault(antonym, [])
            antonym_index[antonym].append(record.record_hash72)
        for pos in entry.pos:
            pos_index.setdefault(pos, [])
            pos_index[pos].append(record.record_hash72)
        for tag in entry.tags + [entry.hhs_category]:
            tag_index.setdefault(tag, [])
            tag_index[tag].append(record.record_hash72)
        self.save(data)

    def search(self, key: str) -> List[Dict[str, object]]:
        data = self.load()
        normalized = _normalize_word(key)
        hits = set()
        for index_name in ["word_index", "hash_index", "symbol_index"]:
            index = data.get(index_name, {})
            if isinstance(index, dict) and key in index:
                hits.add(str(index[key]))
            if isinstance(index, dict) and normalized in index:
                hits.add(str(index[normalized]))
        for index_name in ["synonym_index", "antonym_index", "pos_index", "tag_index"]:
            index = data.get(index_name, {})
            if isinstance(index, dict) and normalized in index:
                hits.update(str(x) for x in index[normalized])
        records = data.get("records", [])
        return [r for r in records if isinstance(r, dict) and r.get("record_hash72") in hits]

    def lookup_word(self, word: str) -> Dict[str, object] | None:
        hits = self.search(word)
        for hit in hits:
            entry = hit.get("entry", {})
            if isinstance(entry, dict) and entry.get("word") == _normalize_word(word):
                return hit
        return hits[0] if hits else None

    def expand_word(self, word: str) -> Dict[str, object]:
        record = self.lookup_word(word)
        if not record:
            return {
                "word": _normalize_word(word),
                "found": False,
                "synonyms": [],
                "antonyms": [],
                "pos": [],
                "tags": [],
                "entry_hash72": None,
                "symbol": None,
            }
        entry = record["entry"]
        return {
            "word": entry["word"],
            "found": True,
            "synonyms": entry.get("synonyms", []),
            "antonyms": entry.get("antonyms", []),
            "pos": entry.get("pos", []),
            "examples": entry.get("examples", []),
            "tags": entry.get("tags", []),
            "hhs_category": entry.get("hhs_category"),
            "entry_hash72": entry.get("entry_hash72"),
            "symbol": entry.get("symbol"),
            "codepoint": entry.get("codepoint"),
        }


def store_entries(
    entries: Sequence[LexiconEntry],
    database_path: str | Path = "demo_reports/hhs_english_lexicon_db_v1.json",
    symbol_cache_path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json",
    ledger_path: str | Path = "demo_reports/hhs_english_lexicon_ledger_v1.json",
) -> LexiconImportReceipt:
    db = EnglishLexiconDatabase(database_path)
    cache = GlobalSymbolCache(symbol_cache_path)
    records: List[LexiconRecord] = []
    for entry in entries:
        gate = invariant_gate_for_entry(entry)
        status = LexiconStatus.COMMITTED if gate.status == ModificationStatus.APPLIED else LexiconStatus.QUARANTINED
        quarantine = None if status == LexiconStatus.COMMITTED else hash72_digest(("lexicon_quarantine", entry.to_dict(), gate.to_dict()), width=18)
        record_hash = hash72_digest(("lexicon_record_v1", entry.to_dict(), gate.receipt_hash72, status.value, quarantine), width=18)
        record = LexiconRecord(entry, gate, status, quarantine, record_hash)
        db.append_record(record)
        records.append(record)
        if status == LexiconStatus.COMMITTED:
            cache.append_record(
                SymbolEntityType.MEMORY,
                f"lexicon:{entry.word}",
                "memory_record",
                record.to_dict(),
                [OrthogonalChain.MEMORY_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
                relation=AddressRelation(by_symbol=entry.symbol, from_symbol=entry.symbol, through_symbol=None, to_symbol=None),
            )

    ledger = MemoryLedger(ledger_path)
    commit = ledger.append_payloads("english_lexicon_record_v1", [record.to_dict() for record in records])
    replay = replay_ledger(ledger_path)
    committed = sum(1 for record in records if record.status == LexiconStatus.COMMITTED)
    quarantined = len(records) - committed
    db_data = db.load()
    index_terms = sum(len(v) if isinstance(v, dict) else 0 for k, v in db_data.items() if k.endswith("_index"))
    receipt = hash72_digest(("english_lexicon_import_v1", [r.record_hash72 for r in records], commit.receipt_hash72, replay.receipt_hash72, committed, quarantined, index_terms), width=18)
    return LexiconImportReceipt(
        module="hhs_english_lexicon_seed_v1",
        database_path=str(database_path),
        entries_seen=len(records),
        entries_committed=committed,
        entries_quarantined=quarantined,
        index_terms=index_terms,
        ledger_commit_receipt=commit.to_dict(),
        replay_receipt=replay.to_dict(),
        receipt_hash72=receipt,
    )


def load_entries_from_json(path: str | Path) -> List[LexiconEntry]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("lexicon JSON must be a list of objects")
    entries = []
    for item in data:
        if not isinstance(item, dict):
            continue
        entries.append(
            make_entry(
                word=str(item.get("word", "")),
                pos=_split_field(item.get("pos", [])),
                synonyms=_split_field(item.get("synonyms", [])),
                antonyms=_split_field(item.get("antonyms", [])),
                examples=item.get("examples", []) if isinstance(item.get("examples", []), list) else _split_field(item.get("examples", [])),
                tags=_split_field(item.get("tags", [])),
                hhs_category=str(item.get("hhs_category", "general")),
            )
        )
    return entries


def load_entries_from_csv(path: str | Path) -> List[LexiconEntry]:
    entries: List[LexiconEntry] = []
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append(
                make_entry(
                    word=row.get("word", ""),
                    pos=_split_field(row.get("pos", "")),
                    synonyms=_split_field(row.get("synonyms", "")),
                    antonyms=_split_field(row.get("antonyms", "")),
                    examples=_split_field(row.get("examples", "")),
                    tags=_split_field(row.get("tags", "")),
                    hhs_category=row.get("hhs_category", "general"),
                )
            )
    return entries


def import_lexicon_file(
    path: str | Path,
    database_path: str | Path = "demo_reports/hhs_english_lexicon_db_v1.json",
    symbol_cache_path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json",
    ledger_path: str | Path = "demo_reports/hhs_english_lexicon_ledger_v1.json",
) -> LexiconImportReceipt:
    p = Path(path)
    if p.suffix.lower() == ".json":
        entries = load_entries_from_json(p)
    elif p.suffix.lower() == ".csv":
        entries = load_entries_from_csv(p)
    else:
        raise ValueError("lexicon import file must be .json or .csv")
    return store_entries(entries, database_path, symbol_cache_path, ledger_path)


STARTER_SEED = [
    make_entry("the", ["article"], [], [], ["the system preserves the invariant"], ["function_word", "determiner"], "grammar"),
    make_entry("be", ["verb"], ["exist", "occur"], ["cease"], ["to be is to hold state"], ["existence", "state"], "state"),
    make_entry("and", ["conjunction"], ["also", "plus"], ["but"], ["phase and structure align"], ["connector"], "relation"),
    make_entry("of", ["preposition"], ["from", "belonging to"], [], ["hash of the state"], ["relation"], "relation"),
    make_entry("to", ["preposition", "particle"], ["toward", "into"], ["from"], ["state moves to attractor"], ["direction"], "transition"),
    make_entry("in", ["preposition"], ["inside", "within"], ["outside"], ["state in ledger"], ["location"], "address"),
    make_entry("that", ["determiner", "conjunction"], ["which"], [], ["that state is valid"], ["reference"], "reference"),
    make_entry("have", ["verb"], ["hold", "possess"], ["lack"], ["agents have goals"], ["state"], "state"),
    make_entry("it", ["pronoun"], ["this", "that"], [], ["it resolves to a symbol"], ["reference"], "reference"),
    make_entry("for", ["preposition"], ["because of", "toward"], ["against"], ["gate for invariants"], ["purpose"], "purpose"),
    make_entry("not", ["adverb"], ["no", "never"], ["yes"], ["not valid means quarantine"], ["negation"], "logic"),
    make_entry("with", ["preposition"], ["alongside", "using"], ["without"], ["state with receipt"], ["association"], "relation"),
    make_entry("as", ["conjunction", "adverb"], ["like", "while"], [], ["token as symbol"], ["mapping"], "mapping"),
    make_entry("state", ["noun", "verb"], ["condition", "configuration"], ["void"], ["the state is committed"], ["hhs", "memory"], "state"),
    make_entry("symbol", ["noun"], ["sign", "glyph"], [], ["each record has a symbol"], ["unicode", "address"], "symbol"),
    make_entry("meaning", ["noun"], ["sense", "structure"], ["nonsense"], ["meaning is addressable structure"], ["semantic"], "semantics"),
    make_entry("truth", ["noun"], ["validity", "fact"], ["falsehood"], ["truth passes gates"], ["logic"], "logic"),
    make_entry("valid", ["adjective"], ["sound", "accepted"], ["invalid"], ["valid transition commits"], ["gate"], "validation"),
    make_entry("invalid", ["adjective"], ["unsound", "false"], ["valid"], ["invalid transition quarantines"], ["gate"], "validation"),
    make_entry("hash", ["noun", "verb"], ["digest", "fingerprint"], [], ["hash every record"], ["hash72"], "hashing"),
    make_entry("memory", ["noun"], ["record", "storage"], ["forgetting"], ["memory stores receipts"], ["ledger"], "memory"),
    make_entry("agent", ["noun"], ["actor", "process"], [], ["agent votes on state"], ["multi_agent"], "agent"),
    make_entry("goal", ["noun"], ["target", "aim"], [], ["goal defines attractor"], ["attractor"], "goal"),
    make_entry("change", ["noun", "verb"], ["modify", "transform"], ["preserve"], ["change must pass invariants"], ["transition"], "transition"),
    make_entry("preserve", ["verb"], ["maintain", "keep"], ["destroy"], ["preserve the invariant"], ["invariant"], "invariant"),
]


def seed_starter_lexicon(
    database_path: str | Path = "demo_reports/hhs_english_lexicon_db_v1.json",
    symbol_cache_path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json",
    ledger_path: str | Path = "demo_reports/hhs_english_lexicon_ledger_v1.json",
) -> LexiconImportReceipt:
    return store_entries(STARTER_SEED, database_path, symbol_cache_path, ledger_path)


def expand_tokens_with_lexicon(words: Sequence[str], database_path: str | Path = "demo_reports/hhs_english_lexicon_db_v1.json") -> List[Dict[str, object]]:
    db = EnglishLexiconDatabase(database_path)
    return [db.expand_word(word) for word in words]


def demo() -> Dict[str, object]:
    demo_dir = Path("demo_reports")
    demo_dir.mkdir(parents=True, exist_ok=True)
    receipt = seed_starter_lexicon(
        database_path=demo_dir / "hhs_english_lexicon_db_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_lexicon_demo_v1.json",
        ledger_path=demo_dir / "hhs_english_lexicon_ledger_demo_v1.json",
    )
    db = EnglishLexiconDatabase(demo_dir / "hhs_english_lexicon_db_demo_v1.json")
    return {
        "receipt": receipt.to_dict(),
        "expand_meaning": db.expand_word("meaning"),
        "expand_valid": db.expand_word("valid"),
    }


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))

"""
HHS WordNet Relation Enforcer v1
================================

Loads WordNet-style CSV exports and validates token/POS/relation structure
without replacing the existing lexicon, tokenizer, semantic DB, or training loop.

Canonical CSV location:
    data/wordnet/*.csv

Fallback CSV location during migration:
    hhs_runtime/*.csv

Supported uploaded CSV shapes:
- WordnetNouns.csv: Word, Count, POS, Definition
- WordnetVerbs.csv: Word, Count, Sense, Definition, Example 1, Example 2
- WordnetAdjectives.csv: Word, Count, Senses, Definition, Example 1..4
- WordnetAdverbs.csv: Word, Count, Senses, Definition, Example
- WordnetSynonyms.csv: Word, Count, POS, Synonyms
- WordnetAntonyms.csv: Word, Count, POS, Antonyms
- WordnetHypernyms.csv: lemma, Count, part_of_speech, hypernyms
- WordnetHyponyms.csv: lemma, Count, part_of_speech, hyponyms
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence
import csv
import json
import re

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest

POS_ALIASES = {
    "n": "noun",
    "v": "verb",
    "a": "adjective",
    "s": "adjective",
    "satellite": "adjective",
    "r": "adverb",
}

WORDNET_CSV_FILENAMES = [
    "WordnetNouns.csv",
    "WordnetVerbs.csv",
    "WordnetAdjectives.csv",
    "WordnetAdverbs.csv",
    "WordnetSynonyms.csv",
    "WordnetAntonyms.csv",
    "WordnetHypernyms.csv",
    "WordnetHyponyms.csv",
]


@dataclass(frozen=True)
class WordRelationEntry:
    word: str
    pos: List[str] = field(default_factory=list)
    definitions: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    antonyms: List[str] = field(default_factory=list)
    hypernyms: List[str] = field(default_factory=list)
    hyponyms: List[str] = field(default_factory=list)
    entry_hash72: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WordRelationFinding:
    token: str
    status: str
    message: str
    pos: List[str]
    relation_counts: Dict[str, int]
    finding_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WordRelationValidationReceipt:
    text: str
    tokens: List[str]
    findings: List[WordRelationFinding]
    unknown_count: int
    known_count: int
    feedback_records: List[Dict[str, Any]]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "tokens": self.tokens,
            "findings": [f.to_dict() for f in self.findings],
            "unknown_count": self.unknown_count,
            "known_count": self.known_count,
            "feedback_records": self.feedback_records,
            "receipt_hash72": self.receipt_hash72,
        }


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower())


def _clean(values: Iterable[Any]) -> List[str]:
    out: List[str] = []
    seen = set()
    for value in values:
        text = _norm(value)
        if not text or text == "nan":
            continue
        if text not in seen:
            out.append(text)
            seen.add(text)
    return out


def _split(value: Any) -> List[str]:
    text = _norm(value)
    if not text or text == "nan":
        return []
    for sep in [";", "|", ","]:
        if sep in text:
            return _clean(text.split(sep))
    return _clean([text])


def _pos(value: Any) -> str:
    text = _norm(value)
    return POS_ALIASES.get(text, text or "unknown")


def _merge_entry(db: Dict[str, WordRelationEntry], word: str, *, pos: Sequence[str] = (), definitions: Sequence[str] = (), examples: Sequence[str] = (), synonyms: Sequence[str] = (), antonyms: Sequence[str] = (), hypernyms: Sequence[str] = (), hyponyms: Sequence[str] = ()) -> None:
    w = _norm(word)
    if not w or w == "nan":
        return
    prev = db.get(w)
    base = prev or WordRelationEntry(word=w)
    merged = WordRelationEntry(
        word=w,
        pos=_clean([*base.pos, *pos]),
        definitions=_clean([*base.definitions, *definitions]),
        examples=_clean([*base.examples, *examples]),
        synonyms=_clean([*base.synonyms, *synonyms]),
        antonyms=_clean([*base.antonyms, *antonyms]),
        hypernyms=_clean([*base.hypernyms, *hypernyms]),
        hyponyms=_clean([*base.hyponyms, *hyponyms]),
    )
    h = hash72_digest(("hhs_word_relation_entry_v1", merged.word, merged.pos, merged.definitions, merged.examples, merged.synonyms, merged.antonyms, merged.hypernyms, merged.hyponyms), width=24)
    db[w] = WordRelationEntry(
        word=merged.word,
        pos=merged.pos,
        definitions=merged.definitions,
        examples=merged.examples,
        synonyms=merged.synonyms,
        antonyms=merged.antonyms,
        hypernyms=merged.hypernyms,
        hyponyms=merged.hyponyms,
        entry_hash72=h,
    )


def load_wordnet_relations(paths: Sequence[str | Path], *, require_all: bool = True) -> Dict[str, WordRelationEntry]:
    missing = [str(Path(p)) for p in paths if not Path(p).exists()]
    if require_all and missing:
        raise FileNotFoundError("Missing WordNet CSV files: " + "; ".join(missing))

    db: Dict[str, WordRelationEntry] = {}
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue
        name = path.name.lower()
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "nouns" in name:
                    _merge_entry(db, row.get("Word", ""), pos=[_pos(row.get("POS", "noun"))], definitions=[row.get("Definition", "")])
                elif "verbs" in name:
                    _merge_entry(db, row.get("Word", ""), pos=["verb"], definitions=[row.get("Definition", "")], examples=[row.get("Example 1", ""), row.get("Example 2", "")])
                elif "adjectives" in name:
                    _merge_entry(db, row.get("Word", ""), pos=["adjective"], definitions=[row.get("Definition", "")], examples=[row.get("Example 1", ""), row.get("Example 2", ""), row.get("Example 3", ""), row.get("Example 4", "")])
                elif "adverbs" in name:
                    _merge_entry(db, row.get("Word", ""), pos=["adverb"], definitions=[row.get("Definition", "")], examples=[row.get("Example", "")])
                elif "synonyms" in name:
                    _merge_entry(db, row.get("Word", ""), pos=[_pos(row.get("POS", ""))], synonyms=_split(row.get("Synonyms", "")))
                elif "antonyms" in name:
                    _merge_entry(db, row.get("Word", ""), pos=[_pos(row.get("POS", ""))], antonyms=_split(row.get("Antonyms", "")))
                elif "hypernyms" in name:
                    _merge_entry(db, row.get("lemma", ""), pos=[_pos(row.get("part_of_speech", ""))], hypernyms=_split(row.get("hypernyms", "")))
                elif "hyponyms" in name:
                    _merge_entry(db, row.get("lemma", ""), pos=[_pos(row.get("part_of_speech", ""))], hyponyms=_split(row.get("hyponyms", "")))
    if require_all and not db:
        raise ValueError("WordNet relation database loaded zero entries")
    return db


def tokenize_words(text: str) -> List[str]:
    return [_norm(t) for t in re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?", text) if _norm(t)]


def validate_word_relations(text: str, relation_db: Dict[str, WordRelationEntry]) -> WordRelationValidationReceipt:
    tokens = tokenize_words(text)
    findings: List[WordRelationFinding] = []
    for token in tokens:
        entry = relation_db.get(token)
        if entry is None:
            msg = "token not found in relation database"
            h = hash72_digest(("hhs_word_relation_finding_v1", token, "UNKNOWN", msg), width=18)
            findings.append(WordRelationFinding(token, "UNKNOWN", msg, [], {}, h))
            continue
        counts = {
            "synonyms": len(entry.synonyms),
            "antonyms": len(entry.antonyms),
            "hypernyms": len(entry.hypernyms),
            "hyponyms": len(entry.hyponyms),
            "definitions": len(entry.definitions),
        }
        has_structure = bool(entry.pos and (entry.definitions or entry.synonyms or entry.antonyms or entry.hypernyms or entry.hyponyms))
        status = "SUPPORTED" if has_structure else "WEAK"
        msg = "relation structure available" if has_structure else "entry has limited relation structure"
        h = hash72_digest(("hhs_word_relation_finding_v1", token, status, entry.entry_hash72, counts), width=18)
        findings.append(WordRelationFinding(token, status, msg, entry.pos, counts, h))

    known = sum(1 for f in findings if f.status in {"SUPPORTED", "WEAK"})
    unknown = sum(1 for f in findings if f.status == "UNKNOWN")
    feedback = []
    for f in findings:
        score = 100 if f.status == "SUPPORTED" else 75 if f.status == "WEAK" else 25
        feedback.append({
            "summary_hash72": f.finding_hash72,
            "phases": [],
            "carrier": "y",
            "status": "STAGED" if f.status != "UNKNOWN" else "HELD",
            "score": score,
            "operator_kind": "WORD_RELATION_VALIDATE",
            "token": f.token,
            "pos": f.pos,
            "relation_counts": f.relation_counts,
        })
    receipt = hash72_digest(("hhs_word_relation_validation_receipt_v1", text, tokens, [f.to_dict() for f in findings], feedback), width=24)
    return WordRelationValidationReceipt(text, tokens, findings, unknown, known, feedback, receipt)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def wordnet_csv_directory() -> Path:
    root = repo_root()
    canonical = root / "data" / "wordnet"
    if all((canonical / name).exists() for name in WORDNET_CSV_FILENAMES):
        return canonical
    fallback = root / "hhs_runtime"
    if all((fallback / name).exists() for name in WORDNET_CSV_FILENAMES):
        return fallback
    return canonical


def default_wordnet_paths(base_dir: str | Path | None = None) -> List[Path]:
    root = Path(base_dir) if base_dir is not None else wordnet_csv_directory()
    return [root / name for name in WORDNET_CSV_FILENAMES]


def validate_wordnet_files(paths: Sequence[str | Path] | None = None) -> Dict[str, Any]:
    resolved = [Path(p) for p in (paths or default_wordnet_paths())]
    existing = [str(p) for p in resolved if p.exists()]
    missing = [str(p) for p in resolved if not p.exists()]
    return {
        "status": "READY" if not missing else "MISSING_FILES",
        "directory": str(resolved[0].parent) if resolved else "",
        "existing": existing,
        "missing": missing,
        "required": WORDNET_CSV_FILENAMES,
    }


def main() -> None:
    file_status = validate_wordnet_files()
    if file_status["status"] != "READY":
        raise FileNotFoundError(json.dumps(file_status, indent=2, sort_keys=True))
    db = load_wordnet_relations(default_wordnet_paths())
    receipt = validate_word_relations("The symbolic system preserves valid meaning", db)
    print(json.dumps({"file_status": file_status, "entries_loaded": len(db), "validation": receipt.to_dict()}, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

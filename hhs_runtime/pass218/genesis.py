"""Pass 218 Iteration 1: exact Genesis relational seed compiler.

This module turns inherited lexical assets into a versioned, nonverbatim,
exact relational seed. It deliberately reuses the existing WordNet parser
and Pass 166 Word2Vec service instead of creating competing language stores.
No promoted relation strength in this module uses floating point.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from hashlib import sha256
import csv
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Protocol, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import (
    WORDNET_CSV_FILENAMES,
    WordRelationEntry,
    default_wordnet_paths,
    load_wordnet_relations,
)

PASS218_GENESIS_COMPILER_VERSION = "HHS-P218-GENESIS-COMPILER-I1-V1"
ENGLISH_WORD_LIST = "hhs_runtime/English_Word_List.txt"
GRAMMAR_CORRECTION = "hhs_runtime/Grammar Correction.csv"


class RelationStatus(IntEnum):
    COUNTERINDICATED = -1
    UNRESOLVED = 0
    SUPPORTED = 1


@dataclass(frozen=True)
class ExactDistributionalRelation:
    target: str
    sign: int
    squared_numerator: int
    squared_denominator: int
    vector_identity: str

    def to_record(self) -> dict[str, Any]:
        if self.sign not in (-1, 0, 1):
            raise ValueError("P218_DISTRIBUTIONAL_SIGN_INVALID")
        if self.squared_numerator < 0 or self.squared_denominator <= 0:
            raise ValueError("P218_DISTRIBUTIONAL_RATIO_INVALID")
        return {
            "target": _normalize_lexeme(self.target),
            "status": self.sign,
            "similarity_squared": {
                "numerator": self.squared_numerator,
                "denominator": self.squared_denominator,
            },
            "vector_identity": self.vector_identity,
        }


class ExactWord2VecProvider(Protocol):
    def exact_neighbors(self, token: str, *, top_k: int) -> Sequence[ExactDistributionalRelation]: ...


class Pass166Word2VecAdapter:
    """Thin exact adapter over inherited Pass 166 Word2Vec runtime."""

    def __init__(self, service: Any, *, model_id: str | None = None) -> None:
        self._service = service
        self._model_id = model_id

    @staticmethod
    def _ratio(value: str) -> tuple[int, int]:
        left, separator, right = value.partition("/")
        if separator != "/":
            raise ValueError("P218_P166_RATIO_INVALID")
        numerator = int(left)
        denominator = int(right)
        if numerator < 0 or denominator <= 0:
            raise ValueError("P218_P166_RATIO_INVALID")
        return numerator, denominator

    def exact_neighbors(self, token: str, *, top_k: int = 8) -> tuple[ExactDistributionalRelation, ...]:
        payload = self._service.nearest(token, model_id=self._model_id, top_k=top_k)
        records: list[ExactDistributionalRelation] = []
        for item in payload["results"]:
            numerator, denominator = self._ratio(item["cosine_squared_exact"])
            records.append(
                ExactDistributionalRelation(
                    target=item["token"],
                    sign=int(item["cosine_sign"]),
                    squared_numerator=numerator,
                    squared_denominator=denominator,
                    vector_identity=item["vector_identity"],
                )
            )
        return tuple(records)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _normalize_lexeme(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _asset_record(path: Path, repository_root: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "path": path.relative_to(repository_root).as_posix(),
        "byte_count": len(raw),
        "sha256": sha256(raw).hexdigest(),
    }


def _grammar_inventory(path: Path) -> dict[str, Any]:
    row_count = 0
    category_counts: dict[str, int] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            row_count += 1
            category = str(row.get("Error Type", "")).strip()
            if category:
                category_counts[category] = category_counts.get(category, 0) + 1
    return {
        "row_count": row_count,
        "error_type_counts": {key: category_counts[key] for key in sorted(category_counts)},
        "verbatim_examples_retained": False,
    }


def repository_asset_manifest(repository_root: str | Path) -> dict[str, Any]:
    """Bind inherited local language assets without retaining their prose."""
    root = Path(repository_root).resolve()
    english = root / ENGLISH_WORD_LIST
    grammar = root / GRAMMAR_CORRECTION
    wordnet = [Path(path).resolve() for path in default_wordnet_paths(root / "hhs_runtime")]
    required = [english, grammar, *wordnet]
    missing = [path.as_posix() for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("P218_GENESIS_ASSET_MISSING:" + ";".join(missing))

    english_words = sorted(
        {
            _normalize_lexeme(line)
            for line in english.read_text("utf-8").splitlines()
            if _normalize_lexeme(line)
        }
    )
    payload = {
        "schema": "HHS-P218-GENESIS-ASSET-MANIFEST-I1-V1",
        "compiler_version": PASS218_GENESIS_COMPILER_VERSION,
        "english": {
            **_asset_record(english, root),
            "lexeme_count": len(english_words),
            "normalized_lexeme_root_sha256": sha256("\n".join(english_words).encode("utf-8")).hexdigest(),
        },
        "grammar": {
            **_asset_record(grammar, root),
            **_grammar_inventory(grammar),
        },
        "wordnet": [_asset_record(path, root) for path in wordnet],
        "wordnet_required_filenames": list(WORDNET_CSV_FILENAMES),
        "verbatim_training_examples_retained": False,
    }
    payload["asset_manifest_hash72"] = hash72_digest(
        {"domain": "HHS-P218-GENESIS-ASSET-MANIFEST-I1-V1"}, payload
    )
    return payload


def _distinction_id(lexeme: str) -> str:
    return hash72_digest(
        {"domain": "HHS-P218-DISTINCTION-I1-V1"},
        {"lexeme": _normalize_lexeme(lexeme)},
    )


def _relation_record(
    source: str,
    target: str,
    relation_type: str,
    status: RelationStatus,
    *,
    provenance: str,
    context: str = "GENESIS_PRIOR",
    exact_strength: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "source_id_hash72": _distinction_id(source),
        "target_id_hash72": _distinction_id(target),
        "relation_type": relation_type,
        "status": int(status),
        "context": context,
        "provenance": provenance,
        "revisable_prior": True,
    }
    if exact_strength is not None:
        numerator = int(exact_strength["numerator"])
        denominator = int(exact_strength["denominator"])
        if numerator < 0 or denominator <= 0:
            raise ValueError("P218_RELATION_STRENGTH_INVALID")
        record["exact_strength"] = {"numerator": numerator, "denominator": denominator}
    record["relation_hash72"] = hash72_digest(
        {"domain": "HHS-P218-RELATION-I1-V1"}, record
    )
    return record


def _wordnet_relations(lexeme: str, entry: WordRelationEntry) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    groups = (
        ("LEXICAL_SYNONYM", RelationStatus.SUPPORTED, entry.synonyms),
        ("LEXICAL_ANTONYM", RelationStatus.COUNTERINDICATED, entry.antonyms),
        ("LEXICAL_HYPERNYM", RelationStatus.SUPPORTED, entry.hypernyms),
        ("LEXICAL_HYPONYM", RelationStatus.SUPPORTED, entry.hyponyms),
    )
    for relation_type, status, targets in groups:
        for target in sorted({_normalize_lexeme(value) for value in targets if _normalize_lexeme(value)}):
            records.append(
                _relation_record(
                    lexeme,
                    target,
                    relation_type,
                    status,
                    provenance="WORDNET_REVISABLE_PRIOR",
                )
            )
    return records


def _form_neighbors(lexeme: str, candidates: Sequence[str], *, max_distance: int = 2, top_k: int = 8) -> list[dict[str, Any]]:
    def distance(left: str, right: str) -> int:
        previous = list(range(len(right) + 1))
        for left_index, left_char in enumerate(left, start=1):
            current = [left_index]
            for right_index, right_char in enumerate(right, start=1):
                current.append(
                    min(
                        current[-1] + 1,
                        previous[right_index] + 1,
                        previous[right_index - 1] + (left_char != right_char),
                    )
                )
            previous = current
        return previous[-1]

    ranked: list[tuple[int, str]] = []
    for candidate in candidates:
        normalized = _normalize_lexeme(candidate)
        if not normalized or normalized == lexeme or abs(len(normalized) - len(lexeme)) > max_distance:
            continue
        edit_distance = distance(lexeme, normalized)
        if edit_distance <= max_distance:
            ranked.append((edit_distance, normalized))
    ranked.sort(key=lambda item: (item[0], item[1]))
    return [
        _relation_record(
            lexeme,
            target,
            "FORM_SIMILARITY",
            RelationStatus.UNRESOLVED,
            provenance="DETERMINISTIC_FORM_NEIGHBORHOOD",
            exact_strength={"numerator": max_distance + 1 - edit_distance, "denominator": max_distance + 1},
        )
        for edit_distance, target in ranked[:top_k]
    ]


@dataclass(frozen=True)
class GenesisSeed:
    payload: Mapping[str, Any]
    genesis_seed_hash72: str
    validation_hash72: str
    hash216: str

    def to_record(self) -> dict[str, Any]:
        return {
            "payload": dict(self.payload),
            "genesis_seed_hash72": self.genesis_seed_hash72,
            "validation_hash72": self.validation_hash72,
            "hash216": self.hash216,
        }


class GenesisSeedBuilder:
    """Compile bounded Stage-0 relational state from inherited language assets."""

    def __init__(
        self,
        repository_root: str | Path,
        *,
        relation_db: Mapping[str, WordRelationEntry] | None = None,
        word2vec: ExactWord2VecProvider | None = None,
    ) -> None:
        self.repository_root = Path(repository_root).resolve()
        self.asset_manifest = repository_asset_manifest(self.repository_root)
        self.relation_db = relation_db
        self.word2vec = word2vec

    def load_repository_wordnet(self) -> Mapping[str, WordRelationEntry]:
        if self.relation_db is None:
            self.relation_db = load_wordnet_relations(
                default_wordnet_paths(self.repository_root / "hhs_runtime"),
                require_all=True,
            )
        return self.relation_db

    def _english_vocabulary(self) -> tuple[str, ...]:
        path = self.repository_root / ENGLISH_WORD_LIST
        return tuple(
            sorted(
                {
                    _normalize_lexeme(line)
                    for line in path.read_text("utf-8").splitlines()
                    if _normalize_lexeme(line)
                }
            )
        )

    def compile(self, lexemes: Iterable[str], *, use_repository_wordnet: bool = True) -> GenesisSeed:
        requested = tuple(sorted({_normalize_lexeme(value) for value in lexemes if _normalize_lexeme(value)}))
        if not requested:
            raise ValueError("P218_GENESIS_LEXEME_SET_EMPTY")
        relation_db = self.load_repository_wordnet() if use_repository_wordnet else (self.relation_db or {})
        vocabulary = self._english_vocabulary()

        distinctions: list[dict[str, Any]] = []
        relations: list[dict[str, Any]] = []
        for lexeme in requested:
            entry = relation_db.get(lexeme)
            distinctions.append(
                {
                    "lexeme": lexeme,
                    "distinction_id_hash72": _distinction_id(lexeme),
                    "form_hash72": hash72_digest({"domain": "HHS-P218-FORM-I1-V1"}, lexeme),
                    "pos": sorted(entry.pos) if entry is not None else [],
                    "provisional": entry is None,
                    "meaning_status": "PROVISIONAL_RELATIONAL_OBJECT" if entry is None else "LEXICALLY_GROUNDED_PRIOR",
                }
            )
            if entry is not None:
                relations.extend(_wordnet_relations(lexeme, entry))
            relations.extend(_form_neighbors(lexeme, vocabulary))
            if self.word2vec is not None:
                for neighbor in self.word2vec.exact_neighbors(lexeme, top_k=8):
                    item = neighbor.to_record()
                    relations.append(
                        _relation_record(
                            lexeme,
                            item["target"],
                            "DISTRIBUTIONAL_NEIGHBOR",
                            RelationStatus(item["status"]),
                            provenance="PASS166_EXACT_WORD2VEC",
                            exact_strength=item["similarity_squared"],
                        )
                    )

        relations.sort(
            key=lambda item: (
                item["source_id_hash72"],
                item["relation_type"],
                item["target_id_hash72"],
                item["relation_hash72"],
            )
        )
        symbolic_logic_schema = [
            "IDENTITY",
            "NONIDENTITY",
            "CONJUNCTION",
            "DISJUNCTION",
            "NEGATION",
            "IMPLICATION",
            "CONTRADICTION",
        ]
        mythopoetic_schema = [
            "ANALOGICAL",
            "SYMBOLIZES",
            "METAPHORICAL",
            "ALLEGORICAL",
        ]
        payload = {
            "schema": "HHS-P218-GENESIS-SEED-I1-V1",
            "compiler_version": PASS218_GENESIS_COMPILER_VERSION,
            "asset_manifest_hash72": self.asset_manifest["asset_manifest_hash72"],
            "lexeme_request_count": len(requested),
            "distinctions": distinctions,
            "relations": relations,
            "grammar_seed": {
                "asset_sha256": self.asset_manifest["grammar"]["sha256"],
                "error_type_counts": self.asset_manifest["grammar"]["error_type_counts"],
                "verbatim_examples_retained": False,
                "rule_compilation_status": "CATEGORY_PRIOR_ONLY_ITERATION_1",
            },
            "symbolic_logic_relation_types": symbolic_logic_schema,
            "mythopoetic_relation_types": mythopoetic_schema,
            "mythopoetic_empirical_truth_authority": False,
            "distributional_grounding": "PASS166_EXACT" if self.word2vec is not None else "NOT_CONFIGURED",
            "authoritative_float_weights": False,
            "wordnet_definitions_retained": False,
            "wordnet_examples_retained": False,
            "seed_is_revisable_prior": True,
        }
        genesis_hash72 = hash72_digest(
            {"domain": "HHS-P218-GENESIS-STATE-I1-V1"}, payload
        )
        validation_payload = {
            "schema": "HHS-P218-GENESIS-VALIDATION-I1-V1",
            "genesis_seed_hash72": genesis_hash72,
            "distinction_count": len(distinctions),
            "relation_count": len(relations),
            "nonverbatim": True,
            "exact_relation_status": all(item["status"] in (-1, 0, 1) for item in relations),
            "no_authoritative_float_weights": True,
            "analogy_not_identity": "ANALOGICAL" in mythopoetic_schema and "IDENTITY" in symbolic_logic_schema,
        }
        validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-GENESIS-VALIDATION-I1-V1"}, validation_payload
        )
        manifest_hash72 = self.asset_manifest["asset_manifest_hash72"]
        return GenesisSeed(
            payload=payload,
            genesis_seed_hash72=genesis_hash72,
            validation_hash72=validation_hash72,
            hash216=manifest_hash72 + genesis_hash72 + validation_hash72,
        )

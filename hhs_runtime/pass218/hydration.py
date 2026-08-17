"""Pass 218 Iteration 2 nonverbatim narrative-beat hydration.

This layer turns bounded narrative text into exact structural beat records.
The source prose is consumed transiently; promoted records retain hashes,
counts, relation types, and Genesis distinction identifiers only.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Any, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72

from .genesis import GenesisSeed
from .grammar import GrammarRuleSet

PASS218_NARRATIVE_HYDRATOR_VERSION = "HHS-P218-NARRATIVE-HYDRATOR-I2-V1"
_WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
_TIME_RE = re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b")
_SENTENCE_END_RE = re.compile(r"[.!?]+")
_FIRST_PERSON = frozenset({"i", "me", "my", "mine", "we", "us", "our", "ours"})
_SECOND_PERSON = frozenset({"you", "your", "yours"})
_THIRD_PERSON = frozenset({
    "he", "him", "his", "she", "her", "hers", "they", "them", "their", "theirs", "it", "its"
})
_NEGATION = frozenset({
    "no", "not", "never", "nothing", "without", "cannot", "can't", "don't", "doesn't", "didn't", "won't"
})
_MODAL = frozenset({"can", "could", "may", "might", "must", "shall", "should", "will", "would"})
_AUTHORITY = frozenset({
    "authority", "authorize", "authorized", "authorization", "deny", "denied", "grant", "granted",
    "hold", "held", "permission", "revoke", "revoked", "scope"
})
_TEMPORAL = frozenset({"after", "before", "earlier", "later", "then", "until", "when", "while"})


def _strip_frontmatter_and_headings(text: str) -> str:
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                start = index + 1
                break
    body = []
    for line in lines[start:]:
        if line.lstrip().startswith("#"):
            continue
        body.append(line)
    return "\n".join(body)


def _paragraphs(text: str) -> tuple[str, ...]:
    body = _strip_frontmatter_and_headings(text)
    return tuple(
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", body)
        if paragraph.strip()
    )


def _words(text: str) -> tuple[str, ...]:
    return tuple(match.group(0).casefold() for match in _WORD_RE.finditer(text))


def _dominant_perspective(first: int, second: int, third: int) -> str:
    ranked = sorted(
        (("FIRST_PERSON", first), ("SECOND_PERSON", second), ("THIRD_PERSON", third)),
        key=lambda item: (-item[1], item[0]),
    )
    if ranked[0][1] == 0:
        return "UNSPECIFIED"
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return "MIXED"
    return ranked[0][0]


def _relation_types(
    *,
    negation_count: int,
    modal_count: int,
    authority_count: int,
    temporal_count: int,
    dialogue_turn_count: int,
    dominant_perspective: str,
) -> tuple[str, ...]:
    values: list[str] = []
    if temporal_count:
        values.append("TEMPORAL_SUCCESSION")
    if dialogue_turn_count:
        values.append("DIALOGUE_RELATION")
    if negation_count:
        values.append("NEGATION_PRESSURE")
    if modal_count:
        values.append("MODAL_CONSTRAINT")
    if authority_count:
        values.append("AUTHORITY_SCOPE")
    if dominant_perspective != "UNSPECIFIED":
        values.append("PERSPECTIVE_" + dominant_perspective)
    return tuple(sorted(values))


def _distinction_index(seed: GenesisSeed) -> dict[str, str]:
    index: dict[str, str] = {}
    for item in seed.payload.get("distinctions", []):
        lexeme = str(item.get("lexeme", "")).strip().casefold()
        distinction_id = str(item.get("distinction_id_hash72", ""))
        if lexeme and validate_hash72(distinction_id):
            index[lexeme] = distinction_id
    return index


@dataclass(frozen=True)
class NarrativeBeat:
    ordinal: int
    source_span_sha256: str
    paragraph_count: int
    token_count: int
    sentence_count: int
    dialogue_turn_count: int
    first_person_count: int
    second_person_count: int
    third_person_count: int
    negation_count: int
    modal_count: int
    authority_count: int
    temporal_count: int
    dominant_perspective: str
    relation_types: tuple[str, ...]
    distinction_mentions: tuple[tuple[str, int], ...]
    beat_hash72: str

    def to_record(self) -> dict[str, Any]:
        return {
            "ordinal": self.ordinal,
            "source_span_sha256": self.source_span_sha256,
            "paragraph_count": self.paragraph_count,
            "token_count": self.token_count,
            "sentence_count": self.sentence_count,
            "dialogue_turn_count": self.dialogue_turn_count,
            "perspective_counts": {
                "first_person": self.first_person_count,
                "second_person": self.second_person_count,
                "third_person": self.third_person_count,
            },
            "negation_count": self.negation_count,
            "modal_count": self.modal_count,
            "authority_count": self.authority_count,
            "temporal_count": self.temporal_count,
            "dominant_perspective": self.dominant_perspective,
            "relation_types": list(self.relation_types),
            "distinction_mentions": [
                {"distinction_id_hash72": distinction_id, "count": count}
                for distinction_id, count in self.distinction_mentions
            ],
            "beat_hash72": self.beat_hash72,
            "verbatim_source_retained": False,
        }


@dataclass(frozen=True)
class NarrativeHydrationCandidate:
    source_id: str
    source_sha256: str
    source_epistemic_class: str
    genesis_seed_hash72: str
    grammar_rule_set_hash72: str
    beats: tuple[NarrativeBeat, ...]
    hydration_hash72: str
    validation_hash72: str
    hash216: str

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "HHS-P218-NARRATIVE-HYDRATION-CANDIDATE-I2-V1",
            "hydrator_version": PASS218_NARRATIVE_HYDRATOR_VERSION,
            "source_id": self.source_id,
            "source_sha256": self.source_sha256,
            "source_epistemic_class": self.source_epistemic_class,
            "genesis_seed_hash72": self.genesis_seed_hash72,
            "grammar_rule_set_hash72": self.grammar_rule_set_hash72,
            "beats": [beat.to_record() for beat in self.beats],
            "hydration_hash72": self.hydration_hash72,
            "validation_hash72": self.validation_hash72,
            "hash216": self.hash216,
            "hash216_semantics": ["PREVIOUS_GENESIS_STATE", "NEXT_HYDRATION_CANDIDATE", "VALIDATION_RECEIPT"],
            "verbatim_source_retained": False,
            "source_text_retained": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "authoritative_vector_store_promotion": False,
            "authoritative_float_weights": False,
        }


class NarrativeBeatHydrator:
    def __init__(self, *, paragraphs_per_beat: int = 4) -> None:
        if paragraphs_per_beat <= 0:
            raise ValueError("P218_PARAGRAPHS_PER_BEAT_INVALID")
        self.paragraphs_per_beat = paragraphs_per_beat

    def _beat(
        self,
        ordinal: int,
        span: Sequence[str],
        distinction_index: Mapping[str, str],
    ) -> NarrativeBeat:
        joined = "\n\n".join(span)
        words = _words(joined)
        first = sum(word in _FIRST_PERSON for word in words)
        second = sum(word in _SECOND_PERSON for word in words)
        third = sum(word in _THIRD_PERSON for word in words)
        negation = sum(word in _NEGATION for word in words)
        modal = sum(word in _MODAL for word in words)
        authority = sum(word in _AUTHORITY for word in words)
        temporal = sum(word in _TEMPORAL for word in words) + len(_TIME_RE.findall(joined))
        dialogue = sum(
            paragraph.lstrip().startswith(("\"", "“", "'"))
            or paragraph.count("\"") >= 2
            or (paragraph.count("“") and paragraph.count("”"))
            for paragraph in span
        )
        sentence_count = len(_SENTENCE_END_RE.findall(joined))
        if words and sentence_count == 0:
            sentence_count = 1
        dominant = _dominant_perspective(first, second, third)
        mentions: dict[str, int] = {}
        for word in words:
            distinction_id = distinction_index.get(word)
            if distinction_id is not None:
                mentions[distinction_id] = mentions.get(distinction_id, 0) + 1
        mention_items = tuple(sorted(mentions.items()))
        relations = _relation_types(
            negation_count=negation,
            modal_count=modal,
            authority_count=authority,
            temporal_count=temporal,
            dialogue_turn_count=dialogue,
            dominant_perspective=dominant,
        )
        payload = {
            "schema": "HHS-P218-NARRATIVE-BEAT-I2-V1",
            "ordinal": ordinal,
            "source_span_sha256": sha256(joined.encode("utf-8")).hexdigest(),
            "paragraph_count": len(span),
            "token_count": len(words),
            "sentence_count": sentence_count,
            "dialogue_turn_count": dialogue,
            "perspective_counts": {
                "first_person": first,
                "second_person": second,
                "third_person": third,
            },
            "negation_count": negation,
            "modal_count": modal,
            "authority_count": authority,
            "temporal_count": temporal,
            "dominant_perspective": dominant,
            "relation_types": list(relations),
            "distinction_mentions": [
                {"distinction_id_hash72": distinction_id, "count": count}
                for distinction_id, count in mention_items
            ],
            "verbatim_source_retained": False,
        }
        beat_hash72 = hash72_digest({"domain": "HHS-P218-NARRATIVE-BEAT-I2-V1"}, payload)
        return NarrativeBeat(
            ordinal=ordinal,
            source_span_sha256=payload["source_span_sha256"],
            paragraph_count=len(span),
            token_count=len(words),
            sentence_count=sentence_count,
            dialogue_turn_count=dialogue,
            first_person_count=first,
            second_person_count=second,
            third_person_count=third,
            negation_count=negation,
            modal_count=modal,
            authority_count=authority,
            temporal_count=temporal,
            dominant_perspective=dominant,
            relation_types=relations,
            distinction_mentions=mention_items,
            beat_hash72=beat_hash72,
        )

    def hydrate(
        self,
        source_text: str,
        *,
        source_id: str,
        source_epistemic_class: str,
        genesis_seed: GenesisSeed,
        grammar_rule_set: GrammarRuleSet,
        expected_source_sha256: str | None = None,
    ) -> NarrativeHydrationCandidate:
        if not source_id.strip():
            raise ValueError("P218_NARRATIVE_SOURCE_ID_EMPTY")
        if not validate_hash72(genesis_seed.genesis_seed_hash72):
            raise ValueError("P218_GENESIS_HASH72_INVALID")
        if not validate_hash72(grammar_rule_set.rule_set_hash72):
            raise ValueError("P218_GRAMMAR_RULE_SET_HASH72_INVALID")
        source_sha256 = sha256(source_text.encode("utf-8")).hexdigest()
        if expected_source_sha256 is not None and expected_source_sha256 != source_sha256:
            raise ValueError("P218_NARRATIVE_SOURCE_CHECKSUM_MISMATCH")
        paragraphs = _paragraphs(source_text)
        if not paragraphs:
            raise ValueError("P218_NARRATIVE_SOURCE_EMPTY")

        distinction_index = _distinction_index(genesis_seed)
        beats = tuple(
            self._beat(
                ordinal,
                paragraphs[start:start + self.paragraphs_per_beat],
                distinction_index,
            )
            for ordinal, start in enumerate(range(0, len(paragraphs), self.paragraphs_per_beat))
        )
        hydration_payload = {
            "schema": "HHS-P218-NARRATIVE-HYDRATION-I2-V1",
            "hydrator_version": PASS218_NARRATIVE_HYDRATOR_VERSION,
            "source_id": source_id,
            "source_sha256": source_sha256,
            "source_epistemic_class": source_epistemic_class,
            "genesis_seed_hash72": genesis_seed.genesis_seed_hash72,
            "grammar_rule_set_hash72": grammar_rule_set.rule_set_hash72,
            "grammar_validation_hash72": grammar_rule_set.validation_hash72,
            "beat_hash72_roots": [beat.beat_hash72 for beat in beats],
            "beat_count": len(beats),
            "verbatim_source_retained": False,
            "source_text_retained": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "authoritative_vector_store_promotion": False,
            "authoritative_float_weights": False,
        }
        hydration_hash72 = hash72_digest(
            {"domain": "HHS-P218-NARRATIVE-HYDRATION-I2-V1"}, hydration_payload
        )
        validation_payload = {
            "schema": "HHS-P218-NARRATIVE-HYDRATION-VALIDATION-I2-V1",
            "genesis_seed_hash72": genesis_seed.genesis_seed_hash72,
            "hydration_hash72": hydration_hash72,
            "source_sha256": source_sha256,
            "grammar_rule_set_hash72": grammar_rule_set.rule_set_hash72,
            "beat_count": len(beats),
            "beat_ordinals_contiguous": [beat.ordinal for beat in beats] == list(range(len(beats))),
            "all_beat_hashes_valid": all(validate_hash72(beat.beat_hash72) for beat in beats),
            "all_source_spans_digest_only": all(len(beat.source_span_sha256) == 64 for beat in beats),
            "verbatim_source_retained": False,
            "source_text_retained": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "authoritative_vector_store_promotion": False,
            "authoritative_float_weights": False,
        }
        validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-NARRATIVE-HYDRATION-VALIDATION-I2-V1"},
            validation_payload,
        )
        return NarrativeHydrationCandidate(
            source_id=source_id,
            source_sha256=source_sha256,
            source_epistemic_class=source_epistemic_class,
            genesis_seed_hash72=genesis_seed.genesis_seed_hash72,
            grammar_rule_set_hash72=grammar_rule_set.rule_set_hash72,
            beats=beats,
            hydration_hash72=hydration_hash72,
            validation_hash72=validation_hash72,
            hash216=genesis_seed.genesis_seed_hash72 + hydration_hash72 + validation_hash72,
        )

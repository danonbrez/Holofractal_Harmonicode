"""Pass 218 reference crawler for repository-native creative-writing evidence.

This module is deliberately bounded. It demonstrates deterministic discovery,
skip-by-default triage, ephemeral text analysis, nonverbatim feature retention,
native Hash72/Hash216 candidate receipts, and sequential closure. It does not
claim production semantic grounding or authoritative vector-store promotion.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import re
import statistics
import unicodedata
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72


WORD_RE = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
PHRASE_SPLIT_RE = re.compile(r"[,;:!?—–\n]+")
FORBIDDEN_RETAINED_KEYS = frozenset(
    {
        "content",
        "raw",
        "raw_bytes",
        "source_content",
        "source_text",
        "text",
        "tokens",
        "verbatim",
    }
)
REFERENCE_SCHEMA = "HHS-P218-REFERENCE-CANDIDATE-V1"
DEFAULT_CREATIVE_WRITING_ROOT = "creative_writing/the_invariant_keeper"


class Pass218PolicyError(ValueError):
    """Raised when a requested crawl target violates the reference policy."""


@dataclass(frozen=True)
class CrawlPolicy:
    """Bounded policy used by the Pass 218 reference evidence."""

    allowlisted_roots: tuple[str, ...] = (DEFAULT_CREATIVE_WRITING_ROOT,)
    allowed_suffixes: tuple[str, ...] = (".md",)
    max_file_bytes: int = 2_000_000
    minimum_long_span: int = 64
    source_authority: str = "REPOSITORY_NATIVE_CREATIVE_WRITING"
    rights_class: str = "REPOSITORY_NATIVE_TEST_AUTHORITY"
    policy_version: str = "HHS-P218-SKIP-DEFAULT-V1"
    perspective_profile: str = "HHS-USER-PERSPECTIVE-PENDING-GROUNDED-PROMOTION"


@dataclass
class Pass218ReferenceCrawler:
    """Reference-only crawler that never claims authoritative promotion."""

    repository_root: Path
    policy: CrawlPolicy = field(default_factory=CrawlPolicy)
    _seen_source_hashes: set[str] = field(default_factory=set, init=False)

    def __post_init__(self) -> None:
        self.repository_root = self.repository_root.resolve()
        if not self.repository_root.is_dir():
            raise Pass218PolicyError("P218_REPOSITORY_ROOT_MISSING")

    @staticmethod
    def _canonical_bytes(value: Any) -> bytes:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")

    def _relative_path(self, path: Path) -> str:
        resolved = path.resolve()
        try:
            return resolved.relative_to(self.repository_root).as_posix()
        except ValueError as exc:
            raise Pass218PolicyError("P218_PATH_OUTSIDE_REPOSITORY") from exc

    def _lexical_relative_path(self, path: Path) -> str:
        absolute = Path(os.path.abspath(path))
        try:
            return absolute.relative_to(self.repository_root).as_posix()
        except ValueError as exc:
            raise Pass218PolicyError("P218_PATH_OUTSIDE_REPOSITORY") from exc

    def _is_under_allowlist(self, path: Path) -> bool:
        resolved = path.resolve()
        for relative_root in self.policy.allowlisted_roots:
            root = (self.repository_root / relative_root).resolve()
            if resolved == root or root in resolved.parents:
                return True
        return False

    def _contains_symlink(self, path: Path) -> bool:
        current = Path(os.path.abspath(path))
        while True:
            if current.is_symlink():
                return True
            if current == self.repository_root:
                return False
            if self.repository_root not in current.parents:
                return True
            current = current.parent

    def triage(self, path: Path) -> dict[str, Any]:
        """Return a compact decision without reading eligible content."""

        path = Path(path)
        try:
            relative = self._lexical_relative_path(path)
        except Pass218PolicyError:
            return {
                "route": "SKIPPED",
                "reason": "OUTSIDE_REPOSITORY",
                "policy_version": self.policy.policy_version,
            }

        decision = {
            "route": "SKIPPED",
            "reason": "DEFAULT_SKIP",
            "relative_path": relative,
            "policy_version": self.policy.policy_version,
        }
        if not path.exists() and not path.is_symlink():
            decision["reason"] = "MISSING"
            return decision
        if self._contains_symlink(path):
            decision["reason"] = "SYMLINK_OR_ESCAPE"
            return decision
        if not self._is_under_allowlist(path):
            decision["reason"] = "OUTSIDE_ALLOWLIST"
            return decision
        if not path.is_file():
            decision["reason"] = "NOT_A_FILE"
            return decision
        if path.name.startswith("."):
            decision["reason"] = "HIDDEN_FILE"
            return decision
        if path.suffix.lower() not in self.policy.allowed_suffixes:
            decision["reason"] = "UNSUPPORTED_SUFFIX"
            return decision
        byte_count = path.stat().st_size
        if byte_count > self.policy.max_file_bytes:
            decision["reason"] = "SIZE_LIMIT"
            decision["byte_count"] = byte_count
            return decision

        decision.update(
            {
                "route": "CANDIDATE",
                "reason": "POSITIVE_REPOSITORY_NATIVE_EVIDENCE",
                "byte_count": byte_count,
                "source_authority": self.policy.source_authority,
                "rights_class": self.policy.rights_class,
            }
        )
        return decision

    def discover(self, relative_root: str = DEFAULT_CREATIVE_WRITING_ROOT) -> list[Path]:
        """Discover candidate files in deterministic repository-relative order."""

        root = self.repository_root / relative_root
        if not root.exists() or not root.is_dir():
            raise Pass218PolicyError("P218_ALLOWLISTED_CRAWL_ROOT_MISSING")
        if not self._is_under_allowlist(root) or self._contains_symlink(root):
            raise Pass218PolicyError("P218_ALLOWLISTED_CRAWL_ROOT_INVALID")

        candidates: list[Path] = []
        for current_root, directory_names, file_names in os.walk(
            root,
            topdown=True,
            followlinks=False,
        ):
            directory_names[:] = sorted(
                name
                for name in directory_names
                if not name.startswith(".")
                and not (Path(current_root) / name).is_symlink()
            )
            for file_name in sorted(file_names):
                candidate = Path(current_root) / file_name
                if self.triage(candidate)["route"] == "CANDIDATE":
                    candidates.append(candidate)

        return sorted(candidates, key=self._relative_path)

    @staticmethod
    def _words(text: str) -> list[str]:
        return [match.group(0).lower() for match in WORD_RE.finditer(text)]

    @staticmethod
    def _syllable_proxy(word: str) -> int:
        groups = re.findall(r"[aeiouy]+", word.lower())
        return max(1, len(groups))

    @staticmethod
    def _vowel_signature(word: str) -> str:
        groups = re.findall(r"[aeiouy]+", word.lower())
        return groups[-1] if groups else ""

    @staticmethod
    def _rhyme_key(word: str) -> str:
        lowered = re.sub(r"[^a-z]", "", word.lower())
        match = re.search(r"[aeiouy][a-z]*$", lowered)
        return match.group(0)[-5:] if match else lowered[-3:]

    @classmethod
    def _rhyme_scheme(cls, text: str, limit: int = 64) -> str:
        keys: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            words = cls._words(stripped)
            if words:
                keys.append(cls._rhyme_key(words[-1]))
            if len(keys) == limit:
                break

        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        classes: dict[str, str] = {}
        scheme: list[str] = []
        for key in keys:
            if key not in classes:
                index = len(classes)
                classes[key] = alphabet[index] if index < len(alphabet) else "*"
            scheme.append(classes[key])
        return "".join(scheme)

    @classmethod
    def extract_style_vector(cls, text: str) -> dict[str, Any]:
        """Return aggregate, deterministic, nonverbatim style features."""

        words = cls._words(text)
        sentences = [
            segment.strip()
            for segment in SENTENCE_SPLIT_RE.split(text)
            if cls._words(segment)
        ]
        phrases = [
            cls._words(segment)
            for segment in PHRASE_SPLIT_RE.split(text)
            if cls._words(segment)
        ]

        word_lengths = [len(word) for word in words]
        phrase_word_medians = [
            float(statistics.median(len(word) for word in phrase))
            for phrase in phrases
        ]
        phrase_syllables = [
            sum(cls._syllable_proxy(word) for word in phrase)
            for phrase in phrases
        ]
        sentence_word_counts = [len(cls._words(sentence)) for sentence in sentences]

        adjacent_pairs = max(0, len(words) - 1)
        alliterative_pairs = sum(
            1
            for first, second in zip(words, words[1:])
            if first[0] == second[0]
        )
        assonant_pairs = sum(
            1
            for first, second in zip(words, words[1:])
            if cls._vowel_signature(first)
            and cls._vowel_signature(first) == cls._vowel_signature(second)
        )

        unique_words = len(set(words))
        type_token_ratio = unique_words / len(words) if words else 0.0
        long_word_ratio = (
            sum(1 for length in word_lengths if length >= 8) / len(word_lengths)
            if word_lengths
            else 0.0
        )
        rhythm_variance = (
            statistics.pvariance(phrase_syllables)
            if len(phrase_syllables) > 1
            else 0.0
        )

        vector = {
            "schema": "HHS-P218-POETIC-STYLE-VECTOR-V1",
            "word_count": len(words),
            "unique_word_count": unique_words,
            "sentence_count": len(sentences),
            "phrase_count": len(phrases),
            "median_word_length": (
                float(statistics.median(word_lengths)) if word_lengths else 0.0
            ),
            "median_word_length_per_phrase": (
                float(statistics.median(phrase_word_medians))
                if phrase_word_medians
                else 0.0
            ),
            "median_sentence_words": (
                float(statistics.median(sentence_word_counts))
                if sentence_word_counts
                else 0.0
            ),
            "median_phrase_syllable_proxy": (
                float(statistics.median(phrase_syllables))
                if phrase_syllables
                else 0.0
            ),
            "rhythm_phrase_syllable_variance_proxy": float(rhythm_variance),
            "alliteration_adjacent_pair_density": (
                alliterative_pairs / adjacent_pairs if adjacent_pairs else 0.0
            ),
            "assonance_adjacent_pair_density_proxy": (
                assonant_pairs / adjacent_pairs if adjacent_pairs else 0.0
            ),
            "vocabulary_type_token_ratio": float(type_token_ratio),
            "vocabulary_long_word_ratio": float(long_word_ratio),
            "rhyme_scheme_pattern": cls._rhyme_scheme(text),
            "mythology_temperature": None,
            "poetic_temperature_scalar": None,
            "meter_profile_status": "REQUIRES_PRONUNCIATION_AND_STRESS_AUTHORITY",
            "semantic_compression_status": "REQUIRES_GROUNDED_SEMANTIC_GRAPH",
        }
        for value in vector.values():
            if isinstance(value, float) and not math.isfinite(value):
                raise RuntimeError("P218_NONFINITE_STYLE_VECTOR")
        return vector

    def _grounding_inventory(self) -> dict[str, Any]:
        runtime_root = self.repository_root / "hhs_runtime"
        wordnet_files = sorted(
            path.name for path in runtime_root.glob("Wordnet*.csv") if path.is_file()
        )
        return {
            "wordnet_csv_inventory_count": len(wordnet_files),
            "wordnet_csv_inventory_hash": sha256(
                "\n".join(wordnet_files).encode("utf-8")
            ).hexdigest(),
            "wordnet_sense_disambiguation_complete": False,
            "word2vec_distributional_hydration_complete": False,
            "open_weight_contextual_hydration_complete": False,
            "user_perspective_semantic_validation_complete": False,
            "perspective_profile": self.policy.perspective_profile,
            "authoritative_semantic_promotion_ready": False,
        }

    @staticmethod
    def _contains_forbidden_key(value: Any) -> bool:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if str(key).lower() in FORBIDDEN_RETAINED_KEYS:
                    return True
                if Pass218ReferenceCrawler._contains_forbidden_key(child):
                    return True
        elif isinstance(value, (list, tuple)):
            return any(
                Pass218ReferenceCrawler._contains_forbidden_key(child)
                for child in value
            )
        return False

    def _validate_nonretention(self, record: Mapping[str, Any], text: str) -> bool:
        if self._contains_forbidden_key(record):
            return False
        serialized = self._canonical_bytes(record).decode("utf-8")
        for line in text.splitlines():
            normalized = " ".join(line.split())
            if len(normalized) >= self.policy.minimum_long_span:
                probe = normalized[: self.policy.minimum_long_span]
                if probe in serialized:
                    return False
        return True

    def _skip_duplicate(
        self,
        triage: Mapping[str, Any],
        source_hash: str,
    ) -> dict[str, Any]:
        payload = {
            "schema": "HHS-P218-COMPACT-SKIP-RECEIPT-V1",
            "status": "SKIP_DUPLICATE",
            "relative_path": triage["relative_path"],
            "source_sha256": source_hash,
            "policy_version": self.policy.policy_version,
        }
        payload["skip_receipt_sha256"] = sha256(
            self._canonical_bytes(payload)
        ).hexdigest()
        return payload

    def crawl_file(
        self,
        path: Path,
        *,
        parent_closure_hash72: str | None = None,
    ) -> dict[str, Any]:
        """Process one candidate; source bytes/text remain local to this call."""

        triage = self.triage(path)
        if triage["route"] != "CANDIDATE":
            return {
                "schema": "HHS-P218-COMPACT-SKIP-RECEIPT-V1",
                "status": "SKIPPED",
                "reason": triage["reason"],
                "relative_path": triage.get("relative_path"),
                "policy_version": self.policy.policy_version,
            }

        state_trace = ["DISCOVERED", "ACQUIRED_EPHEMERAL"]
        raw_bytes = Path(path).read_bytes()
        source_hash = sha256(raw_bytes).hexdigest()
        if source_hash in self._seen_source_hashes:
            return self._skip_duplicate(triage, source_hash)

        try:
            text = unicodedata.normalize(
                "NFC",
                raw_bytes.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"),
            )
        except UnicodeDecodeError as exc:
            return {
                "schema": "HHS-P218-COMPACT-SKIP-RECEIPT-V1",
                "status": "REJECTED",
                "reason": "INVALID_UTF8",
                "relative_path": triage["relative_path"],
                "source_sha256": source_hash,
                "policy_version": self.policy.policy_version,
                "error_type": type(exc).__name__,
            }

        state_trace.append("NORMALIZED")
        style_vector = self.extract_style_vector(text)
        state_trace.append("EXTRACTED")
        grounding = self._grounding_inventory()
        state_trace.append("REFERENCE_GROUNDING_INVENTORIED")

        manifest = {
            "relative_path": triage["relative_path"],
            "byte_count": len(raw_bytes),
            "source_sha256": source_hash,
            "source_authority": triage["source_authority"],
            "rights_class": triage["rights_class"],
            "media_type": "text/markdown",
            "encoding": "utf-8",
            "policy_version": self.policy.policy_version,
        }
        abstraction = {
            "feature_schema": style_vector["schema"],
            "style_vector": style_vector,
            "grounding_inventory": grounding,
            "verbatim_retention": False,
            "authoritative_semantic_promotion": False,
        }
        parent = parent_closure_hash72 or hash72_digest(
            {"domain": "HHS-P218-REFERENCE-GENESIS-V1"},
            self.policy.allowlisted_roots,
        )
        receipt_payload = {
            "schema": REFERENCE_SCHEMA,
            "parent_closure_hash72": parent,
            "manifest_root_sha256": sha256(
                self._canonical_bytes(manifest)
            ).hexdigest(),
            "abstraction_root_sha256": sha256(
                self._canonical_bytes(abstraction)
            ).hexdigest(),
            "validators": {
                "bounded_allowlist": True,
                "deterministic_feature_schema": True,
                "grounding_promotion_ready": False,
                "nonverbatim_candidate": None,
                "native_hash72": True,
            },
            "purge_claim": "LOGICAL_EPHEMERAL_RELEASE_ONLY",
            "physical_erasure_claimed": False,
        }

        source_hash72 = hash72_digest(
            {"domain": "HHS-P218-SOURCE-MANIFEST-V1"},
            manifest,
        )
        abstraction_hash72 = hash72_digest(
            {"domain": "HHS-P218-NONVERBATIM-ABSTRACTION-V1"},
            abstraction,
        )

        candidate_without_receipt = {
            "schema": REFERENCE_SCHEMA,
            "status": "REFERENCE_CANDIDATE",
            "manifest": manifest,
            "abstraction": abstraction,
            "parent_closure_hash72": parent,
            "source_hash72": source_hash72,
            "abstraction_hash72": abstraction_hash72,
        }
        if not self._validate_nonretention(candidate_without_receipt, text):
            return {
                "schema": "HHS-P218-COMPACT-SKIP-RECEIPT-V1",
                "status": "QUARANTINED",
                "reason": "NONRETENTION_VALIDATION_FAILURE",
                "relative_path": triage["relative_path"],
                "source_sha256": source_hash,
                "policy_version": self.policy.policy_version,
            }

        receipt_payload["validators"]["nonverbatim_candidate"] = True
        receipt_hash72 = hash72_digest(
            {"domain": "HHS-P218-REFERENCE-VALIDATION-RECEIPT-V1"},
            receipt_payload,
        )
        hash216 = source_hash72 + abstraction_hash72 + receipt_hash72
        if (
            len(hash216) != 216
            or not validate_hash72(hash216[:72])
            or not validate_hash72(hash216[72:144])
            or not validate_hash72(hash216[144:])
        ):
            raise RuntimeError("P218_HASH216_CANDIDATE_INVALID")

        state_trace.extend(
            [
                "REFERENCE_VALIDATED",
                "CANDIDATE_COMMITTED",
                "VERBATIM_PURGED",
                "CLOSED",
            ]
        )
        closure_hash72 = hash72_digest(
            {"domain": "HHS-P218-REFERENCE-CLOSURE-V1"},
            hash216,
        )
        record = {
            **candidate_without_receipt,
            "status": "CLOSED",
            "promotion_eligible": False,
            "receipt_payload": receipt_payload,
            "receipt_hash72": receipt_hash72,
            "hash216": hash216,
            "closure_hash72": closure_hash72,
            "state_trace": state_trace,
            "retained_artifact_inventory": [
                "source_manifest_metadata",
                "source_sha256",
                "aggregate_style_vector",
                "grounding_inventory",
                "hash72_segments",
                "hash216_candidate",
                "closure_hash72",
                "validation_and_logical_purge_receipt",
            ],
        }

        if not self._validate_nonretention(record, text):
            raise RuntimeError("P218_POST_RECEIPT_NONRETENTION_FAILURE")

        self._seen_source_hashes.add(source_hash)
        del text
        del raw_bytes
        return record

    def crawl_folder(
        self,
        relative_root: str = DEFAULT_CREATIVE_WRITING_ROOT,
    ) -> list[dict[str, Any]]:
        """Crawl one file at a time, chaining only after prior closure."""

        results: list[dict[str, Any]] = []
        parent = hash72_digest(
            {"domain": "HHS-P218-REFERENCE-FOLDER-GENESIS-V1"},
            relative_root,
        )
        for path in self.discover(relative_root):
            record = self.crawl_file(path, parent_closure_hash72=parent)
            if record["status"] == "CLOSED":
                parent = record["closure_hash72"]
            elif record["status"] not in {
                "SKIPPED",
                "SKIP_DUPLICATE",
                "REJECTED",
                "QUARANTINED",
            }:
                raise RuntimeError("P218_NONTERMINAL_REFERENCE_RECORD")
            results.append(record)
        return results

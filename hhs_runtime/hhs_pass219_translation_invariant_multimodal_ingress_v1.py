"""Pass 219 translation-invariant multimodal open-source ingress v1.

This layer composes revision-pinned open-source repository provenance with the
existing Pass 165 multimodal analyzer. It preserves raw source identity while
allowing external multilingual/multimodal models to contribute *candidate*
semantic projections that can converge on a shared translation-invariant
semantic family.

No network access, model execution, canonical learning commit, VM81 mutation,
Hash72 authority minting, canonical Hash216 minting, or truth promotion occurs
inside this module. Remote fetching and model execution remain outside the
canonical kernel and must provide immutable repository revisions plus exact
output receipts.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
import re
import unicodedata
from typing import Any, Mapping, Protocol, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import WordRelationEntry, tokenize_words
from hhs_runtime.pass165.ingestion import IngestionResult, MultimodalLearningService

VERSION = "HHS-P219-TRANSLATION-INVARIANT-MULTIMODAL-INGRESS-V1"
ARTIFACT_SCHEMA = "HHS-P219-OPEN-SOURCE-INGRESS-ARTIFACT-V1"
PROJECTION_SCHEMA = "HHS-P219-TRANSLATION-INVARIANT-PROJECTION-V1"
BATCH_SCHEMA = "HHS-P219-TRANSLATION-INVARIANT-HYDRATION-BATCH-V1"
MAX_ARTIFACT_BYTES = 16 * 1024 * 1024
MAX_PROJECTIONS = 32
MAX_PIVOT_CHARS = 32768
MAX_LABELS = 256
IMMUTABLE_REVISION = re.compile(r"[0-9a-f]{40}")
SHA256_HEX = re.compile(r"[0-9a-f]{64}")

ALLOWED_PROVIDERS = frozenset({"HUGGING_FACE", "GITHUB"})
ALLOWED_REPO_KINDS = frozenset({"MODEL", "DATASET", "CODE", "SPACE"})
ALLOWED_LICENSES = frozenset({
    "apache-2.0",
    "mit",
    "bsd-2-clause",
    "bsd-3-clause",
    "cc-by-4.0",
})


class TranslationInvariantIngressError(RuntimeError):
    """Fail-closed error for repository and projection admission."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _normalize_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", str(value)).casefold().split())


def _upper(value: str) -> str:
    return "_".join(str(value).strip().upper().split())


def _ordered_unique(values: Sequence[str], *, lower: bool = False) -> tuple[str, ...]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in values:
        value = _normalize_text(raw) if lower else str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return tuple(out)


def _fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


@dataclass(frozen=True)
class OpenSourceRepositoryDescriptor:
    provider: str
    repo_id: str
    revision: str
    license_id: str
    repo_kind: str
    source_url: str
    modalities: tuple[str, ...] = ()

    def validated(self) -> "OpenSourceRepositoryDescriptor":
        provider = _upper(self.provider)
        repo_kind = _upper(self.repo_kind)
        repo_id = str(self.repo_id).strip()
        revision = str(self.revision).strip().lower()
        license_id = str(self.license_id).strip().lower()
        source_url = str(self.source_url).strip()
        if provider not in ALLOWED_PROVIDERS:
            raise TranslationInvariantIngressError("P219_TIMI_PROVIDER_NOT_ALLOWED")
        if repo_kind not in ALLOWED_REPO_KINDS:
            raise TranslationInvariantIngressError("P219_TIMI_REPO_KIND_NOT_ALLOWED")
        if not repo_id or "/" not in repo_id:
            raise TranslationInvariantIngressError("P219_TIMI_REPO_ID_INVALID")
        if IMMUTABLE_REVISION.fullmatch(revision) is None:
            raise TranslationInvariantIngressError("P219_TIMI_IMMUTABLE_REVISION_REQUIRED")
        if license_id not in ALLOWED_LICENSES:
            raise TranslationInvariantIngressError("P219_TIMI_LICENSE_NOT_ALLOWED")
        if not source_url.startswith("https://"):
            raise TranslationInvariantIngressError("P219_TIMI_SOURCE_URL_HTTPS_REQUIRED")
        modalities = tuple(_upper(item) for item in _ordered_unique(self.modalities))
        return OpenSourceRepositoryDescriptor(
            provider=provider,
            repo_id=repo_id,
            revision=revision,
            license_id=license_id,
            repo_kind=repo_kind,
            source_url=source_url,
            modalities=modalities,
        )

    def receipt_body(self) -> dict[str, Any]:
        item = self.validated()
        return {
            "provider": item.provider,
            "repo_id": item.repo_id,
            "revision": item.revision,
            "license_id": item.license_id,
            "repo_kind": item.repo_kind,
            "source_url": item.source_url,
            "modalities": list(item.modalities),
        }


@dataclass(frozen=True)
class RepositoryArtifact:
    repository: OpenSourceRepositoryDescriptor
    path: str
    content: bytes
    declared_media_type: str | None = None
    source_language: str | None = None

    def validated(self) -> "RepositoryArtifact":
        repository = self.repository.validated()
        path = str(self.path).strip().lstrip("/")
        raw = bytes(self.content)
        if not path or ".." in path.split("/"):
            raise TranslationInvariantIngressError("P219_TIMI_ARTIFACT_PATH_INVALID")
        if not raw:
            raise TranslationInvariantIngressError("P219_TIMI_ARTIFACT_EMPTY")
        if len(raw) > MAX_ARTIFACT_BYTES:
            raise TranslationInvariantIngressError("P219_TIMI_ARTIFACT_SIZE_BOUND")
        declared = self.declared_media_type.upper() if self.declared_media_type else None
        language = _normalize_text(self.source_language) if self.source_language else None
        return RepositoryArtifact(repository, path, raw, declared, language)


@dataclass(frozen=True)
class ExactSemanticProjection:
    model_repository: OpenSourceRepositoryDescriptor
    pivot_text: str
    source_language: str
    pivot_language: str
    source_modality: str
    model_output_sha256: str
    vector_identity_sha256: str
    similarity_numerator: int
    similarity_denominator: int
    semantic_labels: tuple[str, ...] = ()
    translation_chain: tuple[str, ...] = ()
    candidate_only: bool = True

    def validated(self) -> "ExactSemanticProjection":
        model = self.model_repository.validated()
        pivot = " ".join(str(self.pivot_text).split())
        if not pivot or len(pivot) > MAX_PIVOT_CHARS:
            raise TranslationInvariantIngressError("P219_TIMI_PIVOT_TEXT_INVALID")
        source_language = _normalize_text(self.source_language)
        pivot_language = _normalize_text(self.pivot_language)
        if not source_language or not pivot_language:
            raise TranslationInvariantIngressError("P219_TIMI_LANGUAGE_REQUIRED")
        modality = _upper(self.source_modality)
        output_sha = str(self.model_output_sha256).lower()
        vector_sha = str(self.vector_identity_sha256).lower()
        if SHA256_HEX.fullmatch(output_sha) is None or SHA256_HEX.fullmatch(vector_sha) is None:
            raise TranslationInvariantIngressError("P219_TIMI_PROJECTION_HASH_INVALID")
        if isinstance(self.similarity_numerator, bool) or isinstance(self.similarity_denominator, bool):
            raise TranslationInvariantIngressError("P219_TIMI_SIMILARITY_INTEGER_REQUIRED")
        try:
            similarity = Fraction(int(self.similarity_numerator), int(self.similarity_denominator))
        except (ValueError, ZeroDivisionError) as exc:
            raise TranslationInvariantIngressError("P219_TIMI_SIMILARITY_INVALID") from exc
        if similarity < 0 or similarity > 1:
            raise TranslationInvariantIngressError("P219_TIMI_SIMILARITY_RANGE")
        if self.candidate_only is not True:
            raise TranslationInvariantIngressError("P219_TIMI_PROJECTION_AUTHORITY_DRIFT")
        labels = _ordered_unique(self.semantic_labels, lower=True)
        if len(labels) > MAX_LABELS:
            raise TranslationInvariantIngressError("P219_TIMI_LABEL_BOUND")
        chain = _ordered_unique(self.translation_chain)
        return ExactSemanticProjection(
            model_repository=model,
            pivot_text=pivot,
            source_language=source_language,
            pivot_language=pivot_language,
            source_modality=modality,
            model_output_sha256=output_sha,
            vector_identity_sha256=vector_sha,
            similarity_numerator=similarity.numerator,
            similarity_denominator=similarity.denominator,
            semantic_labels=labels,
            translation_chain=chain,
            candidate_only=True,
        )

    @property
    def similarity(self) -> Fraction:
        item = self.validated()
        return Fraction(item.similarity_numerator, item.similarity_denominator)


class SemanticProjectionProvider(Protocol):
    def project(self, artifact: RepositoryArtifact) -> Sequence[ExactSemanticProjection]: ...


class TranslationInvariantMultimodalIngress:
    """Revision-pinned candidate ingress over Pass 165 analysis."""

    def __init__(
        self,
        relation_db: Mapping[str, WordRelationEntry],
        projector: SemanticProjectionProvider,
        *,
        pass165: MultimodalLearningService | None = None,
        minimum_similarity: Fraction = Fraction(1, 2),
    ) -> None:
        if not relation_db:
            raise TranslationInvariantIngressError("P219_TIMI_WORDNET_REQUIRED")
        if minimum_similarity < 0 or minimum_similarity > 1:
            raise TranslationInvariantIngressError("P219_TIMI_MINIMUM_SIMILARITY_RANGE")
        self.relation_db = relation_db
        self.projector = projector
        self.pass165 = pass165 or MultimodalLearningService()
        self.minimum_similarity = minimum_similarity

    def _semantic_terms(self, pivot_text: str, labels: Sequence[str]) -> tuple[str, ...]:
        terms: set[str] = {_normalize_text(item) for item in labels if _normalize_text(item)}
        for token in tokenize_words(pivot_text):
            normalized = _normalize_text(token)
            if not normalized:
                continue
            terms.add(normalized)
            entry = self.relation_db.get(normalized)
            if entry is None:
                continue
            for family in (entry.synonyms, entry.hypernyms, entry.hyponyms):
                for value in family:
                    normalized_value = _normalize_text(value)
                    if normalized_value:
                        terms.add(normalized_value)
        return tuple(sorted(terms))

    def _projection_record(self, projection: ExactSemanticProjection) -> dict[str, Any]:
        item = projection.validated()
        terms = self._semantic_terms(item.pivot_text, item.semantic_labels)
        family_body = {
            "pivot_language": item.pivot_language,
            "semantic_terms": list(terms),
            "semantic_labels": list(item.semantic_labels),
        }
        family_hash72 = hash72_digest(
            {"domain": "HHS-P219-TRANSLATION-INVARIANT-SEMANTIC-FAMILY-V1"},
            family_body,
        )
        body = {
            "schema": PROJECTION_SCHEMA,
            "model_repository": item.model_repository.receipt_body(),
            "pivot_text": item.pivot_text,
            "source_language": item.source_language,
            "pivot_language": item.pivot_language,
            "source_modality": item.source_modality,
            "model_output_sha256": item.model_output_sha256,
            "vector_identity_sha256": item.vector_identity_sha256,
            "similarity": _fraction_record(item.similarity),
            "semantic_labels": list(item.semantic_labels),
            "semantic_terms": list(terms),
            "translation_chain": list(item.translation_chain),
            "translation_invariant_semantic_family_hash72": family_hash72,
            "candidate_only": True,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "vm81_commit_invoked": False,
            "canonical_hash216_minted": False,
        }
        body["projection_receipt_hash72"] = hash72_digest(
            {"domain": PROJECTION_SCHEMA}, body
        )
        return body

    def analyze_artifact(self, artifact: RepositoryArtifact) -> dict[str, Any]:
        item = artifact.validated()
        repository = item.repository.validated()
        provenance = (
            f"{repository.provider}:{repository.repo_id}@{repository.revision}:{item.path}"
        )
        analysis: IngestionResult = self.pass165.analyze(
            item.content,
            declared_media_type=item.declared_media_type,
            provenance=provenance,
            authorization_scope="PASS219_TRANSLATION_INVARIANT_OPEN_SOURCE_CANDIDATE",
        )
        source_sha = sha256(item.content).hexdigest()
        if analysis.source.source_hash != source_sha:
            raise TranslationInvariantIngressError("P219_TIMI_PASS165_SOURCE_HASH_DIVERGENCE")
        projected = tuple(self.projector.project(item))
        if len(projected) > MAX_PROJECTIONS:
            raise TranslationInvariantIngressError("P219_TIMI_PROJECTION_BOUND")
        projection_records = [self._projection_record(projection) for projection in projected]
        projection_records.sort(
            key=lambda value: (
                Fraction(value["similarity"]["numerator"], value["similarity"]["denominator"]),
                len(value["semantic_terms"]),
                value["projection_receipt_hash72"],
            ),
            reverse=True,
        )
        selected = projection_records[0] if projection_records else None
        if selected is None:
            classification = "HOLD_NO_SEMANTIC_PROJECTION"
        else:
            score = Fraction(
                selected["similarity"]["numerator"],
                selected["similarity"]["denominator"],
            )
            classification = (
                "TRANSLATION_INVARIANT_CANDIDATE"
                if score >= self.minimum_similarity and selected["semantic_terms"]
                else "HOLD_SEMANTIC_PROJECTION_BELOW_THRESHOLD"
            )
        body = {
            "schema": ARTIFACT_SCHEMA,
            "version": VERSION,
            "repository": repository.receipt_body(),
            "artifact_path": item.path,
            "source_language": item.source_language,
            "source_sha256": source_sha,
            "source_byte_length": len(item.content),
            "pass165_detected_media_type": analysis.source.detected_media_type,
            "pass165_projection_hash72": analysis.projection_hash72,
            "pass165_token_stream_root": analysis.token_stream_root,
            "pass165_chunk_graph_root": analysis.chunk_graph_root,
            "pass165_ingestion_operation_hash216": analysis.ingestion_operation_hash216,
            "semantic_projections": projection_records,
            "selected_projection_receipt_hash72": (
                selected["projection_receipt_hash72"] if selected else None
            ),
            "translation_invariant_semantic_family_hash72": (
                selected["translation_invariant_semantic_family_hash72"] if selected else None
            ),
            "semantic_terms": selected["semantic_terms"] if selected else [],
            "classification": classification,
            "raw_source_identity_preserved": True,
            "remote_fetch_performed_by_kernel": False,
            "external_model_output_is_candidate_evidence": True,
            "candidate_only": True,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "vm81_commit_invoked": False,
            "canonical_hash72_minted": False,
            "canonical_hash216_minted": False,
            "requires_i29_or_equivalent_validation_before_lane5": True,
        }
        body["artifact_receipt_hash72"] = hash72_digest(
            {"domain": ARTIFACT_SCHEMA}, body
        )
        return body

    def analyze_batch(self, artifacts: Sequence[RepositoryArtifact]) -> dict[str, Any]:
        if not artifacts:
            raise TranslationInvariantIngressError("P219_TIMI_BATCH_EMPTY")
        records = [self.analyze_artifact(item) for item in artifacts]
        groups: dict[str, list[dict[str, Any]]] = {}
        for record in records:
            family = record.get("translation_invariant_semantic_family_hash72")
            if family:
                groups.setdefault(str(family), []).append(record)
        families: list[dict[str, Any]] = []
        for family_hash72, members in sorted(groups.items()):
            languages = sorted({str(item.get("source_language") or "") for item in members if item.get("source_language")})
            modalities = sorted({str(item["pass165_detected_media_type"]) for item in members})
            providers = sorted({str(item["repository"]["provider"]) for item in members})
            sources = sorted(str(item["source_sha256"]) for item in members)
            families.append({
                "semantic_family_hash72": family_hash72,
                "member_count": len(members),
                "source_languages": languages,
                "modalities": modalities,
                "providers": providers,
                "source_sha256": sources,
                "cross_language_correspondence_observed": len(languages) > 1,
                "cross_modal_correspondence_observed": len(modalities) > 1,
                "translation_invariance_status": "CANDIDATE_CORRESPONDENCE_NOT_TRUTH_PROOF",
            })
        body = {
            "schema": BATCH_SCHEMA,
            "version": VERSION,
            "record_count": len(records),
            "records": records,
            "semantic_families": families,
            "candidate_family_count": len(families),
            "translation_invariance_semantics": (
                "SHARED_REVISION_PINNED_CANDIDATE_SEMANTIC_FAMILY_WITH_DISTINCT_RAW_SOURCE_IDENTITIES"
            ),
            "candidate_only": True,
            "truth_promotion": False,
            "canonical_learning_commit_invoked": False,
            "vm81_commit_invoked": False,
            "canonical_hash216_minted": False,
        }
        body["batch_receipt_hash72"] = hash72_digest({"domain": BATCH_SCHEMA}, body)
        body["candidate_index_sha256"] = sha256(_canonical_bytes(body)).hexdigest()
        return body


__all__ = [
    "ALLOWED_LICENSES",
    "ARTIFACT_SCHEMA",
    "BATCH_SCHEMA",
    "ExactSemanticProjection",
    "OpenSourceRepositoryDescriptor",
    "PROJECTION_SCHEMA",
    "RepositoryArtifact",
    "SemanticProjectionProvider",
    "TranslationInvariantIngressError",
    "TranslationInvariantMultimodalIngress",
    "VERSION",
]

"""Pass 219 live acquisition and replay worker v1.

This application-boundary worker acquires revision-pinned public repository
artifacts, verifies their byte identity before analysis, accepts externally
executed semantic projection evidence, and composes the verified material with
the merged translation-invariant multimodal ingress.

Network transfer and model execution are explicitly noncanonical. Replay can
be performed from archived source/output bytes without network access or model
execution. Neither path can mint truth, action authority, VM81 state, or
canonical Hash72/Hash216 state.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import ipaddress
import json
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Mapping, Protocol, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.hhs_pass219_translation_invariant_multimodal_ingress_v1 import (
    MAX_ARTIFACT_BYTES,
    ExactSemanticProjection,
    OpenSourceRepositoryDescriptor,
    RepositoryArtifact,
    TranslationInvariantMultimodalIngress,
)
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import WordRelationEntry
from hhs_runtime.pass165.ingestion import MultimodalLearningService

VERSION = "HHS-P219-LIVE-ACQUISITION-REPLAY-WORKER-V1"
SOURCE_SCHEMA = "HHS-P219-LIVE-ACQUISITION-SOURCE-V1"
PROJECTION_SCHEMA = "HHS-P219-EXTERNAL-PROJECTION-EVIDENCE-V1"
REPORT_SCHEMA = "HHS-P219-LIVE-ACQUISITION-REPLAY-REPORT-V1"
REPLAY_CLOSURE_SCHEMA = "HHS-P219-LARW-REPLAY-CLOSURE-V1"
SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")
MAX_PROJECTION_OUTPUT_BYTES = 8 * 1024 * 1024
MAX_VECTOR_IDENTITY_BYTES = 8 * 1024 * 1024
MAX_PROJECTIONS = 32
DEFAULT_TIMEOUT_SECONDS = 30


class LiveAcquisitionReplayError(RuntimeError):
    """Fail-closed error for the external acquisition/replay boundary."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _safe_path(value: str) -> str:
    path = str(value).strip().lstrip("/")
    parts = path.split("/")
    if not path or any(part in {"", ".", ".."} for part in parts):
        raise LiveAcquisitionReplayError("P219_LARW_ARTIFACT_PATH_INVALID")
    return path


def _safe_revision(value: str) -> str:
    revision = str(value).strip().lower()
    if re.fullmatch(r"[0-9a-f]{40}", revision) is None:
        raise LiveAcquisitionReplayError("P219_LARW_IMMUTABLE_REVISION_REQUIRED")
    return revision


def _provider_host_allowed(provider: str, host: str) -> bool:
    normalized = host.lower().rstrip(".")
    if provider == "GITHUB":
        return normalized == "raw.githubusercontent.com"
    if provider == "HUGGING_FACE":
        return (
            normalized == "huggingface.co"
            or normalized.endswith(".huggingface.co")
            or normalized.endswith(".hf.co")
        )
    return False


def _assert_public_host(provider: str, host: str) -> None:
    if not _provider_host_allowed(provider, host):
        raise LiveAcquisitionReplayError("P219_LARW_PROVIDER_HOST_MISMATCH")
    try:
        infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise LiveAcquisitionReplayError("P219_LARW_DNS_RESOLUTION_FAILED") from exc
    if not infos:
        raise LiveAcquisitionReplayError("P219_LARW_DNS_RESOLUTION_EMPTY")
    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_multicast
            or address.is_reserved
            or address.is_unspecified
        ):
            raise LiveAcquisitionReplayError("P219_LARW_NONPUBLIC_ADDRESS_REJECTED")


@dataclass(frozen=True)
class AcquisitionSourceSpec:
    repository: OpenSourceRepositoryDescriptor
    artifact_path: str
    expected_sha256: str
    expected_byte_length: int
    declared_media_type: str | None = None
    source_language: str | None = None

    def validated(self) -> "AcquisitionSourceSpec":
        repository = self.repository.validated()
        path = _safe_path(self.artifact_path)
        expected_sha = str(self.expected_sha256).strip().lower()
        if SHA256_HEX.fullmatch(expected_sha) is None:
            raise LiveAcquisitionReplayError("P219_LARW_EXPECTED_SHA256_INVALID")
        if isinstance(self.expected_byte_length, bool):
            raise LiveAcquisitionReplayError("P219_LARW_EXPECTED_LENGTH_INVALID")
        expected_length = int(self.expected_byte_length)
        if expected_length <= 0 or expected_length > MAX_ARTIFACT_BYTES:
            raise LiveAcquisitionReplayError("P219_LARW_EXPECTED_LENGTH_BOUND")
        media = str(self.declared_media_type).strip() if self.declared_media_type else None
        language = str(self.source_language).strip() if self.source_language else None
        return AcquisitionSourceSpec(
            repository=repository,
            artifact_path=path,
            expected_sha256=expected_sha,
            expected_byte_length=expected_length,
            declared_media_type=media,
            source_language=language,
        )

    def pinned_url(self) -> str:
        item = self.validated()
        repository = item.repository
        revision = _safe_revision(repository.revision)
        quoted_path = "/".join(
            urllib.parse.quote(part, safe="") for part in item.artifact_path.split("/")
        )
        quoted_repo = "/".join(
            urllib.parse.quote(part, safe="") for part in repository.repo_id.split("/")
        )
        if repository.provider == "GITHUB":
            return f"https://raw.githubusercontent.com/{quoted_repo}/{revision}/{quoted_path}"
        if repository.provider == "HUGGING_FACE":
            return f"https://huggingface.co/{quoted_repo}/resolve/{revision}/{quoted_path}"
        raise LiveAcquisitionReplayError("P219_LARW_PROVIDER_UNSUPPORTED")

    def receipt_body(self) -> dict[str, Any]:
        item = self.validated()
        return {
            "repository": item.repository.receipt_body(),
            "artifact_path": item.artifact_path,
            "expected_sha256": item.expected_sha256,
            "expected_byte_length": item.expected_byte_length,
            "declared_media_type": item.declared_media_type,
            "source_language": item.source_language,
            "pinned_url": item.pinned_url(),
        }


@dataclass(frozen=True)
class FetchResponse:
    requested_url: str
    final_url: str
    status: int
    body: bytes
    headers: tuple[tuple[str, str], ...] = ()

    def normalized_headers(self) -> tuple[tuple[str, str], ...]:
        allowed = {"content-length", "content-type", "etag", "last-modified"}
        values = {
            (str(key).strip().lower(), " ".join(str(value).split()))
            for key, value in self.headers
            if str(key).strip().lower() in allowed and str(value).strip()
        }
        return tuple(sorted(values))


class SourceTransport(Protocol):
    def fetch(self, spec: AcquisitionSourceSpec) -> FetchResponse: ...


class _StrictRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, provider: str):
        super().__init__()
        self.provider = provider

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        parsed = urllib.parse.urlparse(newurl)
        if parsed.scheme != "https" or not parsed.hostname:
            raise LiveAcquisitionReplayError("P219_LARW_REDIRECT_HTTPS_REQUIRED")
        _assert_public_host(self.provider, parsed.hostname)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class PinnedHTTPSSourceTransport:
    """Minimal HTTPS transport restricted to provider-derived immutable URLs."""

    def __init__(self, *, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> None:
        if isinstance(timeout_seconds, bool) or int(timeout_seconds) <= 0:
            raise LiveAcquisitionReplayError("P219_LARW_TIMEOUT_INVALID")
        self.timeout_seconds = int(timeout_seconds)

    def fetch(self, spec: AcquisitionSourceSpec) -> FetchResponse:
        item = spec.validated()
        url = item.pinned_url()
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise LiveAcquisitionReplayError("P219_LARW_HTTPS_REQUIRED")
        _assert_public_host(item.repository.provider, parsed.hostname)
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            _StrictRedirectHandler(item.repository.provider),
        )
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "*/*",
                "Accept-Encoding": "identity",
                "User-Agent": "HHS-P219-Live-Acquisition-Replay-Worker/1",
            },
            method="GET",
        )
        try:
            with opener.open(request, timeout=self.timeout_seconds) as response:
                final_url = response.geturl()
                final = urllib.parse.urlparse(final_url)
                if final.scheme != "https" or not final.hostname:
                    raise LiveAcquisitionReplayError("P219_LARW_FINAL_URL_HTTPS_REQUIRED")
                _assert_public_host(item.repository.provider, final.hostname)
                status = int(getattr(response, "status", 200))
                if status != 200:
                    raise LiveAcquisitionReplayError("P219_LARW_HTTP_STATUS_REJECTED")
                body = response.read(item.expected_byte_length + 1)
                if len(body) > item.expected_byte_length:
                    raise LiveAcquisitionReplayError("P219_LARW_RESPONSE_EXCEEDS_EXPECTED_LENGTH")
                headers = tuple((key, value) for key, value in response.headers.items())
        except LiveAcquisitionReplayError:
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise LiveAcquisitionReplayError("P219_LARW_NETWORK_FETCH_FAILED") from exc
        return FetchResponse(url, final_url, status, body, headers)


@dataclass(frozen=True)
class ExternalProjectionEvidence:
    model_repository: OpenSourceRepositoryDescriptor
    pivot_text: str
    source_language: str
    pivot_language: str
    source_modality: str
    output_bytes: bytes
    vector_identity_bytes: bytes
    similarity_numerator: int
    similarity_denominator: int
    semantic_labels: tuple[str, ...] = ()
    translation_chain: tuple[str, ...] = ()

    def validated(self) -> "ExternalProjectionEvidence":
        model = self.model_repository.validated()
        output = bytes(self.output_bytes)
        vector = bytes(self.vector_identity_bytes)
        if not output or len(output) > MAX_PROJECTION_OUTPUT_BYTES:
            raise LiveAcquisitionReplayError("P219_LARW_MODEL_OUTPUT_BOUND")
        if not vector or len(vector) > MAX_VECTOR_IDENTITY_BYTES:
            raise LiveAcquisitionReplayError("P219_LARW_VECTOR_IDENTITY_BOUND")
        if isinstance(self.similarity_numerator, bool) or isinstance(self.similarity_denominator, bool):
            raise LiveAcquisitionReplayError("P219_LARW_SIMILARITY_INTEGER_REQUIRED")
        try:
            similarity = Fraction(int(self.similarity_numerator), int(self.similarity_denominator))
        except (ValueError, ZeroDivisionError) as exc:
            raise LiveAcquisitionReplayError("P219_LARW_SIMILARITY_INVALID") from exc
        if similarity < 0 or similarity > 1:
            raise LiveAcquisitionReplayError("P219_LARW_SIMILARITY_RANGE")
        pivot = " ".join(str(self.pivot_text).split())
        if not pivot:
            raise LiveAcquisitionReplayError("P219_LARW_PIVOT_TEXT_REQUIRED")
        source_language = str(self.source_language).strip().casefold()
        pivot_language = str(self.pivot_language).strip().casefold()
        source_modality = str(self.source_modality).strip().upper()
        if not source_language or not pivot_language or not source_modality:
            raise LiveAcquisitionReplayError("P219_LARW_PROJECTION_METADATA_REQUIRED")
        labels = tuple(dict.fromkeys(str(x).strip() for x in self.semantic_labels if str(x).strip()))
        chain = tuple(dict.fromkeys(str(x).strip() for x in self.translation_chain if str(x).strip()))
        return ExternalProjectionEvidence(
            model_repository=model,
            pivot_text=pivot,
            source_language=source_language,
            pivot_language=pivot_language,
            source_modality=source_modality,
            output_bytes=output,
            vector_identity_bytes=vector,
            similarity_numerator=similarity.numerator,
            similarity_denominator=similarity.denominator,
            semantic_labels=labels,
            translation_chain=chain,
        )

    def to_exact_projection(self) -> ExactSemanticProjection:
        item = self.validated()
        return ExactSemanticProjection(
            model_repository=item.model_repository,
            pivot_text=item.pivot_text,
            source_language=item.source_language,
            pivot_language=item.pivot_language,
            source_modality=item.source_modality,
            model_output_sha256=sha256(item.output_bytes).hexdigest(),
            vector_identity_sha256=sha256(item.vector_identity_bytes).hexdigest(),
            similarity_numerator=item.similarity_numerator,
            similarity_denominator=item.similarity_denominator,
            semantic_labels=item.semantic_labels,
            translation_chain=item.translation_chain,
            candidate_only=True,
        ).validated()

    def receipt_body(self) -> dict[str, Any]:
        item = self.validated()
        exact = item.to_exact_projection()
        body = {
            "schema": PROJECTION_SCHEMA,
            "model_repository": item.model_repository.receipt_body(),
            "pivot_text": item.pivot_text,
            "source_language": item.source_language,
            "pivot_language": item.pivot_language,
            "source_modality": item.source_modality,
            "model_output_sha256": exact.model_output_sha256,
            "model_output_byte_length": len(item.output_bytes),
            "vector_identity_sha256": exact.vector_identity_sha256,
            "vector_identity_byte_length": len(item.vector_identity_bytes),
            "similarity": _fraction_record(
                Fraction(item.similarity_numerator, item.similarity_denominator)
            ),
            "semantic_labels": list(item.semantic_labels),
            "translation_chain": list(item.translation_chain),
            "external_model_execution": True,
            "candidate_only": True,
            "truth_promotion": False,
            "canonical_learning_commit_invoked": False,
            "vm81_commit_invoked": False,
            "canonical_hash72_minted": False,
            "canonical_hash216_minted": False,
        }
        body["external_projection_receipt_hash72"] = hash72_digest(
            {"domain": PROJECTION_SCHEMA}, body
        )
        return body


class ExternalProjector(Protocol):
    def project(self, artifact: RepositoryArtifact) -> Sequence[ExternalProjectionEvidence]: ...


class _StaticProjectionProvider:
    def __init__(self, evidence: Sequence[ExternalProjectionEvidence]) -> None:
        self._projections = tuple(item.to_exact_projection() for item in evidence)

    def project(self, artifact: RepositoryArtifact) -> Sequence[ExactSemanticProjection]:
        del artifact
        return self._projections


class LiveAcquisitionReplayWorker:
    """Acquire/verify/project/replay wrapper around the authoritative ingress."""

    def __init__(
        self,
        relation_db: Mapping[str, WordRelationEntry],
        *,
        transport: SourceTransport | None = None,
        pass165: MultimodalLearningService | None = None,
        minimum_similarity: Fraction = Fraction(1, 2),
    ) -> None:
        if not relation_db:
            raise LiveAcquisitionReplayError("P219_LARW_WORDNET_REQUIRED")
        if minimum_similarity < 0 or minimum_similarity > 1:
            raise LiveAcquisitionReplayError("P219_LARW_MINIMUM_SIMILARITY_RANGE")
        self.relation_db = relation_db
        self.transport = transport or PinnedHTTPSSourceTransport()
        self.pass165 = pass165
        self.minimum_similarity = minimum_similarity

    @staticmethod
    def _verify_source_bytes(spec: AcquisitionSourceSpec, source_bytes: bytes) -> RepositoryArtifact:
        item = spec.validated()
        raw = bytes(source_bytes)
        if len(raw) != item.expected_byte_length:
            raise LiveAcquisitionReplayError("P219_LARW_SOURCE_LENGTH_MISMATCH")
        if sha256(raw).hexdigest() != item.expected_sha256:
            raise LiveAcquisitionReplayError("P219_LARW_SOURCE_DIGEST_MISMATCH")
        return RepositoryArtifact(
            repository=item.repository,
            path=item.artifact_path,
            content=raw,
            declared_media_type=item.declared_media_type,
            source_language=item.source_language,
        ).validated()

    @staticmethod
    def _validate_evidence(
        evidence: Sequence[ExternalProjectionEvidence],
    ) -> tuple[ExternalProjectionEvidence, ...]:
        if len(evidence) > MAX_PROJECTIONS:
            raise LiveAcquisitionReplayError("P219_LARW_PROJECTION_BOUND")
        return tuple(item.validated() for item in evidence)

    @staticmethod
    def _replay_closure_components(
        source_sha256: str,
        projection_receipts: Sequence[Mapping[str, Any]],
        ingress_record: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "source_sha256": source_sha256,
            "projection_receipts": list(projection_receipts),
            "ingress_record": dict(ingress_record),
        }

    def _compose_report(
        self,
        *,
        mode: str,
        spec: AcquisitionSourceSpec,
        artifact: RepositoryArtifact,
        evidence: Sequence[ExternalProjectionEvidence],
        fetch_response: FetchResponse | None,
    ) -> dict[str, Any]:
        item = spec.validated()
        checked_evidence = self._validate_evidence(evidence)
        ingress = TranslationInvariantMultimodalIngress(
            self.relation_db,
            _StaticProjectionProvider(checked_evidence),
            pass165=self.pass165,
            minimum_similarity=self.minimum_similarity,
        )
        ingress_record = ingress.analyze_artifact(artifact)
        source_receipt = {
            "schema": SOURCE_SCHEMA,
            **item.receipt_body(),
            "actual_sha256": sha256(artifact.content).hexdigest(),
            "actual_byte_length": len(artifact.content),
            "mode": mode,
            "network_fetch_performed": fetch_response is not None,
            "http_status": fetch_response.status if fetch_response else None,
            "final_url": fetch_response.final_url if fetch_response else item.pinned_url(),
            "response_headers": (
                [list(pair) for pair in fetch_response.normalized_headers()]
                if fetch_response else []
            ),
        }
        source_receipt["source_receipt_hash72"] = hash72_digest(
            {"domain": SOURCE_SCHEMA}, source_receipt
        )
        projection_receipts = [entry.receipt_body() for entry in checked_evidence]
        replay_closure_hash72 = hash72_digest(
            {"domain": REPLAY_CLOSURE_SCHEMA},
            self._replay_closure_components(
                source_receipt["actual_sha256"], projection_receipts, ingress_record
            ),
        )
        body = {
            "schema": REPORT_SCHEMA,
            "version": VERSION,
            "mode": mode,
            "source": source_receipt,
            "external_projection_receipts": projection_receipts,
            "ingress_record": ingress_record,
            "replay_closure_hash72": replay_closure_hash72,
            "source_identity_verified_before_analysis": True,
            "replay_requires_same_source_and_projection_bytes": True,
            "candidate_only": True,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "vm81_commit_invoked": False,
            "canonical_hash72_minted": False,
            "canonical_hash216_minted": False,
            "permanent_prune_authorized": False,
        }
        body["report_hash72"] = hash72_digest({"domain": REPORT_SCHEMA}, body)
        body["report_sha256"] = sha256(_canonical_bytes(body)).hexdigest()
        return body

    def execute_live(
        self,
        spec: AcquisitionSourceSpec,
        projector: ExternalProjector,
    ) -> dict[str, Any]:
        item = spec.validated()
        fetched = self.transport.fetch(item)
        if fetched.requested_url != item.pinned_url():
            raise LiveAcquisitionReplayError("P219_LARW_REQUEST_URL_DIVERGENCE")
        if fetched.status != 200:
            raise LiveAcquisitionReplayError("P219_LARW_HTTP_STATUS_REJECTED")
        final = urllib.parse.urlparse(fetched.final_url)
        if (
            final.scheme != "https"
            or not final.hostname
            or not _provider_host_allowed(item.repository.provider, final.hostname)
        ):
            raise LiveAcquisitionReplayError("P219_LARW_FINAL_URL_PROVIDER_MISMATCH")
        artifact = self._verify_source_bytes(item, fetched.body)
        evidence = projector.project(artifact)
        return self._compose_report(
            mode="LIVE_ACQUISITION",
            spec=item,
            artifact=artifact,
            evidence=evidence,
            fetch_response=fetched,
        )

    def replay_archived(
        self,
        spec: AcquisitionSourceSpec,
        *,
        source_bytes: bytes,
        projection_evidence: Sequence[ExternalProjectionEvidence],
        expected_replay_closure_hash72: str | None = None,
    ) -> dict[str, Any]:
        item = spec.validated()
        artifact = self._verify_source_bytes(item, source_bytes)
        report = self._compose_report(
            mode="ARCHIVED_REPLAY",
            spec=item,
            artifact=artifact,
            evidence=projection_evidence,
            fetch_response=None,
        )
        if expected_replay_closure_hash72 is not None:
            expected = str(expected_replay_closure_hash72).strip()
            if expected != report["replay_closure_hash72"]:
                raise LiveAcquisitionReplayError("P219_LARW_REPLAY_CLOSURE_MISMATCH")
            report["verified_expected_replay_closure_hash72"] = expected
        report["network_fetch_performed"] = False
        report["external_model_execution_performed"] = False
        return report

    @staticmethod
    def replay_closure_hash72(report: Mapping[str, Any]) -> str:
        source = report.get("source")
        projections = report.get("external_projection_receipts")
        ingress = report.get("ingress_record")
        if (
            not isinstance(source, Mapping)
            or not isinstance(projections, list)
            or not isinstance(ingress, Mapping)
        ):
            raise LiveAcquisitionReplayError("P219_LARW_REPORT_SHAPE_INVALID")
        source_sha = str(source.get("actual_sha256") or "")
        if SHA256_HEX.fullmatch(source_sha) is None:
            raise LiveAcquisitionReplayError("P219_LARW_REPORT_SOURCE_SHA_INVALID")
        return hash72_digest(
            {"domain": REPLAY_CLOSURE_SCHEMA},
            LiveAcquisitionReplayWorker._replay_closure_components(
                source_sha, projections, ingress
            ),
        )


__all__ = [
    "AcquisitionSourceSpec",
    "ExternalProjectionEvidence",
    "ExternalProjector",
    "FetchResponse",
    "LiveAcquisitionReplayError",
    "LiveAcquisitionReplayWorker",
    "PinnedHTTPSSourceTransport",
    "REPORT_SCHEMA",
    "SOURCE_SCHEMA",
    "SourceTransport",
    "VERSION",
]

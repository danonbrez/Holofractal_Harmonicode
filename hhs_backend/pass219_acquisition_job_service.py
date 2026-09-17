"""Persistent application-service jobs for Pass 219 acquisition/replay.

This module is an application boundary above the canonical runtime.  It owns a
small SQLite job ledger plus replay bundles, delegates acquisition and replay to
the already validated live acquisition worker, and never grants VM81/Hash72/
Hash216 authority.
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from time import time_ns
from typing import Any, Mapping, Sequence
from uuid import uuid4
import json
import os
import sqlite3

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.hhs_pass219_live_acquisition_replay_worker_v1 import (
    AcquisitionSourceSpec,
    ExternalProjectionEvidence,
    ExternalProjector,
    FetchResponse,
    LiveAcquisitionReplayError,
    LiveAcquisitionReplayWorker,
    PinnedHTTPSSourceTransport,
    SourceTransport,
)
from hhs_runtime.hhs_pass219_translation_invariant_multimodal_ingress_v1 import (
    OpenSourceRepositoryDescriptor,
    RepositoryArtifact,
)
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import (
    WordRelationEntry,
    default_wordnet_paths,
    load_wordnet_relations,
)

VERSION = "HHS-P219-ACQUISITION-JOB-SERVICE-V1"
JOB_SCHEMA = "HHS-P219-ACQUISITION-JOB-V1"
JOB_RECEIPT_SCHEMA = "HHS-P219-ACQUISITION-JOB-RECEIPT-V1"
BUNDLE_SCHEMA = "HHS-P219-ACQUISITION-REPLAY-BUNDLE-V1"
MAX_HISTORY = 200


class AcquisitionJobServiceError(RuntimeError):
    pass


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)


def _mapping(value: Any, code: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AcquisitionJobServiceError(code)
    return value


def _required(value: Any, code: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise AcquisitionJobServiceError(code)
    return text


def _decode_b64(value: Any, code: str) -> bytes:
    try:
        raw = b64decode(_required(value, code), validate=True)
    except Exception as exc:
        raise AcquisitionJobServiceError(code) from exc
    if not raw:
        raise AcquisitionJobServiceError(code)
    return raw


@dataclass
class _CaptureTransport:
    inner: SourceTransport
    response: FetchResponse | None = None

    def fetch(self, spec: AcquisitionSourceSpec) -> FetchResponse:
        self.response = self.inner.fetch(spec)
        return self.response


class _SourceOnlyProjector:
    def project(self, artifact: RepositoryArtifact) -> Sequence[ExternalProjectionEvidence]:
        del artifact
        return ()


class _EvidenceProjector:
    def __init__(self, evidence: Sequence[ExternalProjectionEvidence]) -> None:
        self.evidence = tuple(evidence)

    def project(self, artifact: RepositoryArtifact) -> Sequence[ExternalProjectionEvidence]:
        del artifact
        return self.evidence


PROJECTORS: tuple[dict[str, Any], ...] = (
    {
        "projector_id": "SOURCE_ONLY_V1",
        "classification": "VERIFIED_ACQUISITION_WITHOUT_SEMANTIC_PROJECTION",
        "requires_projection_evidence": False,
        "candidate_only": True,
        "description": "Acquire and verify immutable source bytes; semantic projection remains HOLD.",
    },
    {
        "projector_id": "EXTERNAL_EVIDENCE_V1",
        "classification": "SEALED_EXTERNAL_PROJECTION_EVIDENCE",
        "requires_projection_evidence": True,
        "candidate_only": True,
        "description": "Use caller-supplied external projection bytes after exact validation and sealing.",
    },
)


class AcquisitionJobService:
    """Durable synchronous job surface with network-free replay."""

    def __init__(
        self,
        state_root: str | Path,
        *,
        relation_db: Mapping[str, WordRelationEntry] | None = None,
        transport: SourceTransport | None = None,
    ) -> None:
        self.root = Path(state_root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.bundle_root = self.root / "bundles"
        self.bundle_root.mkdir(parents=True, exist_ok=True)
        self.db_path = self.root / "jobs.sqlite3"
        self.transport = transport or PinnedHTTPSSourceTransport()
        self.relation_db = dict(relation_db or load_wordnet_relations(default_wordnet_paths()))
        if not self.relation_db:
            raise AcquisitionJobServiceError("P219_AJS_WORDNET_REQUIRED")
        self._lock = RLock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10.0)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._lock, self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS acquisition_jobs (
                    job_id TEXT PRIMARY KEY,
                    created_ns INTEGER NOT NULL,
                    updated_ns INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    projector_id TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    result_json TEXT,
                    error_json TEXT,
                    receipt_hash72 TEXT
                )
                """
            )
            db.execute("CREATE INDEX IF NOT EXISTS acquisition_jobs_updated_idx ON acquisition_jobs(updated_ns DESC)")

    @staticmethod
    def projectors() -> dict[str, Any]:
        return {
            "schema": "HHS-P219-APPROVED-PROJECTOR-REGISTRY-V1",
            "version": VERSION,
            "projectors": list(PROJECTORS),
            "model_execution_is_external_to_canonical_kernel": True,
            "candidate_only": True,
        }

    @staticmethod
    def _repository(raw: Mapping[str, Any]) -> OpenSourceRepositoryDescriptor:
        return OpenSourceRepositoryDescriptor(
            provider=_required(raw.get("provider"), "P219_AJS_PROVIDER_REQUIRED"),
            repo_id=_required(raw.get("repo_id"), "P219_AJS_REPO_ID_REQUIRED"),
            revision=_required(raw.get("revision"), "P219_AJS_REVISION_REQUIRED"),
            license_id=_required(raw.get("license_id"), "P219_AJS_LICENSE_REQUIRED"),
            repo_kind=str(raw.get("repo_kind") or "CODE"),
            source_url=_required(raw.get("source_url"), "P219_AJS_SOURCE_URL_REQUIRED"),
            modalities=tuple(str(x) for x in raw.get("modalities", ()) if str(x).strip()),
        ).validated()

    @classmethod
    def _source_spec(cls, raw: Mapping[str, Any]) -> AcquisitionSourceSpec:
        repository = cls._repository(_mapping(raw.get("repository"), "P219_AJS_REPOSITORY_REQUIRED"))
        return AcquisitionSourceSpec(
            repository=repository,
            artifact_path=_required(raw.get("artifact_path"), "P219_AJS_ARTIFACT_PATH_REQUIRED"),
            expected_sha256=_required(raw.get("expected_sha256"), "P219_AJS_EXPECTED_SHA_REQUIRED"),
            expected_byte_length=int(raw.get("expected_byte_length") or 0),
            declared_media_type=(str(raw.get("declared_media_type")).strip() if raw.get("declared_media_type") else None),
            source_language=(str(raw.get("source_language")).strip() if raw.get("source_language") else None),
        ).validated()

    @classmethod
    def _projection_evidence(cls, rows: Any) -> tuple[ExternalProjectionEvidence, ...]:
        if rows is None:
            return ()
        if not isinstance(rows, list):
            raise AcquisitionJobServiceError("P219_AJS_PROJECTION_EVIDENCE_LIST_REQUIRED")
        result: list[ExternalProjectionEvidence] = []
        for raw_value in rows:
            raw = _mapping(raw_value, "P219_AJS_PROJECTION_EVIDENCE_INVALID")
            model = cls._repository(_mapping(raw.get("model_repository"), "P219_AJS_MODEL_REPOSITORY_REQUIRED"))
            similarity = _mapping(raw.get("similarity"), "P219_AJS_SIMILARITY_REQUIRED")
            result.append(ExternalProjectionEvidence(
                model_repository=model,
                pivot_text=_required(raw.get("pivot_text"), "P219_AJS_PIVOT_TEXT_REQUIRED"),
                source_language=_required(raw.get("source_language"), "P219_AJS_PROJECTION_SOURCE_LANGUAGE_REQUIRED"),
                pivot_language=_required(raw.get("pivot_language"), "P219_AJS_PIVOT_LANGUAGE_REQUIRED"),
                source_modality=_required(raw.get("source_modality"), "P219_AJS_SOURCE_MODALITY_REQUIRED"),
                output_bytes=_decode_b64(raw.get("output_b64"), "P219_AJS_OUTPUT_B64_INVALID"),
                vector_identity_bytes=_decode_b64(raw.get("vector_identity_b64"), "P219_AJS_VECTOR_B64_INVALID"),
                similarity_numerator=int(similarity.get("numerator")),
                similarity_denominator=int(similarity.get("denominator")),
                semantic_labels=tuple(str(x) for x in raw.get("semantic_labels", ()) if str(x).strip()),
                translation_chain=tuple(str(x) for x in raw.get("translation_chain", ()) if str(x).strip()),
            ).validated())
        return tuple(result)

    @staticmethod
    def _evidence_to_bundle(evidence: ExternalProjectionEvidence) -> dict[str, Any]:
        item = evidence.validated()
        return {
            "model_repository": item.model_repository.receipt_body(),
            "pivot_text": item.pivot_text,
            "source_language": item.source_language,
            "pivot_language": item.pivot_language,
            "source_modality": item.source_modality,
            "output_b64": b64encode(item.output_bytes).decode("ascii"),
            "vector_identity_b64": b64encode(item.vector_identity_bytes).decode("ascii"),
            "similarity": {"numerator": item.similarity_numerator, "denominator": item.similarity_denominator},
            "semantic_labels": list(item.semantic_labels),
            "translation_chain": list(item.translation_chain),
        }

    def _projector(self, projector_id: str, evidence: Sequence[ExternalProjectionEvidence]) -> ExternalProjector:
        projector = projector_id.strip().upper()
        if projector == "SOURCE_ONLY_V1":
            if evidence:
                raise AcquisitionJobServiceError("P219_AJS_SOURCE_ONLY_EVIDENCE_FORBIDDEN")
            return _SourceOnlyProjector()
        if projector == "EXTERNAL_EVIDENCE_V1":
            if not evidence:
                raise AcquisitionJobServiceError("P219_AJS_EXTERNAL_EVIDENCE_REQUIRED")
            return _EvidenceProjector(evidence)
        raise AcquisitionJobServiceError("P219_AJS_PROJECTOR_NOT_APPROVED")

    def _insert(self, job_id: str, projector_id: str, request: Mapping[str, Any]) -> None:
        now = time_ns()
        with self._lock, self._connect() as db:
            db.execute(
                "INSERT INTO acquisition_jobs(job_id,created_ns,updated_ns,status,projector_id,request_json) VALUES(?,?,?,?,?,?)",
                (job_id, now, now, "QUEUED", projector_id, _canonical_json(request)),
            )

    def _update(self, job_id: str, *, status: str, result: Any = None, error: Any = None, receipt_hash72: str | None = None) -> None:
        with self._lock, self._connect() as db:
            db.execute(
                "UPDATE acquisition_jobs SET updated_ns=?, status=?, result_json=?, error_json=?, receipt_hash72=? WHERE job_id=?",
                (
                    time_ns(), status,
                    _canonical_json(result) if result is not None else None,
                    _canonical_json(error) if error is not None else None,
                    receipt_hash72,
                    job_id,
                ),
            )

    def _write_bundle(self, job_id: str, payload: Mapping[str, Any]) -> None:
        destination = self.bundle_root / f"{job_id}.json"
        temporary = destination.with_suffix(".json.tmp")
        temporary.write_text(_canonical_json(payload), encoding="utf-8")
        os.replace(temporary, destination)

    def _read_bundle(self, job_id: str) -> Mapping[str, Any]:
        path = self.bundle_root / f"{job_id}.json"
        if not path.is_file():
            raise AcquisitionJobServiceError("P219_AJS_REPLAY_BUNDLE_MISSING")
        return _mapping(json.loads(path.read_text("utf-8")), "P219_AJS_REPLAY_BUNDLE_INVALID")

    @staticmethod
    def _receipt(job_id: str, result: Mapping[str, Any]) -> dict[str, Any]:
        body = {
            "schema": JOB_RECEIPT_SCHEMA,
            "version": VERSION,
            "job_id": job_id,
            "report_hash72": result.get("report_hash72"),
            "report_sha256": result.get("report_sha256"),
            "replay_closure_hash72": result.get("replay_closure_hash72"),
            "classification": (result.get("ingress_record") or {}).get("classification"),
            "candidate_only": True,
            "canonical_authority_minted": False,
        }
        body["job_receipt_hash72"] = hash72_digest({"domain": JOB_RECEIPT_SCHEMA}, body)
        return body

    def submit(self, request: Mapping[str, Any]) -> dict[str, Any]:
        raw = dict(request)
        projector_id = str(raw.get("projector_id") or "SOURCE_ONLY_V1").strip().upper()
        spec = self._source_spec(_mapping(raw.get("source"), "P219_AJS_SOURCE_REQUIRED"))
        evidence = self._projection_evidence(raw.get("projection_evidence"))
        projector = self._projector(projector_id, evidence)
        job_id = uuid4().hex
        normalized_request = {
            "schema": "HHS-P219-ACQUISITION-JOB-REQUEST-V1",
            "projector_id": projector_id,
            "source": spec.receipt_body(),
            "projection_evidence_count": len(evidence),
            "candidate_only": True,
        }
        self._insert(job_id, projector_id, normalized_request)
        self._update(job_id, status="RUNNING")
        capture = _CaptureTransport(self.transport)
        try:
            worker = LiveAcquisitionReplayWorker(self.relation_db, transport=capture)
            result = worker.execute_live(spec, projector)
            if capture.response is None:
                raise AcquisitionJobServiceError("P219_AJS_SOURCE_CAPTURE_MISSING")
            receipt = self._receipt(job_id, result)
            bundle = {
                "schema": BUNDLE_SCHEMA,
                "version": VERSION,
                "job_id": job_id,
                "source_spec": spec.receipt_body(),
                "source_b64": b64encode(capture.response.body).decode("ascii"),
                "projection_evidence": [self._evidence_to_bundle(item) for item in evidence],
                "expected_replay_closure_hash72": result["replay_closure_hash72"],
                "candidate_only": True,
            }
            self._write_bundle(job_id, bundle)
            persisted = {"report": result, "receipt": receipt, "replay_bundle_persisted": True}
            self._update(job_id, status="COMPLETED", result=persisted, receipt_hash72=receipt["job_receipt_hash72"])
        except Exception as exc:
            classification = str(exc) or type(exc).__name__
            self._update(job_id, status="FAILED", error={"classification": classification, "type": type(exc).__name__})
        return self.get(job_id)

    def replay(self, job_id: str) -> dict[str, Any]:
        job = self.get(job_id)
        if job["status"] != "COMPLETED":
            raise AcquisitionJobServiceError("P219_AJS_REPLAY_REQUIRES_COMPLETED_JOB")
        bundle = self._read_bundle(job_id)
        source_spec_raw = _mapping(bundle.get("source_spec"), "P219_AJS_BUNDLE_SOURCE_SPEC_REQUIRED")
        # receipt_body stores repository and source fields in the same shape expected here.
        spec = self._source_spec(source_spec_raw)
        evidence = self._projection_evidence(bundle.get("projection_evidence"))
        worker = LiveAcquisitionReplayWorker(self.relation_db, transport=self.transport)
        replay = worker.replay_archived(
            spec,
            source_bytes=_decode_b64(bundle.get("source_b64"), "P219_AJS_BUNDLE_SOURCE_B64_INVALID"),
            projection_evidence=evidence,
            expected_replay_closure_hash72=_required(bundle.get("expected_replay_closure_hash72"), "P219_AJS_REPLAY_CLOSURE_REQUIRED"),
        )
        return {
            "schema": "HHS-P219-ACQUISITION-JOB-REPLAY-V1",
            "job_id": job_id,
            "status": "REPLAY_VERIFIED",
            "replay": replay,
            "network_fetch_performed": False,
            "external_model_execution_performed": False,
            "candidate_only": True,
        }

    def get(self, job_id: str) -> dict[str, Any]:
        with self._lock, self._connect() as db:
            row = db.execute("SELECT * FROM acquisition_jobs WHERE job_id=?", (str(job_id),)).fetchone()
        if row is None:
            raise AcquisitionJobServiceError("P219_AJS_JOB_NOT_FOUND")
        return self._row(row)

    def list(self, limit: int = 25) -> dict[str, Any]:
        bounded = max(1, min(int(limit), MAX_HISTORY))
        with self._lock, self._connect() as db:
            rows = db.execute("SELECT * FROM acquisition_jobs ORDER BY updated_ns DESC LIMIT ?", (bounded,)).fetchall()
        return {
            "schema": "HHS-P219-ACQUISITION-JOB-HISTORY-V1",
            "version": VERSION,
            "jobs": [self._row(row) for row in rows],
            "count": len(rows),
            "candidate_only": True,
        }

    def receipt(self, job_id: str) -> dict[str, Any]:
        job = self.get(job_id)
        result = job.get("result") or {}
        receipt = result.get("receipt") if isinstance(result, Mapping) else None
        if not isinstance(receipt, Mapping):
            raise AcquisitionJobServiceError("P219_AJS_JOB_RECEIPT_UNAVAILABLE")
        return dict(receipt)

    @staticmethod
    def _row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": JOB_SCHEMA,
            "version": VERSION,
            "job_id": row["job_id"],
            "created_ns": row["created_ns"],
            "updated_ns": row["updated_ns"],
            "status": row["status"],
            "projector_id": row["projector_id"],
            "request": json.loads(row["request_json"]),
            "result": json.loads(row["result_json"]) if row["result_json"] else None,
            "error": json.loads(row["error_json"]) if row["error_json"] else None,
            "receipt_hash72": row["receipt_hash72"],
            "candidate_only": True,
            "canonical_authority_minted": False,
        }


__all__ = [
    "AcquisitionJobService",
    "AcquisitionJobServiceError",
    "BUNDLE_SCHEMA",
    "JOB_RECEIPT_SCHEMA",
    "JOB_SCHEMA",
    "PROJECTORS",
    "VERSION",
]

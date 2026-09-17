"""Server-side Pass 219 approved projector execution bridge.

The web/API process never imports PyTorch or sentence-transformers.  Verified
source bytes cross into an isolated projector subprocess only after the existing
live acquisition worker has proved the source length/SHA/immutable URL contract.
The generated projection evidence is then persisted through the already
validated EXTERNAL_EVIDENCE_V1 acquisition path using the exact captured source
response, so persistence performs no second network fetch and offline replay
remains model-free.
"""
from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
import json
import os
import subprocess
import sys

from hhs_backend.pass219_acquisition_job_service import AcquisitionJobService
from hhs_runtime.hhs_pass219_live_acquisition_replay_worker_v1 import (
    AcquisitionSourceSpec,
    ExternalProjectionEvidence,
    FetchResponse,
    LiveAcquisitionReplayWorker,
    SourceTransport,
)
from hhs_runtime.hhs_pass219_translation_invariant_multimodal_ingress_v1 import RepositoryArtifact

VERSION = "HHS-P219-SERVER-PROJECTOR-EXECUTION-V1"
SCHEMA = "HHS-P219-SERVER-PROJECTOR-EXECUTION-RESULT-V1"
RUNTIME_SCHEMA = "HHS-P219-SERVER-PROJECTOR-RUNTIME-STATUS-V1"
DEFAULT_PROJECTOR_PYTHON = "/opt/hhs/pass219-projector-venv/bin/python"
DEFAULT_TIMEOUT_SECONDS = 900
MIN_TIMEOUT_SECONDS = 30
MAX_TIMEOUT_SECONDS = 1800
APPROVED_PROFILE = "MULTILINGUAL_MPNET_TEXT_V1"


class ServerProjectorExecutionError(RuntimeError):
    pass


ProcessRunner = Callable[..., subprocess.CompletedProcess[str]]


def _mapping(value: Any, code: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ServerProjectorExecutionError(code)
    return value


def _required(value: Any, code: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ServerProjectorExecutionError(code)
    return text


def _string_list(value: Any, code: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ServerProjectorExecutionError(code)
    return tuple(dict.fromkeys(str(item).strip() for item in value if str(item).strip()))


def _timeout_seconds() -> int:
    raw = os.environ.get("HHS_P219_PROJECTOR_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ServerProjectorExecutionError("P219_SPE_TIMEOUT_INVALID") from exc
    if value < MIN_TIMEOUT_SECONDS or value > MAX_TIMEOUT_SECONDS:
        raise ServerProjectorExecutionError("P219_SPE_TIMEOUT_RANGE")
    return value


def _projector_python() -> str:
    return os.environ.get("HHS_P219_PROJECTOR_PYTHON") or DEFAULT_PROJECTOR_PYTHON


def server_execution_status() -> dict[str, Any]:
    python_path = _projector_python()
    ready = Path(python_path).is_file() and os.access(python_path, os.X_OK)
    return {
        "schema": RUNTIME_SCHEMA,
        "version": VERSION,
        "projector_python": python_path,
        "runtime_ready": ready,
        "timeout_seconds": _timeout_seconds(),
        "profile_id": APPROVED_PROFILE,
        "subprocess_isolated": True,
        "model_execution_external_to_canonical_kernel": True,
        "candidate_only": True,
        "canonical_authority_minted": False,
    }


@dataclass
class _CaptureTransport:
    inner: SourceTransport
    response: FetchResponse | None = None

    def fetch(self, spec: AcquisitionSourceSpec) -> FetchResponse:
        self.response = self.inner.fetch(spec)
        return self.response


@dataclass(frozen=True)
class _StaticVerifiedTransport:
    response: FetchResponse

    def fetch(self, spec: AcquisitionSourceSpec) -> FetchResponse:
        expected = spec.validated().pinned_url()
        if self.response.requested_url != expected:
            raise ServerProjectorExecutionError("P219_SPE_CAPTURED_SOURCE_URL_MISMATCH")
        return self.response


class _ApprovedSubprocessProjector:
    def __init__(
        self,
        service: AcquisitionJobService,
        execution: Mapping[str, Any],
        *,
        process_runner: ProcessRunner = subprocess.run,
        python_executable: str | None = None,
    ) -> None:
        self.service = service
        self.profile_id = _required(execution.get("profile_id"), "P219_SPE_PROFILE_REQUIRED").upper()
        if self.profile_id != APPROVED_PROFILE:
            raise ServerProjectorExecutionError("P219_SPE_PROFILE_NOT_PRODUCTION_APPROVED")
        self.pivot_text = " ".join(_required(execution.get("pivot_text"), "P219_SPE_PIVOT_REQUIRED").split())
        self.pivot_language = str(execution.get("pivot_language") or "en").strip().casefold()
        if not self.pivot_language:
            raise ServerProjectorExecutionError("P219_SPE_PIVOT_LANGUAGE_REQUIRED")
        self.semantic_labels = _string_list(execution.get("semantic_labels"), "P219_SPE_SEMANTIC_LABELS_LIST_REQUIRED")
        self.translation_chain = _string_list(execution.get("translation_chain"), "P219_SPE_TRANSLATION_CHAIN_LIST_REQUIRED")
        self.process_runner = process_runner
        self.python_executable = python_executable or _projector_python()
        self.timeout_seconds = _timeout_seconds()
        self.raw_evidence: dict[str, Any] | None = None
        self.evidence: tuple[ExternalProjectionEvidence, ...] = ()

    @staticmethod
    def _classification(stderr: str) -> str:
        for line in reversed(str(stderr).splitlines()):
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, Mapping) and payload.get("classification"):
                return str(payload["classification"])
        return "P219_SPE_PROJECTOR_PROCESS_FAILED"

    def project(self, artifact: RepositoryArtifact) -> Sequence[ExternalProjectionEvidence]:
        item = artifact.validated()
        if not item.source_language:
            raise ServerProjectorExecutionError("P219_SPE_SOURCE_LANGUAGE_REQUIRED")
        if not item.declared_media_type:
            raise ServerProjectorExecutionError("P219_SPE_SOURCE_MODALITY_REQUIRED")
        if self.process_runner is subprocess.run:
            path = Path(self.python_executable)
            if not path.is_file() or not os.access(path, os.X_OK):
                raise ServerProjectorExecutionError("P219_SPE_PROJECTOR_RUNTIME_UNAVAILABLE")

        request = {
            "profile_id": self.profile_id,
            "source_b64": b64encode(item.content).decode("ascii"),
            "source_sha256": sha256(item.content).hexdigest(),
            "source_language": item.source_language,
            "source_modality": item.declared_media_type,
            "pivot_text": self.pivot_text,
            "pivot_language": self.pivot_language,
            "semantic_labels": list(self.semantic_labels),
            "translation_chain": list(self.translation_chain),
        }
        repository_root = Path(os.environ.get("HHS_REPOSITORY_ROOT") or Path(__file__).resolve().parents[1]).resolve()
        environment = dict(os.environ)
        inherited_pythonpath = environment.get("PYTHONPATH", "")
        environment["PYTHONPATH"] = str(repository_root) + (os.pathsep + inherited_pythonpath if inherited_pythonpath else "")
        environment.setdefault("HF_HOME", "/var/lib/hhs/models/huggingface")
        environment.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
        environment.setdefault("TOKENIZERS_PARALLELISM", "false")
        environment.setdefault("OMP_NUM_THREADS", "1")
        environment.setdefault("MKL_NUM_THREADS", "1")
        device = environment.get("HHS_P219_PROJECTOR_DEVICE", "cpu").strip().lower()
        if device not in {"cpu", "cuda", "mps"}:
            raise ServerProjectorExecutionError("P219_SPE_DEVICE_INVALID")
        command = [
            self.python_executable,
            "-m",
            "hhs_runtime.hhs_pass219_approved_projector_execution_v1",
            "--input",
            "-",
            "--device",
            device,
        ]
        try:
            completed = self.process_runner(
                command,
                input=json.dumps(request, sort_keys=True, separators=(",", ":")),
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                cwd=str(repository_root),
                env=environment,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ServerProjectorExecutionError("P219_SPE_PROJECTOR_TIMEOUT") from exc
        except OSError as exc:
            raise ServerProjectorExecutionError("P219_SPE_PROJECTOR_PROCESS_START_FAILED") from exc
        if completed.returncode != 0:
            raise ServerProjectorExecutionError(self._classification(completed.stderr))
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise ServerProjectorExecutionError("P219_SPE_PROJECTOR_OUTPUT_JSON_INVALID") from exc
        if not isinstance(payload, Mapping):
            raise ServerProjectorExecutionError("P219_SPE_PROJECTOR_OUTPUT_OBJECT_REQUIRED")
        if payload.get("projector_profile_id") != self.profile_id or payload.get("projector_id") != "EXTERNAL_EVIDENCE_V1":
            raise ServerProjectorExecutionError("P219_SPE_PROJECTOR_OUTPUT_IDENTITY_MISMATCH")
        if payload.get("candidate_only") is not True:
            raise ServerProjectorExecutionError("P219_SPE_PROJECTOR_AUTHORITY_DRIFT")
        parsed = self.service._projection_evidence([dict(payload)])
        if len(parsed) != 1:
            raise ServerProjectorExecutionError("P219_SPE_PROJECTOR_EVIDENCE_CARDINALITY")
        self.raw_evidence = dict(payload)
        self.evidence = parsed
        return parsed


def execute_and_persist_server_projection(
    service: AcquisitionJobService,
    request: Mapping[str, Any],
    *,
    process_runner: ProcessRunner = subprocess.run,
    python_executable: str | None = None,
) -> dict[str, Any]:
    """Verify source, execute approved model once, persist exact evidence, replay-ready."""

    raw = dict(request)
    spec = service._source_spec(_mapping(raw.get("source"), "P219_SPE_SOURCE_REQUIRED"))
    execution = _mapping(raw.get("execution"), "P219_SPE_EXECUTION_REQUIRED")
    capture = _CaptureTransport(service.transport)
    projector = _ApprovedSubprocessProjector(
        service,
        execution,
        process_runner=process_runner,
        python_executable=python_executable,
    )
    worker = LiveAcquisitionReplayWorker(service.relation_db, transport=capture)
    validation_report = worker.execute_live(spec, projector)
    if capture.response is None:
        raise ServerProjectorExecutionError("P219_SPE_CAPTURED_SOURCE_MISSING")
    if projector.raw_evidence is None or len(projector.evidence) != 1:
        raise ServerProjectorExecutionError("P219_SPE_EXECUTION_EVIDENCE_MISSING")

    # Persist through the authoritative job service without another network fetch
    # or another model execution.  The worker will re-verify the exact captured
    # bytes and seal the supplied evidence into the replay bundle.
    persistence = AcquisitionJobService(
        service.root,
        relation_db=service.relation_db,
        transport=_StaticVerifiedTransport(capture.response),
    )
    job = persistence.submit({
        "projector_id": "EXTERNAL_EVIDENCE_V1",
        "source": spec.receipt_body(),
        "projection_evidence": [projector.raw_evidence],
    })
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "status": job["status"],
        "job": job,
        "execution": {
            "profile_id": projector.profile_id,
            "execution_record_sha256": projector.raw_evidence.get("execution_record_sha256"),
            "projector_version": projector.raw_evidence.get("projector_version"),
            "verified_source_sha256": sha256(capture.response.body).hexdigest(),
            "initial_validation_report_hash72": validation_report.get("report_hash72"),
            "network_fetch_count": 1,
            "external_model_execution_count": 1,
            "persistence_network_fetch_count": 0,
            "persistence_external_model_execution_count": 0,
            "subprocess_isolated": True,
        },
        "candidate_only": True,
        "truth_promotion": False,
        "canonical_learning_commit_invoked": False,
        "vm81_commit_invoked": False,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
        "permanent_prune_authorized": False,
    }


__all__ = [
    "APPROVED_PROFILE",
    "DEFAULT_PROJECTOR_PYTHON",
    "RUNTIME_SCHEMA",
    "SCHEMA",
    "ServerProjectorExecutionError",
    "VERSION",
    "execute_and_persist_server_projection",
    "server_execution_status",
]

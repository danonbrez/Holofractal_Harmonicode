from __future__ import annotations

from base64 import b64encode
from hashlib import sha256
import json
import subprocess

import pytest

from hhs_backend.api.pass219_acquisition_routes import router
from hhs_backend.pass219_acquisition_job_service import AcquisitionJobService
from hhs_backend.pass219_server_projector_execution import (
    ServerProjectorExecutionError,
    execute_and_persist_server_projection,
)
from hhs_runtime.hhs_pass219_approved_projector_execution_v1 import TEXT_MODEL, VERSION as PROJECTOR_VERSION
from hhs_runtime.hhs_pass219_live_acquisition_replay_worker_v1 import FetchResponse
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import WordRelationEntry

SOURCE = b"A cat sits on a mat.\n"
SOURCE_SHA = sha256(SOURCE).hexdigest()
REVISION = "a" * 40


def _entry(word: str) -> WordRelationEntry:
    return WordRelationEntry(
        word=word,
        pos=["noun"],
        definitions=[f"definition:{word}"],
        synonyms=[],
        antonyms=[],
        hypernyms=[],
        hyponyms=[],
        entry_hash72=(word[:1] or "x") * 24,
    )


@pytest.fixture()
def relation_db():
    return {"cat": _entry("cat"), "mat": _entry("mat"), "sits": _entry("sits")}


class _Transport:
    def __init__(self, body: bytes = SOURCE):
        self.body = body
        self.calls = 0

    def fetch(self, spec):
        self.calls += 1
        url = spec.pinned_url()
        return FetchResponse(url, url, 200, self.body, (("content-length", str(len(self.body))),))


def _source():
    return {
        "repository": {
            "provider": "GITHUB",
            "repo_id": "huggingface/sentence-transformers",
            "revision": REVISION,
            "license_id": "apache-2.0",
            "repo_kind": "CODE",
            "source_url": "https://github.com/huggingface/sentence-transformers",
            "modalities": ["TEXT"],
        },
        "artifact_path": "README.md",
        "expected_sha256": SOURCE_SHA,
        "expected_byte_length": len(SOURCE),
        "declared_media_type": "TEXT",
        "source_language": "en",
    }


def _request(profile: str = "MULTILINGUAL_MPNET_TEXT_V1"):
    return {
        "source": _source(),
        "execution": {
            "profile_id": profile,
            "pivot_text": "A cat sits on a mat",
            "pivot_language": "en",
            "semantic_labels": ["cat", "mat"],
            "translation_chain": ["en"],
        },
    }


class _Runner:
    def __init__(self, *, returncode: int = 0, classification: str | None = None):
        self.calls = 0
        self.requests = []
        self.returncode = returncode
        self.classification = classification

    def __call__(self, command, **kwargs):
        self.calls += 1
        request = json.loads(kwargs["input"])
        self.requests.append(request)
        if self.returncode:
            stderr = json.dumps({"classification": self.classification or "TEST_PROJECTOR_FAILURE"})
            return subprocess.CompletedProcess(command, self.returncode, stdout="", stderr=stderr)
        output_bytes = b"approved-projector-output"
        vector_bytes = b"source-vector+pivot-vector"
        payload = {
            "model_repository": TEXT_MODEL.receipt_body(),
            "pivot_text": request["pivot_text"],
            "source_language": request["source_language"],
            "pivot_language": request["pivot_language"],
            "source_modality": request["source_modality"],
            "output_b64": b64encode(output_bytes).decode("ascii"),
            "vector_identity_b64": b64encode(vector_bytes).decode("ascii"),
            "similarity": {"numerator": 9, "denominator": 10},
            "semantic_labels": request["semantic_labels"],
            "translation_chain": request["translation_chain"],
            "execution_record_sha256": sha256(output_bytes).hexdigest(),
            "projector_profile_id": request["profile_id"],
            "projector_version": PROJECTOR_VERSION,
            "projector_id": "EXTERNAL_EVIDENCE_V1",
            "candidate_only": True,
        }
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(payload), stderr="")


def test_server_execution_uses_verified_source_once_and_persists_replay_bundle(tmp_path, relation_db):
    transport = _Transport()
    service = AcquisitionJobService(tmp_path, relation_db=relation_db, transport=transport)
    runner = _Runner()

    result = execute_and_persist_server_projection(
        service,
        _request(),
        process_runner=runner,
        python_executable="/fake/projector-python",
    )

    assert result["status"] == "COMPLETED"
    assert result["execution"]["network_fetch_count"] == 1
    assert result["execution"]["external_model_execution_count"] == 1
    assert result["execution"]["persistence_network_fetch_count"] == 0
    assert result["execution"]["persistence_external_model_execution_count"] == 0
    assert result["canonical_hash216_minted"] is False
    assert transport.calls == 1
    assert runner.calls == 1
    assert runner.requests[0]["source_sha256"] == SOURCE_SHA
    assert runner.requests[0]["source_modality"] == "TEXT"

    job = result["job"]
    report = job["result"]["report"]
    assert report["ingress_record"]["classification"] == "TRANSLATION_INVARIANT_CANDIDATE"
    assert report["external_projection_receipts"][0]["model_repository"]["revision"] == TEXT_MODEL.revision
    replay = service.replay(job["job_id"])
    assert replay["status"] == "REPLAY_VERIFIED"
    assert replay["network_fetch_performed"] is False
    assert replay["external_model_execution_performed"] is False
    assert transport.calls == 1
    assert runner.calls == 1


def test_source_digest_failure_prevents_model_execution_and_job_creation(tmp_path, relation_db):
    service = AcquisitionJobService(tmp_path, relation_db=relation_db, transport=_Transport(b"tampered"))
    runner = _Runner()
    with pytest.raises(Exception, match="SOURCE_LENGTH_MISMATCH|SOURCE_DIGEST_MISMATCH"):
        execute_and_persist_server_projection(
            service,
            _request(),
            process_runner=runner,
            python_executable="/fake/projector-python",
        )
    assert runner.calls == 0
    assert service.list()["count"] == 0


def test_blocked_profile_fails_before_network_or_model(tmp_path, relation_db):
    transport = _Transport()
    service = AcquisitionJobService(tmp_path, relation_db=relation_db, transport=transport)
    runner = _Runner()
    with pytest.raises(ServerProjectorExecutionError, match="PROFILE_NOT_PRODUCTION_APPROVED"):
        execute_and_persist_server_projection(
            service,
            _request("MULTILINGUAL_CLIP_IMAGE_TEXT_V1"),
            process_runner=runner,
            python_executable="/fake/projector-python",
        )
    assert transport.calls == 0
    assert runner.calls == 0


def test_projector_process_failure_preserves_classification_and_does_not_persist(tmp_path, relation_db):
    service = AcquisitionJobService(tmp_path, relation_db=relation_db, transport=_Transport())
    runner = _Runner(returncode=2, classification="P219_APE_NONFINITE_VECTOR_REJECTED")
    with pytest.raises(ServerProjectorExecutionError, match="P219_APE_NONFINITE_VECTOR_REJECTED"):
        execute_and_persist_server_projection(
            service,
            _request(),
            process_runner=runner,
            python_executable="/fake/projector-python",
        )
    assert service.list()["count"] == 0


def test_execute_route_precedes_dynamic_job_route():
    paths = [route.path for route in router.routes]
    execute = "/api/v1/pass174/acquisition/jobs/execute"
    dynamic = "/api/v1/pass174/acquisition/jobs/{job_id}"
    assert execute in paths
    assert paths.index(execute) < paths.index(dynamic)

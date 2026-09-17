from __future__ import annotations

from base64 import b64encode
from hashlib import sha256

import pytest

from hhs_backend.api.pass219_acquisition_routes import router
from hhs_backend.pass219_acquisition_job_service import (
    AcquisitionJobService,
    AcquisitionJobServiceError,
)
from hhs_runtime.hhs_pass219_live_acquisition_replay_worker_v1 import FetchResponse
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import WordRelationEntry


SOURCE = b"A cat sits on a mat.\n"
SOURCE_SHA = sha256(SOURCE).hexdigest()
REVISION = "a" * 40
MODEL_REVISION = "b" * 40


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


def _model():
    return {
        "provider": "HUGGING_FACE",
        "repo_id": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        "revision": MODEL_REVISION,
        "license_id": "apache-2.0",
        "repo_kind": "MODEL",
        "source_url": "https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        "modalities": ["TEXT"],
    }


@pytest.fixture()
def relation_db():
    return {"cat": _entry("cat"), "mat": _entry("mat"), "sits": _entry("sits")}


def test_source_only_job_persists_hold_and_replays_without_network(tmp_path, relation_db):
    transport = _Transport()
    service = AcquisitionJobService(tmp_path, relation_db=relation_db, transport=transport)
    job = service.submit({"projector_id": "SOURCE_ONLY_V1", "source": _source()})

    assert job["status"] == "COMPLETED"
    assert job["result"]["report"]["ingress_record"]["classification"] == "HOLD_NO_SEMANTIC_PROJECTION"
    assert job["result"]["replay_bundle_persisted"] is True
    assert job["result"]["receipt"]["candidate_only"] is True
    assert transport.calls == 1

    replay = service.replay(job["job_id"])
    assert replay["status"] == "REPLAY_VERIFIED"
    assert replay["network_fetch_performed"] is False
    assert replay["external_model_execution_performed"] is False
    assert transport.calls == 1
    assert (
        replay["replay"]["replay_closure_hash72"]
        == job["result"]["report"]["replay_closure_hash72"]
    )


def test_external_evidence_job_seals_projection_and_survives_service_restart(tmp_path, relation_db):
    transport = _Transport()
    service = AcquisitionJobService(tmp_path, relation_db=relation_db, transport=transport)
    request = {
        "projector_id": "EXTERNAL_EVIDENCE_V1",
        "source": _source(),
        "projection_evidence": [{
            "model_repository": _model(),
            "pivot_text": "A cat sits on a mat",
            "source_language": "en",
            "pivot_language": "en",
            "source_modality": "TEXT",
            "output_b64": b64encode(b"external-model-output").decode("ascii"),
            "vector_identity_b64": b64encode(b"vector-identity").decode("ascii"),
            "similarity": {"numerator": 9, "denominator": 10},
            "semantic_labels": ["cat", "mat"],
            "translation_chain": ["en"],
        }],
    }
    job = service.submit(request)
    assert job["status"] == "COMPLETED"
    report = job["result"]["report"]
    assert report["ingress_record"]["classification"] == "TRANSLATION_INVARIANT_CANDIDATE"
    assert report["external_projection_receipts"][0]["model_output_sha256"] == sha256(b"external-model-output").hexdigest()
    assert report["vm81_commit_invoked"] is False
    assert report["canonical_hash216_minted"] is False

    restarted = AcquisitionJobService(tmp_path, relation_db=relation_db, transport=_Transport(b"network-must-not-be-used"))
    loaded = restarted.get(job["job_id"])
    assert loaded["receipt_hash72"] == job["receipt_hash72"]
    replay = restarted.replay(job["job_id"])
    assert replay["status"] == "REPLAY_VERIFIED"


def test_failed_digest_is_persisted_as_failed_job(tmp_path, relation_db):
    service = AcquisitionJobService(tmp_path, relation_db=relation_db, transport=_Transport(b"tampered"))
    job = service.submit({"projector_id": "SOURCE_ONLY_V1", "source": _source()})
    assert job["status"] == "FAILED"
    assert "SOURCE_LENGTH_MISMATCH" in job["error"]["classification"] or "SOURCE_DIGEST_MISMATCH" in job["error"]["classification"]
    with pytest.raises(AcquisitionJobServiceError, match="REPLAY_REQUIRES_COMPLETED_JOB"):
        service.replay(job["job_id"])


def test_unapproved_projector_fails_before_job_creation(tmp_path, relation_db):
    service = AcquisitionJobService(tmp_path, relation_db=relation_db, transport=_Transport())
    with pytest.raises(AcquisitionJobServiceError, match="PROJECTOR_NOT_APPROVED"):
        service.submit({"projector_id": "REMOTE_SHELL_V1", "source": _source()})
    assert service.list()["count"] == 0


def test_api_router_exposes_job_history_receipt_and_replay_paths():
    paths = {route.path for route in router.routes}
    assert "/api/v1/pass174/acquisition/status" in paths
    assert "/api/v1/pass174/acquisition/projectors" in paths
    assert "/api/v1/pass174/acquisition/jobs" in paths
    assert "/api/v1/pass174/acquisition/jobs/{job_id}" in paths
    assert "/api/v1/pass174/acquisition/jobs/{job_id}/receipt" in paths
    assert "/api/v1/pass174/acquisition/jobs/{job_id}/replay" in paths

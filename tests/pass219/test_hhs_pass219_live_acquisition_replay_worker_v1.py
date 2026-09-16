from __future__ import annotations

from hashlib import sha256

import pytest

from hhs_runtime.hhs_pass219_live_acquisition_replay_worker_v1 import (
    AcquisitionSourceSpec,
    ExternalProjectionEvidence,
    FetchResponse,
    LiveAcquisitionReplayError,
    LiveAcquisitionReplayWorker,
)
from hhs_runtime.hhs_pass219_translation_invariant_multimodal_ingress_v1 import (
    OpenSourceRepositoryDescriptor,
    TranslationInvariantIngressError,
)
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import WordRelationEntry


SOURCE_BYTES = b"A cat sits on a mat."


def _entry(word: str, *, synonyms=(), hypernyms=(), hyponyms=()) -> WordRelationEntry:
    return WordRelationEntry(
        word=word,
        pos=["noun"],
        definitions=[f"definition:{word}"],
        examples=[],
        synonyms=list(synonyms),
        antonyms=[],
        hypernyms=list(hypernyms),
        hyponyms=list(hyponyms),
        entry_hash72=(word[:1] or "x") * 24,
    )


@pytest.fixture()
def relation_db():
    return {
        "cat": _entry("cat", synonyms=("feline",), hypernyms=("animal",)),
        "feline": _entry("feline", synonyms=("cat",), hypernyms=("animal",)),
        "animal": _entry("animal", hyponyms=("cat",)),
        "mat": _entry("mat", synonyms=("rug",)),
        "rug": _entry("rug", synonyms=("mat",)),
        "sits": _entry("sits", synonyms=("rests",)),
        "rests": _entry("rests", synonyms=("sits",)),
    }


def _source_repo(*, revision: str = "a" * 40):
    return OpenSourceRepositoryDescriptor(
        provider="GITHUB",
        repo_id="example/open-source-corpus",
        revision=revision,
        license_id="apache-2.0",
        repo_kind="CODE",
        source_url="https://github.com/example/open-source-corpus",
        modalities=("TEXT",),
    )


def _model_repo():
    return OpenSourceRepositoryDescriptor(
        provider="HUGGING_FACE",
        repo_id="sentence-transformers/clip-ViT-B-32-multilingual-v1",
        revision="b" * 40,
        license_id="apache-2.0",
        repo_kind="MODEL",
        source_url="https://huggingface.co/sentence-transformers/clip-ViT-B-32-multilingual-v1",
        modalities=("TEXT", "IMAGE"),
    )


def _spec(*, content: bytes = SOURCE_BYTES, revision: str = "a" * 40):
    return AcquisitionSourceSpec(
        repository=_source_repo(revision=revision),
        artifact_path="corpus/cat.en.txt",
        expected_sha256=sha256(content).hexdigest(),
        expected_byte_length=len(content),
        declared_media_type="TEXT",
        source_language="en",
    )


def _evidence(*, output_bytes: bytes = b'{"label":"cat","score":"9/10"}'):
    return ExternalProjectionEvidence(
        model_repository=_model_repo(),
        pivot_text="A cat sits on a mat",
        source_language="en",
        pivot_language="en",
        source_modality="TEXT",
        output_bytes=output_bytes,
        vector_identity_bytes=b"vector:a-cat-on-mat",
        similarity_numerator=9,
        similarity_denominator=10,
        semantic_labels=("cat", "mat"),
        translation_chain=("en",),
    )


class _Transport:
    def __init__(self, body: bytes = SOURCE_BYTES, *, requested_url: str | None = None, status: int = 200):
        self.body = body
        self.requested_url = requested_url
        self.status = status
        self.calls = 0

    def fetch(self, spec: AcquisitionSourceSpec):
        self.calls += 1
        url = self.requested_url or spec.pinned_url()
        return FetchResponse(
            requested_url=url,
            final_url=url,
            status=self.status,
            body=self.body,
            headers=(("Content-Type", "text/plain"), ("ETag", '"abc"')),
        )


class _Projector:
    def __init__(self, evidence=None):
        self.evidence = evidence or (_evidence(),)
        self.calls = 0

    def project(self, artifact):
        self.calls += 1
        return self.evidence


def test_github_source_url_is_derived_from_immutable_revision():
    spec = _spec()
    assert spec.pinned_url() == (
        "https://raw.githubusercontent.com/example/open-source-corpus/"
        + ("a" * 40)
        + "/corpus/cat.en.txt"
    )


def test_moving_revision_is_rejected_before_fetch():
    with pytest.raises(TranslationInvariantIngressError, match="IMMUTABLE_REVISION_REQUIRED"):
        _spec(revision="main").validated()


def test_source_digest_is_verified_before_external_model_execution(relation_db):
    transport = _Transport(body=b"tampered")
    projector = _Projector()
    worker = LiveAcquisitionReplayWorker(relation_db, transport=transport)
    with pytest.raises(LiveAcquisitionReplayError, match="SOURCE_LENGTH_MISMATCH"):
        worker.execute_live(_spec(), projector)
    assert transport.calls == 1
    assert projector.calls == 0


def test_live_acquisition_seals_source_model_output_and_candidate_ingress(relation_db):
    transport = _Transport()
    projector = _Projector()
    worker = LiveAcquisitionReplayWorker(relation_db, transport=transport)
    report = worker.execute_live(_spec(), projector)

    assert report["mode"] == "LIVE_ACQUISITION"
    assert report["source"]["network_fetch_performed"] is True
    assert report["source"]["actual_sha256"] == sha256(SOURCE_BYTES).hexdigest()
    external = report["external_projection_receipts"][0]
    assert external["model_output_sha256"] == sha256(_evidence().output_bytes).hexdigest()
    assert external["vector_identity_sha256"] == sha256(b"vector:a-cat-on-mat").hexdigest()
    assert external["similarity"] == {"numerator": 9, "denominator": 10}
    assert report["ingress_record"]["classification"] == "TRANSLATION_INVARIANT_CANDIDATE"
    assert report["candidate_only"] is True
    assert report["truth_promotion"] is False
    assert report["vm81_commit_invoked"] is False
    assert report["canonical_hash72_minted"] is False
    assert report["canonical_hash216_minted"] is False


def test_archived_replay_closes_without_network_or_model_execution(relation_db):
    transport = _Transport()
    projector = _Projector()
    worker = LiveAcquisitionReplayWorker(relation_db, transport=transport)
    live = worker.execute_live(_spec(), projector)

    replay = worker.replay_archived(
        _spec(),
        source_bytes=SOURCE_BYTES,
        projection_evidence=(_evidence(),),
        expected_replay_closure_hash72=live["replay_closure_hash72"],
    )
    assert replay["replay_closure_hash72"] == live["replay_closure_hash72"]
    assert replay["network_fetch_performed"] is False
    assert replay["external_model_execution_performed"] is False
    assert transport.calls == 1
    assert projector.calls == 1


def test_tampered_archived_projection_cannot_replay_as_same_closure(relation_db):
    worker = LiveAcquisitionReplayWorker(relation_db, transport=_Transport())
    live = worker.execute_live(_spec(), _Projector())
    tampered = _evidence(output_bytes=b'{"label":"dog","score":"9/10"}')
    with pytest.raises(LiveAcquisitionReplayError, match="REPLAY_CLOSURE_MISMATCH"):
        worker.replay_archived(
            _spec(),
            source_bytes=SOURCE_BYTES,
            projection_evidence=(tampered,),
            expected_replay_closure_hash72=live["replay_closure_hash72"],
        )


def test_transport_cannot_substitute_a_different_request_url(relation_db):
    transport = _Transport(requested_url="https://raw.githubusercontent.com/other/repo/deadbeef/file")
    worker = LiveAcquisitionReplayWorker(relation_db, transport=transport)
    with pytest.raises(LiveAcquisitionReplayError, match="REQUEST_URL_DIVERGENCE"):
        worker.execute_live(_spec(), _Projector())


def test_non_200_transport_response_is_rejected(relation_db):
    worker = LiveAcquisitionReplayWorker(relation_db, transport=_Transport(status=404))
    with pytest.raises(LiveAcquisitionReplayError, match="HTTP_STATUS_REJECTED"):
        worker.execute_live(_spec(), _Projector())


def test_projection_similarity_must_be_exact_and_bounded():
    bad = ExternalProjectionEvidence(
        model_repository=_model_repo(),
        pivot_text="cat",
        source_language="en",
        pivot_language="en",
        source_modality="TEXT",
        output_bytes=b"x",
        vector_identity_bytes=b"v",
        similarity_numerator=11,
        similarity_denominator=10,
    )
    with pytest.raises(LiveAcquisitionReplayError, match="SIMILARITY_RANGE"):
        bad.validated()


def test_replay_closure_can_be_recomputed_from_report(relation_db):
    worker = LiveAcquisitionReplayWorker(relation_db, transport=_Transport())
    report = worker.execute_live(_spec(), _Projector())
    assert worker.replay_closure_hash72(report) == report["replay_closure_hash72"]

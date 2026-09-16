from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass219_translation_invariant_multimodal_ingress_v1 import (
    ALLOWED_LICENSES,
    ExactSemanticProjection,
    OpenSourceRepositoryDescriptor,
    RepositoryArtifact,
    TranslationInvariantIngressError,
    TranslationInvariantMultimodalIngress,
)
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import WordRelationEntry


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


def _github_repo(*, license_id: str = "apache-2.0", revision: str = "a" * 40):
    return OpenSourceRepositoryDescriptor(
        provider="GITHUB",
        repo_id="example/open-source-corpus",
        revision=revision,
        license_id=license_id,
        repo_kind="CODE",
        source_url="https://github.com/example/open-source-corpus",
        modalities=("TEXT", "IMAGE"),
    )


def _hf_model(*, candidate_only: bool = True):
    return OpenSourceRepositoryDescriptor(
        provider="HUGGING_FACE",
        repo_id="sentence-transformers/clip-ViT-B-32-multilingual-v1",
        revision="b" * 40,
        license_id="apache-2.0",
        repo_kind="MODEL",
        source_url="https://huggingface.co/sentence-transformers/clip-ViT-B-32-multilingual-v1",
        modalities=("TEXT", "IMAGE"),
    )


def _projection(artifact: RepositoryArtifact, *, score=(9, 10), candidate_only=True):
    payload = f"projection:{artifact.path}:a cat sits on a mat".encode("utf-8")
    return ExactSemanticProjection(
        model_repository=_hf_model(),
        pivot_text="A cat sits on a mat",
        source_language=artifact.source_language or "und",
        pivot_language="en",
        source_modality=artifact.declared_media_type or "TEXT",
        model_output_sha256=sha256(payload).hexdigest(),
        vector_identity_sha256=sha256(b"vector:a-cat-on-mat").hexdigest(),
        similarity_numerator=score[0],
        similarity_denominator=score[1],
        semantic_labels=("cat", "mat"),
        translation_chain=(artifact.source_language or "und", "en"),
        candidate_only=candidate_only,
    )


class _Projector:
    def __init__(self, *, score=(9, 10), empty=False, candidate_only=True):
        self.score = score
        self.empty = empty
        self.candidate_only = candidate_only

    def project(self, artifact: RepositoryArtifact):
        if self.empty:
            return ()
        return (_projection(artifact, score=self.score, candidate_only=self.candidate_only),)


def _pipeline(relation_db, projector=None):
    return TranslationInvariantMultimodalIngress(
        relation_db,
        projector or _Projector(),
    )


def test_revision_must_be_immutable_commit():
    with pytest.raises(TranslationInvariantIngressError, match="IMMUTABLE_REVISION_REQUIRED"):
        _github_repo(revision="main").validated()


def test_noncommercial_license_is_not_production_open_source_admission():
    assert "cc-by-nc-4.0" not in ALLOWED_LICENSES
    with pytest.raises(TranslationInvariantIngressError, match="LICENSE_NOT_ALLOWED"):
        _github_repo(license_id="cc-by-nc-4.0").validated()


def test_cross_language_translation_invariant_family_preserves_raw_identity(relation_db):
    pipeline = _pipeline(relation_db)
    english = RepositoryArtifact(
        _github_repo(),
        "corpus/cat.en.txt",
        b"A cat sits on a mat.",
        "TEXT",
        "en",
    )
    spanish = RepositoryArtifact(
        _github_repo(),
        "corpus/cat.es.txt",
        "Un gato se sienta en una estera.".encode("utf-8"),
        "TEXT",
        "es",
    )
    result = pipeline.analyze_batch((english, spanish))
    records = result["records"]
    assert records[0]["source_sha256"] != records[1]["source_sha256"]
    assert (
        records[0]["translation_invariant_semantic_family_hash72"]
        == records[1]["translation_invariant_semantic_family_hash72"]
    )
    family = result["semantic_families"][0]
    assert family["cross_language_correspondence_observed"] is True
    assert family["translation_invariance_status"] == "CANDIDATE_CORRESPONDENCE_NOT_TRUTH_PROOF"


def test_cross_modal_text_image_can_share_candidate_family(relation_db):
    pipeline = _pipeline(relation_db)
    text = RepositoryArtifact(
        _github_repo(),
        "corpus/cat.txt",
        b"A cat sits on a mat.",
        "TEXT",
        "en",
    )
    image = RepositoryArtifact(
        _github_repo(),
        "images/cat.png",
        b"\x89PNG\r\n\x1a\n" + (b"\x00" * 512),
        "IMAGE",
        None,
    )
    result = pipeline.analyze_batch((text, image))
    assert result["candidate_family_count"] == 1
    family = result["semantic_families"][0]
    assert family["cross_modal_correspondence_observed"] is True
    assert set(family["modalities"]) == {"IMAGE", "TEXT"}


def test_low_exact_similarity_holds_without_rejection_or_commit(relation_db):
    pipeline = _pipeline(relation_db, _Projector(score=(1, 4)))
    artifact = RepositoryArtifact(
        _github_repo(),
        "corpus/weak.txt",
        b"A cat sits on a mat.",
        "TEXT",
        "en",
    )
    result = pipeline.analyze_artifact(artifact)
    assert result["classification"] == "HOLD_SEMANTIC_PROJECTION_BELOW_THRESHOLD"
    assert result["candidate_only"] is True
    assert result["truth_promotion"] is False
    assert result["canonical_learning_commit_invoked"] is False
    assert result["vm81_commit_invoked"] is False
    assert result["canonical_hash216_minted"] is False


def test_missing_projection_holds_and_keeps_pass165_source_receipt(relation_db):
    pipeline = _pipeline(relation_db, _Projector(empty=True))
    artifact = RepositoryArtifact(
        _github_repo(),
        "corpus/unprojected.txt",
        b"Unprojected but preserved source bytes.",
        "TEXT",
        "en",
    )
    result = pipeline.analyze_artifact(artifact)
    assert result["classification"] == "HOLD_NO_SEMANTIC_PROJECTION"
    assert result["source_sha256"] == sha256(artifact.content).hexdigest()
    assert result["pass165_projection_hash72"]
    assert result["translation_invariant_semantic_family_hash72"] is None


def test_external_projection_cannot_self_grant_authority(relation_db):
    pipeline = _pipeline(relation_db, _Projector(candidate_only=False))
    artifact = RepositoryArtifact(
        _github_repo(),
        "corpus/drift.txt",
        b"A cat sits on a mat.",
        "TEXT",
        "en",
    )
    with pytest.raises(TranslationInvariantIngressError, match="PROJECTION_AUTHORITY_DRIFT"):
        pipeline.analyze_artifact(artifact)


def test_repository_and_model_receipts_are_revision_pinned(relation_db):
    pipeline = _pipeline(relation_db)
    artifact = RepositoryArtifact(
        _github_repo(),
        "corpus/pinned.txt",
        b"A cat sits on a mat.",
        "TEXT",
        "en",
    )
    result = pipeline.analyze_artifact(artifact)
    assert result["repository"]["revision"] == "a" * 40
    selected = result["semantic_projections"][0]
    assert selected["model_repository"]["revision"] == "b" * 40
    assert selected["similarity"] == {"numerator": 9, "denominator": 10}


def test_registry_records_only_allowlisted_production_references():
    root = Path(__file__).resolve().parents[2]
    registry = json.loads(
        (root / "data" / "pass219" / "open_source_multimodal_ingress_registry_v1.json").read_text("utf-8")
    )
    assert registry["policy"]["immutable_revision_required_for_ingestion"] is True
    assert registry["policy"]["publicly_downloadable_is_not_equivalent_to_open_source"] is True
    for item in registry["references"]:
        assert item["license_id"] in ALLOWED_LICENSES
        if item["discovery_only"] is False:
            assert len(item["revision"]) == 40
    excluded = {item["repo_id"]: item for item in registry["excluded_examples"]}
    assert excluded["facebook/nllb-200-distilled-600M"]["license_id"] == "cc-by-nc-4.0"

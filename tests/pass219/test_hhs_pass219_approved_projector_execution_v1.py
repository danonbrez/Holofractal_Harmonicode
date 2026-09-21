from __future__ import annotations

from base64 import b64decode
from hashlib import sha256
import json
import math

import pytest

from hhs_runtime.hhs_pass219_approved_projector_execution_v1 import (
    ApprovedProjectorExecutionError,
    ProjectionExecutionRequest,
    execute_projection,
    execution_profiles,
)


class FakeRuntime:
    def __init__(self, source_vector=(1.0, 0.0), pivot_vector=(0.8, 0.6)) -> None:
        self.source_vector = source_vector
        self.pivot_vector = pivot_vector
        self.calls = 0

    def encode_text(self, model, text):
        del model, text
        self.calls += 1
        return self.source_vector if self.calls == 1 else self.pivot_vector

    def encode_image(self, model, image_bytes):
        del model, image_bytes
        raise AssertionError("image execution must not run in the production-approved text profile")


def make_request(source: bytes = b"The weather is lovely today.") -> ProjectionExecutionRequest:
    return ProjectionExecutionRequest(
        profile_id="MULTILINGUAL_MPNET_TEXT_V1",
        source_bytes=source,
        source_sha256=sha256(source).hexdigest(),
        source_language="en",
        source_modality="TEXT",
        pivot_text="It is sunny outside.",
        pivot_language="en",
        semantic_labels=("weather", "sunny"),
        translation_chain=("en",),
    )


def test_profile_registry_keeps_clip_blocked_until_license_and_compatibility_proof():
    profiles = execution_profiles()
    by_id = {item["profile_id"]: item for item in profiles["profiles"]}
    assert by_id["MULTILINGUAL_MPNET_TEXT_V1"]["production_approved"] is True
    blocked = by_id["MULTILINGUAL_CLIP_IMAGE_TEXT_V1"]
    assert blocked["production_approved"] is False
    assert "LICENSE_NOT_EXPLICIT" in blocked["blocked_reason"]
    assert profiles["canonical_authority_minted"] is False


def test_text_execution_emits_external_evidence_v1_shape_with_exact_rational():
    result = execute_projection(make_request(), FakeRuntime())
    assert result["projector_id"] == "EXTERNAL_EVIDENCE_V1"
    assert result["projector_profile_id"] == "MULTILINGUAL_MPNET_TEXT_V1"
    assert result["candidate_only"] is True
    assert result["similarity"] == {"numerator": 4, "denominator": 5}
    assert result["model_repository"]["revision"] == "79f2382ceacceacdf38563d7c5d16b9ff8d725d6"
    output = json.loads(b64decode(result["output_b64"]).decode("utf-8"))
    assert output["external_model_execution"] is True
    assert output["trust_remote_code"] is False
    assert output["safetensors_required"] is True
    assert output["canonical_authority_minted"] is False
    assert output["bounded_similarity_decimal"] == "0.800000000"
    assert len(b64decode(result["vector_identity_b64"])) == 24


def test_source_digest_mismatch_fails_before_model_execution():
    request = make_request()
    bad = ProjectionExecutionRequest(
        **{**request.__dict__, "source_sha256": "0" * 64}
    )
    runtime = FakeRuntime()
    with pytest.raises(ApprovedProjectorExecutionError, match="P219_APE_SOURCE_SHA256_MISMATCH"):
        execute_projection(bad, runtime)
    assert runtime.calls == 0


def test_nonfinite_vector_output_cannot_become_exact_witness():
    runtime = FakeRuntime(source_vector=(1.0, math.nan), pivot_vector=(1.0, 0.0))
    with pytest.raises(ApprovedProjectorExecutionError, match="P219_APE_NONFINITE_VECTOR_REJECTED"):
        execute_projection(make_request(), runtime)


def test_image_profile_is_not_executable_until_production_admitted():
    request = make_request()
    blocked = ProjectionExecutionRequest(
        **{**request.__dict__, "profile_id": "MULTILINGUAL_CLIP_IMAGE_TEXT_V1", "source_modality": "IMAGE"}
    )
    with pytest.raises(ApprovedProjectorExecutionError, match="P219_APE_PROFILE_NOT_PRODUCTION_APPROVED"):
        execute_projection(blocked, FakeRuntime())


def test_wrong_modality_rejected_for_text_profile():
    request = make_request()
    wrong = ProjectionExecutionRequest(
        **{**request.__dict__, "source_modality": "IMAGE"}
    )
    with pytest.raises(ApprovedProjectorExecutionError, match="P219_APE_TEXT_PROFILE_MODALITY_MISMATCH"):
        execute_projection(wrong, FakeRuntime())

from __future__ import annotations

from copy import deepcopy

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_hash216_vm5184_i28 import (
    install_pass218_i28_transition_control,
)
from hhs_backend.runtime_os_pass218_hash216_vm5184_validation_i29 import (
    PASS218_I29_STATUS_PATH,
    PASS218_I29_VALIDATE_PATH,
    Pass218I29RuntimeValidationControl,
    install_pass218_i29_validation_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.formal_analogical_differentiation_i27 import (
    Pass218I27DifferentiationRequest,
)
from hhs_runtime.pass218.grounded_manifold_i26 import Pass218I26ManifoldRequest
from hhs_runtime.pass218.hash216_vm5184_transition_i28 import (
    Pass218I28Hash216VM5184Transition,
    Pass218I28TransitionRequest,
)
from hhs_runtime.pass218.hash216_vm5184_validation_i29 import (
    Pass218I29Hash216VM5184Validator,
    Pass218I29ValidationError,
    Pass218I29ValidationRequest,
)
from hhs_runtime.pass218.narrative_beat_i24 import Pass218I24BeatRequest
from hhs_runtime.pass218.perspective_context_i25 import (
    Pass218I25PerspectiveProfile,
    Pass218I25PerspectiveRequest,
)


def h72(domain: str, value: object) -> str:
    return hash72_digest({"domain": domain}, value)


def h216(domain: str, value: object) -> str:
    return h72(domain + "-A", value) + h72(domain + "-B", value) + h72(domain + "-C", value)


class FakeNativeBridge:
    @staticmethod
    def abi_status() -> dict[str, object]:
        return {
            "state_bits": 5184,
            "cell_count": 81,
            "bits_per_cell": 64,
            "projection_channels": 32,
            "canonical_float_fields": 0,
        }

    @staticmethod
    def state_root(words):
        return h216("I29-STATE", list(words))

    @staticmethod
    def project_full(words):
        return [
            [int((int(word) >> (channel % 64)) & 0xFFFFFFFF) for word in words]
            for channel in range(32)
        ]

    @staticmethod
    def projection_root(channels):
        return h216("I29-PROJECTION", [list(row) for row in channels])

    @staticmethod
    def hash216_bytes(payload: bytes):
        return h216("I29-BYTES", payload.hex())

    @staticmethod
    def build_token(**kwargs):
        return {
            "parent_root216": kwargs["parent_root"],
            "content_root216": kwargs["content_root"],
            "delta_root216": kwargs["delta_root"],
            "hydration_root216": kwargs["hydration_root"],
            "dependency_root216": kwargs["dependency_root"],
            "projection_root216": kwargs["projection_root"],
            "learning_root216": kwargs["learning_root"],
            "continuation_root216": h216("I29-CONTINUATION", kwargs),
            "parent_receipt_hash72": kwargs["parent_receipt"],
            "receipt_hash72": h72("I29-NATIVE-RECEIPT", kwargs),
            "generation": int(kwargs["generation"]),
        }


class FakeI27Control:
    def status(self) -> dict:
        return {
            "formal_analogical_differentiation_candidate_ready": True,
            "formal_analogical_differentiation_status": (
                "REVISABLE_FORMAL_ANALOGICAL_DIFFERENTIATION_CANDIDATE"
            ),
            "formal_analogical_typing_canonical": False,
            "hash216_continuation_verified": False,
            "vm5184_authoritative_projection_invoked": False,
            "vm81_authorization_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }

    def differentiate(self, request: Pass218I27DifferentiationRequest) -> dict:
        request.validated()
        profile_version = (
            request.manifold_request.perspective_request.perspective_profile.profile_version
        )
        curriculum = (
            request.manifold_request.perspective_request.beat_request.curriculum_identity_hash72
        )
        grounding = h72("I29-GROUNDING", [curriculum, profile_version])
        specs = (
            ("LEXICAL_SYNONYM", "SIMILARITY", 1),
            ("LEXICAL_HYPERNYM", "IMPLICATION", 1),
            ("LEXICAL_ANTONYM", "CONTRADICTION", -1),
        )
        relations = []
        for rank, (relation_type, family, status) in enumerate(specs, start=1):
            relations.append(
                {
                    "source_id_hash72": h72("I29-SOURCE", rank),
                    "target_id_hash72": h72("I29-TARGET", rank),
                    "grounded_relation_hash72": h72("I29-GROUNDED", rank),
                    "differentiated_relation_hash72": h72(
                        "I29-DIFFERENTIATED", [rank, profile_version]
                    ),
                    "grounding_identity_hash72": grounding,
                    "perspective_order_rank": rank,
                    "relation_type": relation_type,
                    "relation_family_candidate": family,
                    "relation_family_resolved": True,
                    "differentiation_mode": (
                        "COMPARATIVE" if family == "SIMILARITY" else "FORMAL"
                    ),
                    "status": status,
                    "exact_strength": {
                        "numerator": rank + 3,
                        "denominator": rank + 5,
                    },
                    "provenance": "I29_TEST_FIXTURE",
                }
            )
        return {
            **self.status(),
            "formal_analogical_typing_invoked": True,
            "formal_analogical_differentiation_hash72": h72(
                "I29-I27-RESULT", profile_version
            ),
            "differentiation_state_hash72": h72("I29-I27-STATE", profile_version),
            "i26_grounded_relational_manifold_hash72": h72("I29-I26", profile_version),
            "i24_narrative_beat_hash72": h72("I29-I24", profile_version),
            "i25_perspective_context_hash72": h72("I29-I25", profile_version),
            "grounding_identity": {
                "grounding_identity_hash72": grounding,
                "curriculum_identity_hash72": curriculum,
                "source_checksum_sha256": "a" * 64,
                "general_english_genesis_mutated": False,
            },
            "differentiated_relations": relations,
            "relation_family_layers": [
                {"relation_family_candidate": family, "candidate_only": True}
                for family in ("SIMILARITY", "IMPLICATION", "CONTRADICTION")
            ],
            "relation_count": len(relations),
            "resolved_relation_count": len(relations),
            "unresolved_relation_count": 0,
            "differentiation_complete": True,
            "meaning_conservation": {
                "i26_manifold_identity_preserved": True,
                "grounding_identity_preserved": True,
                "relation_direction_preserved": True,
                "upstream_relation_type_preserved": True,
                "exact_status_preserved": True,
                "provenance_preserved": True,
                "authorization_not_widened": True,
                "validation_status_not_promoted": True,
            },
            "validation_receipt": {
                "differentiation_validation_receipt_hash72": h72(
                    "I29-I27-RECEIPT", profile_version
                )
            },
            "i20_binding_hash72": h72("I29-I20", "binding"),
            "i21_batch_hash72": h72("I29-I21", "batch"),
            "i22_graph_hash72": h72("I29-I22", "graph"),
            "i23_contextual_state_hash72": h72("I29-I23", "state"),
        }


def transition_request(profile_version: str = "v1") -> Pass218I28TransitionRequest:
    beat = Pass218I24BeatRequest(
        tokens=("relation", "validation"),
        context_id="i29 hash216 vm5184 validation fixture",
        curriculum_identity_hash72=h72("I29-CURRICULUM", "fixture"),
        curriculum_position=29,
        source_id="i29-fixture",
        source_checksum_sha256="b" * 64,
        source_authority="REPOSITORY_NATIVE",
        rights_class="REPOSITORY_NATIVE",
        evidence_id="i29-fixture-evidence",
        evidence_type="RELATIONAL_OBSERVATION",
        evidence_epistemic_status="OBSERVED",
        evidence_payload_hash72=h72("I29-EVIDENCE", "fixture"),
        attention_tokens=("relation",),
        top_k=2,
        attention_radius=1,
        max_hydrated_nodes=24,
    ).validated()
    profile = Pass218I25PerspectiveProfile(
        profile_id="i29-test-perspective",
        profile_version=profile_version,
        profile_origin="USER_AUTHORED",
        rules=(),
    ).validated()
    perspective = Pass218I25PerspectiveRequest(
        beat_request=beat,
        perspective_profile=profile,
    ).validated()
    manifold = Pass218I26ManifoldRequest(perspective_request=perspective).validated()
    differentiation = Pass218I27DifferentiationRequest(
        manifold_request=manifold
    ).validated()
    return Pass218I28TransitionRequest(
        differentiation_request=differentiation
    ).validated()


def validation_request(profile_version: str = "v1") -> Pass218I29ValidationRequest:
    return Pass218I29ValidationRequest(
        transition_request=transition_request(profile_version)
    ).validated()


def api_payload() -> dict:
    request = transition_request()
    perspective = request.differentiation_request.manifold_request.perspective_request
    beat = perspective.beat_request
    profile = perspective.perspective_profile
    return {
        "tokens": list(beat.tokens),
        "context_id": beat.context_id,
        "curriculum_identity_hash72": beat.curriculum_identity_hash72,
        "curriculum_position": beat.curriculum_position,
        "source_identity": {
            "source_id": beat.source_id,
            "source_checksum_sha256": beat.source_checksum_sha256,
            "source_authority": beat.source_authority,
            "rights_class": beat.rights_class,
        },
        "evidence": {
            "evidence_id": beat.evidence_id,
            "evidence_type": beat.evidence_type,
            "epistemic_status": beat.evidence_epistemic_status,
            "payload_hash72": beat.evidence_payload_hash72,
        },
        "attention_tokens": list(beat.attention_tokens),
        "top_k": beat.top_k,
        "attention_radius": beat.attention_radius,
        "max_hydrated_nodes": beat.max_hydrated_nodes,
        "allowed_relation_families": list(beat.allowed_relation_families),
        "perspective_profile": {
            "profile_id": profile.profile_id,
            "profile_version": profile.profile_version,
            "profile_origin": profile.profile_origin,
            "rules": [],
        },
    }


def components():
    i27 = FakeI27Control()
    i28 = Pass218I28Hash216VM5184Transition(
        i27,
        native_bridge=FakeNativeBridge,
    )
    i29 = Pass218I29Hash216VM5184Validator(
        i28,
        i27,
        native_bridge=FakeNativeBridge,
    )
    return i27, i28, i29


class TamperingI28:
    def __init__(self, base, mutator):
        self.base = base
        self.mutator = mutator

    def status(self):
        return self.base.status()

    def construct(self, request):
        result = deepcopy(self.base.construct(request))
        self.mutator(result)
        return result


class DriftStatusI28:
    def __init__(self, base):
        self.base = base

    def status(self):
        result = dict(self.base.status())
        result["semantic_transition_validated"] = True
        return result

    def construct(self, request):
        return self.base.construct(request)


class FakeRuntimeI27:
    def __init__(self):
        self.differentiator = FakeI27Control()

    def status(self):
        return self.differentiator.status()

    def differentiate(self, request):
        return self.differentiator.differentiate(request)


def test_i29_validates_real_hash216_receipt_without_promotion() -> None:
    _, _, validator = components()
    result = validator.validate(validation_request())
    segments = result["pass218_validated_hash216_segments"]
    assert result["pass218_validated_hash216"] == (
        segments["manifest_curriculum_hash72"]
        + segments["hydrated_transition_state_hash72"]
        + segments["validation_receipt_hash72"]
    )
    assert len(result["pass218_validated_hash216"]) == 216
    assert result["hash216_continuation_verified"] is True
    assert result["semantic_transition_validated"] is True
    assert result["vm5184_candidate_projection_verified"] is True
    assert result["candidate_semantic_binding_verified"] is True
    assert result["formal_semantic_round_trip_verified"] is False
    assert result["atomic_promotion_candidate_ready"] is True
    assert result["atomic_promotion_authorized"] is False
    assert result["vm5184_authoritative_projection_invoked"] is False
    assert result["vm81_authorization_invoked"] is False
    assert result["atomic_promotion_invoked"] is False
    assert result["truth_promotion"] is False
    assert result["action_authority_minted"] is False
    assert result["canonical_learning_commit_invoked"] is False
    assert result["model_activation_invoked"] is False
    assert result["verbatim_corpus_source_retained"] is False
    assert result["authoritative_float_weights_created"] is False


def test_i29_exact_replay_and_profile_change_are_distinct() -> None:
    _, _, validator = components()
    first = validator.validate(validation_request("v1"))
    replay = validator.validate(validation_request("v1"))
    alternate = validator.validate(validation_request("v2"))
    assert first == replay
    assert first["hash216_vm5184_validation_hash72"] == replay[
        "hash216_vm5184_validation_hash72"
    ]
    assert first["pass218_validated_hash216"] == replay["pass218_validated_hash216"]
    assert first["hash216_vm5184_validation_hash72"] != alternate[
        "hash216_vm5184_validation_hash72"
    ]


def test_i29_rejects_vm_and_receipt_tampering() -> None:
    i27, base, _ = components()

    def corrupt_word(result):
        result["vm5184_candidate"]["state_words"][0] ^= 1

    with pytest.raises(
        Pass218I29ValidationError,
        match="P218_I29_VM5184_RELATION_CELL_BINDING_MISMATCH",
    ):
        Pass218I29Hash216VM5184Validator(
            TamperingI28(base, corrupt_word),
            i27,
            native_bridge=FakeNativeBridge,
        ).validate(validation_request())

    def corrupt_receipt(result):
        result["prevalidation_receipt"]["semantic_transition_validated"] = True

    with pytest.raises(
        Pass218I29ValidationError,
        match="P218_I29_PREVALIDATION_RECEIPT_TAMPERED",
    ):
        Pass218I29Hash216VM5184Validator(
            TamperingI28(base, corrupt_receipt),
            i27,
            native_bridge=FakeNativeBridge,
        ).validate(validation_request())


def test_i29_rejects_upstream_authority_drift() -> None:
    i27, base, _ = components()
    with pytest.raises(
        Pass218I29ValidationError,
        match="P218_I29_I28_STATUS_SAFETY_DRIFT",
    ):
        Pass218I29Hash216VM5184Validator(
            DriftStatusI28(base),
            i27,
            native_bridge=FakeNativeBridge,
        ).validate(validation_request())


def test_i29_runtime_surface_is_validation_only_and_browser_safe() -> None:
    app = FastAPI()
    i27_runtime = FakeRuntimeI27()
    i28_control = install_pass218_i28_transition_control(app, i27_runtime)
    i28_control.transitioner._native_bridge_override = FakeNativeBridge
    i29_control = install_pass218_i29_validation_control(
        app,
        i28_control,
        i27_runtime,
    )
    assert isinstance(i29_control, Pass218I29RuntimeValidationControl)
    i29_control.validator._native_bridge_override = FakeNativeBridge

    with TestClient(app) as client:
        status = client.get(PASS218_I29_STATUS_PATH)
        assert status.status_code == 200
        assert status.json()["hash216_vm5184_validation_ready"] is True

        validated = client.post(PASS218_I29_VALIDATE_PATH, json=api_payload())
        assert validated.status_code == 200
        assert validated.json()["semantic_transition_validated"] is True
        assert validated.json()["atomic_promotion_authorized"] is False

        assert client.get(PASS218_I29_VALIDATE_PATH).status_code == 405
        paths = {str(route.path) for route in app.router.routes}
        assert not any("promotion" in path for path in paths)

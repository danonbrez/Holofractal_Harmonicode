from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_hash216_vm5184_i28 import (
    PASS218_I28_CANDIDATES_PATH,
    PASS218_I28_STATUS_PATH,
    Pass218I28RuntimeTransitionControl,
    install_pass218_i28_transition_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.formal_analogical_differentiation_i27 import (
    Pass218I27DifferentiationRequest,
)
from hhs_runtime.pass218.grounded_manifold_i26 import Pass218I26ManifoldRequest
from hhs_runtime.pass218.hash216_vm5184_transition_i28 import (
    PASS218_I28_VM5184_MAPPING_VERSION,
    VM5184_CELL_COUNT,
    VM5184_STATE_BITS,
    Pass218I28Hash216VM5184Transition,
    Pass218I28TransitionError,
    Pass218I28TransitionRequest,
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
        return h216("I28-STATE", list(words))

    @staticmethod
    def project_full(words):
        return [
            [int((int(word) >> (channel % 64)) & 0xFFFFFFFF) for word in words]
            for channel in range(32)
        ]

    @staticmethod
    def projection_root(channels):
        return h216("I28-PROJECTION", [list(row) for row in channels])

    @staticmethod
    def hash216_bytes(payload: bytes):
        return h216("I28-BYTES", payload.hex())

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
            "continuation_root216": h216("I28-CONTINUATION", kwargs),
            "parent_receipt_hash72": kwargs["parent_receipt"],
            "receipt_hash72": h72("I28-NATIVE-RECEIPT", kwargs),
            "generation": int(kwargs["generation"]),
        }


class FakeI27Control:
    def __init__(self, *, unresolved: bool = False, safety_drift: str | None = None) -> None:
        self.unresolved = unresolved
        self.safety_drift = safety_drift

    def status(self) -> dict:
        result = {
            "formal_analogical_differentiation_candidate_ready": True,
            "formal_analogical_differentiation_status": (
                "REVISABLE_FORMAL_ANALOGICAL_DIFFERENTIATION_CANDIDATE"
            ),
            "formal_analogical_typing_canonical": False,
            "grounded_relational_manifold_ready": False,
            "grounded_relational_manifold_promoted": False,
            "hash216_continuation_verified": False,
            "vm5184_authoritative_projection_invoked": False,
            "vm81_authorization_invoked": False,
            "authoritative_semantic_compression_ready": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }
        if self.safety_drift:
            result[self.safety_drift] = True
        return result

    def differentiate(self, request: Pass218I27DifferentiationRequest) -> dict:
        request.validated()
        profile_version = request.manifold_request.perspective_request.perspective_profile.profile_version
        curriculum = request.manifold_request.perspective_request.beat_request.curriculum_identity_hash72
        grounding = h72("I28-GROUNDING", [curriculum, profile_version])
        relations = []
        specs = (
            ("LEXICAL_SYNONYM", "SIMILARITY", 1),
            ("LEXICAL_HYPERNYM", "IMPLICATION", 1),
            ("LEXICAL_ANTONYM", "CONTRADICTION", -1),
        )
        for rank, (relation_type, family, status) in enumerate(specs, start=1):
            relation = {
                "source_id_hash72": h72("I28-SOURCE", rank),
                "target_id_hash72": h72("I28-TARGET", rank),
                "grounded_relation_hash72": h72("I28-GROUNDED", rank),
                "differentiated_relation_hash72": h72(
                    "I28-DIFFERENTIATED", [rank, profile_version]
                ),
                "grounding_identity_hash72": grounding,
                "perspective_order_rank": rank,
                "relation_type": relation_type,
                "relation_family_candidate": None if self.unresolved and rank == 3 else family,
                "relation_family_resolved": not (self.unresolved and rank == 3),
                "differentiation_mode": "FORMAL" if family != "SIMILARITY" else "COMPARATIVE",
                "status": status,
                "exact_strength": {"numerator": 3 + rank, "denominator": 5 + rank},
                "provenance": "I28_TEST_FIXTURE",
                "truth_promotion": False,
                "action_authority_minted": False,
            }
            relations.append(relation)
        result = {
            **self.status(),
            "formal_analogical_typing_invoked": True,
            "formal_analogical_differentiation_hash72": h72(
                "I28-I27-RESULT", profile_version
            ),
            "differentiation_state_hash72": h72("I28-I27-STATE", profile_version),
            "i26_grounded_relational_manifold_hash72": h72("I28-I26", profile_version),
            "i24_narrative_beat_hash72": h72("I28-I24", profile_version),
            "i25_perspective_context_hash72": h72("I28-I25", profile_version),
            "grounding_identity": {
                "grounding_identity_hash72": grounding,
                "curriculum_identity_hash72": curriculum,
                "source_checksum_sha256": "a" * 64,
                "general_english_genesis_mutated": False,
            },
            "differentiated_relations": relations,
            "relation_family_layers": [
                {
                    "relation_family_candidate": "SIMILARITY",
                    "candidate_only": True,
                },
                {
                    "relation_family_candidate": "IMPLICATION",
                    "candidate_only": True,
                },
                {
                    "relation_family_candidate": "CONTRADICTION",
                    "candidate_only": True,
                },
            ],
            "relation_count": len(relations),
            "resolved_relation_count": len(relations) - (1 if self.unresolved else 0),
            "unresolved_relation_count": 1 if self.unresolved else 0,
            "differentiation_complete": not self.unresolved,
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
                    "I28-I27-RECEIPT", profile_version
                )
            },
            "i20_binding_hash72": h72("I28-I20", "binding"),
            "i21_batch_hash72": h72("I28-I21", "batch"),
            "i22_graph_hash72": h72("I28-I22", "graph"),
            "i23_contextual_state_hash72": h72("I28-I23", "state"),
        }
        if self.safety_drift:
            result[self.safety_drift] = True
        return result


def differentiation_request(profile_version: str = "v1") -> Pass218I27DifferentiationRequest:
    beat = Pass218I24BeatRequest(
        tokens=("relation", "transition"),
        context_id="i28 hash216 vm5184 transition fixture",
        curriculum_identity_hash72=h72("I28-CURRICULUM", "fixture"),
        curriculum_position=28,
        source_id="i28-fixture",
        source_checksum_sha256="b" * 64,
        source_authority="REPOSITORY_NATIVE",
        rights_class="REPOSITORY_NATIVE",
        evidence_id="i28-fixture-evidence",
        evidence_type="RELATIONAL_OBSERVATION",
        evidence_epistemic_status="OBSERVED",
        evidence_payload_hash72=h72("I28-EVIDENCE", "fixture"),
        attention_tokens=("relation",),
        top_k=2,
        attention_radius=1,
        max_hydrated_nodes=24,
    ).validated()
    profile = Pass218I25PerspectiveProfile(
        profile_id="i28-test-perspective",
        profile_version=profile_version,
        profile_origin="USER_AUTHORED",
        rules=(),
    ).validated()
    perspective = Pass218I25PerspectiveRequest(
        beat_request=beat,
        perspective_profile=profile,
    ).validated()
    manifold = Pass218I26ManifoldRequest(perspective_request=perspective).validated()
    return Pass218I27DifferentiationRequest(manifold_request=manifold).validated()


def request(profile_version: str = "v1") -> Pass218I28TransitionRequest:
    return Pass218I28TransitionRequest(
        differentiation_request=differentiation_request(profile_version)
    ).validated()


def api_payload() -> dict:
    differentiation = differentiation_request()
    perspective = differentiation.manifold_request.perspective_request
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


def transitioner(control: FakeI27Control | None = None) -> Pass218I28Hash216VM5184Transition:
    return Pass218I28Hash216VM5184Transition(
        control or FakeI27Control(),
        native_bridge=FakeNativeBridge,
    )


def test_i28_constructs_three_segment_hash216_and_native_vm5184_candidate() -> None:
    result = transitioner().construct(request())
    segments = result["pass218_hash216_segments"]
    assert result["pass218_hash216_candidate"] == (
        segments["manifest_curriculum_hash72"]
        + segments["hydrated_transition_state_hash72"]
        + segments["prevalidation_receipt_hash72"]
    )
    assert len(result["pass218_hash216_candidate"]) == 216
    vm = result["vm5184_candidate"]
    assert vm["mapping_version"] == PASS218_I28_VM5184_MAPPING_VERSION
    assert vm["state_bits"] == VM5184_STATE_BITS
    assert vm["cell_count"] == VM5184_CELL_COUNT
    assert len(vm["state_words"]) == 81
    assert vm["populated_relation_cells"] == 3
    assert vm["zero_padded_cells"] == 78
    assert vm["native_abi_canonical_float_fields"] == 0
    assert result["native_vm5184_transition_constructed"] is True
    assert result["hash216_continuation_constructed"] is True
    assert result["hash216_continuation_verified"] is False
    assert result["vm5184_authoritative_projection_invoked"] is False
    assert result["vm81_authorization_invoked"] is False
    assert result["atomic_promotion_invoked"] is False
    assert result["truth_promotion"] is False


def test_i28_exact_replay_and_profile_change_are_distinct() -> None:
    engine = transitioner()
    first = engine.construct(request("v1"))
    replay = engine.construct(request("v1"))
    alternate = engine.construct(request("v2"))
    assert first == replay
    assert first["hash216_vm5184_transition_hash72"] == replay[
        "hash216_vm5184_transition_hash72"
    ]
    assert first["pass218_hash216_candidate"] == replay["pass218_hash216_candidate"]
    assert first["hash216_vm5184_transition_hash72"] != alternate[
        "hash216_vm5184_transition_hash72"
    ]
    assert first["native_continuation_token"]["continuation_root216"] != alternate[
        "native_continuation_token"
    ]["continuation_root216"]


def test_i28_preserves_relation_order_and_exact_candidate_meaning() -> None:
    result = transitioner().construct(request())
    assert all(result["transition_conservation"].values())
    assert result["relation_count"] == 3
    assert result["prevalidation_receipt"]["semantic_transition_validated"] is False
    assert result["prevalidation_receipt"]["atomic_promotion_permitted"] is False
    assert result["native_continuation_token"]["generation"] == 28


def test_i28_rejects_unresolved_i27_and_authority_drift() -> None:
    with pytest.raises(
        Pass218I28TransitionError,
        match="P218_I28_UNRESOLVED_DIFFERENTIATION_BLOCKS_TRANSITION",
    ):
        transitioner(FakeI27Control(unresolved=True)).construct(request())

    for field in (
        "formal_analogical_typing_canonical",
        "hash216_continuation_verified",
        "vm5184_authoritative_projection_invoked",
        "vm81_authorization_invoked",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
    ):
        with pytest.raises(Pass218I28TransitionError, match="P218_I28_I27_SAFETY_DRIFT"):
            transitioner(FakeI27Control(safety_drift=field)).construct(request())


def test_i28_runtime_surface_is_candidate_only_and_browser_safe() -> None:
    app = FastAPI()
    i27 = FakeI27Control()
    control = install_pass218_i28_transition_control(app, i27)
    assert isinstance(control, Pass218I28RuntimeTransitionControl)
    control.transitioner._native_bridge_override = FakeNativeBridge

    with TestClient(app) as client:
        status = client.get(PASS218_I28_STATUS_PATH)
        assert status.status_code == 200
        assert status.json()["atomic_promotion_invoked"] is False

        response = client.post(PASS218_I28_CANDIDATES_PATH, json=api_payload())
        assert response.status_code == 200
        payload = response.json()
        assert payload["hash216_vm5184_transition_status"] == (
            "REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE"
        )
        assert payload["hash216_continuation_verified"] is False
        assert payload["vm81_authorization_invoked"] is False
        assert client.get(PASS218_I28_CANDIDATES_PATH).status_code == 405
        assert client.post(PASS218_I28_STATUS_PATH, json={}).status_code == 405

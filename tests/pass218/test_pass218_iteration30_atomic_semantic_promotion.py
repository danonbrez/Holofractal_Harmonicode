from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_atomic_semantic_promotion_i30 import (
    PASS218_I30_PROMOTE_PATH,
    PASS218_I30_STATUS_PATH,
    Pass218I30RuntimePromotionControl,
    install_pass218_i30_atomic_semantic_promotion_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import (
    PASS218_I30_PENDING_PURGE_STATUS,
    PASS218_I30_TARGET_SCOPE,
    Pass218I30AtomicSemanticPromoter,
    Pass218I30PromotionError,
    Pass218I30PromotionRequest,
    Pass218I30PromotionStateError,
    Pass218I30PromotionValidationError,
)
from hhs_runtime.pass218.hash216_vm5184_validation_i29 import (
    PASS218_I29_VALIDATION_SCHEMA,
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
        return h216("I30-STATE", list(words))

    @staticmethod
    def project_full(words):
        return [
            [int((int(word) >> (channel % 64)) & 0xFFFFFFFF) for word in words]
            for channel in range(32)
        ]

    @staticmethod
    def projection_root(channels):
        return h216("I30-PROJECTION", [list(row) for row in channels])


class FakeLifecycle:
    def __init__(self, ready: bool = True) -> None:
        self.ready = ready
        self.require_count = 0

    def require_ingestion_ready(self) -> None:
        self.require_count += 1
        if not self.ready:
            raise RuntimeError("P218_I30_TEST_WRITER_FENCE_REQUIRED")

    def status(self) -> dict:
        return {
            "ingestion_enabled": self.ready,
            "ownership_writer_authority": self.ready,
        }


class FakeValidationRequest:
    def __init__(self) -> None:
        self.transition_request = SimpleNamespace(differentiation_request=object())

    def validated(self):
        return self


def relation(rank: int, family: str, relation_type: str, status: int) -> dict:
    return {
        "source_id_hash72": h72("I30-SOURCE", rank),
        "target_id_hash72": h72("I30-TARGET", rank),
        "grounded_relation_hash72": h72("I30-GROUNDED", rank),
        "differentiated_relation_hash72": h72("I30-DIFFERENTIATED", rank),
        "grounding_identity_hash72": h72("I30-GROUNDING", "fixture"),
        "perspective_order_rank": rank,
        "relation_type": relation_type,
        "upstream_relation_type": relation_type,
        "relation_family_candidate": family,
        "differentiation_mode": "FORMAL" if family != "SIMILARITY" else "COMPARATIVE",
        "differentiation_basis": "I30_TEST_FIXTURE",
        "status": status,
        "exact_strength": {"numerator": rank + 3, "denominator": rank + 7},
        "provenance": "I30_TEST_FIXTURE",
        "relation_family_resolved": True,
        "formal_relation_type_assigned": family in {"IMPLICATION", "CONTRADICTION"},
        "analogical_relation_type_assigned": False,
        "association_relation_type_assigned": False,
        "similarity_relation_type_assigned": family == "SIMILARITY",
        "symbolization_relation_type_assigned": False,
        "causal_relation_type_assigned": False,
        "counterfactual_relation_type_assigned": False,
        "empirical_observation_relation_type_assigned": False,
        "formal_entailment_verified": False,
        "causality_verified": False,
        "empirical_observation_verified": False,
        "logical_contradiction_verified": False,
        "upstream_relation_type_preserved": True,
        "relation_direction_preserved": True,
        "exact_status_preserved": True,
        "provenance_preserved": True,
        "perspective_order_preserved": True,
        # These lexical hints prove I30 does not retain upstream token-bearing
        # presentation fields in the promoted semantic graph.
        "source_token": "DO_NOT_PERSIST_SOURCE_TOKEN",
        "target_token": "DO_NOT_PERSIST_TARGET_TOKEN",
    }


class FakeI27Control:
    def __init__(self) -> None:
        self.relations = [
            relation(1, "SIMILARITY", "LEXICAL_SYNONYM", 1),
            relation(2, "IMPLICATION", "LEXICAL_HYPERNYM", 1),
            relation(3, "CONTRADICTION", "LEXICAL_ANTONYM", -1),
        ]
        self.result_hash72 = h72("I30-I27-RESULT", "fixture")

    def differentiate(self, request) -> dict:
        return {
            "formal_analogical_differentiation_hash72": self.result_hash72,
            "differentiation_state_hash72": h72("I30-I27-STATE", "fixture"),
            "i26_grounded_relational_manifold_hash72": h72("I30-I26", "fixture"),
            "i24_narrative_beat_hash72": h72("I30-I24", "fixture"),
            "i25_perspective_context_hash72": h72("I30-I25", "fixture"),
            "i20_binding_hash72": h72("I30-I20", "fixture"),
            "i21_batch_hash72": h72("I30-I21", "fixture"),
            "i22_graph_hash72": h72("I30-I22", "fixture"),
            "i23_contextual_state_hash72": h72("I30-I23", "fixture"),
            "grounding_identity": {
                "grounding_identity_hash72": h72("I30-GROUNDING", "fixture"),
                "curriculum_identity_hash72": h72("I30-CURRICULUM", "fixture"),
                "source_checksum_sha256": "a" * 64,
                "general_english_genesis_mutated": False,
            },
            "perspective_profile": {
                "profile_id": "i30-test-perspective",
                "profile_version": "v1",
                "profile_origin": "USER_AUTHORED",
                "accepted_for_organization": True,
                "separately_versioned_from_general_english_genesis": True,
                "general_english_genesis_mutated": False,
                "inferred_rules_require_separate_acceptance": True,
                "perspective_profile_hash72": h72("I30-PROFILE", "v1"),
                "rules": [
                    {
                        "rule_id": "rule-1",
                        "rule_payload_hash72": h72("I30-RULE-PAYLOAD", 1),
                        "perspective_rule_hash72": h72("I30-RULE", 1),
                        "salience_delta": 5,
                        "applied_authority": True,
                        "source_tokens": ["DO_NOT_PERSIST_PROFILE_TOKEN"],
                    }
                ],
            },
            "active_context": {
                "context_id": "fixture-context",
                "attention_tokens": ["DO_NOT_PERSIST_ATTENTION_STREAM"],
                "attention_radius": 1,
            },
            "attention_configuration": {
                "attention_tokens": ["DO_NOT_PERSIST_ATTENTION_STREAM"],
                "attention_radius": 1,
                "max_hydrated_nodes": 16,
                "context_configuration_hash72": h72("I30-CONTEXT", "fixture"),
            },
            "relation_taxonomy": {
                "taxonomy_hash72": h72("I30-TAXONOMY", "fixture"),
                "relation_families": ["SIMILARITY", "IMPLICATION", "CONTRADICTION"],
            },
            "relation_family_layers": [
                {
                    "relation_family_candidate": family,
                    "relation_count": 1,
                    "differentiated_relation_hashes": [self.relations[index]["differentiated_relation_hash72"]],
                    "candidate_only": True,
                }
                for index, family in enumerate(("SIMILARITY", "IMPLICATION", "CONTRADICTION"))
            ],
            "differentiated_relations": self.relations,
            "relation_count": 3,
            "resolved_relation_count": 3,
            "unresolved_relation_count": 0,
            "meaning_conservation": {
                "relation_direction_preserved": True,
                "exact_status_preserved": True,
                "provenance_preserved": True,
                "authorization_not_widened": True,
            },
        }


def expected_words(relations: list[dict]) -> list[int]:
    from hashlib import sha256
    import json

    words = [0] * 81
    for rank, row in enumerate(relations, start=1):
        projection = {
            "mapping_version": "HHS-P218-I28-RELATION-CELL-MAPPING-V1",
            "perspective_order_rank": rank,
            "source_id_hash72": row["source_id_hash72"],
            "target_id_hash72": row["target_id_hash72"],
            "grounded_relation_hash72": row["grounded_relation_hash72"],
            "differentiated_relation_hash72": row["differentiated_relation_hash72"],
            "relation_type": row.get("relation_type"),
            "relation_family_candidate": row.get("relation_family_candidate"),
            "differentiation_mode": row.get("differentiation_mode"),
            "status": row.get("status"),
            "exact_strength": row.get("exact_strength"),
            "provenance": row.get("provenance"),
            "grounding_identity_hash72": row["grounding_identity_hash72"],
        }
        raw = json.dumps(
            projection,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        words[rank - 1] = int.from_bytes(sha256(raw).digest()[:8], "big")
    return words


class FakeI29Control:
    def __init__(self, i27: FakeI27Control) -> None:
        words = expected_words(i27.relations)
        projection = FakeNativeBridge.project_full(words)
        self.validation_hash72 = h72("I30-I29-VALIDATION", "fixture")
        self.validated_hash216 = h216("I30-VALIDATED-HASH216", "fixture")
        self.result = {
            "schema": PASS218_I29_VALIDATION_SCHEMA,
            "hash216_vm5184_validation_status": (
                "VALIDATED_REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE"
            ),
            "hash216_vm5184_validation_hash72": self.validation_hash72,
            "i28_hash216_vm5184_transition_hash72": h72("I30-I28", "fixture"),
            "i27_formal_analogical_differentiation_hash72": i27.result_hash72,
            "pass218_validated_hash216": self.validated_hash216,
            "validation_receipt": {
                "validation_receipt_hash72": h72("I30-I29-RECEIPT", "fixture")
            },
            "semantic_validation_witness": {
                "differentiated_relation_hashes": [
                    row["differentiated_relation_hash72"] for row in i27.relations
                ],
                "semantic_witness_hash72": h72("I30-SEMANTIC-WITNESS", "fixture"),
            },
            "native_validation": {
                "state_root216": FakeNativeBridge.state_root(words),
                "projection_root216": FakeNativeBridge.projection_root(projection),
                "continuation_root216": h216("I30-CONTINUATION", "fixture"),
                "canonical_float_fields": 0,
            },
            "hash216_continuation_verified": True,
            "semantic_transition_validated": True,
            "vm5184_candidate_projection_verified": True,
            "candidate_semantic_binding_verified": True,
            "atomic_promotion_candidate_ready": True,
            "formal_semantic_round_trip_verified": False,
            "atomic_promotion_authorized": False,
            "vm5184_authoritative_projection_invoked": False,
            "vm81_authorization_invoked": False,
            "atomic_promotion_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }

    def validate(self, request) -> dict:
        return self.result


def promotion_request(i29: FakeI29Control, *, sequence: int = 30) -> Pass218I30PromotionRequest:
    return Pass218I30PromotionRequest(
        validation_request=FakeValidationRequest(),
        grantor_authority_hash72=h72("I30-GRANTOR", "fixture"),
        grant_sequence=sequence,
        expected_i29_validation_hash72=i29.validation_hash72,
        expected_validated_hash216=i29.validated_hash216,
        target_scope=PASS218_I30_TARGET_SCOPE,
    ).validated()


def components(tmp_path: Path, *, ready: bool = True):
    i27 = FakeI27Control()
    i29 = FakeI29Control(i27)
    lifecycle = FakeLifecycle(ready)
    promoter = Pass218I30AtomicSemanticPromoter(
        i29,
        i27,
        lifecycle=lifecycle,
        store_root=tmp_path / "semantic-store",
        native_bridge=FakeNativeBridge,
    )
    return i27, i29, lifecycle, promoter


def test_i30_atomic_promotion_round_trip_and_pending_purge(tmp_path: Path) -> None:
    _, i29, lifecycle, promoter = components(tmp_path)
    receipt = promoter.promote(promotion_request(i29))

    assert lifecycle.require_count == 1
    assert receipt["promotion_status"] == PASS218_I30_PENDING_PURGE_STATUS
    assert receipt["candidate_commit_verified"] is True
    assert receipt["prospective_root_verified"] is True
    assert receipt["formal_semantic_round_trip_verified"] is True
    assert receipt["grounded_round_trip_verified"] is True
    assert receipt["perspective_round_trip_verified"] is True
    assert receipt["vm5184_authoritative_projection_invoked"] is True
    assert receipt["vm5184_authoritative_state_committed"] is True
    assert receipt["vm81_authorization_invoked"] is False
    assert receipt["atomic_promotion_authorized"] is True
    assert receipt["atomic_promotion_invoked"] is True
    assert receipt["atomic_manifest_swap"] is True
    assert receipt["failed_partial_promotion_possible"] is False
    assert receipt["purge_status"] == "PENDING_VERBATIM_PURGE"
    assert receipt["verbatim_purge_invoked"] is False
    assert receipt["purge_receipt_issued"] is False
    assert receipt["curriculum_advance_permitted"] is False
    assert receipt["truth_promotion"] is False
    assert receipt["action_authority_minted"] is False
    assert receipt["canonical_learning_commit_invoked"] is False
    assert receipt["model_activation_invoked"] is False
    assert receipt["authoritative_float_weights_created"] is False

    active = promoter.store.active_generation()
    assert active is not None
    promoted = active["promoted_object"]
    serialized = str(promoted)
    assert "DO_NOT_PERSIST_SOURCE_TOKEN" not in serialized
    assert "DO_NOT_PERSIST_TARGET_TOKEN" not in serialized
    assert "DO_NOT_PERSIST_PROFILE_TOKEN" not in serialized
    assert "DO_NOT_PERSIST_ATTENTION_STREAM" not in serialized
    assert promoted["source_text_retained"] is False
    assert promoted["source_token_stream_retained"] is False
    assert promoted["verbatim_corpus_source_retained"] is False

    status = promoter.status()
    assert status["promotion_present"] is True
    assert status["formal_semantic_round_trip_verified"] is True
    assert status["atomic_promotion_invoked"] is True
    assert status["purge_receipt_issued"] is False
    assert status["curriculum_advance_permitted"] is False


def test_i30_exact_replay_is_idempotent_and_durable(tmp_path: Path) -> None:
    i27, i29, lifecycle, promoter = components(tmp_path)
    request = promotion_request(i29)
    first = promoter.promote(request)
    replay = promoter.promote(request)
    assert first == replay

    restarted = Pass218I30AtomicSemanticPromoter(
        i29,
        i27,
        lifecycle=lifecycle,
        store_root=tmp_path / "semantic-store",
        native_bridge=FakeNativeBridge,
    )
    assert restarted.status()["canonical_root_hash72"] == first["target_root_after_hash72"]
    assert restarted.promote(request) == first

    with pytest.raises(
        Pass218I30PromotionStateError,
        match="P218_I30_PREVIOUS_PROMOTION_PENDING_PURGE",
    ):
        restarted.promote(promotion_request(i29, sequence=31))


def test_i30_failure_before_atomic_swap_leaves_canonical_root_unchanged(tmp_path: Path) -> None:
    _, i29, _, promoter = components(tmp_path)
    root_before = promoter.status()["canonical_root_hash72"]
    with pytest.raises(
        Pass218I30PromotionStateError,
        match="P218_I30_INJECTED_FAILURE_BEFORE_ATOMIC_PROMOTION",
    ):
        promoter.promote(promotion_request(i29), fail_before_atomic_swap=True)
    status = promoter.status()
    assert status["promotion_present"] is False
    assert status["canonical_root_hash72"] == root_before
    assert not promoter.store.manifest_path.exists()
    assert list(promoter.store.candidates.glob("candidate-*.json"))


def test_i30_requires_writer_fence_and_exact_authority_binding(tmp_path: Path) -> None:
    _, i29, _, blocked = components(tmp_path / "blocked", ready=False)
    with pytest.raises(Pass218I30PromotionError, match="P218_I30_TEST_WRITER_FENCE_REQUIRED"):
        blocked.promote(promotion_request(i29))

    _, i29_ok, _, promoter = components(tmp_path / "mismatch")
    bad = Pass218I30PromotionRequest(
        validation_request=FakeValidationRequest(),
        grantor_authority_hash72=h72("I30-GRANTOR", "fixture"),
        grant_sequence=30,
        expected_i29_validation_hash72=h72("I30-WRONG-I29", "fixture"),
        expected_validated_hash216=i29_ok.validated_hash216,
        target_scope=PASS218_I30_TARGET_SCOPE,
    ).validated()
    with pytest.raises(
        Pass218I30PromotionValidationError,
        match="P218_I30_EXPECTED_I29_VALIDATION_MISMATCH",
    ):
        promoter.promote(bad)


def test_i30_runtime_os_surface_is_promotion_only(tmp_path: Path) -> None:
    app = FastAPI()
    i27 = FakeI27Control()
    i29 = FakeI29Control(i27)

    class I29Runtime:
        validator = i29

    class I27Runtime:
        differentiator = i27

    lifecycle = FakeLifecycle(True)
    control = install_pass218_i30_atomic_semantic_promotion_control(
        app,
        I29Runtime(),
        I27Runtime(),
        lifecycle,
        state_root=tmp_path,
    )
    assert isinstance(control, Pass218I30RuntimePromotionControl)
    client = TestClient(app)
    response = client.get(PASS218_I30_STATUS_PATH)
    assert response.status_code == 200
    assert response.json()["promotion_present"] is False
    assert client.head(PASS218_I30_STATUS_PATH).status_code == 200

    expected = {"promotion_status": PASS218_I30_PENDING_PURGE_STATUS}
    control.promote = lambda payload: expected
    response = client.post(PASS218_I30_PROMOTE_PATH, json={"test": True})
    assert response.status_code == 200
    assert response.json() == expected
    assert not any(
        "purge" in str(getattr(route, "path", ""))
        for route in app.router.routes
        if str(getattr(route, "path", "")).startswith(
            "/api/runtime/pass218/cognition/atomic-semantic-promotion"
        )
    )

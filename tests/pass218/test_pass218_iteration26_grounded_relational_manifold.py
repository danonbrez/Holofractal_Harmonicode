from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_grounded_manifold_i26 import (
    PASS218_I26_CANDIDATES_PATH,
    PASS218_I26_STATUS_PATH,
    install_pass218_i26_grounded_manifold_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.grounded_manifold_i26 import (
    Pass218I26GroundedManifoldError,
    Pass218I26GroundedRelationalManifold,
    Pass218I26ManifoldRequest,
)
from hhs_runtime.pass218.narrative_beat_i24 import Pass218I24BeatRequest
from hhs_runtime.pass218.perspective_context_i25 import (
    Pass218I25PerspectiveProfile,
    Pass218I25PerspectiveRequest,
    Pass218I25PerspectiveRule,
)


def h72(domain: str, value: object) -> str:
    return hash72_digest({"domain": domain}, value)


_CONSERVATION = {
    "beat_identity_preserved": True,
    "curriculum_identity_preserved": True,
    "source_identity_preserved": True,
    "context_identity_preserved": True,
    "attention_configuration_preserved": True,
    "relation_direction_preserved": True,
    "relation_type_preserved": True,
    "exact_status_preserved": True,
    "epistemic_modality_preserved": True,
    "provenance_preserved": True,
    "curriculum_location_preserved": True,
    "authorization_not_widened": True,
    "validation_status_not_promoted": True,
}


class FakeI25Control:
    def __init__(
        self,
        *,
        safety_drift: str | None = None,
        conservation_drift: str | None = None,
        inferred: bool = False,
    ) -> None:
        self.safety_drift = safety_drift
        self.conservation_drift = conservation_drift
        self.inferred = inferred
        self.calls = 0

    def status(self) -> dict:
        result = {
            "perspective_context_candidate_ready": True,
            "perspective_context_status": "REVISABLE_PERSPECTIVE_CONTEXT_HYDRATION_CANDIDATE",
            "perspective_hydration_canonical": False,
            "grounded_relational_manifold_ready": False,
            "formal_analogical_typing_invoked": False,
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

    def hydrate(self, payload: dict) -> dict:
        self.calls += 1
        version = payload["perspective_profile"]["profile_version"]
        profile_hash = h72("I26-PROFILE", version)
        perspective_state = h72("I26-PERSPECTIVE-STATE", version)
        perspective_context = h72("I26-PERSPECTIVE-CONTEXT", version)
        beat_hash = h72("I26-BEAT", "fixture")
        source = h72("I26-SRC", "king")
        queen = h72("I26-DST", "queen")
        rule_hash = h72("I26-RULE", version)
        conservation = dict(_CONSERVATION)
        if self.conservation_drift:
            conservation[self.conservation_drift] = False
        salience = 0 if self.inferred else 7
        applied = [] if self.inferred else [rule_hash]
        candidate = [rule_hash] if self.inferred else []
        relations = [
            {
                "source_token": "king",
                "target_token": "queen",
                "source_id_hash72": source,
                "target_id_hash72": queen,
                "relation_type": "DISTRIBUTIONAL_NEIGHBOR",
                "status": 1,
                "provenance": "PASS166_EXACT_WORD2VEC_VIA_I20",
                "upstream_hash72": h72("I26-UP", "distributional"),
                "i22_edge_hash72": h72("I26-I22-EDGE", "distributional"),
                "beat_relation_hash72": h72("I26-BEAT-REL", "distributional"),
                "candidate_only": True,
                "relation_type_change_applied": False,
                "epistemic_change_applied": False,
                "truth_promotion": False,
                "exact_strength": {"numerator": 81, "denominator": 100},
                "perspective_profile_hash72": profile_hash,
                "perspective_salience_delta": salience,
                "applied_perspective_rule_hashes": applied,
                "candidate_perspective_rule_hashes": candidate,
                "relation_direction_preserved": True,
                "relation_type_preserved": True,
                "exact_status_preserved": True,
                "provenance_preserved": True,
                "perspective_relation_hash72": h72(
                    "I26-PERSPECTIVE-REL", [version, "distributional"]
                ),
            },
            {
                "source_token": "king",
                "target_token": "queen",
                "source_id_hash72": source,
                "target_id_hash72": queen,
                "relation_type": "COUNTER_EVIDENCE",
                "status": -1,
                "provenance": "REPOSITORY_NATIVE_COUNTER_WITNESS",
                "upstream_hash72": h72("I26-UP", "counter"),
                "i22_edge_hash72": h72("I26-I22-EDGE", "counter"),
                "beat_relation_hash72": h72("I26-BEAT-REL", "counter"),
                "candidate_only": True,
                "relation_type_change_applied": False,
                "epistemic_change_applied": False,
                "truth_promotion": False,
                "perspective_profile_hash72": profile_hash,
                "perspective_salience_delta": 0,
                "applied_perspective_rule_hashes": [],
                "candidate_perspective_rule_hashes": [],
                "relation_direction_preserved": True,
                "relation_type_preserved": True,
                "exact_status_preserved": True,
                "provenance_preserved": True,
                "perspective_relation_hash72": h72(
                    "I26-PERSPECTIVE-REL", [version, "counter"]
                ),
            },
        ]
        result = {
            **self.status(),
            "perspective_context_candidate_ready": True,
            "perspective_hydration_invoked": True,
            "perspective_context_hash72": perspective_context,
            "perspective_state_hash72": perspective_state,
            "i24_narrative_beat_hash72": beat_hash,
            "perspective_profile": {
                "profile_id": payload["perspective_profile"]["profile_id"],
                "profile_version": version,
                "profile_origin": payload["perspective_profile"]["profile_origin"],
                "accepted_for_organization": not self.inferred,
                "rules": [],
                "separately_versioned_from_general_english_genesis": True,
                "general_english_genesis_mutated": False,
                "inferred_rules_require_separate_acceptance": True,
                "perspective_profile_hash72": profile_hash,
            },
            "active_context": {
                "context_id": payload["context_id"],
                "attention_tokens": list(payload["attention_tokens"]),
            },
            "attention_configuration": {
                "attention_tokens": list(payload["attention_tokens"]),
                "attention_radius": payload["attention_radius"],
                "max_hydrated_nodes": payload["max_hydrated_nodes"],
                "allowed_relation_families": list(payload["allowed_relation_families"]),
                "context_configuration_hash72": h72("I26-CONTEXT", payload["context_id"]),
            },
            "perspective_relations": relations,
            "candidate_relation_count": len(relations),
            "accepted_rule_count": 0 if self.inferred else 1,
            "inferred_candidate_rule_count": 1 if self.inferred else 0,
            "meaning_conservation": conservation,
            "validation_receipt": {
                "meaning_conservation_validated": not bool(self.conservation_drift),
                "perspective_validation_receipt_hash72": h72("I26-I25-RECEIPT", version),
            },
            "i20_binding_hash72": h72("I20", "binding"),
            "i21_batch_hash72": h72("I21", "batch"),
            "i22_graph_hash72": h72("I22", "graph"),
            "i23_contextual_state_hash72": h72("I23", "state"),
        }
        if self.safety_drift:
            result[self.safety_drift] = True
        return result


def beat_request() -> Pass218I24BeatRequest:
    return Pass218I24BeatRequest(
        tokens=("king", "queen"),
        context_id="royal succession",
        curriculum_identity_hash72=h72("I26-CURRICULUM", "fixture"),
        curriculum_position=4,
        source_id="fixture-source",
        source_checksum_sha256="a" * 64,
        source_authority="REPOSITORY_NATIVE",
        rights_class="REPOSITORY_NATIVE",
        evidence_id="fixture-evidence",
        evidence_type="RELATIONAL_OBSERVATION",
        evidence_epistemic_status="OBSERVED",
        evidence_payload_hash72=h72("I26-EVIDENCE", "fixture"),
        attention_tokens=("king",),
        top_k=2,
        attention_radius=1,
        max_hydrated_nodes=12,
    ).validated()


def perspective_request(version: str = "v1", origin: str = "USER_AUTHORED") -> Pass218I25PerspectiveRequest:
    rule = Pass218I25PerspectiveRule(
        rule_id="favor-distributional",
        rule_payload_hash72=h72("I26-RULE-PAYLOAD", version),
        salience_delta=7,
        relation_types=("DISTRIBUTIONAL_NEIGHBOR",),
    )
    profile = Pass218I25PerspectiveProfile(
        profile_id="glyphbearer-perspective",
        profile_version=version,
        profile_origin=origin,
        rules=(rule,),
    )
    return Pass218I25PerspectiveRequest(
        beat_request=beat_request(),
        perspective_profile=profile,
    ).validated()


def request(version: str = "v1", origin: str = "USER_AUTHORED") -> Pass218I26ManifoldRequest:
    return Pass218I26ManifoldRequest(
        perspective_request=perspective_request(version, origin),
    ).validated()


def api_payload(version: str = "v1", origin: str = "USER_AUTHORED") -> dict:
    req = perspective_request(version, origin)
    beat = req.beat_request
    profile = req.perspective_profile
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
            "rules": [
                {
                    "rule_id": item.rule_id,
                    "rule_payload_hash72": item.rule_payload_hash72,
                    "salience_delta": item.salience_delta,
                    "relation_types": list(item.relation_types),
                    "source_tokens": list(item.source_tokens),
                    "target_tokens": list(item.target_tokens),
                }
                for item in profile.rules
            ],
        },
    }


def test_i26_constructs_grounded_candidate_without_authority_promotion() -> None:
    result = Pass218I26GroundedRelationalManifold(FakeI25Control()).construct(request())

    assert result["grounded_relational_manifold_candidate_ready"] is True
    assert result["grounding_invoked"] is True
    assert result["grounding_canonical"] is False
    assert result["grounded_relational_manifold_ready"] is False
    assert result["grounded_relational_manifold_promoted"] is False
    assert result["formal_analogical_typing_invoked"] is False
    assert result["hash216_continuation_verified"] is False
    assert result["vm81_authorization_invoked"] is False
    assert result["truth_promotion"] is False
    assert result["action_authority_minted"] is False
    assert result["canonical_learning_commit_invoked"] is False
    assert result["relation_count"] == 2
    assert result["node_count"] == 2
    assert all(result["topology_conservation"].values())


def test_i26_preserves_perspective_order_and_orthogonal_relation_layers() -> None:
    result = Pass218I26GroundedRelationalManifold(FakeI25Control()).construct(request())
    relations = result["manifold_relations"]
    assert [item["perspective_order_rank"] for item in relations] == [1, 2]
    assert relations[0]["relation_type"] == "DISTRIBUTIONAL_NEIGHBOR"
    assert relations[0]["perspective_salience_delta"] == 7
    assert relations[1]["relation_type"] == "COUNTER_EVIDENCE"
    assert relations[1]["status"] == -1
    assert result["relation_layer_count"] == 2
    assert {
        (item["relation_type"], item["provenance"])
        for item in result["relation_layers"]
    } == {
        ("DISTRIBUTIONAL_NEIGHBOR", "PASS166_EXACT_WORD2VEC_VIA_I20"),
        ("COUNTER_EVIDENCE", "REPOSITORY_NATIVE_COUNTER_WITNESS"),
    }


def test_i26_preserves_mixed_polarity_as_unresolved_candidate() -> None:
    result = Pass218I26GroundedRelationalManifold(FakeI25Control()).construct(request())
    assert result["polarity_conflict_candidate_count"] == 1
    conflict = result["polarity_conflict_candidates"][0]
    assert conflict["status_polarities"] == [-1, 1]
    assert conflict["conflict_resolution_invoked"] is False
    assert conflict["truth_resolution_invoked"] is False


def test_i26_replay_is_exact_and_profile_version_changes_identity() -> None:
    control = FakeI25Control()
    manifold = Pass218I26GroundedRelationalManifold(control)
    first = manifold.construct(request("v1"))
    replay = manifold.construct(request("v1"))
    changed = manifold.construct(request("v2"))
    assert first == replay
    assert first["grounded_relational_manifold_hash72"] != changed[
        "grounded_relational_manifold_hash72"
    ]
    assert first["grounding_identity"]["curriculum_identity_hash72"] == changed[
        "grounding_identity"
    ]["curriculum_identity_hash72"]


def test_i26_inferred_perspective_rules_remain_unapplied_in_manifold() -> None:
    result = Pass218I26GroundedRelationalManifold(
        FakeI25Control(inferred=True)
    ).construct(request(origin="INFERRED_CANDIDATE"))
    first = result["manifold_relations"][0]
    assert first["perspective_salience_delta"] == 0
    assert first["applied_perspective_rule_hashes"] == []
    assert first["candidate_perspective_rule_hashes"]
    assert result["truth_promotion"] is False


def test_i26_fails_closed_on_i25_authority_or_conservation_drift() -> None:
    for field in (
        "grounded_relational_manifold_ready",
        "formal_analogical_typing_invoked",
        "hash216_continuation_verified",
        "vm81_authorization_invoked",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
    ):
        with pytest.raises(
            Pass218I26GroundedManifoldError,
            match="P218_I26_I25_SAFETY_DRIFT",
        ):
            Pass218I26GroundedRelationalManifold(
                FakeI25Control(safety_drift=field)
            ).construct(request())

    with pytest.raises(
        Pass218I26GroundedManifoldError,
        match="P218_I26_I25_MEANING_CONSERVATION_INVALID",
    ):
        Pass218I26GroundedRelationalManifold(
            FakeI25Control(conservation_drift="relation_type_preserved")
        ).construct(request())


def test_i26_runtime_surface_is_candidate_only_and_browser_safe() -> None:
    app = FastAPI()
    control = install_pass218_i26_grounded_manifold_control(app, FakeI25Control())
    assert control.status()["grounded_relational_manifold_candidate_ready"] is True

    with TestClient(app) as client:
        status = client.get(PASS218_I26_STATUS_PATH)
        assert status.status_code == 200
        assert status.json()["grounded_relational_manifold_ready"] is False

        response = client.post(PASS218_I26_CANDIDATES_PATH, json=api_payload())
        assert response.status_code == 200
        payload = response.json()
        assert payload["grounded_relational_manifold_status"] == (
            "REVISABLE_GROUNDED_RELATIONAL_MANIFOLD_CANDIDATE"
        )
        assert payload["relation_count"] == 2
        assert payload["formal_analogical_typing_invoked"] is False
        assert payload["truth_promotion"] is False
        assert client.get(PASS218_I26_CANDIDATES_PATH).status_code == 405
        assert client.post(PASS218_I26_STATUS_PATH, json={}).status_code == 405

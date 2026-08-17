from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_perspective_context_i25 import (
    PASS218_I25_CANDIDATES_PATH,
    PASS218_I25_STATUS_PATH,
    install_pass218_i25_perspective_context_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.narrative_beat_i24 import Pass218I24BeatRequest
from hhs_runtime.pass218.perspective_context_i25 import (
    Pass218I25PerspectiveContextError,
    Pass218I25PerspectiveContextHydrator,
    Pass218I25PerspectiveProfile,
    Pass218I25PerspectiveRequest,
    Pass218I25PerspectiveRule,
)


def h72(domain: str, value: object) -> str:
    return hash72_digest({"domain": domain}, value)


class FakeI24Control:
    def __init__(self, *, safety_drift: str | None = None) -> None:
        self.safety_drift = safety_drift
        self.calls = 0
        self.beat_hash72 = h72("I25-TEST-BEAT", {"beat": 1})
        self.beat_id = h72("I25-TEST-BEAT-ID", {"beat": 1})
        self.successor = h72("I25-TEST-SUCCESSOR", {"beat": 1})
        self.context_hash = h72("I25-TEST-CONTEXT", {"context": "royal succession"})
        self.source_hash = h72("I25-TEST-SOURCE", {"source": "fixture"})
        self.evidence_hash = h72("I25-TEST-EVIDENCE", {"evidence": "fixture"})

    def status(self) -> dict:
        result = {
            "narrative_beat_candidate_ready": True,
            "narrative_beat_status": "REVISABLE_NARRATIVE_BEAT_TRANSITION_CANDIDATE",
            "narrative_beat_integration_invoked": False,
            "perspective_hydration_invoked": False,
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

    def assemble(self, payload: dict) -> dict:
        self.calls += 1
        result = {
            **self.status(),
            "narrative_beat_hash72": self.beat_hash72,
            "beat_id": self.beat_id,
            "successor_candidate_root": self.successor,
            "admitted_predecessor_state": False,
            "active_context": {
                "context_id": "royal succession",
                "context_id_hash72": self.context_hash,
                "attention_tokens": ["king"],
                "attention_radius": 1,
                "max_hydrated_nodes": 12,
                "allowed_relation_families": [],
            },
            "attention_configuration": {
                "attention_tokens": ["king"],
                "attention_radius": 1,
                "max_hydrated_nodes": 12,
                "allowed_relation_families": [],
                "context_configuration_hash72": self.context_hash,
            },
            "curriculum_identity": {
                "curriculum_identity_hash72": payload["curriculum_identity_hash72"],
                "curriculum_position": payload["curriculum_position"],
            },
            "source_identity": {
                "source_identity_hash72": self.source_hash,
                "source_id": payload["source_identity"]["source_id"],
            },
            "new_evidence_or_experience": {
                "evidence_descriptor_hash72": self.evidence_hash,
                "declared_epistemic_status": payload["evidence"]["epistemic_status"],
            },
            "candidate_relations": [
                {
                    "source_token": "king",
                    "target_token": "queen",
                    "source_id_hash72": h72("SRC", "king"),
                    "target_id_hash72": h72("DST", "queen"),
                    "relation_type": "DISTRIBUTIONAL_NEIGHBOR",
                    "status": 1,
                    "provenance": "PASS166_EXACT_WORD2VEC_VIA_I20",
                    "upstream_hash72": h72("UP", "king-queen"),
                    "i22_edge_hash72": h72("EDGE", "king-queen"),
                    "beat_relation_hash72": h72("BEAT-REL", "king-queen"),
                    "candidate_only": True,
                    "relation_type_change_applied": False,
                    "epistemic_change_applied": False,
                    "truth_promotion": False,
                    "exact_strength": {"numerator": 81, "denominator": 100},
                },
                {
                    "source_token": "king",
                    "target_token": "man",
                    "source_id_hash72": h72("SRC", "king"),
                    "target_id_hash72": h72("DST", "man"),
                    "relation_type": "LEXICAL_PRIOR",
                    "status": 1,
                    "provenance": "WORDNET_PRIOR",
                    "upstream_hash72": h72("UP", "king-man"),
                    "i22_edge_hash72": h72("EDGE", "king-man"),
                    "beat_relation_hash72": h72("BEAT-REL", "king-man"),
                    "candidate_only": True,
                    "relation_type_change_applied": False,
                    "epistemic_change_applied": False,
                    "truth_promotion": False,
                },
            ],
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
        curriculum_identity_hash72=h72("CURRICULUM", "fixture"),
        curriculum_position=3,
        source_id="fixture-source",
        source_checksum_sha256="a" * 64,
        source_authority="REPOSITORY_NATIVE",
        rights_class="REPOSITORY_NATIVE",
        evidence_id="fixture-evidence",
        evidence_type="RELATIONAL_OBSERVATION",
        evidence_epistemic_status="OBSERVED",
        evidence_payload_hash72=h72("EVIDENCE", "fixture"),
        attention_tokens=("king",),
        top_k=2,
        attention_radius=1,
        max_hydrated_nodes=12,
    ).validated()


def rule(*, rule_id: str, delta: int, relation_type: str = "") -> Pass218I25PerspectiveRule:
    return Pass218I25PerspectiveRule(
        rule_id=rule_id,
        rule_payload_hash72=h72("I25-RULE-PAYLOAD", rule_id),
        salience_delta=delta,
        relation_types=(() if not relation_type else (relation_type,)),
    )


def profile(origin: str = "USER_AUTHORED") -> Pass218I25PerspectiveProfile:
    return Pass218I25PerspectiveProfile(
        profile_id="glyphbearer-perspective",
        profile_version="v1",
        profile_origin=origin,
        rules=(
            rule(rule_id="favor-distributional", delta=7, relation_type="DISTRIBUTIONAL_NEIGHBOR"),
            rule(rule_id="deemphasize-lexical", delta=-3, relation_type="LEXICAL_PRIOR"),
        ),
    ).validated()


def request(origin: str = "USER_AUTHORED") -> Pass218I25PerspectiveRequest:
    return Pass218I25PerspectiveRequest(
        beat_request=beat_request(),
        perspective_profile=profile(origin),
    ).validated()


def api_payload(origin: str = "USER_AUTHORED") -> dict:
    req = beat_request()
    p = profile(origin)
    return {
        "tokens": list(req.tokens),
        "context_id": req.context_id,
        "curriculum_identity_hash72": req.curriculum_identity_hash72,
        "curriculum_position": req.curriculum_position,
        "source_identity": {
            "source_id": req.source_id,
            "source_checksum_sha256": req.source_checksum_sha256,
            "source_authority": req.source_authority,
            "rights_class": req.rights_class,
        },
        "evidence": {
            "evidence_id": req.evidence_id,
            "evidence_type": req.evidence_type,
            "epistemic_status": req.evidence_epistemic_status,
            "payload_hash72": req.evidence_payload_hash72,
        },
        "attention_tokens": list(req.attention_tokens),
        "top_k": req.top_k,
        "attention_radius": req.attention_radius,
        "max_hydrated_nodes": req.max_hydrated_nodes,
        "allowed_relation_families": list(req.allowed_relation_families),
        "perspective_profile": {
            "profile_id": p.profile_id,
            "profile_version": p.profile_version,
            "profile_origin": p.profile_origin,
            "rules": [
                {
                    "rule_id": item.rule_id,
                    "rule_payload_hash72": item.rule_payload_hash72,
                    "salience_delta": item.salience_delta,
                    "relation_types": list(item.relation_types),
                    "source_tokens": list(item.source_tokens),
                    "target_tokens": list(item.target_tokens),
                }
                for item in p.rules
            ],
        },
    }


def test_i25_user_authored_profile_organizes_salience_without_retyping_relation() -> None:
    i24 = FakeI24Control()
    result = Pass218I25PerspectiveContextHydrator(i24).hydrate(request())

    assert result["perspective_context_candidate_ready"] is True
    assert result["perspective_hydration_invoked"] is True
    assert result["perspective_hydration_canonical"] is False
    assert result["perspective_profile"]["accepted_for_organization"] is True
    assert result["perspective_profile"]["separately_versioned_from_general_english_genesis"] is True
    assert result["perspective_profile"]["general_english_genesis_mutated"] is False
    assert result["accepted_rule_count"] == 2
    assert result["inferred_candidate_rule_count"] == 0

    first = result["perspective_relations"][0]
    assert first["relation_type"] == "DISTRIBUTIONAL_NEIGHBOR"
    assert first["status"] == 1
    assert first["perspective_salience_delta"] == 7
    assert first["relation_direction_preserved"] is True
    assert first["relation_type_preserved"] is True
    assert first["exact_status_preserved"] is True
    assert first["truth_promotion"] is False

    assert result["grounded_relational_manifold_ready"] is False
    assert result["formal_analogical_typing_invoked"] is False
    assert result["hash216_continuation_verified"] is False
    assert result["vm81_authorization_invoked"] is False
    assert result["truth_promotion"] is False
    assert result["action_authority_minted"] is False
    assert result["canonical_learning_commit_invoked"] is False


def test_i25_inferred_rules_remain_unapplied_candidates_until_accepted() -> None:
    result = Pass218I25PerspectiveContextHydrator(FakeI24Control()).hydrate(
        request("INFERRED_CANDIDATE")
    )
    assert result["perspective_profile"]["accepted_for_organization"] is False
    assert result["accepted_rule_count"] == 0
    assert result["inferred_candidate_rule_count"] == 2
    for relation in result["perspective_relations"]:
        assert relation["perspective_salience_delta"] == 0
        assert relation["applied_perspective_rule_hashes"] == []
    matched = [
        relation
        for relation in result["perspective_relations"]
        if relation["candidate_perspective_rule_hashes"]
    ]
    assert len(matched) == 2


def test_i25_deterministic_replay_and_profile_version_changes_identity() -> None:
    hydrator = Pass218I25PerspectiveContextHydrator(FakeI24Control())
    first = hydrator.hydrate(request())
    replay = hydrator.hydrate(request())
    assert first == replay

    changed_profile = Pass218I25PerspectiveProfile(
        profile_id="glyphbearer-perspective",
        profile_version="v2",
        profile_origin="USER_AUTHORED",
        rules=profile().rules,
    )
    changed = hydrator.hydrate(
        Pass218I25PerspectiveRequest(beat_request(), changed_profile)
    )
    assert changed["perspective_context_hash72"] != first["perspective_context_hash72"]
    assert changed["i24_narrative_beat_hash72"] == first["i24_narrative_beat_hash72"]


def test_i25_rule_order_is_canonical_and_duplicate_ids_fail_closed() -> None:
    reversed_profile = Pass218I25PerspectiveProfile(
        profile_id="glyphbearer-perspective",
        profile_version="v1",
        profile_origin="USER_AUTHORED",
        rules=tuple(reversed(profile().rules)),
    )
    hydrator = Pass218I25PerspectiveContextHydrator(FakeI24Control())
    assert hydrator.hydrate(
        Pass218I25PerspectiveRequest(beat_request(), reversed_profile)
    )["perspective_context_hash72"] == hydrator.hydrate(request())[
        "perspective_context_hash72"
    ]

    duplicate = Pass218I25PerspectiveProfile(
        profile_id="p",
        profile_version="v1",
        profile_origin="USER_AUTHORED",
        rules=(rule(rule_id="same", delta=1), rule(rule_id="same", delta=2)),
    )
    with pytest.raises(
        Pass218I25PerspectiveContextError,
        match="P218_I25_DUPLICATE_RULE_ID",
    ):
        duplicate.validated()


def test_i25_fails_closed_on_i24_authority_drift() -> None:
    for field in (
        "grounded_relational_manifold_ready",
        "hash216_continuation_verified",
        "vm81_authorization_invoked",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
    ):
        hydrator = Pass218I25PerspectiveContextHydrator(
            FakeI24Control(safety_drift=field)
        )
        with pytest.raises(
            Pass218I25PerspectiveContextError,
            match="P218_I25_I24_SAFETY_DRIFT",
        ):
            hydrator.hydrate(request())


def test_i25_runtime_surface_exposes_candidate_only_perspective_hydration() -> None:
    app = FastAPI()
    control = install_pass218_i25_perspective_context_control(app, FakeI24Control())
    assert control.status()["perspective_context_candidate_ready"] is True

    with TestClient(app) as client:
        status = client.get(PASS218_I25_STATUS_PATH)
        assert status.status_code == 200
        assert status.json()["grounded_relational_manifold_ready"] is False

        response = client.post(PASS218_I25_CANDIDATES_PATH, json=api_payload())
        assert response.status_code == 200
        payload = response.json()
        assert payload["perspective_profile"]["profile_origin"] == "USER_AUTHORED"
        assert payload["perspective_relations"][0]["perspective_salience_delta"] == 7
        assert payload["truth_promotion"] is False
        assert client.get(PASS218_I25_CANDIDATES_PATH).status_code == 405
        assert client.post(PASS218_I25_STATUS_PATH, json={}).status_code == 405


def test_i25_runtime_rejects_unversioned_or_unsupported_profile() -> None:
    app = FastAPI()
    install_pass218_i25_perspective_context_control(app, FakeI24Control())
    with TestClient(app) as client:
        missing_version = api_payload()
        del missing_version["perspective_profile"]["profile_version"]
        response = client.post(PASS218_I25_CANDIDATES_PATH, json=missing_version)
        assert response.status_code == 409
        assert "P218_I25_PROFILE_VERSION_STRING_REQUIRED" in response.json()["detail"]

        unsupported = api_payload()
        unsupported["perspective_profile"]["profile_origin"] = "MODEL_ASSUMED"
        response = client.post(PASS218_I25_CANDIDATES_PATH, json=unsupported)
        assert response.status_code == 409
        assert "P218_I25_PROFILE_ORIGIN_UNSUPPORTED" in response.json()["detail"]

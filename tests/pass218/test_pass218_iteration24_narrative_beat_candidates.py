from __future__ import annotations

from hashlib import sha256
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_narrative_beat_i24 import (
    PASS218_I24_CANDIDATES_PATH,
    PASS218_I24_STATUS_PATH,
    install_pass218_i24_narrative_beat_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.narrative_beat_i24 import (
    Pass218I24BeatRequest,
    Pass218I24NarrativeBeatAssembler,
    Pass218I24NarrativeBeatError,
)


def _h72(domain: str, value: object) -> str:
    return hash72_digest({"domain": domain}, value)


def _node(lexeme: str) -> dict:
    distinction = _h72("I24-TEST-DISTINCTION", {"lexeme": lexeme})
    body = {
        "lexeme": lexeme,
        "distinction_id_hash72": distinction,
        "revisable_candidate": True,
    }
    return {
        **body,
        "node_hash72": _h72("I24-TEST-NODE", body),
        "context_distance": 0 if lexeme == "alpha" else 1,
    }


def _edge(source: str, target: str, status: int, suffix: str) -> dict:
    body = {
        "source_token": source,
        "target_token": target,
        "source_id_hash72": _h72("I24-TEST-DISTINCTION", {"lexeme": source}),
        "target_id_hash72": _h72("I24-TEST-DISTINCTION", {"lexeme": target}),
        "relation_type": "LEXICAL_TEST",
        "status": status,
        "provenance": "I24_TEST_REVISABLE_PRIOR",
        "upstream_hash72": _h72("I24-TEST-UPSTREAM", {"suffix": suffix}),
        "revisable_candidate": True,
        "empirical_truth_authority": False,
        "action_authority": False,
        "canonical_learning_commit": False,
    }
    return {**body, "edge_hash72": _h72("I24-TEST-EDGE", body)}


class FakeI23Control:
    def __init__(self) -> None:
        self.binding_hash72 = _h72("I24-TEST-I20", {"binding": 24})
        self.asset_hash72 = _h72("I24-TEST-ASSET", {"wordnet": 24})
        self.safety_drift = False

    def status(self) -> dict:
        return {
            "contextual_state_candidate_ready": True,
            "contextual_state_status": "REVISABLE_CONTEXTUAL_STATE_CANDIDATE",
            "contextual_hydration_candidate_ready": True,
            "i20_binding_hash72": self.binding_hash72,
            "wordnet_asset_manifest_hash72": self.asset_hash72,
            "narrative_beat_integration_invoked": self.safety_drift,
            "perspective_hydration_invoked": False,
            "grounded_relational_manifold_ready": False,
            "formal_analogical_typing_invoked": False,
            "authoritative_semantic_compression_ready": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }

    def hydrate(self, payload: dict) -> dict:
        tokens = sorted(set(str(item).strip().lower() for item in payload["tokens"]))
        attention = sorted(
            set(str(item).strip().lower() for item in payload.get("attention_tokens", []))
        ) or tokens
        context_config = {
            "context_id": str(payload["context_id"]).strip(),
            "context_id_hash72": _h72(
                "I24-TEST-CONTEXT-ID",
                {"context_id": str(payload["context_id"]).strip()},
            ),
            "attention_tokens": attention,
            "attention_radius": int(payload.get("attention_radius", 1)),
            "max_hydrated_nodes": int(payload.get("max_hydrated_nodes", 24)),
            "allowed_relation_families": sorted(
                set(payload.get("allowed_relation_families", []))
            ),
            "traversal_semantics": "BIDIRECTIONAL_DISCOVERY_DIRECTION_PRESERVED",
        }
        config_hash72 = _h72("I24-TEST-CONTEXT-CONFIG", context_config)
        nodes = [_node("alpha"), _node("beta"), _node("gamma")]
        edges = [
            _edge("alpha", "beta", 1, "support"),
            _edge("alpha", "beta", -1, "counter"),
            _edge("beta", "gamma", 1, "chain"),
        ]
        participation = []
        for node in nodes:
            lexeme = node["lexeme"]
            body = {
                "lexeme": lexeme,
                "distinction_id_hash72": node["distinction_id_hash72"],
                "stored_addressable": True,
                "retrieved": True,
                "hydrated": True,
                "attention_active": lexeme in attention,
                "candidate_influential": True,
                "validated": False,
                "promoted": False,
            }
            body["participation_hash72"] = _h72("I24-TEST-PARTICIPATION", body)
            participation.append(body)
        state_body = {
            "context_configuration_hash72": config_hash72,
            "edge_hashes": [edge["edge_hash72"] for edge in edges],
            "attention": attention,
        }
        state_hash72 = _h72("I24-TEST-I23-STATE", state_body)
        return {
            "contextual_state_status": "REVISABLE_CONTEXTUAL_STATE_CANDIDATE",
            "contextual_hydration_candidate_ready": True,
            "contextual_state_hash72": state_hash72,
            "context_configuration": context_config,
            "context_configuration_hash72": config_hash72,
            "hydrated_nodes": nodes,
            "hydrated_edges": edges,
            "participation": participation,
            "retrieved_node_count": len(nodes),
            "hydrated_node_count": len(nodes),
            "hydrated_edge_count": len(edges),
            "attention_active_count": sum(1 for item in participation if item["attention_active"]),
            "candidate_influential_count": len(participation),
            "i20_binding_hash72": self.binding_hash72,
            "i21_batch_hash72": _h72("I24-TEST-I21", {"batch": tokens}),
            "i22_graph_hash72": _h72("I24-TEST-I22", {"graph": tokens}),
            "wordnet_asset_manifest_hash72": self.asset_hash72,
            "narrative_beat_integration_invoked": False,
            "perspective_hydration_invoked": False,
            "grounded_relational_manifold_ready": False,
            "formal_analogical_typing_invoked": False,
            "authoritative_semantic_compression_ready": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }


def _request(**overrides: object) -> Pass218I24BeatRequest:
    values = {
        "tokens": ("beta", "alpha", "alpha"),
        "context_id": "test-context",
        "curriculum_identity_hash72": _h72("I24-TEST-CURRICULUM", {"id": 24}),
        "curriculum_position": 3,
        "source_id": "repository-native-i24-test",
        "source_checksum_sha256": sha256(b"repository-native-i24-test").hexdigest(),
        "source_authority": "REPOSITORY_NATIVE_TEST_AUTHORITY",
        "rights_class": "REPOSITORY_NATIVE_TEST_AUTHORITY",
        "evidence_id": "event-24",
        "evidence_type": "OBSERVATION",
        "evidence_epistemic_status": "OBSERVED",
        "evidence_payload_hash72": _h72("I24-TEST-EVIDENCE", {"event": 24}),
        "attention_tokens": ("alpha",),
        "top_k": 4,
        "attention_radius": 1,
        "max_hydrated_nodes": 8,
        "allowed_relation_families": ("LEXICAL_TEST",),
    }
    values.update(overrides)
    return Pass218I24BeatRequest(**values)


def _payload(**overrides: object) -> dict:
    request = _request(**overrides).validated()
    payload = request.i23_payload()
    payload.update(
        {
            "curriculum_identity_hash72": request.curriculum_identity_hash72,
            "curriculum_position": request.curriculum_position,
            "source_identity": {
                "source_id": request.source_id,
                "source_checksum_sha256": request.source_checksum_sha256,
                "source_authority": request.source_authority,
                "rights_class": request.rights_class,
            },
            "evidence": {
                "evidence_id": request.evidence_id,
                "evidence_type": request.evidence_type,
                "epistemic_status": request.evidence_epistemic_status,
                "payload_hash72": request.evidence_payload_hash72,
            },
        }
    )
    return payload


def test_i24_deterministic_replay_and_authority_separation() -> None:
    control = FakeI23Control()
    assembler = Pass218I24NarrativeBeatAssembler(control)
    first = assembler.assemble(_request())
    replay = assembler.assemble(
        _request(tokens=("alpha", "beta"), allowed_relation_families=("lexical_test",))
    )

    assert first["narrative_beat_hash72"] == replay["narrative_beat_hash72"]
    assert first["beat_id"] == replay["beat_id"]
    assert first["successor_candidate_root"] == replay["successor_candidate_root"]
    assert first["predecessor_root_semantics"] == "I23_REVISABLE_CONTEXTUAL_STATE_CANDIDATE"
    assert first["admitted_predecessor_state"] is False
    assert first["narrative_beat_status"] == "REVISABLE_NARRATIVE_BEAT_TRANSITION_CANDIDATE"
    assert first["narrative_beat_candidate_ready"] is True
    assert first["optional_narrative_projection"] is None
    assert first["natural_language_projection_generated"] is False
    assert first["hash216_continuation_identity"] is None
    assert first["hash216_continuation_verified"] is False
    assert first["vm81_authorization_invoked"] is False
    assert first["perspective_hydration_invoked"] is False
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["canonical_learning_commit_invoked"] is False


def test_i24_context_or_evidence_change_changes_transition_identity() -> None:
    assembler = Pass218I24NarrativeBeatAssembler(FakeI23Control())
    baseline = assembler.assemble(_request())
    changed_context = assembler.assemble(_request(context_id="different-context"))
    changed_evidence = assembler.assemble(
        _request(
            evidence_payload_hash72=_h72(
                "I24-TEST-EVIDENCE",
                {"event": 25},
            )
        )
    )
    assert baseline["narrative_beat_hash72"] != changed_context["narrative_beat_hash72"]
    assert baseline["narrative_beat_hash72"] != changed_evidence["narrative_beat_hash72"]
    assert baseline["successor_candidate_root"] != changed_evidence["successor_candidate_root"]


def test_i24_mixed_polarity_is_diagnostic_candidate_not_applied_change() -> None:
    result = Pass218I24NarrativeBeatAssembler(FakeI23Control()).assemble(_request())
    assert len(result["contradiction_changes"]) == 1
    contradiction = result["contradiction_changes"][0]
    assert contradiction["status_polarities"] == [-1, 1]
    assert contradiction["candidate_contradiction_state"] == "MIXED_POLARITY_PRESENT"
    assert contradiction["authoritative_contradiction_change_applied"] is False
    assert result["relation_type_changes"] == []
    assert result["epistemic_status_changes"] == []
    assert result["salience_changes"] == []
    assert result["contradiction_change_application_invoked"] is False


def test_i24_rejects_invalid_identity_material() -> None:
    with pytest.raises(Pass218I24NarrativeBeatError, match="P218_I24_CURRICULUM_IDENTITY_HASH72_INVALID"):
        _request(curriculum_identity_hash72="not-hash72").validated()
    with pytest.raises(Pass218I24NarrativeBeatError, match="P218_I24_SOURCE_SHA256_INVALID"):
        _request(source_checksum_sha256="00").validated()
    with pytest.raises(Pass218I24NarrativeBeatError, match="P218_I24_EPISTEMIC_STATUS_UNSUPPORTED"):
        _request(evidence_epistemic_status="CERTAIN_BECAUSE_MODEL_SAID_SO").validated()


def test_i24_fails_closed_on_i23_safety_drift() -> None:
    control = FakeI23Control()
    control.safety_drift = True
    assembler = Pass218I24NarrativeBeatAssembler(control)
    with pytest.raises(Pass218I24NarrativeBeatError, match="P218_I24_I23_SAFETY_DRIFT"):
        assembler.assemble(_request())
    assert assembler.status()["narrative_beat_candidate_ready"] is False


def test_i24_retains_nonverbatim_identity_only_evidence() -> None:
    result = Pass218I24NarrativeBeatAssembler(FakeI23Control()).assemble(_request())
    evidence = result["new_evidence_or_experience"]
    assert evidence["retention_semantics"] == "NONVERBATIM_IDENTITY_ONLY"
    assert "text" not in evidence
    assert "raw" not in evidence
    assert "tokens" not in evidence
    encoded = json.dumps(result, sort_keys=True)
    assert "verbatim_source_retained\": true" not in encoded.lower()


def test_i24_runtime_routes_are_bounded_and_idempotent() -> None:
    app = FastAPI()
    control = FakeI23Control()
    first = install_pass218_i24_narrative_beat_control(app, control)
    second = install_pass218_i24_narrative_beat_control(app, control)
    assert first is second

    client = TestClient(app)
    status = client.get(PASS218_I24_STATUS_PATH)
    assert status.status_code == 200
    assert status.json()["narrative_beat_candidate_ready"] is True

    response = client.post(PASS218_I24_CANDIDATES_PATH, json=_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["narrative_beat_candidate_ready"] is True
    assert body["truth_promotion"] is False

    invalid = _payload()
    invalid["evidence"] = {"evidence_id": "missing-fields"}
    rejected = client.post(PASS218_I24_CANDIDATES_PATH, json=invalid)
    assert rejected.status_code == 409

    paths = [str(getattr(route, "path", "")) for route in app.router.routes]
    assert paths.count(PASS218_I24_STATUS_PATH) == 1
    assert paths.count(PASS218_I24_CANDIDATES_PATH) == 1

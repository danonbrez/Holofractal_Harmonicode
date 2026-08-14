from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_contextual_state_i23 import (
    PASS218_I23_CANDIDATES_PATH,
    PASS218_I23_STATUS_PATH,
    install_pass218_i23_contextual_state_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.contextual_state_i23 import (
    Pass218I23ContextQuery,
    Pass218I23ContextualStateError,
    Pass218I23ContextualStateHydrator,
)


def _node(lexeme: str) -> dict:
    body = {
        "lexeme": lexeme,
        "distinction_id_hash72": hash72_digest(
            {"domain": "HHS-P218-I23-TEST-DISTINCTION"},
            {"lexeme": lexeme},
        ),
        "revisable_candidate": True,
    }
    body["node_hash72"] = hash72_digest(
        {"domain": "HHS-P218-I23-TEST-NODE"},
        body,
    )
    return body


def _edge(source: dict, target: dict, relation_type: str, status: int) -> dict:
    body = {
        "source_token": source["lexeme"],
        "target_token": target["lexeme"],
        "source_id_hash72": source["distinction_id_hash72"],
        "target_id_hash72": target["distinction_id_hash72"],
        "relation_type": relation_type,
        "status": status,
        "provenance": "I23_TEST_I22_GRAPH",
        "upstream_hash72": hash72_digest(
            {"domain": "HHS-P218-I23-TEST-UPSTREAM"},
            {
                "source": source["lexeme"],
                "target": target["lexeme"],
                "relation_type": relation_type,
            },
        ),
        "revisable_candidate": True,
        "empirical_truth_authority": False,
        "action_authority": False,
        "canonical_learning_commit": False,
    }
    body["edge_hash72"] = hash72_digest(
        {"domain": "HHS-P218-I23-TEST-EDGE"},
        body,
    )
    return body


class FakeI22Control:
    def __init__(self) -> None:
        nodes = {name: _node(name) for name in ("king", "queen", "monarch", "woman", "tyrant")}
        edges = [
            _edge(nodes["king"], nodes["queen"], "LEXICAL_SYNONYM", 1),
            _edge(nodes["king"], nodes["monarch"], "LEXICAL_HYPERNYM", 1),
            _edge(nodes["queen"], nodes["woman"], "DISTRIBUTIONAL_NEIGHBOR", 1),
            _edge(nodes["king"], nodes["tyrant"], "LEXICAL_ANTONYM", -1),
        ]
        edges.sort(
            key=lambda item: (
                item["source_id_hash72"],
                item["relation_type"],
                item["target_id_hash72"],
                item["edge_hash72"],
            )
        )
        graph_body = {
            "semantic_graph_status": "REVISABLE_SEMANTIC_GRAPH_CANDIDATE",
            "candidate_semantic_compression_input_ready": True,
            "authoritative_semantic_compression_ready": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
            "i20_binding_hash72": hash72_digest(
                {"domain": "HHS-P218-I23-TEST-I20"},
                {"id": "binding"},
            ),
            "i21_batch_hash72": hash72_digest(
                {"domain": "HHS-P218-I23-TEST-I21"},
                {"id": "batch"},
            ),
            "wordnet_asset_manifest_hash72": hash72_digest(
                {"domain": "HHS-P218-I23-TEST-WORDNET"},
                {"id": "assets"},
            ),
            "nodes": sorted(nodes.values(), key=lambda item: item["distinction_id_hash72"]),
            "edges": edges,
        }
        self.graph = {
            **graph_body,
            "graph_hash72": hash72_digest(
                {"domain": "HHS-P218-I23-TEST-I22-GRAPH"},
                graph_body,
            ),
        }
        self.status_payload = {
            "semantic_graph_candidate_ready": True,
            "semantic_graph_status": "REVISABLE_SEMANTIC_GRAPH_CANDIDATE",
            "candidate_semantic_compression_input_ready": True,
            "authoritative_semantic_compression_ready": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
            "i20_binding_hash72": self.graph["i20_binding_hash72"],
            "wordnet_asset_manifest_hash72": self.graph["wordnet_asset_manifest_hash72"],
        }

    def status(self) -> dict:
        return deepcopy(self.status_payload)

    def assemble(self, payload: dict) -> dict:
        assert payload["tokens"]
        assert 1 <= int(payload["top_k"]) <= 72
        return deepcopy(self.graph)


def _query(**overrides) -> Pass218I23ContextQuery:
    base = {
        "tokens": ("king", "queen"),
        "context_id": "court succession",
        "attention_tokens": ("king",),
        "top_k": 4,
        "attention_radius": 1,
        "max_hydrated_nodes": 4,
        "allowed_relation_families": (),
    }
    base.update(overrides)
    return Pass218I23ContextQuery(**base)


def test_i23_replay_is_byte_structurally_deterministic() -> None:
    hydrator = Pass218I23ContextualStateHydrator(FakeI22Control())
    first = hydrator.hydrate(_query())
    replay = hydrator.hydrate(
        _query(tokens=("queen", "king", "king"), attention_tokens=("king",))
    )
    assert first == replay
    assert first["contextual_state_hash72"] == replay["contextual_state_hash72"]
    assert first["contextual_state_status"] == "REVISABLE_CONTEXTUAL_STATE_CANDIDATE"


def test_i23_attention_changes_local_hydration_without_deleting_global_addressability() -> None:
    hydrator = Pass218I23ContextualStateHydrator(FakeI22Control())
    king = hydrator.hydrate(_query(attention_tokens=("king",), max_hydrated_nodes=5))
    queen = hydrator.hydrate(_query(attention_tokens=("queen",), max_hydrated_nodes=5))
    king_lexemes = {node["lexeme"] for node in king["hydrated_nodes"]}
    queen_lexemes = {node["lexeme"] for node in queen["hydrated_nodes"]}
    assert king_lexemes != queen_lexemes
    assert "monarch" in king_lexemes
    assert "woman" in queen_lexemes
    assert all(item["stored_addressable"] for item in queen["participation"])
    assert all(item["retrieved"] for item in queen["participation"])
    assert any(not item["hydrated"] for item in queen["participation"])


def test_i23_relation_family_filter_and_node_budget_are_exact() -> None:
    hydrator = Pass218I23ContextualStateHydrator(FakeI22Control())
    state = hydrator.hydrate(
        _query(
            allowed_relation_families=("LEXICAL_SYNONYM",),
            attention_radius=2,
            max_hydrated_nodes=2,
        )
    )
    assert state["hydrated_node_count"] == 2
    assert state["hydrated_edge_count"] == 1
    assert {edge["relation_type"] for edge in state["hydrated_edges"]} == {
        "LEXICAL_SYNONYM"
    }


def test_i23_participation_states_remain_separate_and_unpromoted() -> None:
    hydrator = Pass218I23ContextualStateHydrator(FakeI22Control())
    state = hydrator.hydrate(_query(attention_radius=0, max_hydrated_nodes=1))
    by_lexeme = {item["lexeme"]: item for item in state["participation"]}
    assert by_lexeme["king"]["attention_active"] is True
    assert by_lexeme["king"]["hydrated"] is True
    assert by_lexeme["king"]["candidate_influential"] is False
    assert by_lexeme["woman"]["retrieved"] is True
    assert by_lexeme["woman"]["hydrated"] is False
    assert all(item["validated"] is False for item in state["participation"])
    assert all(item["promoted"] is False for item in state["participation"])


def test_i23_fails_closed_on_i22_authority_drift() -> None:
    i22 = FakeI22Control()
    i22.status_payload["truth_promotion"] = True
    hydrator = Pass218I23ContextualStateHydrator(i22)
    with pytest.raises(
        Pass218I23ContextualStateError,
        match="P218_I23_I22_SAFETY_DRIFT",
    ):
        hydrator.hydrate(_query())


def test_i23_rejects_attention_seed_outside_retrieved_graph() -> None:
    hydrator = Pass218I23ContextualStateHydrator(FakeI22Control())
    with pytest.raises(
        Pass218I23ContextualStateError,
        match="P218_I23_ATTENTION_SEED_NOT_IN_GRAPH",
    ):
        hydrator.hydrate(_query(attention_tokens=("absent-token",)))


def test_i23_runtime_surface_is_candidate_only() -> None:
    app = FastAPI()
    control = install_pass218_i23_contextual_state_control(app, FakeI22Control())
    client = TestClient(app)
    status = client.get(PASS218_I23_STATUS_PATH)
    assert status.status_code == 200
    assert status.json()["contextual_state_candidate_ready"] is True

    response = client.post(
        PASS218_I23_CANDIDATES_PATH,
        json={
            "tokens": ["queen", "king"],
            "context_id": "court succession",
            "attention_tokens": ["king"],
            "top_k": 4,
            "attention_radius": 1,
            "max_hydrated_nodes": 4,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["contextual_hydration_candidate_ready"] is True
    assert payload["narrative_beat_integration_invoked"] is False
    assert payload["perspective_hydration_invoked"] is False
    assert payload["grounded_relational_manifold_ready"] is False
    assert payload["formal_analogical_typing_invoked"] is False
    assert payload["truth_promotion"] is False
    assert payload["action_authority_minted"] is False
    assert payload["canonical_learning_commit_invoked"] is False
    assert control.status()["contextual_state_count"] == 1

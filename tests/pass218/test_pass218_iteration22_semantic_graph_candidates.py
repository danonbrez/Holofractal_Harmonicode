from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_semantic_graph_i22 import (
    PASS218_I22_CANDIDATES_PATH,
    PASS218_I22_STATUS_PATH,
    install_pass218_i22_semantic_graph_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.semantic_graph_i22 import (
    Pass218I22GraphQuery,
    Pass218I22SemanticGraphCandidateAssembler,
    Pass218I22SemanticGraphError,
    Pass218I22WordNetPriorProvider,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _hash(domain: str, value: object) -> str:
    return hash72_digest({"domain": domain}, value)


class FakeI21Control:
    def __init__(self, *, ready: bool = True, truth_promotion: bool = False) -> None:
        self.ready = ready
        self.truth_promotion = truth_promotion
        self.binding_hash72 = _hash("HHS-P218-I22-TEST-I20", "binding")
        self.calls: list[tuple[tuple[str, ...], int]] = []

    def status(self) -> dict:
        return {
            "candidate_consumption_ready": self.ready,
            "i20_binding_hash72": self.binding_hash72,
            "candidate_semantics": "REVISABLE_RELATIONAL_EVIDENCE",
            "truth_promotion": self.truth_promotion,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }

    def consume(self, payload: dict) -> dict:
        tokens = tuple(payload["tokens"])
        top_k = int(payload["top_k"])
        self.calls.append((tokens, top_k))
        results = []
        for token in tokens:
            target = "queen" if token == "king" else "king"
            candidate = {
                "source_token": token,
                "rank": 1,
                "target": target,
                "relation_type": "DISTRIBUTIONAL_NEIGHBOR",
                "status": 1,
                "similarity_squared": {"numerator": 81, "denominator": 100},
                "vector_identity": "fixture-vector-" + target,
                "provenance": "PASS166_EXACT_WORD2VEC_VIA_I20",
                "revisable_candidate": True,
                "empirical_truth_authority": False,
                "action_authority": False,
                "canonical_learning_commit": False,
            }
            candidate["candidate_hash72"] = _hash(
                "HHS-P218-I22-TEST-I21-CANDIDATE",
                candidate,
            )
            results.append(
                {
                    "source_token": token,
                    "candidate_count": 1,
                    "candidates": [candidate][:top_k],
                }
            )
        body = {
            "i20_binding_hash72": self.binding_hash72,
            "candidate_semantics": "REVISABLE_RELATIONAL_EVIDENCE",
            "query": {"tokens": list(tokens), "top_k": top_k},
            "results": results,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }
        return {
            **body,
            "batch_hash72": _hash("HHS-P218-I22-TEST-I21-BATCH", body),
        }


class FakeLexicalProvider:
    def __init__(self, *, mixed: bool = False) -> None:
        self.mixed = mixed
        self.asset_hash72 = _hash("HHS-P218-I22-TEST-WORDNET-ASSET", "asset")

    def status(self) -> dict:
        return {
            "lexical_prior_ready": True,
            "asset_manifest_hash72": self.asset_hash72,
            "load_error_code": None,
        }

    def snapshot(self, tokens: tuple[str, ...]) -> dict:
        relations = []
        if "king" in tokens:
            relation = {
                "source_token": "king",
                "target_token": "queen",
                "relation_type": "LEXICAL_SYNONYM",
                "status": 1,
                "provenance": "WORDNET_REVISABLE_PRIOR",
                "revisable_candidate": True,
                "empirical_truth_authority": False,
            }
            relation["lexical_prior_hash72"] = _hash(
                "HHS-P218-I22-TEST-LEXICAL",
                relation,
            )
            relations.append(relation)
            if self.mixed:
                opposite = {
                    "source_token": "king",
                    "target_token": "queen",
                    "relation_type": "LEXICAL_ANTONYM",
                    "status": -1,
                    "provenance": "WORDNET_REVISABLE_PRIOR",
                    "revisable_candidate": True,
                    "empirical_truth_authority": False,
                }
                opposite["lexical_prior_hash72"] = _hash(
                    "HHS-P218-I22-TEST-LEXICAL",
                    opposite,
                )
                relations.append(opposite)
        return {
            "schema": "HHS-P218-I22-WORDNET-SNAPSHOT-V1",
            "asset_manifest_hash72": self.asset_hash72,
            "relations": relations,
            "relation_count": len(relations),
            "definitions_retained": False,
            "examples_retained": False,
            "empirical_truth_authority": False,
        }


def test_i22_assembles_revisable_semantic_graph_from_lexical_and_i21_evidence() -> None:
    i21 = FakeI21Control()
    assembler = Pass218I22SemanticGraphCandidateAssembler(
        i21,
        FakeLexicalProvider(),
    )
    graph = assembler.assemble(
        Pass218I22GraphQuery(tokens=("king",), top_k=2)
    )

    assert graph["semantic_graph_status"] == "REVISABLE_SEMANTIC_GRAPH_CANDIDATE"
    assert graph["candidate_semantic_compression_input_ready"] is True
    assert graph["authoritative_semantic_compression_ready"] is False
    assert graph["truth_promotion"] is False
    assert graph["action_authority_minted"] is False
    assert graph["canonical_learning_commit_invoked"] is False
    assert graph["model_activation_invoked"] is False
    assert graph["verbatim_corpus_source_retained"] is False
    assert graph["authoritative_float_weights_created"] is False
    assert graph["i20_binding_hash72"] == i21.binding_hash72
    assert {node["lexeme"] for node in graph["nodes"]} == {"king", "queen"}
    assert {edge["relation_type"] for edge in graph["edges"]} == {
        "LEXICAL_SYNONYM",
        "DISTRIBUTIONAL_NEIGHBOR",
    }
    distributional = next(
        edge for edge in graph["edges"]
        if edge["relation_type"] == "DISTRIBUTIONAL_NEIGHBOR"
    )
    assert distributional["exact_strength"] == {"numerator": 81, "denominator": 100}
    assert validate_hash72(graph["graph_hash72"])


def test_i22_graph_identity_is_order_and_duplicate_stable() -> None:
    assembler = Pass218I22SemanticGraphCandidateAssembler(
        FakeI21Control(),
        FakeLexicalProvider(),
    )
    first = assembler.assemble(
        Pass218I22GraphQuery(tokens=("queen", "king", "king"), top_k=1)
    )
    second = assembler.assemble(
        Pass218I22GraphQuery(tokens=("king", "queen"), top_k=1)
    )
    assert first["graph_hash72"] == second["graph_hash72"]
    assert first["nodes"] == second["nodes"]
    assert first["edges"] == second["edges"]
    assert assembler.status()["graph_count"] == 2


def test_i22_preserves_mixed_polarity_as_evidence_not_truth_resolution() -> None:
    assembler = Pass218I22SemanticGraphCandidateAssembler(
        FakeI21Control(),
        FakeLexicalProvider(mixed=True),
    )
    graph = assembler.assemble(
        Pass218I22GraphQuery(tokens=("king",), top_k=1)
    )
    bundle = next(
        item for item in graph["evidence_bundles"]
        if item["source_token"] == "king" and item["target_token"] == "queen"
    )
    assert bundle["polarity_class"] == "MIXED_POLARITY_EVIDENCE"
    assert bundle["status_polarities"] == [-1, 1]
    assert bundle["pair_truth_promotion"] is False
    assert graph["mixed_polarity_pair_count"] == 1


def test_i22_fails_closed_on_i21_readiness_or_authority_drift() -> None:
    unavailable = Pass218I22SemanticGraphCandidateAssembler(
        FakeI21Control(ready=False),
        FakeLexicalProvider(),
    )
    with pytest.raises(
        Pass218I22SemanticGraphError,
        match="P218_I22_I21_CANDIDATE_PROVIDER_REQUIRED",
    ):
        unavailable.assemble(Pass218I22GraphQuery(tokens=("king",), top_k=1))

    drifted = Pass218I22SemanticGraphCandidateAssembler(
        FakeI21Control(truth_promotion=True),
        FakeLexicalProvider(),
    )
    with pytest.raises(
        Pass218I22SemanticGraphError,
        match="P218_I22_I21_SAFETY_DRIFT",
    ):
        drifted.assemble(Pass218I22GraphQuery(tokens=("king",), top_k=1))


def test_i22_query_bounds_reject_non_integer_and_out_of_range_values() -> None:
    with pytest.raises(
        Pass218I22SemanticGraphError,
        match="P218_I22_TOP_K_INTEGER_REQUIRED",
    ):
        Pass218I22GraphQuery(tokens=("king",), top_k="1").validated()  # type: ignore[arg-type]
    with pytest.raises(
        Pass218I22SemanticGraphError,
        match="P218_I22_TOP_K_OUT_OF_RANGE",
    ):
        Pass218I22GraphQuery(tokens=("king",), top_k=73).validated()


def test_i22_repository_wordnet_provider_reuses_inherited_assets_nonverbosely() -> None:
    provider = Pass218I22WordNetPriorProvider(REPOSITORY_ROOT)
    status = provider.status()
    assert status["lexical_prior_ready"] is True
    assert validate_hash72(status["asset_manifest_hash72"])
    snapshot = provider.snapshot(("king",))
    assert snapshot["asset_manifest_hash72"] == status["asset_manifest_hash72"]
    assert snapshot["definitions_retained"] is False
    assert snapshot["examples_retained"] is False
    assert snapshot["empirical_truth_authority"] is False


def test_i22_runtime_surface_is_bounded_and_non_authoritative() -> None:
    app = FastAPI()
    i21 = FakeI21Control()
    control = install_pass218_i22_semantic_graph_control(
        app,
        i21,
        repository_root=REPOSITORY_ROOT,
    )
    assert control.status()["semantic_graph_candidate_ready"] is True

    with TestClient(app) as client:
        status = client.get(PASS218_I22_STATUS_PATH)
        assert status.status_code == 200
        assert status.json()["truth_promotion"] is False

        response = client.post(
            PASS218_I22_CANDIDATES_PATH,
            json={"tokens": ["king"], "top_k": 1},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["semantic_graph_status"] == "REVISABLE_SEMANTIC_GRAPH_CANDIDATE"
        assert payload["model_activation_invoked"] is False
        assert payload["authoritative_semantic_compression_ready"] is False

        assert client.get(PASS218_I22_CANDIDATES_PATH).status_code == 405
        assert client.post(PASS218_I22_STATUS_PATH, json={}).status_code == 405

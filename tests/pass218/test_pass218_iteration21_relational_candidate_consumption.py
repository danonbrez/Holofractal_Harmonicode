from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_relations_i21 import (
    PASS218_I21_CANDIDATES_PATH,
    PASS218_I21_STATUS_PATH,
    install_pass218_i21_relational_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.genesis import ExactDistributionalRelation
from hhs_runtime.pass218.relational_consumption_i21 import (
    Pass218I21CandidateQuery,
    Pass218I21RelationalCandidateConsumer,
    Pass218I21RelationalConsumptionError,
)


class FakeExactProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def exact_neighbors(
        self,
        token: str,
        *,
        top_k: int,
    ) -> tuple[ExactDistributionalRelation, ...]:
        self.calls.append((token, top_k))
        fixtures = {
            "king": (
                ExactDistributionalRelation("queen", 1, 81, 100, "vector-queen"),
                ExactDistributionalRelation("man", 1, 64, 100, "vector-man"),
            ),
            "queen": (
                ExactDistributionalRelation("king", 1, 81, 100, "vector-king"),
                ExactDistributionalRelation("woman", 1, 64, 100, "vector-woman"),
            ),
        }
        return fixtures.get(token, ())[:top_k]


class FakeI20Control:
    def __init__(self, *, ready: bool = True, truth_promotion: bool = False) -> None:
        self.provider = FakeExactProvider()
        self.ready = ready
        self.truth_promotion = truth_promotion
        self.provider_requests = 0
        self.binding_hash72 = hash72_digest(
            {"domain": "HHS-P218-I20-TEST-BINDING"},
            {"model_id": "i21-fixture"},
        )

    def status(self) -> dict:
        return {
            "relational_candidate_provider_ready": self.ready,
            "binding_hash72": self.binding_hash72,
            "model_id": "i21-fixture",
            "canonical_model_root": "1" * 64,
            "index_root": "2" * 64,
            "browser_model_activation_permitted": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": self.truth_promotion,
            "action_authority_minted": False,
            "pass165_source_retaining_learning_commit_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }

    def exact_provider(self) -> FakeExactProvider:
        self.provider_requests += 1
        return self.provider


def test_i21_consumes_exact_i20_relations_as_revisable_candidates() -> None:
    i20 = FakeI20Control()
    consumer = Pass218I21RelationalCandidateConsumer(i20)
    batch = consumer.consume(
        Pass218I21CandidateQuery(tokens=("king", "queen"), top_k=2)
    )

    assert batch["i20_binding_hash72"] == i20.binding_hash72
    assert batch["candidate_semantics"] == "REVISABLE_RELATIONAL_EVIDENCE"
    assert batch["truth_promotion"] is False
    assert batch["action_authority_minted"] is False
    assert batch["canonical_learning_commit_invoked"] is False
    assert batch["model_activation_invoked"] is False
    assert batch["verbatim_corpus_source_retained"] is False
    assert batch["authoritative_float_weights_created"] is False
    assert [item["source_token"] for item in batch["results"]] == ["king", "queen"]
    king = batch["results"][0]["candidates"]
    assert [item["rank"] for item in king] == [1, 2]
    assert king[0]["target"] == "queen"
    assert king[0]["similarity_squared"] == {"numerator": 81, "denominator": 100}
    assert king[0]["revisable_candidate"] is True
    assert king[0]["empirical_truth_authority"] is False
    assert king[0]["candidate_hash72"]
    assert i20.provider_requests == 1


def test_i21_batch_identity_is_order_and_duplicate_stable() -> None:
    i20 = FakeI20Control()
    consumer = Pass218I21RelationalCandidateConsumer(i20)
    first = consumer.consume(
        Pass218I21CandidateQuery(tokens=("queen", "king", "king"), top_k=2)
    )
    second = consumer.consume(
        Pass218I21CandidateQuery(tokens=("king", "queen"), top_k=2)
    )
    assert first["batch_hash72"] == second["batch_hash72"]
    assert first["results"] == second["results"]
    assert consumer.status()["batch_count"] == 2
    assert consumer.status()["last_batch_hash72"] == second["batch_hash72"]


def test_i21_fails_closed_when_i20_is_not_ready_or_safety_drifted() -> None:
    unavailable = Pass218I21RelationalCandidateConsumer(FakeI20Control(ready=False))
    with pytest.raises(
        Pass218I21RelationalConsumptionError,
        match="P218_I21_I20_RELATIONAL_PROVIDER_REQUIRED",
    ):
        unavailable.consume(Pass218I21CandidateQuery(tokens=("king",), top_k=1))

    drifted = Pass218I21RelationalCandidateConsumer(
        FakeI20Control(truth_promotion=True)
    )
    with pytest.raises(
        Pass218I21RelationalConsumptionError,
        match="P218_I21_I20_SAFETY_DRIFT",
    ):
        drifted.consume(Pass218I21CandidateQuery(tokens=("king",), top_k=1))


def test_i21_rejects_non_integer_or_out_of_range_query_bounds() -> None:
    with pytest.raises(
        Pass218I21RelationalConsumptionError,
        match="P218_I21_TOP_K_INTEGER_REQUIRED",
    ):
        Pass218I21CandidateQuery(tokens=("king",), top_k="2").validated()  # type: ignore[arg-type]
    with pytest.raises(
        Pass218I21RelationalConsumptionError,
        match="P218_I21_TOP_K_OUT_OF_RANGE",
    ):
        Pass218I21CandidateQuery(tokens=("king",), top_k=73).validated()


def test_i21_runtime_surface_queries_candidates_without_activation_authority() -> None:
    app = FastAPI()
    i20 = FakeI20Control()
    control = install_pass218_i21_relational_control(app, i20)
    assert control.status()["candidate_consumption_ready"] is True

    with TestClient(app) as client:
        status = client.get(PASS218_I21_STATUS_PATH)
        assert status.status_code == 200
        assert status.json()["truth_promotion"] is False

        response = client.post(
            PASS218_I21_CANDIDATES_PATH,
            json={"tokens": ["king"], "top_k": 2},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["results"][0]["candidates"][0]["target"] == "queen"
        assert payload["model_activation_invoked"] is False

        assert client.get(PASS218_I21_CANDIDATES_PATH).status_code == 405
        assert client.post(PASS218_I21_STATUS_PATH, json={}).status_code == 405


def test_i21_runtime_surface_rejects_candidate_query_when_i20_not_ready() -> None:
    app = FastAPI()
    install_pass218_i21_relational_control(app, FakeI20Control(ready=False))
    with TestClient(app) as client:
        response = client.post(
            PASS218_I21_CANDIDATES_PATH,
            json={"tokens": ["king"], "top_k": 1},
        )
        assert response.status_code == 409
        assert "P218_I21_I20_RELATIONAL_PROVIDER_REQUIRED" in response.json()["detail"]

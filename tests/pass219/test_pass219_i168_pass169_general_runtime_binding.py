from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.pass169_algebra_routes import build_pass169_algebra_router
from hhs_runtime.pass169.public_service import Pass169AlgebraService, Pass169PublicSurfaceError
from hhs_runtime.pass169.runtime_binding import (
    CANONICAL_SOURCE_SHA256,
    VERIFIED_OPERATIONS,
    Pass169CanonicalRuntimeBinding,
)
from hhs_runtime.pass219.pass169_terminal_gate_i167 import build_i167_pass169_terminal_gate

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_RECEIPT_HASH72 = "i91e<BXYyem<yft9yU>pPRowX-aIvY*2esocIG8LVXN6A0TrNm3ttdkrpD4oCN?bS1ID!QoJ"
EXPECTED_TRANSITION_HASH216 = "xhfHT5FB/MI5rH*yinth2RcAO1zArnsidZHvZXT6yW3IV!?874xAJdm27yhJa3>yEOt+BMAPV-jCe*8!e41n1piMHtVFwX+SvcErOdWFC<*i/DOv?VO//UlYS<>oJT1Ou>//9S/KRYYUF6AuB6B3xsCfcWb(TUolnSU20VK9fYSDQFVzYco8h/xD)PKQ+!/W>bv(azKhx+S9OwtIuCk-1y18"


class _Authority:
    def status(self) -> dict[str, object]:
        return {
            "contract": "HHS-RUNTIME-AUTHORITY",
            "runtime_mode": "canonical",
            "singleton_vm81_authority": True,
        }


def test_i168_deployed_runtime_binding_proves_all_required_operations() -> None:
    record = Pass169CanonicalRuntimeBinding(ROOT).record()
    assert record["operation_verified_mask"] == record["required_operation_mask"] == 0x0FFF
    assert record["verified_operations"] == list(VERIFIED_OPERATIONS)
    assert record["canonical_source_sha256"] == CANONICAL_SOURCE_SHA256
    assert record["source_identity_exact"] is True
    assert record["pass159_frontend_chain_complete"] is True
    assert record["typed_proof_verified"] is True
    assert record["interpreter_compiler_equality_verified"] is True
    assert record["exact_vm81_admission_verified"] is True
    assert record["atomic_commit_verified"] is True
    assert record["hash72_receipts_verified"] is True
    assert record["hash216_identities_verified"] is True
    assert record["deterministic_replay_verified"] is True
    assert record["reverse_restores_prior_state_verified"] is True
    assert record["live_runtime_abi_verified"] is True
    assert record["canonical_computation_through_runtime_abi"] is True
    assert record["single_vm81_commit_authority"] is True
    assert record["fallback_used"] is False
    assert record["floating_point_canonical_authority"] is False
    assert record["hash216_persistence_authority"] is False
    assert record["receipt_hash72"] == EXPECTED_RECEIPT_HASH72
    assert record["transition_hash216"] == EXPECTED_TRANSITION_HASH216
    for key in (
        "source_hash216",
        "tokens_hash216",
        "ast_hash216",
        "type_environment_hash216",
        "constraint_graph_hash216",
        "normalized_ir_hash216",
        "vmir_hash216",
        "proof_hash216",
        "transition_hash216",
        "reverse_hash216",
    ):
        assert len(record[key]) == 216


def test_i168_public_service_executes_canonical_operation_chain() -> None:
    service = Pass169AlgebraService(ROOT, authority_provider=lambda: _Authority())
    canonical_text = (ROOT / "HHS_PASS_169_CANONICAL_ALGEBRA_CORPUS.harmonicode").read_text()
    registered = service.register_source(canonical_text)
    source_id = registered["source"]["source_id"]
    assert source_id == f"canonical:sha256:{CANONICAL_SOURCE_SHA256}"
    assert registered["source"]["canonical_pass169_corpus"] is True

    assert service.dispatch("tokens", source_id=source_id)["artifact_kind"] == "TOKEN_STREAM"
    assert service.dispatch("ast", source_id=source_id)["artifact_kind"] == "AST"
    assert service.dispatch("symbols", source_id=source_id)["artifact_kind"] == "TYPE_ENVIRONMENT"
    assert service.dispatch("constraints", source_id=source_id)["artifact_kind"] == "CONSTRAINT_GRAPH"
    assert service.dispatch("typecheck", source_id=source_id)["verified"] is True
    assert len(service.dispatch("normalize", source_id=source_id)["vmir_hash216"]) == 216
    proof = service.dispatch("prove", source_id=source_id)
    assert proof["typed_proof_verified"] is True
    constrained = service.dispatch("prove-constraint", source_id=source_id, constraint="typed-zero")
    assert constrained["proof_id"] == proof["proof_id"]

    candidate = service.dispatch("evaluate-candidate", source_id=source_id)
    candidate_id = candidate["candidate_id"]
    assert candidate["candidate_verified"] is True
    admitted = service.dispatch("admit", candidate_id=candidate_id)
    assert admitted["admitted"] is True
    committed = service.dispatch("commit", candidate_id=candidate_id)
    transition_id = committed["transition_id"]
    assert committed["atomic_commit_verified"] is True
    assert committed["receipt_hash72"] == EXPECTED_RECEIPT_HASH72

    receipt = service.dispatch("receipt", transition_id=transition_id)
    assert receipt["hash72_receipt_verified"] is True
    replay = service.dispatch("replay", transition_id=transition_id)
    assert replay["deterministic_replay_verified"] is True
    reverse = service.dispatch("reverse", transition_id=transition_id)
    assert reverse["prior_state_restored"] is True
    assert service.dispatch("divergence", transition_id=transition_id)["divergence_detected"] is False
    assert service.dispatch("inspect", node=f"transition:{transition_id}")["transition_id"] == transition_id
    assert service.dispatch("export-proof", transition_id=proof["proof_id"])["proof_id"] == proof["proof_id"]
    assert service.dispatch("validate")["admitted"] is True

    status = service.status()
    assert status["authority"]["canonical_gateway_bound"] is True
    assert status["authority"]["singleton_vm81_authority"] is True
    assert status["new_vm81_authority"] is False
    assert status["new_hash72_mint_authority"] is False
    assert status["hash216_persistence_authority"] is False
    assert status["floating_point_canonical_authority"] is False


def test_i168_noncanonical_source_cannot_borrow_canonical_authority() -> None:
    service = Pass169AlgebraService(ROOT)
    registered = service.register_source("x==y")
    source_id = registered["source"]["source_id"]
    assert registered["source"]["canonical_authority"] is False
    with pytest.raises(Pass169PublicSurfaceError) as caught:
        service.dispatch("tokens", source_id=source_id)
    assert caught.value.code == "PASS169_NONCANONICAL_SOURCE_RUNTIME_AUTHORITY_DENIED"


def test_i168_hardened_terminal_gate_tracks_runtime_receipt_only() -> None:
    receipt_present = (ROOT / "HHS_PASS_169_RUNTIME_BINDING_RECEIPT.json").is_file()
    report = build_i167_pass169_terminal_gate(ROOT)
    assert report["canonical_corpus"]["provenance"]["verified"] is True
    assert report["required_artifacts"]["complete"] is True
    assert report["pass168_parent"]["resolved"] is True
    assert report["public_surfaces"]["cli"]["complete"] is True
    assert report["public_surfaces"]["http"]["complete"] is True
    assert report["general_runtime_binding"]["receipt_present"] is receipt_present
    assert report["general_runtime_binding"]["verified"] is receipt_present
    assert report["pass169_terminal_contract_verified"] is receipt_present
    if receipt_present:
        assert report["blockers"] == []
        assert report["next_boundary"] == "PASS169_TERMINAL_CLOSURE_VERIFIED"
    else:
        assert report["blockers"] == ["PASS169_GENERAL_RUNTIME_BINDING_NOT_VERIFIED"]
        assert report["next_boundary"] == "PASS169_GENERAL_RUNTIME_BINDING_CLOSURE"


def test_i168_canonical_http_chain_uses_one_router_and_runtime_binding() -> None:
    app = FastAPI()
    app.include_router(build_pass169_algebra_router(lambda: _Authority()))
    client = TestClient(app)
    canonical_text = (ROOT / "HHS_PASS_169_CANONICAL_ALGEBRA_CORPUS.harmonicode").read_text()

    create = client.post("/v1/algebra/sources", json={"source": canonical_text})
    assert create.status_code == 200
    source_id = create.json()["source"]["source_id"]

    for suffix in ("tokens", "ast", "constraints"):
        response = client.get(f"/v1/algebra/sources/{source_id}/{suffix}")
        assert response.status_code == 200, response.text
        assert response.json()["runtime_abi_verified"] is True
    for suffix in ("typecheck", "normalize"):
        response = client.post(f"/v1/algebra/sources/{source_id}/{suffix}")
        assert response.status_code == 200, response.text

    candidate_response = client.post(f"/v1/algebra/sources/{source_id}/candidates")
    assert candidate_response.status_code == 200
    candidate_id = candidate_response.json()["candidate_id"]
    assert client.get(f"/v1/algebra/candidates/{candidate_id}").status_code == 200
    assert client.post(f"/v1/algebra/candidates/{candidate_id}/validate").status_code == 200
    commit = client.post(f"/v1/algebra/candidates/{candidate_id}/commit")
    assert commit.status_code == 200
    transition_id = commit.json()["transition_id"]
    proof_id = Pass169CanonicalRuntimeBinding(ROOT).record()["proof_id"]
    assert client.get(f"/v1/algebra/proofs/{proof_id}").status_code == 200
    assert client.get(f"/v1/algebra/transitions/{transition_id}").status_code == 200
    assert client.get(f"/v1/algebra/transitions/{transition_id}/receipt").status_code == 200
    assert client.post(f"/v1/algebra/transitions/{transition_id}/replay").status_code == 200
    reverse = client.post(f"/v1/algebra/transitions/{transition_id}/reverse")
    assert reverse.status_code == 200
    assert reverse.json()["prior_state_restored"] is True

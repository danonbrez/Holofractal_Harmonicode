from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from hhs_backend.public_api_server import create_app
from hhs_runtime.pass169.cli import CLI_EQUIVALENTS, build_parser
from hhs_runtime.pass169.public_service import Pass169AlgebraService, Pass169PublicSurfaceError

EXPECTED_HTTP = {
    ("GET", "/v1/algebra"),
    ("POST", "/v1/algebra/sources"),
    ("GET", "/v1/algebra/sources/{source_id}"),
    ("GET", "/v1/algebra/sources/{source_id}/tokens"),
    ("GET", "/v1/algebra/sources/{source_id}/ast"),
    ("GET", "/v1/algebra/sources/{source_id}/constraints"),
    ("POST", "/v1/algebra/sources/{source_id}/typecheck"),
    ("POST", "/v1/algebra/sources/{source_id}/normalize"),
    ("POST", "/v1/algebra/sources/{source_id}/candidates"),
    ("GET", "/v1/algebra/candidates/{candidate_id}"),
    ("POST", "/v1/algebra/candidates/{candidate_id}/validate"),
    ("POST", "/v1/algebra/candidates/{candidate_id}/commit"),
    ("GET", "/v1/algebra/proofs/{proof_id}"),
    ("GET", "/v1/algebra/transitions/{transition_id}"),
    ("GET", "/v1/algebra/transitions/{transition_id}/receipt"),
    ("POST", "/v1/algebra/transitions/{transition_id}/replay"),
    ("POST", "/v1/algebra/transitions/{transition_id}/reverse"),
}


class FakeContext:
    def status(self):
        return {
            "contract": "HHS-P190-OVRA-HOSS-PCA-FHF-VM81-H72-H216",
            "runtime_mode": "READ_ONLY_CANONICAL_RUNTIME",
            "singleton_vm81_authority": "INHERITED_PASS190_DURABLE_AUTHORITY",
        }


def test_i165_shared_service_keeps_terminal_gate_false() -> None:
    report = Pass169AlgebraService(Path.cwd()).status()
    assert report["ok"] is True
    assert report["canonical_corpus_present"] is False
    assert report["pass169_terminal_contract_verified"] is False
    assert report["frozen_evidence_verified"] is True
    assert report["floating_point_canonical_authority"] is False


def test_i165_candidate_source_ingress_is_exact_but_noncanonical() -> None:
    service = Pass169AlgebraService(Path.cwd())
    first = service.register_source("O!=Pi; xy!=yx")
    second = service.get_source(first["source"]["source_id"])
    assert first["source"]["canonical_authority"] is False
    assert first["source"]["canonical_pass169_corpus"] is False
    assert second["source"]["source"] == "O!=Pi; xy!=yx"
    assert first["canonical_state_mutated"] is False


def test_i165_canonical_execution_operations_fail_closed_without_corpus() -> None:
    service = Pass169AlgebraService(Path.cwd())
    for operation in ("tokens", "typecheck", "normalize", "prove", "evaluate-candidate", "admit", "commit", "replay", "reverse"):
        try:
            service.dispatch(operation, source_id="candidate")
        except Pass169PublicSurfaceError as exc:
            assert exc.code == "PASS169_CANONICAL_CORPUS_ABSENT"
        else:
            raise AssertionError(f"{operation} did not fail closed")


def test_i165_cli_contract_has_all_twenty_equivalents_and_parses() -> None:
    assert len(CLI_EQUIVALENTS) == 20
    parser = build_parser()
    assert parser.parse_args(["algebra", "status"]).operation == "status"
    assert parser.parse_args(["algebra", "prove", "--constraint", "edge8"]).constraint == "edge8"
    assert parser.parse_args(["algebra", "commit", "candidate-1"]).candidate_id == "candidate-1"
    assert parser.parse_args(["algebra", "reverse", "transition-1"]).transition_id == "transition-1"


def test_i165_canonical_public_gateway_exposes_all_seventeen_pass169_routes() -> None:
    app = create_app(context=FakeContext())
    found = set()
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None) or set()
        if path is None:
            continue
        for method in methods:
            normalized_method = str(getattr(method, "value", method)).upper()
            pair = (normalized_method, path)
            if pair in EXPECTED_HTTP:
                found.add(pair)
    assert found == EXPECTED_HTTP


def test_i165_http_status_and_ingress_work_but_commit_fails_closed() -> None:
    app = create_app(context=FakeContext())
    client = TestClient(app)
    status = client.get("/v1/algebra")
    assert status.status_code == 200
    assert status.json()["canonical_corpus_present"] is False

    created = client.post("/v1/algebra/sources", json={"source": "O!=Pi; xy!=yx"})
    assert created.status_code == 200
    source_id = created.json()["source"]["source_id"]
    fetched = client.get(f"/v1/algebra/sources/{source_id}")
    assert fetched.status_code == 200
    assert fetched.json()["source"]["source"] == "O!=Pi; xy!=yx"

    blocked = client.post("/v1/algebra/candidates/candidate-1/commit")
    assert blocked.status_code == 409
    assert blocked.json()["detail"]["error"] == "PASS169_CANONICAL_CORPUS_ABSENT"

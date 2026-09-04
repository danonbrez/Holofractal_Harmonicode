from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from fastapi.testclient import TestClient

from hhs_backend.pass168_parameter_circuit_routes import build_pass168_parameter_circuit_router
from hhs_backend.public_api_server import create_app
from hhs_runtime.pass168.public_service import (
    SOURCE_SHA256,
    Pass168ParameterCircuitService,
)


REQUIRED_HTTP = {
    ("GET", "/v1/parameter-circuit"),
    ("GET", "/v1/parameter-circuit/source"),
    ("GET", "/v1/parameter-circuit/map"),
    ("GET", "/v1/parameter-circuit/threads"),
    ("GET", "/v1/parameter-circuit/parameters"),
    ("GET", "/v1/parameter-circuit/parameters/{parameter_id}"),
    ("POST", "/v1/parameter-circuit/candidates"),
    ("GET", "/v1/parameter-circuit/candidates/{candidate_id}"),
    ("POST", "/v1/parameter-circuit/candidates/{candidate_id}/validate"),
    ("POST", "/v1/parameter-circuit/candidates/{candidate_id}/commit"),
    ("GET", "/v1/parameter-circuit/dependencies/{parameter_id}"),
    ("GET", "/v1/parameter-circuit/matrices/upper"),
    ("GET", "/v1/parameter-circuit/matrices/lower"),
    ("GET", "/v1/parameter-circuit/comparators/{comparator_id}"),
    ("GET", "/v1/parameter-circuit/transitions/{transition_id}"),
    ("POST", "/v1/parameter-circuit/transitions/{transition_id}/replay"),
    ("POST", "/v1/parameter-circuit/transitions/{transition_id}/rollback"),
    ("GET", "/v1/parameter-circuit/transitions/{transition_id}/receipt"),
}


def _route_pairs(routes) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for route in routes:
        path = getattr(route, "path", "")
        for method in getattr(route, "methods", set()) or set():
            if method in {"HEAD", "OPTIONS"}:
                continue
            pairs.add((method, path))
    return pairs


def test_pass168_native_service_exact_commit_replay_and_rollback(tmp_path: Path) -> None:
    service = Pass168ParameterCircuitService(tmp_path)
    status = service.status()
    proof = status["native_self_test"]
    assert proof["status"] == 0
    assert proof["source_preserved"] is True
    assert proof["parenthesis_parameters_registered"] == 28
    assert proof["equality_half_gates_registered"] == 12
    assert proof["threads_registered"] == 64
    assert proof["raw_threads"] == 40
    assert proof["derived_threads"] == 24
    assert proof["cells_covered"] == 5184
    assert proof["duplicate_addresses"] == 0
    assert proof["inverse_address_failures"] == 0
    assert proof["comparators_verified"] == 6
    assert proof["sparse_dependency_updates_verified"] is True
    assert proof["hash72_receipts_verified"] is True
    assert proof["hash216_identity_verified"] is True
    assert proof["rollback_verified"] is True
    assert proof["repair_verified"] is True
    assert proof["deterministic_replay_verified"] is True
    assert proof["floating_point_canonical_authority"] is False
    assert proof["fallback_used"] is False
    assert status["threads_registered"] == 64
    assert status["cells_registered"] == 5184
    assert status["single_vm81_commit_authority"] is True
    assert status["floating_point_canonical_authority"] is False
    assert status["fallback_used"] is False

    source = service.source()
    assert source["bytes"] == 424
    assert source["sha256"] == SOURCE_SHA256
    assert source["byte_authoritative"] is True

    candidate = service.create_candidate({"P13": 2})
    assert candidate["candidate_only"] is True
    assert candidate["canonical_state_mutated"] is False
    candidate_id = candidate["candidate_id"]
    validation = service.validate_candidate(candidate_id)
    assert validation["status"] == 0
    assert validation["valid"] is True
    assert validation["reject_reason"] == 0
    evaluated = service.evaluate_candidate(candidate_id)
    assert evaluated["canonical_state_mutated"] is False

    committed = service.commit_candidate(candidate_id)
    transition_id = committed["transition_id"]
    assert committed["canonical_state_mutated"] is True
    assert committed["native_commit_surface"] == "hhs_pass168_commit_candidate"
    receipt = service.receipt(transition_id)
    assert len(receipt["change_hash72"]) == 72
    assert len(receipt["receipt_hash72"]) == 72
    assert len(receipt["hash216_triplet"]) == 216
    assert len(receipt["hash216_identity"]) == 216
    assert receipt["fallback_used"] == 0

    replayed = service.replay(transition_id)
    assert replayed["canonical_state_mutated"] is False
    assert replayed["replayed_state"]["state_hash216"] == committed["state"]["state_hash216"]

    restored = Pass168ParameterCircuitService(tmp_path)
    restored_status = restored.status()
    assert restored_status["generation"] == 1
    assert restored_status["state_hash216"] == committed["state"]["state_hash216"]
    assert restored.receipt(transition_id) == receipt

    rolled = restored.rollback(transition_id)
    assert rolled["rollback_verified"] is True
    assert rolled["canonical_state_mutated"] is True
    assert rolled["state"]["generation"] == 0


def test_pass168_sparse_topology_and_comparator_surface(tmp_path: Path) -> None:
    service = Pass168ParameterCircuitService(tmp_path)
    assert service.threads()["count"] == 64
    cell_map = service.cell_map()
    assert cell_map["count"] == 5184
    assert cell_map["duplicate_addresses"] == 0
    assert cell_map["inverse_mapping"] == "EXACT"
    dep = service.dependencies("P13")
    assert dep["raw_thread_id"] == 12
    assert dep["affected_thread_count"] < 64
    assert dep["full_5184_rewrite"] is False
    comparator = service.compare("C3")
    assert comparator["comparator_id"] == "C3"
    assert comparator["ordered"] is True
    assert comparator["conformance_verified_count"] == 6
    assert comparator["floating_point_canonical_authority"] is False


def test_pass168_router_and_canonical_gateway_bind_exactly_once() -> None:
    router = build_pass168_parameter_circuit_router()
    assert _route_pairs(router.routes) == REQUIRED_HTTP
    app = create_app()
    paths = app.openapi()["paths"]
    for method, path in REQUIRED_HTTP:
        assert path in paths, (method, path)
        assert method.lower() in paths[path], (method, path)


def test_pass168_http_executes_native_service_without_float_authority(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HHS_PASS168_STATE_DIR", str(tmp_path))
    import hhs_backend.pass168_parameter_circuit_routes as routes

    routes._DEFAULT_SERVICE = None
    with TestClient(create_app()) as client:
        response = client.get("/v1/parameter-circuit/source")
        assert response.status_code == 200
        assert response.json()["sha256"] == SOURCE_SHA256
        bad = client.post("/v1/parameter-circuit/candidates", json={"updates": {"P13": 2.5}})
        assert bad.status_code == 409
        detail = bad.json()["detail"]
        assert detail["error"] == "PASS168_PARAMETER_VALUE_INVALID"
        assert detail["floating_point_canonical_authority"] is False
        candidate = client.post("/v1/parameter-circuit/candidates", json={"updates": {"P13": 2}})
        assert candidate.status_code == 200
        candidate_id = candidate.json()["candidate_id"]
        validation = client.post(f"/v1/parameter-circuit/candidates/{candidate_id}/validate")
        assert validation.status_code == 200
        assert validation.json()["status"] == 0
        assert validation.json()["valid"] is True
        committed = client.post(f"/v1/parameter-circuit/candidates/{candidate_id}/commit")
        assert committed.status_code == 200
        transition_id = committed.json()["transition_id"]
        receipt = client.get(f"/v1/parameter-circuit/transitions/{transition_id}/receipt")
        assert receipt.status_code == 200
        assert len(receipt.json()["receipt_hash72"]) == 72


def test_pass168_cli_json_jsonl_and_text_profiles(tmp_path: Path) -> None:
    base = [
        sys.executable,
        "-m",
        "hhs_runtime.pass168.cli",
        "parameter-circuit",
        "--state-dir",
        str(tmp_path),
    ]
    for profile in ("json", "jsonl", "text"):
        run = subprocess.run(
            [*base, "--output", profile, "status"],
            check=True,
            capture_output=True,
            text=True,
        )
        assert run.stdout.strip()
        if profile == "json":
            assert json.loads(run.stdout)["threads_registered"] == 64
        elif profile == "jsonl":
            assert json.loads(run.stdout)["cells_registered"] == 5184
        else:
            assert "threads_registered" in run.stdout

    created = subprocess.run(
        [*base, "--output", "json", "set", "P13", "2"],
        check=True,
        capture_output=True,
        text=True,
    )
    candidate_id = json.loads(created.stdout)["candidate_id"]
    committed = subprocess.run(
        [*base, "--output", "json", "commit", candidate_id],
        check=True,
        capture_output=True,
        text=True,
    )
    row = json.loads(committed.stdout)
    assert row["native_commit_surface"] == "hhs_pass168_commit_candidate"
    assert row["canonical_state_mutated"] is True

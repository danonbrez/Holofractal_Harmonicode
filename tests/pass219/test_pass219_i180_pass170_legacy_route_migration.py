from __future__ import annotations

from pathlib import Path
import sys

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

import hhs_backend.pass170_legacy_runtime_routes as routes
from hhs_runtime.pass190.completion import PASS190_NATIVE_PYTHON
from hhs_runtime.pass219.pass170_legacy_route_migration_i180 import (
    EXPECTED_HTTP,
    EXPECTED_TARGET_BLOCKERS,
    EXPECTED_WS,
    verify_i180_legacy_route_migration,
)

if str(PASS190_NATIVE_PYTHON) not in sys.path:
    sys.path.insert(0, str(PASS190_NATIVE_PYTHON))
from hhs_pass190_capability import issue_capability_token  # type: ignore  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SECRET = "pass170-i180-runtime-capability-secret-" + ("x" * 40)


def _token(*scopes: str) -> str:
    return issue_capability_token(
        SECRET,
        principal="pass219-i180-test",
        scopes=scopes,
        ttl_seconds=900,
        nonce="pass219-i180-fixed-test-nonce",
    )


def _client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv(routes.CAPABILITY_SECRET_ENV, SECRET)
    app = FastAPI()
    app.include_router(routes.build_pass170_legacy_runtime_router())
    return TestClient(app)


def test_i180_repository_gate() -> None:
    report = verify_i180_legacy_route_migration(ROOT)
    assert report["evidence_verified"] is True
    assert report["parent_i179_exact_main_verified"] is True
    assert report["parent_i179_exact_main_run"] == 34077531408
    assert report["parent_i179_exact_main_artifact"] == 10002586241
    assert report["migrated_http_route_count"] == 11
    assert report["canonical_websocket_replacement_count"] == 4
    assert report["aggregate_operation_count"] == 59
    assert report["new_operation_count"] == 11
    assert report["fastapi_constructor_count"] == 8
    assert report["constructor_retirement_performed"] is False
    assert report["pass190_token_verifier_reused"] is True
    assert report["new_capability_token_authority"] is False
    assert report["new_vm81_authority"] is False
    assert report["new_hash72_mint_authority"] is False
    assert report["hash216_persistence_authority"] is False
    assert report["target_blockers"] == list(EXPECTED_TARGET_BLOCKERS)
    assert report["pass170_terminal_contract_verified"] is False


def test_i180_router_has_exact_http_routes_and_no_duplicate_websockets() -> None:
    router = routes.build_pass170_legacy_runtime_router()
    observed: set[tuple[str, str]] = set()
    websocket_paths: set[str] = set()
    for route in router.routes:
        methods = getattr(route, "methods", None)
        if methods:
            for method in methods:
                if str(method) not in {"HEAD", "OPTIONS"}:
                    observed.add((str(method), str(route.path)))
        else:
            websocket_paths.add(str(getattr(route, "path", "")))
    assert observed == set(EXPECTED_HTTP)
    assert websocket_paths == set()
    assert set(routes.CANONICAL_WEBSOCKET_REPLACEMENTS) == set(EXPECTED_WS)


def test_runtime_admission_fails_closed_without_secret_or_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(routes.CAPABILITY_SECRET_ENV, raising=False)
    with pytest.raises(HTTPException) as missing_secret:
        routes.enforce_runtime_public_admission(
            f"{routes.AUTHORIZATION_SCHEME} {_token(routes.RUNTIME_EXEC_SCOPE)}",
            required_scope=routes.RUNTIME_EXEC_SCOPE,
        )
    assert missing_secret.value.status_code == 503

    monkeypatch.setenv(routes.CAPABILITY_SECRET_ENV, SECRET)
    with pytest.raises(HTTPException) as missing_token:
        routes.enforce_runtime_public_admission(None, required_scope=routes.RUNTIME_EXEC_SCOPE)
    assert missing_token.value.status_code == 401


def test_runtime_admission_rejects_wrong_scope_and_accepts_inherited_signed_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(routes.CAPABILITY_SECRET_ENV, SECRET)
    with pytest.raises(HTTPException) as wrong:
        routes.enforce_runtime_public_admission(
            f"{routes.AUTHORIZATION_SCHEME} {_token('pass170.other')}",
            required_scope=routes.RUNTIME_EXEC_SCOPE,
        )
    assert wrong.value.status_code == 403

    admission = routes.enforce_runtime_public_admission(
        f"{routes.AUTHORIZATION_SCHEME} {_token(routes.RUNTIME_EXEC_SCOPE)}",
        required_scope=routes.RUNTIME_EXEC_SCOPE,
    )
    assert admission["required_scope"] == routes.RUNTIME_EXEC_SCOPE
    assert routes.RUNTIME_EXEC_SCOPE in admission["authorized_scopes"]
    assert admission["new_token_authority"] is False
    assert admission["pass190_verifier_reused"] is True
    assert len(admission["token_hash72"]) == 72


def test_migrated_http_execution_is_gated_but_read_only_status_remains_public(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_status() -> dict[str, object]:
        return {"status": "OK", "source": "legacy-v1"}

    async def fake_eval(_request: object) -> dict[str, object]:
        return {"status": "SOLVED", "receipt_hash72": "r" * 72}

    monkeypatch.setattr(routes.legacy_v1, "api_status", fake_status)
    monkeypatch.setattr(routes.legacy_v1, "api_calculator_evaluate", fake_eval)
    client = _client(monkeypatch)

    status = client.get("/api/status")
    assert status.status_code == 200
    assert status.json()["status"] == "OK"

    rejected = client.post("/api/calculator/evaluate", json={"expression": "x+y"})
    assert rejected.status_code == 401

    wrong = client.post(
        "/api/calculator/evaluate",
        json={"expression": "x+y"},
        headers={"Authorization": f"{routes.AUTHORIZATION_SCHEME} {_token('pass170.other')}"},
    )
    assert wrong.status_code == 403

    accepted = client.post(
        "/api/calculator/evaluate",
        json={"expression": "x+y"},
        headers={"Authorization": f"{routes.AUTHORIZATION_SCHEME} {_token(routes.RUNTIME_EXEC_SCOPE)}"},
    )
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "SOLVED"


def test_i180_manifests_preserve_constructor_and_authority_boundaries() -> None:
    import json

    migration = json.loads((ROOT / "HHS_PUBLIC_LEGACY_ROUTE_MIGRATION_I180.json").read_text())
    index = json.loads((ROOT / "HHS_PUBLIC_OPERATION_RECORD_INDEX_I180.json").read_text())
    scopes = json.loads((ROOT / "HHS_PUBLIC_CAPABILITY_SCOPE_REGISTRY_I180.json").read_text())

    assert migration["constructor_state"]["active_constructor_count"] == 8
    assert migration["constructor_state"]["constructor_retirement_performed"] is False
    assert index["frozen_parent_record_count"] == 48
    assert index["aggregate_record_count"] == 59
    assert len(index["new_operation_ids"]) == 11
    assert scopes["inherited_token_authority"]["new_token_issuer_created"] is False
    assert scopes["invariants"]["new_vm81_authority"] is False
    assert scopes["invariants"]["new_hash72_mint_authority"] is False
    assert scopes["invariants"]["hash216_persistence_authority"] is False


def test_canonical_websocket_replacements_exist_and_adapter_does_not_duplicate_them() -> None:
    canonical = (ROOT / "hhs_backend/runtime/runtime_ws.py").read_text(encoding="utf-8")
    adapter = (ROOT / "hhs_backend/pass170_legacy_runtime_routes.py").read_text(encoding="utf-8")
    legacy = (ROOT / "hhs_runtime_api_server_v1.py").read_text(encoding="utf-8")
    for path in EXPECTED_WS:
        assert f'"{path}"' in canonical
        assert f'"{path}"' in legacy
    assert "@router.websocket" not in adapter
    assert ".websocket(" not in adapter

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

import hhs_backend.runtime.runtime_server as legacy_runtime
import hhs_runtime_api_server_v1 as legacy_v1
from hhs_backend.pass170_legacy_runtime_routes import (
    MIGRATED_HTTP_SIGNATURES,
    build_pass170_legacy_runtime_router,
)
from hhs_runtime.pass219.pass170_legacy_constructor_retirement_i181 import (
    verify_i181_legacy_constructor_retirement,
)

ROOT = Path(__file__).resolve().parents[2]


def _http_signatures(router) -> set[tuple[str, str]]:
    signatures: set[tuple[str, str]] = set()
    for route in router.routes:
        methods = getattr(route, "methods", None)
        if methods:
            for method in methods:
                name = str(method)
                if name not in {"HEAD", "OPTIONS"}:
                    signatures.add((name, str(getattr(route, "path", ""))))
    return signatures


def _ws_paths(router) -> set[str]:
    return {
        str(getattr(route, "path", ""))
        for route in router.routes
        if getattr(route, "methods", None) is None
    }


def test_i181_repository_gate() -> None:
    report = verify_i181_legacy_constructor_retirement(ROOT)
    assert report["evidence_verified"] is True
    assert report["parent_i180_exact_main_verified"] is True
    assert report["parent_i180_exact_main_run"] == 34078826576
    assert report["parent_i180_exact_main_artifact"] == 10002996393
    assert report["fastapi_constructor_count"] == 6
    assert report["newly_retired_constructor_count"] == 2
    assert report["cumulative_retired_constructor_count"] == 4
    assert report["migrated_http_route_count"] == 11
    assert report["canonical_websocket_replacement_count"] == 4
    assert report["legacy_fastapi_constructor_blocker_cleared"] is True
    assert report["pass170_terminal_contract_verified"] is False


def test_retired_sources_have_no_fastapi_constructor() -> None:
    for relative in (
        "hhs_backend/runtime/runtime_server.py",
        "hhs_runtime_api_server_v1.py",
    ):
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert "FastAPI(" not in source
        assert 'CANONICAL_TARGET = "hhs_backend.public_api_server:app"' in source
        assert "INDEPENDENT_FASTAPI_CONSTRUCTOR = False" in source
        assert "def __getattr__(name: str):" in source


def test_legacy_handler_router_shapes_are_preserved() -> None:
    assert _http_signatures(legacy_runtime.legacy_router) == {
        ("GET", "/api/healthz"),
        ("GET", "/api/runtime/metrics"),
        ("POST", "/api/hhs/solve"),
        ("POST", "/api/runtime/event"),
        ("GET", "/api/runtime/replay"),
        ("GET", "/api/runtime/graph"),
        ("GET", "/api/runtime/transport"),
    }
    assert _http_signatures(legacy_v1.legacy_router) == {
        ("GET", "/api/status"),
        ("POST", "/api/calculator/evaluate"),
        ("POST", "/api/agent/run-loop"),
        ("GET", "/api/certification"),
    }
    assert _ws_paths(legacy_v1.legacy_router) == {
        "/ws/runtime",
        "/ws/replay",
        "/ws/graph",
        "/ws/transport",
    }


def test_i180_governed_adapter_keeps_all_eleven_http_operations() -> None:
    assert _http_signatures(build_pass170_legacy_runtime_router()) == set(MIGRATED_HTTP_SIGNATURES)


def test_legacy_app_attributes_resolve_to_exact_canonical_app() -> None:
    from hhs_backend.public_api_server import app as canonical_app

    runtime_app = getattr(legacy_runtime, "app")
    v1_app = getattr(legacy_v1, "app")
    assert isinstance(canonical_app, FastAPI)
    assert runtime_app is canonical_app
    assert v1_app is canonical_app


def test_retirement_does_not_create_forbidden_authority() -> None:
    for module in (legacy_runtime, legacy_v1):
        assert module.INDEPENDENT_FASTAPI_CONSTRUCTOR is False
        assert module.PUBLIC_PORT_AUTHORITY is False
        assert module.NEW_VM81_AUTHORITY is False
        assert module.NEW_HASH72_MINT_AUTHORITY is False
        assert module.HASH216_PERSISTENCE_AUTHORITY is False
        assert module.CAPABILITY_TOKEN_AUTHORITY is False

from __future__ import annotations

from fastapi.testclient import TestClient

from hhs_backend import production_server


def _route_index(*, path: str | None = None, name: str | None = None) -> int:
    for index, route in enumerate(production_server.app.router.routes):
        if path is not None and getattr(route, "path", None) == path:
            return index
        if name is not None and getattr(route, "name", None) == name:
            return index
    raise AssertionError(f"route not found: path={path!r} name={name!r}")


def test_lifecycle_and_pass165_routes_precede_static_application_mount() -> None:
    static_index = _route_index(name="hhs-production-harmonizer")
    assert _route_index(path="/api/runtime/multimodal-ingress/ingest") < static_index
    assert _route_index(path="/api/runtime/development/status") < static_index
    assert _route_index(path="/api/runtime/development/lifecycle") < static_index
    assert _route_index(path="/api/{unmatched_path:path}") < static_index


def test_lifecycle_validation_failure_is_structured_json_not_spa_html() -> None:
    client = TestClient(production_server.app, raise_server_exceptions=False)
    response = client.post("/api/runtime/development/lifecycle", json={})
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/json")
    payload = response.json()
    assert payload.get("detail")


def test_unknown_api_path_is_structured_json_not_static_fallback() -> None:
    client = TestClient(production_server.app, raise_server_exceptions=False)
    response = client.post("/api/runtime/development/not-a-route", json={})
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    payload = response.json()
    assert payload["status"] == "HHS_API_ROUTE_NOT_FOUND"
    assert payload["detail"]["static_fallback_used"] is False

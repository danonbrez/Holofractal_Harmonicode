from __future__ import annotations

from fastapi.testclient import TestClient

from hhs_backend import production_server


SUCCESSOR_STATUS_PATHS = (
    "/api/runtime/integration/status",
    "/api/runtime/calibration/status",
    "/api/runtime/calibration-registry/status",
    "/api/runtime/distributed-calibration/status",
    "/api/runtime/optimization-authority/status",
    "/api/runtime/optimization-canary/status",
    "/api/runtime/optimization-active/status",
)


def test_successor_routes_precede_production_api_fallback() -> None:
    paths = [
        str(getattr(route, "path", ""))
        for route in production_server.app.router.routes
    ]
    fallback_indexes = [
        index
        for index, path in enumerate(paths)
        if path == production_server.API_FALLBACK_PATH
    ]
    assert fallback_indexes
    first_fallback = min(fallback_indexes)

    for path in SUCCESSOR_STATUS_PATHS:
        assert path in paths, path
        assert paths.index(path) < first_fallback, (
            f"{path} is shadowed by {production_server.API_FALLBACK_PATH}"
        )


def test_successor_status_endpoints_are_not_structured_404s() -> None:
    client = TestClient(production_server.app)
    for path in SUCCESSOR_STATUS_PATHS:
        response = client.get(path)
        assert response.status_code != 404, (path, response.text[:500])
        payload = response.json()
        assert payload.get("schema") != "HHS_PRODUCTION_API_ROUTE_NOT_FOUND_V1", path


def test_system_status_advertises_registered_concrete_surfaces() -> None:
    client = TestClient(production_server.app)
    payload = client.get("/api/system/status").json()
    assert payload["capability_api"] == "/api/runtime/capability/status"
    assert payload["document_api"] == "/api/runtime/document/perception/status"
    assert payload["integration_api"] == "/api/runtime/integration"
    assert payload["distributed_calibration_api"] == "/api/runtime/distributed-calibration"
    assert payload["optimization_active_api"] == "/api/runtime/optimization-active"

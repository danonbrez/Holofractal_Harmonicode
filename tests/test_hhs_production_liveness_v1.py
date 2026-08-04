from __future__ import annotations

import asyncio
from pathlib import Path


def test_production_server_owns_one_bounded_api_health_route() -> None:
    from hhs_backend import production_server

    routes = [
        route
        for route in production_server.app.router.routes
        if str(getattr(route, "path", "")) == "/api/health"
    ]
    assert len(routes) == 1
    assert getattr(routes[0], "name", None) == "hhs-production-bounded-liveness"


def test_production_liveness_is_dependency_light_and_runtime_grounded() -> None:
    from hhs_backend import production_server

    payload = asyncio.run(production_server.production_liveness())
    assert payload["schema"] == "HHS_PRODUCTION_BOUNDED_LIVENESS_V1"
    assert payload["ok"] is True
    assert payload["service_available"] is True
    assert payload["authority_ready"] is payload["runtime_ready"]
    assert payload["assistant_ready"] is False
    assert payload["assistant_health_requires_separate_probe"] is True
    assert payload["frontend_runtime_authority"] is False
    assert payload["runtime_authority"] == production_server._runtime_authority_status()
    assert payload["runtime_readiness_uses_committed_live_projection"] is True
    assert payload["status_read_is_bounded"] is True
    assert payload["mutable_runtime_traversal_performed"] is False


def test_production_health_route_precedes_api_fallback_and_static_root() -> None:
    from hhs_backend import production_server

    routes = list(production_server.app.router.routes)
    health_index = next(
        index
        for index, route in enumerate(routes)
        if str(getattr(route, "path", "")) == "/api/health"
    )
    fallback_index = next(
        index
        for index, route in enumerate(routes)
        if str(getattr(route, "path", "")) == "/api/{unmatched_path:path}"
    )
    static_index = next(
        index
        for index, route in enumerate(routes)
        if getattr(route, "name", None) == "hhs-production-harmonizer"
    )
    assert health_index < fallback_index < static_index


def test_deployment_health_uses_the_production_liveness_contract() -> None:
    source = Path(
        "applications/holofractal_harmonizer/src/deployment-health.mjs"
    ).read_text(encoding="utf-8")
    assert "const LIVENESS_PATHS = ['/api/health'];" in source
    assert "'/healthz'" not in source

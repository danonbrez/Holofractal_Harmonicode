#!/usr/bin/env python3
"""Restartable production validation for Pass 201 public API federation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from fastapi.testclient import TestClient

from hhs_backend.application_ide_server import app


def validate() -> Dict[str, Any]:
    federation = app.state.hhs_public_api_federation
    report = app.state.hhs_public_api_registration
    catalog = federation.catalog(app)
    routes = catalog["routes"]
    services = catalog["services"]
    passes = catalog["passes"]

    assert report["registration_started"] is True
    assert report["import_failure_count"] == 0, report["import_failures"]
    assert report["unexposed_route_count"] == 0, report["unexposed_routes"]
    assert report["closed"] is True
    assert catalog["closed"] is True
    assert catalog["openapi_missing_count"] == 0, catalog["openapi_missing"]
    assert len(routes) == len(app.router.routes)
    assert len({route["route_id"] for route in routes}) == len(routes)
    assert len(services) == catalog["service_count"]
    assert len(passes) == catalog["pass_module_count"]
    assert all(service["public_api_available"] for service in services)
    assert all(pass_module["public_api_available"] for pass_module in passes)
    assert any(pass_module["pass_id"] == "pass201" for pass_module in passes)
    assert any(pass_module["pass_id"] == "pass200c" for pass_module in passes)
    assert any(route["path"] == "/api/public/status" for route in routes)
    assert any(route["path"] == "/api/runtime/optimization-active/status" for route in routes)
    assert getattr(app.router.routes[-1], "name", None) == "hhs-full-application-ide"

    public_route_index = next(
        index for index, route in enumerate(app.router.routes)
        if getattr(route, "path", None) == "/api/public/status"
    )
    fallback_indexes = [
        index for index, route in enumerate(app.router.routes)
        if str(getattr(route, "path", "")) == "/api/{path:path}"
    ]
    assert not fallback_indexes or public_route_index < min(fallback_indexes)

    second = federation.catalog(app)
    assert second["catalog_sha256"] == catalog["catalog_sha256"]
    assert second["routes"] == routes
    assert second["services"] == services
    assert second["passes"] == passes

    client = TestClient(app)
    endpoints = (
        "/api/public/status",
        "/api/public/catalog",
        "/api/public/routes",
        "/api/public/services",
        "/api/public/passes",
        "/api/public/openapi",
        "/api/public/tools",
        "/api/health",
    )
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, (endpoint, response.status_code, response.text)
    invocation = client.post(
        "/api/public/tools/invoke",
        json={"tool": "public.status", "arguments": {}},
    )
    assert invocation.status_code == 200, invocation.text

    route_detail = client.get(f"/api/public/routes/{routes[0]['route_id']}")
    assert route_detail.status_code == 200, route_detail.text
    service_detail = client.get(f"/api/public/services/{services[0]['service_id']}")
    assert service_detail.status_code == 200, service_detail.text
    pass_detail = client.get(f"/api/public/passes/{passes[0]['module_name']}")
    assert pass_detail.status_code == 200, pass_detail.text

    return {
        "schema": "HHS_PASS_201_VALIDATION_RECEIPT_V1",
        "contract": catalog["contract"],
        "classification": catalog["classification"],
        "closed": True,
        "production_entrypoint": "hhs_backend.application_ide_server:app",
        "summary": {
            "api_modules": report["api_module_count"],
            "imported_api_modules": report["imported_module_count"],
            "api_import_failures": report["import_failure_count"],
            "routers": report["router_count"],
            "router_routes_discovered": report["discovered_router_route_count"],
            "routes_attached_by_federation": report["attached_route_count"],
            "existing_routes_preserved": report["duplicate_route_count"],
            "unexposed_router_routes": report["unexposed_route_count"],
            "public_routes": catalog["route_count"],
            "public_services": catalog["service_count"],
            "public_pass_modules": catalog["pass_module_count"],
            "openapi_paths": catalog["openapi_path_count"],
            "openapi_missing_operations": catalog["openapi_missing_count"],
            "validated_public_endpoints": len(endpoints) + 4,
        },
        "registration_report_sha256": report["report_sha256"],
        "catalog_sha256": catalog["catalog_sha256"],
        "claim_boundary": catalog["claim_boundary"],
        "public_routes_precede_unknown_api_fallback": True,
        "static_root_is_last": True,
        "deterministic_restart_projection": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", default="evidence/pass201-ci/PASS201_VALIDATION_RECEIPT.json")
    args = parser.parse_args()
    evidence_path = Path(args.evidence)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    receipt = validate()
    evidence_path.write_text(
        json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

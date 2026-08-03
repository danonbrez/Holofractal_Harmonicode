"""Pass 201 public API federation routes."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from hhs_backend.runtime.hhs_pass201_public_api_federation_v1 import (
    CLASSIFICATION,
    CONTRACT,
    PASS201_PUBLIC_API_FEDERATION,
    PUBLIC_API_PREFIX,
)

router = APIRouter(
    prefix=PUBLIC_API_PREFIX,
    tags=["public-api", "service-catalog", "pass-catalog", "pass201"],
)


class PublicToolInvokeRequest(BaseModel):
    tool: str = Field(min_length=1, max_length=128)
    arguments: Dict[str, Any] = Field(default_factory=dict)


def _federation(request: Request):
    return getattr(request.app.state, "hhs_public_api_federation", PASS201_PUBLIC_API_FEDERATION)


@router.get("/status")
def public_api_status(request: Request) -> Dict[str, Any]:
    return _federation(request).status(request.app)


@router.get("/catalog")
def public_api_catalog(request: Request) -> Dict[str, Any]:
    return _federation(request).catalog(request.app)


@router.get("/routes")
def public_api_routes(request: Request) -> Dict[str, Any]:
    routes = _federation(request).route_catalog(request.app)
    return {
        "schema": "HHS_PASS_201_PUBLIC_ROUTE_CATALOG_V1",
        "contract": CONTRACT,
        "classification": CLASSIFICATION,
        "route_count": len(routes),
        "routes": routes,
    }


@router.get("/routes/{route_id}")
def public_api_route_detail(route_id: str, request: Request) -> Dict[str, Any]:
    for route in _federation(request).route_catalog(request.app):
        if route["route_id"] == route_id:
            return {
                "schema": "HHS_PASS_201_PUBLIC_ROUTE_DETAIL_V1",
                "contract": CONTRACT,
                "classification": CLASSIFICATION,
                "route": route,
            }
    raise HTTPException(status_code=404, detail=f"unknown public route: {route_id}")


@router.get("/services")
def public_api_services(request: Request) -> Dict[str, Any]:
    services = _federation(request).service_catalog(request.app)
    return {
        "schema": "HHS_PASS_201_PUBLIC_SERVICE_CATALOG_V1",
        "contract": CONTRACT,
        "classification": CLASSIFICATION,
        "service_count": len(services),
        "services": services,
    }


@router.get("/services/{service_id}")
def public_api_service_detail(service_id: str, request: Request) -> Dict[str, Any]:
    federation = _federation(request)
    routes = federation.route_catalog(request.app)
    for service in federation.service_catalog(request.app):
        if service["service_id"] == service_id:
            route_ids = set(service["route_ids"])
            return {
                "schema": "HHS_PASS_201_PUBLIC_SERVICE_DETAIL_V1",
                "contract": CONTRACT,
                "classification": CLASSIFICATION,
                "service": service,
                "routes": [route for route in routes if route["route_id"] in route_ids],
            }
    raise HTTPException(status_code=404, detail=f"unknown public service: {service_id}")


@router.get("/passes")
def public_api_passes(request: Request) -> Dict[str, Any]:
    passes = _federation(request).pass_catalog(request.app)
    return {
        "schema": "HHS_PASS_201_PUBLIC_PASS_MODULE_CATALOG_V1",
        "contract": CONTRACT,
        "classification": CLASSIFICATION,
        "pass_module_count": len(passes),
        "passes": passes,
    }


@router.get("/passes/{module_name:path}")
def public_api_pass_detail(module_name: str, request: Request) -> Dict[str, Any]:
    for pass_module in _federation(request).pass_catalog(request.app):
        if pass_module["module_name"] == module_name:
            return {
                "schema": "HHS_PASS_201_PUBLIC_PASS_MODULE_DETAIL_V1",
                "contract": CONTRACT,
                "classification": CLASSIFICATION,
                "pass_module": pass_module,
            }
    raise HTTPException(status_code=404, detail=f"unknown pass module: {module_name}")


@router.get("/openapi")
def public_api_openapi(request: Request) -> Dict[str, Any]:
    return request.app.openapi()


@router.get("/tools")
def public_api_tools() -> Dict[str, Any]:
    tools = [
        {"name": "public.status", "description": "Return federation closure and registration status."},
        {"name": "public.catalog", "description": "Return the complete public API catalog."},
        {"name": "public.routes", "description": "Return every registered public route."},
        {"name": "public.services", "description": "Return every registered public service."},
        {"name": "public.passes", "description": "Return every discovered pass module."},
        {"name": "public.openapi", "description": "Return the complete OpenAPI document."},
    ]
    return {
        "schema": "HHS_PASS_201_PUBLIC_TOOL_CATALOG_V1",
        "contract": CONTRACT,
        "classification": CLASSIFICATION,
        "tool_count": len(tools),
        "tools": tools,
        "arbitrary_python_execution_public": False,
    }


@router.post("/tools/invoke")
def public_api_tool_invoke(request_body: PublicToolInvokeRequest, request: Request) -> Dict[str, Any]:
    federation = _federation(request)
    operations = {
        "public.status": lambda: federation.status(request.app),
        "public.catalog": lambda: federation.catalog(request.app),
        "public.routes": lambda: public_api_routes(request),
        "public.services": lambda: public_api_services(request),
        "public.passes": lambda: public_api_passes(request),
        "public.openapi": lambda: request.app.openapi(),
    }
    operation = operations.get(request_body.tool)
    if operation is None:
        raise HTTPException(status_code=404, detail=f"unknown public tool: {request_body.tool}")
    return {
        "schema": "HHS_PASS_201_PUBLIC_TOOL_INVOCATION_V1",
        "contract": CONTRACT,
        "classification": CLASSIFICATION,
        "tool": request_body.tool,
        "arguments": request_body.arguments,
        "result": operation(),
        "tool_server_is_runtime_authority": False,
    }

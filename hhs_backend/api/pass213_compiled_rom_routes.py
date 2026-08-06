"""Pass 213 Iteration 9 governed HTTP projection routes."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import _contract_response
from hhs_backend.runtime.hhs_pass213_governed_surface_v2 import (
    Pass213GovernedSurface,
    Pass213SurfaceAuthorizationError,
    Pass213SurfaceError,
    Pass213SurfaceIntegrityError,
    Pass213SurfaceNotFoundError,
    Pass213SurfaceValidationError,
    get_default_pass213_surface,
)

router = APIRouter(
    tags=[
        "runtime",
        "pass213",
        "compiled-rom",
        "memory-integrity",
        "moving-tensor",
        "timestamp-boundary",
        "inventory",
        "governed-projection",
    ]
)


class ProjectionLookupRequest(BaseModel):
    object_id: str = Field(min_length=1, max_length=512)


_SURFACE_OVERRIDE: Pass213GovernedSurface | None = None


def configure_pass213_governed_surface(
    surface: Pass213GovernedSurface | None,
) -> Pass213GovernedSurface | None:
    """Install an explicit process-local surface for application wiring/tests."""
    global _SURFACE_OVERRIDE
    previous = _SURFACE_OVERRIDE
    _SURFACE_OVERRIDE = surface
    return previous


def _surface() -> Pass213GovernedSurface:
    return _SURFACE_OVERRIDE or get_default_pass213_surface()


def _capability(
    authorization: str | None,
    x_hhs_capability: str | None,
) -> str | None:
    bearer: str | None = None
    if authorization:
        scheme, separator, value = authorization.partition(" ")
        if separator != " " or scheme.lower() != "bearer" or not value.strip():
            raise HTTPException(
                status_code=401,
                detail={
                    "schema": "HHS_PASS_213_CAPABILITY_REJECTION_V1",
                    "ok": False,
                    "reason": "PASS213_CAPABILITY_AUTHORIZATION_HEADER_INVALID",
                },
            )
        bearer = value.strip()
    if bearer and x_hhs_capability and bearer != x_hhs_capability:
        raise HTTPException(
            status_code=401,
            detail={
                "schema": "HHS_PASS_213_CAPABILITY_REJECTION_V1",
                "ok": False,
                "reason": "PASS213_CAPABILITY_HEADERS_CONFLICT",
            },
        )
    return bearer or x_hhs_capability


def _invoke(
    *,
    route: str,
    method: str,
    operation: str,
    arguments: Dict[str, Any] | None = None,
    authorization: str | None = None,
    x_hhs_capability: str | None = None,
) -> Dict[str, Any]:
    try:
        payload = _surface().invoke(
            operation,
            arguments or {},
            capability=_capability(authorization, x_hhs_capability),
        )
    except Pass213SurfaceAuthorizationError as exc:
        raise HTTPException(
            status_code=403,
            detail={
                "schema": "HHS_PASS_213_GOVERNED_SURFACE_REJECTION_V1",
                "ok": False,
                "classification": type(exc).__name__,
                "reason": str(exc),
            },
        ) from exc
    except Pass213SurfaceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "schema": "HHS_PASS_213_GOVERNED_SURFACE_REJECTION_V1",
                "ok": False,
                "classification": type(exc).__name__,
                "reason": str(exc),
            },
        ) from exc
    except Pass213SurfaceIntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "schema": "HHS_PASS_213_GOVERNED_SURFACE_REJECTION_V1",
                "ok": False,
                "classification": type(exc).__name__,
                "reason": str(exc),
            },
        ) from exc
    except Pass213SurfaceValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "schema": "HHS_PASS_213_GOVERNED_SURFACE_REJECTION_V1",
                "ok": False,
                "classification": type(exc).__name__,
                "reason": str(exc),
            },
        ) from exc
    except (OSError, Pass213SurfaceError) as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "schema": "HHS_PASS_213_GOVERNED_SURFACE_REJECTION_V1",
                "ok": False,
                "classification": type(exc).__name__,
                "reason": str(exc),
            },
        ) from exc
    return _contract_response(route, method, payload)


@router.get("/api/runtime/pass213/status")
def pass213_status() -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/pass213/status",
        method="GET",
        operation="surface.status",
    )


@router.get("/api/runtime/pass213/catalog")
def pass213_catalog() -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/pass213/catalog",
        method="GET",
        operation="surface.catalog",
    )


@router.get("/api/runtime/compiled-rom/status")
def compiled_rom_status() -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/compiled-rom/status",
        method="GET",
        operation="compiled.status",
    )


@router.post("/api/runtime/compiled-rom/lookup")
def compiled_rom_lookup(
    request: ProjectionLookupRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_hhs_capability: str | None = Header(default=None, alias="X-HHS-Capability"),
) -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/compiled-rom/lookup",
        method="POST",
        operation="compiled.lookup",
        arguments={"object_id": request.object_id},
        authorization=authorization,
        x_hhs_capability=x_hhs_capability,
    )


@router.get("/api/runtime/memory-integrity/status")
def memory_integrity_status() -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/memory-integrity/status",
        method="GET",
        operation="surface.status",
    )


@router.post("/api/runtime/memory-integrity/scan")
def memory_integrity_scan(
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_hhs_capability: str | None = Header(default=None, alias="X-HHS-Capability"),
) -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/memory-integrity/scan",
        method="POST",
        operation="integrity.scan",
        authorization=authorization,
        x_hhs_capability=x_hhs_capability,
    )


@router.get("/api/runtime/timestamp-boundary/status")
def timestamp_boundary_status() -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/timestamp-boundary/status",
        method="GET",
        operation="timestamp.status",
    )


@router.post("/api/runtime/timestamp-boundary/lookup")
def timestamp_boundary_lookup(
    request: ProjectionLookupRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_hhs_capability: str | None = Header(default=None, alias="X-HHS-Capability"),
) -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/timestamp-boundary/lookup",
        method="POST",
        operation="timestamp.lookup",
        arguments={"object_id": request.object_id},
        authorization=authorization,
        x_hhs_capability=x_hhs_capability,
    )


@router.get("/api/runtime/tensor-lattice/status")
def tensor_lattice_status() -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/tensor-lattice/status",
        method="GET",
        operation="tensor.status",
    )


@router.post("/api/runtime/tensor-lattice/lookup")
def tensor_lattice_lookup(
    request: ProjectionLookupRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_hhs_capability: str | None = Header(default=None, alias="X-HHS-Capability"),
) -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/tensor-lattice/lookup",
        method="POST",
        operation="tensor.lookup",
        arguments={"object_id": request.object_id},
        authorization=authorization,
        x_hhs_capability=x_hhs_capability,
    )


@router.post("/api/runtime/tensor-lattice/verify")
def tensor_lattice_verify(
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_hhs_capability: str | None = Header(default=None, alias="X-HHS-Capability"),
) -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/tensor-lattice/verify",
        method="POST",
        operation="tensor.verify",
        authorization=authorization,
        x_hhs_capability=x_hhs_capability,
    )


@router.get("/api/runtime/inventory/status")
def inventory_status() -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/inventory/status",
        method="GET",
        operation="inventory.status",
    )


@router.post("/api/runtime/inventory/verify")
def inventory_verify(
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_hhs_capability: str | None = Header(default=None, alias="X-HHS-Capability"),
) -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/inventory/verify",
        method="POST",
        operation="inventory.verify",
        authorization=authorization,
        x_hhs_capability=x_hhs_capability,
    )


@router.get("/api/runtime/pass213/receipts/{object_id}")
def pass213_receipt_lookup(
    object_id: str,
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_hhs_capability: str | None = Header(default=None, alias="X-HHS-Capability"),
) -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/pass213/receipts/{object_id}",
        method="GET",
        operation="receipt.lookup",
        arguments={"object_id": object_id},
        authorization=authorization,
        x_hhs_capability=x_hhs_capability,
    )

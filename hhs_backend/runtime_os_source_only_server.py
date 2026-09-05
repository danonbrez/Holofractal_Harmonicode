"""Source-only degraded HHS Runtime OS production shell.

This module is selected only by the outermost production dispatcher when the
compiled HHS C runtime is explicitly unavailable and degraded import has been
requested. It deliberately does not import VM81, Hash72, workspace mutation,
assistant-provider, Pass-218 authority, or canonical runtime modules.

The built TypeScript Runtime OS remains available for local editing, preview,
testing, and ZIP export. Every canonical runtime or mutation surface stays
unavailable and no Python/browser replacement authority is created.
"""
from __future__ import annotations

import platform
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from hhs_backend.runtime_os_projection import project_runtime_os

PUBLIC_MOUNT_NAME = "hhs-runtime-os-application-home"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _runtime_library_path() -> Path:
    system = platform.system().lower()
    if system == "windows":
        name = "hhs_runtime.dll"
    elif system == "darwin":
        name = "libhhs_runtime.dylib"
    else:
        name = "libhhs_runtime.so"
    return REPOSITORY_ROOT / "hhs_runtime" / "builds" / name


def _c_runtime_status() -> dict[str, Any]:
    path = _runtime_library_path()
    available = path.is_file()
    return {
        "schema": "HHS_C_RUNTIME_LIBRARY_STATUS_V1",
        "ok": available,
        "available": available,
        "status": "HHS_C_RUNTIME_AVAILABLE" if available else "HHS_C_RUNTIME_UNAVAILABLE",
        "library_path": str(path),
        "source_only_degraded_mode": not available,
        "degraded_shell_selected": True,
        "canonical_runtime_authority_active": False,
        "python_replacement_authority": False,
        "browser_replacement_authority": False,
        "canonical_c_calls_fail_closed_when_unavailable": True,
    }


def _runtime_status() -> dict[str, Any]:
    c_runtime = _c_runtime_status()
    return {
        "schema": "HHS_SOURCE_ONLY_RUNTIME_STATUS_V1",
        "ok": False,
        "status": "HHS_C_RUNTIME_UNAVAILABLE",
        "canonical_runtime_attached": False,
        "graph_initialized": False,
        "websocket_ready": False,
        "authority_ready": False,
        "source_only_degraded_mode": True,
        "c_runtime": c_runtime,
        "state_hash72": None,
        "receipt_hash72": None,
        "frontend_is_authority": False,
        "python_replacement_authority": False,
    }


app = FastAPI(
    title="HHS Runtime OS Source-Only Degraded Environment",
    version="PASS185-I141-SOURCE-ONLY-V1",
    description=(
        "Finite production shell used only when compiled C runtime authority is "
        "explicitly unavailable. Local source editing/preview/export remain "
        "available; canonical execution and mutation remain closed."
    ),
)


@app.get("/health")
@app.get("/healthz")
async def source_only_health() -> dict[str, Any]:
    return {
        "schema": "HHS_SOURCE_ONLY_PRODUCTION_HEALTH_V1",
        "ok": False,
        "status": "degraded",
        "service_available": True,
        "source_only_degraded_mode": True,
        "runtime": _runtime_status(),
        "canonical_mutation_permitted": False,
        "frontend_is_authority": False,
    }


@app.get("/api/product/health")
async def source_only_product_health() -> dict[str, Any]:
    c_runtime = _c_runtime_status()
    return {
        "schema": "HHS_PRODUCTION_PRODUCT_HEALTH_V1",
        "ok": False,
        "status": "HHS_PRODUCT_EXECUTION_AUTHORITY_DEGRADED",
        "runtime": _runtime_status(),
        "assistant": {
            "schema": "HHS_PRODUCTION_ASSISTANT_STATUS_V2",
            "ok": False,
            "online": False,
            "status": "HHS_PRODUCTION_ASSISTANT_PROVIDER_UNAVAILABLE",
            "effective_mode": "UNAVAILABLE_IN_SOURCE_ONLY_MODE",
            "runtime_mutation_admitted": False,
        },
        "c_runtime": c_runtime,
        "source_only_degraded_mode": True,
        "visual_shell_only": False,
        "local_source_edit_preview_test_zip_available": True,
        "canonical_mutation_permitted": False,
        "frontend_runtime_authority": False,
        "python_replacement_authority": False,
    }


@app.get("/api/system/status")
async def source_only_system_status() -> dict[str, Any]:
    return {
        "schema": "HHS_SOURCE_ONLY_SYSTEM_STATUS_V1",
        "system": "HARMONICODE",
        "status": "SOURCE_ONLY_DEGRADED",
        "source_only_degraded_mode": True,
        "runtime_authority_available": False,
        "assistant_available": False,
        "workspace_backend_mutation_available": False,
        "local_browser_edit_preview_export_available": True,
        "frontend_is_authority": False,
    }


@app.get("/api/runtime/workspace/session")
async def source_only_workspace_session() -> dict[str, Any]:
    return {
        "schema": "HHS_SOURCE_ONLY_WORKSPACE_SESSION_V1",
        "ok": True,
        "status": "WORKSPACE_SOURCE_ONLY_LOCAL",
        "project": None,
        "project_summaries": [],
        "objects": [],
        "history": [],
        "runtime": _runtime_status(),
        "backend_mutation_available": False,
        "local_browser_edit_preview_export_available": True,
        "frontend_is_authority": False,
    }


@app.get("/api/assistant/status")
async def source_only_assistant_status() -> dict[str, Any]:
    return {
        "schema": "HHS_PRODUCTION_ASSISTANT_STATUS_V2",
        "ok": False,
        "online": False,
        "status": "HHS_PRODUCTION_ASSISTANT_PROVIDER_UNAVAILABLE",
        "effective_mode": "UNAVAILABLE_IN_SOURCE_ONLY_MODE",
        "source_only_degraded_mode": True,
        "runtime_mutation_admitted": False,
    }


@app.get("/api/runtime/installation/status")
async def source_only_installation_status() -> dict[str, Any]:
    return {
        "schema": "HHS_SOURCE_ONLY_INSTALLATION_STATUS_V1",
        "ok": False,
        "status": "HHS_C_RUNTIME_UNAVAILABLE",
        "source_only_degraded_mode": True,
        "c_runtime": _c_runtime_status(),
    }


@app.get("/api/runtime/integration/status")
async def source_only_integration_status() -> dict[str, Any]:
    return {
        "schema": "HHS_SOURCE_ONLY_INTEGRATION_STATUS_V1",
        "ok": False,
        "status": "SOURCE_ONLY_DEGRADED",
        "canonical_runtime_authority_active": False,
        "local_browser_edit_preview_export_available": True,
    }


@app.get("/api/public/status")
async def source_only_public_status() -> dict[str, Any]:
    return {
        "schema": "HHS_SOURCE_ONLY_PUBLIC_STATUS_V1",
        "ok": True,
        "status": "HHS_RUNTIME_OS_SOURCE_ONLY_PUBLIC_ROOT",
        "source_only_degraded_mode": True,
        "frontend_is_authority": False,
    }


@app.api_route(
    "/api/{unmatched_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    include_in_schema=False,
)
async def source_only_api_not_found(unmatched_path: str) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "schema": "HHS_SOURCE_ONLY_API_UNAVAILABLE_V1",
            "ok": False,
            "status": "HHS_CANONICAL_RUNTIME_UNAVAILABLE",
            "detail": {
                "classification": "HHS_C_RUNTIME_UNAVAILABLE",
                "path": f"/api/{unmatched_path}",
                "source_only_degraded_mode": True,
                "static_fallback_used": False,
                "frontend_result_fabricated": False,
                "canonical_mutation_permitted": False,
            },
        },
    )


project_runtime_os(app, mount_name=PUBLIC_MOUNT_NAME)

__all__ = ["PUBLIC_MOUNT_NAME", "REPOSITORY_ROOT", "app"]

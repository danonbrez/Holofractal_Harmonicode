"""Production Heroku entrypoint for the HHS Runtime OS.

The public root serves the compiled production interface. Only callable surfaces
are advertised. Assistant requests use the production provider hierarchy and
read-only HHS tools; authority-bearing runtime mutations remain rejected unless
a canonical runtime is attached.
"""
from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

BOOT_ID = str(uuid.uuid4())
STARTED_AT = time.time()
ROOT_DIR = Path(__file__).resolve().parents[1]
RUNTIME_OS_ROOT = ROOT_DIR / "hhs_gui" / "dist"
PASS161_ROOT = ROOT_DIR / "applications" / "holofractal_harmonizer"
SWARM_DEMO_ROOT = ROOT_DIR / "apps" / "unified_gui"

app = FastAPI(
    title="HHS Runtime OS",
    version="2.0.0",
    description="Production HHS visual IDE and governed assistant API.",
)


def _detached_rejection(
    *,
    endpoint: str,
    envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema": "HHS_DETACHED_RUNTIME_REJECTION_V1",
        "ok": False,
        "status": "REJECT_RUNTIME_AUTHORITY_UNAVAILABLE",
        "endpoint": endpoint,
        "deployment_mode": "PRODUCTION_READ_ONLY_RUNTIME",
        "canonical_runtime_attached": False,
        "canonical_runtime_mutated": False,
        "gui_mutated_runtime_truth": False,
        "receipt_hash72": None,
        "envelope": envelope or {},
    }


@app.get("/healthz")
@app.get("/health")
async def health() -> dict[str, Any]:
    from hhs_backend.runtime.hhs_production_assistant_v1 import (
        DEFAULT_PRODUCTION_ASSISTANT_SERVICE,
    )

    assistant_status = DEFAULT_PRODUCTION_ASSISTANT_SERVICE.status()
    return {
        "ok": True,
        "status": "healthy",
        "mode": "HHS_PRODUCTION_RUNTIME_OS",
        "boot_id": BOOT_ID,
        "uptime_seconds": time.time() - STARTED_AT,
        "default_interface": "HHS_RUNTIME_OS_PRODUCTION_IDE",
        "runtime_os_bundle_present": (RUNTIME_OS_ROOT / "index.html").is_file(),
        "assistant_online": True,
        "assistant_mode": assistant_status.get("effective_mode"),
        "model_online": assistant_status.get("model_online", False),
        "canonical_runtime_attached": False,
    }


@app.get("/api/system/status")
async def system_status() -> dict[str, Any]:
    return {
        "schema": "HHS_PUBLIC_SYSTEM_STATUS_V2",
        "system": "HARMONICODE",
        "status": "online",
        "deployment_mode": "HHS_PRODUCTION_RUNTIME_OS",
        "boot_id": BOOT_ID,
        "default_interface": "HHS_RUNTIME_OS_PRODUCTION_IDE",
        "assistant_api": "/api/assistant",
        "capability_api": "/api/product/capabilities",
        "harmonicode_analysis_api": "/api/workspace/harmonicode/analyze",
        "runtime_authority": "DETACHED_READ_ONLY_PROJECTION",
    }


@app.get("/api/product/capabilities")
async def product_capabilities() -> dict[str, Any]:
    return {
        "schema": "HHS_PUBLIC_PRODUCT_CAPABILITIES_V1",
        "ok": True,
        "production": True,
        "demo_mode": False,
        "capabilities": [
            {
                "id": "assistant",
                "title": "Governed natural-language assistant",
                "callable": True,
                "endpoint": "/api/assistant/chat",
            },
            {
                "id": "assistant_tools",
                "title": "Read-only HHS runtime tools",
                "callable": True,
                "endpoint": "/api/assistant/tools",
            },
            {
                "id": "harmonicode_analysis",
                "title": "Repository-native HARMONICODE parse and typed IR",
                "callable": True,
                "endpoint": "/api/workspace/harmonicode/analyze",
            },
            {
                "id": "runtime_projection",
                "title": "Runtime, services, invariants, and Pass status projections",
                "callable": True,
                "endpoint": "/api/runtime/read/{surface}",
            },
        ],
        "hidden_until_callable": [
            "runtime mutation",
            "canonical compiler commit",
            "VM81 state mutation",
            "local GPU model hosting",
        ],
    }


async def _hold_projection_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.receive()
    except WebSocketDisconnect:
        return


@app.websocket("/ws/runtime")
async def runtime_socket(websocket: WebSocket) -> None:
    await _hold_projection_socket(websocket)


@app.websocket("/ws/replay")
async def replay_socket(websocket: WebSocket) -> None:
    await _hold_projection_socket(websocket)


@app.websocket("/ws/graph")
async def graph_socket(websocket: WebSocket) -> None:
    await _hold_projection_socket(websocket)


@app.websocket("/ws/transport")
async def transport_socket(websocket: WebSocket) -> None:
    await _hold_projection_socket(websocket)


_READ_SURFACES = {
    "state": "hhs_runtime_state",
    "services": "hhs_runtime_services",
    "service-status": "hhs_runtime_service_status",
    "invariants": "hhs_kernel_invariants",
    "conformance": "hhs_kernel_conformance_status",
    "pass152": "hhs_pass152_status",
    "pass152-capabilities": "hhs_pass152_capabilities",
}


@app.get("/api/runtime/read/{surface}")
async def runtime_read_surface(surface: str) -> dict[str, Any]:
    from hhs_backend.runtime.hhs_assistant_api_tool_gateway_v1 import (
        execute_hhs_assistant_api_tool,
    )

    tool_name = _READ_SURFACES.get(surface)
    if tool_name is None:
        raise HTTPException(
            status_code=404,
            detail={
                "ok": False,
                "status": "RUNTIME_READ_SURFACE_UNKNOWN",
                "surface": surface,
                "available": sorted(_READ_SURFACES),
            },
        )
    return await execute_hhs_assistant_api_tool(tool_name, {})


@app.post("/api/workspace/harmonicode/analyze")
async def harmonicode_analyze(payload: dict[str, Any]) -> dict[str, Any]:
    source = str(payload.get("source") or "")
    if not source.strip():
        raise HTTPException(status_code=422, detail="HARMONICODE source is required")
    from native_projects.hhs_harmonicode_language.hhs_harmonicode_language_service_v1 import (
        HarmonicodeLanguageService,
    )

    analysis_id = uuid.uuid4().hex
    try:
        result = HarmonicodeLanguageService().parse(
            source,
            document_id=f"public-document:{analysis_id}",
            ir_id=f"public-ir:{analysis_id}",
            source_ref="public-runtime-os-editor",
            source_kind="HARMONICODE",
            source_root_hash72="",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "schema": "HHS_HARMONICODE_ANALYSIS_REJECTION_V1",
                "ok": False,
                "classification": type(exc).__name__,
                "message": str(exc),
            },
        ) from exc
    return {
        "schema": "HHS_PUBLIC_HARMONICODE_ANALYSIS_V1",
        "ok": True,
        "analysis_id": analysis_id,
        "result": result,
        "program_effects_executed": False,
        "runtime_mutation_admitted": False,
    }


@app.post("/api/runtime/gui/command")
async def detached_gui_command(payload: dict[str, Any]) -> dict[str, Any]:
    return _detached_rejection(endpoint="/api/runtime/gui/command", envelope=payload)


@app.post("/api/runtime/workspace/command")
async def detached_workspace_command(payload: dict[str, Any]) -> dict[str, Any]:
    return _detached_rejection(endpoint="/api/runtime/workspace/command", envelope=payload)


@app.api_route(
    "/api/runtime/{runtime_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def detached_runtime_fallback(
    runtime_path: str,
    request: Request,
) -> dict[str, Any]:
    envelope: dict[str, Any] = {}
    if request.method != "GET":
        try:
            candidate = await request.json()
            if isinstance(candidate, dict):
                envelope = candidate
        except Exception:
            envelope = {}
    return _detached_rejection(
        endpoint=f"/api/runtime/{runtime_path}",
        envelope=envelope,
    )


from hhs_backend.api.litert_lm_assistant_routes import router as assistant_router

app.include_router(assistant_router)


if (PASS161_ROOT / "index.html").is_file():
    app.mount(
        "/legacy-assistant",
        StaticFiles(directory=str(PASS161_ROOT), html=True),
        name="hhs-legacy-assistant",
    )

if (SWARM_DEMO_ROOT / "index.html").is_file():
    app.mount(
        "/diagnostics/swarm",
        StaticFiles(directory=str(SWARM_DEMO_ROOT), html=True),
        name="hhs-swarm-diagnostic",
    )

if (RUNTIME_OS_ROOT / "index.html").is_file():
    app.mount(
        "/",
        StaticFiles(directory=str(RUNTIME_OS_ROOT), html=True),
        name="hhs-runtime-os-production-ide",
    )
else:
    @app.get("/", response_class=HTMLResponse)
    async def fallback_home() -> str:
        return """<!doctype html><html><head><meta charset='utf-8'><title>HHS Runtime OS</title></head>
        <body style='background:#050912;color:#e8eef8;font-family:system-ui;padding:2rem'>
        <h1>HHS Runtime OS build unavailable</h1>
        <p>The production frontend bundle was not included in this release.</p>
        <p><a style='color:#8bd5ff' href='/healthz'>View deployment health</a></p>
        </body></html>"""

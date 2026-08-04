"""Canonical production server for the verified HHS visual environment.

This module composes the authoritative HHS backend with the governed assistant,
Pass 165 multimodal lifecycle, Pass 166 language-memory, Pass 172 installation
status, runtime-authority, and product-health routes. The public root is the
front-and-center Holofractal Harmonizer Visual IDE. Runtime execution remains
owned by ``hhs_backend.server``.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

# Hosted production must always have an executable language authority even when
# a large external LiteRT-LM model or Pass 166 vector package has not yet been
# provisioned. Gemma remains preferred whenever its registry is ready.
os.environ.setdefault("HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC", "0")
os.environ.setdefault("HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS", "5")

from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from hhs_backend import server as canonical
from hhs_backend.api.development_lifecycle_routes import router as development_lifecycle_router
from hhs_backend.api.installation_routes import router as installation_router
from hhs_backend.api.litert_lm_assistant_routes import router as assistant_router
from hhs_backend.api.pass210_llm_orchestrator_routes import router as pass210_llm_router
from hhs_backend.api.pass165_multimodal_ingress_routes import router as pass165_router
from hhs_backend.api.pass166_word2vec_routes import router as word2vec_router

ROOT_DIR = Path(__file__).resolve().parents[1]
VISUAL_ROOT = ROOT_DIR / "applications" / "holofractal_harmonizer"
VISUAL_SOURCE_ROOT = VISUAL_ROOT / "src"
VISUAL_SOURCE_MOUNT_NAME = "hhs-production-source-assets"

app = canonical.app
app.title = "HHS Holofractal Harmonizer"
app.version = "3.4.1"
app.description = (
    "Canonical HHS runtime and front-and-center visual IDE with source-preserving "
    "multimodal ingress, Hash216 indexing, exact 5,184-bit VM snapshots, HHS "
    "interpretation, compilation, bounded VM81 execution, receipts, replay, egress, "
    "workspace, installation, language-memory, and assistant services."
)


def _has_route_prefix(prefix: str) -> bool:
    return any(str(getattr(route, "path", "")).startswith(prefix) for route in app.router.routes)


def _has_exact_route(path: str) -> bool:
    return any(str(getattr(route, "path", "")) == path for route in app.router.routes)


if not _has_exact_route("/api/assistant/chat") or not _has_exact_route("/api/assistant/health"):
    app.include_router(assistant_router)
if not _has_route_prefix("/api/runtime/llm-orchestrator"):
    app.include_router(pass210_llm_router)
if not _has_route_prefix("/v1/modalities/language"):
    app.include_router(word2vec_router)
if not _has_route_prefix("/api/runtime/installation"):
    app.include_router(installation_router)
if not _has_route_prefix("/api/runtime/multimodal-ingress"):
    app.include_router(pass165_router)
if not _has_route_prefix("/api/runtime/development"):
    app.include_router(development_lifecycle_router)

# Remove only prior root projections or static root mounts. Every API and
# WebSocket route remains registered before the verified visual application.
app.router.routes = [
    route
    for route in app.router.routes
    if not (
        getattr(route, "path", None) in {"", "/"}
        and (
            "GET" in (getattr(route, "methods", None) or set())
            or getattr(route, "name", None) in {
                "hhs-canonical-visual-runtime-os",
                "hhs-visual-home",
                "hhs-production-harmonizer",
            }
        )
    )
]


def _object_summary(obj: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "object_id": obj.get("object_id"),
        "name": obj.get("name"),
        "object_type": obj.get("object_type"),
        "modality": obj.get("modality"),
        "lifecycle_state": obj.get("lifecycle_state"),
        "root_hash72": obj.get("current_root_hash72") or obj.get("object_root_hash72"),
        "receipt_tip_hash72": obj.get("receipt_tip_hash72"),
        "source_uri": (obj.get("source_provenance") or {}).get("source_uri") or obj.get("canonical_payload_ref"),
    }


def _workspace_session_snapshot(project_id: str | None = None) -> dict[str, Any]:
    loop = canonical.WORKSPACE_AUTHORITY_LOOP
    projects = list(loop.projects.values())
    projects.sort(
        key=lambda item: int(item.get("updated_at_unix_ms") or item.get("created_at_unix_ms") or 0),
        reverse=True,
    )
    active = loop.projects.get(project_id or "") if project_id else None
    if active is None and projects:
        active = projects[0]

    objects: list[dict[str, Any]] = []
    if active:
        registry = dict(active.get("object_registry") or {})
        order = list(active.get("object_order") or registry.keys())
        objects = [_object_summary(registry[object_id]) for object_id in order if object_id in registry]

    history = []
    for decision in loop.command_history[-24:]:
        result = dict(decision.get("result") or {})
        command = dict(decision.get("command") or {})
        history.append({
            "command_id": command.get("command_id"),
            "operation": command.get("operation"),
            "ok": bool(decision.get("ok")),
            "status": decision.get("status"),
            "receipt_hash72": decision.get("receipt_hash72"),
            "result_schema": result.get("schema"),
        })

    return {
        "schema": "HHS_INTEGRATED_WORKSPACE_SESSION_V1",
        "ok": True,
        "status": "WORKSPACE_LIVE" if active else "WORKSPACE_EMPTY",
        "project": active,
        "project_summaries": [
            {
                "project_id": project.get("project_id"),
                "name": project.get("name"),
                "status": project.get("status"),
                "object_count": len(project.get("object_registry") or {}),
                "receipt_tip_hash72": project.get("receipt_tip_hash72"),
                "updated_at_unix_ms": project.get("updated_at_unix_ms"),
            }
            for project in projects
        ],
        "objects": objects,
        "history": history,
        "runtime": {
            "canonical_runtime_attached": bool(canonical.SERVER_STATE.get("runtime_initialized")),
            "graph_initialized": bool(canonical.SERVER_STATE.get("graph_initialized")),
            "websocket_ready": bool(canonical.SERVER_STATE.get("websocket_ready")),
            "live_workflow": canonical.LIVE_WORKFLOW.status(),
        },
        "self_tests_executed": False,
    }


@app.get("/api/runtime/workspace/session")
async def production_workspace_session(project_id: str | None = None) -> dict[str, Any]:
    return _workspace_session_snapshot(project_id)


@app.post("/api/runtime/workspace/session")
async def production_workspace_session_ensure(payload: dict[str, Any]) -> dict[str, Any]:
    requested_id = str(payload.get("project_id") or "")
    if requested_id and requested_id in canonical.WORKSPACE_AUTHORITY_LOOP.projects:
        return _workspace_session_snapshot(requested_id)

    project = canonical.create_workspace_project(str(payload.get("name") or "HHS Workspace"))
    canonical.WORKSPACE_AUTHORITY_LOOP.projects[project["project_id"]] = project
    return _workspace_session_snapshot(project["project_id"])


async def _assistant_health() -> dict[str, Any]:
    try:
        from hhs_backend.runtime.hhs_pass210_production_assistant_v1 import (
            DEFAULT_PASS210_PRODUCTION_ASSISTANT,
        )

        DEFAULT_PASS210_PRODUCTION_ASSISTANT._health_timeout = max(
            float(DEFAULT_PASS210_PRODUCTION_ASSISTANT._health_timeout),
            5.0,
        )
        return await DEFAULT_PASS210_PRODUCTION_ASSISTANT.health()
    except Exception as exc:
        return {
            "ok": False,
            "online": False,
            "status": "ASSISTANT_HEALTH_ERROR",
            "error": f"{type(exc).__name__}: {exc}",
        }


def _runtime_authority_status() -> dict[str, Any]:
    workflow = canonical.LIVE_WORKFLOW.status()
    runtime_state = canonical.runtime_controller.latest_runtime_state()
    last_emission = dict(workflow.get("last_emission") or {})
    receipt_hash72 = last_emission.get("receipt_hash72") or runtime_state.get("receipt_hash72")
    state_hash72 = last_emission.get("runtime_state_hash72") or runtime_state.get("state_hash72")
    authority_ready = bool(
        canonical.SERVER_STATE.get("runtime_initialized")
        and canonical.SERVER_STATE.get("graph_initialized")
        and canonical.SERVER_STATE.get("websocket_ready")
        and workflow.get("running")
        and workflow.get("authority_ready")
        and receipt_hash72
        and state_hash72
    )
    return {
        "schema": "HHS_PRODUCTION_RUNTIME_AUTHORITY_STATUS_V1",
        "ok": authority_ready,
        "status": "HHS_RUNTIME_AUTHORITY_ONLINE" if authority_ready else "HHS_RUNTIME_AUTHORITY_WARMING",
        "canonical_runtime_attached": bool(canonical.SERVER_STATE.get("runtime_initialized")),
        "graph_initialized": bool(canonical.SERVER_STATE.get("graph_initialized")),
        "websocket_ready": bool(canonical.SERVER_STATE.get("websocket_ready")),
        "receipt_hash72": receipt_hash72,
        "runtime_state_hash72": state_hash72,
        "live_workflow": workflow,
        "runtime": runtime_state,
        "authority": "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1",
        "frontend_is_authority": False,
    }


@app.get("/api/runtime/authority/status")
async def production_runtime_authority_status() -> dict[str, Any]:
    return _runtime_authority_status()


@app.get("/api/product/health")
async def production_product_health() -> dict[str, Any]:
    runtime = _runtime_authority_status()
    assistant = await _assistant_health()
    return {
        "schema": "HHS_PRODUCTION_PRODUCT_HEALTH_V1",
        "ok": bool(runtime.get("ok") and assistant.get("online")),
        "status": (
            "HHS_PRODUCT_EXECUTION_AUTHORITIES_ONLINE"
            if runtime.get("ok") and assistant.get("online")
            else "HHS_PRODUCT_EXECUTION_AUTHORITY_DEGRADED"
        ),
        "runtime": runtime,
        "assistant": assistant,
        "visual_shell_only": False,
        "public_interface": "HHS_PASS_174_FRONT_AND_CENTER_VISUAL_IDE",
        "hosted_native_assistant_word2vec_required": False,
        "gemma_preferred_when_registered": True,
    }


@app.get("/healthz")
async def production_health() -> dict[str, Any]:
    canonical_health = await canonical.health()
    assistant_health = await _assistant_health()
    visual_present = (VISUAL_ROOT / "index.html").is_file()
    runtime_status = _runtime_authority_status()
    fully_ready = bool(visual_present and runtime_status.get("ok") and assistant_health.get("online"))
    return {
        "schema": "HHS_CANONICAL_PRODUCTION_HEALTH_V1",
        "ok": fully_ready,
        "status": "healthy" if fully_ready else "degraded",
        "interface": "HHS_PASS_174_FRONT_AND_CENTER_VISUAL_IDE",
        "visual_application_present": visual_present,
        "canonical_runtime_attached": bool(canonical.SERVER_STATE.get("runtime_initialized")),
        "graph_initialized": bool(canonical.SERVER_STATE.get("graph_initialized")),
        "websocket_ready": bool(canonical.SERVER_STATE.get("websocket_ready")),
        "runtime_authority": runtime_status,
        "assistant": assistant_health,
        "canonical": canonical_health,
    }


@app.get("/api/system/status")
async def production_system_status() -> dict[str, Any]:
    return {
        "schema": "HHS_CANONICAL_PRODUCTION_SYSTEM_STATUS_V1",
        "system": "HARMONICODE",
        "interface": "HHS_PASS_174_FRONT_AND_CENTER_VISUAL_IDE",
        "visual_environment": "HHS-P174-HPG-EH216-RAVWSC-VFIDE-SDLC",
        "usability_default": "WORKFLOW_FIRST_PROGRESSIVE_DISCLOSURE",
        "canonical_runtime_attached": bool(canonical.SERVER_STATE.get("runtime_initialized")),
        "graph_initialized": bool(canonical.SERVER_STATE.get("graph_initialized")),
        "websocket_ready": bool(canonical.SERVER_STATE.get("websocket_ready")),
        "runtime_authority_api": "/api/runtime/authority/status",
        "product_health_api": "/api/product/health",
        "workspace_session_api": "/api/runtime/workspace/session",
        "workspace_api": "/api/runtime/workspace",
        "runtime_api": "/api/runtime",
        "runtime_services_api": "/api/runtime/services",
        "capability_api": "/api/runtime/capability",
        "document_api": "/api/runtime/document",
        "multimodal_ingress_api": "/api/runtime/multimodal-ingress",
        "development_lifecycle_api": "/api/runtime/development/lifecycle",
        "assistant_api": "/api/assistant",
        "installation_api": "/api/runtime/installation",
        "word2vec_api": "/v1/modalities/language",
    }


@app.api_route(
    "/api/{unmatched_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    include_in_schema=False,
)
async def production_api_not_found(unmatched_path: str) -> JSONResponse:
    """Prevent unknown API requests from falling through to the HTML SPA mount."""
    return JSONResponse(
        status_code=404,
        content={
            "schema": "HHS_PRODUCTION_API_ROUTE_NOT_FOUND_V1",
            "ok": False,
            "status": "HHS_API_ROUTE_NOT_FOUND",
            "detail": {
                "classification": "HHS_API_ROUTE_NOT_FOUND",
                "path": f"/api/{unmatched_path}",
                "static_fallback_used": False,
                "frontend_result_fabricated": False,
            },
        },
    )


# Serve the browser module graph through a dedicated mount before any inherited
# root SPA mount. Successor composition layers retain this route, preventing
# root-mount replacement from turning the IDE into an HTML-only shell.
app.router.routes = [
    route
    for route in app.router.routes
    if getattr(route, "name", None) != VISUAL_SOURCE_MOUNT_NAME
]
if VISUAL_SOURCE_ROOT.is_dir():
    app.mount(
        "/src",
        StaticFiles(directory=str(VISUAL_SOURCE_ROOT)),
        name=VISUAL_SOURCE_MOUNT_NAME,
    )

if (VISUAL_ROOT / "index.html").is_file():
    app.mount(
        "/",
        StaticFiles(directory=str(VISUAL_ROOT), html=True),
        name="hhs-production-harmonizer",
    )
else:
    @app.get("/", response_class=HTMLResponse)
    async def missing_visual_application() -> str:
        return """<!doctype html><html><head><meta charset='utf-8'><title>HHS Holofractal Harmonizer</title></head>
        <body style='background:#050912;color:#fff;font-family:system-ui;padding:2rem'>
        <h1>Verified Pass 174 visual application unavailable</h1>
        <p>Expected <code>applications/holofractal_harmonizer/index.html</code>.</p>
        <p><a style='color:#67e8f9' href='/healthz'>View canonical backend health</a></p>
        </body></html>"""
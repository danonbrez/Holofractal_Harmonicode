"""Canonical production server for the HHS Visual Runtime OS.

This module composes the repository's authoritative backend server with the
assistant and Pass 166 language-memory routers, then serves the compiled
canonical IDE. It does not replace runtime operations with detached or demo
responses.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from hhs_backend import server as canonical
from hhs_backend.api.litert_lm_assistant_routes import router as assistant_router
from hhs_backend.api.pass166_word2vec_routes import router as word2vec_router

ROOT_DIR = Path(__file__).resolve().parents[1]
RUNTIME_OS_ROOT = ROOT_DIR / "hhs_gui" / "dist"

app = canonical.app
app.title = "HHS Visual Runtime OS"
app.version = "3.0.0"
app.description = (
    "Canonical HHS runtime, workspace, graph, replay, receipt, multimodal, "
    "capability, document, language-memory, and assistant server."
)


def _has_route_prefix(prefix: str) -> bool:
    return any(str(getattr(route, "path", "")).startswith(prefix) for route in app.router.routes)


if not _has_route_prefix("/api/assistant"):
    app.include_router(assistant_router)
if not _has_route_prefix("/v1/modalities/language"):
    app.include_router(word2vec_router)

# The canonical development server exposes JSON at `/`. Production serves the
# actual Runtime OS HTML there while preserving every API and WebSocket route.
app.router.routes = [
    route
    for route in app.router.routes
    if not (
        getattr(route, "path", None) == "/"
        and "GET" in (getattr(route, "methods", None) or set())
    )
]


@app.get("/healthz")
async def production_health() -> dict[str, Any]:
    canonical_health = await canonical.health()
    assistant_health: dict[str, Any]
    try:
        from hhs_backend.runtime.hhs_production_assistant_v1 import (
            DEFAULT_PRODUCTION_ASSISTANT_SERVICE,
        )

        assistant_health = await DEFAULT_PRODUCTION_ASSISTANT_SERVICE.health()
    except Exception as exc:
        assistant_health = {
            "ok": False,
            "online": False,
            "status": "ASSISTANT_HEALTH_ERROR",
            "error": f"{type(exc).__name__}: {exc}",
        }

    bundle_present = (RUNTIME_OS_ROOT / "index.html").is_file()
    return {
        "schema": "HHS_CANONICAL_PRODUCTION_HEALTH_V1",
        "ok": bool(bundle_present and canonical.SERVER_STATE.get("runtime_initialized")),
        "status": "healthy" if bundle_present and canonical.SERVER_STATE.get("runtime_initialized") else "degraded",
        "interface": "HHS_VISUAL_RUNTIME_OS_WORKSPACE",
        "runtime_os_bundle_present": bundle_present,
        "canonical_runtime_attached": bool(canonical.SERVER_STATE.get("runtime_initialized")),
        "graph_initialized": bool(canonical.SERVER_STATE.get("graph_initialized")),
        "websocket_ready": bool(canonical.SERVER_STATE.get("websocket_ready")),
        "assistant": assistant_health,
        "canonical": canonical_health,
    }


@app.get("/api/system/status")
async def production_system_status() -> dict[str, Any]:
    return {
        "schema": "HHS_CANONICAL_PRODUCTION_SYSTEM_STATUS_V1",
        "system": "HARMONICODE",
        "interface": "HHS_VISUAL_RUNTIME_OS_WORKSPACE",
        "canonical_runtime_attached": bool(canonical.SERVER_STATE.get("runtime_initialized")),
        "graph_initialized": bool(canonical.SERVER_STATE.get("graph_initialized")),
        "websocket_ready": bool(canonical.SERVER_STATE.get("websocket_ready")),
        "workspace_api": "/api/runtime/workspace",
        "runtime_api": "/api/runtime",
        "capability_api": "/api/runtime/capability",
        "document_api": "/api/runtime/document",
        "assistant_api": "/api/assistant",
        "word2vec_api": "/v1/modalities/language",
    }


if (RUNTIME_OS_ROOT / "index.html").is_file():
    app.mount(
        "/",
        StaticFiles(directory=str(RUNTIME_OS_ROOT), html=True),
        name="hhs-canonical-visual-runtime-os",
    )
else:
    @app.get("/", response_class=HTMLResponse)
    async def missing_runtime_os_bundle() -> str:
        return """<!doctype html><html><head><meta charset='utf-8'><title>HHS Visual Runtime OS</title></head>
        <body style='background:#000;color:#fff;font-family:system-ui;padding:2rem'>
        <h1>Canonical Runtime OS bundle unavailable</h1>
        <p>Build <code>hhs_gui/dist</code> before starting production.</p>
        <p><a style='color:#67e8f9' href='/healthz'>View canonical backend health</a></p>
        </body></html>"""

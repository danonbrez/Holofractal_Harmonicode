"""Canonical Pass 174 production overlay.

The complete production Visual IDE, assistant, installation, multimodal,
workspace, API, WebSocket, and singleton runtime surfaces are inherited first.
Pass 174 then adds its governed runtime routes, non-blocking readiness watchdog,
and front-and-center visual workspace. The prior production visual application
is preserved at ``/legacy-ide/`` rather than deleted.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
import json
import os
from pathlib import Path
import time
from typing import Any

from fastapi.staticfiles import StaticFiles

from hhs_backend import production_ide_server as inherited_ide
from hhs_backend import production_server as inherited_production
from hhs_backend.api.pass174_runtime_routes import get_runtime, router as pass174_router
from hhs_backend.api import pass174_ws_routes as _pass174_ws_routes  # registers WebSocket routes

app = inherited_ide.app
app.title = "HHS Pass 174 Harmonic Visual SDLC Runtime"
app.version = "4.0.1"
app.description = (
    "Append-only successor to every legacy HHS pass through Pass 173, with a "
    "64:72:81 phase-gear VM81 runtime, encrypted Hash216 retrieval, governed "
    "multimodal SDLC execution, and front-and-center mobile Visual IDE."
)

PASS174_BOOT_STATE: dict[str, Any] = {
    "schema": "HHS_P174_BOOT_STATE_V1",
    "classification": "HHS_P174_BOOT_PENDING",
    "ready": False,
    "authority_ready": False,
    "service_available": False,
    "degraded": False,
    "silent_freeze": False,
    "started_monotonic": time.monotonic(),
}

_repository_root = Path(os.environ.get("HHS_REPOSITORY_ROOT") or Path(__file__).resolve().parents[1]).resolve()
_ide_root = _repository_root / "applications" / "pass174_visual_ide"
_legacy_ide_root = inherited_production.VISUAL_ROOT
_API_FALLBACK_PATH = "/api/{unmatched_path:path}"


def _has_route_prefix(prefix: str) -> bool:
    return any(str(getattr(route, "path", "")).startswith(prefix) for route in app.router.routes)


# Production Server registers a deliberate unknown-API fallback immediately
# before its static root. That fallback must remain, but any successor API
# routes added after it would otherwise be shadowed and return 404. Defer the
# fallback, remove only static roots, register Pass 174, then restore the
# fallback before the final static mount.
_deferred_api_fallback_routes = [
    route for route in app.router.routes
    if str(getattr(route, "path", "")) == _API_FALLBACK_PATH
]
app.router.routes = [
    route
    for route in app.router.routes
    if getattr(route, "name", None) not in {
        "hhs-production-harmonizer",
        "hhs-pass174-visual-ide",
        "hhs-pass174-legacy-ide",
    }
    and str(getattr(route, "path", "")) != _API_FALLBACK_PATH
]

if not _has_route_prefix("/api/v1/pass174"):
    app.include_router(pass174_router)

if _legacy_ide_root.is_dir():
    app.mount(
        "/legacy-ide",
        StaticFiles(directory=str(_legacy_ide_root), html=True),
        name="hhs-pass174-legacy-ide",
    )


def _emit_boot_event() -> None:
    """Emit one bounded machine-readable startup record to platform logs."""
    print(json.dumps(PASS174_BOOT_STATE, sort_keys=True, default=str), flush=True)


async def _pass174_readiness_probe() -> None:
    # Repository specification discovery and SQLite initialization are
    # synchronous filesystem work. Run them off the event loop so the web
    # service remains responsive while the authority becomes ready.
    runtime = await asyncio.to_thread(get_runtime)
    status = await asyncio.to_thread(runtime.status)
    if status["kernel_authorities"] != 1:
        raise RuntimeError("HHS_P174_SINGLETON_VM81_AUTHORITY_REQUIRED")
    if status["frame_bits"] != 5184 or status["frame_bytes"] != 648:
        raise RuntimeError("HHS_P174_FRAME_GEOMETRY_MISMATCH")
    foundation = status["legacy_foundation"]
    if foundation["maximum_inherited_pass"] != 173 or not foundation["minimum_foundation"]:
        raise RuntimeError("HHS_P174_LEGACY_FOUNDATION_INCOMPLETE")
    if not _ide_root.is_dir() or not (_ide_root / "index.html").is_file():
        raise RuntimeError("HHS_P174_VISUAL_IDE_ASSET_ROOT_MISSING")
    if not _has_route_prefix("/api/runtime/workspace"):
        raise RuntimeError("HHS_P174_INHERITED_WORKSPACE_ROUTE_MISSING")
    if not _has_route_prefix("/api/runtime/multimodal-ingress"):
        raise RuntimeError("HHS_P174_INHERITED_MULTIMODAL_ROUTE_MISSING")
    if not _has_route_prefix("/api/v1/pass174/ws/events"):
        raise RuntimeError("HHS_P174_LIVE_EVENT_ROUTE_MISSING")
    route_paths = [str(getattr(route, "path", "")) for route in app.router.routes]
    if _API_FALLBACK_PATH in route_paths and route_paths.index("/api/v1/pass174/status") > route_paths.index(_API_FALLBACK_PATH):
        raise RuntimeError("HHS_P174_API_ROUTE_SHADOWED_BY_FALLBACK")


async def initialize_pass174_overlay() -> bool:
    """Initialize authority without terminating the serving process on failure.

    Readiness remains fail-closed: authority endpoints continue to return their
    explicit 503/rejection classifications until initialization succeeds. The
    web process itself remains available so Heroku can route health, deployment
    status, diagnostics, and the degraded Visual IDE instead of showing H10/H20.
    """
    timeout_seconds = float(os.environ.get("HHS_PASS174_BOOT_TIMEOUT_SECONDS", "12"))
    probe_started = time.monotonic()
    try:
        await asyncio.wait_for(_pass174_readiness_probe(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        PASS174_BOOT_STATE.update({
            "classification": "HHS_P174_BOOT_FREEZE_DETECTED",
            "phase": "PASS174_READINESS_PROBE",
            "ready": False,
            "authority_ready": False,
            "service_available": True,
            "degraded": True,
            "silent_freeze": False,
            "timeout_seconds": timeout_seconds,
            "elapsed_seconds": time.monotonic() - probe_started,
            "remediation": "Inspect /api/v1/pass174/deployment/status and retry after peer recovery.",
        })
        _emit_boot_event()
        return False
    except Exception as exc:
        PASS174_BOOT_STATE.update({
            "classification": getattr(exc, "classification", "HHS_P174_BOOT_PEER_FAILURE"),
            "phase": "PASS174_READINESS_PROBE",
            "ready": False,
            "authority_ready": False,
            "service_available": True,
            "degraded": True,
            "silent_freeze": False,
            "detail": f"{type(exc).__name__}: {exc}",
            "elapsed_seconds": time.monotonic() - probe_started,
            "remediation": "Inspect platform logs and the deployment-status endpoint; runtime authority remains closed.",
        })
        _emit_boot_event()
        return False
    PASS174_BOOT_STATE.update({
        "classification": "HHS_P174_BOOT_READY",
        "phase": "COMPLETE",
        "ready": True,
        "authority_ready": True,
        "service_available": True,
        "degraded": False,
        "silent_freeze": False,
        "ready_monotonic": time.monotonic(),
        "readiness_elapsed_seconds": time.monotonic() - probe_started,
        "asset_root": str(_ide_root),
        "legacy_ide_root": str(_legacy_ide_root),
        "legacy_ide_preserved": _legacy_ide_root.is_dir(),
        "inherited_route_count": len(app.router.routes),
        "api_fallback_deferred": bool(_deferred_api_fallback_routes),
    })
    _emit_boot_event()
    return True


# The inherited production app already owns the complete canonical lifespan.
# Pass 174 starts its bounded authority probe after the serving lifespan enters;
# no recoverable peer or filesystem failure may terminate the only web dyno.
_inherited_lifespan = app.router.lifespan_context


@asynccontextmanager
async def _pass174_lifespan(app_instance):
    async with _inherited_lifespan(app_instance):
        PASS174_BOOT_STATE.update({
            "classification": "HHS_P174_BOOT_PROBING",
            "phase": "PASS174_READINESS_PROBE",
            "service_available": True,
            "authority_ready": False,
            "degraded": False,
            "silent_freeze": False,
        })
        _emit_boot_event()
        readiness_task = asyncio.create_task(
            initialize_pass174_overlay(),
            name="hhs-pass174-readiness-probe",
        )
        try:
            yield
        finally:
            if not readiness_task.done():
                readiness_task.cancel()
            with suppress(asyncio.CancelledError):
                await readiness_task


app.router.lifespan_context = _pass174_lifespan


@app.get("/api/v1/pass174/deployment/status")
async def pass174_deployment_status() -> dict[str, Any]:
    return dict(PASS174_BOOT_STATE)


# Restore the inherited unknown-API classification only after every Pass 174
# API and WebSocket route has been registered.
app.router.routes.extend(_deferred_api_fallback_routes)

# Static root must be mounted last so it can never shadow any inherited or
# Pass 174 API/WebSocket/health route registered above.
if _ide_root.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=str(_ide_root), html=True),
        name="hhs-pass174-visual-ide",
    )
else:
    PASS174_BOOT_STATE.update({
        "classification": "HHS_P174_VISUAL_IDE_ASSET_ROOT_MISSING",
        "asset_root": str(_ide_root),
        "ready": False,
        "authority_ready": False,
        "degraded": True,
    })

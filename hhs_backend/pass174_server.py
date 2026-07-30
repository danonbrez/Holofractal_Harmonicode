"""Canonical Pass 174 production overlay.

The complete production Visual IDE, assistant, installation, multimodal,
workspace, API, WebSocket, and singleton runtime surfaces are inherited first.
Pass 174 then adds its governed runtime routes, bounded readiness watchdog, and
front-and-center visual workspace. The prior production visual application is
preserved at ``/legacy-ide/`` rather than deleted.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
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
app.version = "4.0.0"
app.description = (
    "Append-only successor to every legacy HHS pass through Pass 173, with a "
    "64:72:81 phase-gear VM81 runtime, encrypted Hash216 retrieval, governed "
    "multimodal SDLC execution, and front-and-center mobile Visual IDE."
)

PASS174_BOOT_STATE: dict[str, Any] = {
    "schema": "HHS_P174_BOOT_STATE_V1",
    "classification": "HHS_P174_BOOT_PENDING",
    "ready": False,
    "silent_freeze": False,
    "started_monotonic": time.monotonic(),
}

_repository_root = Path(os.environ.get("HHS_REPOSITORY_ROOT") or Path(__file__).resolve().parents[1]).resolve()
_ide_root = _repository_root / "applications" / "pass174_visual_ide"
_legacy_ide_root = inherited_production.VISUAL_ROOT


def _has_route_prefix(prefix: str) -> bool:
    return any(str(getattr(route, "path", "")).startswith(prefix) for route in app.router.routes)


# Remove only the inherited static root mount. All API, WebSocket, assistant,
# installation, workspace, multimodal, lifecycle, and runtime routes remain.
app.router.routes = [
    route
    for route in app.router.routes
    if getattr(route, "name", None) not in {
        "hhs-production-harmonizer",
        "hhs-pass174-visual-ide",
        "hhs-pass174-legacy-ide",
    }
]

if not _has_route_prefix("/api/v1/pass174"):
    app.include_router(pass174_router)

if _legacy_ide_root.is_dir():
    app.mount(
        "/legacy-ide",
        StaticFiles(directory=str(_legacy_ide_root), html=True),
        name="hhs-pass174-legacy-ide",
    )

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
    })


async def _pass174_readiness_probe() -> None:
    runtime = get_runtime()
    status = runtime.status()
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


async def initialize_pass174_overlay() -> None:
    timeout_seconds = float(os.environ.get("HHS_PASS174_BOOT_TIMEOUT_SECONDS", "12"))
    try:
        await asyncio.wait_for(_pass174_readiness_probe(), timeout=timeout_seconds)
    except asyncio.TimeoutError as exc:
        PASS174_BOOT_STATE.update({
            "classification": "HHS_P174_BOOT_FREEZE_DETECTED",
            "phase": "PASS174_READINESS_PROBE",
            "ready": False,
            "silent_freeze": False,
            "timeout_seconds": timeout_seconds,
        })
        raise RuntimeError("HHS_P174_BOOT_FREEZE_DETECTED:PASS174_READINESS_PROBE") from exc
    except Exception as exc:
        PASS174_BOOT_STATE.update({
            "classification": getattr(exc, "classification", "HHS_P174_BOOT_PEER_FAILURE"),
            "phase": "PASS174_READINESS_PROBE",
            "ready": False,
            "silent_freeze": False,
            "detail": str(exc),
        })
        raise
    PASS174_BOOT_STATE.update({
        "classification": "HHS_P174_BOOT_READY",
        "phase": "COMPLETE",
        "ready": True,
        "silent_freeze": False,
        "ready_monotonic": time.monotonic(),
        "asset_root": str(_ide_root),
        "legacy_ide_root": str(_legacy_ide_root),
        "legacy_ide_preserved": _legacy_ide_root.is_dir(),
        "inherited_route_count": len(app.router.routes),
    })


# The inherited production app already owns the complete canonical lifespan.
# Pass 174 composes its bounded readiness gate inside that authority.
_inherited_lifespan = app.router.lifespan_context


@asynccontextmanager
async def _pass174_lifespan(app_instance):
    async with _inherited_lifespan(app_instance):
        await initialize_pass174_overlay()
        yield


app.router.lifespan_context = _pass174_lifespan


@app.get("/api/v1/pass174/deployment/status")
async def pass174_deployment_status() -> dict[str, Any]:
    return dict(PASS174_BOOT_STATE)

"""Canonical Pass 174 deployment overlay.

The existing hhs_backend.server application remains the inherited backend
origin. This module additively mounts the Pass 174 router, readiness watchdog,
and front-and-center Visual IDE without replacing legacy routes.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import os
from pathlib import Path
import time
from typing import Any

from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

from hhs_backend.server import app
from hhs_backend.api.pass174_runtime_routes import get_runtime, router as pass174_router

PASS174_BOOT_STATE: dict[str, Any] = {
    "schema": "HHS_P174_BOOT_STATE_V1",
    "classification": "HHS_P174_BOOT_PENDING",
    "ready": False,
    "silent_freeze": False,
    "started_monotonic": time.monotonic(),
}


class Pass174FrontDoorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/" and "application/json" not in request.headers.get("accept", ""):
            return RedirectResponse(url="/ide/", status_code=307)
        return await call_next(request)


app.add_middleware(Pass174FrontDoorMiddleware)
app.include_router(pass174_router)

_repository_root = Path(os.environ.get("HHS_REPOSITORY_ROOT") or Path(__file__).resolve().parents[1]).resolve()
_ide_root = _repository_root / "applications" / "pass174_visual_ide"
if not _ide_root.is_dir():
    PASS174_BOOT_STATE.update({
        "classification": "HHS_P174_VISUAL_IDE_ASSET_ROOT_MISSING",
        "asset_root": str(_ide_root),
    })
else:
    app.mount("/ide", StaticFiles(directory=str(_ide_root), html=True), name="pass174-visual-ide")


async def _pass174_readiness_probe() -> None:
    runtime = get_runtime()
    status = runtime.status()
    if status["kernel_authorities"] != 1:
        raise RuntimeError("HHS_P174_SINGLETON_VM81_AUTHORITY_REQUIRED")
    if status["frame_bits"] != 5184:
        raise RuntimeError("HHS_P174_FRAME_GEOMETRY_MISMATCH")
    if status["legacy_foundation"]["maximum_inherited_pass"] != 173:
        raise RuntimeError("HHS_P174_LEGACY_FOUNDATION_INCOMPLETE")
    if not _ide_root.is_dir():
        raise RuntimeError("HHS_P174_VISUAL_IDE_ASSET_ROOT_MISSING")


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
    })


# The inherited application already defines a lifespan context. Compose the
# Pass 174 readiness gate inside that authority rather than registering a
# second startup mechanism that FastAPI may skip when lifespan is present.
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

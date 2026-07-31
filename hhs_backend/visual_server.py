"""Default HHS visual development environment server.

This module composes the canonical HHS FastAPI runtime, the governed LiteRT-LM
assistant API, the read-only Pass 172 installation-status API, the Pass 180
integrated application-factory API, and the Pass 161 Holofractal Harmonizer
static application. The canonical server remains the runtime authority; this
module only changes the HTTP projection presented at the root path.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi.staticfiles import StaticFiles

from hhs_backend import server as canonical_server
from hhs_backend.api.application_factory_routes import router as application_factory_router
from hhs_backend.api.installation_routes import router as installation_router
from hhs_backend.api.litert_lm_assistant_routes import router as assistant_router

app = canonical_server.app


def _route_exists(path: str, name: str | None = None) -> bool:
    for route in app.router.routes:
        if getattr(route, "path", None) != path:
            continue
        if name is None or getattr(route, "name", None) == name:
            return True
    return False


if not _route_exists("/api/assistant/status"):
    app.include_router(assistant_router)

if not _route_exists("/api/runtime/installation/status"):
    app.include_router(installation_router)

if not _route_exists("/api/runtime/application-factory/status"):
    app.include_router(application_factory_router)


@app.get("/api/system/status", tags=["system"])
async def visual_system_status() -> Dict[str, Any]:
    """Preserve the former JSON root response under an explicit API path."""
    return {
        "system": "HARMONICODE",
        "status": "online",
        "boot_id": canonical_server.SERVER_BOOT_ID,
        "default_interface": "HHS_LITERT_LM_VISUAL_DEVELOPMENT_ASSISTANT",
        "assistant_api": "/api/assistant",
        "installation_api": "/api/runtime/installation",
        "application_factory_api": "/api/runtime/application-factory",
        "visual_environment": "HHS-P161-HHUMOCE",
        "application_factory": "HHS-P180-INTEGRATED-APPLICATION-FACTORY",
    }


# The canonical server historically returned JSON at `/`. Remove only that
# single projection route, leaving all runtime, health, docs, and API routes
# unchanged. StaticFiles is mounted last so every registered API route keeps
# precedence over the visual application.
app.router.routes[:] = [
    route
    for route in app.router.routes
    if not (
        getattr(route, "path", None) == "/"
        and "GET" in (getattr(route, "methods", None) or set())
        and getattr(route, "name", None) == "root"
    )
]

_visual_root = (
    Path(__file__).resolve().parents[1]
    / "applications"
    / "holofractal_harmonizer"
)
if not (_visual_root / "index.html").is_file():
    raise RuntimeError(f"Pass 161 visual application is missing: {_visual_root}")

if not any(getattr(route, "name", None) == "hhs-visual-home" for route in app.router.routes):
    app.mount(
        "/",
        StaticFiles(directory=str(_visual_root), html=True),
        name="hhs-visual-home",
    )

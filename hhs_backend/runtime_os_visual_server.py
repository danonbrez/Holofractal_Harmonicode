"""Production visual projection for the HHS TypeScript Runtime OS.

This composition layer preserves the complete canonical FastAPI/runtime surface
registered by :mod:`hhs_backend.visual_server` while replacing only its legacy
root static mount. The public root is the built React/Vite Runtime OS under
``hhs_gui/dist``. Backend/pass authority is unchanged.

The legacy Holofractal Harmonizer remains repository-visible inherited source;
it is no longer the production public-root authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi.staticfiles import StaticFiles

from hhs_backend.visual_server import app as inherited_app

ROOT_DIR = Path(__file__).resolve().parents[1]
RUNTIME_OS_ROOT = ROOT_DIR / "hhs_gui" / "dist"
RUNTIME_OS_INDEX = RUNTIME_OS_ROOT / "index.html"
RUNTIME_OS_ASSETS = RUNTIME_OS_ROOT / "assets"
PUBLIC_MOUNT_NAME = "hhs-runtime-os-home"
LEGACY_ROOT_MOUNT_NAMES = {
    "hhs-visual-home",
    "hhs-production-harmonizer",
    "hhs-production-harmonizer-index",
    "hhs-full-application-ide",
    "hhs-full-application-ide-index",
}

if not RUNTIME_OS_INDEX.is_file():
    raise RuntimeError(f"HHS Runtime OS build is missing: {RUNTIME_OS_INDEX}")
if not RUNTIME_OS_ASSETS.is_dir():
    raise RuntimeError(f"HHS Runtime OS asset directory is missing: {RUNTIME_OS_ASSETS}")

app = inherited_app
app.title = "HHS Visual Runtime OS"
app.description = (
    "Canonical HHS backend/pass authority projected through the TypeScript/React/Vite "
    "Runtime OS workspace. Runtime execution remains owned by the inherited HHS backend."
)

# Remove only root-facing legacy visual projections. API, WebSocket, studio, and
# pass routes remain exactly where the inherited application registered them.
app.router.routes = [
    route
    for route in app.router.routes
    if getattr(route, "name", None) not in LEGACY_ROOT_MOUNT_NAMES
]


@app.get("/api/interface/status", tags=["system"])
async def runtime_os_interface_status() -> Dict[str, Any]:
    """Expose the selected production interface without granting it authority."""
    return {
        "schema": "HHS_RUNTIME_OS_INTERFACE_STATUS_V1",
        "ok": True,
        "status": "HHS_RUNTIME_OS_PUBLIC_ROOT",
        "interface": "HHS_VISUAL_RUNTIME_OS_WORKSPACE",
        "frontend_stack": "typescript-react-vite",
        "asset_root": str(RUNTIME_OS_ROOT),
        "public_root": "/",
        "frontend_is_runtime_authority": False,
        "legacy_harmonizer_is_public_root": False,
    }


# Mount last so no API/WebSocket route can be shadowed by SPA fallback.
app.mount(
    "/",
    StaticFiles(directory=str(RUNTIME_OS_ROOT), html=True),
    name=PUBLIC_MOUNT_NAME,
)

__all__ = [
    "PUBLIC_MOUNT_NAME",
    "RUNTIME_OS_ASSETS",
    "RUNTIME_OS_INDEX",
    "RUNTIME_OS_ROOT",
    "app",
]

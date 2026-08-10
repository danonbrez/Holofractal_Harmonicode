"""Shared public-root projection for the HHS TypeScript Runtime OS.

The function in this module changes only FastAPI static/root projection. It does
not create runtime state, replace backend authority, or modify pass semantics.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

ROOT_DIR = Path(__file__).resolve().parents[1]
RUNTIME_OS_ROOT = ROOT_DIR / "hhs_gui" / "dist"
RUNTIME_OS_INDEX = RUNTIME_OS_ROOT / "index.html"
RUNTIME_OS_ASSETS = RUNTIME_OS_ROOT / "assets"
DEFAULT_PUBLIC_MOUNT_NAME = "hhs-runtime-os-home"

LEGACY_PUBLIC_ROOT_NAMES = {
    "hhs-canonical-visual-runtime-os",
    "hhs-visual-home",
    "hhs-production-harmonizer",
    "hhs-production-harmonizer-index",
    "hhs-pass174-visual-ide",
    "hhs-full-application-ide",
    "hhs-full-application-ide-index",
    DEFAULT_PUBLIC_MOUNT_NAME,
    "hhs-runtime-os-application-home",
}


def require_runtime_os_build() -> None:
    if not RUNTIME_OS_INDEX.is_file():
        raise RuntimeError(f"HHS Runtime OS build is missing: {RUNTIME_OS_INDEX}")
    if not RUNTIME_OS_ASSETS.is_dir():
        raise RuntimeError(f"HHS Runtime OS asset directory is missing: {RUNTIME_OS_ASSETS}")


def project_runtime_os(
    app: FastAPI,
    *,
    mount_name: str = DEFAULT_PUBLIC_MOUNT_NAME,
) -> FastAPI:
    """Replace inherited public-root UI mounts with the built Runtime OS.

    Non-root applications such as `/runtime-console`, `/storybook-reel`, and
    `/probability-hydration` are intentionally left intact. Every API and
    WebSocket route remains registered before the final SPA mount.
    """
    require_runtime_os_build()

    app.router.routes = [
        route
        for route in app.router.routes
        if getattr(route, "name", None) not in LEGACY_PUBLIC_ROOT_NAMES
    ]

    if not any(str(getattr(route, "path", "")) == "/api/interface/status" for route in app.router.routes):
        async def runtime_os_interface_status() -> dict[str, Any]:
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

        app.add_api_route(
            "/api/interface/status",
            runtime_os_interface_status,
            methods=["GET"],
            tags=["system"],
            name="hhs-runtime-os-interface-status",
        )

    app.mount(
        "/",
        StaticFiles(directory=str(RUNTIME_OS_ROOT), html=True),
        name=mount_name,
    )
    return app


__all__ = [
    "DEFAULT_PUBLIC_MOUNT_NAME",
    "LEGACY_PUBLIC_ROOT_NAMES",
    "RUNTIME_OS_ASSETS",
    "RUNTIME_OS_INDEX",
    "RUNTIME_OS_ROOT",
    "project_runtime_os",
    "require_runtime_os_build",
]

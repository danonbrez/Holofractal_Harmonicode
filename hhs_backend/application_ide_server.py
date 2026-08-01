"""Final HHS production composition with the full application IDE at ``/``.

All inherited Pass 174 APIs, VM81/Hash216 authorities, WebSockets, readiness
semantics, assistant routes, multimodal ingress, compiler services, and legacy
contracts remain registered by :mod:`hhs_backend.pass174_server`. Pass 175 adds
its VM5184 × G243 processor, encrypted terminal hydration, firmware, governed
devices, native-kernel evidence, and WebSocket surfaces before all fallbacks and
static mounts. Pass 184 adds verified runtime packaging and supervised listener
readiness without creating a competing VM81 authority.

* ``/`` is owned by one rendered HTML route with the canonical public boot.
* ``/src`` serves repository-owned frontend modules and styles.
* ``/runtime-console/`` preserves the prior Pass 174 diagnostic console.
* ``/runtime-package/`` serves the Pass 184 package and service studio.
* ``/health`` and ``/api/health`` provide bounded, dependency-light liveness.

No static application mount is permitted at ``/`` because it would create a
second public-root authority capable of bypassing the rendered boot document.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.staticfiles import StaticFiles

from hhs_backend import pass174_server as pass174
from hhs_backend import production_server as production
from hhs_backend.api.pass175_runtime_routes import router as pass175_router
from hhs_backend.api.pass175_ws_routes import router as pass175_ws_router
from hhs_backend.api.pass175_terminal_routes import router as pass175_terminal_router
from hhs_backend.api.pass175_terminal_ws_routes import router as pass175_terminal_ws_router
from hhs_backend.api.pass184_runtime_routes import router as pass184_router
from hhs_backend.public_ide_bootstrap import render_public_ide_index

app = pass174.app
app.title = "HHS Full Multimodal Application IDE"
app.version = "4.4.2"
app.description = (
    "Full integrated development environment for real web applications, games, "
    "calculators, documents, audio, video, multimodal projects, HARMONICODE, "
    "multi-target compilation, VM81 execution, Pass 175 Hash216-hydrated "
    "VM5184 × G243 virtual instruction processing, firmware and governed devices, "
    "Pass 184 portable runtime packaging and supervised service readiness, "
    "repository lineage, assistant-led development, preview, testing, and egress."
)

FULL_IDE_ROOT = production.VISUAL_ROOT
RUNTIME_CONSOLE_ROOT = pass174._ide_root
RUNTIME_PACKAGE_STUDIO_ROOT = Path(__file__).resolve().parents[1] / "applications" / "runtime_package_studio"
API_FALLBACK_PATH = pass174._API_FALLBACK_PATH


def _has_route_prefix(prefix: str) -> bool:
    return any(str(getattr(route, "path", "")).startswith(prefix) for route in app.router.routes)


def _has_exact_route(path: str) -> bool:
    return any(str(getattr(route, "path", "")) == path for route in app.router.routes)


def _is_inherited_public_root(route: Any) -> bool:
    """Identify every inherited GET/static authority for the public root."""
    path = str(getattr(route, "path", ""))
    if path not in {"", "/"}:
        return False
    methods = getattr(route, "methods", None)
    return methods is None or bool({"GET", "HEAD"}.intersection(methods))


_deferred_api_fallback_routes = [
    route for route in app.router.routes
    if str(getattr(route, "path", "")) == API_FALLBACK_PATH
]

# Remove every inherited root handler or root static mount before composing the
# sole rendered index route. Route identity is based on path and callable shape,
# so import reuse or inherited naming cannot preserve a competing root.
app.router.routes = [
    route
    for route in app.router.routes
    if not _is_inherited_public_root(route)
    and getattr(route, "name", None) not in {
        "hhs-production-harmonizer",
        "hhs-pass174-visual-ide",
        "hhs-pass174-legacy-ide",
        "hhs-pass174-runtime-console",
        "hhs-pass184-runtime-package-studio",
        "hhs-full-application-ide",
        "hhs-full-application-ide-index",
    }
    and str(getattr(route, "path", "")) != API_FALLBACK_PATH
]

if not _has_route_prefix("/api/v1/pass175/status"):
    app.include_router(pass175_router)
if not _has_route_prefix("/api/v1/pass175/ws/events"):
    app.include_router(pass175_ws_router)
if not _has_route_prefix("/api/v1/pass175/terminal/status"):
    app.include_router(pass175_terminal_router)
if not _has_route_prefix("/api/v1/pass175/terminal/ws/events"):
    app.include_router(pass175_terminal_ws_router)
if not _has_route_prefix("/api/v1/pass184/status"):
    app.include_router(pass184_router)


async def application_ide_liveness() -> dict[str, Any]:
    """Return cheap process and route liveness without invoking heavy peers."""
    boot = dict(pass174.PASS174_BOOT_STATE)
    authority_ready = bool(boot.get("authority_ready") and boot.get("ready"))
    return {
        "schema": "HHS_FULL_APPLICATION_IDE_LIVENESS_V1",
        "ok": True,
        "status": "HHS_IDE_SERVICE_REACHABLE",
        "service_available": True,
        "authority_ready": authority_ready,
        "runtime_ready": authority_ready,
        "assistant_ready": False,
        "assistant_health_requires_product_probe": True,
        "frontend_runtime_authority": False,
        "public_interface": "HHS_FULL_MULTIMODAL_APPLICATION_IDE",
        "pass174_boot": boot,
        "routes": {
            "workspace": _has_route_prefix("/api/runtime/workspace"),
            "development_lifecycle": _has_route_prefix("/api/runtime/development"),
            "assistant": _has_route_prefix("/api/assistant"),
            "pass175_processor": _has_route_prefix("/api/v1/pass175/status"),
            "pass175_terminal": _has_route_prefix("/api/v1/pass175/terminal/status"),
            "pass184_package_authority": _has_route_prefix("/api/v1/pass184/status"),
        },
        "remediation": (
            None
            if authority_ready
            else "The web service is reachable, but runtime authority is not ready. Inspect /api/v1/pass174/deployment/status and platform logs."
        ),
    }


if not _has_exact_route("/health"):
    app.add_api_route(
        "/health",
        application_ide_liveness,
        methods=["GET", "HEAD"],
        include_in_schema=False,
        name="hhs-full-ide-health",
    )
if not _has_exact_route("/api/health"):
    app.add_api_route(
        "/api/health",
        application_ide_liveness,
        methods=["GET", "HEAD"],
        include_in_schema=False,
        name="hhs-full-ide-api-health",
    )

if RUNTIME_PACKAGE_STUDIO_ROOT.is_dir() and not _has_exact_route("/runtime-package"):
    app.mount(
        "/runtime-package",
        StaticFiles(directory=str(RUNTIME_PACKAGE_STUDIO_ROOT), html=True),
        name="hhs-pass184-runtime-package-studio",
    )

if RUNTIME_CONSOLE_ROOT.is_dir():
    app.mount(
        "/runtime-console",
        StaticFiles(directory=str(RUNTIME_CONSOLE_ROOT), html=True),
        name="hhs-pass174-runtime-console",
    )

# Restore the inherited unknown-API classification only after every successor
# API route is registered. It is restricted to /api/* and cannot own `/`.
app.router.routes.extend(_deferred_api_fallback_routes)

if FULL_IDE_ROOT.is_dir() and (FULL_IDE_ROOT / "index.html").is_file():
    async def full_application_ide_index():
        return render_public_ide_index(FULL_IDE_ROOT)

    app.add_api_route(
        "/",
        full_application_ide_index,
        methods=["GET", "HEAD"],
        include_in_schema=False,
        name="hhs-full-application-ide-index",
    )
else:
    pass174.PASS174_BOOT_STATE.update({
        "classification": "HHS_FULL_APPLICATION_IDE_ASSET_ROOT_MISSING",
        "full_ide_root": str(FULL_IDE_ROOT),
        "ready": False,
        "authority_ready": False,
        "degraded": True,
    })

pass174.PASS174_BOOT_STATE.update({
    "public_interface": "HHS_FULL_MULTIMODAL_APPLICATION_IDE",
    "public_asset_root": str(FULL_IDE_ROOT),
    "runtime_console_root": str(RUNTIME_CONSOLE_ROOT),
    "runtime_console_preserved": RUNTIME_CONSOLE_ROOT.is_dir(),
    "runtime_package_studio_root": str(RUNTIME_PACKAGE_STUDIO_ROOT),
    "runtime_package_studio_available": RUNTIME_PACKAGE_STUDIO_ROOT.is_dir(),
    "application_ide_is_public_root": True,
    "diagnostic_console_is_supporting_surface": True,
    "pass175_virtual_instruction_processor_routes": _has_route_prefix("/api/v1/pass175/status"),
    "pass175_websocket_routes": _has_route_prefix("/api/v1/pass175/ws/events"),
    "pass175_terminal_routes": _has_route_prefix("/api/v1/pass175/terminal/status"),
    "pass175_terminal_websocket_routes": _has_route_prefix("/api/v1/pass175/terminal/ws/events"),
    "pass184_portable_runtime_routes": _has_route_prefix("/api/v1/pass184/status"),
    "pass184_runtime_package_studio": _has_exact_route("/runtime-package"),
    "api_fallback_deferred_for_pass175": bool(_deferred_api_fallback_routes),
    "single_public_root_authority": True,
    "public_root_static_fallback": False,
    "public_source_mount": "/src",
    "lightweight_health_route": "/health",
    "lightweight_api_health_route": "/api/health",
    "inline_public_boot": "HHS_INLINE_PUBLIC_BOOT_V2",
    "legacy_parser_module_entries_disabled": True,
    "external_vercel_quota_is_not_pass175_acceptance_gate": True,
})

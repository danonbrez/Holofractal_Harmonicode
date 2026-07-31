"""Final HHS production composition with the full application IDE at ``/``.

All inherited Pass 174 APIs, VM81/Hash216 authorities, WebSockets, readiness
semantics, assistant routes, multimodal ingress, compiler services, and legacy
contracts remain registered by :mod:`hhs_backend.pass174_server`. Pass 175 adds
its VM5184 × G243 processor, encrypted terminal hydration, firmware, governed
devices, native-kernel evidence, and WebSocket surfaces before all fallbacks and
static mounts.

* ``/`` serves the complete Holofractal Harmonizer application IDE.
* ``/runtime-console/`` preserves the prior Pass 174 diagnostic console.

Static mounts are installed last so they cannot shadow any API or WebSocket.
"""
from __future__ import annotations

from fastapi.staticfiles import StaticFiles

from hhs_backend import pass174_server as pass174
from hhs_backend import production_server as production
from hhs_backend.api.pass175_runtime_routes import router as pass175_router
from hhs_backend.api.pass175_ws_routes import router as pass175_ws_router
from hhs_backend.api.pass175_terminal_routes import router as pass175_terminal_router
from hhs_backend.api.pass175_terminal_ws_routes import router as pass175_terminal_ws_router

app = pass174.app
app.title = "HHS Full Multimodal Application IDE"
app.version = "4.3.0"
app.description = (
    "Full integrated development environment for real web applications, games, "
    "calculators, documents, audio, video, multimodal projects, HARMONICODE, "
    "multi-target compilation, VM81 execution, Pass 175 Hash216-hydrated "
    "VM5184 × G243 virtual instruction processing, firmware and governed devices, "
    "repository lineage, assistant-led development, preview, testing, and egress."
)

FULL_IDE_ROOT = production.VISUAL_ROOT
RUNTIME_CONSOLE_ROOT = pass174._ide_root
API_FALLBACK_PATH = pass174._API_FALLBACK_PATH


def _has_route_prefix(prefix: str) -> bool:
    return any(str(getattr(route, "path", "")).startswith(prefix) for route in app.router.routes)


_deferred_api_fallback_routes = [
    route for route in app.router.routes
    if str(getattr(route, "path", "")) == API_FALLBACK_PATH
]

app.router.routes = [
    route
    for route in app.router.routes
    if getattr(route, "name", None) not in {
        "hhs-production-harmonizer",
        "hhs-pass174-visual-ide",
        "hhs-pass174-legacy-ide",
        "hhs-pass174-runtime-console",
        "hhs-full-application-ide",
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

if RUNTIME_CONSOLE_ROOT.is_dir():
    app.mount(
        "/runtime-console",
        StaticFiles(directory=str(RUNTIME_CONSOLE_ROOT), html=True),
        name="hhs-pass174-runtime-console",
    )

app.router.routes.extend(_deferred_api_fallback_routes)

if FULL_IDE_ROOT.is_dir() and (FULL_IDE_ROOT / "index.html").is_file():
    app.mount(
        "/",
        StaticFiles(directory=str(FULL_IDE_ROOT), html=True),
        name="hhs-full-application-ide",
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
    "application_ide_is_public_root": True,
    "diagnostic_console_is_supporting_surface": True,
    "pass175_virtual_instruction_processor_routes": _has_route_prefix("/api/v1/pass175/status"),
    "pass175_websocket_routes": _has_route_prefix("/api/v1/pass175/ws/events"),
    "pass175_terminal_routes": _has_route_prefix("/api/v1/pass175/terminal/status"),
    "pass175_terminal_websocket_routes": _has_route_prefix("/api/v1/pass175/terminal/ws/events"),
    "api_fallback_deferred_for_pass175": bool(_deferred_api_fallback_routes),
    "external_vercel_quota_is_not_pass175_acceptance_gate": True,
})

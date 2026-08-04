"""Final HHS production composition with the full application IDE at ``/``.

All inherited Pass 174 APIs, VM81/Hash216 authorities, WebSockets, readiness
semantics, assistant routes, multimodal ingress, compiler services, and legacy
contracts remain registered by :mod:`hhs_backend.pass174_server`. Pass 175 adds
its VM5184 × G243 processor, encrypted terminal hydration, firmware, governed
devices, native-kernel evidence, and WebSocket surfaces. Pass 201 federates
every registered API router before all fallbacks and static mounts. Pass 203
adds the hydrated-function mainframe and high-fidelity creative runtime. Pass
204 upgrades every indexed declaration to an executable disposable-sandbox
binding and exposes the safe open cloud-computer state/recall surface.

* ``/`` serves the complete Holofractal Harmonizer application IDE.
* ``/runtime-console/`` preserves the prior Pass 174 diagnostic console.
* ``/health`` and ``/api/health`` provide bounded, dependency-light liveness.
* ``/api/public/*`` catalogs every public route, service, and pass module.
* ``/api/runtime/mainframe/*`` exposes universal executable declarations.
* ``/api/runtime/open-cloud/*`` exposes sandbox policy, closure, jobs, and recall.

Static mounts are installed last so they cannot shadow any API or WebSocket.
"""
from __future__ import annotations

from typing import Any

from fastapi.staticfiles import StaticFiles

from hhs_backend import pass174_server as pass174
from hhs_backend import production_server as production
from hhs_backend.api import pass175_runtime_routes as pass175_runtime_api
from hhs_backend.api.pass175_ws_routes import router as pass175_ws_router
from hhs_backend.api.pass175_terminal_routes import router as pass175_terminal_router
from hhs_backend.api.pass175_terminal_ws_routes import router as pass175_terminal_ws_router
from hhs_backend.api.public_api_registry_routes import router as public_api_router
from hhs_backend.public_ide_bootstrap import render_public_ide_index
from hhs_backend.runtime.hhs_pass201_public_api_federation import register_public_api_federation

app = pass174.app
app.title = "HHS Safe Open Cloud Computer IDE"
app.version = "4.5.2"
app.description = (
    "Full integrated development environment and safe open cloud computer for real web applications, "
    "games, calculators, documents, audio, video, multimodal projects, HARMONICODE, multi-target "
    "compilation, VM81 execution, Hash216-hydrated VM5184 × G243 virtual instruction processing, "
    "firmware and governed devices, repository lineage, assistant-led development, preview, testing, "
    "egress, complete public API federation, universal executable declarations, disposable remote "
    "sandboxes, durable jobs, layered state snapshots, and capability-free session recall."
)

FULL_IDE_ROOT = production.VISUAL_ROOT
RUNTIME_CONSOLE_ROOT = pass174._ide_root
API_FALLBACK_PATH = pass174._API_FALLBACK_PATH
RUNTIME_AUTHORITY_STATUS_PATH = "/api/runtime/authority/status"
PASS175_AUTHORITY_STATUS_PATH = "/api/v1/pass175/authority"
PASS175_BOUNDED_STATUS_PATH = "/api/v1/pass175/status"
PASS175_MATERIALIZED_STATUS_PATH = "/api/v1/pass175/status/materialized"
PASS175_FINAL_STATUS_PATHS = frozenset({
    PASS175_AUTHORITY_STATUS_PATH,
    PASS175_BOUNDED_STATUS_PATH,
    PASS175_MATERIALIZED_STATUS_PATH,
})


def _has_route_prefix(prefix: str) -> bool:
    return any(str(getattr(route, "path", "")).startswith(prefix) for route in app.router.routes)


def _has_exact_route(path: str) -> bool:
    return any(str(getattr(route, "path", "")) == path for route in app.router.routes)


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
        "hhs-full-application-ide-index",
    }
    and str(getattr(route, "path", "")) != API_FALLBACK_PATH
]

pass175_router = pass175_runtime_api.router
if not _has_route_prefix("/api/v1/pass175/status"):
    app.include_router(pass175_router)
if not _has_route_prefix("/api/v1/pass175/ws/events"):
    app.include_router(pass175_ws_router)
if not _has_route_prefix("/api/v1/pass175/terminal/status"):
    app.include_router(pass175_terminal_router)
if not _has_route_prefix("/api/v1/pass175/terminal/ws/events"):
    app.include_router(pass175_terminal_ws_router)
if not _has_exact_route("/api/public/status"):
    app.include_router(public_api_router)

# Earlier Pass 175 composition layers may retain an eager status handler that
# materializes all 5,184 permanent instructions. Replace only the three status
# surfaces with the current bounded authority module. Hydration, execution,
# terminal, firmware, device, and WebSocket routes retain their inherited owners.
app.router.routes = [
    route
    for route in app.router.routes
    if str(getattr(route, "path", "")) not in PASS175_FINAL_STATUS_PATHS
]
app.add_api_route(
    PASS175_AUTHORITY_STATUS_PATH,
    pass175_runtime_api.authority_status,
    methods=["GET"],
    name="hhs-pass175-authority-witness",
)
app.add_api_route(
    PASS175_BOUNDED_STATUS_PATH,
    pass175_runtime_api.status,
    methods=["GET"],
    name="hhs-pass175-bounded-status",
)
app.add_api_route(
    PASS175_MATERIALIZED_STATUS_PATH,
    pass175_runtime_api.materialized_status,
    methods=["GET"],
    name="hhs-pass175-materialized-status",
)

# The inherited Pass 54 role-orchestration router and production server both
# register this path. FastAPI resolves the first match, so retain one bounded
# production endpoint before public federation catalogs the final route graph.
app.router.routes = [
    route
    for route in app.router.routes
    if str(getattr(route, "path", "")) != RUNTIME_AUTHORITY_STATUS_PATH
]
app.add_api_route(
    RUNTIME_AUTHORITY_STATUS_PATH,
    production.production_runtime_authority_status,
    methods=["GET"],
    name="hhs-production-runtime-authority-status",
)

# Public federation is composed before fallback/static routes. All importable
# hhs_backend.api routers become directly accessible at their native paths.
PASS201_PUBLIC_API_REGISTRATION = register_public_api_federation(app)


async def application_ide_liveness() -> dict[str, Any]:
    """Return cheap process, route, and committed live-runtime readiness."""
    boot = dict(pass174.PASS174_BOOT_STATE)
    runtime = production._runtime_authority_status()
    authority_ready = bool(runtime.get("ok"))
    return {
        "schema": "HHS_FULL_APPLICATION_IDE_LIVENESS_V3",
        "ok": True,
        "status": "HHS_SAFE_OPEN_CLOUD_IDE_SERVICE_REACHABLE",
        "service_available": True,
        "authority_ready": authority_ready,
        "runtime_ready": authority_ready,
        "assistant_ready": False,
        "assistant_health_requires_product_probe": True,
        "frontend_runtime_authority": False,
        "public_interface": "HHS_SAFE_OPEN_CLOUD_COMPUTER_IDE",
        "public_api": "/api/public",
        "public_api_catalog": "/api/public/catalog",
        "mainframe": "/api/runtime/mainframe/status",
        "open_cloud": "/api/runtime/open-cloud/status",
        "open_cloud_closure": "/api/runtime/open-cloud/closure",
        "public_api_registration_closed": PASS201_PUBLIC_API_REGISTRATION.get("closed", False),
        "pass174_boot": boot,
        "runtime_authority": runtime,
        "runtime_authority_source": RUNTIME_AUTHORITY_STATUS_PATH,
        "runtime_readiness_uses_committed_live_projection": True,
        "routes": {
            "workspace": _has_route_prefix("/api/runtime/workspace"),
            "development_lifecycle": _has_route_prefix("/api/runtime/development"),
            "assistant": _has_route_prefix("/api/assistant"),
            "pass175_processor": _has_exact_route(PASS175_BOUNDED_STATUS_PATH),
            "pass175_authority": _has_exact_route(PASS175_AUTHORITY_STATUS_PATH),
            "pass175_materialized_status": _has_exact_route(PASS175_MATERIALIZED_STATUS_PATH),
            "pass175_terminal": _has_route_prefix("/api/v1/pass175/terminal/status"),
            "public_api": _has_route_prefix("/api/public/status"),
            "mainframe": _has_route_prefix("/api/runtime/mainframe/status"),
            "open_cloud": _has_route_prefix("/api/runtime/open-cloud/status"),
            "open_cloud_closure": _has_route_prefix("/api/runtime/open-cloud/closure"),
            "runtime_authority": _has_exact_route(RUNTIME_AUTHORITY_STATUS_PATH),
        },
        "remediation": (
            None
            if authority_ready
            else "The web service is reachable, but the committed live runtime authority is not ready. Inspect /api/runtime/live/status and platform logs."
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

if RUNTIME_CONSOLE_ROOT.is_dir():
    app.mount(
        "/runtime-console",
        StaticFiles(directory=str(RUNTIME_CONSOLE_ROOT), html=True),
        name="hhs-pass174-runtime-console",
    )

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
    "public_interface": "HHS_SAFE_OPEN_CLOUD_COMPUTER_IDE",
    "public_asset_root": str(FULL_IDE_ROOT),
    "runtime_console_root": str(RUNTIME_CONSOLE_ROOT),
    "runtime_console_preserved": RUNTIME_CONSOLE_ROOT.is_dir(),
    "application_ide_is_public_root": True,
    "diagnostic_console_is_supporting_surface": True,
    "pass175_virtual_instruction_processor_routes": _has_exact_route(PASS175_BOUNDED_STATUS_PATH),
    "pass175_authority_witness_route": PASS175_AUTHORITY_STATUS_PATH,
    "pass175_bounded_status_route": PASS175_BOUNDED_STATUS_PATH,
    "pass175_materialized_status_route": PASS175_MATERIALIZED_STATUS_PATH,
    "pass175_status_routes_deduplicated": True,
    "pass175_websocket_routes": _has_route_prefix("/api/v1/pass175/ws/events"),
    "pass175_terminal_routes": _has_route_prefix("/api/v1/pass175/terminal/status"),
    "pass175_terminal_websocket_routes": _has_route_prefix("/api/v1/pass175/terminal/ws/events"),
    "pass201_public_api_federation": _has_route_prefix("/api/public/status"),
    "pass201_registration_closed": PASS201_PUBLIC_API_REGISTRATION.get("closed", False),
    "pass203_mainframe_routes": _has_route_prefix("/api/runtime/mainframe/status"),
    "pass204_open_cloud_routes": _has_route_prefix("/api/runtime/open-cloud/status"),
    "pass204_executable_declaration_closure": _has_route_prefix("/api/runtime/open-cloud/closure"),
    "api_fallback_deferred_for_integrated_passes": bool(_deferred_api_fallback_routes),
    "lightweight_health_route": "/health",
    "lightweight_api_health_route": "/api/health",
    "runtime_authority_route": RUNTIME_AUTHORITY_STATUS_PATH,
    "runtime_authority_route_deduplicated": True,
    "runtime_readiness_uses_committed_live_projection": True,
    "inline_public_boot": "HHS_INLINE_PUBLIC_BOOT_V2",
    "legacy_parser_module_entries_disabled": True,
    "external_vercel_quota_is_not_acceptance_gate": True,
})
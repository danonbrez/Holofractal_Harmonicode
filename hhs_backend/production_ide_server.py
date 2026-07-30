"""Canonical hosted HHS server with the integrated Pass 174 visual IDE.

This module reuses the single FastAPI app and backend runtime authority from
``hhs_backend.production_server``. It inserts source-preserving multimodal,
development-lifecycle, and repository-lineage routes before remounting the
verified visual application at ``/``.
"""
from __future__ import annotations

from fastapi.staticfiles import StaticFiles

from hhs_backend import production_server as production
from hhs_backend.api.development_lifecycle_routes import router as development_lifecycle_router
from hhs_backend.api.pass165_multimodal_ingress_routes import router as pass165_router
from hhs_backend.api.repository_history_routes import router as repository_history_router

app = production.app
app.title = "HHS Holofractal Harmonizer Visual IDE"
app.version = "3.5.0"
app.description = (
    "Canonical HHS runtime and full integrated development environment with a "
    "project file tree, editable source workspace, sandboxed application and media "
    "preview, source-preserving multimodal ingress, multi-target compilation, exact "
    "5,184-bit VM snapshots, bounded VM81 execution, runtime registry, repository "
    "pass constraints, commit lineage, receipts, replay, and ZIP egress."
)


def _has_route_prefix(prefix: str) -> bool:
    return any(str(getattr(route, "path", "")).startswith(prefix) for route in app.router.routes)


# The production_server mounts the visual root last. Remove only that mount so
# the new API routes remain reachable, then restore the same verified static app.
app.router.routes = [
    route
    for route in app.router.routes
    if getattr(route, "name", None) != "hhs-production-harmonizer"
]

if not _has_route_prefix("/api/runtime/multimodal-ingress"):
    app.include_router(pass165_router)
if not _has_route_prefix("/api/runtime/development"):
    app.include_router(development_lifecycle_router)
if not _has_route_prefix("/api/runtime/repository"):
    app.include_router(repository_history_router)

# production_server owns a deliberate /api/{unmatched_path} fail-closed route.
# Routers added by this composition layer must be ordered before that fallback.
repository_routes = [
    route for route in app.router.routes
    if str(getattr(route, "path", "")).startswith("/api/runtime/repository")
]
if repository_routes:
    app.router.routes = [route for route in app.router.routes if route not in repository_routes]
    fallback_index = next(
        (
            index for index, route in enumerate(app.router.routes)
            if str(getattr(route, "path", "")) == "/api/{unmatched_path:path}"
        ),
        len(app.router.routes),
    )
    for route in reversed(repository_routes):
        app.router.routes.insert(fallback_index, route)

if (production.VISUAL_ROOT / "index.html").is_file():
    app.mount(
        "/",
        StaticFiles(directory=str(production.VISUAL_ROOT), html=True),
        name="hhs-production-harmonizer",
    )

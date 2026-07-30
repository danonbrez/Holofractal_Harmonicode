"""Canonical hosted HHS server with the integrated Pass 161 visual IDE.

This module reuses the single FastAPI app and backend runtime authority from
``hhs_backend.production_server``. It only inserts the existing Pass 165
multimodal authority and the integrated development-lifecycle router before
remounting the verified visual application at ``/``.
"""
from __future__ import annotations

from fastapi.staticfiles import StaticFiles

from hhs_backend import production_server as production
from hhs_backend.api.development_lifecycle_routes import router as development_lifecycle_router
from hhs_backend.api.pass165_multimodal_ingress_routes import router as pass165_router

app = production.app
app.title = "HHS Holofractal Harmonizer Visual IDE"
app.version = "3.4.0"
app.description = (
    "Canonical HHS runtime and front-and-center visual IDE with source-preserving "
    "multimodal ingress, Hash216 indexing, exact 5,184-bit VM snapshots, HHS "
    "interpretation, compilation, bounded VM81 execution, receipts, replay, and egress."
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

if (production.VISUAL_ROOT / "index.html").is_file():
    app.mount(
        "/",
        StaticFiles(directory=str(production.VISUAL_ROOT), html=True),
        name="hhs-production-harmonizer",
    )

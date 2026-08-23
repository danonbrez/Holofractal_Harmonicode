"""Primary API-only HHS backend composition for the Pass 220 migration.

This module inherits the accumulated API/router composition from
``hhs_backend.visual_server`` and removes only the legacy static browser
application mounts. It does not create runtime, receipt, or mutation authority.

The dependency on ``visual_server`` is intentionally transitional: Pass 220
Iteration 1 must inventory and separate common API composition from legacy web
projection after terminal Pass 219 closure. Until that gate, this module
preserves the proven accumulated API surface without duplicating router wiring.
"""
from __future__ import annotations

from typing import Any, Dict

from hhs_backend.visual_server import app as inherited_app

WEB_FRONTEND_STATUS = "DEPRECATED_COMPATIBILITY_ONLY"
PREFERRED_LOCAL_INTERFACE = "HHS_PASS220_NATIVE_LINUX_VM"
CANONICAL_BACKEND_AUTHORITY = "INHERITED_SINGLETON_VM81_KERNEL"
LEGACY_STATIC_ROUTE_NAMES = frozenset(
    {
        "hhs-storybook-reel-studio",
        "hhs-probability-hydration-studio",
        "hhs-visual-home",
    }
)

app = inherited_app
app.title = "HHS Canonical API Backend"
app.description = (
    "Primary machine/API projection for HHS. The browser frontend is deprecated "
    "compatibility-only; canonical execution remains behind the inherited "
    "singleton VM81/kernel authority path."
)

# Remove only the legacy product-UI mounts. API, WebSocket, OpenAPI, assistant,
# runtime, hydration, graphics, and public federation routes remain inherited.
app.router.routes[:] = [
    route
    for route in app.router.routes
    if getattr(route, "name", None) not in LEGACY_STATIC_ROUTE_NAMES
]

app.state.hhs_web_frontend_status = WEB_FRONTEND_STATUS
app.state.hhs_preferred_local_interface = PREFERRED_LOCAL_INTERFACE


@app.get("/api/interface/status", tags=["system"])
async def interface_status() -> Dict[str, Any]:
    return {
        "schema": "HHS_INTERFACE_MIGRATION_STATUS_V1",
        "primary_machine_surface": "API",
        "preferred_local_interface": PREFERRED_LOCAL_INTERFACE,
        "web_frontend_status": WEB_FRONTEND_STATUS,
        "web_frontend_removed": False,
        "legacy_static_routes_mounted": False,
        "canonical_backend_authority": CANONICAL_BACKEND_AUTHORITY,
        "canonical_mutation_authority_created_here": False,
        "pass220_promotion_status": "NON_PROMOTIONAL_PREIMPLEMENTATION",
    }


__all__ = [
    "CANONICAL_BACKEND_AUTHORITY",
    "LEGACY_STATIC_ROUTE_NAMES",
    "PREFERRED_LOCAL_INTERFACE",
    "WEB_FRONTEND_STATUS",
    "app",
]

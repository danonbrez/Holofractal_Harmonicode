"""DigitalOcean visual projection for the HHS TypeScript Runtime OS.

This layer preserves every route and runtime authority registered by
:mod:`hhs_backend.visual_server`, installs the Pass-218 durable lifecycle gate,
and changes only the public-root UI projection.
"""
from __future__ import annotations

from hhs_backend.runtime_os_pass218_lifecycle import (
    PASS218_RUNTIME_STATUS_PATH,
    install_pass218_runtime_os_lifecycle,
)
from hhs_backend.runtime_os_pass220_lane5_tool_hydration import (
    PASS220_LANE5_TOOL_GRAPH_PATH,
    PASS220_LANE5_TOOL_STATUS_PATH,
    install_pass220_lane5_tool_warm_hydration,
)
from hhs_backend.runtime_os_projection import (
    DEFAULT_PUBLIC_MOUNT_NAME,
    RUNTIME_OS_ASSETS,
    RUNTIME_OS_INDEX,
    RUNTIME_OS_ROOT,
    project_runtime_os,
)
from hhs_backend.visual_server import app as inherited_app

APPLICATION_PUBLIC_MOUNT_NAME = "hhs-runtime-os-application-home"
_existing_public_mount_names = {
    str(getattr(route, "name", ""))
    for route in inherited_app.router.routes
}
PUBLIC_MOUNT_NAME = (
    APPLICATION_PUBLIC_MOUNT_NAME
    if APPLICATION_PUBLIC_MOUNT_NAME in _existing_public_mount_names
    else DEFAULT_PUBLIC_MOUNT_NAME
)

app = inherited_app
app.title = "HHS Visual Runtime OS"
app.description = (
    "Canonical HHS backend/pass authority projected through the TypeScript/React/Vite "
    "Runtime OS workspace. Runtime execution remains owned by the inherited HHS backend."
)
PASS218_RUNTIME_OS_LIFECYCLE = install_pass218_runtime_os_lifecycle(app)
PASS220_LANE5_TOOL_WARM_LIFECYCLE = install_pass220_lane5_tool_warm_hydration(app)
project_runtime_os(app, mount_name=PUBLIC_MOUNT_NAME)

__all__ = [
    "PASS218_RUNTIME_OS_LIFECYCLE",
    "PASS218_RUNTIME_STATUS_PATH",
    "PASS220_LANE5_TOOL_GRAPH_PATH",
    "PASS220_LANE5_TOOL_STATUS_PATH",
    "PASS220_LANE5_TOOL_WARM_LIFECYCLE",
    "PUBLIC_MOUNT_NAME",
    "RUNTIME_OS_ASSETS",
    "RUNTIME_OS_INDEX",
    "RUNTIME_OS_ROOT",
    "app",
]

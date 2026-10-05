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
from hhs_backend.runtime_os_pass220_lane5_capability_hydration import (
    SEARCH_PATH as PASS219_LANE5_CAPABILITY_SEARCH_PATH,
    STATUS_PATH as PASS219_LANE5_CAPABILITY_STATUS_PATH,
    SUMMARY_PATH as PASS219_LANE5_CAPABILITY_SUMMARY_PATH,
    install_pass219_lane5_capability_visibility,
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
PASS219_LANE5_CAPABILITY_VISIBILITY = install_pass219_lane5_capability_visibility(app)
project_runtime_os(app, mount_name=PUBLIC_MOUNT_NAME)

__all__ = [
    "PASS218_RUNTIME_OS_LIFECYCLE",
    "PASS218_RUNTIME_STATUS_PATH",
    "PASS219_LANE5_CAPABILITY_SEARCH_PATH",
    "PASS219_LANE5_CAPABILITY_STATUS_PATH",
    "PASS219_LANE5_CAPABILITY_SUMMARY_PATH",
    "PASS219_LANE5_CAPABILITY_VISIBILITY",
    "PUBLIC_MOUNT_NAME",
    "RUNTIME_OS_ASSETS",
    "RUNTIME_OS_INDEX",
    "RUNTIME_OS_ROOT",
    "app",
]

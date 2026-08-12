"""DigitalOcean visual projection for the HHS TypeScript Runtime OS.

This layer preserves every route and runtime authority registered by
:mod:`hhs_backend.visual_server` and changes only the public-root UI projection.
"""
from __future__ import annotations

from hhs_backend.runtime_os_projection import (
    DEFAULT_PUBLIC_MOUNT_NAME,
    RUNTIME_OS_ASSETS,
    RUNTIME_OS_INDEX,
    RUNTIME_OS_ROOT,
    project_runtime_os,
)
from hhs_backend.visual_server import app as inherited_app

PUBLIC_MOUNT_NAME = DEFAULT_PUBLIC_MOUNT_NAME

app = inherited_app
app.title = "HHS Visual Runtime OS"
app.description = (
    "Canonical HHS backend/pass authority projected through the TypeScript/React/Vite "
    "Runtime OS workspace. Runtime execution remains owned by the inherited HHS backend."
)
project_runtime_os(app, mount_name=PUBLIC_MOUNT_NAME)

__all__ = [
    "PUBLIC_MOUNT_NAME",
    "RUNTIME_OS_ASSETS",
    "RUNTIME_OS_INDEX",
    "RUNTIME_OS_ROOT",
    "app",
]

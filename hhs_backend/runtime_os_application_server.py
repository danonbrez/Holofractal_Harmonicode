"""Full HHS application composition with the TypeScript Runtime OS at ``/``.

All Pass 174+ application/server composition remains inherited from
:mod:`hhs_backend.application_ide_server`. This final layer removes only its
public-root visual mount and projects the same backend through ``hhs_gui/dist``.
Supporting surfaces such as ``/runtime-console`` remain intact.
"""
from __future__ import annotations

from hhs_backend.application_ide_server import app as inherited_app
from hhs_backend.runtime_os_projection import (
    RUNTIME_OS_ASSETS,
    RUNTIME_OS_INDEX,
    RUNTIME_OS_ROOT,
    project_runtime_os,
)

PUBLIC_MOUNT_NAME = "hhs-runtime-os-application-home"

app = inherited_app
app.title = "HHS Runtime OS Application Environment"
app.description = (
    "Full cumulative HHS application, API, assistant, VM81, Hash72/Hash216, pass, "
    "workspace, compiler, emulator, replay, and runtime surfaces projected through "
    "the TypeScript/React/Vite Runtime OS."
)
project_runtime_os(app, mount_name=PUBLIC_MOUNT_NAME)

__all__ = [
    "PUBLIC_MOUNT_NAME",
    "RUNTIME_OS_ASSETS",
    "RUNTIME_OS_INDEX",
    "RUNTIME_OS_ROOT",
    "app",
]

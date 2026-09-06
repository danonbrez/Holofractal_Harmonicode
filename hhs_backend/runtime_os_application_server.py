"""Production dispatcher for the HHS Runtime OS application environment.

Normal production imports the Pass170 public gateway first, then the complete
cumulative composition preserved in ``runtime_os_application_server_full``.
This ordering makes the Pass170 public routes part of the same inherited
``hhs_backend.server:app`` object before later IDE/RuntimeOS overlays are added.
Only an explicitly requested missing-C profile selects the source-only shell,
before any VM81/Hash72/Pass authority module is imported.

Historical full-composition source relationships remain:
``from hhs_backend.application_ide_server import app as inherited_app``
``install_pass218_i18_terminal_closure_control_plane``
``project_runtime_os(app, mount_name=PUBLIC_MOUNT_NAME)``
"""
from __future__ import annotations

import os
import platform
from pathlib import Path


_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _runtime_library_path() -> Path:
    system = platform.system().lower()
    if system == "windows":
        libname = "hhs_runtime.dll"
    elif system == "darwin":
        libname = "libhhs_runtime.dylib"
    else:
        libname = "libhhs_runtime.so"
    return _REPOSITORY_ROOT / "hhs_runtime" / "builds" / libname


_RUNTIME_LIBRARY_PATH = _runtime_library_path()
_EXPLICIT_DEGRADED_REQUEST = (
    _truthy("HHS_ALLOW_C_RUNTIME_DEGRADED_IMPORT")
    or _truthy("HHS_DISABLE_C_AUTOBUILD")
)
_SOURCE_ONLY_DEGRADED = bool(
    _EXPLICIT_DEGRADED_REQUEST and not _RUNTIME_LIBRARY_PATH.is_file()
)

if _SOURCE_ONLY_DEGRADED:
    from hhs_backend.runtime_os_source_only_server import (
        PUBLIC_MOUNT_NAME,
        REPOSITORY_ROOT,
        app,
    )

    SOURCE_ONLY_DEGRADED_MODE = True
    PASS170_PUBLIC_GATEWAY_IDENTITY_VERIFIED = False
    C_RUNTIME_LIBRARY_PATH = str(_RUNTIME_LIBRARY_PATH)
    __all__ = [
        "C_RUNTIME_LIBRARY_PATH",
        "PASS170_PUBLIC_GATEWAY_IDENTITY_VERIFIED",
        "PUBLIC_MOUNT_NAME",
        "REPOSITORY_ROOT",
        "SOURCE_ONLY_DEGRADED_MODE",
        "app",
    ]
else:
    # Compose Pass170 onto the inherited production base before any later
    # application/RuntimeOS layer mutates that same FastAPI object.
    from hhs_backend import public_api_server as _pass170_public_gateway
    from hhs_backend.runtime_os_application_server_full import *  # noqa: F401,F403
    from hhs_backend.runtime_os_application_server_full import __all__ as _FULL_ALL

    if app is not _pass170_public_gateway.app:  # type: ignore[name-defined]
        raise RuntimeError("PASS170_PRODUCTION_APPLICATION_IDENTITY_DIVERGED")

    SOURCE_ONLY_DEGRADED_MODE = False
    PASS170_PUBLIC_GATEWAY_IDENTITY_VERIFIED = True
    C_RUNTIME_LIBRARY_PATH = str(_RUNTIME_LIBRARY_PATH)
    __all__ = list(_FULL_ALL) + [
        "C_RUNTIME_LIBRARY_PATH",
        "PASS170_PUBLIC_GATEWAY_IDENTITY_VERIFIED",
        "SOURCE_ONLY_DEGRADED_MODE",
    ]

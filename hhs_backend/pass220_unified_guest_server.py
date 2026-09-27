"""Pass 220 I047 unified Ubuntu guest application selector.

This module creates no new HHS authority. It selects the already-existing
Runtime OS application composition when the exact release assets have been
staged inside the guest; otherwise it exposes the inherited application IDE
backend during bootstrap.
"""
from __future__ import annotations

import os
from pathlib import Path

_asset_root_value = os.environ.get("HHS_RUNTIME_OS_ASSET_ROOT", "").strip()
_asset_root = Path(_asset_root_value).expanduser().resolve() if _asset_root_value else None

if (
    _asset_root is not None
    and (_asset_root / "index.html").is_file()
    and (_asset_root / "assets").is_dir()
):
    from hhs_backend.runtime_os_application_server import app  # noqa: F401

    HHS_PASS220_I047_GUEST_MODE = "RUNTIME_OS"
else:
    from hhs_backend.application_ide_server import app  # noqa: F401

    HHS_PASS220_I047_GUEST_MODE = "IDE_BACKEND_BOOTSTRAP"

app.state.hhs_pass220_i047_guest_mode = HHS_PASS220_I047_GUEST_MODE
app.state.hhs_pass220_i047_canonical_authority = False

__all__ = ["HHS_PASS220_I047_GUEST_MODE", "app"]

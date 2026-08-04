"""Install immutable Pass 203 catalog identity before public route federation."""
from __future__ import annotations

from hhs_backend.runtime.hhs_pass203_catalog_identity_guard_v1 import (
    install_pass203_catalog_identity_guard,
)
from hhs_backend.runtime.hhs_pass203_hydrated_mainframe_v1 import PASS203_MAINFRAME

PASS203_CATALOG_IDENTITY_GUARD = install_pass203_catalog_identity_guard(PASS203_MAINFRAME)
PASS203_CATALOG_IDENTITY_STATUS = PASS203_CATALOG_IDENTITY_GUARD.status()

__all__ = [
    "PASS203_CATALOG_IDENTITY_GUARD",
    "PASS203_CATALOG_IDENTITY_STATUS",
]

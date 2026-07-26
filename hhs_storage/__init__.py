"""Canonical HHS storage package initialization.

Storage owns the compatibility adapter required by inherited persistence and
replay surfaces. Importing the storage package installs only deterministic state
projections; it does not boot, tick, or mutate VM81.
"""

from .runtime_state_compatibility_v1 import (
    COMPATIBILITY_VERSION,
    install_runtime_state_store_compatibility,
)

install_runtime_state_store_compatibility()

__all__ = [
    "COMPATIBILITY_VERSION",
    "install_runtime_state_store_compatibility",
]

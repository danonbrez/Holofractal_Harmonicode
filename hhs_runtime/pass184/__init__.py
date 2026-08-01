"""Pass 184 portable hydration-runtime package and service authority."""

from . import runtime as _runtime

# The full installation profile includes every specialized modality family,
# including the game runtime rather than merely its graphics/audio dependencies.
_runtime.PROFILE_SEEDS["full"] = ("application_ide", "games")

APP_IMPORT = _runtime.APP_IMPORT
CONTRACT_ID = _runtime.CONTRACT_ID
PROFILE_SEEDS = _runtime.PROFILE_SEEDS
RUNTIME_VERSION = _runtime.RUNTIME_VERSION
Pass184Error = _runtime.Pass184Error
PortableRuntimeAuthority = _runtime.PortableRuntimeAuthority
resolve_profile_components = _runtime.resolve_profile_components

__all__ = [
    "APP_IMPORT",
    "CONTRACT_ID",
    "PROFILE_SEEDS",
    "RUNTIME_VERSION",
    "Pass184Error",
    "PortableRuntimeAuthority",
    "resolve_profile_components",
]

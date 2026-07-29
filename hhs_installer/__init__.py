"""Pass 172 universal installation implementation.

This package owns bounded host-provisioning transactions only. It does not
interpret HARMONICODE, execute canonical tensor operations, or create a second
VM81/Hash72/Hash216 authority.
"""

from .schema import (
    CompatibilityClass,
    InstallMode,
    InstallationRequest,
    NetworkPolicy,
    Profile,
    ProviderPolicy,
    SourceKind,
    SourceSpec,
)

CONTRACT_ID = "HHS-P172-UCEOCI-DRVBRAS"
IMPLEMENTATION_VERSION = "HHS_PASS_172_INSTALLER_V1"

__all__ = [
    "CONTRACT_ID",
    "IMPLEMENTATION_VERSION",
    "CompatibilityClass",
    "InstallMode",
    "InstallationRequest",
    "NetworkPolicy",
    "Profile",
    "ProviderPolicy",
    "SourceKind",
    "SourceSpec",
]

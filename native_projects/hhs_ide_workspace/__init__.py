"""Pass 074 native HHS IDE workspace and development-agent protocol product.

Package import is deliberately descriptor-only. Low-level inherited modules use
`hhs_workspace_contracts_v1` directly and must not pay the dependency or startup
cost of the FastAPI projection simply because Python initializes this package.
Public Pass 074 exports remain available through lazy attribute resolution.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "HHSNativeWorkspaceRuntime",
    "build_pass074_release_bundle",
    "create_workspace_app",
    "development_protocol_contract",
]


def __getattr__(name: str) -> Any:
    if name == "development_protocol_contract":
        from .hhs_development_network_protocol_v1 import development_protocol_contract

        return development_protocol_contract
    if name in {"HHSNativeWorkspaceRuntime", "build_pass074_release_bundle"}:
        from .hhs_native_workspace_project_v1 import (
            HHSNativeWorkspaceRuntime,
            build_pass074_release_bundle,
        )

        return {
            "HHSNativeWorkspaceRuntime": HHSNativeWorkspaceRuntime,
            "build_pass074_release_bundle": build_pass074_release_bundle,
        }[name]
    if name == "create_workspace_app":
        from .hhs_unified_runtime_api_v1 import create_workspace_app

        return create_workspace_app
    raise AttributeError(name)

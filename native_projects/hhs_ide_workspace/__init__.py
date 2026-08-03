"""Pass 074 native HHS IDE workspace and development-agent protocol product."""
from .hhs_development_network_protocol_v1 import development_protocol_contract
from .hhs_native_workspace_project_v1 import HHSNativeWorkspaceRuntime, build_pass074_release_bundle

try:
    from .hhs_unified_runtime_api_v1 import create_workspace_app
except ModuleNotFoundError as exc:
    if exc.name != "fastapi":
        raise

    def create_workspace_app(*_args, **_kwargs):
        raise ModuleNotFoundError("No module named 'fastapi'")

__all__ = [
    "HHSNativeWorkspaceRuntime",
    "build_pass074_release_bundle",
    "create_workspace_app",
    "development_protocol_contract",
]

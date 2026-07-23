"""Pass 075 API projection using the unchanged Pass 074 unified routes."""
from native_projects.hhs_ide_workspace.hhs_unified_runtime_api_v1 import create_workspace_app
from .hhs_pass075_workspace_runtime_v1 import HHSNativeLanguageWorkspaceRuntime


def create_language_workspace_app(runtime=None):
    return create_workspace_app(runtime or HHSNativeLanguageWorkspaceRuntime())


app = create_language_workspace_app()

"""Pass 077 API projection over the unchanged Pass 074 unified routes."""
from native_projects.hhs_ide_workspace.hhs_unified_runtime_api_v1 import create_workspace_app
from .hhs_pass077_workspace_runtime_v1 import HHSCompilerArtifactWorkspaceRuntime


def create_compiler_workspace_app(runtime=None):
    return create_workspace_app(runtime or HHSCompilerArtifactWorkspaceRuntime())


app = create_compiler_workspace_app()

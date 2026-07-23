"""Pass 076 API projection over the unchanged Pass 074 canonical routes."""
from native_projects.hhs_ide_workspace.hhs_unified_runtime_api_v1 import create_workspace_app
from .hhs_pass076_workspace_runtime_v1 import HHSNativeInterpreterWorkspaceRuntime


def create_interpreter_workspace_app(runtime=None):
    return create_workspace_app(runtime or HHSNativeInterpreterWorkspaceRuntime())


app = create_interpreter_workspace_app()

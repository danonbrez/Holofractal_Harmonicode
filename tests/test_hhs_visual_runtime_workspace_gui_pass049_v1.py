from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

def test_visual_runtime_workspace_gui_sources():
    shell = read("hhs_gui/runtime_os/workspace/HHSWorkspaceShell.tsx")
    runtime_shell = read("hhs_gui/runtime_os/core/RuntimeShell.tsx")
    client = read("hhs_gui/runtime_os/workspace/WorkspaceCommandClient.ts")
    store = read("hhs_gui/runtime_os/workspace/WorkspaceProjectionStore.ts")
    assert "hhs-visual-runtime-os-workspace" in shell
    assert "HHSWorkspaceShell" in runtime_shell
    assert "HHS_WORKSPACE_COMMAND_ENVELOPE_V1" in client
    assert "frontend_may_commit_runtime_truth: false" in client
    assert "REQUEST_AND_PROJECTION_ONLY" in store
    assert "frontendCacheIsAuthority: false" in store

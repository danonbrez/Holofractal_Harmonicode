from hhs_backend.runtime.hhs_workspace_authority_loop_v1 import WorkspaceAuthorityLoop

def test_workspace_command_boundary_rejects_direct_gui_mutation():
    loop = WorkspaceAuthorityLoop()
    result = loop.submit("source.patch", {"frontend_mutated_runtime_truth": True, "replacement_text": "x=1"})
    assert not result["ok"]
    assert result["status"] == "REJECT_GUI_DIRECT_WORKSPACE_MUTATION"
    assert result["gui_mutated_runtime_truth"] is False

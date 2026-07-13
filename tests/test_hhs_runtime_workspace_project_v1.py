from hhs_backend.runtime.runtime_workspace_project_v1 import runtime_workspace_project_self_test

def test_runtime_workspace_project_self_test():
    result = runtime_workspace_project_self_test()
    assert result["ok"]
    assert result["opened"]["status"] == "WORKSPACE_LIVE"
    assert not result["invalid_manifest_rejection"]["ok"]

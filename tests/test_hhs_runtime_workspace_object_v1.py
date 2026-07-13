from hhs_backend.runtime.runtime_workspace_object_v1 import workspace_object_self_test

def test_runtime_workspace_object_self_test():
    result = workspace_object_self_test()
    assert result["ok"]
    assert result["validation"]["ok"]
    assert not result["frontend_cache_authority_rejection"]["ok"]

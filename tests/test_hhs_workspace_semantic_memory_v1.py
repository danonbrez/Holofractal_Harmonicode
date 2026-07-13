from hhs_backend.runtime.hhs_workspace_semantic_memory_v1 import workspace_semantic_memory_self_test

def test_workspace_semantic_memory_self_test():
    result = workspace_semantic_memory_self_test()
    assert result["ok"]
    assert result["result"]["ranking_is_truth_authority"] is False

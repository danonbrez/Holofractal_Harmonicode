from hhs_backend.runtime.hhs_workspace_persistence_v1 import workspace_persistence_self_test

def test_workspace_persistence_self_test():
    result = workspace_persistence_self_test()
    assert result["ok"]
    assert result["save"]["atomic_manifest_commit"] is True
    assert not result["bad_manifest_rejection"]["ok"]

from hhs_backend.runtime.hhs_workspace_authority_loop_v1 import workspace_authority_loop_self_test
from hhs_backend.runtime.hhs_workspace_command_router_v1 import workspace_command_router_self_test

def test_workspace_authority_loop_self_test():
    result = workspace_authority_loop_self_test()
    assert result["ok"]
    assert not result["direct_gui_mutation_rejection"]["ok"]
    assert result["presentation"]["canonical_runtime_mutated"] is False

def test_workspace_command_router_self_test():
    result = workspace_command_router_self_test()
    assert result["ok"]
    assert result["presentation"]["authority_tier"] == "PRESENTATION_ONLY"

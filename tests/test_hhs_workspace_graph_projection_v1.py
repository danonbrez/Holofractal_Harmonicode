from hhs_backend.runtime.hhs_workspace_graph_projection_v1 import workspace_graph_projection_self_test

def test_workspace_graph_projection_self_test():
    result = workspace_graph_projection_self_test()
    assert result["ok"]
    assert result["projection"]["layout_is_authoritative"] is False

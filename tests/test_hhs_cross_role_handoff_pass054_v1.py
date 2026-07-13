from hhs_backend.runtime.hhs_role_bound_agent_orchestrator_v1 import *
def test_incomplete_handoff_rejected():
    role=build_role_contract(); task=build_task_assignment("source","spec",role)
    h=build_handoff(task,{})
    d=validate_handoff(h)
    assert not d["ok"]
    assert "REJECT_CROSS_AGENT_HANDOFF_WITHOUT_PROVENANCE" in d["reasons"]

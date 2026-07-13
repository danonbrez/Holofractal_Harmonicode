from hhs_backend.runtime.hhs_role_bound_agent_orchestrator_v1 import *

def test_canonical_continuation_and_task_expiration():
    run=run_role_bound_orchestration()
    assert run["ok"]
    assert run["independent_revalidation"]["status"]=="ADMIT_CANONICAL_CONTINUATION"
    assert "REJECT_TASK_AUTHORITY_EXPIRED" in run["task_expiration_decision"]["reasons"]
    assert run["competency_record"]["authority_granted_by_competency"] is False

def test_output_equivalence_not_derivation_equivalence():
    d=validate_derivation_equivalence({"x":1},{"x":1},candidate_source_root="a",reference_source_root="b",candidate_path=["x"],reference_path=["y"],candidate_authority_path=[],reference_authority_path=["canonical"])
    assert d["output_equivalent"] is True
    assert d["canonical_identity_continues"] is False
    assert "REJECT_OUTPUT_EQUIVALENCE_AS_DERIVATION_EQUIVALENCE" in d["reasons"]

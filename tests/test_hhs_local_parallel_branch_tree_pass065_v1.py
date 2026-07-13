from hhs_backend.runtime.hhs_local_parallel_branch_tree_v1 import *

def test_pass065_self_test(): assert local_parallel_branch_tree_self_test()["ok"]
def test_parallel_tree_closes_locally():
 r=run_local_parallel_branch_tree(); assert r["ok"]; assert r["closure"]["closed_local_tree"]
def test_contradiction_does_not_globalize():
 r=run_local_parallel_branch_tree(); assert r["closure"]["global_rejection_emitted"] is False; assert r["closure"]["failed_branch_rejection_propagated"] is False
def test_ab_reintegration_requires_phase_alignment():
 r=run_local_parallel_branch_tree(); assert r["reintegration"]["integration_relation"]=="A=B"; assert r["reintegration"]["translation_phase_aligned"]
def test_branch_selection_is_deterministic():
 r=run_local_parallel_branch_tree(); assert r["comparison"]["selected_branch_id"]=="branch:direct"
def test_missing_provenance_rejected():
 r=run_local_parallel_branch_tree(); x=dict(r["branch_receipts"][0]); x["provenance_complete"]=False; d=compare_branches([x]); assert "REJECT_BRANCH_RESULT_WITHOUT_COMPARATIVE_REVALIDATION" in d["reasons"]

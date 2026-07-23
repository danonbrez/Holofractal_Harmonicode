from pathlib import Path
from native_projects.hhs_bifurcation_calibration.hhs_pass095_pattern_aware_ab_evaluation_v1 import *
R=Path(__file__).resolve().parents[1]

def test_pass094_inputs_are_immutably_committed():
 i=load_pass094_inputs(R); assert i["manifest"]["pass_id"]=="PASS_094" and i["input_commitment_root_hash72"]

def test_registry_has_w95_01_through_w95_16():
 t=task_registry(R); assert len(t)==16 and t[0]["workload_id"]=="W95-01" and t[-1]["workload_id"]=="W95-16"

def test_a_has_no_pattern_access_and_b_is_read_only():
 i=load_pass094_inputs(R); t=task_registry(R)[0]; a=run_trial(t,"A_PATTERN_NAIVE",i); b=run_trial(t,"B_PATTERN_AWARE",i)
 assert not a["pattern_access"] and a["pattern_use_receipt"]["pattern_roots_consulted"]==[]
 assert b["pattern_access"] and not b["pattern_use_receipt"]["authority_conferred_by_pattern"]

def test_matched_pairs_share_validator_semantics_and_exactness():
 i=load_pass094_inputs(R); p=matched_pair(task_registry(R)[0],i)
 assert p["arm_a"]["validator_root_hash72"]==p["arm_b"]["validator_root_hash72"]
 assert p["arm_a"]["task_semantics_root_hash72"]==p["arm_b"]["task_semantics_root_hash72"]
 assert p["arm_a"]["correctness_status"]==p["arm_b"]["correctness_status"]=="EXACT"

def test_specialized_transfer_and_generalization_gains_are_separate():
 r=run(R,default_config(R)); c=r["classification_counts"]
 assert c["SPECIALIZED_EFFICIENCY_GAIN"]>0 and c["TRANSFERABLE_GAIN"]>0 and c["GENERALIZATION_GAIN"]>0

def test_misleading_pattern_is_rejected_and_negative_transfer_preserved():
 r=run(R,default_config(R)); ps=[p for p in r["matched_pairs"] if p["arm_b"]["task_family"]=="MISLEADING_PATTERN_REJECTION"]
 assert ps and all(p["classification"]=="NEGATIVE_TRANSFER" for p in ps)
 assert all(p["arm_b"]["pattern_use_receipt"]["patterns_rejected_as_irrelevant"] for p in ps)

def test_pattern_use_receipts_witness_work_saved_without_authority():
 r=run(R,default_config(R)); receipts=[p["arm_b"]["pattern_use_receipt"] for p in r["matched_pairs"]]
 assert all(not x["authority_conferred_by_pattern"] for x in receipts)
 assert any(x["work_saved_claim"]["saved"]>0 for x in receipts)

def test_trial_isolation_and_held_out_commitments_verified():
 r=run(R,default_config(R)); assert r["trial_isolation_verified"] and r["config"]["held_out_committed_before_evaluation"] and r["config"]["separate_caches"]

def test_replay_is_exact():
 assert verify_replay(R,default_config(R,"T95:replay"))["deterministic_replay_verified"]

def test_all_negative_cases_pass():
 assert all(x["passed"] for x in negative_cases(R))

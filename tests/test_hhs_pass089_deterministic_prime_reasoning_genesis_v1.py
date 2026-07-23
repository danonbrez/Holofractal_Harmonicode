
from pathlib import Path
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass089_deterministic_prime_reasoning_genesis_v1 import default_workload,run,verify_replay,workload_registry,negative_cases
R=Path(__file__).resolve().parents[1]

def test_lo_shu_genesis_starts_at_11():
    w=default_workload(R,workload_id="T145",end_candidate=13)
    assert w["genesis"]["embedded_prime_basis"]==[2,3,5,7]
    r=run(R,w)
    assert r["prime_reasoning_receipt"]["candidate_receipts"][0]["candidate"]==11

def test_prime_and_composite_receipts_are_exact():
    r=run(R,default_workload(R,workload_id="T149",end_candidate=32))
    classes={x["classification"] for x in r["prime_reasoning_receipt"]["candidate_receipts"]}
    assert classes=={"VALIDATED_PRIME","VALIDATED_COMPOSITE"}

def test_frontier_expands_beyond_genesis():
    r=run(R,default_workload(R,workload_id="T148",end_candidate=98))
    assert r["metrics"]["highest_consecutive_prime"]>=97

def test_four_thousand_candidate_scaling():
    r=run(R,default_workload(R,workload_id="T154",end_candidate=4012))
    assert r["metrics"]["processed_candidates"]==4001

def test_replay_exact():
    assert verify_replay(R,default_workload(R,workload_id="TR",end_candidate=128))["deterministic_replay_verified"]

def test_replay_mutation_rejected():
    w=default_workload(R,workload_id="NEG",end_candidate=64); w["alter_candidate_range_on_replay"]=True
    with pytest.raises(ContractError,match="REJECT_PRIME_REASONING_REPLAY_MISMATCH"): verify_replay(R,w)

def test_negative_cases_all_pass():
    assert all(x["passed"] for x in negative_cases(R))

def test_registry_w145_w158():
    ws=workload_registry(R)
    assert len(ws)==14 and ws[0]["workload_id"].startswith("W145") and ws[-1]["workload_id"].startswith("W158")

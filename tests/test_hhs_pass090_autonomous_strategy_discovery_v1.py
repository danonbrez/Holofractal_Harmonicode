
from pathlib import Path
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass090_autonomous_strategy_discovery_v1 import default_workload,run,verify_replay,workload_registry,negative_cases
R=Path(__file__).resolve().parents[1]

def test_strategy_is_non_authoritative_until_validation():
    r=run(R,default_workload(R,workload_id="T90"))
    assert r["strategy_receipt"]["strategy"]["authority"] is False
    assert r["strategy_receipt"]["strategy"]["requires_validation"] is True

def test_heldout_and_transfer_gain_measured():
    r=run(R,default_workload(R,workload_id="T90X"))
    assert r["metrics"]["strategy_gain_numerator"]>0
    assert r["metrics"]["cross_task_gain_numerator"]>0

def test_prediction_separate_from_validation():
    r=run(R,default_workload(R,workload_id="T90P"))
    assert r["strategy_receipt"]["prediction_separate_from_validation"]

def test_no_transfer_classified_without_capability_claim():
    r=run(R,default_workload(R,workload_id="T90:no-benefit-cross-task",required_status="REJECTED_NO_GAIN"))
    assert r["status"]=="REJECTED_NO_GAIN"

def test_replay_exact():
    assert verify_replay(R,default_workload(R,workload_id="TR"))["deterministic_replay_verified"]

def test_replay_mutation_rejected():
    w=default_workload(R,workload_id="NEG"); w["alter_strategy_on_replay"]=True
    with pytest.raises(ContractError,match="REJECT_STRATEGY_REPLAY_MISMATCH"): verify_replay(R,w)

def test_negative_cases_all_pass():
    assert all(x["passed"] for x in negative_cases(R))

def test_registry_w90_01_w90_12():
    ws=workload_registry(R)
    assert len(ws)==12 and ws[0]["workload_id"].startswith("W90-01") and ws[-1]["workload_id"].startswith("W90-12")


from pathlib import Path
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass087_incremental_semantic_graph_learning_v1 import default_workload,run,verify_replay,workload_registry,negative_cases
R=Path(__file__).resolve().parents[1]

def test_incremental_graph_growth():
    r=run(R,default_workload(R,workload_id="T117",base_pattern_count=8,new_pattern_count=4))
    assert r["metrics"]["result_node_count"]>r["metrics"]["base_node_count"]

def test_supersession_preserves_history():
    r=run(R,default_workload(R,workload_id="T120",base_pattern_count=16,new_pattern_count=8,family_count=4))
    assert r["learning_receipt"]["silent_overwrite_occurred"] is False

def test_dependency_scoped_revalidation():
    r=run(R,default_workload(R,workload_id="T119",base_pattern_count=16,new_pattern_count=8,family_count=4))
    assert r["metrics"]["update_count"]>0

def test_one_hundred_twenty_eight_node_scaling():
    r=run(R,default_workload(R,workload_id="T125",base_pattern_count=128,new_pattern_count=32,family_count=8))
    assert r["metrics"]["base_node_count"]==128

def test_replay_exact():
    assert verify_replay(R,default_workload(R,workload_id="TR"))["deterministic_replay_verified"]

def test_replay_mutation_rejected():
    w=default_workload(R,workload_id="NEG"); w["alter_update_on_replay"]=True
    with pytest.raises(ContractError,match="REJECT_GRAPH_REPLAY_MISMATCH"): verify_replay(R,w)

def test_negative_cases_all_pass():
    assert all(x["passed"] for x in negative_cases(R))

def test_registry_w117_w130():
    ws=workload_registry(R)
    assert len(ws)==14 and ws[0]["workload_id"].startswith("W117") and ws[-1]["workload_id"].startswith("W130")

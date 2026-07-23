
from pathlib import Path
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass086_deterministic_multimodal_pattern_admission_v1 import default_workload,run,verify_replay,workload_registry,negative_cases
R=Path(__file__).resolve().parents[1]

def test_patterns_are_evidence_rooted_and_admitted():
    r=run(R,default_workload(R,workload_id="T103",instance_count=8))
    p=r["pattern_admission_receipt"]
    assert p["evidence_lineage_preserved"] and r["metrics"]["admitted_pattern_count"]>0

def test_proposal_and_cache_are_not_authority():
    r=run(R,default_workload(R,workload_id="T115"))
    p=r["pattern_admission_receipt"]
    assert p["proposal_authority_separated"] and p["cache_authority_separated"]

def test_cache_and_graph_are_populated():
    r=run(R,default_workload(R,workload_id="T109",instance_count=16))
    assert r["metrics"]["cache_entry_count"]>0 and r["metrics"]["knowledge_graph_edge_count"]>0

def test_sixty_four_instance_scaling():
    r=run(R,default_workload(R,workload_id="T111",instance_count=64))
    assert r["metrics"]["evidence_count"]>=64

def test_replay_exact():
    assert verify_replay(R,default_workload(R,workload_id="TR"))["deterministic_replay_verified"]

def test_replay_mutation_rejected():
    w=default_workload(R,workload_id="NEG"); w["alter_pattern_on_replay"]=True
    with pytest.raises(ContractError,match="REJECT_PATTERN_REPLAY_MISMATCH"): verify_replay(R,w)

def test_negative_cases_all_pass():
    assert all(x["passed"] for x in negative_cases(R))

def test_registry_w103_w116():
    ws=workload_registry(R)
    assert len(ws)==14 and ws[0]["workload_id"].startswith("W103") and ws[-1]["workload_id"].startswith("W116")

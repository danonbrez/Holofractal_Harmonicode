
from pathlib import Path
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass088_deterministic_training_acceleration_v1 import default_workload,run,verify_replay,workload_registry,negative_cases
R=Path(__file__).resolve().parents[1]

def test_cache_assisted_path_preserves_proof():
    r=run(R,default_workload(R,workload_id="T132",cache_pattern_count=32,sample_count=64,family_count=8,novel_every=0))
    assert r["training_acceleration_receipt"]["proof_strength_preserved"]

def test_constrained_work_below_baseline_for_warm_cache():
    r=run(R,default_workload(R,workload_id="T132B",cache_pattern_count=64,sample_count=64,family_count=8,novel_every=0))
    assert r["metrics"]["constrained_work_units"] < r["metrics"]["baseline_work_units"]

def test_novel_residue_is_preserved():
    r=run(R,default_workload(R,workload_id="T133",cache_pattern_count=32,sample_count=64,family_count=8,novel_every=7))
    assert r["metrics"]["novel_residue_count"]>0

def test_five_hundred_twelve_sample_scaling():
    r=run(R,default_workload(R,workload_id="T139",cache_pattern_count=256,sample_count=512,family_count=32,novel_every=19))
    assert r["metrics"]["sample_count"]==512

def test_replay_exact():
    assert verify_replay(R,default_workload(R,workload_id="TR"))["deterministic_replay_verified"]

def test_replay_mutation_rejected():
    w=default_workload(R,workload_id="NEG"); w["alter_sample_on_replay"]=True
    with pytest.raises(ContractError,match="REJECT_TRAINING_REPLAY_MISMATCH"): verify_replay(R,w)

def test_negative_cases_all_pass():
    assert all(x["passed"] for x in negative_cases(R))

def test_registry_w131_w144():
    ws=workload_registry(R)
    assert len(ws)==14 and ws[0]["workload_id"].startswith("W131") and ws[-1]["workload_id"].startswith("W144")


from pathlib import Path
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass085_deterministic_3d_space_emulation_v1 import default_workload,run,verify_replay,workload_registry,negative_cases
R=Path(__file__).resolve().parents[1]

def test_stereo_reconstruction_closes():
    r=run(R,default_workload(R,workload_id="T90",camera_count=2,audio_sensor_count=0))
    assert r["space_emulation_receipt"]["scene_state"]["closure_verified"]
    assert r["metrics"]["entity_state_count"]>0

def test_identity_layers_remain_distinct():
    r=run(R,default_workload(R,workload_id="T101",camera_count=4,audio_sensor_count=4))
    assert r["space_emulation_receipt"]["scene_state"]["observed_reconstructed_inferred_unresolved_distinct"]

def test_latency_is_not_geometry():
    r=run(R,default_workload(R,workload_id="T92",camera_count=2,audio_sensor_count=4,latency_stride=7))
    assert r["space_emulation_receipt"]["scene_state"]["latency_distinct_from_geometry"]

def test_sixty_four_sensor_scaling():
    r=run(R,default_workload(R,workload_id="T98",camera_count=32,audio_sensor_count=32,observation_count=4))
    assert r["metrics"]["camera_count"]+r["metrics"]["audio_sensor_count"]==64

def test_replay_exact():
    assert verify_replay(R,default_workload(R,workload_id="TR"))["deterministic_replay_verified"]

def test_replay_pose_mutation_rejected():
    w=default_workload(R,workload_id="NEG"); w["alter_pose_on_replay"]=True
    with pytest.raises(ContractError,match="REJECT_SPACE_REPLAY_MISMATCH"): verify_replay(R,w)

def test_negative_cases_all_pass():
    assert all(x["passed"] for x in negative_cases(R))

def test_registry_w89_w102():
    ws=workload_registry(R)
    assert len(ws)==14 and ws[0]["workload_id"].startswith("W89") and ws[-1]["workload_id"].startswith("W102")

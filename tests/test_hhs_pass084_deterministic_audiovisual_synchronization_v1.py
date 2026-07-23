
from pathlib import Path
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass084_deterministic_audiovisual_synchronization_v1 import default_workload,run,verify_replay,workload_registry,negative_cases
R=Path(__file__).resolve().parents[1]

def test_av_normalization_closes_shared_events():
    r=run(R,default_workload(R,workload_id="T75",video_stream_count=1,audio_stream_count=1))
    assert r["synchronization_receipt"]["closure_verified"] and r["metrics"]["shared_event_count"]>0

def test_raw_timestamps_need_not_match():
    r=run(R,default_workload(R,workload_id="T78",video_latency_stride=3,audio_latency_stride=7))
    assert not r["synchronization_receipt"]["raw_timestamp_equality_required"]

def test_modality_identity_preserved():
    r=run(R,default_workload(R,workload_id="T87",video_stream_count=4,audio_stream_count=4))
    assert r["synchronization_receipt"]["modality_identity_preserved"]

def test_sixty_four_stream_scaling():
    r=run(R,default_workload(R,workload_id="T83",video_stream_count=32,audio_stream_count=32,observation_count=4))
    assert r["metrics"]["video_stream_count"]+r["metrics"]["audio_stream_count"]==64

def test_replay_exact():
    r=verify_replay(R,default_workload(R,workload_id="TR"))
    assert r["deterministic_replay_verified"]

def test_replay_mutation_rejected():
    w=default_workload(R,workload_id="NEG"); w["alter_audio_on_replay"]=True
    with pytest.raises(ContractError,match="REJECT_AUDIOVISUAL_REPLAY_MISMATCH"): verify_replay(R,w)

def test_negative_cases_all_pass():
    assert all(x["passed"] for x in negative_cases(R))

def test_registry_w75_w88():
    ws=workload_registry(R)
    assert len(ws)==14 and ws[0]["workload_id"].startswith("W75") and ws[-1]["workload_id"].startswith("W88")

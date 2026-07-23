from pathlib import Path
import copy, pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass082_4_reciprocal_multistring_reconstruction_v1 import default_workload, run, verify_replay, workload_registry
R=Path(__file__).resolve().parents[1]

def test_two_raw_strings_remain_distinct_and_close_after_normalization():
 r=run(R,default_workload(R,workload_id="T47",stream_count=2,phase_stride=1))
 assert r["reconstruction_receipt"]["raw_stream_roots_distinct"]
 assert r["reconstruction_receipt"]["closure_verified"]

def test_latency_normalization_binds_audio_video_event_coordinates():
 r=run(R,default_workload(R,workload_id="T51",stream_count=2,phase_stride=3,latency_stride=7,modalities=["AUDIO","VIDEO"]))
 assert r["metrics"]["latency_offset_diversity"]==2
 assert r["metrics"]["normalized_closure_ratio"]==1.0

def test_sixty_four_stream_scaling():
 r=run(R,default_workload(R,workload_id="T54",stream_count=64,phase_stride=1,string_length=8))
 assert r["metrics"]["stream_count"]==64 and r["metrics"]["raw_string_preservation_ratio"]==1.0

def test_duplicate_stream_identity_rejected():
 w=default_workload(R,workload_id="NEG")
 w["streams"][1]["stream_id"]=w["streams"][0]["stream_id"]
 with pytest.raises(ContractError,match="REJECT_DUPLICATE_STREAM_IDENTITY"): run(R,w)

def test_missing_latency_rejected():
 w=default_workload(R,workload_id="NEG")
 del w["streams"][0]["latency_offset"]
 with pytest.raises(ContractError,match="REJECT_LATENCY_OFFSET_OMITTED_FROM_NORMALIZATION"): run(R,w)

def test_unwitnessed_overlap_rejected():
 w=default_workload(R,workload_id="NEG")
 w["overlap_relations"][0]["overlap_relation_root_hash72"]=""
 with pytest.raises(ContractError,match="REJECT_UNWITNESSED_OVERLAP_RELATION"): run(R,w)

def test_replay_offset_mutation_rejected():
 w=default_workload(R,workload_id="NEG")
 w["alter_phase_on_replay"]=True
 with pytest.raises(ContractError,match="REJECT_MULTISTRING_REPLAY_MISMATCH"): verify_replay(R,w)

def test_registry_w47_w60():
 ws=workload_registry(R)
 assert len(ws)==14 and ws[0]["workload_id"].startswith("W47") and ws[-1]["workload_id"].startswith("W60")

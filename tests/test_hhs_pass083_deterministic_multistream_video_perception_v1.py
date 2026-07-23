from pathlib import Path
import copy, pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass083_deterministic_multistream_video_perception_v1 import default_workload,run,verify_replay,workload_registry
R=Path(__file__).resolve().parents[1]

def test_frames_preserved_and_visual_events_close():
 r=run(R,default_workload(R,workload_id="T61",stream_count=2,frame_count=6)); assert r["perception_receipt"]["frame_roots_preserved"] and r["perception_receipt"]["closure_verified"]

def test_occlusion_is_preserved_not_deleted():
 r=run(R,default_workload(R,workload_id="T65",stream_count=2,frame_count=6,object_count=3)); assert r["metrics"]["occlusion_count"]>0 and r["perception_receipt"]["occlusions_preserved"]

def test_frame_object_trajectory_identity_separation():
 r=run(R,default_workload(R,workload_id="T72",stream_count=2,frame_count=8,object_count=3)); p=r["perception_receipt"]; assert p["frame_identity_distinct_from_object_identity"] and p["trajectory_identity_distinct_from_object_identity"]

def test_sixty_four_stream_scaling():
 r=run(R,default_workload(R,workload_id="T69",stream_count=64,frame_count=4)); assert r["metrics"]["stream_count"]==64

def test_duplicate_frame_rejected():
 w=default_workload(R,workload_id="NEG"); w["streams"][0]["frames"][1]["frame_id"]=w["streams"][0]["frames"][0]["frame_id"]
 with pytest.raises(ContractError,match="REJECT_DUPLICATE_FRAME_IDENTITY"): run(R,w)

def test_occlusion_deletion_rejected():
 w=default_workload(R,workload_id="NEG"); w["occlusion_as_deletion"]=True
 with pytest.raises(ContractError,match="REJECT_OCCLUSION_AS_DELETION"): run(R,w)

def test_replay_mutation_rejected():
 w=default_workload(R,workload_id="NEG"); w["alter_frame_on_replay"]=True
 with pytest.raises(ContractError,match="REJECT_VIDEO_REPLAY_MISMATCH"): verify_replay(R,w)

def test_registry_w61_w74():
 ws=workload_registry(R); assert len(ws)==14 and ws[0]["workload_id"].startswith("W61") and ws[-1]["workload_id"].startswith("W74")

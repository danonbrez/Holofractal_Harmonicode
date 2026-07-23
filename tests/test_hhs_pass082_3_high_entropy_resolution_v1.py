from pathlib import Path
import copy, pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass082_3_high_entropy_resolution_v1 import default_workload, run, verify_replay, workload_registry
R=Path(__file__).resolve().parents[1]

def test_clean_and_noisy_lossless_reconstruction():
 a=run(R,default_workload(R,workload_id="T33",noise_class="NONE",noise_count=0))
 b=run(R,default_workload(R,workload_id="T34",signal_size=90,noise_count=10))
 assert a["metrics"]["lossless_preservation_ratio"]==1 and b["metrics"]["lossless_preservation_ratio"]==1

def test_stable_unresolved_preserves_full_state():
 x=verify_replay(R,default_workload(R,workload_id="T38",noise_class="SEMANTIC",noise_count=16,outcome="LOSSLESS_STABLE_UNRESOLVED"))["initial"]
 assert x["status"]=="LOSSLESS_STABLE_UNRESOLVED" and x["metrics"]["lossless_preservation_ratio"]==1

def test_dense_topology_and_resource_bound():
 d=run(R,default_workload(R,workload_id="T39",groups=8,topology="DENSE_MESH",noise_class="TOPOLOGICAL",noise_count=64))
 r=run(R,default_workload(R,workload_id="T45",signal_size=128,noise_count=128,outcome="LOSSLESS_RESOURCE_BOUNDED"))
 assert d["metrics"]["branch_count"]==16 and r["status"]=="LOSSLESS_RESOURCE_BOUNDED"

def test_lossy_filter_rejected():
 w=default_workload(R,workload_id="NEG",noise_count=2); w["discard_noise_without_lineage"]=True
 with pytest.raises(ContractError,match="REJECT_LOSSY_NOISE_FILTERING"): run(R,w)

def test_conflict_collapse_rejected():
 w=default_workload(R,workload_id="NEG",noise_count=2); w["overwrite_conflict"]=True
 with pytest.raises(ContractError,match="REJECT_CONFLICT_COLLAPSED_SILENTLY"): run(R,w)

def test_reconstruction_failure_rejected():
 w=default_workload(R,workload_id="NEG",noise_count=2); w["simulate_lossy_result"]=True
 with pytest.raises(ContractError,match="REJECT_LOSSLESS_RECONSTRUCTION_FAILURE"): run(R,w)

def test_replay_mutation_rejected():
 w=default_workload(R,workload_id="NEG",noise_count=2); w["alter_noise_on_replay"]=True
 with pytest.raises(ContractError,match="REJECT_NONDETERMINISTIC_RESOLUTION"): verify_replay(R,w)

def test_registry_w33_w46():
 ws=workload_registry(R)
 assert len(ws)==14 and ws[0]["workload_id"].startswith("W33") and ws[-1]["workload_id"].startswith("W46")

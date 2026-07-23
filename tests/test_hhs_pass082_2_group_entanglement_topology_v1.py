from pathlib import Path
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass082_2_group_entanglement_topology_v1 import default_workload, run, verify_replay, workload_registry
R=Path(__file__).resolve().parents[1]

def test_isolated_groups_close_and_remain_distinct():
 x=verify_replay(R,default_workload(R,2,2,"ISOLATED",workload_id="T21"))["initial"]
 assert x["global_receipt"]["group_roots_distinct"] and x["metrics"]["entanglement_edges"]==0

def test_chain_and_ring_topologies():
 c=run(R,default_workload(R,4,4,"CHAIN",workload_id="T23")); r=run(R,default_workload(R,4,4,"RING",workload_id="T24"))
 assert c["metrics"]["entanglement_edges"]==3 and r["metrics"]["entanglement_edges"]==4

def test_cyclic_classification_is_not_ancestry_cycle():
 x=run(R,default_workload(R,6,4,"RING",workload_id="T31",relation_types=["ANTI_COMMUTATIVE"],closure_classification="DETERMINISTIC_CYCLIC"))
 assert x["status"]=="DETERMINISTIC_CYCLIC" and x["global_receipt"]["cycle_length"]==6

def test_stable_unresolved_remains_deterministic():
 x=verify_replay(R,default_workload(R,8,4,"DENSE_MESH",workload_id="T32",closure_classification="DETERMINISTIC_STABLE_UNRESOLVED"))["initial"]
 assert x["status"]=="DETERMINISTIC_STABLE_UNRESOLVED" and x["global_receipt"]["global_replay_verified"]

def test_unwitnessed_edge_rejected():
 w=default_workload(R,2,2,"PAIRWISE",workload_id="NEG"); w["edges"][0]["relation_root_hash72"]=""
 with pytest.raises(ContractError,match="REJECT_UNWITNESSED_ENTANGLEMENT"): run(R,w)

def test_group_identity_collapse_rejected():
 w=default_workload(R,2,2,"PAIRWISE",workload_id="NEG"); w["groups"][1]["group_id"]=w["groups"][0]["group_id"]
 with pytest.raises(ContractError,match="REJECT_GROUP_IDENTITY_ERASURE"): run(R,w)

def test_replay_edge_change_rejected():
 w=default_workload(R,2,2,"PAIRWISE",workload_id="NEG"); w["alter_edge_on_replay"]=True
 with pytest.raises(ContractError,match="REJECT_ENTANGLEMENT_REPLAY_MISMATCH"): verify_replay(R,w)

def test_ancestry_cycle_rejected():
 w=default_workload(R,4,2,"RING",workload_id="NEG"); w["ancestry_cycle"]=True
 with pytest.raises(ContractError,match="REJECT_DERIVATION_CYCLE"): run(R,w)

def test_registry_w21_w32():
 ws=workload_registry(R); assert len(ws)==12 and ws[0]["workload_id"].startswith("W21") and ws[-1]["workload_id"].startswith("W32")

from pathlib import Path
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass082_bifurcation_benchmark_v1 import default_workload, run, verify_replay
R=Path(__file__).resolve().parents[1]
def test_w01_two_branch_bifurcation_and_replay():
 w=default_workload(R); v=verify_replay(R,w); x=v['initial']; assert v['deterministic_replay_verified']; assert x['branch_receipts'][0]['post_state_root_hash72']!=x['branch_receipts'][1]['post_state_root_hash72']; assert x['bifurcation_receipt']['closure_coordinate_roots_match']; assert not x['bifurcation_receipt']['branch_merger_occurred']
def test_separate_non_amplifying_leases():
 x=run(R,default_workload(R)); leases=[r['capability_lease_root_hash72'] for r in x['branch_receipts']]; assert len(set(leases))==2; assert all(not r['successful_result_confers_authority'] for r in x['branch_receipts'])
def test_reject_false_bifurcation():
 w=default_workload(R); w['branch_contracts'][1]=dict(w['branch_contracts'][0]);
 with pytest.raises(ContractError,match='REJECT_FALSE_BIFURCATION'): run(R,w)
def test_reject_missing_binding():
 w=default_workload(R); w['native_binding']['binding_root_hash72']='bad'
 with pytest.raises(ContractError,match='REJECT_NATIVE_INVOCATION_WITHOUT_BINDING'): run(R,w)
def test_reject_inactive_lease():
 w=default_workload(R); w['branch_contracts'][0]['lease_status']='REVOKED'
 with pytest.raises(ContractError,match='REJECT_NATIVE_INVOCATION_WITHOUT_ACTIVE_LEASE'): run(R,w)
def test_eight_branch_scaling():
 x=run(R,default_workload(R,8,64)); assert len(x['branch_receipts'])==8; assert len({r['post_state_root_hash72'] for r in x['branch_receipts']})==8

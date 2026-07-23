from pathlib import Path
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass099_dynamic_u72_computation_v1 import *
R=Path(__file__).resolve().parents[1]

def test_parent_and_carrier():
    assert load_pass098_inputs(R)['manifest']['pass_id']=='PASS_098'
    with pytest.raises(ContractError,match=REJECTIONS[0]): make_program('bad',[],carrier_modulus=71)

def test_state_persists_across_carrier_cycles():
    p=make_program('p',[make_operation('INC',0,cell=0)],input_cells={0:0})
    r=execute_program(p,2)['receipt']
    assert r['carrier_locally_closed'] and not r['computational_state_reset'] and r['final_state'][0]==2

def test_cell_propagation_and_branch():
    p=make_program('p',[make_operation('INC',0,cell=0),make_operation('COPY_WITH_LINEAGE',1,cell=0,target=1),make_operation('BRANCH',2,cell=1,condition={'cell':1,'mode':'POS'})],input_cells={0:0})
    x=execute_program(p,1)
    assert x['receipt']['final_state'][1]==1 and x['branch_receipts'][0]['trinary']==1

def test_noncommutative_order_distinction():
    a=make_program('a',[make_operation('INC',0,cell=0,arg=2),make_operation('INVERT',1,cell=0)],input_cells={0:1})
    b=make_program('b',[make_operation('INVERT',0,cell=0),make_operation('INC',1,cell=0,arg=2)],input_cells={0:1})
    assert execute_program(a,1)['receipt']['final_state'][0] != execute_program(b,1)['receipt']['final_state'][0]

def test_prime_periodic_activation():
    p=make_program('p',[make_operation('INC',3,cell=0)],prime_activation_rules=({'phase':3,'prime':11,'residue':3},))
    r=execute_program(p,12)['receipt']
    assert r['final_state'][0] >= 1

def test_checkpoint_resume_exact():
    p=make_program('p',[make_operation('INC',0,cell=0)],input_cells={0:0})
    first=execute_program(p,3,checkpoint_at=80); cp=first['checkpoints'][0]
    resumed=execute_program(p,3,resume=cp)['receipt']; full=execute_program(p,3)['receipt']
    assert resumed['final_state_root_hash72']==full['final_state_root_hash72']

def test_bounded_synthesis_no_universality_claim():
    r=synthesize_truth_table({-1:1,0:0,1:-1})
    assert r['validated'] and not r['universality_claimed']

def test_workloads_negative_cases_replay_and_artifacts():
    assert len(workloads())==14 and workloads()[-1]['held_out']
    assert all(x['passed'] for x in negative_cases())
    result=run(R)
    assert result['checkpoint_replay_exact'] and result['noncommutative_order_distinguished']
    assert result['carrier_closure_distinct_from_state_reset'] and result['state_persisted_across_cycles']

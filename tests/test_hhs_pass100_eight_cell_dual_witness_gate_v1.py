from pathlib import Path
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass100_eight_cell_dual_witness_gate_v1 import *
R=Path(__file__).resolve().parents[1]
def test_parent_and_clean_codeword():
    assert load_parent(R)['manifest']['pass_id']=='PASS_099'; c=encode((1,0,-1,1)); assert c['physical_cell_count']==8 and len(c['reciprocal_pairing'])==4
def test_pairing_involution_and_independence():
    assert dict((a,b) for a,b in PAIRS)|dict((b,a) for a,b in PAIRS)
    with pytest.raises(ContractError,match=REJECTIONS[2]): encode((1,0,-1,1),independent=False)
def test_single_cell_error_localized_corrected():
    c=encode((1,0,-1,1)); r=dict(c['cell_values']); r['C']+=1; s=diagnose(c,r); assert s['candidate_error_cells']==['C']; x=correct(c,r,s); assert x['post_correction_values']==c['cell_values']
def test_erasure_recovery():
    c=encode((1,0,-1,1)); r=dict(c['cell_values']); r.pop('E'); s=diagnose(c,r,erased=('E',)); assert s['candidate_error_cells']==['E']; assert correct(c,r,s)['post_correction_values']==c['cell_values']
def test_ambiguous_not_force_corrected():
    c=encode((1,0,-1,1)); r=dict(c['cell_values']); r['A']+=1; r['B']+=1; s=diagnose(c,r); assert len(s['candidate_error_cells'])>1
    with pytest.raises(ContractError,match=REJECTIONS[5]): correct(c,r,s)
def test_common_mode_detected_by_history():
    c=encode((1,0,-1,1)); r=dict(c['cell_values']); r['A']+=2; r['F']=(-r['A'])%72; s=diagnose(c,r); assert s['history_syndrome']==1
def test_dynamic_gate_and_replay():
    assert execute_dynamic_gate((1,0,-1,1))['output']==[2,1,0,2]
    x=run(R); assert x['correction_replay_exact'] and x['false_correction_rate']==0 and all(n['passed'] for n in x['negative_cases'])
def test_workloads(): assert len(workloads())==14 and workloads()[-1]['held_out']

from pathlib import Path
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, stable
from native_projects.hhs_vm81_native_exposure.hhs_pass079_native_opcode_registry_v1 import build_registry
from native_projects.hhs_vm81_native_exposure.hhs_pass080_constraint_membrane_v1 import canonical_membrane_state
from native_projects.hhs_exact_recursive_symbolic_runtime.hhs_pass081_runtime_v1 import *
ROOT=Path(__file__).resolve().parents[1]

def admitted(state=None):
    state=state or canonical_membrane_state(); b=build_registry(ROOT)['entries'][0]
    req={'binding_root_hash72':b['binding_root_hash72'],'authority_scope':b['authority_scope'],'lease_status':'ACTIVE_VALIDATED','vm81_lane_binding_status':'BOUND_WITNESSED','pre_state_root':product_root('hhs_vm81_pre_state_v1',stable(state)),'canonical_operand_commitment_status':'BOUND_WITNESSED','lease_boundary':'SEQUENCE_1'}
    return b['native_opcode'],req,state

def test_exact_ratio_and_history():
    r=ExactRatio(6,9,'6/9'); assert r.normalized==Fraction(2,3); assert r.to_dict()['source_numerator']==6
    assert r.multiply(ExactRatio(3,2)).normalized==1
    assert r.reciprocal().normalized==Fraction(3,2)

def test_float_rejected():
    op,q,s=admitted(); s=dict(s); s['A']=1.0
    with pytest.raises(ContractError): execute(ROOT,op,q,s,'A==B')

def test_parser_and_local_p():
    op,q,s=admitted(); x=execute(ROOT,op,q,s,'{A==B,(B==C),A==A}')
    assert len(x['gates'])==3 and len({g['local_p'] for g in x['gates']})==3
    assert x['receipt']['exact_source']=='{A==B,(B==C),A==A}'

def test_universal_identity_occurrence_distinction():
    op,q,s=admitted(); x=execute(ROOT,op,q,s,'x==y,x==z')
    xs=[o for o in x['universal_registry']['occurrences'] if o['name']=='x']
    assert len(xs)==2 and xs[0]['identity_root']==xs[1]['identity_root'] and xs[0]['occurrence_root']!=xs[1]['occurrence_root']

def test_directional_noncommutativity():
    op,q,s=admitted(); x=execute(ROOT,op,q,s,'dog bites man==man bites dog')
    g=x['gates'][0]; assert g['forward_path']!=g['reverse_path']

def test_unresolved_not_false():
    op,q,s=admitted(); x=execute(ROOT,op,q,s,'A==B')
    assert x['receipt']['closure_classification']==0 and x['status']!='PROVEN_NO_GLOBAL_CLOSURE'

def test_fixed_point():
    op,q,s=admitted(); x=execute(ROOT,op,q,s,'A==A')
    assert x['receipt']['closure_classification']==1

def test_loshu_vm81_order():
    op,q,s=admitted(); x=execute(ROOT,op,q,s,'A==A')
    assert [c['value'] for c in x['lo_shu_vm81_mapping']]==[4,9,2,3,5,7,8,1,6]

def test_local_substitution_shadowing():
    op,q,s=admitted(); x=execute(ROOT,op,q,s,'A==A',substitutions=[{'scope':'parent','carrier_sequence':[7],'value':'X'},{'scope':'child','parent_scope':'parent','carrier_sequence':[7],'value':'Y'}])
    assert len(x['receipt']['local_substitution_mapping_roots'])==2

def test_pass080_rejection_blocks_execution():
    op,q,s=admitted(canonical_membrane_state({'A':2})); x=execute(ROOT,op,q,s,'A==A')
    assert x['status']=='PASS_080_ADMISSION_NOT_SATISFIED' and not x['pass081_execution_occurred']

def test_receipt_replay_deterministic():
    op,q,s=admitted(); a=execute(ROOT,op,q,s,CALIBRATION_SOURCE); b=execute(ROOT,op,q,s,CALIBRATION_SOURCE)
    assert a['receipt']['final_hash72_witness_root']==b['receipt']['final_hash72_witness_root']

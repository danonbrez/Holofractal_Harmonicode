from copy import deepcopy
from fractions import Fraction
import pytest

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass117_vm81_deterministic_quantum_simulation_v1 import NativeSymbolicAmplitude
from hhs_runtime.hhs_pass118_symbolic_harmonicode_runtime_v1 import *


def engine(): return HarmonicodeRuntimeEngine()
def auth(): return _hash('pass118-test-authority',118)

def program():
    return {
        "schema": PROGRAM_SCHEMA,
        "program_id": "pass118:test",
        "scope": "test",
        "symbols": [
            {"name":"x","type":"RATIONAL","value":{"node":"literal","kind":"RATIONAL","value":"9/8"}},
            {"name":"y","type":"RATIONAL","value":{"node":"literal","kind":"RATIONAL","value":"8/9"}},
        ],
        "operations": [
            {"kind":"bind","name":"product","expression":{"node":"call","op":"multiply","args":[{"node":"symbol","name":"x"},{"node":"symbol","name":"y"}]}},
            {"kind":"assert","expression":{"node":"call","op":"equal","args":[{"node":"symbol","name":"product"},{"node":"literal","kind":"INTEGER","value":1}]}},
        ],
    }

def test_self_test(): assert pass118_self_test()['status']=='PASS'

def test_exact_program_execution_and_proof():
    x=engine().execute_program(program(),authority_root_hash72=auth())
    assert x['outputs'][-1]['value'] is True
    assert len(x['proofs'])==1 and x['proofs'][0]['proof_status']=='VALIDATED'

def test_runtime_equivalence():
    r=engine().validate_runtime_equivalence(program(),authority_root_hash72=auth())
    assert r['value_match'] and r['state_match'] and r['receipt_match']

def test_hash72_replay_order_detects_mutation():
    e=engine(); x=e.execute_program(program(),authority_root_hash72=auth()); bad=deepcopy(x); bad['transitions'].reverse()
    with pytest.raises(Pass118Error) as z: e.replay_hash72_program(bad,authority_root_hash72=auth())
    assert z.value.code=='REJECT_HASH72_ORDER_LOSS'

def test_replay_requires_payload():
    e=engine(); x=e.execute_program(program(),authority_root_hash72=auth()); del x['transitions'][0]['operation_payload']
    with pytest.raises(Pass118Error) as z: e.replay_hash72_program(x,authority_root_hash72=auth())
    assert z.value.code=='REJECT_HASH72_REPLAY_WITH_MISSING_OPERATION_PAYLOAD'

def test_float_literal_rejected():
    with pytest.raises(Pass118Error) as z: engine().evaluate_expression({'node':'literal','kind':'RATIONAL','value':0.5})
    assert z.value.code=='REJECT_FLOAT_AS_CANONICAL_EXACT_RESULT'

def test_trinary_zero_preserved():
    e=engine(); out=e.evaluate_expression({'node':'call','op':'trinary_and','args':[{'node':'literal','kind':'TRINARY','value':1},{'node':'literal','kind':'TRINARY','value':0}]})
    assert out['result']['value']=={'kind':'TRINARY','value':0}

def test_symbolic_b_inverse_exact_multiply():
    e=engine(); expr={'node':'call','op':'multiply','args':[{'node':'literal','kind':'B_INVERSE'},{'node':'literal','kind':'B_INVERSE'}]}
    out=e.evaluate_expression(expr)
    amp=out['native_value']; assert isinstance(amp,NativeSymbolicAmplitude) and amp.probability()==Fraction(1,4)
    assert amp.real.rational==Fraction(1,2) and amp.real.b_coeff==0

def test_tensor_matmul_hadamard_exact():
    e=engine(); b=NativeSymbolicAmplitude.b_inverse(); one=NativeSymbolicAmplitude.make(1); neg=NativeSymbolicAmplitude.make(-1); zero=NativeSymbolicAmplitude.make()
    h=TensorValue((2,2),(b,b,b,b*neg)); ket=TensorValue((2,),(one,zero)); out=e.matmul(h,ket)
    assert out.values==(b,b)

def test_phase_gear_exact_vm81_execution():
    p=engine().construct_phase_gear(Fraction(1),Fraction(1),Fraction(-1),Fraction(-1),authority_root_hash72=auth())
    assert p['execution_status']=='PHASE_GEAR_VM81_EXECUTED' and p['decision']==1

def test_phase_gear_bad_reciprocal_rejected():
    with pytest.raises(Pass118Error) as z: engine().construct_phase_gear(Fraction(2),Fraction(2),Fraction(1),Fraction(1),authority_root_hash72=auth())
    assert z.value.code=='REJECT_RECIPROCAL_PAIR_MISMATCH'

def test_phase_rotation_has_inverse_contract():
    e=engine(); p=e.construct_phase_gear(Fraction(1),Fraction(1),Fraction(-1),Fraction(-1),authority_root_hash72=auth()); q=e.rotate_phase_gear(p,1); r=e.rotate_phase_gear(q,-1)
    assert [r[k] for k in ('x','y','z','w')]==[p[k] for k in ('x','y','z','w')]

def test_multimodal_token_and_emit():
    e=engine(); t=e.construct_multimodal_token(source_root_hash72='source',token_class='MATH_TOKEN',surface_forms=[{'modality':'TEXT','value':'b^-1'},{'modality':'MATH','value':{'symbol':'b^-1'}}],relations=[{'source':'b^-1','relation':'DENOTES','target':'1/sqrt(2)','direction':'FORWARD'}],grammar_role='TERM',context_root_hash72='context',provenance_root_hash72='proof',renderable_modalities=['TEXT'])
    assert e.emit_token(t,'TEXT')['emission_status']=='EMITTED'
    with pytest.raises(Pass118Error) as z: e.emit_token(t,'MATH')
    assert z.value.code=='REJECT_NONRENDERABLE_TOKEN_REPORTED_AS_EMITTED'

def test_bad_relation_direction_rejected():
    with pytest.raises(Pass118Error) as z: engine().construct_multimodal_token(source_root_hash72='s',token_class='X',surface_forms=[{'modality':'TEXT','value':'x'}],relations=[{'source':'a','relation':'R','target':'b'}],grammar_role='TERM',context_root_hash72='c',provenance_root_hash72='p',renderable_modalities=['TEXT'])
    assert z.value.code=='REJECT_MULTIMODAL_RELATION_DIRECTION_LOSS'

def test_unknown_opcode_rejected():
    p=program(); p['operations'][0]['kind']='invented'
    with pytest.raises(Pass118Error) as z: engine().execute_program(p,authority_root_hash72=auth())
    assert z.value.code=='REJECT_HARMONICODE_OPCODE_WITHOUT_RUNTIME_SURFACE'

def test_registry():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    svc=next(x for x in make_default_service_registry().services() if x['name']=='runtime.symbolic_harmonicode_reasoning.pass118')
    assert svc['conformance_decision']['derivation_complete'] is True

def test_symbolic_i_minus_i_ers_zero_sum_phase_gear():
    i=NativeSymbolicAmplitude.make(imag_rational=1)
    minus_i=NativeSymbolicAmplitude.make(imag_rational=-1)
    p=engine().construct_phase_gear(i,minus_i,i,minus_i,require_negation=True,authority_root_hash72=auth())
    assert p['domain']=='HARMONICODE_Q_B_I' and p['decision']==0
    assert 'y=-x' in p['relations'] and p['execution_status']=='PHASE_GEAR_VM81_EXECUTED'

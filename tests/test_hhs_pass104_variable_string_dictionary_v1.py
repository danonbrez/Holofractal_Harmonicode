from pathlib import Path
import pytest
from native_projects.hhs_bifurcation_calibration.hhs_pass104_variable_string_dictionary_v1 import *
R=Path(__file__).resolve().parents[1]
def test_parent(): assert load_parent(R)['manifest']['pass_id']=='PASS_103'
def test_lengths():
 s=canonical_string('Ψ'); assert s['code_point_length']==1 and s['byte_length_utf8']>1
def test_exact_empty_and_missing():
 d=StringDictionary(); d.bind('empty',''); assert d.lookup_exact('empty')['value']['value']==''
 with pytest.raises(ContractError): d.lookup_exact('missing')
def test_typed_ordered_expansion():
 d=StringDictionary(); r=d.expand('${a} then ${b}',{'a':'A','b':'B'},{'a':'OP','b':'OP'},{'a':'OP','b':'OP'}); assert r['expanded_text']=='A then B' and [x['variable'] for x in r['ordered_variable_bindings']]==['a','b']
def test_partial():
 d=StringDictionary(); r=d.expand('${a} ${b}',{'a':'A'},{'a':'OP'},{'a':'OP','b':'OP'},partial=True); assert r['unresolved_slots']==['b']
def test_type_rejection():
 d=StringDictionary();
 with pytest.raises(ContractError): d.expand('${x}',{'x':'A'},{'x':'STRING'},{'x':'OP'})
def test_run():
 r=run(R); assert r['historical_replay_exact'] and r['empty_string_bound'] and len(r['workloads'])==18 and len(r['negative_cases'])==16

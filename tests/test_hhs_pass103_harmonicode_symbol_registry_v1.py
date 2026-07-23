from pathlib import Path
import pytest
from native_projects.hhs_bifurcation_calibration.hhs_pass103_harmonicode_symbol_registry_v1 import *
R=Path(__file__).resolve().parents[1]
def test_parent(): assert load_parent(R)['manifest']['pass_id']=='PASS_102'
def test_unicode_identity(): assert unicode_identity('é')['canonical_text']==unicode_identity('e\u0301')['canonical_text']
def test_scoped_bindings_and_history():
 r=SymbolRegistry(); a=canonical_object('INTEGER',1); b=canonical_object('INTEGER',2); x=r.bind('x',a,scope='LOCAL'); r.bind('x',b,scope='LOCAL',allow_shadow=True); assert r.resolve('x')['target_root_hash72']==b['target_root_hash72']; assert r.resolve('x',version=1)['binding_root_hash72']==x['binding_root_hash72']
def test_alias_not_identity():
 r=SymbolRegistry(); r.bind('α',canonical_object('INTEGER',72),scope='GLOBAL'); a=r.alias('𝛼','α',scope='GLOBAL'); assert not a['complete_identity']
def test_order_and_cycle():
 r=SymbolRegistry(); r.bind('α',canonical_object('INTEGER',1)); r.bind('β',canonical_object('INTEGER',2)); assert len(r.expand('γ',{'γ':['α','β']})['ordered_target_roots'])==2
 with pytest.raises(ContractError): r.expand('γ',{'γ':['γ']})
def test_merge_conflict():
 a=SymbolRegistry(); b=SymbolRegistry(); a.bind('x',canonical_object('INTEGER',1)); b.bind('x',canonical_object('INTEGER',2)); assert merge(a,b)['status']=='ALPHABET_CONFLICT'
def test_run():
 x=run(R); assert x['historical_replay_exact'] and x['ordered_substitution_preserved'] and len(x['workloads'])==18 and len(x['negative_cases'])==14

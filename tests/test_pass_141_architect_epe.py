import json
from pathlib import Path
import pytest
from hhs_runtime.harmonicode_architect_entropic_phase_equilibrium_v1 import ArchitectEntropicPhaseEquilibrium, EquilibriumError

def req():
 return {"request_id":"p141","ethical_policy":{"max_cycles":9},"architect_request":{
  "request_id":"arch","seed_request":{"request_id":"seed","agent":"A","assignments":{"g":"5/4","h":"4/5","rho":"1/20","xy":1},"constraints":[{"id":"r","lhs":"g*h","rhs":"xy"},{"id":"d","lhs":"rho","rhs":"g+h-2*xy"}],"goals":[{"id":"bad","lhs":"rho*g","rhs":"0"}]},
  "candidate_patches":[{"goals":[{"id":"ok","lhs":"rho*g","rhs":"(g-xy)**2"}]}],"max_cycles":3}}

def test_optimize_cache_readmit(tmp_path):
 rt=ArchitectEntropicPhaseEquilibrium([tmp_path/'a',tmp_path/'b'])
 r=rt.execute(req()); assert r['equilibrium']['equilibrium'] is True
 key=r['cache_commit']['cache_key']; x=rt.readmit(key); assert x['readmitted'] is True

def test_mirror_repairs_corruption(tmp_path):
 rt=ArchitectEntropicPhaseEquilibrium([tmp_path/'a',tmp_path/'b'])
 r=rt.execute(req()); key=r['cache_commit']['cache_key']
 p=Path(r['cache_commit']['paths'][0]); p.write_text('corrupt')
 x=rt.readmit(key); assert x['readmitted'] and x['cache']['repaired']

def test_failed_goal_not_equilibrium(tmp_path):
 q=req(); q['architect_request']['candidate_patches']=[]
 r=ArchitectEntropicPhaseEquilibrium([tmp_path/'a']).execute(q)
 assert r['equilibrium']['equilibrium'] is False

def test_authority_patch_rejected(tmp_path):
 q=req(); q['architect_request']['candidate_patches']=[{"authority":"SELF"}]
 with pytest.raises(Exception): ArchitectEntropicPhaseEquilibrium([tmp_path/'a']).execute(q)

def test_missing_cache_fails(tmp_path):
 rt=ArchitectEntropicPhaseEquilibrium([tmp_path/'a'])
 with pytest.raises(EquilibriumError): rt.readmit('0'*64)

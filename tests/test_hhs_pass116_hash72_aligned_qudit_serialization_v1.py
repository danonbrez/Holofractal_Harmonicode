from copy import deepcopy
import pytest
from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass114_palindromic_decimal_state_v1 import NumeralRecoveryContract
from hhs_runtime.hhs_pass115_canonical_qudit_serialization_v1 import CanonicalQuditSerializationEngine,ManifoldContract
from hhs_runtime.hhs_pass116_hash72_aligned_qudit_serialization_v1 import Hash72AlignedQuditEngine,Hash72AlignmentError,pass116_self_test

def fixture():
 q=CanonicalQuditSerializationEngine(); m=q.serialize([((r*3+r//3+c)%9) for r in range(9) for c in range(9)],contract=ManifoldContract()); a=_hash('a',116); s=_hash('s',116); n=q.encode_with_pass114(m,recovery_contract=NumeralRecoveryContract(30000000,80000000,50000000,2048),authority_root_hash72=a)['numeral']; return q,m,a,s,n

def test_full(): assert pass116_self_test()['status']=='PASS'
def test_symbol_map_injective(): assert len(set(Hash72AlignedQuditEngine.symbol_map().values()))==14
def test_roundtrip():
 q,m,a,s,n=fixture(); e=Hash72AlignedQuditEngine(); x=e.align(m,numeral=n,authority_root_hash72=a,security_policy_root_hash72=s); r=e.recover(x,available_work_units=80000000,available_memory_bytes=50000000,authority_root_hash72=a,security_policy_root_hash72=s); assert r['manifold']==m
def test_order_mutation_rejected():
 q,m,a,s,n=fixture(); e=Hash72AlignedQuditEngine(); x=e.align(m,numeral=n,authority_root_hash72=a,security_policy_root_hash72=s); b=deepcopy(x); b['cell_witnesses'][0],b['cell_witnesses'][1]=b['cell_witnesses'][1],b['cell_witnesses'][0]; b['total_encoding_root_hash72']=_hash('hhs_pass116_total_encoding_v1',{k:deepcopy(v) for k,v in b.items() if k!='total_encoding_root_hash72'}); 
 with pytest.raises(Hash72AlignmentError): e.validate(b,m)
def test_authority_rejected():
 q,m,a,s,n=fixture(); e=Hash72AlignedQuditEngine(); x=e.align(m,numeral=n,authority_root_hash72=a,security_policy_root_hash72=s)
 with pytest.raises(Hash72AlignmentError) as z: e.recover(x,available_work_units=80000000,available_memory_bytes=50000000,authority_root_hash72='bad',security_policy_root_hash72=s)
 assert z.value.code=='REJECT_AUTHORITY_ROOT_NOT_PRESERVED'
def test_security_rejected():
 q,m,a,s,n=fixture(); e=Hash72AlignedQuditEngine(); x=e.align(m,numeral=n,authority_root_hash72=a,security_policy_root_hash72=s)
 with pytest.raises(Hash72AlignmentError) as z: e.recover(x,available_work_units=80000000,available_memory_bytes=50000000,authority_root_hash72=a,security_policy_root_hash72='bad')
 assert z.value.code=='REJECT_SECURITY_POLICY_ROOT_NOT_PRESERVED'
def test_payload_required():
 q,m,a,s,n=fixture(); e=Hash72AlignedQuditEngine(); x=e.align(m,numeral=n,authority_root_hash72=a,security_policy_root_hash72=s); b=deepcopy(x); b['reversible_payload']=None; b['total_encoding_root_hash72']=_hash('hhs_pass116_total_encoding_v1',{k:deepcopy(v) for k,v in b.items() if k!='total_encoding_root_hash72'})
 with pytest.raises(Hash72AlignmentError) as z: e.validate(b,m)
 assert z.value.code=='REJECT_HASH72_USED_AS_PAYLOAD_REPLACEMENT'
def test_registry():
 from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
 svc=next(x for x in make_default_service_registry().services() if x['name']=='runtime.hash72_aligned_qudit_serialization.pass116'); assert svc['conformance_decision']['derivation_complete'] is True

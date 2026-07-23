from copy import deepcopy
from fractions import Fraction
import pytest
from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass117_vm81_deterministic_quantum_simulation_v1 import *

def fixture():
 e=VM81QuantumSimulationEngine(); a=_hash('a',117); s=_hash('substrate',116); st=e.construct_state([2,2],{0:ExactComplex.make(Fraction(1,2)),1:ExactComplex.make(Fraction(1,2)),2:ExactComplex.make(Fraction(1,2)),3:ExactComplex.make(Fraction(1,2))},aligned_substrate_root_hash72=s,authority_root_hash72=a); c=_hash('constraint',{'allowed':[0,3]}); return e,a,s,st,c

def test_self(): assert pass117_self_test()['status']=='PASS'
def test_coordinate_bijection():
 for i in range(12): assert VM81QuantumSimulationEngine.coordinate_to_index(VM81QuantumSimulationEngine.index_to_coordinate(i,[2,3,2]),[2,3,2])==i
def test_float_rejected():
 e=VM81QuantumSimulationEngine()
 with pytest.raises(QuantumSimulationError) as z: ExactComplex.make(0.5)
 assert z.value.code=='REJECT_FLOAT_AMPLITUDE_AS_CANONICAL_AUTHORITY'
def test_unnormalized_rejected():
 e=VM81QuantumSimulationEngine()
 with pytest.raises(QuantumSimulationError) as z: e.construct_state([2],{0:ExactComplex.make(1),1:ExactComplex.make(1)},aligned_substrate_root_hash72='s',authority_root_hash72='a')
 assert z.value.code=='REJECT_UNNORMALIZED_SUPERPOSITION'
def test_seeded_replay():
 e,a,s,st,c=fixture(); x=e.measure(st,admissible_indices=[0,3],seed='same',authority_root_hash72=a,constraint_contract_root_hash72=c); y=e.replay_measurement(st,x['constructor'],seed='same',authority_root_hash72=a); assert x['collapsed_state']==y['collapsed_state']
def test_seed_changes_are_witnessed():
 e,a,s,st,c=fixture(); x=e.measure(st,admissible_indices=[0,3],seed='a',authority_root_hash72=a,constraint_contract_root_hash72=c); y=e.measure(st,admissible_indices=[0,3],seed='b',authority_root_hash72=a,constraint_contract_root_hash72=c); assert x['constructor']['entropy_witness_root_hash72']!=y['constructor']['entropy_witness_root_hash72']
def test_constraint_zero_mass_rejected():
 e,a,s,st,c=fixture()
 with pytest.raises(QuantumSimulationError) as z: e.measure(st,admissible_indices=[],seed='x',authority_root_hash72=a,constraint_contract_root_hash72=c)
 assert z.value.code=='REJECT_COLLAPSE_WITH_EMPTY_ADMISSIBLE_DISTRIBUTION'
def test_authority_rejected():
 e,a,s,st,c=fixture()
 with pytest.raises(QuantumSimulationError) as z: e.measure(st,admissible_indices=[0],seed='x',authority_root_hash72='bad',constraint_contract_root_hash72=c)
 assert z.value.code=='REJECT_COLLAPSE_WITHOUT_AUTHORITY'
def test_exhaustive_weights_one():
 e,a,s,st,c=fixture(); x=e.exhaustive_measurement(st,admissible_indices=[0,3],constraint_contract_root_hash72=c); assert Fraction(x['total_weight']['numerator'],x['total_weight']['denominator'])==1 and len(x['branches'])==2
def test_gate_order_committed():
 e,a,s,st,c=fixture(); x=e.apply_gate(st,'X',[0]); x=e.apply_gate(x,'PHASE_I',[0]); y=e.apply_gate(st,'PHASE_I',[0]); y=e.apply_gate(y,'X',[0]); assert x['state_root_hash72']!=y['state_root_hash72']
def test_swap_reversible():
 e,a,s,st,c=fixture(); x=e.apply_gate(st,'SWAP',[0,1]); y=e.apply_gate(x,'SWAP',[0,1]); assert e._amps(y)==e._amps(st)
def test_state_corruption_rejected():
 e,a,s,st,c=fixture(); b=deepcopy(st); b['nonzero_terms'][0]['amplitude']['real']['numerator']=9
 with pytest.raises(QuantumSimulationError) as z: e.validate_state(b)
 assert z.value.code=='REJECT_STATE_ROOT_MISMATCH'
def test_resource_bound():
 e=VM81QuantumSimulationEngine(QuantumResourceContract(max_basis_states=4))
 with pytest.raises(QuantumSimulationError) as z: e.construct_state([3,2],{0:ExactComplex.make(1)},aligned_substrate_root_hash72='s',authority_root_hash72='a')
 assert z.value.code=='REJECT_UNBOUNDED_HILBERT_SPACE_EXPANSION'
def test_registry():
 from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
 svc=next(x for x in make_default_service_registry().services() if x['name']=='runtime.vm81_deterministic_quantum_simulation.pass117'); assert svc['conformance_decision']['derivation_complete'] is True

def symbolic_fixture():
 e=VM81QuantumSimulationEngine(); a=_hash('symbolic-authority',117); s=_hash('symbolic-substrate',116); return e,a,s

def test_symbolic_b_inverse_exact():
 a=NativeSymbolicAmplitude.b_inverse(); assert (a*a).real==ExactQuadratic.make(Fraction(1,2)) and a.probability()==Fraction(1,2)

def test_symbolic_balanced_state_exact():
 e,a,s=symbolic_fixture(); st=e.construct_symbolic_balanced_state(aligned_substrate_root_hash72=s,authority_root_hash72=a)
 assert st['simulation_model']=='FINITE_NATIVE_SYMBOLIC_TENSOR_STATE_VECTOR'
 assert [Fraction(t['probability']['numerator'],t['probability']['denominator']) for t in st['nonzero_terms']]==[Fraction(1,2),Fraction(1,2)]

def test_symbolic_hadamard_unitary_proof():
 e,_,_=symbolic_fixture(); assert e.prove_symbolic_hadamard_unitary()['valid'] is True

def test_symbolic_hadamard_basis_zero():
 e,a,s=symbolic_fixture(); st=e.construct_state([2],{0:ExactComplex.make(1)},aligned_substrate_root_hash72=s,authority_root_hash72=a); out=e.apply_gate(st,'HADAMARD_SYMBOLIC_B',[0])
 assert out['simulation_model']=='FINITE_NATIVE_SYMBOLIC_TENSOR_STATE_VECTOR'; assert e._amps(out)[0]==NativeSymbolicAmplitude.b_inverse(); assert e._amps(out)[1]==NativeSymbolicAmplitude.b_inverse()

def test_double_symbolic_hadamard_recovers_basis():
 e,a,s=symbolic_fixture(); st=e.construct_state([2],{0:ExactComplex.make(1)},aligned_substrate_root_hash72=s,authority_root_hash72=a); out=e.apply_gate(e.apply_gate(st,'HADAMARD_SYMBOLIC_B',[0]),'HADAMARD_SYMBOLIC_B',[0]); amps=e._amps(out)
 assert amps[0].probability()==1 and 1 not in amps

def test_symbolic_bell_state():
 e,a,s=symbolic_fixture(); st=e.construct_symbolic_bell_state(aligned_substrate_root_hash72=s,authority_root_hash72=a); amps=e._amps(st)
 assert set(amps)=={0,3}; assert amps[0].probability()==amps[3].probability()==Fraction(1,2)

def test_tensor_chain_receipt_replay_deterministic():
 e,a,s=symbolic_fixture(); st=e.construct_state([2],{0:ExactComplex.make(1)},aligned_substrate_root_hash72=s,authority_root_hash72=a); ops=[{'kind':'GATE','gate':'HADAMARD_SYMBOLIC_B','targets':[0]}]
 x=e.emulate_tensor_chain(st,ops,constraint_roots=['b^2=2']); y=e.emulate_tensor_chain(st,ops,constraint_roots=['b^2=2']); assert x['emulation_receipt_root_hash72']==y['emulation_receipt_root_hash72']

def test_symbolic_measurement_exact_and_replay():
 e,a,s=symbolic_fixture(); st=e.construct_symbolic_balanced_state(aligned_substrate_root_hash72=s,authority_root_hash72=a); c=_hash('symbolic-constraint',[0,1]); x=e.measure(st,admissible_indices=[0,1],seed='symbolic-seed',authority_root_hash72=a,constraint_contract_root_hash72=c); y=e.replay_measurement(st,x['constructor'],seed='symbolic-seed',authority_root_hash72=a); assert x['constructor']==y['constructor']

def test_invalid_symbolic_relation_rejected():
 d=NativeSymbolicAmplitude.b_inverse().to_dict(); d['real']['relation']='b^2=3'
 with pytest.raises(QuantumSimulationError) as z: NativeSymbolicAmplitude.from_dict(d)
 assert z.value.code=='REJECT_SYMBOLIC_RELATION_MISMATCH'

def test_unclosed_tensor_chain_rejected():
 e,a,s=symbolic_fixture(); st=e.construct_state([2],{0:ExactComplex.make(1)},aligned_substrate_root_hash72=s,authority_root_hash72=a)
 with pytest.raises(QuantumSimulationError) as z: e.emulate_tensor_chain(st,[{'kind':'UNKNOWN'}])
 assert z.value.code=='REJECT_TENSOR_CHAIN_UNCLOSED'

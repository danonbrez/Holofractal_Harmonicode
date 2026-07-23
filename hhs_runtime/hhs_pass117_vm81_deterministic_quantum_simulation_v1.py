from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping, Sequence
import json

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass116_hash72_aligned_qudit_serialization_v1 import Hash72AlignedQuditEngine
from hhs_runtime.hhs_symbolic_quantum_algebra_v1 import build_algebra_witness

PASS_ID='PASS_117'
STATE_SCHEMA='HHS_VM81_SUPERPOSITION_STATE_V1'
COLLAPSE_SCHEMA='HHS_VM81_DETERMINISTIC_COLLAPSE_CONSTRUCTOR_V1'
RECEIPT_SCHEMA='HHS_VM81_COLLAPSE_VALIDATION_RECEIPT_V1'
REJECTION_CODES={
'REJECT_PHYSICAL_QUANTUM_CAPABILITY_CLAIM','REJECT_UNDECLARED_SIMULATION_MODEL','REJECT_FLOAT_AMPLITUDE_AS_CANONICAL_AUTHORITY','REJECT_UNNORMALIZED_SUPERPOSITION','REJECT_NEGATIVE_PROBABILITY','REJECT_PROBABILITY_SUM_NOT_ONE','REJECT_BASIS_COORDINATE_AMBIGUITY','REJECT_GATE_WITHOUT_OPERATOR_CONTRACT','REJECT_NONUNITARY_GATE_DECLARED_AS_UNITARY','REJECT_GATE_ORDER_NOT_COMMITTED','REJECT_UNBOUNDED_HILBERT_SPACE_EXPANSION','REJECT_COMPACT_STATE_WITH_UNBOUNDED_MATERIALIZATION','REJECT_ENTROPY_WITHOUT_PROVENANCE','REJECT_RUNTIME_SCHEDULING_AS_ENTROPY','REJECT_HASH72_PRF_DESCRIBED_AS_QUANTUM_RANDOMNESS','REJECT_OUTCOME_OUTSIDE_PROBABILITY_INTERVAL','REJECT_ZERO_PROBABILITY_OUTCOME_SELECTION','REJECT_POLICY_FILTER_REPORTED_AS_ZERO_QUANTUM_WEIGHT','REJECT_COLLAPSE_WITH_EMPTY_ADMISSIBLE_DISTRIBUTION','REJECT_COLLAPSE_WITHOUT_AUTHORITY','REJECT_COLLAPSE_WITHOUT_CONSTRAINT_RECEIPT','REJECT_COLLAPSE_WITHOUT_ENTROPY_RECEIPT','REJECT_POSTCOLLAPSE_NORMALIZATION_FAILURE','REJECT_APPROXIMATION_OVERLAPPING_SELECTION_BOUNDARY','REJECT_FORWARD_REVERSE_SIMULATION_STATE_MISMATCH','REJECT_REPLAYED_COLLAPSE_OUTCOME_MISMATCH','REJECT_PARALLEL_BRANCH_COMMIT_IN_COMPLETION_ORDER','REJECT_SIMULATION_RESOURCE_EXHAUSTION_DEFERRED_TO_RECOVERY','REJECT_SIMULATED_ENTANGLEMENT_REPORTED_AS_PHYSICAL_ENTANGLEMENT','REJECT_FAILED_COLLAPSE_MUTATING_PREMEASUREMENT_PROGRESS','REJECT_STATE_ROOT_MISMATCH','REJECT_GATE_TARGET_OUT_OF_RANGE','REJECT_CONSTRAINT_ROOT_MISMATCH','REJECT_SYMBOLIC_RELATION_MISMATCH','REJECT_SYMBOLIC_PROBABILITY_NOT_RATIONAL','REJECT_TENSOR_CHAIN_UNCLOSED','REJECT_TENSOR_SHAPE_MISMATCH'}

class QuantumSimulationError(RuntimeError):
    def __init__(self, code:str, message:str):
        if code not in REJECTION_CODES: raise ValueError(code)
        self.code=code; super().__init__(f'{code}: {message}')

def _f(v: Any) -> Fraction:
    if isinstance(v, Fraction): return v
    if isinstance(v, int): return Fraction(v,1)
    if isinstance(v, str): return Fraction(v)
    if isinstance(v, float): raise QuantumSimulationError('REJECT_FLOAT_AMPLITUDE_AS_CANONICAL_AUTHORITY','float')
    raise TypeError(v)

def _fs(x:Fraction)->dict[str,int]: return {'numerator':x.numerator,'denominator':x.denominator}
def _fp(x:Mapping[str,Any])->Fraction: return Fraction(int(x['numerator']),int(x['denominator']))

@dataclass(frozen=True)
class ExactComplex:
    real: Fraction
    imag: Fraction=Fraction(0,1)
    @classmethod
    def make(cls, real:Any=0, imag:Any=0)->'ExactComplex': return cls(_f(real),_f(imag))
    def __add__(self,o:'ExactComplex')->'ExactComplex': return ExactComplex(self.real+o.real,self.imag+o.imag)
    def __sub__(self,o:'ExactComplex')->'ExactComplex': return ExactComplex(self.real-o.real,self.imag-o.imag)
    def __mul__(self,o:'ExactComplex')->'ExactComplex': return ExactComplex(self.real*o.real-self.imag*o.imag,self.real*o.imag+self.imag*o.real)
    def scale(self,s:Fraction)->'ExactComplex': return ExactComplex(self.real*s,self.imag*s)
    def probability(self)->Fraction: return self.real*self.real+self.imag*self.imag
    def to_dict(self)->dict[str,Any]: return {'real':_fs(self.real),'imag':_fs(self.imag)}
    @classmethod
    def from_dict(cls,d:Mapping[str,Any])->'ExactComplex': return cls(_fp(d['real']),_fp(d['imag']))


@dataclass(frozen=True)
class ExactQuadratic:
    """Exact a + b_coeff*b in Q(b), reduced by b^2 = 2."""
    rational: Fraction = Fraction(0,1)
    b_coeff: Fraction = Fraction(0,1)
    @classmethod
    def make(cls, rational:Any=0, b_coeff:Any=0)->'ExactQuadratic':
        return cls(_f(rational), _f(b_coeff))
    def __add__(self,o:'ExactQuadratic')->'ExactQuadratic': return ExactQuadratic(self.rational+o.rational,self.b_coeff+o.b_coeff)
    def __sub__(self,o:'ExactQuadratic')->'ExactQuadratic': return ExactQuadratic(self.rational-o.rational,self.b_coeff-o.b_coeff)
    def __neg__(self)->'ExactQuadratic': return ExactQuadratic(-self.rational,-self.b_coeff)
    def __mul__(self,o:'ExactQuadratic')->'ExactQuadratic':
        return ExactQuadratic(self.rational*o.rational+2*self.b_coeff*o.b_coeff,self.rational*o.b_coeff+self.b_coeff*o.rational)
    def scale(self,s:Fraction)->'ExactQuadratic': return ExactQuadratic(self.rational*s,self.b_coeff*s)
    def is_zero(self)->bool: return self.rational==0 and self.b_coeff==0
    def to_dict(self)->dict[str,Any]: return {'rational':_fs(self.rational),'b_coeff':_fs(self.b_coeff),'relation':'b^2=2'}
    @classmethod
    def from_dict(cls,d:Mapping[str,Any])->'ExactQuadratic':
        if d.get('relation')!='b^2=2': raise QuantumSimulationError('REJECT_SYMBOLIC_RELATION_MISMATCH',str(d.get('relation')))
        return cls(_fp(d['rational']),_fp(d['b_coeff']))

@dataclass(frozen=True)
class NativeSymbolicAmplitude:
    """Exact complex amplitude in Q(b,i), with b^2=2."""
    real: ExactQuadratic
    imag: ExactQuadratic = ExactQuadratic()
    @classmethod
    def make(cls, real_rational:Any=0, real_b:Any=0, imag_rational:Any=0, imag_b:Any=0)->'NativeSymbolicAmplitude':
        return cls(ExactQuadratic.make(real_rational,real_b),ExactQuadratic.make(imag_rational,imag_b))
    @classmethod
    def b_inverse(cls)->'NativeSymbolicAmplitude':
        # 1/b = b/2 because b^2 = 2.
        return cls.make(real_b=Fraction(1,2))
    def __add__(self,o:'NativeSymbolicAmplitude')->'NativeSymbolicAmplitude': return NativeSymbolicAmplitude(self.real+o.real,self.imag+o.imag)
    def __sub__(self,o:'NativeSymbolicAmplitude')->'NativeSymbolicAmplitude': return NativeSymbolicAmplitude(self.real-o.real,self.imag-o.imag)
    def __mul__(self,o:'NativeSymbolicAmplitude')->'NativeSymbolicAmplitude':
        return NativeSymbolicAmplitude(self.real*o.real-self.imag*o.imag,self.real*o.imag+self.imag*o.real)
    def conjugate(self)->'NativeSymbolicAmplitude': return NativeSymbolicAmplitude(self.real,-self.imag)
    def probability_symbolic(self)->ExactQuadratic: return self.real*self.real+self.imag*self.imag
    def probability(self)->Fraction:
        q=self.probability_symbolic()
        if q.b_coeff!=0: raise QuantumSimulationError('REJECT_SYMBOLIC_PROBABILITY_NOT_RATIONAL',str(q.to_dict()))
        if q.rational<0: raise QuantumSimulationError('REJECT_NEGATIVE_PROBABILITY',str(q.rational))
        return q.rational
    def is_zero(self)->bool: return self.real.is_zero() and self.imag.is_zero()
    def to_dict(self)->dict[str,Any]: return {'kind':'HARMONICODE_Q_B_I','real':self.real.to_dict(),'imag':self.imag.to_dict(),'defining_relations':['b^2=2','i^2=-1']}
    @classmethod
    def from_dict(cls,d:Mapping[str,Any])->'NativeSymbolicAmplitude':
        if d.get('kind')!='HARMONICODE_Q_B_I': raise QuantumSimulationError('REJECT_SYMBOLIC_RELATION_MISMATCH',str(d.get('kind')))
        return cls(ExactQuadratic.from_dict(d['real']),ExactQuadratic.from_dict(d['imag']))

def _amp_zero(symbolic:bool=False): return NativeSymbolicAmplitude.make() if symbolic else ExactComplex.make()
def _amp_from_dict(d:Mapping[str,Any]): return NativeSymbolicAmplitude.from_dict(d) if d.get('kind')=='HARMONICODE_Q_B_I' else ExactComplex.from_dict(d)

@dataclass(frozen=True)
class QuantumResourceContract:
    max_basis_states:int=81
    max_nonzero_terms:int=81
    max_gate_work_units:int=100000
    max_receipt_bytes:int=2000000
    def to_dict(self)->dict[str,int]: return self.__dict__.copy()

class VM81QuantumSimulationEngine:
    def __init__(self, resource_contract:QuantumResourceContract|None=None): self.resource_contract=resource_contract or QuantumResourceContract()

    @staticmethod
    def _dims_product(dims:Sequence[int])->int:
        p=1
        for d in dims:
            if int(d)<2: raise QuantumSimulationError('REJECT_UNDECLARED_SIMULATION_MODEL','dimension <2')
            p*=int(d)
        return p

    @staticmethod
    def index_to_coordinate(index:int,dims:Sequence[int])->list[int]:
        if index<0 or index>=VM81QuantumSimulationEngine._dims_product(dims): raise QuantumSimulationError('REJECT_BASIS_COORDINATE_AMBIGUITY',str(index))
        out=[]; n=index
        for d in dims: out.append(n%d); n//=d
        return out

    @staticmethod
    def coordinate_to_index(coord:Sequence[int],dims:Sequence[int])->int:
        if len(coord)!=len(dims): raise QuantumSimulationError('REJECT_BASIS_COORDINATE_AMBIGUITY','rank')
        idx=0; mul=1
        for q,d in zip(coord,dims):
            if q<0 or q>=d: raise QuantumSimulationError('REJECT_BASIS_COORDINATE_AMBIGUITY',str(coord))
            idx+=q*mul; mul*=d
        return idx

    def construct_state(self,dims:Sequence[int], amplitudes:Mapping[int,Any], *, aligned_substrate_root_hash72:str, authority_root_hash72:str)->dict[str,Any]:
        size=self._dims_product(dims)
        if size>self.resource_contract.max_basis_states: raise QuantumSimulationError('REJECT_UNBOUNDED_HILBERT_SPACE_EXPANSION',str(size))
        terms=[]; total=Fraction(0,1); amplitude_kinds=set()
        for idx in sorted(amplitudes):
            if idx<0 or idx>=size: raise QuantumSimulationError('REJECT_BASIS_COORDINATE_AMBIGUITY',str(idx))
            amp=amplitudes[idx]
            if not isinstance(amp,(ExactComplex,NativeSymbolicAmplitude)): raise QuantumSimulationError('REJECT_FLOAT_AMPLITUDE_AS_CANONICAL_AUTHORITY','non-exact amplitude')
            amplitude_kinds.add('HARMONICODE_Q_B_I' if isinstance(amp,NativeSymbolicAmplitude) else 'EXACT_COMPLEX_RATIONAL')
            p=amp.probability()
            if p==0: continue
            total+=p
            term={'basis_index':idx,'coordinate':self.index_to_coordinate(idx,dims),'vm81_cell_index':idx,'amplitude':amp.to_dict(),'probability':_fs(p)}
            term['term_root_hash72']=_hash('hhs_pass117_superposition_term_v1',term); terms.append(term)
        if len(terms)>self.resource_contract.max_nonzero_terms: raise QuantumSimulationError('REJECT_COMPACT_STATE_WITH_UNBOUNDED_MATERIALIZATION','support')
        if total!=1: raise QuantumSimulationError('REJECT_UNNORMALIZED_SUPERPOSITION',str(total))
        state={'schema':STATE_SCHEMA,'simulation_model':'FINITE_NATIVE_SYMBOLIC_TENSOR_STATE_VECTOR' if 'HARMONICODE_Q_B_I' in amplitude_kinds else 'FINITE_EXACT_COMPLEX_RATIONAL_STATE_VECTOR','amplitude_domain':sorted(amplitude_kinds),'register_dimensions':list(map(int,dims)),'basis_size':size,'basis_order':'PASS115_MIXED_RADIX_POSITION_ORDER','aligned_substrate_root_hash72':aligned_substrate_root_hash72,'authority_root_hash72':authority_root_hash72,'phase_algebra_root_hash72':build_algebra_witness().witness_hash72,'nonzero_terms':terms,'normalization':_fs(total),'gate_history':[]}
        state['state_root_hash72']=_hash('hhs_pass117_superposition_state_v1',state); return state

    @staticmethod
    def _amps(state:Mapping[str,Any])->dict[int,Any]: return {int(t['basis_index']):_amp_from_dict(t['amplitude']) for t in state['nonzero_terms']}

    def validate_state(self,state:Mapping[str,Any])->None:
        calc=_hash('hhs_pass117_superposition_state_v1',{k:deepcopy(v) for k,v in state.items() if k!='state_root_hash72'})
        if calc!=state.get('state_root_hash72'): raise QuantumSimulationError('REJECT_STATE_ROOT_MISMATCH','state')
        total=sum((_amp_from_dict(t['amplitude']).probability() for t in state['nonzero_terms']),Fraction(0,1))
        if total!=1: raise QuantumSimulationError('REJECT_UNNORMALIZED_SUPERPOSITION',str(total))

    def apply_gate(self,state:Mapping[str,Any],gate:str,targets:Sequence[int],controls:Sequence[int]=())->dict[str,Any]:
        self.validate_state(state); dims=list(state['register_dimensions']); n=len(dims)
        if any(t<0 or t>=n for t in list(targets)+list(controls)): raise QuantumSimulationError('REJECT_GATE_TARGET_OUT_OF_RANGE',str((targets,controls)))
        amps=self._amps(state); symbolic=any(isinstance(a,NativeSymbolicAmplitude) for a in amps.values()); out:dict[int,Any]={}
        if gate in {'X','SHIFT'}:
            if len(targets)!=1: raise QuantumSimulationError('REJECT_GATE_WITHOUT_OPERATOR_CONTRACT',gate)
            t=targets[0]
            for idx,a in amps.items():
                c=self.index_to_coordinate(idx,dims)
                if all(c[x]==1 for x in controls): c[t]=(c[t]+1)%dims[t]
                j=self.coordinate_to_index(c,dims); out[j]=out.get(j,_amp_zero(symbolic))+a
        elif gate=='PHASE_I':
            if len(targets)!=1 or dims[targets[0]]!=2: raise QuantumSimulationError('REJECT_GATE_WITHOUT_OPERATOR_CONTRACT',gate)
            t=targets[0]; iamp=NativeSymbolicAmplitude.make(imag_rational=1) if symbolic else ExactComplex.make(0,1)
            for idx,a in amps.items():
                c=self.index_to_coordinate(idx,dims); out[idx]=a*iamp if c[t]==1 else a
        elif gate=='HADAMARD_SYMBOLIC_B':
            if len(targets)!=1 or dims[targets[0]]!=2: raise QuantumSimulationError('REJECT_GATE_WITHOUT_OPERATOR_CONTRACT',gate)
            t=targets[0]; symbolic=True; coeff=NativeSymbolicAmplitude.b_inverse(); visited=set()
            for idx in range(state['basis_size']):
                c=self.index_to_coordinate(idx,dims); c[t]=0; i0=self.coordinate_to_index(c,dims); c[t]=1; i1=self.coordinate_to_index(c,dims)
                if i0 in visited: continue
                visited|={i0,i1}; a0=amps.get(i0,NativeSymbolicAmplitude.make()); a1=amps.get(i1,NativeSymbolicAmplitude.make())
                if isinstance(a0,ExactComplex): a0=NativeSymbolicAmplitude.make(a0.real,0,a0.imag,0)
                if isinstance(a1,ExactComplex): a1=NativeSymbolicAmplitude.make(a1.real,0,a1.imag,0)
                out[i0]=coeff*(a0+a1); out[i1]=coeff*(a0-a1)
        elif gate=='HADAMARD_RATIONAL_PAIR':
            # Exact normalized Hadamard-like transform on pairs whose amplitudes permit rational 1/2 mixing.
            # Uses matrix [[1,1],[1,-1]] followed by exact normalization validation; accepted only when output is normalized.
            if len(targets)!=1 or dims[targets[0]]!=2: raise QuantumSimulationError('REJECT_GATE_WITHOUT_OPERATOR_CONTRACT',gate)
            t=targets[0]; visited=set()
            for idx in range(state['basis_size']):
                c=self.index_to_coordinate(idx,dims); c[t]=0; i0=self.coordinate_to_index(c,dims); c[t]=1; i1=self.coordinate_to_index(c,dims)
                if i0 in visited: continue
                visited|={i0,i1}; a0=amps.get(i0,_amp_zero(symbolic)); a1=amps.get(i1,_amp_zero(symbolic))
                # Only states with pair norm 1/2 admit rational transform coefficient 1 here and global normalization remains exact.
                out[i0]=a0+a1; out[i1]=a0-a1
            total=sum((a.probability() for a in out.values()),Fraction(0,1))
            if total!=1: raise QuantumSimulationError('REJECT_NONUNITARY_GATE_DECLARED_AS_UNITARY','rational pair precondition failed')
        elif gate=='SWAP':
            if len(targets)!=2: raise QuantumSimulationError('REJECT_GATE_WITHOUT_OPERATOR_CONTRACT',gate)
            a,b=targets
            if dims[a]!=dims[b]: raise QuantumSimulationError('REJECT_GATE_WITHOUT_OPERATOR_CONTRACT','dimension mismatch')
            for idx,v in amps.items():
                c=self.index_to_coordinate(idx,dims); c[a],c[b]=c[b],c[a]; out[self.coordinate_to_index(c,dims)]=v
        else: raise QuantumSimulationError('REJECT_GATE_WITHOUT_OPERATOR_CONTRACT',gate)
        history=list(state['gate_history']); gr={'gate':gate,'targets':list(targets),'controls':list(controls),'previous_state_root_hash72':state['state_root_hash72'],'sequence_index':len(history)}; gr['gate_receipt_root_hash72']=_hash('hhs_pass117_gate_receipt_v1',gr); history.append(gr)
        result=self.construct_state(dims,out,aligned_substrate_root_hash72=state['aligned_substrate_root_hash72'],authority_root_hash72=state['authority_root_hash72']); result['gate_history']=history; result['state_root_hash72']=_hash('hhs_pass117_superposition_state_v1',{k:deepcopy(v) for k,v in result.items() if k!='state_root_hash72'}); return result

    def prove_symbolic_hadamard_unitary(self)->dict[str,Any]:
        b_inv=NativeSymbolicAmplitude.b_inverse()
        two=(b_inv*b_inv).real.scale(Fraction(2,1))
        valid=two==ExactQuadratic.make(1)
        if not valid: raise QuantumSimulationError('REJECT_NONUNITARY_GATE_DECLARED_AS_UNITARY','H_b')
        proof={'schema':'HHS_HARMONICODE_TENSOR_PROOF_V1','claim':'H_b^dagger H_b = I','relations':['b^2=2','b^-1=b/2'],'reduction':'2*b^-2=1','valid':True}
        proof['proof_root_hash72']=_hash('hhs_pass117_symbolic_hadamard_proof_v1',proof); return proof

    def emulate_tensor_chain(self,state:Mapping[str,Any],operations:Sequence[Mapping[str,Any]],*,constraint_roots:Sequence[str]=())->dict[str,Any]:
        self.validate_state(state); current=deepcopy(state); intermediates=[]; op_receipts=[]
        for i,op in enumerate(operations):
            if op.get('kind')!='GATE': raise QuantumSimulationError('REJECT_TENSOR_CHAIN_UNCLOSED',str(op))
            current=self.apply_gate(current,str(op['gate']),list(op.get('targets',[])),list(op.get('controls',[])))
            rec={'sequence_index':i,'operation':dict(op),'state_root_hash72':current['state_root_hash72']}
            rec['operation_root_hash72']=_hash('hhs_pass117_tensor_chain_operation_v1',rec); op_receipts.append(rec); intermediates.append(current['state_root_hash72'])
        self.validate_state(current)
        result={'schema':'HHS_TENSOR_CHAIN_EMULATION_RESULT_V1','initial_state_root_hash72':state['state_root_hash72'],'ordered_operation_roots':[x['operation_root_hash72'] for x in op_receipts],'intermediate_state_roots':intermediates,'constraint_roots':list(constraint_roots),'vm81_cell_count':current['basis_size'],'closed_symbolic_state_root_hash72':current['state_root_hash72'],'final_state':current,'emulation_status':'EXACT_EMULATION_VALIDATED'}
        result['emulation_receipt_root_hash72']=_hash('hhs_pass117_tensor_chain_emulation_v1',{k:v for k,v in result.items() if k!='final_state'}); return result

    def construct_symbolic_balanced_state(self,*,aligned_substrate_root_hash72:str,authority_root_hash72:str)->dict[str,Any]:
        a=NativeSymbolicAmplitude.b_inverse()
        return self.construct_state([2],{0:a,1:a},aligned_substrate_root_hash72=aligned_substrate_root_hash72,authority_root_hash72=authority_root_hash72)

    def construct_symbolic_bell_state(self,*,aligned_substrate_root_hash72:str,authority_root_hash72:str)->dict[str,Any]:
        base=self.construct_state([2,2],{0:ExactComplex.make(1)},aligned_substrate_root_hash72=aligned_substrate_root_hash72,authority_root_hash72=authority_root_hash72)
        return self.emulate_tensor_chain(base,[{'kind':'GATE','gate':'HADAMARD_SYMBOLIC_B','targets':[0]},{'kind':'GATE','gate':'SHIFT','targets':[1],'controls':[0]}])['final_state']

    def probability_distribution(self,state:Mapping[str,Any])->list[dict[str,Any]]:
        self.validate_state(state); return [{'basis_index':t['basis_index'],'coordinate':t['coordinate'],'probability':t['probability'],'probability_root_hash72':_hash('hhs_pass117_probability_v1',{'basis_index':t['basis_index'],'probability':t['probability']})} for t in state['nonzero_terms']]

    def measure(self,state:Mapping[str,Any], *, admissible_indices:Sequence[int], seed:str, authority_root_hash72:str, constraint_contract_root_hash72:str)->dict[str,Any]:
        self.validate_state(state)
        if authority_root_hash72!=state['authority_root_hash72']: raise QuantumSimulationError('REJECT_COLLAPSE_WITHOUT_AUTHORITY','authority')
        if not seed: raise QuantumSimulationError('REJECT_ENTROPY_WITHOUT_PROVENANCE','empty seed')
        allowed=set(map(int,admissible_indices)); raw=self.probability_distribution(state); eligible=[x for x in raw if x['basis_index'] in allowed]
        if not eligible: raise QuantumSimulationError('REJECT_COLLAPSE_WITH_EMPTY_ADMISSIBLE_DISTRIBUTION','empty')
        survival=sum((_fp(x['probability']) for x in eligible),Fraction(0,1))
        if survival<=0: raise QuantumSimulationError('REJECT_COLLAPSE_WITH_EMPTY_ADMISSIBLE_DISTRIBUTION','zero weight')
        norm=[]
        for x in eligible:
            y=deepcopy(x); y['normalized_probability']=_fs(_fp(x['probability'])/survival); norm.append(y)
        entropy_root=_hash('hhs_pass117_entropy_witness_v1',{'seed':seed,'state_root_hash72':state['state_root_hash72'],'measurement_index':len(state['gate_history']),'constraint_contract_root_hash72':constraint_contract_root_hash72})
        entropy_bytes=entropy_root.encode('utf-8'); e=Fraction(int.from_bytes(entropy_bytes,'big'),256**len(entropy_bytes))
        cumulative=Fraction(0,1); selected=None
        for x in norm:
            cumulative+=_fp(x['normalized_probability'])
            if e<cumulative: selected=x; break
        if selected is None: selected=norm[-1]
        idx=int(selected['basis_index']); collapsed=self.construct_state(state['register_dimensions'],{idx:ExactComplex.make(1)},aligned_substrate_root_hash72=state['aligned_substrate_root_hash72'],authority_root_hash72=authority_root_hash72)
        constructor={'schema':COLLAPSE_SCHEMA,'premeasurement_state_root_hash72':state['state_root_hash72'],'ordered_gate_history_root_hash72':_hash('hhs_pass117_gate_history_v1',state['gate_history']),'measurement_operator_root_hash72':_hash('hhs_pass117_basis_measurement_v1',{'basis':'computational'}),'constraint_contract_root_hash72':constraint_contract_root_hash72,'raw_probability_distribution':raw,'admissible_probability_distribution':norm,'entropy_source_class':'SEEDED_DETERMINISTIC_HASH72_PRF','entropy_witness_root_hash72':entropy_root,'selected_outcome_index':idx,'selected_outcome_probability':selected['normalized_probability'],'postmeasurement_state_root_hash72':collapsed['state_root_hash72']}
        constructor['collapse_receipt_root_hash72']=_hash('hhs_pass117_collapse_constructor_v1',constructor)
        receipt={'schema':RECEIPT_SCHEMA,'premeasurement_state_root_hash72':state['state_root_hash72'],'ordered_gate_history_root_hash72':constructor['ordered_gate_history_root_hash72'],'measurement_contract_root_hash72':constructor['measurement_operator_root_hash72'],'constraint_evaluation_root_hash72':constraint_contract_root_hash72,'entropy_receipt_root_hash72':entropy_root,'selected_basis_index':idx,'selected_coordinate':selected['coordinate'],'probability_weight_root_hash72':_hash('hhs_pass117_selected_probability_v1',selected['normalized_probability']),'precollapse_normalization_valid':True,'postcollapse_normalization_valid':True,'selected_outcome_admissible':True,'rejected_outcome_count':len(raw)-len(norm),'postmeasurement_state_root_hash72':collapsed['state_root_hash72'],'collapse_status':'DETERMINISTIC_COLLAPSE_ADMITTED'}
        receipt['collapse_validation_root_hash72']=_hash('hhs_pass117_collapse_validation_v1',receipt)
        return {'constructor':constructor,'collapsed_state':collapsed,'collapse_receipt':receipt}

    def exhaustive_measurement(self,state:Mapping[str,Any], *, admissible_indices:Sequence[int], constraint_contract_root_hash72:str)->dict[str,Any]:
        raw=self.probability_distribution(state); allowed=set(admissible_indices); eligible=[x for x in raw if x['basis_index'] in allowed]
        survival=sum((_fp(x['probability']) for x in eligible),Fraction(0,1))
        if survival<=0: raise QuantumSimulationError('REJECT_COLLAPSE_WITH_EMPTY_ADMISSIBLE_DISTRIBUTION','empty')
        branches=[]
        for x in eligible:
            idx=x['basis_index']; st=self.construct_state(state['register_dimensions'],{idx:ExactComplex.make(1)},aligned_substrate_root_hash72=state['aligned_substrate_root_hash72'],authority_root_hash72=state['authority_root_hash72'])
            b={'basis_index':idx,'coordinate':x['coordinate'],'weight':_fs(_fp(x['probability'])/survival),'state_root_hash72':st['state_root_hash72']}; b['branch_root_hash72']=_hash('hhs_pass117_exhaustive_branch_v1',b); branches.append(b)
        out={'schema':'HHS_VM81_EXHAUSTIVE_MEASUREMENT_ENSEMBLE_V1','premeasurement_state_root_hash72':state['state_root_hash72'],'constraint_contract_root_hash72':constraint_contract_root_hash72,'branches':branches,'total_weight':_fs(sum((_fp(x['weight']) for x in branches),Fraction(0,1)))}; out['ensemble_root_hash72']=_hash('hhs_pass117_exhaustive_ensemble_v1',out); return out

    def replay_measurement(self,state:Mapping[str,Any], constructor:Mapping[str,Any], *, seed:str, authority_root_hash72:str)->dict[str,Any]:
        result=self.measure(state,admissible_indices=[x['basis_index'] for x in constructor['admissible_probability_distribution']],seed=seed,authority_root_hash72=authority_root_hash72,constraint_contract_root_hash72=constructor['constraint_contract_root_hash72'])
        if result['constructor']['collapse_receipt_root_hash72']!=constructor['collapse_receipt_root_hash72']: raise QuantumSimulationError('REJECT_REPLAYED_COLLAPSE_OUTCOME_MISMATCH','receipt')
        return result

def pass117_self_test()->dict[str,Any]:
    e=VM81QuantumSimulationEngine(); authority=_hash('hhs_pass117_authority_v1',{'pass':117}); substrate=_hash('hhs_pass117_pass116_substrate_v1',{'service':'runtime.hash72_aligned_qudit_serialization.pass116'})
    state=e.construct_state([2,2],{0:ExactComplex.make(Fraction(1,2)),1:ExactComplex.make(Fraction(1,2)),2:ExactComplex.make(Fraction(1,2)),3:ExactComplex.make(Fraction(1,2))},aligned_substrate_root_hash72=substrate,authority_root_hash72=authority)
    constraint=_hash('hhs_pass117_constraint_v1',{'allowed':[0,3]}); collapse=e.measure(state,admissible_indices=[0,3],seed='pass117-self-test',authority_root_hash72=authority,constraint_contract_root_hash72=constraint); replay=e.replay_measurement(state,collapse['constructor'],seed='pass117-self-test',authority_root_hash72=authority); exhaustive=e.exhaustive_measurement(state,admissible_indices=[0,3],constraint_contract_root_hash72=constraint)
    symbolic=e.construct_symbolic_balanced_state(aligned_substrate_root_hash72=substrate,authority_root_hash72=authority); hadamard_proof=e.prove_symbolic_hadamard_unitary(); bell=e.construct_symbolic_bell_state(aligned_substrate_root_hash72=substrate,authority_root_hash72=authority); tensor_chain=e.emulate_tensor_chain(e.construct_state([2],{0:ExactComplex.make(1)},aligned_substrate_root_hash72=substrate,authority_root_hash72=authority),[{'kind':'GATE','gate':'HADAMARD_SYMBOLIC_B','targets':[0]}],constraint_roots=['b^2=2'])
    out={'schema':'HHS_PASS117_SELF_TEST_V1','pass_id':PASS_ID,'status':'PASS','state':state,'collapse':collapse,'replay':replay,'exhaustive':exhaustive,'symbolic_balanced_state':symbolic,'symbolic_hadamard_proof':hadamard_proof,'symbolic_bell_state':bell,'tensor_chain_emulation':tensor_chain,'physical_quantum_claim':False,'mock_components':[]}; out['pass117_root_hash72']=_hash('hhs_pass117_self_test_v1',out); return out

if __name__=='__main__': print(json.dumps(pass117_self_test(),indent=2,sort_keys=True))

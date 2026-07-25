from __future__ import annotations
from dataclasses import asdict,dataclass
from typing import Any,Callable,Mapping
from .audio import ExactScalar
from .convolution import ConvolutionKernel
from .core import LocalizedModulus,LocalizedRational,NFVError,NFVObject,TransitionPackage,canonical,hash216

def _vector3(values):
    result=tuple(v if isinstance(v,ExactScalar) else ExactScalar(*v) if isinstance(v,tuple) else ExactScalar(int(v)) for v in values)
    if len(result)!=3: raise NFVError('NFV_VECTOR3_REQUIRED','three components required')
    return result
@dataclass(frozen=True)
class InteractionReceiptBundle:
    audio_receipt:str; physics_receipt:str; graphics_receipt:str
    def __post_init__(self):
        if not self.audio_receipt or len({self.audio_receipt,self.physics_receipt,self.graphics_receipt})!=1: raise NFVError('NFV_INTERACTION_RECEIPT_MISMATCH','audio physics graphics receipts must match')
    @property
    def receipt(self):return self.audio_receipt
@dataclass(frozen=True)
class InteractionSample:
    amplitude:ExactScalar; field_gradient:tuple[ExactScalar,...]; curvature:ExactScalar; phase:ExactScalar; phase_gradient:tuple[ExactScalar,...]; constraint_gradient:tuple[ExactScalar,...]; energy:ExactScalar; nonary_residue:int; recursive_scale:int; modulus_state:LocalizedModulus; vm81_cell:int; graph_index:str; source_receipt:str; sample_index:str=''
    def __post_init__(self):
        object.__setattr__(self,'field_gradient',_vector3(self.field_gradient)); object.__setattr__(self,'phase_gradient',_vector3(self.phase_gradient)); object.__setattr__(self,'constraint_gradient',_vector3(self.constraint_gradient))
        if not 0<=self.nonary_residue<9 or self.recursive_scale<0 or not 0<=self.vm81_cell<81: raise NFVError('NFV_INVALID_INTERACTION_COORDINATE','invalid residue scale or VM81 cell')
        if len(self.graph_index)!=216 or not self.source_receipt: raise NFVError('NFV_INVALID_INTERACTION_BINDING','graph index and receipt required')
        expected=hash216(self.identity_payload())
        if self.sample_index and self.sample_index!=expected: raise NFVError('NFV_INTERACTION_IDENTITY_MISMATCH','sample index mismatch')
        object.__setattr__(self,'sample_index',expected)
    def identity_payload(self):
        return {'domain':'HHS-NFV-INTERACTION-SAMPLE-V1','amplitude':self.amplitude.to_dict(),'field_gradient':[v.to_dict() for v in self.field_gradient],'curvature':self.curvature.to_dict(),'phase':self.phase.to_dict(),'phase_gradient':[v.to_dict() for v in self.phase_gradient],'constraint_gradient':[v.to_dict() for v in self.constraint_gradient],'energy':self.energy.to_dict(),'nonary_residue':self.nonary_residue,'recursive_scale':self.recursive_scale,'modulus_state':self.modulus_state.to_dict(),'vm81_cell':self.vm81_cell,'graph_index':self.graph_index,'source_receipt':self.source_receipt}
@dataclass(frozen=True)
class ShaderGradientProjection:
    field_amplitude:float; field_gradient:tuple[float,float,float]; field_curvature:float; phase:float; phase_gradient:tuple[float,float,float]; luminance:float; source_sample_index:str; source_receipt:str; precision_profile:str; authoritative:bool=False
@dataclass(frozen=True)
class LocalizedForceComponent:
    exact:ExactScalar; localized:LocalizedRational
    def __post_init__(self):
        if self.localized.exact!=self.exact.fraction: raise NFVError('NFV_FORCE_RECONSTRUCTION_FAILURE','localized force mismatch')
@dataclass(frozen=True)
class CollisionForceCandidate:
    components:tuple[LocalizedForceComponent,...]; source_sample_index:str; source_receipt:str; candidate_index:str=''; status:str='PROVISIONAL'
    def __post_init__(self):
        if len(self.components)!=3 or self.status!='PROVISIONAL': raise NFVError('NFV_INVALID_COLLISION_CANDIDATE','invalid candidate')
        expected=hash216({'domain':'HHS-NFV-COLLISION-FORCE-V1','components':[{'exact':c.exact.to_dict(),'localized':c.localized.to_dict()} for c in self.components],'source_sample_index':self.source_sample_index,'source_receipt':self.source_receipt})
        object.__setattr__(self,'candidate_index',expected)
@dataclass(frozen=True)
class CollisionAdmissionResult:
    object_a:NFVObject; object_b:NFVObject; source_receipt:str; package_receipts:tuple[str,str]
def project_shader_gradient(sample:InteractionSample,*,precision_profile='IEEE754_RENDER_ONLY'):
    scalar=lambda x:float(x.fraction)
    return ShaderGradientProjection(scalar(sample.amplitude),tuple(scalar(v) for v in sample.field_gradient),scalar(sample.curvature),scalar(sample.phase),tuple(scalar(v) for v in sample.phase_gradient),scalar(sample.energy),sample.sample_index,sample.source_receipt,precision_profile,False)
def project_collision_force(sample:InteractionSample,*,alpha:ExactScalar,beta:ExactScalar,gamma:ExactScalar,contact_force,modulus:int):
    contact=_vector3(contact_force); components=[]
    for i in range(3):
        force=sample.field_gradient[i].multiply(alpha).negate().subtract(sample.phase_gradient[i].multiply(beta)).subtract(sample.constraint_gradient[i].multiply(gamma)).add(contact[i])
        localized=LocalizedRational.localize(force.numerator,force.denominator,numerator_modulus=modulus,denominator_modulus=modulus)
        components.append(LocalizedForceComponent(force,localized))
    return CollisionForceCandidate(tuple(components),sample.sample_index,sample.source_receipt)
def admit_collision_pair(obj_a,obj_b,candidate_a,candidate_b,*,candidate:CollisionForceCandidate,receipts:InteractionReceiptBundle,vm81_admit):
    if candidate.source_receipt!=receipts.receipt: raise NFVError('NFV_INTERACTION_RECEIPT_MISMATCH','candidate source receipt mismatch')
    a_state=dict(canonical(candidate_a)); b_state=dict(canonical(candidate_b)); a_state['_nfv_interaction_receipt']=receipts.receipt; b_state['_nfv_interaction_receipt']=receipts.receipt
    if not vm81_admit(obj_a,a_state) or not vm81_admit(obj_b,b_state): raise NFVError('NFV_VM81_COLLISION_REJECTED','pair admission rejected')
    pa=TransitionPackage.prepare(obj_a,'PROJECT_COLLISION_FORCE',a_state); pb=TransitionPackage.prepare(obj_b,'PROJECT_COLLISION_FORCE',b_state)
    new_a,closed_a=pa.commit(obj_a,vm81_admit=lambda _o,_s:True); new_b,closed_b=pb.commit(obj_b,vm81_admit=lambda _o,_s:True)
    return CollisionAdmissionResult(new_a,new_b,receipts.receipt,(closed_a.receipt,closed_b.receipt))
@dataclass(frozen=True)
class GraphConvolutionEdge:
    edge_id:str; lane_id:str; gain:ExactScalar; delay_samples:int; source_receipt:str; edge_index:str=''
    def __post_init__(self):
        if self.delay_samples<0 or not self.edge_id or not self.source_receipt: raise NFVError('NFV_INVALID_GRAPH_CONVOLUTION_EDGE','invalid edge')
        object.__setattr__(self,'edge_index',hash216({'domain':'HHS-NFV-GRAPH-CONVOLUTION-EDGE-V1','edge_id':self.edge_id,'lane_id':self.lane_id,'gain':self.gain.to_dict(),'delay_samples':self.delay_samples,'source_receipt':self.source_receipt}))
@dataclass(frozen=True)
class GraphProjectedKernel:
    kernel:ConvolutionKernel; edge_indices:tuple[str,...]; projection_index:str; authoritative:bool=False
def project_graph_edges_to_kernel(edges,*,lane_id,source_receipt,maximum_delay):
    selected=tuple(sorted((e for e in edges if e.lane_id==lane_id),key=lambda e:(e.delay_samples,e.edge_index)))
    if any(e.source_receipt!=source_receipt for e in selected): raise NFVError('NFV_INTERACTION_RECEIPT_MISMATCH','graph edge receipt mismatch')
    if any(e.delay_samples>maximum_delay for e in selected): raise NFVError('RESOURCE_BOUNDED','delay exceeds bound')
    coeff=[ExactScalar(0) for _ in range(maximum_delay+1)]
    for e in selected: coeff[e.delay_samples]=coeff[e.delay_samples].add(e.gain)
    kernel=ConvolutionKernel(lane_id,tuple(coeff),source_receipt)
    index=hash216({'domain':'HHS-NFV-GRAPH-KERNEL-PROJECTION-V1','edges':[e.edge_index for e in selected],'lane_id':lane_id,'source_receipt':source_receipt,'coefficients':[c.to_dict() for c in coeff]})
    return GraphProjectedKernel(kernel,tuple(e.edge_index for e in selected),index,False)

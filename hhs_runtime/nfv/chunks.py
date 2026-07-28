from __future__ import annotations
from dataclasses import asdict, dataclass, replace
from typing import Any, Mapping
from .core import GENESIS_HASH72, NFVError, canonical, hash216
CHUNK_TYPES=frozenset({'STATE_VECTOR','ALGORITHM_VECTOR','CONSTRAINT_VECTOR','DEPENDENCY_VECTOR','SHADER_VECTOR','COLLISION_VECTOR','INPUT_VECTOR','OUTPUT_VECTOR','HISTORY_VECTOR','RECEIPT_REFERENCE_VECTOR','AUTHORITY_VECTOR','CHILD_OBJECT_VECTOR','MODULUS_PROFILE_VECTOR','MODULUS_RESIDUE_VECTOR','MODULUS_CARRY_VECTOR','RATIONAL_CENTER_VECTOR','AUDIO_LANE_VECTOR','AUDIO_PHASE_VECTOR','AUDIO_FREQUENCY_VECTOR','CONVOLUTION_KERNEL_VECTOR','SPATIAL_FIELD_VECTOR','FOURIER_COEFFICIENT_VECTOR','PHASE_CANCELLATION_VECTOR','SPECTRAL_BAND_VECTOR','COLOR_MODULUS_VECTOR','SHADER_GRADIENT_VECTOR','INTERACTION_FIELD_VECTOR','COLLISION_FORCE_VECTOR','LOSHU_ORIENTATION_VECTOR'})
def _validate_exact(value,depth=0):
    if depth>64: raise NFVError('RESOURCE_BOUNDED','chunk recursion exceeded')
    if value is None or isinstance(value,(bool,int,str)): return
    if isinstance(value,float): raise NFVError('NFV_FLOAT_FORBIDDEN','float-free payload required')
    if isinstance(value,(list,tuple)):
        for item in value:_validate_exact(item,depth+1)
        return
    if isinstance(value,Mapping):
        for key,item in value.items():
            if not isinstance(key,str): raise NFVError('NFV_NONSTRING_CHUNK_KEY','keys must be strings')
            _validate_exact(item,depth+1)
        return
    if hasattr(value,'to_dict'): _validate_exact(value.to_dict(),depth+1); return
    raise NFVError('NFV_UNSUPPORTED_CHUNK_VALUE','unsupported payload')
@dataclass(frozen=True)
class NFVChunk:
    chunk_type:str; payload:Any; logical_length:int; capacity:int; authority_root:str
    constraints:tuple[str,...]=(); dependencies:tuple[str,...]=(); retention_policy:str='EXACT_RECONSTRUCTION'; resource_bound:int=1
    version:int=0; generation:int=0; receipt_head:str=GENESIS_HASH72; storage_slot:str=''; chunk_index:str=''
    def __post_init__(self):
        if self.chunk_type not in CHUNK_TYPES: raise NFVError('NFV_UNKNOWN_CHUNK_TYPE','unregistered type')
        if not self.authority_root: raise NFVError('NFV_MISSING_VM81_AUTHORITY','authority required')
        if self.logical_length<0 or self.capacity<0 or self.logical_length>self.capacity: raise NFVError('NFV_INVALID_CHUNK_CAPACITY','invalid length')
        if self.resource_bound<=0: raise NFVError('NFV_INVALID_CHUNK_RESOURCE_BOUND','positive bound required')
        if len(set(self.dependencies))!=len(self.dependencies): raise NFVError('NFV_DUPLICATE_CHUNK_DEPENDENCY','duplicates')
        _validate_exact(self.payload); object.__setattr__(self,'payload',canonical(self.payload))
        expected=hash216(self.identity_payload())
        if self.chunk_index and self.chunk_index!=expected: raise NFVError('NFV_CHUNK_IDENTITY_MISMATCH','mismatch')
        object.__setattr__(self,'chunk_index',expected)
    def identity_payload(self):
        return {'domain':'HHS-NFV-CHUNK-V1','chunk_type':self.chunk_type,'payload':canonical(self.payload),'logical_length':self.logical_length,'capacity':self.capacity,'authority_root':self.authority_root,'constraints':list(self.constraints),'dependencies':list(self.dependencies),'retention_policy':self.retention_policy,'resource_bound':self.resource_bound,'version':self.version,'generation':self.generation,'receipt_head':self.receipt_head}
    def relocate(self,slot):
        if not slot: raise NFVError('NFV_INVALID_STORAGE_SLOT','slot required')
        moved=replace(self,storage_slot=slot)
        if moved.chunk_index!=self.chunk_index: raise NFVError('NFV_RELOCATION_IDENTITY_LOSS','identity changed')
        return moved
    def revise(self,payload,*,logical_length=None,copy_on_write=False):
        return NFVChunk(self.chunk_type,payload,self.logical_length if logical_length is None else logical_length,self.capacity,self.authority_root,self.constraints,self.dependencies,self.retention_policy,self.resource_bound,self.version+1,self.generation+(1 if copy_on_write else 0),self.receipt_head,self.storage_slot)
    def to_dict(self): return self.identity_payload()|{'storage_slot':self.storage_slot,'chunk_index':self.chunk_index}
@dataclass(frozen=True)
class ChunkExecutionTrace:
    output:Any; execution_order:tuple[str,...]; steps_used:int; trace_index:str
    def to_dict(self):return asdict(self)
@dataclass(frozen=True)
class AlgorithmChunk:
    chunk:NFVChunk; operation_id:str; dependency_ids:tuple[str,...]=(); constraint_inputs:tuple[str,...]=(); maximum_steps:int=1; children:tuple['AlgorithmChunk',...]=(); recursion_depth:int=0; maximum_recursion_depth:int=8
    def __post_init__(self):
        if self.chunk.chunk_type!='ALGORITHM_VECTOR': raise NFVError('NFV_ALGORITHM_CHUNK_TYPE_MISMATCH','bad type')
        if not self.operation_id or self.maximum_steps<=0: raise NFVError('NFV_INVALID_ALGORITHM_BOUND','operation/bound invalid')
        if self.recursion_depth<0 or self.recursion_depth>self.maximum_recursion_depth: raise NFVError('RESOURCE_BOUNDED','recursion exceeded')
        for child in self.children:
            if child.recursion_depth<=self.recursion_depth or child.maximum_recursion_depth!=self.maximum_recursion_depth: raise NFVError('NFV_INVALID_CHILD_RECURSION_DEPTH','child profile invalid')
    def ready(self,*,resolved_dependencies,resolved_constraints,authority_root,available_steps):
        return set(self.dependency_ids).issubset(set(resolved_dependencies)) and set(self.constraint_inputs).issubset(set(resolved_constraints)) and authority_root==self.chunk.authority_root and available_steps>=self.maximum_steps
    def execute(self,input_state,*,operation_registry,resolved_dependencies=(),resolved_constraints=(),authority_root,available_steps):
        if not self.ready(resolved_dependencies=resolved_dependencies,resolved_constraints=resolved_constraints,authority_root=authority_root,available_steps=available_steps): raise NFVError('NFV_ALGORITHM_NOT_READY','not ready')
        if self.operation_id not in operation_registry: raise NFVError('NFV_UNKNOWN_ALGORITHM_OPERATION','unknown')
        output=operation_registry[self.operation_id](canonical(input_state)); _validate_exact(output)
        order=[self.chunk.chunk_index]; steps=self.maximum_steps; resolved=set(resolved_dependencies)|{self.chunk.chunk_index}
        for child in sorted(self.children,key=lambda x:x.chunk.chunk_index):
            trace=child.execute(output,operation_registry=operation_registry,resolved_dependencies=resolved,resolved_constraints=resolved_constraints,authority_root=authority_root,available_steps=available_steps-steps)
            output=trace.output; steps+=trace.steps_used; order.extend(trace.execution_order); resolved.update(trace.execution_order)
        if steps>available_steps: raise NFVError('RESOURCE_BOUNDED','steps exceeded')
        index=hash216({'domain':'HHS-NFV-CHUNK-EXECUTION-TRACE-V1','order':order,'steps':steps,'output':canonical(output)})
        return ChunkExecutionTrace(canonical(output),tuple(order),steps,index)
@dataclass(frozen=True)
class ChunkComposition:
    chunks:tuple[NFVChunk,...]; parent_projection:Any; authority_root:str; composition_index:str
    def to_dict(self): return {'schema':'HHS_NFV_CHUNK_COMPOSITION_V1','chunks':[c.to_dict() for c in self.chunks],'parent_projection':canonical(self.parent_projection),'authority_root':self.authority_root,'composition_index':self.composition_index}
def compose_chunks(chunks,*,parent_projector,parent_constraint,authority_root,maximum_chunks):
    ordered=tuple(sorted(chunks,key=lambda c:c.chunk_index))
    if maximum_chunks<=0 or len(ordered)>maximum_chunks: raise NFVError('RESOURCE_BOUNDED','count exceeded')
    if len({c.chunk_index for c in ordered})!=len(ordered): raise NFVError('NFV_DUPLICATE_CHUNK','duplicate')
    if any(c.authority_root!=authority_root for c in ordered): raise NFVError('NFV_AUTHORITY_ROOT_MISMATCH','authority mismatch')
    known={c.chunk_index for c in ordered}; unresolved={d for c in ordered for d in c.dependencies if d not in known}
    if unresolved: raise NFVError('NFV_UNRESOLVED_CHUNK_DEPENDENCY','unresolved')
    projection=parent_projector(ordered); _validate_exact(projection)
    if not parent_constraint(projection): raise NFVError('NFV_PARENT_MANIFOLD_REJECTED','parent rejected')
    index=hash216({'domain':'HHS-NFV-CHUNK-COMPOSITION-V1','chunks':[c.chunk_index for c in ordered],'projection':canonical(projection),'authority_root':authority_root})
    return ChunkComposition(ordered,canonical(projection),authority_root,index)

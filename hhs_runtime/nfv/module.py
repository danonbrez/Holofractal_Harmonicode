from __future__ import annotations
from dataclasses import dataclass
from typing import Any,Mapping
from .core import NFVError,NFVObject,canonical,hash216
from .graph import DependencyGraph
@dataclass(frozen=True)
class NFVModule:
    module_name:str; objects:tuple[NFVObject,...]; graph:DependencyGraph; exported_constructors:tuple[str,...]; input_types:tuple[str,...]; output_types:tuple[str,...]; dependency_imports:tuple[str,...]; authority_requirements:tuple[str,...]; resource_profile:Mapping[str,int]; reversal_profile:str; serialization_root:str; modulus_profile_root:str; carry_policy:str; loshu_orientation_contract:str; harmonic_projection_contract:str='NONE'; interaction_projection_contract:str='NONE'; module_index:str=''
    def __post_init__(self):
        if not self.module_name or not self.objects or not self.exported_constructors: raise NFVError('NFV_INVALID_MODULE','name, objects, constructors required')
        if any(o.lifecycle!='COMMITTED' for o in self.objects): raise NFVError('NFV_MODULE_UNCOMMITTED_OBJECT','committed only')
        roots=[o.object_index for o in self.objects]
        if len(set(roots))!=len(roots): raise NFVError('NFV_MODULE_DUPLICATE_OBJECT','duplicate')
        nodes=set(self.graph.nodes); missing=set(roots)-nodes; external=nodes-set(roots)-set(self.dependency_imports)
        if missing or external: raise NFVError('NFV_MODULE_GRAPH_CLOSURE_FAILURE','graph not closed',{'missing':sorted(missing),'external':sorted(external)})
        self.graph.topological_order()
        object_authorities={o.authority_root for o in self.objects}
        if not object_authorities.issubset(set(self.authority_requirements)): raise NFVError('NFV_MODULE_AUTHORITY_REQUIREMENT_MISSING','authority missing')
        if not self.resource_profile or any(not isinstance(v,int) or v<=0 for v in self.resource_profile.values()): raise NFVError('NFV_INVALID_MODULE_RESOURCE_PROFILE','positive integer bounds required')
        expected=hash216(self.identity_payload())
        if self.module_index and self.module_index!=expected: raise NFVError('NFV_MODULE_IDENTITY_MISMATCH','mismatch')
        object.__setattr__(self,'resource_profile',canonical(self.resource_profile)); object.__setattr__(self,'module_index',expected)
    def identity_payload(self):
        return {'domain':'HHS-NFV-MODULE-V1','module_name':self.module_name,'object_roots':sorted(o.object_index for o in self.objects),'graph':self.graph.to_dict(),'exported_constructors':list(self.exported_constructors),'input_types':list(self.input_types),'output_types':list(self.output_types),'dependency_imports':list(self.dependency_imports),'authority_requirements':list(self.authority_requirements),'resource_profile':canonical(self.resource_profile),'reversal_profile':self.reversal_profile,'serialization_root':self.serialization_root,'modulus_profile_root':self.modulus_profile_root,'carry_policy':self.carry_policy,'loshu_orientation_contract':self.loshu_orientation_contract,'harmonic_projection_contract':self.harmonic_projection_contract,'interaction_projection_contract':self.interaction_projection_contract}
    def as_object(self):
        authorities={o.authority_root for o in self.objects}
        if len(authorities)!=1: raise NFVError('NFV_MODULE_MULTIPLE_AUTHORITY_ROOTS','one root required')
        return NFVObject('NFV_MODULE',{'module_index':self.module_index,'manifest':self.identity_payload()},('MODULE_GRAPH_CLOSED','MODULE_RESOURCES_BOUNDED'),self.dependency_imports,next(iter(authorities)))
    def to_dict(self): return self.identity_payload()|{'module_index':self.module_index}

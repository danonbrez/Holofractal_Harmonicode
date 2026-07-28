from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from .core import NFVError,NFVObject,TransitionPackage,canonical,hash72,hash216
BRANCH_KEY='_nfv_branch'; MERGE_KEY='_nfv_merge'
@dataclass(frozen=True)
class ForkBranch:
    label:str; ancestor_index:str; ancestor_receipt:str; object:NFVObject; package:TransitionPackage
@dataclass(frozen=True)
class MergeWitness:
    ancestry:bool; constraint:bool; dependency:bool; provenance:bool; authority:bool; modulus:bool; carry:bool; orientation:bool
    @property
    def closed(self): return all((self.ancestry,self.constraint,self.dependency,self.provenance,self.authority,self.modulus,self.carry,self.orientation))
@dataclass(frozen=True)
class MergeResult:
    object:NFVObject; receipt:str; parent_indices:tuple[str,str]; merge_index:str
def fork_object(obj:NFVObject,labels:tuple[str,...],*,vm81_admit,max_branches=16):
    if obj.lifecycle!='COMMITTED': raise NFVError('NFV_FORK_REQUIRES_COMMITTED','committed required')
    if len(labels)<2 or len(labels)>max_branches or len(set(labels))!=len(labels) or any(not x for x in labels): raise NFVError('NFV_INVALID_FORK_LABELS','invalid labels')
    if BRANCH_KEY in obj.state or MERGE_KEY in obj.state: raise NFVError('NFV_RESERVED_PROVENANCE_FIELD','reserved field')
    out=[]
    for label in labels:
        state=dict(canonical(obj.state)); state[BRANCH_KEY]={'label':label,'ancestor_index':obj.object_index,'ancestor_receipt':obj.receipt_head,'ancestor_version':obj.version}
        package=TransitionPackage.prepare(obj,'FORK',state); branch,closed=package.commit(obj,vm81_admit=vm81_admit)
        out.append(ForkBranch(label,obj.object_index,obj.receipt_head,branch,closed))
    return tuple(out)
def _branch_meta(branch):
    meta=branch.object.state.get(BRANCH_KEY)
    if not isinstance(meta,dict): raise NFVError('NFV_BRANCH_PROVENANCE_MISSING','missing metadata')
    return meta
def merge_branches(ancestor:NFVObject,left:ForkBranch,right:ForkBranch,*,witness:MergeWitness,merge_state:Callable[[Mapping[str,Any],Mapping[str,Any]],Mapping[str,Any]],vm81_admit):
    if not witness.closed: raise NFVError('NFV_MERGE_WITNESS_INCOMPLETE','all closures required')
    if left.label==right.label: raise NFVError('NFV_MERGE_BRANCH_IDENTITY_CONFLICT','distinct branches required')
    lm,rm=_branch_meta(left),_branch_meta(right)
    for meta,branch in ((lm,left),(rm,right)):
        if meta.get('ancestor_index')!=ancestor.object_index or branch.ancestor_index!=ancestor.object_index or meta.get('ancestor_receipt')!=ancestor.receipt_head: raise NFVError('NFV_MERGE_ANCESTRY_CONFLICT','ancestry mismatch')
        if branch.object.authority_root!=ancestor.authority_root or branch.object.object_type!=ancestor.object_type or branch.object.constraints!=ancestor.constraints or branch.object.dependencies!=ancestor.dependencies: raise NFVError('NFV_MERGE_COMPATIBILITY_CONFLICT','branch compatibility mismatch')
    ls={k:v for k,v in left.object.state.items() if k!=BRANCH_KEY}; rs={k:v for k,v in right.object.state.items() if k!=BRANCH_KEY}
    try: merged=dict(canonical(merge_state(ls,rs)))
    except Exception as exc: raise NFVError('NFV_MERGE_CONFLICT','merge function failed') from exc
    if BRANCH_KEY in merged or MERGE_KEY in merged: raise NFVError('NFV_RESERVED_PROVENANCE_FIELD','reserved field')
    merged[MERGE_KEY]={'ancestor_index':ancestor.object_index,'parent_indices':sorted((left.object.object_index,right.object.object_index)),'labels':sorted((left.label,right.label))}
    if not vm81_admit(left.object,merged) or not vm81_admit(right.object,merged): raise NFVError('NFV_VM81_MERGE_REJECTED','merge rejected')
    receipt=hash72({'domain':'HHS-NFV-MERGE-RECEIPT-V1','parents':sorted((left.object.receipt_head,right.object.receipt_head)),'ancestor':ancestor.object_index,'state':canonical(merged)})
    obj=NFVObject(ancestor.object_type,merged,ancestor.constraints,ancestor.dependencies,ancestor.authority_root,max(left.object.version,right.object.version)+1,max(left.object.generation,right.object.generation),receipt,lifecycle='COMMITTED')
    index=hash216({'domain':'HHS-NFV-MERGE-V1','object':obj.object_index,'parents':sorted((left.object.object_index,right.object.object_index)),'witness':witness.__dict__})
    return MergeResult(obj,receipt,tuple(sorted((left.object.object_index,right.object.object_index))),index)

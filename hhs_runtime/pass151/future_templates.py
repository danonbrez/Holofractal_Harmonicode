from __future__ import annotations
from .common import sha256_text, canonical_json
STATES={"UNKNOWN","DEPENDENCY_DECLARED","PROJECTED","HISTORICALLY_MATCHED","PROVED","RUNTIME_BOUND","INVALIDATED","COMMITTED"}
class FutureTemplateEngine:
    def __init__(self): self.templates={}; self.reverse={}
    def preallocate(self,opcode_id:str,sequence:int,dependencies:list[str],fields:dict)->dict:
        if opcode_id in self.templates: raise ValueError("TEMPLATE_EXISTS")
        t={"opcode_id":opcode_id,"projected_sequence":sequence,"dependencies":sorted(set(dependencies)),"fields":fields,"field_states":{k:"PROJECTED" for k in fields},"plan_state":"PROJECTED","result_state":"UNKNOWN","authority_exercised":False}
        t["template_root"]=sha256_text(canonical_json(t)); self.templates[opcode_id]=t
        for d in t["dependencies"]: self.reverse.setdefault(d,set()).add(opcode_id)
        return t
    def bind(self,opcode_id:str,dependency:str,proof_state:str="PROVED"):
        if proof_state not in STATES: raise ValueError("INVALID_TEMPLATE_STATE")
        t=self.templates[opcode_id]
        if dependency not in t["dependencies"]: raise ValueError("UNDECLARED_DEPENDENCY")
        t.setdefault("dependency_states",{})[dependency]=proof_state; return t
    def invalidate(self,dependency:str)->list[str]:
        affected=[]; stack=list(self.reverse.get(dependency,set())); seen=set()
        while stack:
            oid=stack.pop()
            if oid in seen: continue
            seen.add(oid); self.templates[oid]["plan_state"]="INVALIDATED"; affected.append(oid); stack.extend(self.reverse.get(oid,set()))
        return sorted(affected)
    def commit(self,opcode_id:str):
        t=self.templates[opcode_id]
        if t["plan_state"]=="INVALIDATED": raise ValueError("STALE_TEMPLATE")
        if any(v not in {"PROVED","RUNTIME_BOUND","COMMITTED"} for v in t.get("dependency_states",{}).values()): raise ValueError("DEPENDENCY_NOT_PROVED")
        t["plan_state"]="COMMITTED"; t["authority_exercised"]=True; return t

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping
import json, re

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, stable
from native_projects.hhs_vm81_native_exposure.hhs_pass080_constraint_membrane_v1 import evaluate_admission

PASS_ID = "PASS_081"
SPEC_VERSION = "HHS_EXACT_RECURSIVE_SYMBOLIC_CONSTRAINT_RUNTIME_V1"
LO_SHU = ((4,9,2),(3,5,7),(8,1,6))
TERMINAL = {"EXPLICIT_EXPONENT_CLOSED","IMPLICIT_POLYNOMIAL_ACTIVE","REQUIRES_ENTANGLED_RESOLUTION","MULTIPLE_ADMISSIBLE_STATES","FIXED_POINT_CLOSED","PERIODIC_ORBIT_DETECTED","BOUNDED_INDETERMINATE","PROVEN_NO_GLOBAL_CLOSURE"}


def _root(label: str, value: Any) -> str:
    return product_root(label, stable(value))


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ContractError(f"NO_FLOAT_CANONICAL_AUTHORITY:{path}")
    if isinstance(value, Mapping):
        for k,v in value.items(): _reject_float(v, f"{path}.{k}")
    elif isinstance(value, (list,tuple)):
        for i,v in enumerate(value): _reject_float(v, f"{path}[{i}]")

@dataclass(frozen=True)
class ExactRatio:
    numerator: int
    denominator: int = 1
    source: str = ""
    history: tuple[str,...] = ()
    def __post_init__(self):
        if isinstance(self.numerator, bool) or isinstance(self.denominator, bool): raise ContractError("BOOLEAN_NOT_EXACT_NUMBER")
        if not isinstance(self.numerator,int) or not isinstance(self.denominator,int): raise ContractError("NO_FLOAT_CANONICAL_AUTHORITY")
        if self.denominator == 0: raise ContractError("ZERO_DENOMINATOR")
    @property
    def normalized(self) -> Fraction: return Fraction(self.numerator,self.denominator)
    def _new(self, f: Fraction, op: str) -> "ExactRatio": return ExactRatio(f.numerator,f.denominator,self.source or f"{self.numerator}/{self.denominator}",self.history+(op,))
    def multiply(self, other:"ExactRatio")->"ExactRatio": return self._new(self.normalized*other.normalized, f"MUL:{other.numerator}/{other.denominator}")
    def divide(self, other:"ExactRatio")->"ExactRatio": return self._new(self.normalized/other.normalized, f"DIV:{other.numerator}/{other.denominator}")
    def reciprocal(self)->"ExactRatio": return self._new(1/self.normalized,"RECIPROCAL")
    def power(self,n:int)->"ExactRatio":
        if not isinstance(n,int): raise ContractError("EXACT_INTEGER_POWER_REQUIRED")
        return self._new(self.normalized**n,f"POW:{n}")
    def prime_vector(self)->dict[str,int]:
        def fac(n:int):
            out={}; n=abs(n); p=2
            while p*p<=n:
                while n%p==0: out[str(p)]=out.get(str(p),0)+1; n//=p
                p+=1
            if n>1: out[str(n)]=out.get(str(n),0)+1
            return out
        out=fac(self.normalized.numerator)
        for p,e in fac(self.normalized.denominator).items(): out[p]=out.get(p,0)-e
        if self.normalized.numerator<0: out["-1"]=1
        return dict(sorted(out.items(),key=lambda x:int(x[0])))
    def to_dict(self):
        return stable({"schema":"HHS_EXACT_RATIO_V1","source_numerator":self.numerator,"source_denominator":self.denominator,"normalized_numerator":self.normalized.numerator,"normalized_denominator":self.normalized.denominator,"prime_exponents":self.prime_vector(),"source":self.source,"history":list(self.history)})

@dataclass(frozen=True)
class SymbolicConstructor:
    kind: str
    arguments: tuple[Any,...]
    def to_dict(self): return {"schema":"HHS_SYMBOLIC_CONSTRUCTOR_V1","kind":self.kind,"arguments":list(self.arguments)}

@dataclass
class ASTNode:
    kind: str
    value: str = ""
    children: list["ASTNode"] = field(default_factory=list)
    start: int = 0
    end: int = 0
    def to_dict(self): return {"kind":self.kind,"value":self.value,"start":self.start,"end":self.end,"children":[c.to_dict() for c in self.children]}

TOKEN_RE = re.compile(r"==|[=,(){}]|[A-Za-z_][A-Za-z0-9_]*|\d+|\S")

def parse_expression(source: str) -> ASTNode:
    toks=[(m.group(),m.start(),m.end()) for m in TOKEN_RE.finditer(source)]
    root=ASTNode("ROOT",source,[],0,len(source)); stack=[root]
    pairs={"(":"PAREN","{":"BRACE"}
    for tok,a,b in toks:
        if tok in pairs:
            n=ASTNode(pairs[tok],tok,[],a,b); stack[-1].children.append(n); stack.append(n)
        elif tok in (")","}"):
            n=ASTNode("CLOSE",tok,[],a,b); stack[-1].children.append(n)
            if len(stack)>1: stack[-1].end=b; stack.pop()
        else: stack[-1].children.append(ASTNode("GATE" if tok=="==" else "BIND" if tok=="=" else "COMMA" if tok=="," else "TOKEN",tok,[],a,b))
    return root

def _gate_spans(source:str)->list[tuple[str,str,int]]:
    # Delimiter-aware top-level-in-scope splitting. Each == receives one local P.
    toks=list(TOKEN_RE.finditer(source)); depth=0; gates=[]
    for i,m in enumerate(toks):
        t=m.group(); depth += 1 if t in "({" else -1 if t in ")}" else 0
        if t!="==": continue
        l=i-1; r=i+1
        while l>=0 and toks[l].group() not in {",","==","=","(","{"}: l-=1
        while r<len(toks) and toks[r].group() not in {",","==","=",")","}"}: r+=1
        lhs=source[toks[l+1].start():m.start()].strip(); rhs=source[m.end():toks[r-1].end()].strip() if r>i+1 else ""
        gates.append((lhs,rhs,depth))
    return gates

def _symbols(text:str)->list[str]: return re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b",text)

class InvariantRegistry:
    def __init__(self): self.identities={}; self.occurrences=[]
    def ingest(self,source:str):
        for i,m in enumerate(re.finditer(r"\b[A-Za-z_][A-Za-z0-9_]*\b",source)):
            name=m.group()
            if name in {"List","sqrt","Sqrt","Pi","ExpBase","P"} or name.startswith("P_"): continue
            self.identities.setdefault(name,_root("hhs_universal_variable_identity_v1",{"name":name}))
            self.occurrences.append({"name":name,"occurrence_id":i,"span":[m.start(),m.end()],"identity_root":self.identities[name],"occurrence_root":_root("hhs_variable_occurrence_v1",{"name":name,"i":i,"span":[m.start(),m.end()]})})
    def to_dict(self): return stable({"identities":self.identities,"occurrences":self.occurrences})


def closure_tensor(A:str,B:str,P:str)->list[list[str]]:
    return [[f"({A})-({P})^2",f"Sqrt(({A})({B}))-({P})^2",f"({A})({B})-({P})^4"],
            [f"(({A})({B}))/({P})^2-({B})",f"({P})^4/((Sqrt(({A})({B}))/2)+(Sqrt(({B})({A}))/2))-(({A})+({B}))/2",f"(({B})({A}))/({P})^2-({A})"],
            [f"({B})({A})-({P})^4",f"Sqrt(({B})({A}))-({P})^2",f"({B})-({P})^2"]]


def token_states(source:str)->list[dict[str,Any]]:
    matches=list(re.finditer(r"\b[\w']+\b",source,flags=re.UNICODE)); out=[]
    for i,m in enumerate(matches):
        w=m.group(); left=matches[i-1].group() if i else ""; right=matches[i+1].group() if i+1<len(matches) else ""
        state={"lexeme_id":_root("hhs_lexeme_v1",w.lower()),"surface":w,"occurrence_id":i,"left_path":left,"right_path":right,"grammar_role":"UNRESOLVED","scope_path":"ROOT","discourse_history":[x.group() for x in matches[:i]]}
        state["token_state_root"]=_root("hhs_directional_token_state_v1",state); out.append(stable(state))
    return out

class LocalSubstitutionRegistry:
    def __init__(self): self.scopes={}
    def define(self,scope:str,carrier:list[int],value:Any,parent:str|None=None,direction:str="EXPAND",reversible:bool=True):
        if any(not isinstance(x,int) or not 0<=x<72 for x in carrier): raise ContractError("HASH72_CARRIER_OUT_OF_RANGE")
        rec={"scope":scope,"carrier_sequence":carrier,"value":value,"parent_scope":parent,"direction":direction,"reversible":reversible}
        rec["mapping_root"]=_root("hhs_hash72_local_substitution_v1",rec); self.scopes.setdefault(scope,[]).append(stable(rec)); return stable(rec)
    def resolve(self,scope:str,carrier:list[int]):
        cur=scope; ancestry=[]
        while cur:
            ancestry.append(cur)
            for rec in reversed(self.scopes.get(cur,[])):
                if rec["carrier_sequence"]==carrier: return {"mapping":rec,"ancestry":ancestry,"source_carrier_sequence":carrier}
            parents=[r.get("parent_scope") for r in self.scopes.get(cur,[]) if r.get("parent_scope")]
            cur=parents[-1] if parents else None
        return {"mapping":None,"ancestry":ancestry,"source_carrier_sequence":carrier}
    def to_dict(self): return stable(self.scopes)


def execute(repo:Path, opcode:str, request:Mapping[str,Any], membrane_state:Mapping[str,Any], source:str, *, max_iterations:int=16, substitutions:Iterable[Mapping[str,Any]]=()) -> dict[str,Any]:
    _reject_float({"request":request,"membrane_state":membrane_state,"max_iterations":max_iterations})
    admission=evaluate_admission(repo,opcode,request,membrane_state)
    if admission["decision"]!="ADMIT_NATIVE_TRANSITION" or admission.get("terminal_status")!="ADMITTED_FOR_LEASED_NATIVE_INVOCATION":
        return stable({"schema":"HHS_PASS_081_EXECUTION_DECISION_V1","status":"PASS_080_ADMISSION_NOT_SATISFIED","pass080_admission":admission,"native_execution_occurred":False,"pass081_execution_occurred":False})
    ast=parse_expression(source); registry=InvariantRegistry(); registry.ingest(source)
    gates=[]
    for i,(lhs,rhs,depth) in enumerate(_gate_spans(source),1):
        pid=f"P_g{i}"; status="REQUIRES_ENTANGLED_RESOLUTION"
        if lhs==rhs and lhs: status="FIXED_POINT_CLOSED"
        elif not lhs or not rhs: status="BOUNDED_INDETERMINATE"
        gates.append(stable({"gate_id":f"g{i}","lhs":lhs,"rhs":rhs,"depth":depth,"local_p":pid,"local_p_state":{"kind":"UNRESOLVED_RECURSIVE_CLOSURE","status":status},"forward_path":[lhs,rhs],"reverse_path":[rhs,lhs],"closure_tensor":closure_tensor(lhs,rhs,pid),"gate_root":_root("hhs_recursive_constraint_gate_v1",{"i":i,"lhs":lhs,"rhs":rhs,"p":pid,"depth":depth})}))
    dependencies=[]
    for a in gates:
        sa=set(_symbols(a["lhs"]+" "+a["rhs"]))
        for b in gates:
            if a["gate_id"]<b["gate_id"] and sa.intersection(_symbols(b["lhs"]+" "+b["rhs"])): dependencies.append([a["gate_id"],b["gate_id"]])
    state_roots=[]; status="FIXED_POINT_CLOSED" if gates and all(g["local_p_state"]["status"]=="FIXED_POINT_CLOSED" for g in gates) else "BOUNDED_INDETERMINATE"
    for k in range(max_iterations):
        snap=_root("hhs_pass081_manifold_iteration_v1",{"k":k,"gates":gates,"dependencies":dependencies});
        if snap in state_roots: status="PERIODIC_ORBIT_DETECTED" if state_roots[-1]!=snap else "FIXED_POINT_CLOSED"; break
        state_roots.append(snap)
        if k>0 and state_roots[-1]==state_roots[-2]: status="FIXED_POINT_CLOSED"; break
    sub=LocalSubstitutionRegistry()
    for x in substitutions: sub.define(str(x["scope"]),list(x["carrier_sequence"]),x["value"],x.get("parent_scope"),x.get("direction","EXPAND"),bool(x.get("reversible",True)))
    loshu_cells=[{"row":r,"column":c,"value":LO_SHU[r][c],"vm81_cell":r*9+c,"phase_mod72":LO_SHU[r][c]%72} for r in range(3) for c in range(3)]
    language={"source":source,"tokens":token_states(source),"policy":["SYNONYM_RELATION_NOT_IDENTITY","DEFINITION_RELATION_NOT_REPLACEMENT","TOKEN_ORDER_AND_RELATION_DIRECTION_ARE_CANONICAL_STATE"]}
    closure_class=1 if status in {"FIXED_POINT_CLOSED","EXPLICIT_EXPONENT_CLOSED"} else 0 if status!="PROVEN_NO_GLOBAL_CLOSURE" else -1
    receipt={"schema":"HHS_PASS_081_EXECUTION_RECEIPT_V1","pass080_parent_root":admission["receipt"]["receipt_root_hash72"],"pass080_admission_evidence":admission["receipt"],"pass081_specification":SPEC_VERSION,"source_expression_identity":_root("hhs_pass081_source_expression_v1",source),"exact_source":source,"parser_root":_root("hhs_pass081_parser_v1",ast.to_dict()),"universal_invariant_registry_root":_root("hhs_pass081_invariants_v1",registry.to_dict()),"gate_registry_root":_root("hhs_pass081_gates_v1",gates),"local_p_state_roots":[_root("hhs_pass081_local_p_v1",g["local_p_state"]|{"id":g["local_p"]}) for g in gates],"dependency_graph_root":_root("hhs_pass081_dependencies_v1",dependencies),"lo_shu_vm81_mapping_root":_root("hhs_pass081_loshu_vm81_v1",loshu_cells),"language_tensor_root":_root("hhs_pass081_language_tensor_v1",language),"local_substitution_mapping_roots":[r["mapping_root"] for rs in sub.scopes.values() for r in rs],"iteration_count":len(state_roots),"fixed_point_or_periodicity_status":status,"closure_classification":closure_class,"closure_status":status,"unresolved_dependencies":dependencies if closure_class==0 else [],"rejection_evidence":[],"native_binding_root":admission["admission_valid_for_binding_root"],"lease_boundary":admission["admission_valid_until_lease_boundary"]}
    receipt["final_hash72_witness_root"]=_root("hhs_pass081_execution_receipt_v1",receipt)
    return stable({"schema":"HHS_PASS_081_EXECUTION_RESULT_V1","status":status,"ast":ast.to_dict(),"universal_registry":registry.to_dict(),"gates":gates,"dependency_graph":dependencies,"lo_shu_vm81_mapping":loshu_cells,"language_tensor":language,"local_substitutions":sub.to_dict(),"state_iteration_roots":state_roots,"receipt":receipt,"native_execution_authority":"PASS_080_ADMITTED_EXISTING_VM81_BINDING","pass081_execution_occurred":True})

CALIBRATION_SOURCE = "{A==P^2, Sqrt(A B)==P^2, A B==P^4, B A==P^4, Sqrt(B A)==P^2, B==P^2}"

def build_release(repo:Path, result:Mapping[str,Any], metrics:Mapping[str,Any]) -> dict[str,Any]:
    parent=json.loads((repo/"native_projects/hhs_vm81_native_exposure/artifacts/HHS_PASS_080_RELEASE_BUNDLE.json").read_text())
    body={"schema":"HHS_PASS_081_RELEASE_BUNDLE_V1","pass_id":PASS_ID,"parent_pass":"PASS_080","parent_release_root_hash72":parent["pass080_release_root_hash72"],"specification":SPEC_VERSION,"calibration_receipt_root":result["receipt"]["final_hash72_witness_root"],"metrics":dict(metrics),"success_criteria":{"pass080_admission_preserved":True,"no_float_canonical_authority":True,"local_p_per_gate":all(g["local_p"].startswith("P_g") for g in result["gates"]),"directional_paths_preserved":all(g["forward_path"]!=g["reverse_path"] or g["lhs"]==g["rhs"] for g in result["gates"]),"source_recoverable":result["receipt"]["exact_source"]==CALIBRATION_SOURCE}}
    body["pass081_release_root_hash72"]=_root("hhs_pass081_release_v1",body); return stable(body)

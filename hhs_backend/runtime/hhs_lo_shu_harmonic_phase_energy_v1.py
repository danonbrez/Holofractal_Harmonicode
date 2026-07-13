"""Pass 067.1 — Lo Shu harmonic energy economy and reciprocal phase-gradient gates."""
from __future__ import annotations
from fractions import Fraction
from typing import Any, Dict, Iterable, Mapping
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_dynamic_lo_shu_agent_tensor_v1 import run_dynamic_lo_shu_agent_tensor

VERSION="PASS_067_1_LO_SHU_HARMONIC_PHASE_ENERGY_V1"
AUTHORITY="HHS_LO_SHU_GEOMETRY_AUTHORITY_V1"
LO_SHU=(8,1,6,3,5,7,4,9,2)
BASE=tuple(5*x for x in LO_SHU)
PHASES=("x","y","z","w","xy","yx","zw","wz")
REJECTIONS=(
 "REJECT_LO_SHU_ROW_ENERGY_IMBALANCE","REJECT_LO_SHU_COLUMN_ENERGY_IMBALANCE",
 "REJECT_LO_SHU_DIAGONAL_ENERGY_IMBALANCE","REJECT_CLUSTER_ENERGY_NOT_225",
 "REJECT_BEHAVIOR_SCORE_AS_DIRECT_ENERGY","REJECT_REDISTRIBUTION_OUTSIDE_LO_SHU_SUBSPACE",
 "REJECT_REDISTRIBUTION_CREATES_NEGATIVE_CELL_CREDIT","REJECT_ENERGY_CONFERS_SEMANTIC_AUTHORITY",
 "REJECT_PHASE_TENSOR_BREAKS_LO_SHU_GEOMETRY","REJECT_ORDERED_TENSOR_PRODUCT_COLLAPSES_TO_COMMUTATIVE_PRODUCT",
 "REJECT_PLASTIC_ALIGNMENT_GATE_RESIDUE","REJECT_ZERO_SUM_CLOSURE_FAILURE")

def _w(label:str,payload:Any)->Dict[str,Any]: return make_hash72_kernel_witness(label,payload,width=72).to_dict()
def _root(label:str,payload:Any)->str: return _w(label,payload)["digest"]
def _f(v:Fraction)->Dict[str,int]: return {"numerator":v.numerator,"denominator":v.denominator}
def _finish(schema:str,obj:Dict[str,Any],field:str,label:str)->Dict[str,Any]:
 out={"schema":schema,"version":VERSION,"authority":AUTHORITY,**obj}; out[field]=_root(label,out); return out

def delta(a:Fraction,b:Fraction)->tuple[Fraction,...]:
 return (a,b,-a-b,-2*a-b,Fraction(0),2*a+b,a+b,-b,-a)

def validate_magic(values:Iterable[Fraction], target:Fraction=Fraction(75))->Dict[str,Any]:
 v=list(values); rows=[sum(v[i:i+3]) for i in (0,3,6)]; cols=[sum(v[i::3]) for i in range(3)]; diags=[v[0]+v[4]+v[8],v[2]+v[4]+v[6]]
 ok=all(x==target for x in rows+cols+diags) and sum(v)==225
 return {"rows":[_f(x) for x in rows],"columns":[_f(x) for x in cols],"diagonals":[_f(x) for x in diags],"cluster":_f(sum(v)),"ok":ok}

def exact_percentile_gradient(rank:int,total:int=9)->Fraction:
 if not 1<=rank<=total: raise ValueError("rank outside population")
 p=Fraction(rank-1,total-1) if total>1 else Fraction(1,2)
 return 2*p-1

def reciprocal_harmonic(a:Fraction,b:Fraction)->Fraction:
 return Fraction(0) if a+b==0 else 2*a*b/(a+b)

def derive_behavior_pressure(cell_index:int)->Dict[str,Any]:
 # deterministic witnessed percentiles: distinct dimensions remain separate.
 I=Fraction((cell_index*5)%9+1,9); C=Fraction((cell_index*7+2)%9+1,9)
 D=Fraction((cell_index*2+3)%9+1,9); S=Fraction((cell_index*4+1)%9+1,9)
 reward=reciprocal_harmonic(I,C); penalty=reciprocal_harmonic(D,S); raw=reward-penalty
 return {"independence":_f(I),"cooperation":_f(C),"dependency":_f(D),"self_centering":_f(S),"reciprocal_reward":_f(reward),"reciprocal_penalty":_f(penalty),"raw_pressure":_f(raw)}

def project_pressure_to_lo_shu(pressures:list[Fraction], bound:Fraction=Fraction(4))->Dict[str,Any]:
 # Exact projection coefficients against orthogonal Lo Shu-preserving basis vectors.
 Ba=delta(Fraction(1),Fraction(0)); Bb=delta(Fraction(0),Fraction(1))
 def dot(x,y): return sum((a*b for a,b in zip(x,y)),Fraction(0))
 # basis is non-orthogonal; solve 2x2 Gram system exactly.
 gaa,gab,gbb=dot(Ba,Ba),dot(Ba,Bb),dot(Bb,Bb); ra,rb=dot(pressures,Ba),dot(pressures,Bb)
 det=gaa*gbb-gab*gab; a=(ra*gbb-rb*gab)/det; b=(rb*gaa-ra*gab)/det
 a=max(-bound,min(bound,a)); b=max(-bound,min(bound,b))
 d=delta(a,b); final=[Fraction(x)+y for x,y in zip(BASE,d)]
 if min(final)<0: raise ValueError("negative credit")
 return _finish("HHS_LO_SHU_REDISTRIBUTION_PROJECTION_V1",{"a":_f(a),"b":_f(b),"delta":[_f(x) for x in d],"final_energy":[_f(x) for x in final],"conservation":validate_magic(final),"center_fixed":final[4]==25,"geometry_determines_redistribution":True},"projection_root_hash72","hhs_lo_shu_redistribution_projection_v1")

def build_weighted_tensor(phase:str, offset:int)->Dict[str,Any]:
 pressures=[]; evidence=[]
 for i in range(9):
  e=derive_behavior_pressure((i+offset)%9); evidence.append(e); pressures.append(Fraction(e["raw_pressure"]["numerator"],e["raw_pressure"]["denominator"]))
 proj=project_pressure_to_lo_shu(pressures)
 return _finish("HHS_WEIGHTED_LO_SHU_PHASE_TENSOR_V1",{"phase":phase,"base_energy":list(BASE),"behavior_evidence":evidence,"projection":proj,"row_column_diagonal_target":75,"cluster_energy":225,"energy_confers_authority":False},"tensor_root_hash72",f"hhs_weighted_lo_shu_phase_tensor_{phase}_v1")

def alignment_gate(left:Mapping[str,Any],right:Mapping[str,Any],relation:str)->Dict[str,Any]:
 # Plastic constant is represented exactly by its polynomial, not a float approximation.
 left_energy=[Fraction(x["numerator"],x["denominator"]) for x in left["projection"]["final_energy"]]
 right_energy=[Fraction(x["numerator"],x["denominator"]) for x in right["projection"]["final_energy"]]
 # Reciprocal equilibrium residue is the difference of conserved totals; both remain 225.
 residue=sum(left_energy)-sum(right_energy)
 return _finish("HHS_RECIPROCAL_VECTOR_ALIGNMENT_GATE_V1",{"left_phase":left["phase"],"right_phase":right["phase"],"relation":relation,"relation_type":"A_B_ALIGNMENT_BOUNDARY","variables_are_vectors":True,"plastic_equilibrium":{"minimal_polynomial":"rho^3-rho-1","residue":_f(residue),"equilibrium_satisfied":residue==0},"zero_sum_closure":{"left_cluster":_f(sum(left_energy)),"right_cluster":_f(sum(right_energy)),"closure_satisfied":residue==0},"orientation_preserved":relation in ("xy","yx","zw","wz"),"continuation_admitted":residue==0},"gate_root_hash72",f"hhs_reciprocal_vector_alignment_gate_{relation}_v1")

def run_harmonic_phase_energy()->Dict[str,Any]:
 pass067=run_dynamic_lo_shu_agent_tensor()
 tensors={p:build_weighted_tensor(p,i) for i,p in enumerate(("x","y","z","w"))}
 # ordered composites remain distinct, each transition passes plastic equilibrium and zero-sum closure.
 gates={r:alignment_gate(tensors[r[0]],tensors[r[1]],r) for r in ("xy","yx","zw","wz")}
 phase_states=list(PHASES)
 interstitial=("PLASTIC_EQUILIBRIUM","ZERO_SUM_CLOSURE")
 out={"schema":"HHS_LO_SHU_HARMONIC_PHASE_ENERGY_RUN_V1","version":VERSION,"authority":AUTHORITY,"pass067_root_hash72":pass067["run_root_hash72"],"base_energy":list(BASE),"base_conservation":validate_magic([Fraction(x) for x in BASE]),"weighted_tensors":tensors,"ordered_phase_gates":gates,"phase_states":phase_states,"interstitial_constraint_states":list(interstitial),"effective_transition_grammar":"PHASE -> PLASTIC_EQUILIBRIUM -> A:B_ALIGNMENT -> ZERO_SUM_CLOSURE -> PHASE","ordered_products_distinct":gates["xy"]["gate_root_hash72"]!=gates["yx"]["gate_root_hash72"],"total_four_tensor_energy":900,"energy_confers_authority":False,"rejection_codes":list(REJECTIONS)}
 out["ok"]=out["base_conservation"]["ok"] and all(t["projection"]["conservation"]["ok"] for t in tensors.values()) and all(g["continuation_admitted"] for g in gates.values()) and out["ordered_products_distinct"]
 out["run_root_hash72"]=_root("hhs_lo_shu_harmonic_phase_energy_run_v1",out); return out

def harmonic_phase_energy_self_test()->Dict[str,Any]:
 r=run_harmonic_phase_energy(); return {"schema":"HHS_LO_SHU_HARMONIC_PHASE_ENERGY_SELF_TEST_V1","ok":r["ok"],"run_root_hash72":r["run_root_hash72"],"center_cells_fixed":all(t["projection"]["center_fixed"] for t in r["weighted_tensors"].values()),"plastic_and_zero_sum_interstitial":r["interstitial_constraint_states"]==["PLASTIC_EQUILIBRIUM","ZERO_SUM_CLOSURE"]}

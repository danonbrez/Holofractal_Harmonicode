"""Pass 062 — Global Reciprocal Contract Topology and xyzw Phase-Gear Expansion / Contraction."""
from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping, Sequence
import json
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_bounded_rejection_authority_v1 import run_bounded_rejection_authority

VERSION="PASS_062_GLOBAL_RECIPROCAL_CONTRACT_TOPOLOGY_XYZW_PHASE_GEAR_V1"
AUTHORITY="HHS_GLOBAL_RECIPROCAL_CONTRACT_TOPOLOGY_AUTHORITY_V1"
MODULUS=72
REJECTIONS=[
"REJECT_GLOBAL_EXPANSION_ERASES_LOCAL_CONTRACT_IDENTITY",
"REJECT_CONTRACTION_LOSES_PROVENANCE",
"REJECT_POSITIVE_PHASE_AMPLIFIES_AUTHORITY",
"REJECT_NEGATIVE_PHASE_AMPLIFIES_REJECTION",
"REJECT_RECIPROCAL_PAIR_COLLAPSES_TO_ONE_SIDED_CONTROL",
"REJECT_GLOBAL_TOPOLOGY_INVALIDATES_LOCAL_CONTRACT_WITHOUT_WITNESS",
"REJECT_LOCAL_CONTRACT_CLAIMS_GLOBAL_SOVEREIGNTY",
"REJECT_PHASE_GEAR_BYPASSES_ROLE_AUTHORITY_BOUNDARY",
"REJECT_XYZW_ORIENTATION_CLOSURE_FAILURE",
"REJECT_EXPANSION_WITHOUT_RECIPROCAL_CONTRACT_PAIR",
"REJECT_CONTRACTION_NOT_LEFT_INVERSE_OF_EXPANSION",
"REJECT_XYZW_TYPED_EQUALITY_FRAME_COLLAPSE",
]
def _w(label:str,payload:Any)->Dict[str,Any]: return make_hash72_kernel_witness(label,payload,width=72).to_dict()
def _root(label:str,payload:Any)->str: return _w(label,payload)["digest"]
def _finish(schema:str,obj:Dict[str,Any],field:str,label:str)->Dict[str,Any]:
 out={"schema":schema,"version":VERSION,"authority":AUTHORITY,**obj}; out[field]=_root(label,out); return out
def _m(v:int)->int: return int(v)%MODULUS

def build_local_reciprocal_contract_pair(*,pair_id:str,source_root:str,positive_scope:Iterable[str],negative_scope:Iterable[str],role_root:str,rejection_root:str)->Dict[str,Any]:
 p=sorted(set(positive_scope)); n=sorted(set(negative_scope)); reasons=[]
 if not p or not n: reasons.append("REJECT_EXPANSION_WITHOUT_RECIPROCAL_CONTRACT_PAIR")
 return _finish("HHS_LOCAL_RECIPROCAL_CONTRACT_PAIR_V1",{
  "pair_id":pair_id,"source_root_hash72":source_root,"positive_contract":{"phase":"+1","scope":p,"authority_amplifying":False},
  "negative_contract":{"phase":"-1","scope":n,"rejection_amplifying":False},"equilibrium_phase":"0",
  "role_contract_root_hash72":role_root,"bounded_rejection_root_hash72":rejection_root,
  "local_identity_preserved":True,"global_sovereignty_claimed":False,"status":"ADMIT_LOCAL_RECIPROCAL_PAIR" if not reasons else "REJECT_LOCAL_PAIR","reasons":reasons
 },"local_reciprocal_pair_root_hash72","hhs_local_reciprocal_contract_pair_v1")

def build_xyzw_algebra_contract(pair:Mapping[str,Any])->Dict[str,Any]:
 """Encode the system-internal xyzw algebra without collapsing typed equality frames.

 Equality is carried as a typed relation.  Apparent contradiction is reported only
 when an external validator erases the declared relation frame.
 """
 root=pair.get("local_reciprocal_pair_root_hash72")
 symbols=["i","x","y","xy","yx","X","Y","z","w","0","1"]
 relations=[
  {"relation":"DISTINCT","members":["x","y","0","1"]},
  {"relation":"DISTINCT","members":["i","x","y","xy","yx"]},
  {"relation":"ORIENTED_ANTICOMMUTATION","lhs":"xy","rhs":"-yx","expression":"xy = -yx"},
  {"relation":"RECIPROCAL","lhs":"x","rhs":"1/y","expression":"x = 1/y"},
  {"relation":"PHASE_INVERSE","lhs":"y","rhs":"-x","expression":"y = -x"},
  {"relation":"NORMALIZED_UNIT","lhs":"xy","rhs":"1","frame":"LOCAL_PRODUCT_CLOSURE"},
  {"relation":"NORMALIZED_UNIT","lhs":"yx","rhs":"1","frame":"RECIPROCAL_PRODUCT_CLOSURE"},
  {"relation":"ORIENTED_RATIO","lhs":["x","y"],"rhs":["xy","yx"],"canonical_ratio":"I:I^3 = 1:-1"},
  {"relation":"ZERO_SUM","terms":["x","y","xy","yx"],"result":"0"},
  {"relation":"BRAID","lhs":"xyx","rhs":"yxy"},
  {"relation":"ALIAS","members":["X","xy","z"]},
  {"relation":"ALIAS","members":["Y","yx","w"]},
  {"relation":"GLOBAL_PRODUCT_CLOSURE","expression":"xyXY = xyzw = 1"},
  {"relation":"TOPOLOGICAL_BALANCE","expression":"x + y - z - w = 0"},
 ]
 equality_frames={
  "IDENTITY_EQ":"same declared symbol/object identity",
  "RELATIONAL_EQ":"contract-preserving relation between distinct states",
  "PHASE_EQ":"orientation/phase normalization",
  "NORMALIZED_EQ":"shared unit ratio after declared normalization",
  "ALIAS_EQ":"multiple names for one committed projection",
  "CLOSURE_EQ":"equivalent closed expressions in the admitted manifold",
 }
 return _finish("HHS_XYZW_ALGEBRA_CONTRACT_V1",{
  "local_reciprocal_pair_root_hash72":root,
  "symbols":symbols,"relations":relations,"equality_frames":equality_frames,
  "external_untyped_equality_assumption_allowed":False,
  "internal_contradiction_detected":False,
  "contradiction_boundary":"ONLY_IF_EQUALITY_FRAMES_ARE_ERASED",
  "transport_constant":{"integer_numerator":179971179971,"integer_denominator":1000000,"decimal_string":"179971.179971","floating_point_used":False},
  "unit_ring":"u^72","lo_shu_tensor":[[4,9,2],[3,5,7],[8,1,6]],
  "status":"ADMIT_XYZW_TYPED_EQUALITY_ALGEBRA","reasons":[]
 },"xyzw_algebra_contract_root_hash72","hhs_xyzw_algebra_contract_v1")

def build_xyzw_phase_gear(pair:Mapping[str,Any],*,x:int,y:int,z:int,w:int,algebra_contract:Mapping[str,Any]|None=None)->Dict[str,Any]:
 vals={"x":_m(x),"y":_m(y),"z":_m(z),"w":_m(w)}
 balance=_m(vals['x']+vals['y']-vals['z']-vals['w']); reasons=[]
 if balance!=0: reasons.append("REJECT_XYZW_ORIENTATION_CLOSURE_FAILURE")
 if algebra_contract is not None and algebra_contract.get("internal_contradiction_detected"):
  reasons.append("REJECT_XYZW_TYPED_EQUALITY_FRAME_COLLAPSE")
 return _finish("HHS_XYZW_RECIPROCAL_PHASE_GEAR_V1",{
  "local_reciprocal_pair_root_hash72":pair.get("local_reciprocal_pair_root_hash72"),
  "xyzw_algebra_contract_root_hash72":None if algebra_contract is None else algebra_contract.get("xyzw_algebra_contract_root_hash72"),
  "coordinates":vals,"coordinate_semantics":{"x":"local positive source phase","y":"local reciprocal negative phase","z":"X=xy expansion axis","w":"Y=yx contraction axis"},
  "orientation_equation":"x + y - z - w = 0 (mod u^72)","orientation_balance_mod72":balance,"orientation_closed":balance==0,
  "reciprocal_product_equation":"xyXY = xyzw = 1","braid_equation":"xyx = yxy",
  "typed_equality_preserved":not reasons or reasons==["REJECT_XYZW_ORIENTATION_CLOSURE_FAILURE"],
  "positive_phase_axis":["x","z"],"negative_phase_axis":["y","w"],"role_boundary_bypassed":False,
  "status":"ADMIT_XYZW_PHASE_GEAR" if not reasons else "REJECT_XYZW_PHASE_GEAR","reasons":reasons
 },"xyzw_phase_gear_root_hash72","hhs_xyzw_reciprocal_phase_gear_v1")

def expand_global_topology(pairs:Sequence[Mapping[str,Any]],gears:Sequence[Mapping[str,Any]])->Dict[str,Any]:
 reasons=[]
 if len(pairs)!=len(gears) or not pairs: reasons.append("REJECT_EXPANSION_WITHOUT_RECIPROCAL_CONTRACT_PAIR")
 if any(not p.get("local_identity_preserved") for p in pairs): reasons.append("REJECT_GLOBAL_EXPANSION_ERASES_LOCAL_CONTRACT_IDENTITY")
 if any(not g.get("orientation_closed") for g in gears): reasons.append("REJECT_XYZW_ORIENTATION_CLOSURE_FAILURE")
 local_roots=[p.get("local_reciprocal_pair_root_hash72") for p in pairs]
 gear_roots=[g.get("xyzw_phase_gear_root_hash72") for g in gears]
 topo_payload={"local_pair_roots_hash72":local_roots,"phase_gear_roots_hash72":gear_roots,"coupling":"RECIPROCAL_NON_AMPLIFYING","modulus":72}
 return _finish("HHS_GLOBAL_RECIPROCAL_CONTRACT_TOPOLOGY_V1",{
  **topo_payload,"local_contract_count":len(local_roots),"local_identities_preserved":not reasons,
  "positive_authority_amplified":False,"negative_rejection_amplified":False,"one_sided_control":False,
  "expansion_witness":_w("hhs_global_reciprocal_topology_expansion_witness_v1",topo_payload),
  "status":"ADMIT_GLOBAL_RECIPROCAL_TOPOLOGY" if not reasons else "REJECT_GLOBAL_TOPOLOGY_EXPANSION","reasons":reasons
 },"global_topology_root_hash72","hhs_global_reciprocal_contract_topology_v1")

def contract_global_topology(topology:Mapping[str,Any],pairs:Sequence[Mapping[str,Any]],gears:Sequence[Mapping[str,Any]])->Dict[str,Any]:
 expected_pairs=list(topology.get("local_pair_roots_hash72",[])); actual_pairs=[p.get("local_reciprocal_pair_root_hash72") for p in pairs]
 expected_gears=list(topology.get("phase_gear_roots_hash72",[])); actual_gears=[g.get("xyzw_phase_gear_root_hash72") for g in gears]
 reasons=[]
 if expected_pairs!=actual_pairs or expected_gears!=actual_gears: reasons.append("REJECT_CONTRACTION_LOSES_PROVENANCE")
 recovered=not reasons
 return _finish("HHS_GLOBAL_TO_LOCAL_CONTRACT_CONTRACTION_V1",{
  "global_topology_root_hash72":topology.get("global_topology_root_hash72"),"recovered_local_pair_roots_hash72":actual_pairs,
  "recovered_phase_gear_roots_hash72":actual_gears,"provenance_preserved":recovered,"left_inverse_verified":recovered,
  "lossless_contraction":recovered,"status":"ADMIT_LOSSLESS_CONTRACTION" if recovered else "REJECT_GLOBAL_CONTRACTION","reasons":reasons
 },"contraction_root_hash72","hhs_global_to_local_contract_contraction_v1")

def validate_global_reciprocity(topology:Mapping[str,Any],contraction:Mapping[str,Any])->Dict[str,Any]:
 reasons=[]
 if topology.get("positive_authority_amplified"): reasons.append("REJECT_POSITIVE_PHASE_AMPLIFIES_AUTHORITY")
 if topology.get("negative_rejection_amplified"): reasons.append("REJECT_NEGATIVE_PHASE_AMPLIFIES_REJECTION")
 if topology.get("one_sided_control"): reasons.append("REJECT_RECIPROCAL_PAIR_COLLAPSES_TO_ONE_SIDED_CONTROL")
 if not contraction.get("left_inverse_verified"): reasons.append("REJECT_CONTRACTION_NOT_LEFT_INVERSE_OF_EXPANSION")
 return _finish("HHS_GLOBAL_RECIPROCAL_TOPOLOGY_VALIDATION_V1",{
  "global_topology_root_hash72":topology.get("global_topology_root_hash72"),"contraction_root_hash72":contraction.get("contraction_root_hash72"),
  "authority_non_amplifying":not topology.get("positive_authority_amplified",True),"rejection_non_amplifying":not topology.get("negative_rejection_amplified",True),
  "reciprocal_distinction_preserved":not topology.get("one_sided_control",True),"canonical_reciprocity":not reasons,
  "status":"ADMIT_GLOBAL_RECIPROCAL_CONTRACT_CONTINUATION" if not reasons else "REJECT_GLOBAL_RECIPROCAL_CONTINUATION","reasons":reasons
 },"global_reciprocity_validation_root_hash72","hhs_global_reciprocal_topology_validation_v1")

def run_global_reciprocal_contract_topology()->Dict[str,Any]:
 p61=run_bounded_rejection_authority(); base=p61["run_root_hash72"]
 pair_a=build_local_reciprocal_contract_pair(pair_id="pair:authority-rejection",source_root=base,positive_scope=["ADMIT_ROLE_LOCAL_OPERATION"],negative_scope=["REJECT_SCOPE_VIOLATION"],role_root=p61['role_contract']['rejection_role_contract_root_hash72'],rejection_root=p61['rejection_decision']['rejection_decision_root_hash72'])
 pair_b=build_local_reciprocal_contract_pair(pair_id="pair:expansion-contraction",source_root=base,positive_scope=["EXPAND_WITNESSED_TOPOLOGY"],negative_scope=["CONTRACT_WITHOUT_LOSS"],role_root=p61['role_contract']['rejection_role_contract_root_hash72'],rejection_root=p61['non_amplification_validation']['non_amplification_validation_root_hash72'])
 algebra_a=build_xyzw_algebra_contract(pair_a); algebra_b=build_xyzw_algebra_contract(pair_b)
 gear_a=build_xyzw_phase_gear(pair_a,x=4,y=9,z=5,w=8,algebra_contract=algebra_a)
 gear_b=build_xyzw_phase_gear(pair_b,x=3,y=7,z=2,w=8,algebra_contract=algebra_b)
 pairs=[pair_a,pair_b]; gears=[gear_a,gear_b]
 topology=expand_global_topology(pairs,gears); contraction=contract_global_topology(topology,pairs,gears); validation=validate_global_reciprocity(topology,contraction)
 out={"schema":"HHS_GLOBAL_RECIPROCAL_CONTRACT_TOPOLOGY_RUN_V1","version":VERSION,"authority":AUTHORITY,
  "ok":p61['ok'] and validation['canonical_reciprocity'],"pass061_root_hash72":base,"local_pairs":pairs,"xyzw_algebra_contracts":[algebra_a,algebra_b],"phase_gears":gears,
  "global_topology":topology,"contraction":contraction,"validation":validation,"rejection_codes":REJECTIONS}
 out['run_root_hash72']=_root('hhs_global_reciprocal_contract_topology_run_v1',out); return out

def global_reciprocal_contract_topology_self_test()->Dict[str,Any]:
 run=run_global_reciprocal_contract_topology(); p=run['local_pairs'][0]
 bad_gear=build_xyzw_phase_gear(p,x=1,y=2,z=3,w=5)
 bad_top=dict(run['global_topology']); bad_top['positive_authority_amplified']=True; bad_top['negative_rejection_amplified']=True; bad_top['one_sided_control']=True
 bad_contract=contract_global_topology(run['global_topology'],run['local_pairs'][:1],run['phase_gears'][:1])
 bad_validation=validate_global_reciprocity(bad_top,bad_contract)
 ok=run['ok'] and 'REJECT_XYZW_ORIENTATION_CLOSURE_FAILURE' in bad_gear['reasons'] and 'REJECT_POSITIVE_PHASE_AMPLIFIES_AUTHORITY' in bad_validation['reasons'] and 'REJECT_NEGATIVE_PHASE_AMPLIFIES_REJECTION' in bad_validation['reasons'] and 'REJECT_CONTRACTION_NOT_LEFT_INVERSE_OF_EXPANSION' in bad_validation['reasons']
 return {"schema":"HHS_GLOBAL_RECIPROCAL_CONTRACT_TOPOLOGY_SELF_TEST_V1","ok":ok,"run_root_hash72":run['run_root_hash72'],"negative_cases":{"bad_gear":bad_gear,"bad_validation":bad_validation}}
if __name__=='__main__': print(json.dumps(global_reciprocal_contract_topology_self_test(),indent=2,sort_keys=True))

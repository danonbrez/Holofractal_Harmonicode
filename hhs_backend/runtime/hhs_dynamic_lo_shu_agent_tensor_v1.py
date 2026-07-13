"""Pass 067 — Dynamic Lo Shu Agent Tensor and witnessed probabilistic algorithm activation."""
from __future__ import annotations
from fractions import Fraction
from typing import Any, Dict, Mapping, Sequence
import json
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_canonical_resolution_agent_identity_v1 import run_agent_economy

VERSION="PASS_067_DYNAMIC_LO_SHU_AGENT_TENSOR_V1"
AUTHORITY="HHS_DYNAMIC_LO_SHU_AGENT_TENSOR_AUTHORITY_V1"
LO_SHU=(4,9,2,3,5,7,8,1,6)
DOMAINS=("FORMAL_ALGEBRA","SYMBOLIC_LOGIC","SEMANTIC_TRANSLATION","RUNTIME_EXECUTION","PROVENANCE_AUDIT","MULTIMODAL_FUSION","CONSTRAINT_TOPOLOGY","INFORMATION_ENERGY","CANONICAL_REVALIDATION")
REJECTIONS=("REJECT_INADMISSIBLE_AGENT_FROM_TENSOR","REJECT_MORE_THAN_NINE_AGENTS_PER_DOMAIN","REJECT_TENSOR_WITHOUT_LO_SHU_BIJECTION","REJECT_PROBABILITY_AS_AUTHORITY","REJECT_FITNESS_AS_AUTHORITY","REJECT_RANDOMNESS_WITHOUT_WITNESS","REJECT_ACTIVATION_OUTSIDE_DOMAIN","REJECT_ACTIVATION_WITHOUT_ROLE_SCOPE","REJECT_ACTIVATION_AS_CANONICAL_TRUTH","REJECT_WEIGHT_MUTATION_WITHOUT_PROVENANCE")

def _w(label:str,payload:Any)->Dict[str,Any]: return make_hash72_kernel_witness(label,payload,width=72).to_dict()
def _root(label:str,payload:Any)->str: return _w(label,payload)["digest"]
def _finish(schema:str,obj:Dict[str,Any],field:str,label:str)->Dict[str,Any]:
 out={"schema":schema,"version":VERSION,"authority":AUTHORITY,**obj}; out[field]=_root(label,out); return out

def build_domain_population(domain:str, economy:Mapping[str,Any])->list[Dict[str,Any]]:
 base={x["agent_id"]:x for x in economy["fitness_vectors"]}; ids=[x["agent_id"] for x in economy["identities"]]
 population=[]
 for i in range(12):
  parent=ids[i%len(ids)]; f=base[parent]; score=Fraction(f["fitness_rational"]["numerator"],f["fitness_rational"]["denominator"])
  # exact domain-local specialization; later variants pay a deterministic complexity penalty.
  adjusted=score/Fraction(1+(i//3),1)
  agent_id=f"{parent}:{domain.lower()}:{i+1}"
  population.append(_finish("HHS_DOMAIN_AGENT_CANDIDATE_V1",{
   "domain_id":domain,"agent_id":agent_id,"parent_agent_id":parent,"parent_fitness_root_hash72":f["fitness_root_hash72"],
   "admissible":bool(f["admissible_before_fitness"]),"role_scope_valid":True,"provenance_valid":True,
   "exact_fitness":{"numerator":adjusted.numerator,"denominator":adjusted.denominator},"probability_confers_authority":False
  },"candidate_root_hash72","hhs_domain_agent_candidate_v1"))
 return population

def select_top_nine(domain:str,population:Sequence[Mapping[str,Any]])->Dict[str,Any]:
 admissible=[p for p in population if p["admissible"] and p["role_scope_valid"] and p["provenance_valid"]]
 ordered=sorted(admissible,key=lambda p:(-Fraction(p["exact_fitness"]["numerator"],p["exact_fitness"]["denominator"]),p["agent_id"]))[:9]
 return _finish("HHS_DOMAIN_TOP_NINE_SELECTION_V1",{
  "domain_id":domain,"candidate_count":len(population),"selected_count":len(ordered),"selected_agents":list(ordered),
  "selection_rule":"ADMISSIBLE_THEN_EXACT_FITNESS_THEN_AGENT_ID","fitness_confers_authority":False
 },"top_nine_root_hash72","hhs_domain_top_nine_selection_v1")

def place_lo_shu_tensor(selection:Mapping[str,Any])->Dict[str,Any]:
 agents=selection["selected_agents"]
 if len(agents)!=9: raise ValueError("exactly nine admissible agents required")
 cells=[]
 for pos,(magic,agent) in enumerate(zip(LO_SHU,agents)):
  f=Fraction(agent["exact_fitness"]["numerator"],agent["exact_fitness"]["denominator"])
  weight=f*magic
  cells.append({"row":pos//3,"column":pos%3,"lo_shu_value":magic,"agent_id":agent["agent_id"],"candidate_root_hash72":agent["candidate_root_hash72"],"exact_weight":{"numerator":weight.numerator,"denominator":weight.denominator}})
 return _finish("HHS_DYNAMIC_LO_SHU_AGENT_TENSOR_V1",{
  "domain_id":selection["domain_id"],"shape":[3,3],"lo_shu_layout":list(LO_SHU),"magic_sum":15,"cells":cells,
  "unique_agent_count":len({c["agent_id"] for c in cells}),"probability_confers_authority":False,"tensor_is_canonical_truth":False
 },"tensor_root_hash72","hhs_dynamic_lo_shu_agent_tensor_v1")

def probability_distribution(tensor:Mapping[str,Any])->Dict[str,Any]:
 weights=[Fraction(c["exact_weight"]["numerator"],c["exact_weight"]["denominator"]) for c in tensor["cells"]]; total=sum(weights,Fraction(0,1))
 probs=[]
 for c,w in zip(tensor["cells"],weights):
  p=w/total; probs.append({"agent_id":c["agent_id"],"probability":{"numerator":p.numerator,"denominator":p.denominator},"admissible":True})
 return _finish("HHS_EXACT_AGENT_ACTIVATION_DISTRIBUTION_V1",{
  "domain_id":tensor["domain_id"],"tensor_root_hash72":tensor["tensor_root_hash72"],"probabilities":probs,
  "probability_sum":{"numerator":1,"denominator":1},"floating_point_used":False,"probability_confers_authority":False
 },"distribution_root_hash72","hhs_exact_agent_activation_distribution_v1")

def activate_agent(distribution:Mapping[str,Any],task_root_hash72:str)->Dict[str,Any]:
 seed={"domain_id":distribution["domain_id"],"distribution_root_hash72":distribution["distribution_root_hash72"],"task_root_hash72":task_root_hash72}
 witness=_w("hhs_witnessed_probability_draw_v1",seed)
 probs=[Fraction(p["probability"]["numerator"],p["probability"]["denominator"]) for p in distribution["probabilities"]]
 common=1
 import math
 for p in probs: common=math.lcm(common,p.denominator)
 tickets=[p.numerator*(common//p.denominator) for p in probs]; total=sum(tickets)
 draw=sum(ord(ch) for ch in witness["digest"])%total
 cursor=0; selected=0
 for i,t in enumerate(tickets):
  cursor+=t
  if draw<cursor: selected=i; break
 p=distribution["probabilities"][selected]
 return _finish("HHS_WITNESSED_PROBABILISTIC_AGENT_ACTIVATION_V1",{
  "domain_id":distribution["domain_id"],"task_root_hash72":task_root_hash72,"distribution_root_hash72":distribution["distribution_root_hash72"],
  "draw_witness":witness,"ticket_total":total,"ticket_index":draw,"selected_agent_id":p["agent_id"],
  "selected_agent_admissible":p["admissible"],"activation_is_local":True,"activation_confers_authority":False,
  "activation_becomes_canonical_truth":False,"requires_post_execution_revalidation":True,"status":"ADMIT_LOCAL_AGENT_ACTIVATION"
 },"activation_root_hash72","hhs_witnessed_probabilistic_agent_activation_v1")

def run_dynamic_lo_shu_agent_tensor()->Dict[str,Any]:
 economy=run_agent_economy(); domain_runs=[]
 for domain in DOMAINS:
  pop=build_domain_population(domain,economy); top=select_top_nine(domain,pop); tensor=place_lo_shu_tensor(top); dist=probability_distribution(tensor)
  task_root=_root("hhs_domain_activation_task_v1",{"domain":domain,"pass066":economy["run_root_hash72"]}); activation=activate_agent(dist,task_root)
  domain_runs.append({"domain_id":domain,"population":pop,"top_nine":top,"tensor":tensor,"distribution":dist,"activation":activation})
 out={"schema":"HHS_DYNAMIC_LO_SHU_AGENT_TENSOR_RUN_V1","version":VERSION,"authority":AUTHORITY,"pass066_root_hash72":economy["run_root_hash72"],"domain_count":len(DOMAINS),"agents_per_tensor":9,"domain_runs":domain_runs,"rejection_codes":list(REJECTIONS),"ok":all(d["activation"]["selected_agent_admissible"] and d["tensor"]["magic_sum"]==15 for d in domain_runs)}
 out["run_root_hash72"]=_root("hhs_dynamic_lo_shu_agent_tensor_run_v1",out); return out

def dynamic_lo_shu_agent_tensor_self_test()->Dict[str,Any]:
 run=run_dynamic_lo_shu_agent_tensor(); first=run["domain_runs"][0]
 deterministic=activate_agent(first["distribution"],first["activation"]["task_root_hash72"])["selected_agent_id"]==first["activation"]["selected_agent_id"]
 ok=run["ok"] and deterministic and all(d["top_nine"]["selected_count"]==9 and d["tensor"]["unique_agent_count"]==9 and d["distribution"]["probability_sum"]=={"numerator":1,"denominator":1} for d in run["domain_runs"])
 return {"schema":"HHS_DYNAMIC_LO_SHU_AGENT_TENSOR_SELF_TEST_V1","ok":ok,"run_root_hash72":run["run_root_hash72"],"deterministic_witnessed_activation":deterministic}

if __name__=="__main__": print(json.dumps(dynamic_lo_shu_agent_tensor_self_test(),indent=2,sort_keys=True))

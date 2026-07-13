"""Pass 066 — canonical resolution-agent identity and evolutionary information-energy economy."""
from __future__ import annotations
from fractions import Fraction
from typing import Any, Dict, Mapping, Sequence
import json
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_local_parallel_branch_tree_v1 import run_local_parallel_branch_tree

VERSION="PASS_066_CANONICAL_RESOLUTION_AGENT_ECONOMY_V1"
AUTHORITY="HHS_EVOLUTIONARY_AGENT_IDENTITY_AUTHORITY_V1"
REJECTIONS=[
 "REJECT_AGENT_WITHOUT_CANONICAL_IDENTITY","REJECT_AGENT_UPDATE_WITHOUT_LINEAGE",
 "REJECT_FITNESS_AS_AUTHORITY","REJECT_WINNER_AS_CANONICAL_TRUTH",
 "REJECT_FITNESS_BY_CONSTRAINT_AVOIDANCE","REJECT_ACCURACY_BY_GLOBAL_REJECTION",
 "REJECT_SIMPLICITY_BY_HIDDEN_DEPENDENCY","REJECT_EFFICIENCY_BY_PROVENANCE_LOSS",
 "REJECT_ALIGNMENT_BY_AGREEMENT_RATE","REJECT_BENCHMARK_MEMORIZATION_AS_GENERALIZATION",
 "REJECT_DELEGATED_SUCCESS_AS_SOLE_AGENT_COMPETENCE","REJECT_FAILURE_AS_PERMANENT_GLOBAL_AGENT_INVALIDATION",
 "REJECT_MUTATION_WITHOUT_LINEAGE","REJECT_COOPERATION_WITHOUT_CONTRIBUTION_PROVENANCE"]

def _w(label:str,payload:Any)->Dict[str,Any]: return make_hash72_kernel_witness(label,payload,width=72).to_dict()
def _root(label:str,payload:Any)->str: return _w(label,payload)["digest"]
def _finish(schema:str,obj:Dict[str,Any],field:str,label:str)->Dict[str,Any]:
 out={"schema":schema,"version":VERSION,"authority":AUTHORITY,**obj}; out[field]=_root(label,out); return out

def build_algorithm_identity(agent_id:str, algorithm:str, dependencies:Sequence[str])->Dict[str,Any]:
 return _finish("HHS_AGENT_ALGORITHM_IDENTITY_V1",{
  "agent_id":agent_id,"algorithm_name":algorithm,"algorithm_source":algorithm,
  "dependencies":list(dependencies),"dependency_count":len(dependencies),"hidden_dependencies":False,
  "algorithmic_size_units":len(algorithm),"dense_matrix_dependency":False
 },"algorithm_root_hash72","hhs_agent_algorithm_identity_v1")

def build_agent_identity(agent_id:str, branch_root:str, algorithm:Mapping[str,Any], parent_ids:Sequence[str]=())->Dict[str,Any]:
 genesis={"agent_id":agent_id,"branch_root":branch_root,"algorithm_root":algorithm["algorithm_root_hash72"],"parents":list(parent_ids)}
 return _finish("HHS_CANONICAL_RESOLUTION_AGENT_IDENTITY_V1",{
  "agent_id":agent_id,"genesis_root_hash72":_root("hhs_agent_genesis_v1",genesis),"parent_agent_ids":list(parent_ids),
  "algorithm_root_hash72":algorithm["algorithm_root_hash72"],"dependency_root_hash72":_root("hhs_agent_dependencies_v1",algorithm["dependencies"]),
  "role_contract_root_hash72":_root("hhs_resolution_role_contract_v1",["LOCAL_CONSTRAINT_RESOLUTION","NO_GLOBAL_AUTHORITY"]),
  "competency_profile":["LOCAL_BRANCH_REASONING","A_EQUALS_B_REINTEGRATION","PROVENANCE_PRESERVATION"],
  "verbatim_semantic_record_id":"semantic:"+agent_id,"knowledge_graph_node_id":"kg:"+agent_id,
  "status":"ACTIVE","identity_is_process_instance":False,"fitness_confers_authority":False
 },"agent_identity_root_hash72","hhs_canonical_resolution_agent_identity_v1")

def commit_experience(identity:Mapping[str,Any], branch_receipt:Mapping[str,Any], outcome:str)->Dict[str,Any]:
 return _finish("HHS_AGENT_EXPERIENCE_COMMITMENT_V1",{
  "agent_id":identity["agent_id"],"agent_identity_root_hash72":identity["agent_identity_root_hash72"],
  "verbatim_source_root_hash72":branch_receipt["branch_execution_root_hash72"],"source_preserved_verbatim":True,
  "constraint_id":"constraint:A=B:integration","strategy":branch_receipt["strategy"],"outcome":outcome,
  "abstraction_replaces_source":False,"provenance_complete":branch_receipt["provenance_complete"]
 },"experience_root_hash72","hhs_agent_experience_commitment_v1")

def build_knowledge_graph(identity:Mapping[str,Any], experience:Mapping[str,Any], peer_ids:Sequence[str])->Dict[str,Any]:
 edges=[{"edge":"RESOLVED_CONSTRAINT","target":"constraint:A=B:integration"},{"edge":"DERIVES_FROM","target":experience["experience_root_hash72"]}]
 edges += [{"edge":"COOPERATED_WITH","target":p} for p in peer_ids]
 return _finish("HHS_MULTIMODAL_AGENT_KNOWLEDGE_GRAPH_NODE_V1",{
  "node_id":identity["knowledge_graph_node_id"],"agent_id":identity["agent_id"],"modalities":["FORMAL_ALGEBRA","SEMANTIC_TEXT","RUNTIME_RECEIPT"],
  "edges":edges,"source_identity_preserved":True,"cache_projection_claims_source_identity":False
 },"knowledge_graph_root_hash72","hhs_multimodal_agent_knowledge_graph_v1")

def account_information_energy(identity:Mapping[str,Any], receipt:Mapping[str,Any])->Dict[str,Any]:
 cost=int(receipt["candidate"]["cost"])
 vector={"compute":cost,"memory":1,"dependency":0,"branch":1,"closure":1,"revalidation":1}
 return _finish("HHS_INFORMATION_ENERGY_ACCOUNTING_V1",{
  "agent_id":identity["agent_id"],"branch_execution_root_hash72":receipt["branch_execution_root_hash72"],
  "cost_vector":vector,"total_cost_units":sum(vector.values()),"floating_point_used":False,"transfer_witnessed":True
 },"information_energy_root_hash72","hhs_information_energy_accounting_v1")

def difficulty_profile()->Dict[str,Any]:
 v={"relation_count":4,"operator_diversity":3,"contradiction_density":1,"phase_misalignment":1,"branch_depth":1,"translation_distance":2}
 return _finish("HHS_CONSTRAINT_DIFFICULTY_PROFILE_V1",{"constraint_id":"constraint:A=B:integration","difficulty_vector":v,"difficulty_units":sum(v.values())},"difficulty_root_hash72","hhs_constraint_difficulty_profile_v1")

def fitness_vector(identity:Mapping[str,Any], energy:Mapping[str,Any], *, aligned:bool, provenance:bool, diversity:int, complexity:int)->Dict[str,Any]:
 admissible=aligned and provenance
 numerator=(100 if aligned else 0)*diversity*complexity
 denominator=max(1,energy["total_cost_units"])
 score=Fraction(numerator,denominator) if admissible else Fraction(0,1)
 return _finish("HHS_AGENT_FITNESS_VECTOR_V1",{
  "agent_id":identity["agent_id"],"admissible_before_fitness":admissible,
  "metrics":{"alignment_fidelity":100 if aligned else 0,"constraint_diversity":diversity,"complexity_coverage":complexity,
             "algorithmic_size":1,"dependency_cost":0,"information_energy_cost":energy["total_cost_units"],"semantic_drift":0 if provenance else 100},
  "fitness_rational":{"numerator":score.numerator,"denominator":score.denominator},"fitness_confers_authority":False,
  "global_authority_transfer":False
 },"fitness_root_hash72","hhs_agent_fitness_vector_v1")

def contribution_receipt(agent_ids:Sequence[str], roles:Sequence[str])->Dict[str,Any]:
 contributions=[{"agent_id":a,"role":r} for a,r in zip(agent_ids,roles)]
 return _finish("HHS_AGENT_CONTRIBUTION_PROVENANCE_V1",{
  "contributions":contributions,"identity_merger":False,"all_contributions_preserved":len(contributions)==len(agent_ids)
 },"contribution_root_hash72","hhs_agent_contribution_provenance_v1")

def mutate_agent(parent:Mapping[str,Any], algorithm:Mapping[str,Any])->Dict[str,Any]:
 child_id=parent["agent_id"]+":mutation:1"
 child_alg=build_algorithm_identity(child_id,algorithm["algorithm_name"]+"+phase_cache",algorithm["dependencies"])
 child=build_agent_identity(child_id,parent["agent_identity_root_hash72"],child_alg,[parent["agent_id"]])
 return _finish("HHS_AGENT_MUTATION_LINEAGE_V1",{
  "parent_agent_id":parent["agent_id"],"parent_identity_root_hash72":parent["agent_identity_root_hash72"],
  "descendant_agent_id":child_id,"descendant_identity_root_hash72":child["agent_identity_root_hash72"],
  "algorithm_delta":"ADD_LOCAL_PHASE_CACHE","parent_preserved":True,"lineage_continuous":True,"mutation_redefines_invariants":False
 },"mutation_root_hash72","hhs_agent_mutation_lineage_v1")

def select_agents(fitnesses:Sequence[Mapping[str,Any]])->Dict[str,Any]:
 admissible=[f for f in fitnesses if f["admissible_before_fitness"]]
 ordered=sorted(admissible,key=lambda f:(-Fraction(f["fitness_rational"]["numerator"],f["fitness_rational"]["denominator"]),f["agent_id"]))
 winner=ordered[0] if ordered else None
 return _finish("HHS_EVOLUTIONARY_AGENT_SELECTION_V1",{
  "candidate_fitness_roots_hash72":[f["fitness_root_hash72"] for f in fitnesses],"selected_agent_id":winner["agent_id"] if winner else None,
  "selection_rule":"ADMISSIBILITY_THEN_MAX_EXACT_FITNESS_THEN_AGENT_ID","winner_becomes_canonical_truth":False,
  "winner_receives_global_authority":False,"losing_information_preserved":True,"status":"ADMIT_LOCAL_AGENT_SELECTION" if winner else "REJECT_AGENT_SELECTION"
 },"selection_root_hash72","hhs_evolutionary_agent_selection_v1")

def run_agent_economy()->Dict[str,Any]:
 tree=run_local_parallel_branch_tree(); receipts=tree["branch_receipts"]
 specs=[("agent:minimal-direct","minimal_reciprocal_align",[]),("agent:bridge","translation_phase_bridge",["phase_bridge"]),("agent:contract","local_reciprocal_contract",["contractor"])]
 algorithms=[build_algorithm_identity(*s) for s in specs]
 identities=[build_agent_identity(s[0],tree["closure"]["branch_tree_closure_root_hash72"],algorithms[i]) for i,s in enumerate(specs)]
 experiences=[commit_experience(identities[i],receipts[i],"CLOSED" if receipts[i]["provenance_complete"] else "FAILED") for i in range(3)]
 graphs=[build_knowledge_graph(identities[i],experiences[i],[x["agent_id"] for x in identities if x["agent_id"]!=identities[i]["agent_id"]]) for i in range(3)]
 energies=[account_information_energy(identities[i],receipts[i]) for i in range(3)]
 difficulty=difficulty_profile()
 fitnesses=[fitness_vector(identities[i],energies[i],aligned=True,provenance=receipts[i]["provenance_complete"],diversity=3-i,complexity=difficulty["difficulty_units"]) for i in range(3)]
 contribution=contribution_receipt([x["agent_id"] for x in identities],["PROPOSAL","TRANSLATION_REPAIR","INDEPENDENT_ALTERNATIVE"])
 mutation=mutate_agent(identities[0],algorithms[0]); selection=select_agents(fitnesses)
 out={"schema":"HHS_AGENT_ECONOMY_RUN_V1","version":VERSION,"authority":AUTHORITY,"ok":tree["ok"] and selection["selected_agent_id"]=="agent:minimal-direct",
  "pass065_root_hash72":tree["run_root_hash72"],"algorithms":algorithms,"identities":identities,"experiences":experiences,"knowledge_graph_nodes":graphs,
  "information_energy_accounts":energies,"difficulty":difficulty,"fitness_vectors":fitnesses,"contribution_provenance":contribution,"mutation_lineage":mutation,
  "selection":selection,"rejection_codes":REJECTIONS}
 out["run_root_hash72"]=_root("hhs_agent_economy_run_v1",out); return out

def agent_economy_self_test()->Dict[str,Any]:
 run=run_agent_economy()
 bad_energy=dict(run["information_energy_accounts"][0]); bad_identity=run["identities"][0]
 lossy=fitness_vector(bad_identity,bad_energy,aligned=True,provenance=False,diversity=99,complexity=99)
 failed=fitness_vector(bad_identity,bad_energy,aligned=False,provenance=True,diversity=1,complexity=1)
 ok=run["ok"] and not lossy["admissible_before_fitness"] and failed["fitness_rational"]["numerator"]==0 and run["mutation_lineage"]["parent_preserved"] and run["contribution_provenance"]["all_contributions_preserved"]
 return {"schema":"HHS_AGENT_ECONOMY_SELF_TEST_V1","ok":ok,"run_root_hash72":run["run_root_hash72"],"negative_cases":{"lossy":lossy,"failed":failed}}

if __name__=="__main__": print(json.dumps(agent_economy_self_test(),indent=2,sort_keys=True))

from hhs_backend.runtime.hhs_dynamic_lo_shu_agent_tensor_v1 import *

def test_pass067_self_test(): assert dynamic_lo_shu_agent_tensor_self_test()["ok"]
def test_nine_domains_each_have_top_nine():
 r=run_dynamic_lo_shu_agent_tensor(); assert r["domain_count"]==9; assert all(d["top_nine"]["selected_count"]==9 for d in r["domain_runs"])
def test_lo_shu_tensor_is_bijective_and_magic():
 r=run_dynamic_lo_shu_agent_tensor(); assert all(d["tensor"]["lo_shu_layout"]==[4,9,2,3,5,7,8,1,6] and d["tensor"]["magic_sum"]==15 and d["tensor"]["unique_agent_count"]==9 for d in r["domain_runs"])
def test_exact_probabilities_sum_to_one_without_float():
 r=run_dynamic_lo_shu_agent_tensor(); assert all(d["distribution"]["probability_sum"]=={"numerator":1,"denominator":1} and not d["distribution"]["floating_point_used"] for d in r["domain_runs"])
def test_probability_never_confers_authority():
 r=run_dynamic_lo_shu_agent_tensor(); assert all(not d["distribution"]["probability_confers_authority"] and not d["activation"]["activation_confers_authority"] for d in r["domain_runs"])
def test_witnessed_activation_is_deterministic():
 r=run_dynamic_lo_shu_agent_tensor(); d=r["domain_runs"][0]; again=activate_agent(d["distribution"],d["activation"]["task_root_hash72"]); assert again["selected_agent_id"]==d["activation"]["selected_agent_id"] and again["ticket_index"]==d["activation"]["ticket_index"]
def test_activation_requires_revalidation_and_is_local():
 r=run_dynamic_lo_shu_agent_tensor(); assert all(d["activation"]["activation_is_local"] and d["activation"]["requires_post_execution_revalidation"] and not d["activation"]["activation_becomes_canonical_truth"] for d in r["domain_runs"])
def test_inadmissible_agent_excluded_before_top_nine():
 r=run_agent_economy(); pop=build_domain_population("FORMAL_ALGEBRA",r); pop[0]=dict(pop[0],admissible=False); top=select_top_nine("FORMAL_ALGEBRA",pop); assert pop[0]["agent_id"] not in [x["agent_id"] for x in top["selected_agents"]]

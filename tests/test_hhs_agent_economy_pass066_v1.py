from hhs_backend.runtime.hhs_canonical_resolution_agent_identity_v1 import *

def test_pass066_self_test(): assert agent_economy_self_test()["ok"]
def test_unique_agent_identity_and_lineage():
 r=run_agent_economy(); ids=[a["agent_id"] for a in r["identities"]]; assert len(ids)==len(set(ids)); assert r["mutation_lineage"]["lineage_continuous"]
def test_fitness_never_confers_authority():
 r=run_agent_economy(); assert all(not f["fitness_confers_authority"] for f in r["fitness_vectors"]); assert not r["selection"]["winner_receives_global_authority"]
def test_verbatim_semantic_source_preserved():
 r=run_agent_economy(); assert all(e["source_preserved_verbatim"] and not e["abstraction_replaces_source"] for e in r["experiences"])
def test_cooperation_preserves_contributors():
 r=run_agent_economy(); assert r["contribution_provenance"]["all_contributions_preserved"]; assert not r["contribution_provenance"]["identity_merger"]
def test_lossy_agent_cannot_game_fitness():
 r=run_agent_economy(); f=fitness_vector(r["identities"][0],r["information_energy_accounts"][0],aligned=True,provenance=False,diversity=999,complexity=999); assert not f["admissible_before_fitness"]
def test_minimal_agent_wins_locally_without_global_authority():
 r=run_agent_economy(); assert r["selection"]["selected_agent_id"]=="agent:minimal-direct"; assert not r["selection"]["winner_becomes_canonical_truth"]
def test_failure_is_information_not_global_rejection():
 r=run_agent_economy(); f=fitness_vector(r["identities"][0],r["information_energy_accounts"][0],aligned=False,provenance=True,diversity=1,complexity=1); assert f["fitness_rational"]["numerator"]==0; assert r["identities"][0]["status"]=="ACTIVE"

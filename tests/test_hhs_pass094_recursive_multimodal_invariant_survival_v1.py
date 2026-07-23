from pathlib import Path
from native_projects.hhs_bifurcation_calibration.hhs_pass094_recursive_multimodal_invariant_survival_v1 import *
R=Path(__file__).resolve().parents[1]

def test_pass093_inputs_immutably_committed():
 i=load_pass093_inputs(R); assert i["manifest"]["pass_id"]=="PASS_093" and i["input_commitment_root_hash72"]

def test_at_least_eight_modalities_and_five_invariants():
 assert len(MODALITIES)>=8 and len(invariant_registry())>=5

def test_translation_contracts_declare_supported_fields():
 cs=translation_contract_registry(); assert cs and all(c["supported_invariants"] for c in cs)

def test_all_primary_round_trips_survive_exactly():
 r=run(R,default_workload(R)); assert r["all_exact"] and all(x["exact_survival"] for x in r["survival_receipts"])

def test_noncommutative_history_survives_ordered_path():
 inv=[i for i in invariant_registry() if i["formal_definition"]["type"]=="ORDERED_HISTORY"][0]
 x=translate(inv,["FORMAL_SYMBOLIC","GRAPH","NATURAL_LANGUAGE","FORMAL_SYMBOLIC"]); assert x["exact_survival"]

def test_recursive_translation_cycles_do_not_drift():
 inv=invariant_registry()[0]; c=recursive_cycle(inv,["FORMAL_SYMBOLIC","AUDIO_TONE_SEQUENCE","FORMAL_SYMBOLIC"],10); assert c["exact_survival"] and not c["recursive_translation_drift"]

def test_noise_controls_distinguish_irrelevant_and_targeted_change():
 inv=[i for i in invariant_registry() if i["formal_definition"]["type"]=="ORDERED_HISTORY"][0]
 n=noise_calibration(inv); assert any(x["classification"]=="EXACT_SURVIVAL" for x in n) and any(x["classification"]=="INVARIANT_FAILURE" for x in n)

def test_simplified_alphabet_has_exact_reconstruction_contract():
 a=simplified_alphabet(invariant_registry()); assert a["reconstruction_contract"]["exact"]

def test_replay_reproduces_complete_registry():
 assert verify_replay(R,default_workload(R,"T94:replay"))["deterministic_replay_verified"]

def test_all_negative_cases_pass():
 assert all(x["passed"] for x in negative_cases(R))

def test_registry_has_w94_01_through_w94_14():
 w=workload_registry(R); assert len(w)==14 and w[0]["workload_id"].startswith("W94-01") and w[-1]["workload_id"].startswith("W94-14")

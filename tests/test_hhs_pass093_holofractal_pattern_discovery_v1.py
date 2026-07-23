from pathlib import Path

from native_projects.hhs_bifurcation_calibration.hhs_pass093_holofractal_pattern_discovery_v1 import (
    build_alphabet, default_workload, load_pass092_inputs, negative_cases, null_models,
    run, verify_replay, workload_registry,
)

R=Path(__file__).resolve().parents[1]

def test_pass092_inputs_are_immutably_committed():
    i=load_pass092_inputs(R)
    assert i["manifest"]["pass_id"]=="PASS_092"
    assert i["input_commitment_root_hash72"]

def test_multiscale_candidates_have_exact_definitions_and_scale_maps():
    r=run(R,default_workload(R))
    assert r["candidate_registry"]
    assert all(c["exact_feature_definition"] for c in r["candidate_registry"])
    assert all(c["scale_maps"] for c in r["candidate_registry"])

def test_at_least_three_structure_preserving_null_models():
    lanes=load_pass092_inputs(R)["lanes"][:64]
    models=null_models(lanes)
    assert len(models)>=3
    assert all(m["preserves"] for m in models)

def test_alphabet_is_lossless_and_held_out_reconstructable():
    r=run(R,default_workload(R,"T93:alphabet"))
    a=r["discovered_alphabets"][0]
    assert a["loss_classification"]=="LOSSLESS"
    assert a["reconstruction_contract"]["exact"]
    assert r["held_out_alphabet_check"]["loss_classification"]=="LOSSLESS"

def test_prime_and_composite_lanes_are_compared():
    r=run(R,default_workload(R,"T93:prime-composite"))
    assert r["prime_composite_comparison"]["prime_lanes"]>0
    assert r["prime_composite_comparison"]["composite_lanes"]>0

def test_noncommutative_history_remains_identity_bearing():
    r=run(R,default_workload(R,"T93:order"))
    c=[c for c in r["candidate_registry"] if c["candidate_id"]=="invariant:ordered-history"][0]
    assert "OPERATION_ORDER_SHUFFLE" in c["fails_under"]

def test_noise_results_preserve_lineage_and_are_non_authoritative():
    r=run(R,default_workload(R,"T93:noise"))
    assert r["noise_results"]
    assert all(x["lineage_preserved"] for x in r["noise_results"])
    assert all(not point["authority"] for x in r["noise_results"] for point in x["curve"])

def test_cross_domain_transfer_is_attempted_not_promoted():
    r=run(R,default_workload(R,"T93:transfer"))
    assert r["cross_domain_transfer"]["target"]=="VM81_ROUTING"
    assert r["authority"] is False

def test_replay_reproduces_pattern_registry():
    assert verify_replay(R,default_workload(R,"T93:replay"))["deterministic_replay_verified"]

def test_all_mandatory_negative_cases_pass():
    assert all(c["passed"] for c in negative_cases(R))

def test_registry_has_w93_01_through_w93_12():
    w=workload_registry(R)
    assert len(w)==12
    assert w[0]["workload_id"].startswith("W93-01")
    assert w[-1]["workload_id"].startswith("W93-12")

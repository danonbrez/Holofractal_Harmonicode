from hhs_backend.runtime.hhs_restart_safe_phase_gear_folding_v1 import (
    run_restart_safe_phase_gear_folding,
    restart_safe_phase_gear_folding_self_test,
    resume_from_checkpoint,
    write_checkpoint_atomic,
    load_checkpoint,
)


def test_self_test():
    assert restart_safe_phase_gear_folding_self_test()["ok"]


def test_overlap_buffer_preserves_complete_context():
    r = run_restart_safe_phase_gear_folding()
    assert r["overlap"]["context_capsule_complete"]
    assert not r["overlap"]["thread_context_required_for_resume"]
    assert not r["overlap"]["context_reset_permitted"]


def test_checkpoint_is_restart_safe_and_root_bound():
    r = run_restart_safe_phase_gear_folding()
    c = r["checkpoint"]
    assert c["restart_safe"]
    assert c["pass070_root_hash72"] == r["pass070_root_hash72"]
    assert c["next_stage"] == "COMPLETE"


def test_resume_after_simulated_hang_preserves_derivation():
    r = run_restart_safe_phase_gear_folding()
    receipt = resume_from_checkpoint(r["mid_checkpoint"])
    assert receipt["resumed"]
    assert receipt["resumed_without_thread_context"]
    assert not receipt["context_reset_occurred"]
    assert receipt["final_derivation_root_hash72"] == r["revalidation"]["derivation_root_hash72"]


def test_context_journal_is_append_only():
    r = run_restart_safe_phase_gear_folding()
    assert r["journal"]["append_only_verified"]
    assert r["journal"]["entry_count"] == 9


def test_symbolic_genome_retains_binary_source_identity():
    r = run_restart_safe_phase_gear_folding()
    assert r["genome"]["token_count"] == 32
    assert r["unfolding"]["binary_source_identity_recovered"]
    assert r["unfolding"]["switch_states_preserved"]


def test_phase_gear_folds_execute_all_three_lanes():
    r = run_restart_safe_phase_gear_folding()
    assert r["folds"]["all_paths_use_three_lanes"]
    assert all(f["plastic_lane"]["post_correction_residue"] == 0 for f in r["folds"]["folds"])
    assert all(f["zero_sum_lane"]["post_correction_residue"] == 0 for f in r["folds"]["folds"])


def test_folding_does_not_rewrite_source_sequence():
    r = run_restart_safe_phase_gear_folding()
    assert r["genome"]["source_sequence_immutable"]
    assert r["topology"]["source_sequence_preserved"]
    assert r["topology"]["topology_is_projection_not_source"]


def test_energy_bias_does_not_create_authority():
    r = run_restart_safe_phase_gear_folding()
    assert r["potential"]["potential_guides_search_not_authority"]
    assert all(not p["thermodynamic_bias_confers_authority"] for p in r["potential"]["records"])


def test_canonical_continuation_requires_revalidation():
    r = run_restart_safe_phase_gear_folding()
    assert r["revalidation"]["independent_revalidation_performed"]
    assert r["revalidation"]["canonical_continuation"]


def test_hash72_is_not_sha256_label():
    assert not run_restart_safe_phase_gear_folding()["sha256_labeled_hash72"]


def test_atomic_checkpoint_persistence(tmp_path):
    r = run_restart_safe_phase_gear_folding()
    path = tmp_path / "resume.json"
    receipt = write_checkpoint_atomic(path, r["mid_checkpoint"])
    loaded = load_checkpoint(path)
    assert receipt["written"]
    assert receipt["atomic_replace_used"]
    assert loaded["checkpoint_root_hash72"] == r["mid_checkpoint"]["checkpoint_root_hash72"]
    assert resume_from_checkpoint(loaded)["resumed"]

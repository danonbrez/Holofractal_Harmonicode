from hhs_backend.runtime.hhs_total_system_recursive_holographic_closure_v1 import (
    CLOSURE_DIMENSIONS,
    MAX_SUBSYSTEMS,
    evaluate_membership_authority_claim,
    make_reconstruction_dependency_index,
    reconstruct_selected_subsystems,
    resume_from_pass072_checkpoint,
    run_total_system_recursive_holographic_closure,
)


def test_pass072_is_derived_from_canonical_pass071_runtime():
    result = run_total_system_recursive_holographic_closure()
    assert result["pass_id"] == "PASS_072"
    assert result["parent_pass_id"] == "PASS_071"
    assert result["parent"]["canonical_continuation"] is True
    assert result["pass071_root_hash72"] == result["parent"]["run_root_hash72"]


def test_nine_source_bound_holographic_subsystem_capsules_exist():
    result = run_total_system_recursive_holographic_closure()
    capsules = result["capsules"]
    assert len(capsules) == MAX_SUBSYSTEMS == 9
    assert len({capsule["subsystem_id"] for capsule in capsules}) == 9
    assert all(capsule["source_root_hash72"] for capsule in capsules)
    assert all(capsule["capsule_root_hash72"] for capsule in capsules)
    assert all(capsule["semantic_payload_root_separate_from_membership_witness"] for capsule in capsules)


def test_total_system_root_is_executable_and_canonical():
    result = run_total_system_recursive_holographic_closure()
    root = result["total_root"]
    assert root["schema"] == "HHS_TOTAL_SYSTEM_ROOT_V1"
    assert root["subsystem_count"] == 9
    assert root["closure_dimension_count"] == 8
    assert root["qudit81_kernel_closed"] is True
    assert root["phase_gear_macro_loop_closed"] is True
    assert root["canonical_continuation"] is True
    assert result["total_system_root_hash72"] == root["total_system_root_hash72"]


def test_recursive_identity_paths_close_both_directions():
    result = run_total_system_recursive_holographic_closure()
    paths = result["identity_paths"]
    assert paths["path_count"] == 18
    assert paths["part_to_whole_path_count"] == 9
    assert paths["whole_to_part_path_count"] == 9
    assert paths["all_paths_identity_preserving"] is True
    assert result["part_to_whole_path"] is True
    assert result["whole_to_part_path"] is True


def test_reconstruction_dependency_index_is_acyclic_and_cycle_is_rejected():
    result = run_total_system_recursive_holographic_closure()
    index = result["dependency_index"]
    assert index["derivation_ancestry_acyclic"] is True
    assert len(index["topological_order"]) == 9
    cyclic = make_reconstruction_dependency_index(
        [
            {"subsystem_id": "A", "dependencies": ["B"]},
            {"subsystem_id": "B", "dependencies": ["A"]},
        ]
    )
    assert cyclic["derivation_ancestry_acyclic"] is False
    assert cyclic["status"] == "REJECT_DERIVATION_ANCESTRY_CYCLE"


def test_eight_closure_dimensions_have_independent_receipts():
    result = run_total_system_recursive_holographic_closure()
    registry = result["dimension_registry"]
    assert registry["dimensions"] == list(CLOSURE_DIMENSIONS)
    assert registry["independently_closed_count"] == 8
    assert registry["all_dimensions_closed"] is True
    assert all(receipt["evidence_count"] >= 1 for receipt in registry["receipts"])
    assert len({receipt["dimension_receipt_root_hash72"] for receipt in registry["receipts"]}) == 8


def test_bounded_partial_reconstruction_regenerates_selected_capsules_and_total_root():
    result = run_total_system_recursive_holographic_closure()
    receipt = result["partial_reconstruction"]
    assert receipt["selected_count"] == 4
    assert receipt["bounded"] is True
    assert receipt["all_selected_capsules_match"] is True
    assert receipt["reconstructed_root_matches_admitted_root"] is True
    assert receipt["status"] == "ADMIT_BOUNDED_PARTIAL_RECONSTRUCTION"


def test_full_nine_capsule_reconstruction_remains_bounded_and_matches():
    result = run_total_system_recursive_holographic_closure()
    all_ids = [capsule["subsystem_id"] for capsule in result["capsules"]]
    receipt = reconstruct_selected_subsystems(result, all_ids)
    assert receipt["selected_count"] == 9
    assert receipt["bounded"] is True
    assert receipt["all_selected_capsules_match"] is True
    assert receipt["reconstructed_root_matches_admitted_root"] is True


def test_membership_cannot_create_authority():
    admitted = evaluate_membership_authority_claim("QUDIT81_KERNEL", False)
    rejected = evaluate_membership_authority_claim("QUDIT81_KERNEL", True)
    assert admitted["status"] == "ADMIT_MEMBERSHIP_WITHOUT_AUTHORITY_TRANSFER"
    assert admitted["admitted"] is True
    assert rejected["status"] == "REJECT_MEMBERSHIP_AS_AUTHORITY"
    assert rejected["admitted"] is False
    assert rejected["membership_confers_authority"] is False


def test_phase_gear_pathfinder_and_81_cell_kernel_are_inside_total_root():
    result = run_total_system_recursive_holographic_closure()
    phase = result["phase_gear_pathfinder"]
    kernel = result["kernel"]
    root = result["total_root"]
    assert phase["holofractal_closure"] is True
    assert phase["local_periods"] == [4] * 9
    assert phase["total_rotation_steps"] == 36
    assert kernel["global_closure"] is True
    assert root["phase_gear_pathfinder_root_hash72"] == phase["run_root_hash72"]
    assert root["qudit81_lattice_root_hash72"] == kernel["lattice_root_hash72"]


def test_pass072_checkpoint_resumes_without_thread_context():
    result = run_total_system_recursive_holographic_closure()
    checkpoint = result["checkpoint"]
    resume = resume_from_pass072_checkpoint(checkpoint)
    assert checkpoint["pass_id"] == "PASS_072"
    assert checkpoint["completed_stage"] == "INDEPENDENT_REVALIDATION"
    assert checkpoint["next_stage"] == "COMPLETE"
    assert checkpoint["restart_safe"] is True
    assert checkpoint["thread_context_required"] is False
    assert resume["parent_root_matches"] is True
    assert resume["total_system_root_matches"] is True
    assert resume["resumed_without_thread_context"] is True
    assert resume["resumed"] is True


def test_pass072_root_and_canonical_continuation_are_deterministic():
    first = run_total_system_recursive_holographic_closure()
    root = first["run_root_hash72"]
    total_root = first["total_system_root_hash72"]
    run_total_system_recursive_holographic_closure.cache_clear()
    second = run_total_system_recursive_holographic_closure()
    assert second["run_root_hash72"] == root
    assert second["total_system_root_hash72"] == total_root
    assert second["canonical_continuation"] is True

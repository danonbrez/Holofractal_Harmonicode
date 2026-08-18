from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i117_pass207 import (
    PASS207_BIND_SYMBOL,
    REQUIRED_OPERATIONS,
    pass207_membrane_manifest,
    pass207_membrane_source_evidence,
    pass207_surface_declaration,
    preflight_pass207_membrane,
)


def main() -> None:
    source = pass207_membrane_source_evidence()
    assert source["main_merge_head"] == "b350afea4f7d5a45ba8b8b0bb9740e40731cdb97"
    assert source["validated_branch_head"] == "406eee3d68ec6c06017374085a46c9992d5778e3"
    assert source["branch_validation_run"] == 30915233211
    assert source["branch_validation_job"] == 92011562422
    assert source["contract"]["pass"] == 207
    assert source["successor_pass208"]["main_merge_head"] == "cbeabffff4e70db6207f8c349dd88ea8b7bd6ea9"

    declaration = pass207_surface_declaration()
    assert declaration["surface_id"] == "runtime:pass207.vm81-gpu-hyperthread-driver"
    assert declaration["symbol"] == "Pass207VM81GPURuntime"
    assert declaration["mutation_policy"] == "GPU_CANDIDATE_ONLY_SINGLETON_VM81_ADMISSION"
    assert declaration["persistence_policy"] == "NO_GPU_CANONICAL_PERSISTENCE"
    assert tuple(declaration["declared_operations"]) == REQUIRED_OPERATIONS
    assert PASS207_BIND_SYMBOL in declaration["validators"]

    manifest = pass207_membrane_manifest()
    assert manifest["pass_number"] == 207
    assert manifest["classification"] == "WIRED"
    assert manifest["vm81_cells"] == 81
    assert manifest["logical_hyperthreads_per_cell"] == 64
    assert manifest["logical_lanes_per_batch"] == 5184
    assert manifest["phase_dimension"] == 72
    assert manifest["projection_channels"] == 32
    assert manifest["stable_vm5184_lane_dispatch_bound"] is True
    assert manifest["lane_phase_bijection_bound"] is True
    assert manifest["ordered_cell_pack_bound"] is True
    assert manifest["ordered_hydration_bound"] is True
    assert manifest["exact_cpu_oracle_verification_bound"] is True
    assert manifest["content_keyed_cache_bound"] is True
    assert manifest["stable_vector_ranking_bound"] is True
    assert manifest["candidate_only_bound"] is True
    assert manifest["gpu_hash72_commit_forbidden"] is True
    assert manifest["gpu_canonical_mutation_forbidden"] is True
    assert manifest["gpu_vm81_bypass_forbidden"] is True
    assert manifest["pass205_singleton_vm81_admission_bound"] is True
    assert manifest["physical_gpu_fail_closed"] is True
    assert manifest["pass208_successor_bound"] is True
    assert manifest["pass219_new_canonical_mutation_authority"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["direct_gpu_vm81_mutation_authority"] is False
    assert manifest["next_pass_to_census"] == 206

    preflight = preflight_pass207_membrane()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(REQUIRED_OPERATIONS)
    assert all(row.get("ok") is True for row in preflight["operations"])


if __name__ == "__main__":
    main()

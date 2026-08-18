from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass208 import (
    PASS208_BIND_SYMBOL,
    REQUIRED_OPERATIONS,
    pass208_membrane_manifest,
    pass208_membrane_source_evidence,
    pass208_surface_declaration,
    preflight_pass208_membrane,
)


def main() -> None:
    source = pass208_membrane_source_evidence()
    assert source["main_merge_head"] == "cbeabffff4e70db6207f8c349dd88ea8b7bd6ea9"
    assert source["validated_branch_head"] == "6cc968b9f95d63e1a8701d32008969477caf894f"
    assert source["branch_validation_run"] == 30918852368
    assert source["branch_validation_job"] == 92023855007
    assert source["contract"]["pass"] == 208
    assert source["successor_pass209"]["main_merge_head"] == "c05cf860e4be5a0865813529baf9ad99e50dbe02"

    declaration = pass208_surface_declaration()
    assert declaration["surface_id"] == "runtime:pass208.gpu-branch-manifold"
    assert declaration["symbol"] == "Pass208GPUBranchManifold"
    assert declaration["mutation_policy"] == "GPU_CANDIDATE_ONLY_DELEGATED_SINGLETON_VM81_COMMIT"
    assert declaration["persistence_policy"] == "NO_GPU_CANONICAL_PERSISTENCE"
    assert tuple(declaration["declared_operations"]) == REQUIRED_OPERATIONS
    assert PASS208_BIND_SYMBOL in declaration["validators"]

    manifest = pass208_membrane_manifest()
    assert manifest["pass_number"] == 208
    assert manifest["classification"] == "WIRED"
    assert manifest["logical_lanes_per_branch"] == 5184
    assert manifest["json_spec_file_count"] == 23
    assert manifest["gpu_candidate_expansion_bound"] is True
    assert manifest["exact_cpu_oracle_verification_bound"] is True
    assert manifest["stable_integer_ranking_bound"] is True
    assert manifest["pass205_singleton_vm81_commit_path_bound"] is True
    assert manifest["gpu_hash72_commit_forbidden"] is True
    assert manifest["gpu_canonical_persistence_forbidden"] is True
    assert manifest["gpu_vm81_bypass_forbidden"] is True
    assert manifest["physical_gpu_fail_closed"] is True
    assert manifest["pass209_successor_bound"] is True
    assert manifest["pass219_new_canonical_mutation_authority"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["direct_gpu_vm81_mutation_authority"] is False
    assert manifest["next_pass_to_census"] == 207

    preflight = preflight_pass208_membrane()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(REQUIRED_OPERATIONS)
    assert all(row.get("ok") is True for row in preflight["operations"])


if __name__ == "__main__":
    main()

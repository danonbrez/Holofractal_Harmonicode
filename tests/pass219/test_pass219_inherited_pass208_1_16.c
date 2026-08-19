#include "hhs_pass219_inherited_pass208_1_16.h"

#include <assert.h>
#include <string.h>

static HHSExactPass208GPUBranchManifoldWitnessV1 witness(void) {
    HHSExactPass208GPUBranchManifoldWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass208_version();
    w.runtime_verified = 1U;
    w.logical_lanes_per_branch = 5184U;
    w.json_spec_file_count = 23U;
    w.minimum_example_count = 4U;
    w.required_operation_count = 6U;
    w.same_kernel_bytecode_hydration_lattice = 1U;
    w.same_parent_snapshot_required = 1U;
    w.same_constraint_root_required = 1U;
    w.same_hash216_lineage_required = 1U;
    w.same_hash72_commit_stream_required = 1U;
    w.branch_candidate_only = 1U;
    w.gpu_cpu_equality_required = 1U;
    w.stable_integer_ranking_bound = 1U;
    w.gpu_may_commit_hash72 = 0U;
    w.gpu_may_persist_canonical_snapshot = 0U;
    w.gpu_may_bypass_vm81 = 0U;
    w.cache_hit_authorizes_mutation = 0U;
    w.pass205_singleton_vm81_commit_authority_preserved = 1U;
    w.physical_gpu_fail_closed = 1U;
    w.pass209_inherits_pass208 = 1U;
    w.pass219_new_canonical_mutation_authority = 0U;
    w.cxx_mutation_authority = 0U;
    w.direct_gpu_vm81_mutation_authority = 0U;
    w.branch_validation_run = 30918852368ULL;
    w.branch_validation_job = 92023855007ULL;
    strcpy(w.validated_branch_head, "6cc968b9f95d63e1a8701d32008969477caf894f");
    strcpy(w.main_merge_head, "cbeabffff4e70db6207f8c349dd88ea8b7bd6ea9");
    strcpy(w.contract_git_blob, "b77413b816a32e61a3b1336b16bc6c4ecb0f4efa");
    strcpy(w.runtime_git_blob, "54e1e2089cdaeb4e3c613a5139c08cc226061afd");
    strcpy(w.routes_git_blob, "936bb542379db613805cd709482da7f1932c33e2");
    strcpy(w.restart_git_blob, "b3faee9ba0e666ff34cc1e3e0bd205788edca46b");
    strcpy(w.validation_workflow_git_blob, "41146f3d09fd95008cee0d5cf3a52bfb359c364d");
    strcpy(w.runtime_test_git_blob, "cd060b56ec8c505af67deaa3196e5c886502a416");
    strcpy(w.deployment_test_git_blob, "a593eeda7925a37c801b96627bb5e390183daa2e");
    strcpy(w.preflight_git_blob, "ae9e778b25f19e2263f975ef1edb9bc831684942");
    strcpy(w.spec_validator_git_blob, "78268251e20de4b8c896b7e58f192b557b92ec50");
    strcpy(w.pass209_main_merge_head, "c05cf860e4be5a0865813529baf9ad99e50dbe02");
    return w;
}

int main(void) {
    HHSExactPass208GPUBranchManifoldWitnessV1 w = witness();
    HHSExactPass219InheritedPass208BindingV1 b;
    assert(hhs_exact_pass219_bind_pass208_gpu_branch_manifold(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.pass_number == 208U);
    assert(b.gpu_candidate_expansion_bound == 1U);
    assert(b.exact_cpu_oracle_verification_bound == 1U);
    assert(b.stable_integer_ranking_bound == 1U);
    assert(b.pass205_singleton_vm81_commit_path_bound == 1U);
    assert(b.gpu_hash72_commit_forbidden == 1U);
    assert(b.gpu_canonical_persistence_forbidden == 1U);
    assert(b.gpu_vm81_bypass_forbidden == 1U);
    assert(b.physical_gpu_fail_closed == 1U);
    assert(b.pass209_successor_bound == 1U);
    assert(b.pass219_new_canonical_mutation_authority == 0U);
    assert(b.cxx_mutation_authority == 0U);
    assert(b.direct_gpu_vm81_mutation_authority == 0U);
    assert(b.logical_lanes_per_branch == 5184U);
    assert(b.json_spec_file_count == 23U);

    w.gpu_may_commit_hash72 = 1U;
    assert(hhs_exact_pass219_bind_pass208_gpu_branch_manifold(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.pass205_singleton_vm81_commit_authority_preserved = 0U;
    assert(hhs_exact_pass219_bind_pass208_gpu_branch_manifold(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.runtime_git_blob[0] = '0';
    assert(hhs_exact_pass219_bind_pass208_gpu_branch_manifold(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}

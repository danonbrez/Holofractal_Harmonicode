#include "../include/hhs_pass219_inherited_pass208_1_16.h"

#include <stddef.h>
#include <string.h>

static const char P208_VALIDATED_HEAD[] = "6cc968b9f95d63e1a8701d32008969477caf894f";
static const char P208_MAIN_MERGE[] = "cbeabffff4e70db6207f8c349dd88ea8b7bd6ea9";
static const char P208_CONTRACT_BLOB[] = "b77413b816a32e61a3b1336b16bc6c4ecb0f4efa";
static const char P208_RUNTIME_BLOB[] = "54e1e2089cdaeb4e3c613a5139c08cc226061afd";
static const char P208_ROUTES_BLOB[] = "936bb542379db613805cd709482da7f1932c33e2";
static const char P208_RESTART_BLOB[] = "b3faee9ba0e666ff34cc1e3e0bd205788edca46b";
static const char P208_WORKFLOW_BLOB[] = "41146f3d09fd95008cee0d5cf3a52bfb359c364d";
static const char P208_RUNTIME_TEST_BLOB[] = "cd060b56ec8c505af67deaa3196e5c886502a416";
static const char P208_DEPLOYMENT_TEST_BLOB[] = "a593eeda7925a37c801b96627bb5e390183daa2e";
static const char P208_PREFLIGHT_BLOB[] = "ae9e778b25f19e2263f975ef1edb9bc831684942";
static const char P208_SPEC_VALIDATOR_BLOB[] = "78268251e20de4b8c896b7e58f192b557b92ec50";
static const char P208_SUCCESSOR_P209_MAIN_MERGE[] = "c05cf860e4be5a0865813529baf9ad99e50dbe02";

static uint32_t p208_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS208_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS208_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS208_VERSION_PATCH;
}

static int p208_text(const char *value, size_t size, const char *expected, size_t expected_len) {
    return value != NULL && expected != NULL && size == expected_len + 1U &&
           value[expected_len] == '\0' && memcmp(value, expected, expected_len) == 0;
}

static int p208_git(
    const char value[HHS_EXACT_PASS208_GIT_SHA_STRLEN],
    const char expected[HHS_EXACT_PASS208_GIT_SHA_STRLEN]
) {
    return p208_text(value, HHS_EXACT_PASS208_GIT_SHA_STRLEN, expected, HHS_EXACT_PASS208_GIT_SHA_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass208_version(void) { return p208_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass208_gpu_branch_manifold(
    const HHSExactPass208GPUBranchManifoldWitnessV1 *witness,
    HHSExactPass219InheritedPass208BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p208_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (witness->runtime_verified != 1U ||
        witness->logical_lanes_per_branch != HHS_EXACT_PASS208_LOGICAL_LANES_PER_BRANCH ||
        witness->json_spec_file_count != HHS_EXACT_PASS208_JSON_SPEC_FILE_COUNT ||
        witness->minimum_example_count != HHS_EXACT_PASS208_MINIMUM_EXAMPLE_COUNT ||
        witness->required_operation_count != HHS_EXACT_PASS208_REQUIRED_OPERATION_COUNT ||
        witness->same_kernel_bytecode_hydration_lattice != 1U ||
        witness->same_parent_snapshot_required != 1U ||
        witness->same_constraint_root_required != 1U ||
        witness->same_hash216_lineage_required != 1U ||
        witness->same_hash72_commit_stream_required != 1U ||
        witness->branch_candidate_only != 1U ||
        witness->gpu_cpu_equality_required != 1U ||
        witness->stable_integer_ranking_bound != 1U ||
        witness->gpu_may_commit_hash72 != 0U ||
        witness->gpu_may_persist_canonical_snapshot != 0U ||
        witness->gpu_may_bypass_vm81 != 0U ||
        witness->cache_hit_authorizes_mutation != 0U ||
        witness->pass205_singleton_vm81_commit_authority_preserved != 1U ||
        witness->physical_gpu_fail_closed != 1U ||
        witness->pass209_inherits_pass208 != 1U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->direct_gpu_vm81_mutation_authority != 0U ||
        witness->branch_validation_run != 30918852368ULL ||
        witness->branch_validation_job != 92023855007ULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!p208_git(witness->validated_branch_head, P208_VALIDATED_HEAD) ||
        !p208_git(witness->main_merge_head, P208_MAIN_MERGE) ||
        !p208_git(witness->contract_git_blob, P208_CONTRACT_BLOB) ||
        !p208_git(witness->runtime_git_blob, P208_RUNTIME_BLOB) ||
        !p208_git(witness->routes_git_blob, P208_ROUTES_BLOB) ||
        !p208_git(witness->restart_git_blob, P208_RESTART_BLOB) ||
        !p208_git(witness->validation_workflow_git_blob, P208_WORKFLOW_BLOB) ||
        !p208_git(witness->runtime_test_git_blob, P208_RUNTIME_TEST_BLOB) ||
        !p208_git(witness->deployment_test_git_blob, P208_DEPLOYMENT_TEST_BLOB) ||
        !p208_git(witness->preflight_git_blob, P208_PREFLIGHT_BLOB) ||
        !p208_git(witness->spec_validator_git_blob, P208_SPEC_VALIDATOR_BLOB) ||
        !p208_git(witness->pass209_main_merge_head, P208_SUCCESSOR_P209_MAIN_MERGE))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p208_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS208_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->gpu_candidate_expansion_bound = 1U;
    out_binding->exact_cpu_oracle_verification_bound = 1U;
    out_binding->stable_integer_ranking_bound = 1U;
    out_binding->pass205_singleton_vm81_commit_path_bound = 1U;
    out_binding->gpu_hash72_commit_forbidden = 1U;
    out_binding->gpu_canonical_persistence_forbidden = 1U;
    out_binding->gpu_vm81_bypass_forbidden = 1U;
    out_binding->physical_gpu_fail_closed = 1U;
    out_binding->pass209_successor_bound = 1U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->direct_gpu_vm81_mutation_authority = 0U;
    out_binding->logical_lanes_per_branch = witness->logical_lanes_per_branch;
    out_binding->json_spec_file_count = witness->json_spec_file_count;
    memcpy(out_binding->main_merge_head, witness->main_merge_head, HHS_EXACT_PASS208_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

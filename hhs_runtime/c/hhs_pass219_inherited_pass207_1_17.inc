#include "../include/hhs_pass219_inherited_pass207_1_17.h"

#include <stddef.h>
#include <string.h>

static const char P207_VALIDATED_HEAD[] = "406eee3d68ec6c06017374085a46c9992d5778e3";
static const char P207_MAIN_MERGE[] = "b350afea4f7d5a45ba8b8b0bb9740e40731cdb97";
static const char P207_CONTRACT_BLOB[] = "727660f3b48c87a78d7e274a5b71ded1bf6e4910";
static const char P207_MANIFEST_BLOB[] = "2f8bb40210b77430a3e6861338d99d06b2ab5596";
static const char P207_DRIVER_HEADER_BLOB[] = "d73b80f53f8843a8c015ebdd735ee419f0877ae0";
static const char P207_DRIVER_SOURCE_BLOB[] = "d812005e5be19383472193a7a9cdc50efbe96277";
static const char P207_DRIVER_PART1_BLOB[] = "97bef9b58357f44e4801b35de1cda2fea3a726d3";
static const char P207_DRIVER_PART2_BLOB[] = "ca8245293cfecc2d73afc063af512e7ff6322a02";
static const char P207_DRIVER_PART3_BLOB[] = "c76665697aa3417a1cc8789c794dcebf0219c282";
static const char P207_DRIVER_PART4_BLOB[] = "85f8acf834487ff6dc6fa062bebc509b2ab526b7";
static const char P207_DRIVER_PART5_BLOB[] = "dbc87a68e0ecdccceb37bb0f6f99bd9491489a0b";
static const char P207_NATIVE_BRIDGE_BLOB[] = "f66249e67b6a70b2e5d6bdd42e57e814043fe4d1";
static const char P207_PYTHON_BRIDGE_BLOB[] = "53e409665471f126925e6119f9f20ead3978766b";
static const char P207_RUNTIME_BLOB[] = "66a1f25489cde4748fe034bb4b050aef74942a49";
static const char P207_RESTART_BLOB[] = "af3c4d8ec508de5f5e99431df22ed65f58021205";
static const char P207_WORKFLOW_BLOB[] = "5f6ff36b68cf02ec43b6a65b0493afbb56cee7d4";
static const char P207_NATIVE_TEST_BLOB[] = "326546d25004e5789a526ac83aadb22b17b57c7d";
static const char P207_PYTHON_TEST_BLOB[] = "88ad4fec4f883f284858d4850e429245438fe98d";
static const char P207_SUCCESSOR_P208_MAIN_MERGE[] = "cbeabffff4e70db6207f8c349dd88ea8b7bd6ea9";

static uint32_t p207_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS207_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS207_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS207_VERSION_PATCH;
}

static int p207_text(const char *value, size_t size, const char *expected, size_t expected_len) {
    return value != NULL && expected != NULL && size == expected_len + 1U &&
           value[expected_len] == '\0' && memcmp(value, expected, expected_len) == 0;
}

static int p207_git(
    const char value[HHS_EXACT_PASS207_GIT_SHA_STRLEN],
    const char expected[HHS_EXACT_PASS207_GIT_SHA_STRLEN]
) {
    return p207_text(value, HHS_EXACT_PASS207_GIT_SHA_STRLEN, expected, HHS_EXACT_PASS207_GIT_SHA_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass207_version(void) { return p207_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass207_gpu_hyperthread_driver(
    const HHSExactPass207GPUHyperthreadWitnessV1 *witness,
    HHSExactPass219InheritedPass207BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p207_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (witness->runtime_verified != 1U ||
        witness->vm81_cells != HHS_EXACT_PASS207_VM81_CELLS ||
        witness->logical_hyperthreads_per_cell != HHS_EXACT_PASS207_LOGICAL_HYPERTHREADS_PER_CELL ||
        witness->logical_lanes_per_batch != HHS_EXACT_PASS207_LOGICAL_LANES_PER_BATCH ||
        witness->phase_dimension != HHS_EXACT_PASS207_PHASE_DIMENSION ||
        witness->projection_channels != HHS_EXACT_PASS207_PROJECTION_CHANNELS ||
        witness->required_operation_count != HHS_EXACT_PASS207_REQUIRED_OPERATION_COUNT ||
        witness->stable_lane_identity != 1U ||
        witness->lane_phase_bijection_bound != 1U ||
        witness->disjoint_lane_writes != 1U ||
        witness->ordered_cell_pack_bound != 1U ||
        witness->ordered_projection_bound != 1U ||
        witness->ordered_hydration_bound != 1U ||
        witness->exact_cpu_oracle_equality_required != 1U ||
        witness->candidate_only != 1U ||
        witness->buffer_cache_content_keyed != 1U ||
        witness->cache_hit_authorizes_mutation != 0U ||
        witness->stable_vector_ranking_bound != 1U ||
        witness->gpu_may_commit_hash72 != 0U ||
        witness->gpu_may_mutate_canonical_state != 0U ||
        witness->gpu_may_bypass_vm81 != 0U ||
        witness->parallel_canonical_authorities_allowed != 0U ||
        witness->physical_completion_order_noncanonical != 1U ||
        witness->physical_gpu_fail_closed != 1U ||
        witness->pass205_singleton_vm81_admission_preserved != 1U ||
        witness->pass208_inherits_pass207 != 1U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->direct_gpu_vm81_mutation_authority != 0U ||
        witness->branch_validation_run != 30915233211ULL ||
        witness->branch_validation_job != 92011562422ULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p207_git(witness->validated_branch_head, P207_VALIDATED_HEAD) ||
        !p207_git(witness->main_merge_head, P207_MAIN_MERGE) ||
        !p207_git(witness->contract_git_blob, P207_CONTRACT_BLOB) ||
        !p207_git(witness->manifest_git_blob, P207_MANIFEST_BLOB) ||
        !p207_git(witness->driver_header_git_blob, P207_DRIVER_HEADER_BLOB) ||
        !p207_git(witness->driver_source_git_blob, P207_DRIVER_SOURCE_BLOB) ||
        !p207_git(witness->driver_part1_git_blob, P207_DRIVER_PART1_BLOB) ||
        !p207_git(witness->driver_part2_git_blob, P207_DRIVER_PART2_BLOB) ||
        !p207_git(witness->driver_part3_git_blob, P207_DRIVER_PART3_BLOB) ||
        !p207_git(witness->driver_part4_git_blob, P207_DRIVER_PART4_BLOB) ||
        !p207_git(witness->driver_part5_git_blob, P207_DRIVER_PART5_BLOB) ||
        !p207_git(witness->native_bridge_git_blob, P207_NATIVE_BRIDGE_BLOB) ||
        !p207_git(witness->python_bridge_git_blob, P207_PYTHON_BRIDGE_BLOB) ||
        !p207_git(witness->runtime_git_blob, P207_RUNTIME_BLOB) ||
        !p207_git(witness->restart_git_blob, P207_RESTART_BLOB) ||
        !p207_git(witness->validation_workflow_git_blob, P207_WORKFLOW_BLOB) ||
        !p207_git(witness->native_test_git_blob, P207_NATIVE_TEST_BLOB) ||
        !p207_git(witness->python_test_git_blob, P207_PYTHON_TEST_BLOB) ||
        !p207_git(witness->pass208_main_merge_head, P207_SUCCESSOR_P208_MAIN_MERGE))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p207_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS207_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->stable_vm5184_lane_dispatch_bound = 1U;
    out_binding->lane_phase_bijection_bound = 1U;
    out_binding->ordered_cell_pack_bound = 1U;
    out_binding->ordered_hydration_bound = 1U;
    out_binding->exact_cpu_oracle_verification_bound = 1U;
    out_binding->content_keyed_cache_bound = 1U;
    out_binding->stable_vector_ranking_bound = 1U;
    out_binding->candidate_only_bound = 1U;
    out_binding->gpu_hash72_commit_forbidden = 1U;
    out_binding->gpu_canonical_mutation_forbidden = 1U;
    out_binding->gpu_vm81_bypass_forbidden = 1U;
    out_binding->pass205_singleton_vm81_admission_bound = 1U;
    out_binding->physical_gpu_fail_closed = 1U;
    out_binding->pass208_successor_bound = 1U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->direct_gpu_vm81_mutation_authority = 0U;
    out_binding->logical_lanes_per_batch = witness->logical_lanes_per_batch;
    out_binding->projection_channels = witness->projection_channels;
    memcpy(out_binding->main_merge_head, witness->main_merge_head, HHS_EXACT_PASS207_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

#include "../include/hhs_pass219_inherited_pass206_1_18.h"

#include <stddef.h>
#include <string.h>

static const char P206_BASELINE[] = "918121aeb6d1c55aa8fbd5d60b15f03c4eb22423";
static const char P206_PREDECESSOR[] = "2fe770d68f6e1da172d2c7992a90e31d69577b90";
static const char P206_FREEZE_HEAD[] = "84e057047e6c3da8753ea500a88193f769e49cca";
static const char P206_COMPLETION_HEAD[] = "16d17c1db690116fdc5f5b63ef7a097548685885";
static const char P206_REPAIR_MERGE[] = "284bf652d9635cc0c940f79dfe6aff6f8b787c3c";
static const char P206_FREEZE_SHA256[] = "d60f6191c3fd77d8255e629dc73a7050d4093fe94845ff1bc63bd81d2dfa6da2";
static const char P206_REPAIR_SHA256[] = "29d0fa640d9a75b6520738826df3e17b769fc4129db4771c8720b7039b4f3440";
static const char P206_PRE_MATRIX_SHA256[] = "1f4da9ca815d99f76c30e26076435cc277c3912ce1658cb5ddb6876f5358406b";
static const char P206_RECEIPT_SHA256[] = "c25d3db3f6d20aef54092d4fda7663370ec855e8841df691b7ef1bf6d9db2c24";
static const char P206_POST_MATRIX_SHA256[] = "ec6aaaeb917abb0bc1f8c1c54e2c721b175e841b603094eb6e687751bb6b79df";

static uint32_t p206_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS206_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS206_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS206_VERSION_PATCH;
}

static int p206_text(const char *value, size_t size, const char *expected, size_t expected_len) {
    return value != NULL && expected != NULL && size == expected_len + 1U &&
           value[expected_len] == '\0' && memcmp(value, expected, expected_len) == 0;
}

static int p206_git(const char value[HHS_EXACT_PASS206_GIT_SHA_STRLEN], const char *expected) {
    return p206_text(value, HHS_EXACT_PASS206_GIT_SHA_STRLEN, expected, HHS_EXACT_PASS206_GIT_SHA_LEN);
}

static int p206_sha256(const char value[HHS_EXACT_PASS206_SHA256_STRLEN], const char *expected) {
    return p206_text(value, HHS_EXACT_PASS206_SHA256_STRLEN, expected, HHS_EXACT_PASS206_SHA256_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass206_version(void) { return p206_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass206_cumulative_enforcement(
    const HHSExactPass206CumulativeEnforcementWitnessV1 *witness,
    HHSExactPass219InheritedPass206BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p206_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->enforcement_admitted != 1U ||
        witness->frozen_core_count != HHS_EXACT_PASS206_FROZEN_CORE_COUNT ||
        witness->approved_successor_count != HHS_EXACT_PASS206_APPROVED_SUCCESSOR_COUNT ||
        witness->canonical_mutation_authority_count != HHS_EXACT_PASS206_CANONICAL_MUTATION_AUTHORITY_COUNT ||
        witness->canonical_hash72_commit_stream_count != HHS_EXACT_PASS206_CANONICAL_HASH72_STREAM_COUNT ||
        witness->development_implementation_complete != 1U ||
        witness->development_final_replay_complete != 1U ||
        witness->development_completion_receipt_emitted != 1U ||
        witness->ready_for_pass219_inherited_membrane != 1U ||
        witness->canonical_main_verified != 0U ||
        witness->canonical_main_promotion_authorized != 0U ||
        witness->canonical_completion_claimed != 0U ||
        witness->pass207_successor_preserved != 1U ||
        witness->pass206_new_mutation_authority != 0U ||
        witness->pass206_new_persistence_authority != 0U ||
        witness->pass206_new_hash72_clock != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U ||
        witness->dependency_validation_run != 32176768793ULL ||
        witness->dependency_validation_exact_job != 95840408861ULL ||
        witness->dependency_validation_synthetic_job != 95840408810ULL ||
        witness->final_replay_pass206_run != 32177179707ULL ||
        witness->final_replay_pass206_exact_job != 95841688861ULL ||
        witness->final_replay_pass206_synthetic_job != 95841688933ULL ||
        witness->final_replay_cumulative_run != 32177179709ULL ||
        witness->final_replay_cumulative_exact_job != 95841688968ULL ||
        witness->final_replay_cumulative_synthetic_job != 95841688796ULL ||
        witness->completion_validation_run != 32178471795ULL ||
        witness->completion_validation_exact_job != 95845723288ULL ||
        witness->completion_validation_synthetic_job != 95845723004ULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p206_git(witness->grounding_baseline, P206_BASELINE) ||
        !p206_git(witness->sealed_predecessor, P206_PREDECESSOR) ||
        !p206_git(witness->freeze_checkpoint, P206_FREEZE_HEAD) ||
        !p206_git(witness->development_completion_head, P206_COMPLETION_HEAD) ||
        !p206_git(witness->approved_repair_merge, P206_REPAIR_MERGE) ||
        !p206_sha256(witness->freeze_manifest_sha256, P206_FREEZE_SHA256) ||
        !p206_sha256(witness->approved_repair_lineage_sha256, P206_REPAIR_SHA256) ||
        !p206_sha256(witness->pre_receipt_matrix_sha256, P206_PRE_MATRIX_SHA256) ||
        !p206_sha256(witness->completion_receipt_sha256, P206_RECEIPT_SHA256) ||
        !p206_sha256(witness->post_receipt_matrix_sha256, P206_POST_MATRIX_SHA256))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p206_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS206_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->frozen_core_count = witness->frozen_core_count;
    out_binding->approved_successor_count = witness->approved_successor_count;
    out_binding->single_vm81_authority_bound = 1U;
    out_binding->single_hash72_stream_bound = 1U;
    out_binding->enforcement_admitted_bound = 1U;
    out_binding->development_completion_bound = 1U;
    out_binding->canonical_main_pending_bound = 1U;
    out_binding->pass207_successor_bound = 1U;
    out_binding->no_new_mutation_authority_bound = 1U;
    out_binding->no_new_persistence_authority_bound = 1U;
    out_binding->no_new_hash72_clock_bound = 1U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->development_completion_head, witness->development_completion_head, HHS_EXACT_PASS206_GIT_SHA_STRLEN);
    memcpy(out_binding->completion_receipt_sha256, witness->completion_receipt_sha256, HHS_EXACT_PASS206_SHA256_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

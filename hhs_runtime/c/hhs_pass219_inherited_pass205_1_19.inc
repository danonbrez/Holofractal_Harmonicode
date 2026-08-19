#include "../include/hhs_pass219_inherited_pass205_1_19.h"

#include <stddef.h>
#include <string.h>

static const char P205_GROUNDING_BASELINE[] = "918121aeb6d1c55aa8fbd5d60b15f03c4eb22423";
static const char P205_IMPLEMENTATION_MERGE[] = "7be753b36d5b4c7a370b6435ddb027b6b05965d8";
static const char P205_CLOSURE_MERGE[] = "c717ab9e0437e1f407bbd3b22ed1fdd14bcd29b6";
static const char P205_COMPLETION_EVIDENCE_MERGE[] = "8e6cded890b86e36a2acd2162acf91d1cb4331ac";
static const char P205_COMPLETION_EVIDENCE_HEAD[] = "97f4e6a3828bd7fb85ad3cf9c2617c3ec99264e7";
static const char P205_CANDIDATE_MERGE_TREE[] = "73e3b87d162cfc73a9d6967a153a7cbb17b96e0d";
static const char P205_COMPLETION_RECEIPT_BLOB[] = "7884f6a2b00f1c2254fef5fdf87edca94ac5c6aa";
static const char P205_TERMINAL_RECEIPT_HASH72[] = "87rndLmp6DJW!?V9S7ZZcP6xft4GX+(FCMTve!L(BNDEr4v>OoT/HV<RLeqQ4J9P64>HI8N4";

static uint32_t p205_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS205_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS205_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS205_VERSION_PATCH;
}

static int p205_text(const char *value, size_t size, const char *expected, size_t expected_len) {
    return value != NULL && expected != NULL && size == expected_len + 1U &&
           value[expected_len] == '\0' && memcmp(value, expected, expected_len) == 0;
}

static int p205_git(const char value[HHS_EXACT_PASS205_GIT_SHA_STRLEN], const char *expected) {
    return p205_text(value, HHS_EXACT_PASS205_GIT_SHA_STRLEN, expected, HHS_EXACT_PASS205_GIT_SHA_LEN);
}

static int p205_hash72(const char value[HHS_EXACT_PASS205_HASH72_STRLEN], const char *expected) {
    return p205_text(value, HHS_EXACT_PASS205_HASH72_STRLEN, expected, HHS_EXACT_PASS205_HASH72_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass205_version(void) { return p205_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass205_deterministic_continuation(
    const HHSExactPass205DeterministicContinuationWitnessV1 *witness,
    HHSExactPass219InheritedPass205BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p205_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->production_verified != 1U ||
        witness->cell_count != HHS_EXACT_PASS205_CELL_COUNT ||
        witness->bits_per_cell != HHS_EXACT_PASS205_BITS_PER_CELL ||
        witness->state_bits != HHS_EXACT_PASS205_STATE_BITS ||
        witness->control_count != HHS_EXACT_PASS205_CONTROL_COUNT ||
        witness->q_address_count != HHS_EXACT_PASS205_Q_ADDRESS_COUNT ||
        witness->projection_channel_count != HHS_EXACT_PASS205_PROJECTION_CHANNEL_COUNT ||
        witness->canonical_mutation_authority_count != HHS_EXACT_PASS205_CANONICAL_MUTATION_AUTHORITY_COUNT ||
        witness->canonical_hash72_commit_stream_count != HHS_EXACT_PASS205_CANONICAL_HASH72_STREAM_COUNT ||
        witness->q_bijection_complete != 1U ||
        witness->sparse_full_equivalence_verified != 1U ||
        witness->parent_bound_hash216_lineage != 1U ||
        witness->retrieval_exact_rerank != 1U ||
        witness->accelerator_candidate_only != 1U ||
        witness->accelerator_may_commit_hash72 != 0U ||
        witness->physical_gpu_execution_claimed != 0U ||
        witness->canonical_float_fields != 0U ||
        witness->pass206_successor_preserved != 1U ||
        witness->pass205_new_mutation_authority != 0U ||
        witness->pass205_new_persistence_authority != 0U ||
        witness->pass205_new_hash72_clock != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U ||
        witness->implementation_pull_request != 149U ||
        witness->closure_pull_request != 150U ||
        witness->completion_evidence_pull_request != 151U ||
        witness->ordered_chain_generations != 73U ||
        witness->stored_snapshots != 77U ||
        witness->lineage_edges != 76U ||
        witness->closure_workflow_run != 30837753796ULL ||
        witness->closure_validation_job != 91766983285ULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p205_git(witness->grounding_baseline, P205_GROUNDING_BASELINE) ||
        !p205_git(witness->implementation_merge, P205_IMPLEMENTATION_MERGE) ||
        !p205_git(witness->closure_merge, P205_CLOSURE_MERGE) ||
        !p205_git(witness->completion_evidence_merge, P205_COMPLETION_EVIDENCE_MERGE) ||
        !p205_git(witness->completion_evidence_head, P205_COMPLETION_EVIDENCE_HEAD) ||
        !p205_git(witness->candidate_merge_tree, P205_CANDIDATE_MERGE_TREE) ||
        !p205_git(witness->completion_receipt_blob, P205_COMPLETION_RECEIPT_BLOB) ||
        !p205_hash72(witness->terminal_receipt_hash72, P205_TERMINAL_RECEIPT_HASH72))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p205_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS205_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->vm5184_state_bound = 1U;
    out_binding->g243_control_bound = 1U;
    out_binding->q_bijection_bound = 1U;
    out_binding->projection_channels_bound = 1U;
    out_binding->single_vm81_authority_bound = 1U;
    out_binding->single_hash72_stream_bound = 1U;
    out_binding->hash216_lineage_bound = 1U;
    out_binding->exact_sparse_full_equivalence_bound = 1U;
    out_binding->exact_retrieval_rerank_bound = 1U;
    out_binding->accelerator_candidate_only_bound = 1U;
    out_binding->pass206_successor_bound = 1U;
    out_binding->no_new_mutation_authority_bound = 1U;
    out_binding->no_new_persistence_authority_bound = 1U;
    out_binding->no_new_hash72_clock_bound = 1U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->closure_merge, witness->closure_merge, HHS_EXACT_PASS205_GIT_SHA_STRLEN);
    memcpy(out_binding->completion_receipt_blob, witness->completion_receipt_blob, HHS_EXACT_PASS205_GIT_SHA_STRLEN);
    memcpy(out_binding->terminal_receipt_hash72, witness->terminal_receipt_hash72, HHS_EXACT_PASS205_HASH72_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

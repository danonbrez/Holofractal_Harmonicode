#include "../include/hhs_pass219_inherited_pass215_1_16.h"

#include <stddef.h>
#include <string.h>

static const uint32_t HHS_EXACT_PASS215_SELECTED_TOKEN_IDS[HHS_EXACT_PASS215_SELECTED_TOKEN_COUNT] = {
    450U, 6575U, 471U, 528U, 2827U, 322U, 278U
};
static const char HHS_EXACT_PASS215_FINAL_HEAD[] =
    "b85ea7c340976a20a78f9c7d8d89a688a1b4f8fc";
static const char HHS_EXACT_PASS215_FINAL_TREE[] =
    "17127e80a3f4852aeaedd1b807971fb4b4fba229";
static const char HHS_EXACT_PASS215_MAIN_MERGE[] =
    "cc7a0d67d7d9e4bd1e800f62d5ef577cb4ab1086";
static const char HHS_EXACT_PASS215_ARTIFACT_SHA256[] =
    "9e71ff3f48cd4da24c34854f8eadfa57f26d7c6ef5bddd1026c89e2ace63bf55";
static const char HHS_EXACT_PASS215_MODEL_SHA256[] =
    "6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04";
static const char HHS_EXACT_PASS215_EARLIER_CHECKPOINT_ROOT[] =
    "151113337a143adb29eecfa9cb1f4df41b6458953afb2c5258b97dff5f3643b4";
static const char HHS_EXACT_PASS215_LATER_CHECKPOINT_ROOT[] =
    "bff3f18e1324caacdbd610b833b3ebd6ebe35e525821c0ffad349fc81ad9474f";
static const char HHS_EXACT_PASS215_SHARED_CONTENT_STORE_ROOT[] =
    "b7a9eb1678f263f20c5b61c0d9d3f01b76b152e2786b7e887ecb8265cbe454da";
static const char HHS_EXACT_PASS215_SHARED_CHECKPOINT_BUNDLE_ROOT[] =
    "14953737a095ee9365386e436706cedd7a77328a04eb4dc3d5e45935cd367c8a";
static const char HHS_EXACT_PASS215_SEQUENTIAL_REUSE_ROOT[] =
    "52980a2e4b7890d136e549a4812dd859cc75e0ea4f442872dc99392e261ed7c0";
static const char HHS_EXACT_PASS215_TERMINAL_COMPLETION_ROOT[] =
    "3dfb034753309c5f45f56f9bec5bf2178b1eb74974264cc306e46c8d6551f76a";
static const char HHS_EXACT_PASS215_SUITE_ROOT[] =
    "3be955aecac999e945cdf48df63e0be13d2c353de8e20c6869a2364c2ba72234";
static const char HHS_EXACT_PASS215_EVIDENCE_ROOT[] =
    "5a8a17e10b1dc10db2912bc2df40aa67306fc520439716eab47596dc1e8aac1e";
static const char HHS_EXACT_PASS215_RECEIPT_HASH72[] =
    "rimw6Mf!E(*xCD5DK1/WGTK)*WRAl<RWjBQyi!qSI+rXW>H0L9AtWuu/3Cs5HKZ!B)JCwUTM";

static uint32_t hhs_exact_pass219_inherited_pass215_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS215_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS215_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS215_VERSION_PATCH;
}

static int hhs_exact_pass215_exact_text(
    const char *value,
    size_t value_size,
    const char *expected,
    size_t expected_length
) {
    if (value == NULL || expected == NULL || value_size != expected_length + 1U)
        return 0;
    if (value[expected_length] != '\0')
        return 0;
    return memcmp(value, expected, expected_length) == 0;
}

static int hhs_exact_pass215_exact_git_sha(
    const char value[HHS_EXACT_PASS215_GIT_SHA_STRLEN],
    const char expected[HHS_EXACT_PASS215_GIT_SHA_STRLEN]
) {
    return hhs_exact_pass215_exact_text(
        value,
        HHS_EXACT_PASS215_GIT_SHA_STRLEN,
        expected,
        HHS_EXACT_PASS215_GIT_SHA_LEN);
}

static int hhs_exact_pass215_exact_sha256(
    const char value[HHS_EXACT_PASS215_SHA256_HEX_STRLEN],
    const char expected[HHS_EXACT_PASS215_SHA256_HEX_STRLEN]
) {
    return hhs_exact_pass215_exact_text(
        value,
        HHS_EXACT_PASS215_SHA256_HEX_STRLEN,
        expected,
        HHS_EXACT_PASS215_SHA256_HEX_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass215_version(void) {
    return hhs_exact_pass219_inherited_pass215_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass215_terminal_closure(
    const HHSExactPass215TerminalClosureWitnessV1 *witness,
    HHSExactPass219InheritedPass215BindingV1 *out_binding
) {
    size_t index;
    if (witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != hhs_exact_pass219_inherited_pass215_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->cumulative_test_count != 240U ||
        witness->selected_token_count != HHS_EXACT_PASS215_SELECTED_TOKEN_COUNT ||
        witness->terminal_iteration != 20U ||
        witness->contracted_benchmark_complete != 1U ||
        witness->bounded_profile_only != 1U ||
        witness->broader_generation_authority_promoted != 0U ||
        witness->output_projection_pruning_executed != 0U ||
        witness->candidates_pruned != 0U ||
        witness->probabilistic_sampling_executed != 0U ||
        witness->canonical_float_interpretation_performed != 0U ||
        witness->transport_compression_numerical_authority != 0U ||
        witness->runtime_mutation_authority_promoted != 0U ||
        witness->canonical_mutation_authorized != 0U ||
        witness->cross_process_replay != 1U ||
        witness->semantic_exactness != 1U ||
        witness->earlier_restore_prefix_forward_replays != 0U ||
        witness->earlier_restore_generated_forward_replays != 0U ||
        witness->later_restore_prefix_forward_replays != 0U ||
        witness->later_restore_generated_forward_replays != 0U ||
        witness->reused_unique_chunk_count != 36U ||
        witness->reused_compressed_blob_bytes != 28375966ULL ||
        witness->incremental_later_compressed_blob_bytes != 125510422ULL ||
        witness->later_standalone_compressed_blob_bytes != 153886388ULL ||
        witness->shared_store_savings_bytes != 28375966ULL ||
        witness->validation_run != 31325831364ULL ||
        witness->validation_job != 93275935886ULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (index = 0U; index < HHS_EXACT_PASS215_SELECTED_TOKEN_COUNT; ++index) {
        if (witness->selected_token_ids[index] != HHS_EXACT_PASS215_SELECTED_TOKEN_IDS[index])
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (!hhs_exact_pass215_exact_git_sha(witness->final_head, HHS_EXACT_PASS215_FINAL_HEAD) ||
        !hhs_exact_pass215_exact_git_sha(witness->final_tree, HHS_EXACT_PASS215_FINAL_TREE) ||
        !hhs_exact_pass215_exact_git_sha(witness->main_merge, HHS_EXACT_PASS215_MAIN_MERGE) ||
        !hhs_exact_pass215_exact_sha256(witness->artifact_sha256, HHS_EXACT_PASS215_ARTIFACT_SHA256) ||
        !hhs_exact_pass215_exact_sha256(witness->model_sha256, HHS_EXACT_PASS215_MODEL_SHA256) ||
        !hhs_exact_pass215_exact_sha256(witness->earlier_checkpoint_root_hash216, HHS_EXACT_PASS215_EARLIER_CHECKPOINT_ROOT) ||
        !hhs_exact_pass215_exact_sha256(witness->later_checkpoint_root_hash216, HHS_EXACT_PASS215_LATER_CHECKPOINT_ROOT) ||
        !hhs_exact_pass215_exact_sha256(witness->shared_content_store_root_hash216, HHS_EXACT_PASS215_SHARED_CONTENT_STORE_ROOT) ||
        !hhs_exact_pass215_exact_sha256(witness->shared_checkpoint_bundle_root_hash216, HHS_EXACT_PASS215_SHARED_CHECKPOINT_BUNDLE_ROOT) ||
        !hhs_exact_pass215_exact_sha256(witness->sequential_checkpoint_reuse_root_hash216, HHS_EXACT_PASS215_SEQUENTIAL_REUSE_ROOT) ||
        !hhs_exact_pass215_exact_sha256(witness->terminal_completion_root_hash216, HHS_EXACT_PASS215_TERMINAL_COMPLETION_ROOT) ||
        !hhs_exact_pass215_exact_sha256(witness->suite_root_hash216, HHS_EXACT_PASS215_SUITE_ROOT) ||
        !hhs_exact_pass215_exact_sha256(witness->evidence_root_hash216, HHS_EXACT_PASS215_EVIDENCE_ROOT) ||
        !hhs_exact_pass215_exact_text(witness->receipt_hash72,
                                      HHS_EXACT_PASS215_HASH72_STRLEN,
                                      HHS_EXACT_PASS215_RECEIPT_HASH72,
                                      HHS_EXACT_HASH72_LEN))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = hhs_exact_pass219_inherited_pass215_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS215_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->terminal_closure_bound = 1U;
    out_binding->exact_checkpoint_reuse_bound = 1U;
    out_binding->strict_argmax_chain_bound = 1U;
    out_binding->zero_restore_replay_bound = 1U;
    out_binding->bounded_profile_only = 1U;
    out_binding->broader_generation_authority_promoted = 0U;
    out_binding->output_projection_pruning_executed = 0U;
    out_binding->probabilistic_sampling_executed = 0U;
    out_binding->floating_point_canonical_authority = 0U;
    out_binding->transport_compression_numerical_authority = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    out_binding->canonical_mutation_authorized = 0U;
    out_binding->cumulative_test_count = witness->cumulative_test_count;
    memcpy(out_binding->final_head, witness->final_head, HHS_EXACT_PASS215_GIT_SHA_STRLEN);
    memcpy(out_binding->final_tree, witness->final_tree, HHS_EXACT_PASS215_GIT_SHA_STRLEN);
    memcpy(out_binding->main_merge, witness->main_merge, HHS_EXACT_PASS215_GIT_SHA_STRLEN);
    memcpy(out_binding->artifact_sha256, witness->artifact_sha256, HHS_EXACT_PASS215_SHA256_HEX_STRLEN);
    memcpy(out_binding->terminal_completion_root_hash216,
           witness->terminal_completion_root_hash216,
           HHS_EXACT_PASS215_SHA256_HEX_STRLEN);
    memcpy(out_binding->evidence_root_hash216,
           witness->evidence_root_hash216,
           HHS_EXACT_PASS215_SHA256_HEX_STRLEN);
    memcpy(out_binding->receipt_hash72,
           witness->receipt_hash72,
           HHS_EXACT_PASS215_HASH72_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

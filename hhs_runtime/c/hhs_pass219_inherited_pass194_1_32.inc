#include "../include/hhs_pass219_inherited_pass194_1_32.h"

#include <stddef.h>
#include <string.h>

static const char P194_AUTHORIZATION_COMMIT[] = "714f3f3c5c77eab9714be421811ce4fd650a8e99";
static const char P194_BASELINE_COMMIT[] = "31aad2b8281c9a68c5f810948dac630dd5a387e0";
static const char P194_FROZEN_I131[] = "b8202201bc92470afdd15d701d16ea102aeb3aab";
static const char P194_CONTRACT_BLOB[] = "f437461b4cb74b40ba8444c48319ad8f906359cf";
static const char P194_RUNTIME_BLOB[] = "37c7a7dd3ad246674111398c50ee94e580e72d58";
static const char P194_API_BLOB[] = "b414b77d2bf35e5fef3056e6e91da3d7146fc278";
static const char P194_VISUAL_SERVER_BLOB[] = "998852398931f2e3af2da57ec455211f938b2661";
static const char P194_RUNTIME_TEST_BLOB[] = "ee7044605fde90f5bd40813de18cdf5d30b6d560";
static const char P194_API_TEST_BLOB[] = "7954ea3d45184088ef7f4406a018316075388054";
static const char P194_FOCUSED_WORKFLOW_BLOB[] = "f5cb94c8ad9f92741dab81ec2b8cdf1661f6c979";

static uint32_t p194_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS194_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS194_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS194_VERSION_PATCH;
}

static int p194_git(
    const char value[HHS_EXACT_PASS194_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS194_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS194_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass194_version(void) {
    return p194_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass194_storage_training_snapshot_authority(
    const HHSExactPass194StorageTrainingSnapshotAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass194BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p194_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->immutable_content_addressed_blob_store != 1U ||
        witness->versioned_sql_context_graph != 1U ||
        witness->sqlite_wal_full_sync != 1U ||
        witness->default_deny_training_sharing_public != 1U ||
        witness->explicit_consent_license_closure != 1U ||
        witness->encrypted_hash216_vector_projection != 1U ||
        witness->immutable_hydration_snapshot != 1U ||
        witness->governed_dataset_release != 1U ||
        witness->training_run_lineage != 1U ||
        witness->checkpoint_lineage != 1U ||
        witness->deletion_revocation_propagation != 1U ||
        witness->deterministic_replay_receipt_chain != 1U ||
        witness->vm81_authorized_metadata_mutations != 1U ||
        witness->pass195_successor_preserved != 1U ||
        witness->vector_store_is_source_authority != 0U ||
        witness->vector_store_is_consent_authority != 0U ||
        witness->snapshot_is_training_authorization != 0U ||
        witness->training_provider_is_vm81_authority != 0U ||
        witness->browser_is_authority != 0U ||
        witness->pass219_new_candidate_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p194_git(witness->contract_authorization_commit, P194_AUTHORIZATION_COMMIT) ||
        !p194_git(witness->contract_baseline_commit, P194_BASELINE_COMMIT) ||
        !p194_git(witness->frozen_i131_commit, P194_FROZEN_I131) ||
        !p194_git(witness->contract_blob, P194_CONTRACT_BLOB) ||
        !p194_git(witness->runtime_blob, P194_RUNTIME_BLOB) ||
        !p194_git(witness->api_blob, P194_API_BLOB) ||
        !p194_git(witness->visual_server_blob, P194_VISUAL_SERVER_BLOB) ||
        !p194_git(witness->runtime_test_blob, P194_RUNTIME_TEST_BLOB) ||
        !p194_git(witness->api_test_blob, P194_API_TEST_BLOB) ||
        !p194_git(witness->focused_workflow_blob, P194_FOCUSED_WORKFLOW_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p194_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS194_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->immutable_blob_store_bound = 1U;
    out_binding->sql_context_graph_bound = 1U;
    out_binding->default_deny_consent_bound = 1U;
    out_binding->encrypted_vector_projection_bound = 1U;
    out_binding->immutable_snapshot_bound = 1U;
    out_binding->dataset_training_lineage_bound = 1U;
    out_binding->deletion_replay_bound = 1U;
    out_binding->inherited_vm81_mutation_receipt_bound = 1U;
    out_binding->pass195_successor_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->vector_store_is_source_authority = 0U;
    out_binding->vector_store_is_consent_authority = 0U;
    out_binding->snapshot_is_training_authorization = 0U;
    out_binding->training_provider_is_vm81_authority = 0U;
    out_binding->browser_is_authority = 0U;
    out_binding->pass219_new_candidate_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(
        out_binding->contract_authorization_commit,
        witness->contract_authorization_commit,
        HHS_EXACT_PASS194_GIT_SHA_STRLEN
    );
    memcpy(
        out_binding->frozen_i131_commit,
        witness->frozen_i131_commit,
        HHS_EXACT_PASS194_GIT_SHA_STRLEN
    );
    return HHS_EXACT_STATUS_OK;
}

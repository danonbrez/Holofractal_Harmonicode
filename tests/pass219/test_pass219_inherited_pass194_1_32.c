#include "hhs_pass219_inherited_pass194_1_32.h"

#include <assert.h>
#include <string.h>

static HHSExactPass194StorageTrainingSnapshotAuthorityWitnessV1 witness(void) {
    HHSExactPass194StorageTrainingSnapshotAuthorityWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass194_version();
    w.immutable_content_addressed_blob_store = 1U;
    w.versioned_sql_context_graph = 1U;
    w.sqlite_wal_full_sync = 1U;
    w.default_deny_training_sharing_public = 1U;
    w.explicit_consent_license_closure = 1U;
    w.encrypted_hash216_vector_projection = 1U;
    w.immutable_hydration_snapshot = 1U;
    w.governed_dataset_release = 1U;
    w.training_run_lineage = 1U;
    w.checkpoint_lineage = 1U;
    w.deletion_revocation_propagation = 1U;
    w.deterministic_replay_receipt_chain = 1U;
    w.vm81_authorized_metadata_mutations = 1U;
    w.pass195_successor_preserved = 1U;
    strcpy(w.contract_authorization_commit, "714f3f3c5c77eab9714be421811ce4fd650a8e99");
    strcpy(w.contract_baseline_commit, "31aad2b8281c9a68c5f810948dac630dd5a387e0");
    strcpy(w.frozen_i131_commit, "b8202201bc92470afdd15d701d16ea102aeb3aab");
    strcpy(w.contract_blob, "f437461b4cb74b40ba8444c48319ad8f906359cf");
    strcpy(w.runtime_blob, "37c7a7dd3ad246674111398c50ee94e580e72d58");
    strcpy(w.api_blob, "b414b77d2bf35e5fef3056e6e91da3d7146fc278");
    strcpy(w.visual_server_blob, "998852398931f2e3af2da57ec455211f938b2661");
    strcpy(w.runtime_test_blob, "ee7044605fde90f5bd40813de18cdf5d30b6d560");
    strcpy(w.api_test_blob, "7954ea3d45184088ef7f4406a018316075388054");
    strcpy(w.focused_workflow_blob, "f5cb94c8ad9f92741dab81ec2b8cdf1661f6c979");
    return w;
}

int main(void) {
    HHSExactPass194StorageTrainingSnapshotAuthorityWitnessV1 w = witness();
    HHSExactPass219InheritedPass194BindingV1 binding;
    assert(hhs_exact_pass219_bind_pass194_storage_training_snapshot_authority(&w, &binding) == HHS_EXACT_STATUS_OK);
    assert(binding.pass_number == 194U);
    assert(binding.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(binding.immutable_blob_store_bound == 1U);
    assert(binding.sql_context_graph_bound == 1U);
    assert(binding.default_deny_consent_bound == 1U);
    assert(binding.encrypted_vector_projection_bound == 1U);
    assert(binding.immutable_snapshot_bound == 1U);
    assert(binding.dataset_training_lineage_bound == 1U);
    assert(binding.deletion_replay_bound == 1U);
    assert(binding.inherited_vm81_mutation_receipt_bound == 1U);
    assert(binding.pass195_successor_bound == 1U);
    assert(binding.no_new_authority_bound == 1U);
    assert(binding.vector_store_is_source_authority == 0U);
    assert(binding.vector_store_is_consent_authority == 0U);
    assert(binding.snapshot_is_training_authorization == 0U);
    assert(binding.training_provider_is_vm81_authority == 0U);
    assert(binding.browser_is_authority == 0U);
    assert(binding.pass219_new_candidate_authority == 0U);
    assert(binding.pass219_new_canonical_mutation_authority == 0U);
    assert(binding.pass219_new_persistence_authority == 0U);
    assert(binding.pass219_new_hash72_clock == 0U);
    assert(binding.cxx_mutation_authority == 0U);
    assert(binding.vm81_mutation_authority == 0U);

    w = witness();
    w.default_deny_training_sharing_public = 0U;
    assert(hhs_exact_pass219_bind_pass194_storage_training_snapshot_authority(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.vector_store_is_source_authority = 1U;
    assert(hhs_exact_pass219_bind_pass194_storage_training_snapshot_authority(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.training_provider_is_vm81_authority = 1U;
    assert(hhs_exact_pass219_bind_pass194_storage_training_snapshot_authority(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    strcpy(w.runtime_blob, "0000000000000000000000000000000000000000");
    assert(hhs_exact_pass219_bind_pass194_storage_training_snapshot_authority(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}

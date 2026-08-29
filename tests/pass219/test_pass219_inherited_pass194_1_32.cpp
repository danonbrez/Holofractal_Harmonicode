#include "hhs_pass219_inherited_pass194_1_32.hpp"

#include <cassert>
#include <cstring>

int main() {
    using hhs::rna::InheritedPass194StorageTrainingSnapshotAuthority;
    HHSExactPass194StorageTrainingSnapshotAuthorityWitnessV1 witness{};
    HHSExactPass219InheritedPass194BindingV1 binding{};
    witness.struct_size = sizeof(witness);
    witness.version = InheritedPass194StorageTrainingSnapshotAuthority::version();
    witness.immutable_content_addressed_blob_store = 1U;
    witness.versioned_sql_context_graph = 1U;
    witness.sqlite_wal_full_sync = 1U;
    witness.default_deny_training_sharing_public = 1U;
    witness.explicit_consent_license_closure = 1U;
    witness.encrypted_hash216_vector_projection = 1U;
    witness.immutable_hydration_snapshot = 1U;
    witness.governed_dataset_release = 1U;
    witness.training_run_lineage = 1U;
    witness.checkpoint_lineage = 1U;
    witness.deletion_revocation_propagation = 1U;
    witness.deterministic_replay_receipt_chain = 1U;
    witness.vm81_authorized_metadata_mutations = 1U;
    witness.pass195_successor_preserved = 1U;
    std::strcpy(witness.contract_authorization_commit, "714f3f3c5c77eab9714be421811ce4fd650a8e99");
    std::strcpy(witness.contract_baseline_commit, "31aad2b8281c9a68c5f810948dac630dd5a387e0");
    std::strcpy(witness.frozen_i131_commit, "b8202201bc92470afdd15d701d16ea102aeb3aab");
    std::strcpy(witness.contract_blob, "f437461b4cb74b40ba8444c48319ad8f906359cf");
    std::strcpy(witness.runtime_blob, "37c7a7dd3ad246674111398c50ee94e580e72d58");
    std::strcpy(witness.api_blob, "b414b77d2bf35e5fef3056e6e91da3d7146fc278");
    std::strcpy(witness.visual_server_blob, "998852398931f2e3af2da57ec455211f938b2661");
    std::strcpy(witness.runtime_test_blob, "ee7044605fde90f5bd40813de18cdf5d30b6d560");
    std::strcpy(witness.api_test_blob, "7954ea3d45184088ef7f4406a018316075388054");
    std::strcpy(witness.focused_workflow_blob, "f5cb94c8ad9f92741dab81ec2b8cdf1661f6c979");

    assert(InheritedPass194StorageTrainingSnapshotAuthority::bind(witness, binding) == HHS_EXACT_STATUS_OK);
    assert(binding.pass_number == 194U);
    assert(binding.no_new_authority_bound == 1U);
    static_assert(!InheritedPass194StorageTrainingSnapshotAuthority::mutation_authority());
    static_assert(!InheritedPass194StorageTrainingSnapshotAuthority::new_persistence_authority());
    static_assert(!InheritedPass194StorageTrainingSnapshotAuthority::hash72_clock_authority());
    static_assert(!InheritedPass194StorageTrainingSnapshotAuthority::vm81_mutation_authority());
    static_assert(!InheritedPass194StorageTrainingSnapshotAuthority::candidate_authority());
    static_assert(!InheritedPass194StorageTrainingSnapshotAuthority::vector_source_authority());
    static_assert(!InheritedPass194StorageTrainingSnapshotAuthority::vector_consent_authority());
    static_assert(!InheritedPass194StorageTrainingSnapshotAuthority::snapshot_training_authorization());
    static_assert(!InheritedPass194StorageTrainingSnapshotAuthority::training_provider_vm81_authority());
    static_assert(!InheritedPass194StorageTrainingSnapshotAuthority::browser_authority());
    static_assert(InheritedPass194StorageTrainingSnapshotAuthority::singleton_vm81_authority_remains_inherited());
    static_assert(InheritedPass194StorageTrainingSnapshotAuthority::default_deny_training());
    static_assert(InheritedPass194StorageTrainingSnapshotAuthority::explicit_consent_license_closure());
    static_assert(InheritedPass194StorageTrainingSnapshotAuthority::deterministic_replay());
    return 0;
}

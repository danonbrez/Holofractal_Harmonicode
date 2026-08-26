#ifndef HHS_PASS219_INHERITED_PASS194_1_32_H
#define HHS_PASS219_INHERITED_PASS194_1_32_H

#include "hhs_pass219_inherited_pass195_1_31.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS194_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS194_VERSION_MINOR 32U
#define HHS_EXACT_PASS219_INHERITED_PASS194_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS194_NUMBER 194U
#define HHS_EXACT_PASS194_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS194_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass194StorageTrainingSnapshotAuthorityWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t immutable_content_addressed_blob_store;
    uint32_t versioned_sql_context_graph;
    uint32_t sqlite_wal_full_sync;
    uint32_t default_deny_training_sharing_public;
    uint32_t explicit_consent_license_closure;
    uint32_t encrypted_hash216_vector_projection;
    uint32_t immutable_hydration_snapshot;
    uint32_t governed_dataset_release;
    uint32_t training_run_lineage;
    uint32_t checkpoint_lineage;
    uint32_t deletion_revocation_propagation;
    uint32_t deterministic_replay_receipt_chain;
    uint32_t vm81_authorized_metadata_mutations;
    uint32_t pass195_successor_preserved;
    uint32_t vector_store_is_source_authority;
    uint32_t vector_store_is_consent_authority;
    uint32_t snapshot_is_training_authorization;
    uint32_t training_provider_is_vm81_authority;
    uint32_t browser_is_authority;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char contract_authorization_commit[HHS_EXACT_PASS194_GIT_SHA_STRLEN];
    char contract_baseline_commit[HHS_EXACT_PASS194_GIT_SHA_STRLEN];
    char frozen_i131_commit[HHS_EXACT_PASS194_GIT_SHA_STRLEN];
    char contract_blob[HHS_EXACT_PASS194_GIT_SHA_STRLEN];
    char runtime_blob[HHS_EXACT_PASS194_GIT_SHA_STRLEN];
    char api_blob[HHS_EXACT_PASS194_GIT_SHA_STRLEN];
    char visual_server_blob[HHS_EXACT_PASS194_GIT_SHA_STRLEN];
    char runtime_test_blob[HHS_EXACT_PASS194_GIT_SHA_STRLEN];
    char api_test_blob[HHS_EXACT_PASS194_GIT_SHA_STRLEN];
    char focused_workflow_blob[HHS_EXACT_PASS194_GIT_SHA_STRLEN];
} HHSExactPass194StorageTrainingSnapshotAuthorityWitnessV1;

typedef struct HHSExactPass219InheritedPass194BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t immutable_blob_store_bound;
    uint32_t sql_context_graph_bound;
    uint32_t default_deny_consent_bound;
    uint32_t encrypted_vector_projection_bound;
    uint32_t immutable_snapshot_bound;
    uint32_t dataset_training_lineage_bound;
    uint32_t deletion_replay_bound;
    uint32_t inherited_vm81_mutation_receipt_bound;
    uint32_t pass195_successor_bound;
    uint32_t no_new_authority_bound;
    uint32_t vector_store_is_source_authority;
    uint32_t vector_store_is_consent_authority;
    uint32_t snapshot_is_training_authorization;
    uint32_t training_provider_is_vm81_authority;
    uint32_t browser_is_authority;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char contract_authorization_commit[HHS_EXACT_PASS194_GIT_SHA_STRLEN];
    char frozen_i131_commit[HHS_EXACT_PASS194_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass194BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass194_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass194_storage_training_snapshot_authority(
    const HHSExactPass194StorageTrainingSnapshotAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass194BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif

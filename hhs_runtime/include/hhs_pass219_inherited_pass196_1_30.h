#ifndef HHS_PASS219_INHERITED_PASS196_1_30_H
#define HHS_PASS219_INHERITED_PASS196_1_30_H

#include "hhs_pass219_inherited_pass197_1_29.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS196_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS196_VERSION_MINOR 30U
#define HHS_EXACT_PASS219_INHERITED_PASS196_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS196_NUMBER 196U
#define HHS_EXACT_PASS196_PRIMARY_PR 128U
#define HHS_EXACT_PASS196_TOPOLOGY_PR 130U
#define HHS_EXACT_PASS196_REVIEW_FINDING_COUNT 10U
#define HHS_EXACT_PASS196_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS196_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass196RepairedIntegratedEnvironmentWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t primary_pull_request;
    uint32_t topology_pull_request;
    uint32_t review_finding_count;
    uint32_t vm81_hash72_receipt_required_for_persistence;
    uint32_t persisted_restart_lineage_restored;
    uint32_t distinct_executable_evidence_required;
    uint32_t validated_projection_refresh_bound;
    uint32_t host_independent_manifest_identity;
    uint32_t same_bytes_hash_and_classification;
    uint32_t service_state_directory_preserved;
    uint32_t strict_boolean_tool_ingress;
    uint32_t failed_scan_quarantine;
    uint32_t scan_error_mapping_parity;
    uint32_t historical_v1_preserved;
    uint32_t pass197_successor_preserved;
    uint32_t vector_store_is_source_authority;
    uint32_t browser_projection_is_authority;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char accepted_primary_merge[HHS_EXACT_PASS196_GIT_SHA_STRLEN];
    char accepted_topology_merge[HHS_EXACT_PASS196_GIT_SHA_STRLEN];
    char frozen_i129_commit[HHS_EXACT_PASS196_GIT_SHA_STRLEN];
    char historical_v1_blob[HHS_EXACT_PASS196_GIT_SHA_STRLEN];
    char repaired_v2_blob[HHS_EXACT_PASS196_GIT_SHA_STRLEN];
    char repaired_api_blob[HHS_EXACT_PASS196_GIT_SHA_STRLEN];
    char repaired_frontend_blob[HHS_EXACT_PASS196_GIT_SHA_STRLEN];
    char projection_refresh_blob[HHS_EXACT_PASS196_GIT_SHA_STRLEN];
    char repair_regression_blob[HHS_EXACT_PASS196_GIT_SHA_STRLEN];
    char repair_workflow_blob[HHS_EXACT_PASS196_GIT_SHA_STRLEN];
} HHSExactPass196RepairedIntegratedEnvironmentWitnessV1;

typedef struct HHSExactPass219InheritedPass196BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t inherited_findings_repaired;
    uint32_t vm81_receipt_admission_bound;
    uint32_t restart_lineage_bound;
    uint32_t executable_evidence_bound;
    uint32_t projection_refresh_bound;
    uint32_t reproducible_manifest_bound;
    uint32_t immutable_observation_bound;
    uint32_t service_topology_bound;
    uint32_t strict_tool_ingress_bound;
    uint32_t failure_quarantine_bound;
    uint32_t error_parity_bound;
    uint32_t pass197_successor_bound;
    uint32_t no_new_authority_bound;
    uint32_t vector_store_is_source_authority;
    uint32_t browser_projection_is_authority;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char accepted_primary_merge[HHS_EXACT_PASS196_GIT_SHA_STRLEN];
    char accepted_topology_merge[HHS_EXACT_PASS196_GIT_SHA_STRLEN];
    char frozen_i129_commit[HHS_EXACT_PASS196_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass196BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass196_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass196_repaired_integrated_environment(
    const HHSExactPass196RepairedIntegratedEnvironmentWitnessV1 *witness,
    HHSExactPass219InheritedPass196BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif

#ifndef HHS_PASS219_INHERITED_PASS187_1_39_H
#define HHS_PASS219_INHERITED_PASS187_1_39_H

#include "hhs_pass219_inherited_pass188_1_38.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS187_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS187_VERSION_MINOR 39U
#define HHS_EXACT_PASS219_INHERITED_PASS187_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS187_NUMBER 187U
#define HHS_EXACT_PASS187_I139_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass187CumulativeAuthorityWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t composition_contract_preserved;
    uint32_t composition_completion_verified;
    uint32_t composition_acceptance_scenario_count;
    uint32_t harmonicode_roundtrip_verified;
    uint32_t incremental_recomposition_verified;
    uint32_t linux_adapter_integration_verified;
    uint32_t visual_browser_acceptance_verified;
    uint32_t cold_restart_recovery_verified;
    uint32_t inherited_vm81_witness_required;
    uint32_t local_event_evidence_is_mutation_authority;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_clock;
    uint32_t float_canonical_authority;
    uint32_t historical_bott_contract_preserved;
    uint32_t historical_bott_baseline_verified;
    uint32_t historical_bott_runtime_gap_record_preserved;
    uint32_t pass188_bott_runtime_closure_preserved;
    uint32_t pass188_successor_preserved;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;

    char composition_contract_commit[HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN];
    char historical_bott_merge_commit[HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN];
    char pass188_bott_runtime_commit[HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN];
    char composition_completion_head[HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN];
    char frozen_i138_commit[HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN];
    char composition_contract_blob[HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN];
    char bott_receipt_blob[HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN];
    char composition_runtime_blob[HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN];
    char composition_tests_blob[HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN];
    char composition_browser_blob[HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN];
    char composition_workflow_blob[HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN];
} HHSExactPass187CumulativeAuthorityWitnessV1;

typedef struct HHSExactPass219InheritedPass187BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t composition_contract_bound;
    uint32_t composition_completion_bound;
    uint32_t harmonicode_order_bound;
    uint32_t incremental_recomposition_bound;
    uint32_t linux_adapter_bound;
    uint32_t visual_interaction_bound;
    uint32_t replay_restart_bound;
    uint32_t vm81_witness_boundary_bound;
    uint32_t historical_bott_baseline_bound;
    uint32_t pass188_bott_runtime_closure_bound;
    uint32_t pass188_successor_bound;
    uint32_t no_new_authority_bound;
    uint32_t float_is_canonical_authority;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char frozen_i138_commit[HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN];
    char composition_completion_head[HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass187BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass187_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass187_cumulative_authority(
    const HHSExactPass187CumulativeAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass187BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif

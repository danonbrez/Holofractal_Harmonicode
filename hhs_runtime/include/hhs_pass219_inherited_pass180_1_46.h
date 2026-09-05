#ifndef HHS_PASS219_INHERITED_PASS180_1_46_H
#define HHS_PASS219_INHERITED_PASS180_1_46_H

#include "hhs_pass219_inherited_pass181_1_45.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS180_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS180_VERSION_MINOR 46U
#define HHS_EXACT_PASS219_INHERITED_PASS180_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS180_NUMBER 180U
#define HHS_EXACT_PASS180_I146_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS180_I146_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass180ApplicationFactoryWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t historical_contract_preserved;
    uint32_t historical_implementation_preserved;
    uint32_t historical_ci_green;
    uint32_t module_catalog_bound;
    uint32_t workflow_catalog_bound;
    uint32_t dependency_closure_bound;
    uint32_t incremental_planning_bound;
    uint32_t bounded_lifecycle_bound;
    uint32_t eight_checkpoint_lifecycle_bound;
    uint32_t deterministic_source_zip_bound;
    uint32_t deterministic_project_replay_bound;
    uint32_t visual_server_routes_bound;
    uint32_t vm81_canonical_mutation_repair_bound;
    uint32_t hash72_after_vm81_bound;
    uint32_t external_success_nonfabrication_bound;
    uint32_t singleton_vm81_bound;
    uint32_t pass181_successor_preserved;
    uint32_t i146_dependency_scoped_validation_green;
    uint32_t terminal_pass180_completion;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_authority;
    uint32_t hash216_mutation_authority;
    uint32_t floating_point_canonical_authority;
    char historical_green_head[HHS_EXACT_PASS180_I146_GIT_SHA_STRLEN];
    char frozen_i145_checkpoint[HHS_EXACT_PASS180_I146_GIT_SHA_STRLEN];
    char i145_validation_receipt_blob[HHS_EXACT_PASS180_I146_GIT_SHA_STRLEN];
} HHSExactPass180ApplicationFactoryWitnessV1;

typedef struct HHSExactPass219InheritedPass180BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t historical_runtime_reachable;
    uint32_t module_catalog_bound;
    uint32_t workflow_catalog_bound;
    uint32_t dependency_closure_bound;
    uint32_t incremental_planning_bound;
    uint32_t bounded_lifecycle_bound;
    uint32_t eight_checkpoint_lifecycle_bound;
    uint32_t deterministic_source_zip_bound;
    uint32_t deterministic_project_replay_bound;
    uint32_t visual_server_routes_bound;
    uint32_t vm81_canonical_mutation_repair_bound;
    uint32_t hash72_after_vm81_bound;
    uint32_t external_success_nonfabrication_bound;
    uint32_t singleton_vm81_bound;
    uint32_t no_new_authority_bound;
    uint32_t terminal_completion_claimed;
    uint32_t repair_forward_required;
    uint32_t remaining_terminal_obligation_count;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_authority;
    uint32_t hash216_mutation_authority;
    uint32_t floating_point_canonical_authority;
    char historical_green_head[HHS_EXACT_PASS180_I146_GIT_SHA_STRLEN];
    char frozen_i145_checkpoint[HHS_EXACT_PASS180_I146_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass180BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass180_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass180_application_factory(
    const HHSExactPass180ApplicationFactoryWitnessV1 *witness,
    HHSExactPass219InheritedPass180BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif
#endif

#ifndef HHS_PASS219_INHERITED_PASS177_1_49_H
#define HHS_PASS219_INHERITED_PASS177_1_49_H

#include "hhs_pass219_inherited_pass178_1_48.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS177_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS177_VERSION_MINOR 49U
#define HHS_EXACT_PASS219_INHERITED_PASS177_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS177_NUMBER 177U
#define HHS_EXACT_PASS177_I149_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS177_I149_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS177_I149_REMAINING_TERMINAL_CATEGORY_COUNT 12U

typedef struct HHSExactPass177WorkflowWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t contract_preserved;
    uint32_t historical_merge_preserved;
    uint32_t module_library_bound;
    uint32_t project_factory_bound;
    uint32_t workflow_engine_bound;
    uint32_t browser_candidate_identity_bound;
    uint32_t vm81_project_admission_bound;
    uint32_t vm81_checkpoint_admission_bound;
    uint32_t historical_stage_truth_preserved;
    uint32_t pre_cumulative_validation_green;
    uint32_t pass178_successor_preserved;
    uint32_t terminal_pass177_completion;
    uint32_t repair_forward_required;
    uint32_t remaining_terminal_category_count;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_commit_authority;
    uint32_t hash216_mutation_authority;
    uint32_t browser_identity_authority;
    uint32_t memory_checkpoint_authority;
    char validated_authority_head[HHS_EXACT_PASS177_I149_GIT_SHA_STRLEN];
    char authority_receipt_blob[HHS_EXACT_PASS177_I149_GIT_SHA_STRLEN];
} HHSExactPass177WorkflowWitnessV1;

typedef struct HHSExactPass219InheritedPass177BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t historical_runtime_reachable;
    uint32_t browser_workflow_bound;
    uint32_t vm81_project_admission_bound;
    uint32_t vm81_checkpoint_admission_bound;
    uint32_t historical_stage_truth_preserved;
    uint32_t no_new_authority_bound;
    uint32_t terminal_completion_claimed;
    uint32_t repair_forward_required;
    uint32_t remaining_terminal_category_count;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_commit_authority;
    uint32_t hash216_mutation_authority;
    uint32_t browser_identity_authority;
    uint32_t memory_checkpoint_authority;
    char validated_authority_head[HHS_EXACT_PASS177_I149_GIT_SHA_STRLEN];
    char authority_receipt_blob[HHS_EXACT_PASS177_I149_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass177BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass177_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass177_creation_workflows(
    const HHSExactPass177WorkflowWitnessV1 *witness,
    HHSExactPass219InheritedPass177BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif
#endif

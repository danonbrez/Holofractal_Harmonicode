#ifndef HHS_PASS219_INHERITED_PASS178_1_48_H
#define HHS_PASS219_INHERITED_PASS178_1_48_H

#include "hhs_pass219_inherited_pass179_1_47.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS178_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS178_VERSION_MINOR 48U
#define HHS_EXACT_PASS219_INHERITED_PASS178_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS178_NUMBER 178U
#define HHS_EXACT_PASS178_I148_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS178_I148_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS178_I148_REMAINING_TERMINAL_CATEGORY_COUNT 12U

typedef struct HHSExactPass178PhysicsWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t contract_preserved;
    uint32_t exact_rational_complex_bound;
    uint32_t algebraic_root_branch_bound;
    uint32_t constraint_graph_bound;
    uint32_t relativistic_nucleus_bound;
    uint32_t quantum_cayley_nucleus_bound;
    uint32_t native_public_abi_bound;
    uint32_t vm81_state_admission_bound;
    uint32_t deterministic_replay_bound;
    uint32_t immutable_render_packet_bound;
    uint32_t served_physics_studio_bound;
    uint32_t pre_cumulative_validation_green;
    uint32_t pass179_successor_preserved;
    uint32_t terminal_pass178_completion;
    uint32_t repair_forward_required;
    uint32_t complete_historical_constraint_corpus;
    uint32_t remaining_terminal_category_count;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_commit_authority;
    uint32_t hash216_mutation_authority;
    uint32_t renderer_mutation_authority;
    uint32_t gpu_mutation_authority;
    uint32_t browser_mutation_authority;
    uint32_t floating_point_canonical_authority;
    char validated_nucleus_head[HHS_EXACT_PASS178_I148_GIT_SHA_STRLEN];
    char nucleus_receipt_blob[HHS_EXACT_PASS178_I148_GIT_SHA_STRLEN];
} HHSExactPass178PhysicsWitnessV1;

typedef struct HHSExactPass219InheritedPass178BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t native_runtime_reachable;
    uint32_t exact_physics_nucleus_bound;
    uint32_t vm81_state_admission_bound;
    uint32_t deterministic_replay_bound;
    uint32_t immutable_render_packet_bound;
    uint32_t served_physics_studio_bound;
    uint32_t no_new_authority_bound;
    uint32_t terminal_completion_claimed;
    uint32_t repair_forward_required;
    uint32_t complete_historical_constraint_corpus;
    uint32_t remaining_terminal_category_count;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_commit_authority;
    uint32_t hash216_mutation_authority;
    uint32_t renderer_mutation_authority;
    uint32_t gpu_mutation_authority;
    uint32_t browser_mutation_authority;
    uint32_t floating_point_canonical_authority;
    char validated_nucleus_head[HHS_EXACT_PASS178_I148_GIT_SHA_STRLEN];
    char nucleus_receipt_blob[HHS_EXACT_PASS178_I148_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass178BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass178_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass178_exact_physics(
    const HHSExactPass178PhysicsWitnessV1 *witness,
    HHSExactPass219InheritedPass178BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif
#endif

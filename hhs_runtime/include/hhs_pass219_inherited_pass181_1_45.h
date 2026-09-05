#ifndef HHS_PASS219_INHERITED_PASS181_1_45_H
#define HHS_PASS219_INHERITED_PASS181_1_45_H

#include "hhs_pass219_inherited_pass182_1_44.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS181_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS181_VERSION_MINOR 45U
#define HHS_EXACT_PASS219_INHERITED_PASS181_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS181_NUMBER 181U
#define HHS_EXACT_PASS181_I145_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS181_I145_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS181_I145_REMAINING_TERMINAL_OBLIGATIONS 3U

typedef struct HHSExactPass181GraphicsHydrationWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t historical_contract_preserved;
    uint32_t historical_implementation_preserved;
    uint32_t historical_ci_green;
    uint32_t read_only_reference_ingestion_bound;
    uint32_t canonical_mp4_timeline_bound;
    uint32_t native_recipe_residual_bound;
    uint32_t bounded_optimization_bound;
    uint32_t vector_hydration_bound;
    uint32_t governed_constraint_registry_bound;
    uint32_t vm81_admission_repair_bound;
    uint32_t legacy_direct_promotion_disabled;
    uint32_t cold_restart_constraint_registry_replay_bound;
    uint32_t singleton_vm81_bound;
    uint32_t hash72_evidence_bound;
    uint32_t hash216_archival_only_bound;
    uint32_t pass182_successor_preserved;
    uint32_t terminal_pass181_completion;
    uint32_t remaining_terminal_obligation_count;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_authority;
    uint32_t hash216_mutation_authority;
    uint32_t floating_point_canonical_authority;
    uint32_t threejs_final_frame_authority;
    char historical_green_head[HHS_EXACT_PASS181_I145_GIT_SHA_STRLEN];
    char frozen_i144_checkpoint[HHS_EXACT_PASS181_I145_GIT_SHA_STRLEN];
} HHSExactPass181GraphicsHydrationWitnessV1;

typedef struct HHSExactPass219InheritedPass181BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t historical_runtime_reachable;
    uint32_t read_only_reference_ingestion_bound;
    uint32_t canonical_mp4_timeline_bound;
    uint32_t native_recipe_residual_bound;
    uint32_t bounded_optimization_bound;
    uint32_t vector_hydration_bound;
    uint32_t governed_constraint_registry_bound;
    uint32_t vm81_admission_repair_bound;
    uint32_t legacy_direct_promotion_disabled;
    uint32_t cold_restart_constraint_registry_replay_bound;
    uint32_t singleton_vm81_bound;
    uint32_t hash72_evidence_bound;
    uint32_t hash216_archival_only_bound;
    uint32_t no_new_authority_bound;
    uint32_t terminal_completion_claimed;
    uint32_t repair_forward_required;
    uint32_t remaining_terminal_obligation_count;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_authority;
    uint32_t hash216_mutation_authority;
    uint32_t floating_point_canonical_authority;
    uint32_t threejs_final_frame_authority;
    char historical_green_head[HHS_EXACT_PASS181_I145_GIT_SHA_STRLEN];
    char frozen_i144_checkpoint[HHS_EXACT_PASS181_I145_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass181BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass181_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass181_graphics_hydration(
    const HHSExactPass181GraphicsHydrationWitnessV1 *witness,
    HHSExactPass219InheritedPass181BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif
#endif

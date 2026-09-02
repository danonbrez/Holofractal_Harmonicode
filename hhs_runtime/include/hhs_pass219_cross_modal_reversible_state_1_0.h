#ifndef HHS_PASS219_CROSS_MODAL_REVERSIBLE_STATE_1_0_H
#define HHS_PASS219_CROSS_MODAL_REVERSIBLE_STATE_1_0_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_PASS219_CROSS_MODAL_VERSION 1u
#define HHS_PASS219_CROSS_MODAL_VM81_CELLS 81u
#define HHS_PASS219_CROSS_MODAL_OPERATIONS_PER_CELL 64u
#define HHS_PASS219_CROSS_MODAL_ADDRESSES 5184u
#define HHS_PASS219_CROSS_MODAL_MAX_MODALITIES 64u
#define HHS_PASS219_CROSS_MODAL_MAX_DEPTH 1000000u
#define HHS_PASS219_CROSS_MODAL_MAX_CONSTRAINTS 1000000u

typedef enum HHSExactPass219CrossModalStatusV1 {
    HHS_PASS219_CROSS_MODAL_OK = 0,
    HHS_PASS219_CROSS_MODAL_NULL = 1,
    HHS_PASS219_CROSS_MODAL_RANGE_ERROR = 2,
    HHS_PASS219_CROSS_MODAL_LINEAGE_ERROR = 3,
    HHS_PASS219_CROSS_MODAL_PHASE_ORDER_ERROR = 4,
    HHS_PASS219_CROSS_MODAL_MODALITY_COVERAGE_ERROR = 5,
    HHS_PASS219_CROSS_MODAL_ROUNDTRIP_ERROR = 6,
    HHS_PASS219_CROSS_MODAL_CONSTRAINT_ERROR = 7,
    HHS_PASS219_CROSS_MODAL_AUTHORITY_ERROR = 8,
    HHS_PASS219_CROSS_MODAL_OVERFLOW = 9
} HHSExactPass219CrossModalStatusV1;

typedef struct HHSExactPass219CrossModalStateWitnessV1 {
    uint32_t version;
    uint32_t depth;
    uint32_t required_modalities;
    uint32_t mapped_modalities;
    uint32_t constraints_total;
    uint32_t constraints_passed;
    uint32_t reversible_edges_required;
    uint32_t reversible_edges_verified;
    uint32_t genesis_lineage_bound;
    uint32_t ordered_phase_path_bound;
    uint32_t hash216_lineage_bound;
    uint32_t global_constraint_root_bound;
    uint32_t modality_registry_root_bound;
    uint32_t singleton_vm81_authority_required;
    uint32_t candidate_mutation_authority;
    uint32_t floating_point_authority;
} HHSExactPass219CrossModalStateWitnessV1;

typedef struct HHSExactPass219CrossModalWorkPlanV1 {
    uint32_t version;
    uint32_t depth;
    uint32_t modalities;
    uint32_t constraints_per_state;
    uint32_t cached_prefix_depth;
    uint32_t changed_constraints;
    uint32_t prefix_proof_valid;
    uint32_t hub_roundtrip_verified;
    uint32_t optimization_selected;
    uint32_t complete_fallback;
    uint64_t baseline_constraint_checks;
    uint64_t baseline_translation_checks;
    uint64_t baseline_authority_checks;
    uint64_t baseline_total_work;
    uint64_t candidate_constraint_checks;
    uint64_t candidate_translation_checks;
    uint64_t candidate_authority_checks;
    uint64_t candidate_total_work;
    uint64_t selected_total_work;
    uint64_t exact_work_saved;
} HHSExactPass219CrossModalWorkPlanV1;

HHSExactPass219CrossModalStatusV1
hhs_exact_pass219_cross_modal_state_validate(
    const HHSExactPass219CrossModalStateWitnessV1 *witness);

HHSExactPass219CrossModalStatusV1
hhs_exact_pass219_cross_modal_work_plan(
    uint32_t depth,
    uint32_t modalities,
    uint32_t constraints_per_state,
    uint32_t cached_prefix_depth,
    uint32_t changed_constraints,
    uint32_t prefix_proof_valid,
    uint32_t hub_roundtrip_verified,
    HHSExactPass219CrossModalWorkPlanV1 *out);

#ifdef __cplusplus
}
#endif

#endif

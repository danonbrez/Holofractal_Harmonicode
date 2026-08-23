#ifndef HHS_PASS219B_SELECTIVE_PROJECTION_1_0_H
#define HHS_PASS219B_SELECTIVE_PROJECTION_1_0_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219B_SELECTIVE_PROJECTION_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219B_SELECTIVE_PROJECTION_VERSION_MINOR 0U
#define HHS_EXACT_PASS219B_SELECTIVE_PROJECTION_VERSION_PATCH 0U
#define HHS_EXACT_PASS219B_SELECTIVE_PROJECTION_MAX_CELL_RANGES 81U

typedef struct HHSExactPass219BProjectionRatioV1 {
    uint32_t numerator_p;
    uint32_t denominator_q;
} HHSExactPass219BProjectionRatioV1;

typedef struct HHSExactPass219BProjectionCellRangeV1 {
    uint64_t first_selected;
    uint64_t end_selected;
} HHSExactPass219BProjectionCellRangeV1;

typedef struct HHSExactPass219BSelectiveProjectionPlanV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t numerator_p;
    uint32_t denominator_q;
    uint64_t source_count;
    uint64_t selected_count;
    uint64_t avoided_count;
    uint8_t precomputed_id_buffer_required;
    uint8_t precomputed_cell_ranges_required;
    uint8_t measured_hot_path_division_forbidden;
    uint8_t measured_hot_path_modulo_forbidden;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_persistence_authority;
    uint8_t canonical_hash72_authority;
    uint8_t projection_only;
} HHSExactPass219BSelectiveProjectionPlanV1;

HHS_EXACT_API uint32_t hhs_exact_pass219b_selective_projection_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_selective_projection_plan(
    uint64_t source_count,
    uint32_t numerator_p,
    uint32_t denominator_q,
    HHSExactPass219BSelectiveProjectionPlanV1 *out_plan
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_selective_projection_selected_count(
    uint64_t source_count,
    uint32_t numerator_p,
    uint32_t denominator_q,
    uint64_t *out_selected_count
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_selective_projection_build_ids_u32(
    uint64_t source_count,
    uint32_t numerator_p,
    uint32_t denominator_q,
    uint32_t *out_ids,
    size_t capacity,
    size_t *out_count
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_selective_projection_validate_ids_u32(
    uint64_t source_count,
    uint32_t numerator_p,
    uint32_t denominator_q,
    const uint32_t *selected_ids,
    size_t selected_count
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_selective_projection_build_equal_cell_ranges(
    const uint32_t *selected_ids,
    size_t selected_count,
    uint64_t source_count,
    uint32_t cell_count,
    HHSExactPass219BProjectionCellRangeV1 *out_ranges,
    size_t range_capacity
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_selective_projection_verify(
    const HHSExactPass219BSelectiveProjectionPlanV1 *plan,
    uint64_t realized_selected_count,
    uint32_t ids_strictly_increasing,
    uint32_t original_identity_preserved,
    uint32_t exact_state_digest_equal,
    uint32_t canonical_authority_requested
);

#ifdef __cplusplus
}
#endif

#endif

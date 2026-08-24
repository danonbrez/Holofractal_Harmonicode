#ifndef HHS_PASS219B_SPARSE_DIRTY_PROJECTION_1_0_H
#define HHS_PASS219B_SPARSE_DIRTY_PROJECTION_1_0_H

#include "hhs_pass219b_selective_projection_1_0.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219B_SPARSE_DIRTY_PROJECTION_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219B_SPARSE_DIRTY_PROJECTION_VERSION_MINOR 0U
#define HHS_EXACT_PASS219B_SPARSE_DIRTY_PROJECTION_VERSION_PATCH 0U
#define HHS_EXACT_PASS219B_SPARSE_DIRTY_PROJECTION_MAX_CELLS 81U

typedef struct HHSExactPass219BSparseProjectionSpanV1 {
    uint64_t first_selected;
    uint64_t end_selected;
} HHSExactPass219BSparseProjectionSpanV1;

typedef struct HHSExactPass219BSparseDirtyProjectionPlanV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t cell_count;
    uint32_t dirty_cell_count;
    uint32_t span_count;
    uint32_t reserved_u32;
    uint64_t selected_count;
    uint64_t update_selected_count;
    uint64_t avoided_selected_count;
    uint8_t precomputed_cell_ranges_required;
    uint8_t dirty_cells_sorted_unique_required;
    uint8_t contiguous_selected_spans_coalesced;
    uint8_t measured_hot_path_division_forbidden;
    uint8_t measured_hot_path_modulo_forbidden;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_persistence_authority;
    uint8_t canonical_hash72_authority;
    uint8_t projection_only;
} HHSExactPass219BSparseDirtyProjectionPlanV1;

HHS_EXACT_API uint32_t hhs_exact_pass219b_sparse_dirty_projection_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_sparse_dirty_projection_validate_ranges(
    const HHSExactPass219BProjectionCellRangeV1 *cell_ranges,
    uint32_t cell_count,
    uint64_t selected_count
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_sparse_dirty_projection_build_spans(
    const HHSExactPass219BProjectionCellRangeV1 *cell_ranges,
    uint32_t cell_count,
    const uint32_t *dirty_cells,
    size_t dirty_cell_count,
    HHSExactPass219BSparseProjectionSpanV1 *out_spans,
    size_t span_capacity,
    HHSExactPass219BSparseDirtyProjectionPlanV1 *out_plan
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_sparse_dirty_projection_verify(
    const HHSExactPass219BSparseDirtyProjectionPlanV1 *plan,
    const HHSExactPass219BSparseProjectionSpanV1 *spans,
    size_t span_count,
    uint64_t realized_update_selected_count,
    uint32_t exact_projection_equal,
    uint32_t canonical_authority_requested
);

#ifdef __cplusplus
}
#endif

#endif

#ifndef HHS_PASS219B_SPARSE_DIRTY_PROJECTION_1_0_HPP
#define HHS_PASS219B_SPARSE_DIRTY_PROJECTION_1_0_HPP

#include "hhs_pass219b_sparse_dirty_projection_1_0.h"

#include <cstddef>
#include <cstdint>
#include <type_traits>

namespace hhs::pass219b {

inline HHSExactStatus build_sparse_dirty_projection_spans(
    const HHSExactPass219BProjectionCellRangeV1* cell_ranges,
    std::uint32_t cell_count,
    std::uint64_t selected_count,
    const std::uint32_t* dirty_cells,
    std::size_t dirty_cell_count,
    HHSExactPass219BSparseProjectionSpanV1* out_spans,
    std::size_t span_capacity,
    HHSExactPass219BSparseDirtyProjectionPlanV1* out_plan) noexcept {
    return hhs_exact_pass219b_sparse_dirty_projection_build_spans(
        cell_ranges,
        cell_count,
        selected_count,
        dirty_cells,
        dirty_cell_count,
        out_spans,
        span_capacity,
        out_plan);
}

inline HHSExactStatus verify_sparse_dirty_projection(
    const HHSExactPass219BSparseDirtyProjectionPlanV1& plan,
    const HHSExactPass219BSparseProjectionSpanV1* spans,
    std::size_t span_count,
    std::uint64_t realized_update_selected_count,
    bool dirty_set_complete,
    bool exact_projection_equal,
    bool canonical_authority_requested = false) noexcept {
    return hhs_exact_pass219b_sparse_dirty_projection_verify(
        &plan,
        spans,
        span_count,
        realized_update_selected_count,
        dirty_set_complete ? 1U : 0U,
        exact_projection_equal ? 1U : 0U,
        canonical_authority_requested ? 1U : 0U);
}

static_assert(std::is_standard_layout_v<HHSExactPass219BSparseProjectionSpanV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219BSparseProjectionSpanV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219BSparseDirtyProjectionPlanV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219BSparseDirtyProjectionPlanV1>);

}  // namespace hhs::pass219b

#endif

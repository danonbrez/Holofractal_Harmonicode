#include "../../hhs_runtime/include/hhs_pass219b_selective_projection_1_0.hpp"
#include "../../hhs_runtime/include/hhs_pass219b_sparse_dirty_projection_1_0.hpp"

#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>

int main() {
    std::array<std::uint32_t, 1728> ids{};
    std::array<HHSExactPass219BProjectionCellRangeV1, 81> ranges{};
    std::array<HHSExactPass219BSparseProjectionSpanV1, 81> spans{};
    const std::array<std::uint32_t, 5> dirty{{0U, 1U, 2U, 40U, 80U}};
    HHSExactPass219BSparseDirtyProjectionPlanV1 plan{};
    std::size_t selected_count = 0U;

    assert(hhs::pass219b::build_projection_ids(
        5184ULL, 1U, 3U, ids.data(), ids.size(), &selected_count) == HHS_EXACT_STATUS_OK);
    assert(selected_count == ids.size());
    assert(hhs::pass219b::build_equal_cell_ranges(
        ids.data(),
        selected_count,
        5184ULL,
        81U,
        ranges.data(),
        ranges.size()) == HHS_EXACT_STATUS_OK);

    assert(hhs::pass219b::build_sparse_dirty_projection_spans(
        ranges.data(),
        81U,
        static_cast<std::uint64_t>(selected_count),
        dirty.data(),
        dirty.size(),
        spans.data(),
        spans.size(),
        &plan) == HHS_EXACT_STATUS_OK);

    assert(plan.projection_only == 1U);
    assert(plan.canonical_mutation_authority == 0U);
    assert(plan.canonical_persistence_authority == 0U);
    assert(plan.canonical_hash72_authority == 0U);
    assert(plan.dirty_cell_count == dirty.size());
    assert(plan.span_count == 3U);
    assert(plan.update_selected_count < plan.selected_count);
    assert(plan.avoided_selected_count == plan.selected_count - plan.update_selected_count);

    assert(hhs::pass219b::verify_sparse_dirty_projection(
        plan,
        spans.data(),
        plan.span_count,
        plan.update_selected_count,
        true) == HHS_EXACT_STATUS_OK);
    assert(hhs::pass219b::verify_sparse_dirty_projection(
        plan,
        spans.data(),
        plan.span_count,
        plan.update_selected_count,
        false) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(hhs::pass219b::verify_sparse_dirty_projection(
        plan,
        spans.data(),
        plan.span_count,
        plan.update_selected_count,
        true,
        true) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    return 0;
}

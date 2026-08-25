#include "../../hhs_runtime/include/hhs_pass219b_selective_projection_1_0.hpp"

#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>

int main() {
    hhs::pass219b::SelectiveProjectionPlan plan(17625600ULL, 7U, 20U);
    assert(plan.status() == HHS_EXACT_STATUS_OK);
    assert(plan.numerator() == 7U);
    assert(plan.denominator() == 20U);
    assert(plan.source_count() == 17625600ULL);
    assert(plan.selected_count() == 6168960ULL);
    assert(plan.avoided_count() == 11456640ULL);
    assert(plan.projection_only());
    assert(!plan.authoritative());
    assert(plan.hot_path_division_forbidden());
    assert(plan.hot_path_modulo_forbidden());

    hhs::pass219b::SelectiveProjectionPlan local(5184ULL, 1U, 3U);
    assert(local.status() == HHS_EXACT_STATUS_OK);
    assert(local.selected_count() == 1728ULL);

    std::array<std::uint32_t, 1728> ids{};
    std::array<HHSExactPass219BProjectionCellRangeV1, 81> ranges{};
    std::size_t count = 0U;
    auto status = hhs::pass219b::build_projection_ids(
        5184ULL, 1U, 3U, ids.data(), ids.size(), &count);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(count == ids.size());
    for (std::size_t i = 1U; i < count; ++i) {
        assert(ids[i] > ids[i - 1U]);
    }

    status = hhs::pass219b::build_equal_cell_ranges(
        ids.data(), ids.size(), 5184ULL, 81U,
        ranges.data(), ranges.size());
    assert(status == HHS_EXACT_STATUS_OK);
    assert(ranges.front().first_selected == 0U);
    assert(ranges.back().end_selected == ids.size());

    hhs::pass219b::SelectiveProjectionPlan invalid(81ULL, 4U, 3U);
    assert(invalid.status() == HHS_EXACT_STATUS_RANGE_ERROR);

    return 0;
}

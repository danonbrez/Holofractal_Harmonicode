#ifndef HHS_PASS219B_SELECTIVE_PROJECTION_1_0_HPP
#define HHS_PASS219B_SELECTIVE_PROJECTION_1_0_HPP

#include "hhs_pass219b_selective_projection_1_0.h"

#include <cstddef>
#include <cstdint>
#include <type_traits>

namespace hhs::pass219b {

class SelectiveProjectionPlan final {
public:
    SelectiveProjectionPlan(
        std::uint64_t source_count,
        std::uint32_t numerator_p,
        std::uint32_t denominator_q) noexcept {
        status_ = hhs_exact_pass219b_selective_projection_plan(
            source_count, numerator_p, denominator_q, &record_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    std::uint32_t numerator() const noexcept { return record_.numerator_p; }
    std::uint32_t denominator() const noexcept { return record_.denominator_q; }
    std::uint64_t source_count() const noexcept { return record_.source_count; }
    std::uint64_t selected_count() const noexcept { return record_.selected_count; }
    std::uint64_t avoided_count() const noexcept { return record_.avoided_count; }
    bool projection_only() const noexcept { return record_.projection_only == 1U; }
    bool authoritative() const noexcept {
        return record_.canonical_mutation_authority != 0U ||
               record_.canonical_persistence_authority != 0U ||
               record_.canonical_hash72_authority != 0U;
    }
    bool hot_path_division_forbidden() const noexcept {
        return record_.measured_hot_path_division_forbidden == 1U;
    }
    bool hot_path_modulo_forbidden() const noexcept {
        return record_.measured_hot_path_modulo_forbidden == 1U;
    }
    const HHSExactPass219BSelectiveProjectionPlanV1& record() const noexcept {
        return record_;
    }

private:
    HHSExactPass219BSelectiveProjectionPlanV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

inline HHSExactStatus build_projection_ids(
    std::uint64_t source_count,
    std::uint32_t numerator_p,
    std::uint32_t denominator_q,
    std::uint32_t* out_ids,
    std::size_t capacity,
    std::size_t* out_count) noexcept {
    return hhs_exact_pass219b_selective_projection_build_ids_u32(
        source_count, numerator_p, denominator_q,
        out_ids, capacity, out_count);
}

inline HHSExactStatus build_equal_cell_ranges(
    const std::uint32_t* selected_ids,
    std::size_t selected_count,
    std::uint64_t source_count,
    std::uint32_t cell_count,
    HHSExactPass219BProjectionCellRangeV1* out_ranges,
    std::size_t range_capacity) noexcept {
    return hhs_exact_pass219b_selective_projection_build_equal_cell_ranges(
        selected_ids, selected_count, source_count, cell_count,
        out_ranges, range_capacity);
}

static_assert(std::is_standard_layout_v<HHSExactPass219BProjectionRatioV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219BProjectionCellRangeV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219BSelectiveProjectionPlanV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219BSelectiveProjectionPlanV1>);

}  // namespace hhs::pass219b

#endif

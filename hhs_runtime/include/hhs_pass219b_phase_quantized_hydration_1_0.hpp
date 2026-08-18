#ifndef HHS_PASS219B_PHASE_QUANTIZED_HYDRATION_1_0_HPP
#define HHS_PASS219B_PHASE_QUANTIZED_HYDRATION_1_0_HPP

#include "hhs_pass219b_phase_quantized_hydration_1_0.h"

#include <cstddef>
#include <cstdint>
#include <type_traits>

namespace hhs::pass219b {

class OuterPhaseView final {
public:
    explicit constexpr OuterPhaseView(
        const HHSExactPass219BOuterPhaseCellV1* record = nullptr) noexcept
        : record_(record) {}

    constexpr bool valid() const noexcept { return record_ != nullptr; }
    constexpr std::uint8_t perimeter_index() const noexcept {
        return record_ != nullptr ? record_->perimeter_index : 0U;
    }
    constexpr HHSExactPass219BRing ring() const noexcept {
        return record_ != nullptr
            ? static_cast<HHSExactPass219BRing>(record_->ring)
            : HHS_EXACT_PASS219B_RING_XY;
    }
    constexpr std::uint8_t ring_step() const noexcept {
        return record_ != nullptr ? record_->ring_step : 0U;
    }
    constexpr HHSExactPhaseBasis basis() const noexcept {
        return record_ != nullptr
            ? static_cast<HHSExactPhaseBasis>(record_->phase_basis)
            : HHS_EXACT_PHASE_X;
    }
    constexpr HHSExactPass219BRotationFamily rotation_family() const noexcept {
        return record_ != nullptr
            ? static_cast<HHSExactPass219BRotationFamily>(record_->rotation_family)
            : HHS_EXACT_PASS219B_ROTATION_I;
    }
    constexpr std::int8_t direction() const noexcept {
        return record_ != nullptr ? record_->direction : 0;
    }
    constexpr std::uint8_t phase_position() const noexcept {
        return record_ != nullptr ? record_->phase_position81 : 0U;
    }
    constexpr HHSExactPass219BRelationRole relation_role() const noexcept {
        return record_ != nullptr
            ? static_cast<HHSExactPass219BRelationRole>(record_->relation_role)
            : HHS_EXACT_PASS219B_REL_X_RECIPROCAL;
    }

private:
    const HHSExactPass219BOuterPhaseCellV1* record_;
};

class PhaseCell final {
public:
    PhaseCell(
        const HHSExactPass219HydrationCoordinateV1& parent,
        std::uint8_t origin81) noexcept {
        status_ = hhs_exact_pass219b_phase_cell(&parent, origin81, &record_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    std::uint8_t origin() const noexcept { return record_.phase_origin81; }
    std::uint64_t projection_index() const noexcept { return record_.projection_index; }
    bool center_closure_preserved() const noexcept {
        return record_.center_closure_preserved == 1U;
    }
    bool authoritative() const noexcept {
        return record_.canonical_mutation_authority != 0U ||
               record_.canonical_persistence_authority != 0U ||
               record_.canonical_hash72_authority != 0U;
    }
    OuterPhaseView outer(std::size_t index) const noexcept {
        return index < HHS_EXACT_PASS219B_OUTER_CELL_COUNT
            ? OuterPhaseView(&record_.outer[index])
            : OuterPhaseView();
    }
    const HHSExactPass219BPhaseCellV1& record() const noexcept { return record_; }

private:
    HHSExactPass219BPhaseCellV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

class ExpansionPlan final {
public:
    ExpansionPlan(std::uint64_t parent_count, std::uint32_t origin_count) noexcept {
        status_ = hhs_exact_pass219b_expansion_plan(
            parent_count, origin_count, &record_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    std::uint64_t required_cells() const noexcept { return record_.required_phase_cells; }
    std::uint64_t full_projection_cells() const noexcept {
        return record_.full_phase_projection_cells;
    }
    bool requires_full_materialization() const noexcept {
        return record_.full_materialization_required != 0U;
    }
    const HHSExactPass219BExpansionPlanV1& record() const noexcept { return record_; }

private:
    HHSExactPass219BExpansionPlanV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

inline HHSExactStatus expand_selected(
    const HHSExactPass219HydrationCoordinateV1* parents,
    std::size_t parent_count,
    std::uint8_t first_origin81,
    std::uint8_t origin_count,
    HHSExactPass219BPhaseCellV1* out_cells,
    std::size_t capacity,
    std::size_t* out_count) noexcept {
    return hhs_exact_pass219b_expand_selected(
        parents, parent_count, first_origin81, origin_count,
        out_cells, capacity, out_count);
}

static_assert(std::is_standard_layout_v<HHSExactPass219BOuterPhaseCellV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219BPhaseCellV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219BExpansionPlanV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219BPhaseCellV1>);

}  // namespace hhs::pass219b

#endif

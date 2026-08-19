#ifndef HHS_PASS219B_UNIVERSAL_PHASE_LOCALITY_1_0_HPP
#define HHS_PASS219B_UNIVERSAL_PHASE_LOCALITY_1_0_HPP

#include "hhs_pass219b_universal_phase_locality_1_0.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <stdexcept>

namespace hhs::rna {

class UniversalPhaseLocalityPlan final {
public:
    template <std::size_t N>
    static UniversalPhaseLocalityPlan build(
        const std::array<HHSExactPass219BPhaseLocalityDimensionV1, N>& dimensions,
        bool exact_selector_available,
        bool audit_dense_authorized,
        std::uint64_t base_units
    ) {
        HHSExactPass219BPhaseLocalityPlanV1 plan{};
        const auto status = hhs_exact_pass219b_phase_locality_plan(
            dimensions.data(), N,
            exact_selector_available ? 1U : 0U,
            audit_dense_authorized ? 1U : 0U,
            base_units, &plan);
        if (status != HHS_EXACT_STATUS_OK)
            throw std::runtime_error("phase locality plan rejected");
        return UniversalPhaseLocalityPlan(plan);
    }

    const HHSExactPass219BPhaseLocalityPlanV1& abi() const noexcept { return plan_; }

    bool verify(
        std::uint64_t realized_units,
        bool original_identity_preserved,
        bool exact_selected_equal
    ) const noexcept {
        return hhs_exact_pass219b_phase_locality_verify_realization(
            &plan_, realized_units,
            original_identity_preserved ? 1U : 0U,
            exact_selected_equal ? 1U : 0U,
            0U) == HHS_EXACT_STATUS_OK;
    }

private:
    explicit UniversalPhaseLocalityPlan(HHSExactPass219BPhaseLocalityPlanV1 plan) noexcept
        : plan_(plan) {}
    HHSExactPass219BPhaseLocalityPlanV1 plan_{};
};

}  // namespace hhs::rna

#endif

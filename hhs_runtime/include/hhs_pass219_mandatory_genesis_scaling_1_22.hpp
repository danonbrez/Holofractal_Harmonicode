#ifndef HHS_PASS219_MANDATORY_GENESIS_SCALING_1_22_HPP
#define HHS_PASS219_MANDATORY_GENESIS_SCALING_1_22_HPP

#include "hhs_pass219_mandatory_genesis_scaling_1_22.h"

#include <array>
#include <cstdint>
#include <stdexcept>

namespace hhs::rna {

class Pass219GenesisQuditView final {
public:
    Pass219GenesisQuditView() {
        const auto status = hhs_exact_pass219_genesis_descriptor(&descriptor_);
        if (status != HHS_EXACT_STATUS_OK)
            throw std::runtime_error("Pass219 Genesis descriptor construction failed");
        if (hhs_exact_pass219_genesis_validate(&descriptor_) != HHS_EXACT_STATUS_OK)
            throw std::runtime_error("Pass219 Genesis descriptor validation failed");
    }

    const HHSExactPass219GenesisDescriptorV1 &native() const noexcept {
        return descriptor_;
    }

    const HHSExactPass219GenesisCellV1 &cell(std::uint8_t index) const {
        if (index >= HHS_EXACT_PASS219_GENESIS_CELL_COUNT)
            throw std::out_of_range("Pass219 Genesis cell");
        return descriptor_.cells[index];
    }

    HHSExactPass219GenesisAddressV1 address(
        std::uint8_t cell81,
        std::uint8_t operation64
    ) const {
        HHSExactPass219GenesisAddressV1 out{};
        if (hhs_exact_pass219_genesis_address_encode(cell81, operation64, &out) !=
            HHS_EXACT_STATUS_OK)
            throw std::out_of_range("Pass219 Genesis address");
        return out;
    }

private:
    HHSExactPass219GenesisDescriptorV1 descriptor_{};
};

class Pass219MandatoryScalingPlan final {
public:
    explicit Pass219MandatoryScalingPlan(
        const HHSExactPass219MandatoryScalingRequestV1 &request
    ) {
        const auto status = hhs_exact_pass219_mandatory_scaling_plan(&request, &plan_);
        if (status != HHS_EXACT_STATUS_OK)
            throw std::runtime_error("Pass219 mandatory scaling plan failed");
    }

    const HHSExactPass219MandatoryScalingPlanV1 &native() const noexcept {
        return plan_;
    }

    void verify(const HHSExactPass219MandatoryScalingWitnessV1 &witness) const {
        if (hhs_exact_pass219_mandatory_scaling_verify(&plan_, &witness) !=
            HHS_EXACT_STATUS_OK)
            throw std::runtime_error("Pass219 mandatory scaling verification failed");
    }

private:
    HHSExactPass219MandatoryScalingPlanV1 plan_{};
};

inline HHSExactPass219MandatoryScalingRequestV1 make_pass219_data_ml_request(
    std::uint32_t work_kind,
    std::uint64_t source_count,
    std::uint32_t projection_p,
    std::uint32_t projection_q,
    std::uint32_t phase_depth = 1U
) {
    HHSExactPass219MandatoryScalingRequestV1 request{};
    request.struct_size = sizeof(request);
    request.version = hhs_exact_pass219_mandatory_genesis_scaling_version();
    request.work_kind = work_kind;
    request.phase_depth = phase_depth;
    request.source_count = source_count;
    request.candidate_family_count = 2U;
    request.projection_numerator_p = projection_p;
    request.projection_denominator_q = projection_q;
    request.exact_phase_selector_available = 1U;
    request.dirty_set_complete = 0U;
    for (std::uint32_t i = 0; i < phase_depth; ++i)
        request.phase_selected_s[i] = 1U;
    return request;
}

}  // namespace hhs::rna

#endif

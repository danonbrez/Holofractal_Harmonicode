#ifndef HHS_PASS219_CROSS_MODAL_REVERSIBLE_STATE_1_0_HPP
#define HHS_PASS219_CROSS_MODAL_REVERSIBLE_STATE_1_0_HPP

#include "hhs_pass219_cross_modal_reversible_state_1_0.h"

namespace hhs::pass219 {

class CrossModalStateWitness final {
public:
    static bool validate(const HHSExactPass219CrossModalStateWitnessV1& witness) noexcept {
        return hhs_exact_pass219_cross_modal_state_validate(&witness) ==
            HHS_PASS219_CROSS_MODAL_OK;
    }
};

class CrossModalWorkPlan final {
public:
    static HHSExactPass219CrossModalStatusV1 make(
        uint32_t depth,
        uint32_t modalities,
        uint32_t constraints_per_state,
        uint32_t cached_prefix_depth,
        uint32_t changed_constraints,
        bool prefix_proof_valid,
        bool hub_roundtrip_verified,
        HHSExactPass219CrossModalWorkPlanV1& out) noexcept {
        return hhs_exact_pass219_cross_modal_work_plan(
            depth,
            modalities,
            constraints_per_state,
            cached_prefix_depth,
            changed_constraints,
            prefix_proof_valid ? 1u : 0u,
            hub_roundtrip_verified ? 1u : 0u,
            &out);
    }
};

}  // namespace hhs::pass219

#endif

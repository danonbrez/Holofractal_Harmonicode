#ifndef HHS_PASS219_DYNAMIC_PARADOX_PHASE_CYCLE_1_0_HPP
#define HHS_PASS219_DYNAMIC_PARADOX_PHASE_CYCLE_1_0_HPP

#include "hhs_pass219_dynamic_paradox_phase_cycle_1_0.h"

namespace hhs::pass219 {

class DynamicParadoxPhaseCycle final {
public:
    static HHSExactPass219ParadoxStatusV1 analyze(
        const HHSExactPass219ParadoxProblemV1& problem,
        HHSExactPass219ParadoxWitnessV1& out) noexcept {
        return hhs_exact_pass219_paradox_analyze(&problem, &out);
    }

    static bool validate(
        const HHSExactPass219ParadoxProblemV1& problem,
        const HHSExactPass219ParadoxWitnessV1& witness) noexcept {
        return hhs_exact_pass219_paradox_witness_validate(&problem, &witness) ==
            HHS_EXACT_PASS219_PARADOX_OK;
    }

    static bool h36(HHSExactPass219H36ClosureWitnessV1& out) noexcept {
        return hhs_exact_pass219_h36_closure_identity(&out) ==
            HHS_EXACT_PASS219_PARADOX_OK;
    }
};

}  // namespace hhs::pass219

#endif

#ifndef HHS_PASS219_INHERITED_PASS199_1_27_HPP
#define HHS_PASS219_INHERITED_PASS199_1_27_HPP

#include "hhs_pass219_inherited_pass199_1_27.h"

namespace hhs::rna {

class InheritedPass199RepairedCalibrationAuthority final {
public:
    static constexpr uint32_t version() noexcept {
        return (HHS_EXACT_PASS219_INHERITED_PASS199_VERSION_MAJOR << 16) |
               (HHS_EXACT_PASS219_INHERITED_PASS199_VERSION_MINOR << 8) |
               HHS_EXACT_PASS219_INHERITED_PASS199_VERSION_PATCH;
    }

    static HHSExactStatus bind(
        const HHSExactPass199RepairedCalibrationWitnessV3 &witness,
        HHSExactPass219InheritedPass199BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass199_repaired_calibration_authority(&witness, &binding);
    }

    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool pass198_mutation_authority() noexcept { return false; }
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool full_replay_required_for_closure() noexcept { return true; }
};

}  // namespace hhs::rna

#endif

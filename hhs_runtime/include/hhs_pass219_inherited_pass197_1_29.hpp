#ifndef HHS_PASS219_INHERITED_PASS197_1_29_HPP
#define HHS_PASS219_INHERITED_PASS197_1_29_HPP

#include "hhs_pass219_inherited_pass197_1_29.h"

namespace hhs::rna {

class InheritedPass197RepairedHydrationCalibration final {
public:
    static constexpr uint32_t version() noexcept {
        return (HHS_EXACT_PASS219_INHERITED_PASS197_VERSION_MAJOR << 16) |
               (HHS_EXACT_PASS219_INHERITED_PASS197_VERSION_MINOR << 8) |
               HHS_EXACT_PASS219_INHERITED_PASS197_VERSION_PATCH;
    }

    static HHSExactStatus bind(
        const HHSExactPass197RepairedHydrationCalibrationWitnessV1 &witness,
        HHSExactPass219InheritedPass197BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass197_repaired_hydration_calibration(&witness, &binding);
    }

    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool pre_persistence_kernel_audit_required() noexcept { return true; }
    static constexpr bool full_replay_required_for_closure() noexcept { return true; }
    static constexpr uint32_t maximum_synchronous_parameter_states() noexcept {
        return HHS_EXACT_PASS197_DEFAULT_STATES;
    }
};

}  // namespace hhs::rna

#endif

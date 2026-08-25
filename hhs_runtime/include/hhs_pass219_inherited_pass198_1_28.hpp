#ifndef HHS_PASS219_INHERITED_PASS198_1_28_HPP
#define HHS_PASS219_INHERITED_PASS198_1_28_HPP

#include "hhs_pass219_inherited_pass198_1_28.h"

namespace hhs::rna {

class InheritedPass198RepairedCalibrationRegistry final {
public:
    static constexpr uint32_t version() noexcept {
        return (HHS_EXACT_PASS219_INHERITED_PASS198_VERSION_MAJOR << 16) |
               (HHS_EXACT_PASS219_INHERITED_PASS198_VERSION_MINOR << 8) |
               HHS_EXACT_PASS219_INHERITED_PASS198_VERSION_PATCH;
    }

    static HHSExactStatus bind(
        const HHSExactPass198RepairedCalibrationRegistryWitnessV1 &witness,
        HHSExactPass219InheritedPass198BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass198_repaired_calibration_registry(&witness, &binding);
    }

    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool api_mutation_authority() noexcept { return false; }
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool full_replay_required_for_verified_proofs() noexcept { return true; }
    static constexpr bool executed_negative_mutations_required_for_verified_proofs() noexcept { return true; }
    static constexpr uint32_t executed_negative_mutation_count() noexcept {
        return HHS_EXACT_PASS198_NEGATIVE_MUTATION_COUNT;
    }
};

}  // namespace hhs::rna

#endif

#ifndef HHS_PASS219_INHERITED_PASS200A_1_26_HPP
#define HHS_PASS219_INHERITED_PASS200A_1_26_HPP

#include "hhs_pass219_inherited_pass200a_1_26.h"

namespace hhs::rna {

class InheritedPass200ARepairedShadowAuthority final {
public:
    static constexpr uint32_t version() noexcept {
        return (HHS_EXACT_PASS219_INHERITED_PASS200A_VERSION_MAJOR << 16) |
               (HHS_EXACT_PASS219_INHERITED_PASS200A_VERSION_MINOR << 8) |
               HHS_EXACT_PASS219_INHERITED_PASS200A_VERSION_PATCH;
    }

    static HHSExactStatus bind(
        const HHSExactPass200ARepairedShadowWitnessV2 &witness,
        HHSExactPass219InheritedPass200ABindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass200a_repaired_shadow_authority(&witness, &binding);
    }

    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool reference_result_remains_authoritative() noexcept { return true; }
};

}  // namespace hhs::rna

#endif

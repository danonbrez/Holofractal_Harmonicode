#ifndef HHS_PASS219_INHERITED_PASS195_1_31_HPP
#define HHS_PASS219_INHERITED_PASS195_1_31_HPP

#include "hhs_pass219_inherited_pass195_1_31.h"

namespace hhs::rna {

class InheritedPass195RepairedKimiK3ContentEngine final {
public:
    static constexpr uint32_t version() noexcept {
        return (HHS_EXACT_PASS219_INHERITED_PASS195_VERSION_MAJOR << 16) |
               (HHS_EXACT_PASS219_INHERITED_PASS195_VERSION_MINOR << 8) |
               HHS_EXACT_PASS219_INHERITED_PASS195_VERSION_PATCH;
    }

    static HHSExactStatus bind(
        const HHSExactPass195RepairedKimiK3ContentEngineWitnessV1 &witness,
        HHSExactPass219InheritedPass195BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass195_repaired_kimi_k3_content_engine(&witness, &binding);
    }

    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool new_persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool external_provider_canonical_authority() noexcept { return false; }
    static constexpr bool browser_handoff_canonical_authority() noexcept { return false; }
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool strict_provider_plan_validation() noexcept { return true; }
    static constexpr bool image_analysis_requires_capability_admission() noexcept { return true; }
    static constexpr bool paid_generation_requires_operator_authorization() noexcept { return true; }
};

}  // namespace hhs::rna

#endif

#ifndef HHS_PASS219_INHERITED_PASS193_1_33_HPP
#define HHS_PASS219_INHERITED_PASS193_1_33_HPP

#include "hhs_pass219_inherited_pass193_1_33.h"

namespace hhs::rna {

class InheritedPass193HypersolidNativeEgress final {
public:
    static constexpr uint32_t version() noexcept {
        return (HHS_EXACT_PASS219_INHERITED_PASS193_VERSION_MAJOR << 16) |
               (HHS_EXACT_PASS219_INHERITED_PASS193_VERSION_MINOR << 8) |
               HHS_EXACT_PASS219_INHERITED_PASS193_VERSION_PATCH;
    }

    static HHSExactStatus bind(
        const HHSExactPass193HypersolidNativeEgressAuthorityWitnessV1 &witness,
        HHSExactPass219InheritedPass193BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass193_hypersolid_native_egress(&witness, &binding);
    }

    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool projection_authority() noexcept { return false; }
    static constexpr bool floating_point_canonical_authority() noexcept { return false; }
    static constexpr bool package_autoexec_authority() noexcept { return false; }
    static constexpr bool nft_identity_execution_authority() noexcept { return false; }
    static constexpr bool native_evidence_vm81_authority() noexcept { return false; }
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool exact_geometry_required() noexcept { return true; }
    static constexpr bool ordered_phase_history_required() noexcept { return true; }
    static constexpr bool pass192_nesting_preserved() noexcept { return true; }
    static constexpr bool explicit_install_action_required() noexcept { return true; }
};

}  // namespace hhs::rna

#endif

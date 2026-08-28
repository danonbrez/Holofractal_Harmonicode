#ifndef HHS_PASS219_INHERITED_PASS188_1_38_HPP
#define HHS_PASS219_INHERITED_PASS188_1_38_HPP

#include "hhs_pass219_inherited_pass188_1_38.h"

namespace hhs::rna {

class InheritedPass188CumulativeAuthority final {
public:
    static constexpr uint32_t version() noexcept {
        return (HHS_EXACT_PASS219_INHERITED_PASS188_VERSION_MAJOR << 16) |
               (HHS_EXACT_PASS219_INHERITED_PASS188_VERSION_MINOR << 8) |
               HHS_EXACT_PASS219_INHERITED_PASS188_VERSION_PATCH;
    }

    static HHSExactStatus bind(
        const HHSExactPass188CumulativeAuthorityWitnessV1 &witness,
        HHSExactPass219InheritedPass188BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass188_cumulative_authority(&witness, &binding);
    }

    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool floating_point_canonical_authority() noexcept { return false; }
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool license_vm81_witness_required() noexcept { return true; }
    static constexpr bool license_external_chain_authority() noexcept { return false; }
    static constexpr bool bott_canonical_mutation_authority() noexcept { return false; }
    static constexpr bool pass189_successor_preserved() noexcept { return true; }
};

}  // namespace hhs::rna

#endif

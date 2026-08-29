#ifndef HHS_PASS219_INHERITED_PASS186_1_40_HPP
#define HHS_PASS219_INHERITED_PASS186_1_40_HPP

#include "hhs_pass219_inherited_pass186_1_40.h"

namespace hhs::rna {

class InheritedPass186X64VM81Q144Authority final {
public:
    static constexpr uint32_t version() noexcept {
        return (HHS_EXACT_PASS219_INHERITED_PASS186_VERSION_MAJOR << 16) |
               (HHS_EXACT_PASS219_INHERITED_PASS186_VERSION_MINOR << 8) |
               HHS_EXACT_PASS219_INHERITED_PASS186_VERSION_PATCH;
    }

    static HHSExactStatus bind(
        const HHSExactPass186CumulativeAuthorityWitnessV1 &witness,
        HHSExactPass219InheritedPass186BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass186_cumulative_authority(&witness, &binding);
    }

    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool independent_opcode_authority() noexcept { return false; }
    static constexpr bool floating_point_canonical_authority() noexcept { return false; }
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool ordered_product_witness_is_identity() noexcept { return false; }
    static constexpr bool ordered_basis_tag_is_identity() noexcept { return true; }
    static constexpr bool historical_pass186_runtime_reused() noexcept { return true; }
    static constexpr bool pass187_successor_preserved() noexcept { return true; }
};

}  // namespace hhs::rna

#endif

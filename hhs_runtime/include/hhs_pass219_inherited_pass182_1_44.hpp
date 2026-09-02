#ifndef HHS_PASS219_INHERITED_PASS182_1_44_HPP
#define HHS_PASS219_INHERITED_PASS182_1_44_HPP

#include "hhs_pass219_inherited_pass182_1_44.h"

namespace hhs::rna {

class InheritedPass182UniversalHydrationAuthority final {
public:
    static constexpr bool source_tree_mutation_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool hash216_mutation_authority() noexcept { return false; }
    static constexpr bool floating_point_canonical_authority() noexcept { return false; }
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool hash216_archival_only() noexcept { return true; }
    static constexpr bool pass183_successor_preserved() noexcept { return true; }

    static HHSExactStatus bind(
        const HHSExactPass182UniversalHydrationWitnessV1 &witness,
        HHSExactPass219InheritedPass182BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass182_universal_hydration(&witness, &binding);
    }
};

}  // namespace hhs::rna
#endif

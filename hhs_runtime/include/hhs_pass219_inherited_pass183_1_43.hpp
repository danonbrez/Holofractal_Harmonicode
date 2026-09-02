#ifndef HHS_PASS219_INHERITED_PASS183_1_43_HPP
#define HHS_PASS219_INHERITED_PASS183_1_43_HPP

#include "hhs_pass219_inherited_pass183_1_43.h"

namespace hhs::rna {

class InheritedPass183ProbabilityHydrationAuthority final {
public:
    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool hash216_precommit_authority() noexcept { return false; }
    static constexpr bool hash216_archival_only() noexcept { return true; }
    static constexpr bool legacy_native_hash_witness_canonical() noexcept { return false; }
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool pass184_successor_preserved() noexcept { return true; }

    static HHSExactStatus bind(
        const HHSExactPass183ProbabilityHydrationWitnessV1 &witness,
        HHSExactPass219InheritedPass183BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass183_probability_hydration(&witness, &binding);
    }
};

}  // namespace hhs::rna
#endif

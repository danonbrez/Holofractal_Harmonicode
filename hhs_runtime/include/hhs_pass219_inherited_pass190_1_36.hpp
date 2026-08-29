#ifndef HHS_PASS219_INHERITED_PASS190_1_36_HPP
#define HHS_PASS219_INHERITED_PASS190_1_36_HPP

#include "hhs_pass219_inherited_pass190_1_36.h"

namespace hhs::rna {

class InheritedPass190FullCompletionAuthority final {
public:
    static constexpr uint32_t version() noexcept {
        return (HHS_EXACT_PASS219_INHERITED_PASS190_VERSION_MAJOR << 16) |
               (HHS_EXACT_PASS219_INHERITED_PASS190_VERSION_MINOR << 8) |
               HHS_EXACT_PASS219_INHERITED_PASS190_VERSION_PATCH;
    }

    static HHSExactStatus bind(
        const HHSExactPass190FullCompletionAuthorityWitnessV1 &witness,
        HHSExactPass219InheritedPass190BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass190_full_completion_authority(
            &witness, &binding
        );
    }

    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool floating_point_canonical_authority() noexcept { return false; }
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool full_contract_required() noexcept { return true; }
    static constexpr bool exact_registry_52_required() noexcept { return true; }
    static constexpr bool deterministic_replay_required() noexcept { return true; }
    static constexpr bool interface_parity_required() noexcept { return true; }
    static constexpr bool repository_hydration_reuse_required() noexcept { return true; }
    static constexpr bool pass191_successor_preserved() noexcept { return true; }
};

}  // namespace hhs::rna

#endif

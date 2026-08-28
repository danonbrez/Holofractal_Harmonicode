#ifndef HHS_PASS219_INHERITED_PASS187_1_39_HPP
#define HHS_PASS219_INHERITED_PASS187_1_39_HPP

#include "hhs_pass219_inherited_pass187_1_39.h"

namespace hhs::rna {

class InheritedPass187CumulativeAuthority final {
public:
    static constexpr uint32_t version() noexcept {
        return (HHS_EXACT_PASS219_INHERITED_PASS187_VERSION_MAJOR << 16) |
               (HHS_EXACT_PASS219_INHERITED_PASS187_VERSION_MINOR << 8) |
               HHS_EXACT_PASS219_INHERITED_PASS187_VERSION_PATCH;
    }

    static HHSExactStatus bind(
        const HHSExactPass187CumulativeAuthorityWitnessV1 &witness,
        HHSExactPass219InheritedPass187BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass187_cumulative_authority(&witness, &binding);
    }

    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool floating_point_canonical_authority() noexcept { return false; }
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool local_graph_event_evidence_is_authority() noexcept { return false; }
    static constexpr bool historical_bott_gap_closed_by_pass188() noexcept { return true; }
    static constexpr bool pass188_successor_preserved() noexcept { return true; }
};

}  // namespace hhs::rna

#endif

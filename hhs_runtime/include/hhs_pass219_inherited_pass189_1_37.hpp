#ifndef HHS_PASS219_INHERITED_PASS189_1_37_HPP
#define HHS_PASS219_INHERITED_PASS189_1_37_HPP

#include "hhs_pass219_inherited_pass189_1_37.h"

namespace hhs::rna {

class InheritedPass189CumulativeAuthority final {
public:
    static constexpr uint32_t version() noexcept {
        return (HHS_EXACT_PASS219_INHERITED_PASS189_VERSION_MAJOR << 16) |
               (HHS_EXACT_PASS219_INHERITED_PASS189_VERSION_MINOR << 8) |
               HHS_EXACT_PASS219_INHERITED_PASS189_VERSION_PATCH;
    }

    static HHSExactStatus bind(
        const HHSExactPass189CumulativeAuthorityWitnessV1 &witness,
        HHSExactPass219InheritedPass189BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass189_cumulative_authority(
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
    static constexpr bool calibration_in_progress() noexcept { return true; }
    static constexpr bool real_hardware_execution_authorized() noexcept { return false; }
    static constexpr bool software_test_adapters_only() noexcept { return true; }
    static constexpr bool deterministic_replay_required() noexcept { return true; }
    static constexpr bool pass190_successor_preserved() noexcept { return true; }
};

}  // namespace hhs::rna

#endif

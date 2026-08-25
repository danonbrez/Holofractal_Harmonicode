#ifndef HHS_PASS219_INHERITED_PASS196_1_30_HPP
#define HHS_PASS219_INHERITED_PASS196_1_30_HPP

#include "hhs_pass219_inherited_pass196_1_30.h"

namespace hhs::rna {

class InheritedPass196RepairedIntegratedEnvironment final {
public:
    static constexpr uint32_t version() noexcept {
        return (HHS_EXACT_PASS219_INHERITED_PASS196_VERSION_MAJOR << 16) |
               (HHS_EXACT_PASS219_INHERITED_PASS196_VERSION_MINOR << 8) |
               HHS_EXACT_PASS219_INHERITED_PASS196_VERSION_PATCH;
    }

    static HHSExactStatus bind(
        const HHSExactPass196RepairedIntegratedEnvironmentWitnessV1 &witness,
        HHSExactPass219InheritedPass196BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass196_repaired_integrated_environment(&witness, &binding);
    }

    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool new_persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool vector_store_source_authority() noexcept { return false; }
    static constexpr bool browser_projection_authority() noexcept { return false; }
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool vm81_receipt_required_for_persistence() noexcept { return true; }
    static constexpr bool failed_scan_quarantines_current_success() noexcept { return true; }
};

}  // namespace hhs::rna

#endif

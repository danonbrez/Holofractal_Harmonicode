#ifndef HHS_PASS219_INHERITED_PASS184_1_42_HPP
#define HHS_PASS219_INHERITED_PASS184_1_42_HPP
#include "hhs_pass219_inherited_pass184_1_42.h"
namespace hhs::rna {
class InheritedPass184PortableRuntimeAuthority final {
public:
    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool package_is_projection_authority() noexcept { return false; }
    static constexpr bool supervised_service_is_process_authority_only() noexcept { return true; }
    static constexpr bool pass185_successor_preserved() noexcept { return true; }
    static HHSExactStatus bind(const HHSExactPass184PortableRuntimeWitnessV1 &witness,
                               HHSExactPass219InheritedPass184BindingV1 &binding) noexcept {
        return hhs_exact_pass219_bind_pass184_portable_runtime(&witness, &binding);
    }
};
}
#endif

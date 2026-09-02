#ifndef HHS_PASS219_INHERITED_PASS180_1_46_HPP
#define HHS_PASS219_INHERITED_PASS180_1_46_HPP

#include "hhs_pass219_inherited_pass180_1_46.h"

namespace hhs::rna {

class InheritedPass180ApplicationFactoryAuthority final {
public:
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool independent_vm81_authority() noexcept { return false; }
    static constexpr bool independent_hash72_authority() noexcept { return false; }
    static constexpr bool hash216_mutation_authority() noexcept { return false; }
    static constexpr bool floating_point_canonical_authority() noexcept { return false; }
    static constexpr bool hash72_follows_vm81_mutation() noexcept { return true; }
    static constexpr bool external_success_may_be_fabricated() noexcept { return false; }
    static constexpr bool terminal_pass180_completion_claimed() noexcept { return true; }
    static constexpr bool repair_forward_required() noexcept { return false; }
    static constexpr uint32_t remaining_terminal_obligations() noexcept { return 0U; }

    static HHSExactStatus bind(
        const HHSExactPass180ApplicationFactoryWitnessV1 &witness,
        HHSExactPass219InheritedPass180BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass180_application_factory(&witness, &binding);
    }
};

}  // namespace hhs::rna
#endif

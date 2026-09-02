#ifndef HHS_PASS219_INHERITED_PASS179_1_47_HPP
#define HHS_PASS219_INHERITED_PASS179_1_47_HPP

#include "hhs_pass219_inherited_pass179_1_47.h"

namespace hhs::rna {

class InheritedPass179NativeGraphicsAuthority final {
public:
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool independent_vm81_authority() noexcept { return false; }
    static constexpr bool independent_hash72_commit_authority() noexcept { return false; }
    static constexpr bool hash216_mutation_authority() noexcept { return false; }
    static constexpr bool gpu_mutation_authority() noexcept { return false; }
    static constexpr bool browser_mutation_authority() noexcept { return false; }
    static constexpr bool floating_point_canonical_authority() noexcept { return false; }
    static constexpr bool software_renderer_is_projection_only() noexcept { return true; }
    static constexpr bool terminal_pass179_completion_claimed() noexcept { return false; }
    static constexpr bool repair_forward_required() noexcept { return true; }
    static constexpr uint32_t remaining_terminal_categories() noexcept {
        return HHS_EXACT_PASS179_I147_REMAINING_TERMINAL_CATEGORY_COUNT;
    }

    static HHSExactStatus bind(
        const HHSExactPass179NativeGraphicsWitnessV1 &witness,
        HHSExactPass219InheritedPass179BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass179_native_graphics(&witness, &binding);
    }
};

}  // namespace hhs::rna
#endif

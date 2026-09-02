#ifndef HHS_PASS219_INHERITED_PASS181_1_45_HPP
#define HHS_PASS219_INHERITED_PASS181_1_45_HPP

#include "hhs_pass219_inherited_pass181_1_45.h"

namespace hhs::rna {

class InheritedPass181GraphicsHydrationAuthority final {
public:
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool independent_vm81_authority() noexcept { return false; }
    static constexpr bool independent_hash72_authority() noexcept { return false; }
    static constexpr bool hash216_mutation_authority() noexcept { return false; }
    static constexpr bool floating_point_canonical_authority() noexcept { return false; }
    static constexpr bool threejs_final_frame_authority() noexcept { return false; }
    static constexpr bool legacy_direct_constraint_promotion_allowed() noexcept { return false; }
    static constexpr bool terminal_pass181_completion_claimed() noexcept { return false; }
    static constexpr bool repair_forward_required() noexcept { return true; }
    static constexpr uint32_t remaining_terminal_obligations() noexcept {
        return HHS_EXACT_PASS181_I145_REMAINING_TERMINAL_OBLIGATIONS;
    }

    static HHSExactStatus bind(
        const HHSExactPass181GraphicsHydrationWitnessV1 &witness,
        HHSExactPass219InheritedPass181BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass181_graphics_hydration(&witness, &binding);
    }
};

}  // namespace hhs::rna
#endif

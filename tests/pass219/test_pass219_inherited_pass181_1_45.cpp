#include <assert.h>
#include "hhs_runtime_exact_abi.h"
#include "hhs_pass219_inherited_pass181_1_45.hpp"

int main() {
    using H = hhs::rna::InheritedPass181GraphicsHydrationAuthority;
    static_assert(H::singleton_vm81_authority_remains_inherited());
    static_assert(!H::independent_vm81_authority());
    static_assert(!H::independent_hash72_authority());
    static_assert(!H::hash216_mutation_authority());
    static_assert(!H::floating_point_canonical_authority());
    static_assert(!H::threejs_final_frame_authority());
    static_assert(!H::legacy_direct_constraint_promotion_allowed());
    static_assert(!H::terminal_pass181_completion_claimed());
    static_assert(H::repair_forward_required());
    static_assert(H::remaining_terminal_obligations() == 3U);
    assert(hhs_exact_pass219_inherited_pass181_version() == ((1U << 16) | (45U << 8)));
    return 0;
}

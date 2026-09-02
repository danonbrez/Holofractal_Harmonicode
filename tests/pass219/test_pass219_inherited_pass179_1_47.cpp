#include <assert.h>
#include "hhs_runtime_exact_abi.h"
#include "hhs_pass219_inherited_pass179_1_47.hpp"

int main() {
    using H = hhs::rna::InheritedPass179NativeGraphicsAuthority;
    static_assert(H::singleton_vm81_authority_remains_inherited());
    static_assert(!H::independent_vm81_authority());
    static_assert(!H::independent_hash72_commit_authority());
    static_assert(!H::hash216_mutation_authority());
    static_assert(!H::gpu_mutation_authority());
    static_assert(!H::browser_mutation_authority());
    static_assert(!H::floating_point_canonical_authority());
    static_assert(H::software_renderer_is_projection_only());
    static_assert(!H::terminal_pass179_completion_claimed());
    static_assert(H::repair_forward_required());
    static_assert(H::remaining_terminal_categories() == 10U);
    assert(hhs_exact_pass219_inherited_pass179_version() == ((1U << 16) | (47U << 8)));
    return 0;
}

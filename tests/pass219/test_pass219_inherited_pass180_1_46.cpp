#include <assert.h>
#include "hhs_runtime_exact_abi.h"
#include "hhs_pass219_inherited_pass180_1_46.hpp"

int main() {
    using H = hhs::rna::InheritedPass180ApplicationFactoryAuthority;
    static_assert(H::singleton_vm81_authority_remains_inherited());
    static_assert(!H::independent_vm81_authority());
    static_assert(!H::independent_hash72_authority());
    static_assert(!H::hash216_mutation_authority());
    static_assert(!H::floating_point_canonical_authority());
    static_assert(H::hash72_follows_vm81_mutation());
    static_assert(!H::external_success_may_be_fabricated());
    static_assert(H::terminal_pass180_completion_claimed());
    static_assert(!H::repair_forward_required());
    static_assert(H::remaining_terminal_obligations() == 0U);
    assert(hhs_exact_pass219_inherited_pass180_version() == ((1U << 16) | (46U << 8)));
    return 0;
}

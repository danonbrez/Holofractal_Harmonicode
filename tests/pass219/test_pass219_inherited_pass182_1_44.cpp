#include <assert.h>
#include "hhs_runtime_exact_abi.h"
#include "hhs_pass219_inherited_pass182_1_44.hpp"

int main() {
    using H = hhs::rna::InheritedPass182UniversalHydrationAuthority;
    static_assert(!H::source_tree_mutation_authority());
    static_assert(!H::vm81_mutation_authority());
    static_assert(!H::hash72_clock_authority());
    static_assert(!H::hash216_mutation_authority());
    static_assert(!H::floating_point_canonical_authority());
    static_assert(H::singleton_vm81_authority_remains_inherited());
    static_assert(H::hash216_archival_only());
    static_assert(H::pass183_successor_preserved());
    assert(hhs_exact_pass219_inherited_pass182_version() == ((1U << 16) | (44U << 8)));
    return 0;
}

#include <assert.h>
#include "hhs_runtime_exact_abi.h"
#include "hhs_pass219_inherited_pass177_1_49.hpp"

int main() {
    using H = hhs::rna::InheritedPass177CreationWorkflows;
    static_assert(H::pass_number() == 177U);
    static_assert(!H::terminal_pass177_completion_claimed());
    static_assert(H::repair_forward_required());
    static_assert(H::remaining_terminal_category_count() == 12U);
    static_assert(H::singleton_vm81_inherited());
    static_assert(!H::independent_vm81_authority());
    static_assert(!H::independent_hash72_commit_authority());
    static_assert(!H::hash216_mutation_authority());
    static_assert(!H::browser_identity_authority());
    static_assert(!H::memory_checkpoint_authority());
    static_assert(H::historical_stage_truth_preserved());
    assert(hhs_exact_pass219_inherited_pass177_version() == ((1U << 16) | (49U << 8)));
    return 0;
}

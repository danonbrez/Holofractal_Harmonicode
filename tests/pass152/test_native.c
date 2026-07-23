#include <assert.h>
#include <stdio.h>
#include "../../hhs_runtime/pass152/hhs152_native.h"

int main(void) {
    hhs_p152_closure_flags all = {1,1,1,1,1,1,1};
    hhs_p152_closure_flags missing = {1,1,1,1,0,1,1};
    assert(hhs_p152_closure_satisfied(&all) == 1);
    assert(hhs_p152_closure_satisfied(&missing) == 0);
    assert(hhs_p152_commit_gate(&all, 1, 1) == 1);
    assert(hhs_p152_commit_gate(&all, 0, 1) == 0);
    assert(hhs_p152_transition_allowed(HHS_P152_PROVISIONAL, HHS_P152_VERIFIED) == 1);
    assert(hhs_p152_transition_allowed(HHS_P152_COMMITTED, HHS_P152_INVALIDATED) == 0);
    assert(hhs_p152_provisional_may_advance_hash72() == 0);

    hhs_p152_recursive_control_boundary lawful = {0,0,0,0,0,0,1};
    hhs_p152_recursive_control_boundary truth_mutation = {1,0,0,0,0,0,1};
    hhs_p152_recursive_control_boundary history_rewrite = {0,0,0,0,1,0,1};
    hhs_p152_recursive_control_boundary not_policy = {0,0,0,0,0,0,0};
    assert(hhs_p152_recursive_control_gate(&lawful) == 1);
    assert(hhs_p152_recursive_control_gate(&truth_mutation) == 0);
    assert(hhs_p152_recursive_control_gate(&history_rewrite) == 0);
    assert(hhs_p152_recursive_control_gate(&not_policy) == 0);
    assert(hhs_p152_history_append_gate(7, 8, 1) == 1);
    assert(hhs_p152_history_append_gate(7, 7, 1) == 0);
    assert(hhs_p152_history_append_gate(7, 8, 0) == 0);
    puts("HHS_PASS152_NATIVE_TESTS_PASSED");
    return 0;
}

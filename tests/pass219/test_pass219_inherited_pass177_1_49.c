#include <assert.h>
#include <string.h>
#include "hhs_runtime_exact_abi.h"

static void fill(char out[HHS_EXACT_PASS177_I149_GIT_SHA_STRLEN], const char *value) {
    memcpy(out, value, HHS_EXACT_PASS177_I149_GIT_SHA_LEN);
    out[HHS_EXACT_PASS177_I149_GIT_SHA_LEN] = '\0';
}

static HHSExactPass177WorkflowWitnessV1 witness(void) {
    HHSExactPass177WorkflowWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass177_version();
    w.contract_preserved = 1U;
    w.historical_merge_preserved = 1U;
    w.module_library_bound = 1U;
    w.project_factory_bound = 1U;
    w.workflow_engine_bound = 1U;
    w.browser_candidate_identity_bound = 1U;
    w.vm81_project_admission_bound = 1U;
    w.vm81_checkpoint_admission_bound = 1U;
    w.historical_stage_truth_preserved = 1U;
    w.pre_cumulative_validation_green = 1U;
    w.pass178_successor_preserved = 1U;
    w.terminal_pass177_completion = 0U;
    w.repair_forward_required = 1U;
    w.remaining_terminal_category_count = HHS_EXACT_PASS177_I149_REMAINING_TERMINAL_CATEGORY_COUNT;
    fill(w.validated_authority_head, "15fa5a458c6755eab4d1af4b405b83b3467d45d9");
    fill(w.authority_receipt_blob, "357365c6c55df87b1c199e64fb53d889c7315249");
    return w;
}

int main(void) {
    HHSExactPass177WorkflowWitnessV1 w = witness();
    HHSExactPass219InheritedPass177BindingV1 b;
    assert(hhs_exact_pass219_bind_pass177_creation_workflows(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.pass_number == 177U);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.historical_runtime_reachable == 1U);
    assert(b.browser_workflow_bound == 1U);
    assert(b.vm81_project_admission_bound == 1U);
    assert(b.vm81_checkpoint_admission_bound == 1U);
    assert(b.historical_stage_truth_preserved == 1U);
    assert(b.no_new_authority_bound == 1U);
    assert(b.terminal_completion_claimed == 0U);
    assert(b.repair_forward_required == 1U);
    assert(b.remaining_terminal_category_count == 12U);
    assert(b.independent_vm81_authority == 0U);
    assert(b.independent_hash72_commit_authority == 0U);
    assert(b.hash216_mutation_authority == 0U);
    assert(b.browser_identity_authority == 0U);
    assert(b.memory_checkpoint_authority == 0U);

    w.browser_identity_authority = 1U;
    assert(hhs_exact_pass219_bind_pass177_creation_workflows(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.terminal_pass177_completion = 1U;
    assert(hhs_exact_pass219_bind_pass177_creation_workflows(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}

#include <assert.h>
#include <string.h>
#include "hhs_runtime_exact_abi.h"

static void fill(char out[HHS_EXACT_PASS180_I146_GIT_SHA_STRLEN], const char *value) {
    memcpy(out, value, HHS_EXACT_PASS180_I146_GIT_SHA_LEN);
    out[HHS_EXACT_PASS180_I146_GIT_SHA_LEN] = '\0';
}

static HHSExactPass180ApplicationFactoryWitnessV1 witness(void) {
    HHSExactPass180ApplicationFactoryWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass180_version();
    w.historical_contract_preserved = 1U;
    w.historical_implementation_preserved = 1U;
    w.historical_ci_green = 1U;
    w.module_catalog_bound = 1U;
    w.workflow_catalog_bound = 1U;
    w.dependency_closure_bound = 1U;
    w.incremental_planning_bound = 1U;
    w.bounded_lifecycle_bound = 1U;
    w.eight_checkpoint_lifecycle_bound = 1U;
    w.deterministic_source_zip_bound = 1U;
    w.deterministic_project_replay_bound = 1U;
    w.visual_server_routes_bound = 1U;
    w.vm81_canonical_mutation_repair_bound = 1U;
    w.hash72_after_vm81_bound = 1U;
    w.external_success_nonfabrication_bound = 1U;
    w.singleton_vm81_bound = 1U;
    w.pass181_successor_preserved = 1U;
    w.i146_dependency_scoped_validation_green = 1U;
    w.terminal_pass180_completion = 1U;
    fill(w.historical_green_head, "9d0e8ef4a60d450f69ef5bf4dab3ad1c18b30dba");
    fill(w.frozen_i145_checkpoint, "4762e1b5428f09a957905cc59669b7c9aeb36f06");
    fill(w.i145_validation_receipt_blob, "331ca8095e5828dc8de0846f6c96c0336e260293");
    return w;
}

int main(void) {
    HHSExactPass180ApplicationFactoryWitnessV1 w = witness();
    HHSExactPass219InheritedPass180BindingV1 b;
    assert(hhs_exact_pass219_bind_pass180_application_factory(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.pass_number == 180U);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.vm81_canonical_mutation_repair_bound == 1U);
    assert(b.hash72_after_vm81_bound == 1U);
    assert(b.external_success_nonfabrication_bound == 1U);
    assert(b.singleton_vm81_bound == 1U);
    assert(b.no_new_authority_bound == 1U);
    assert(b.terminal_completion_claimed == 1U);
    assert(b.repair_forward_required == 0U);
    assert(b.remaining_terminal_obligation_count == 0U);
    assert(b.independent_vm81_authority == 0U);
    assert(b.independent_hash72_authority == 0U);
    assert(b.hash216_mutation_authority == 0U);
    assert(b.floating_point_canonical_authority == 0U);

    w.vm81_canonical_mutation_repair_bound = 0U;
    assert(hhs_exact_pass219_bind_pass180_application_factory(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.terminal_pass180_completion = 0U;
    assert(hhs_exact_pass219_bind_pass180_application_factory(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}

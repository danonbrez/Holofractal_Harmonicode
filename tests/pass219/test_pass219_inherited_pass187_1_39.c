#include "hhs_pass219_inherited_pass187_1_39.h"

#include <assert.h>
#include <string.h>

static HHSExactPass187CumulativeAuthorityWitnessV1 witness(void) {
    HHSExactPass187CumulativeAuthorityWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass187_version();
    w.composition_contract_preserved = 1U;
    w.composition_completion_verified = 1U;
    w.composition_acceptance_scenario_count = 12U;
    w.harmonicode_roundtrip_verified = 1U;
    w.incremental_recomposition_verified = 1U;
    w.linux_adapter_integration_verified = 1U;
    w.visual_browser_acceptance_verified = 1U;
    w.cold_restart_recovery_verified = 1U;
    w.inherited_vm81_witness_required = 1U;
    w.historical_bott_contract_preserved = 1U;
    w.historical_bott_baseline_verified = 1U;
    w.historical_bott_runtime_gap_record_preserved = 1U;
    w.pass188_bott_runtime_closure_preserved = 1U;
    w.pass188_successor_preserved = 1U;

    strcpy(w.composition_contract_commit, "6584c8e118eb73e0884165b3d1afd1ec84f34f57");
    strcpy(w.historical_bott_merge_commit, "5db45d6b72b93132997f815d16df4540fd13adfc");
    strcpy(w.pass188_bott_runtime_commit, "c77e3feef42448a111d8b8912a1d1cb157d51925");
    strcpy(w.composition_completion_head, "c36beacd8d6748f65c30ca3b02ac237eac38c34d");
    strcpy(w.frozen_i138_commit, "6f59481b48903759395dfbe94a4dc61097b306b1");
    strcpy(w.composition_contract_blob, "ac25bc7084b1a5e7202e25da47a5890307cf5e27");
    strcpy(w.bott_receipt_blob, "79a8915337397a06d30bee4452ee273fa2bae105");
    strcpy(w.composition_runtime_blob, "e5b41b12cb24158010f0dffc7a88b6f2740e5d2b");
    strcpy(w.composition_tests_blob, "64aa62e1ace43b49f8dbf4951ef0b87707129aeb");
    strcpy(w.composition_browser_blob, "2fce626b94a4895800a9ffb48f3201078631d037");
    strcpy(w.composition_workflow_blob, "7692878d88efb260e9430295648e384e78e5a50d");
    return w;
}

int main(void) {
    HHSExactPass187CumulativeAuthorityWitnessV1 w = witness();
    HHSExactPass219InheritedPass187BindingV1 b;

    assert(hhs_exact_pass219_bind_pass187_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.pass_number == 187U);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.composition_contract_bound == 1U);
    assert(b.composition_completion_bound == 1U);
    assert(b.harmonicode_order_bound == 1U);
    assert(b.incremental_recomposition_bound == 1U);
    assert(b.linux_adapter_bound == 1U);
    assert(b.visual_interaction_bound == 1U);
    assert(b.replay_restart_bound == 1U);
    assert(b.vm81_witness_boundary_bound == 1U);
    assert(b.historical_bott_baseline_bound == 1U);
    assert(b.pass188_bott_runtime_closure_bound == 1U);
    assert(b.pass188_successor_bound == 1U);
    assert(b.no_new_authority_bound == 1U);
    assert(b.float_is_canonical_authority == 0U);

    w = witness();
    w.independent_vm81_authority = 1U;
    assert(hhs_exact_pass219_bind_pass187_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.local_event_evidence_is_mutation_authority = 1U;
    assert(hhs_exact_pass219_bind_pass187_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.float_canonical_authority = 1U;
    assert(hhs_exact_pass219_bind_pass187_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    strcpy(w.composition_runtime_blob, "0000000000000000000000000000000000000000");
    assert(hhs_exact_pass219_bind_pass187_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}

#include "hhs_pass219_inherited_pass188_1_38.h"

#include <assert.h>
#include <string.h>

static HHSExactPass188CumulativeAuthorityWitnessV1 witness(void) {
    HHSExactPass188CumulativeAuthorityWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass188_version();
    w.license_contract_preserved = 1U;
    w.license_completion_verified = 1U;
    w.license_acceptance_scenario_count = 16U;
    w.immutable_content_versions = 1U;
    w.immutable_license_versions = 1U;
    w.inherited_vm81_witness_required = 1U;
    w.license_hash72_event_chain = 1U;
    w.license_hash216_identity = 1U;
    w.license_deterministic_replay = 1U;
    w.license_materialized_integrity = 1U;
    w.license_cold_restart_recovery = 1U;
    w.license_pass187_graph_impact = 1U;
    w.license_transfer_delegation = 1U;
    w.license_revocation_expiry = 1U;
    w.license_exact_royalty = 1U;
    w.bott_runtime_verified = 1U;
    w.bott_projected_address_count = 1259712U;
    w.bott_deterministic_replay = 1U;
    w.pass189_successor_preserved = 1U;

    strcpy(w.license_contract_commit, "50aec3f624fe6cbaefa3220b7d709bb1b388a942");
    strcpy(w.bott_runtime_commit, "c77e3feef42448a111d8b8912a1d1cb157d51925");
    strcpy(w.license_completion_head, "8e6f209aa8974da30d0b1dcb85a7ca2dc10060c6");
    strcpy(w.frozen_i137_commit, "ef27a1caf0d977e0f767b13126dba8fe49b09dab");
    strcpy(w.license_contract_blob, "871ed3fff0a677ad6173eb00a099d010ac1a730b");
    strcpy(w.bott_receipt_blob, "492d60716896c66cdb507f6e76163d988d1d41e6");
    strcpy(w.license_runtime_blob, "9ead3669a04b211be09adca66b35f37269350056");
    strcpy(w.license_tests_blob, "e55466723c0f15667fea93ecbb076a1f2fb5d570");
    strcpy(w.license_workflow_blob, "943f93de78036622be13fe6f530e2a5c596de7e6");
    return w;
}

int main(void) {
    HHSExactPass188CumulativeAuthorityWitnessV1 w = witness();
    HHSExactPass219InheritedPass188BindingV1 b;

    assert(hhs_exact_pass219_bind_pass188_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.pass_number == 188U);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.license_contract_bound == 1U);
    assert(b.license_completion_bound == 1U);
    assert(b.immutable_lineage_bound == 1U);
    assert(b.vm81_witness_boundary_bound == 1U);
    assert(b.license_receipt_replay_bound == 1U);
    assert(b.legacy_transfer_revocation_bound == 1U);
    assert(b.pass187_impact_bound == 1U);
    assert(b.bott_runtime_bound == 1U);
    assert(b.bott_nonmutation_bound == 1U);
    assert(b.pass189_successor_bound == 1U);
    assert(b.no_new_authority_bound == 1U);
    assert(b.float_is_canonical_authority == 0U);

    w = witness();
    w.license_external_chain_required = 1U;
    assert(hhs_exact_pass219_bind_pass188_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.license_independent_vm81_authority = 1U;
    assert(hhs_exact_pass219_bind_pass188_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.bott_canonical_mutation_authority = 1U;
    assert(hhs_exact_pass219_bind_pass188_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    strcpy(w.license_runtime_blob, "0000000000000000000000000000000000000000");
    assert(hhs_exact_pass219_bind_pass188_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}

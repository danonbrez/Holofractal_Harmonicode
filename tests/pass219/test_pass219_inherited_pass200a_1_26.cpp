#include "hhs_pass219_inherited_pass200a_1_26.hpp"

#include <cassert>
#include <cstring>

static HHSExactPass200ARepairedShadowWitnessV2 make_witness() {
    HHSExactPass200ARepairedShadowWitnessV2 w{};
    w.struct_size = static_cast<uint32_t>(sizeof(w));
    w.version = hhs::rna::InheritedPass200ARepairedShadowAuthority::version();
    w.primary_pull_request = 138U;
    w.production_envelopes = 4U;
    w.production_states = 290U;
    w.production_branch_jobs = 580U;
    w.production_admitted = 263U;
    w.production_rejected = 27U;
    w.production_vm5184_comparisons = 1363392U;
    w.negative_mutations = 24U;
    w.optimization_bundles = 4U;
    w.shadow_matches = 4U;
    w.reference_returns = 4U;
    w.vm81_receipt_chain_provenance_required = 1U;
    w.reference_lane_independently_executed = 1U;
    w.candidate_lane_independently_executed = 1U;
    w.exact_semantic_comparison_required = 1U;
    w.exact_witness_comparison_required = 1U;
    w.exact_replay_comparison_required = 1U;
    w.shadow_payload_hash_revalidated = 1U;
    w.shadow_event_payload_binding_required = 1U;
    w.current_pass198_proof_required = 1U;
    w.revoked_pass198_proof_rejected = 1U;
    w.production_profile_identity_required = 1U;
    w.production_acceptance_totals_required = 1U;
    w.singleton_upgraded_in_place = 1U;
    w.duplicate_default_authority_forbidden = 1U;
    w.partial_holdout_state_recoverable = 1U;
    w.reference_result_remains_authoritative = 1U;
    w.pass200b_successor_preserved = 1U;
    std::strcpy(w.historical_base_commit, "649be68e1566002ce66c919463a386b8018bc2fb");
    std::strcpy(w.historical_reviewed_head, "5ef1d3ab6c0ceb3a20d468447b991066626de366");
    std::strcpy(w.accepted_merge_commit, "eee6670f7d3c6743e1bf32c7e42a4150d07351e3");
    std::strcpy(w.frozen_i125_commit, "21bf16233a0c4573a754c29686d13782bcc4fc44");
    std::strcpy(w.contract_blob, "46c9a8fdbacb80e1d136a67bd4b48e2e4a82c367");
    std::strcpy(w.runtime_v1_blob, "1f6d7b0092da3916705a58af9ae2ad2c22c3bab3");
    std::strcpy(w.historical_production_blob, "521e89fc1c8b3067574884fb69a79a4d856887a1");
    std::strcpy(w.historical_workflow_blob, "2817d207568e43f5621d56267f076503fa7e9628");
    std::strcpy(w.historical_routes_blob, "3f123916520c6b7f877903d50bb924992895bff6");
    std::strcpy(w.historical_test_blob, "068a5e15e5a877ff439ab42535b1429cf77b00ad");
    std::strcpy(w.historical_restart_blob, "984950272cd9463319b163cb7a2a1e2037c0da12");
    return w;
}

int main() {
    using Surface = hhs::rna::InheritedPass200ARepairedShadowAuthority;
    static_assert(!Surface::mutation_authority());
    static_assert(!Surface::persistence_authority());
    static_assert(!Surface::hash72_clock_authority());
    static_assert(!Surface::vm81_mutation_authority());
    static_assert(!Surface::candidate_authority());
    static_assert(Surface::reference_result_remains_authoritative());

    auto w = make_witness();
    HHSExactPass219InheritedPass200ABindingV1 b{};
    assert(Surface::bind(w, b) == HHS_EXACT_STATUS_OK);
    assert(b.inherited_defects_repaired == 1U);
    assert(b.pass200b_successor_bound == 1U);
    assert(b.pass219_new_candidate_authority == 0U);
    return 0;
}

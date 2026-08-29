#include "hhs_pass219_inherited_pass188_1_38.hpp"

#include <cassert>
#include <cstring>

static HHSExactPass188CumulativeAuthorityWitnessV1 witness() {
    HHSExactPass188CumulativeAuthorityWitnessV1 w{};
    w.struct_size = sizeof(w);
    w.version = hhs::rna::InheritedPass188CumulativeAuthority::version();
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

    std::strcpy(w.license_contract_commit, "50aec3f624fe6cbaefa3220b7d709bb1b388a942");
    std::strcpy(w.bott_runtime_commit, "c77e3feef42448a111d8b8912a1d1cb157d51925");
    std::strcpy(w.license_completion_head, "8e6f209aa8974da30d0b1dcb85a7ca2dc10060c6");
    std::strcpy(w.frozen_i137_commit, "ef27a1caf0d977e0f767b13126dba8fe49b09dab");
    std::strcpy(w.license_contract_blob, "871ed3fff0a677ad6173eb00a099d010ac1a730b");
    std::strcpy(w.bott_receipt_blob, "492d60716896c66cdb507f6e76163d988d1d41e6");
    std::strcpy(w.license_runtime_blob, "9ead3669a04b211be09adca66b35f37269350056");
    std::strcpy(w.license_tests_blob, "e55466723c0f15667fea93ecbb076a1f2fb5d570");
    std::strcpy(w.license_workflow_blob, "943f93de78036622be13fe6f530e2a5c596de7e6");
    return w;
}

int main() {
    using hhs::rna::InheritedPass188CumulativeAuthority;
    auto w = witness();
    HHSExactPass219InheritedPass188BindingV1 b{};

    assert(InheritedPass188CumulativeAuthority::bind(w, b) == HHS_EXACT_STATUS_OK);
    assert(b.pass_number == 188U);
    assert(b.license_completion_bound == 1U);
    assert(b.bott_nonmutation_bound == 1U);
    assert(b.pass189_successor_bound == 1U);
    assert(b.no_new_authority_bound == 1U);

    static_assert(!InheritedPass188CumulativeAuthority::candidate_authority());
    static_assert(!InheritedPass188CumulativeAuthority::mutation_authority());
    static_assert(!InheritedPass188CumulativeAuthority::persistence_authority());
    static_assert(!InheritedPass188CumulativeAuthority::hash72_clock_authority());
    static_assert(!InheritedPass188CumulativeAuthority::vm81_mutation_authority());
    static_assert(!InheritedPass188CumulativeAuthority::floating_point_canonical_authority());
    static_assert(InheritedPass188CumulativeAuthority::singleton_vm81_authority_remains_inherited());
    static_assert(InheritedPass188CumulativeAuthority::license_vm81_witness_required());
    static_assert(!InheritedPass188CumulativeAuthority::license_external_chain_authority());
    static_assert(!InheritedPass188CumulativeAuthority::bott_canonical_mutation_authority());
    static_assert(InheritedPass188CumulativeAuthority::pass189_successor_preserved());
    return 0;
}

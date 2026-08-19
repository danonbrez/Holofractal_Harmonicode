#include "hhs_pass219_inherited_pass209_1_16.hpp"

#include <cassert>
#include <cstring>

static HHSExactPass209RuntimeBootstrapWitnessV1 witness() {
    HHSExactPass209RuntimeBootstrapWitnessV1 w{};
    w.struct_size = static_cast<uint32_t>(sizeof(w));
    w.version = hhs_exact_pass219_inherited_pass209_version();
    w.runtime_verified = 1U;
    w.status_catalog_count = 9U;
    w.required_operation_count = 7U;
    w.persistent_cache_bound = 1U;
    w.stale_while_revalidate_bound = 1U;
    w.isolated_sequential_probe_bound = 1U;
    w.cold_miss_warming_projection_bound = 1U;
    w.direct_status_intercept_bound = 1U;
    w.browser_readiness_coordination_bound = 1U;
    w.external_state_roots_bound = 1U;
    w.repository_checkout_readonly_bound = 1U;
    w.canonical_backend_authority_preserved = 1U;
    w.cache_projection_noncanonical = 1U;
    w.pass210_inherits_pass209 = 1U;
    w.branch_validation_run = 31012056789ULL;
    w.branch_validation_job = 92326490304ULL;
    std::strcpy(w.validated_branch_head, "f14a03d1d7dee552efd8133b01dda63063b4a32e");
    std::strcpy(w.main_merge_head, "c05cf860e4be5a0865813529baf9ad99e50dbe02");
    std::strcpy(w.restart_git_blob, "c0810c39f1aaeaf350512811b7390770986d223f");
    std::strcpy(w.cache_git_blob, "7efcf952aede8894162d54ecb0575a5aecd7cb83");
    std::strcpy(w.probe_git_blob, "5fcce879fe4a435da743e64d35e48c0132416d4f");
    std::strcpy(w.gateway_git_blob, "c8b81218a84dc25ddc6b4d2b28b696085edbf707");
    std::strcpy(w.production_gateway_git_blob, "4b2c4c0d8fa6bc75acd57a29cf1fbbd2bff3b25b");
    std::strcpy(w.service_git_blob, "d0ef21446e56602c2cea242622dbcc707fb59c1b");
    std::strcpy(w.gateway_test_git_blob, "97f515056afb71fed25314402d74894ee4534170");
    std::strcpy(w.production_test_git_blob, "9de2afc05a3814167f69e7dcefedc738c6c93cfe");
    std::strcpy(w.validation_workflow_git_blob, "c0816b71a7e4fd61ea6ad2025f1fdf6f84b16b24");
    std::strcpy(w.pass210_contract_git_blob, "ac46a61f568b0443794f854cf84e5a3cfc1bf908");
    return w;
}

int main() {
    auto w = witness();
    hhs::rna::InheritedPass209RuntimeBootstrapGateway membrane(w);
    assert(membrane.status() == HHS_EXACT_STATUS_OK);
    assert(membrane.wired());
    const auto& b = membrane.record();
    assert(b.pass_number == 209U);
    assert(b.status_catalog_count == 9U);
    assert(b.pass219_new_canonical_mutation_authority == 0U);
    assert(b.cxx_mutation_authority == 0U);
    assert(b.vm81_mutation_authority == 0U);

    w.repository_checkout_readonly_bound = 0U;
    hhs::rna::InheritedPass209RuntimeBootstrapGateway rejected(w);
    assert(rejected.status() == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(!rejected.wired());
    return 0;
}

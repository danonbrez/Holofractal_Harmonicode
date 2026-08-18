#include "hhs_pass219_inherited_pass209_1_16.h"

#include <assert.h>
#include <string.h>

static HHSExactPass209RuntimeBootstrapWitnessV1 witness(void) {
    HHSExactPass209RuntimeBootstrapWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
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
    strcpy(w.validated_branch_head, "f14a03d1d7dee552efd8133b01dda63063b4a32e");
    strcpy(w.main_merge_head, "c05cf860e4be5a0865813529baf9ad99e50dbe02");
    strcpy(w.restart_git_blob, "c0810c39f1aaeaf350512811b7390770986d223f");
    strcpy(w.cache_git_blob, "7efcf952aede8894162d54ecb0575a5aecd7cb83");
    strcpy(w.probe_git_blob, "5fcce879fe4a435da743e64d35e48c0132416d4f");
    strcpy(w.gateway_git_blob, "c8b81218a84dc25ddc6b4d2b28b696085edbf707");
    strcpy(w.production_gateway_git_blob, "4b2c4c0d8fa6bc75acd57a29cf1fbbd2bff3b25b");
    strcpy(w.service_git_blob, "d0ef21446e56602c2cea242622dbcc707fb59c1b");
    strcpy(w.gateway_test_git_blob, "97f515056afb71fed25314402d74894ee4534170");
    strcpy(w.production_test_git_blob, "9de2afc05a3814167f69e7dcefedc738c6c93cfe");
    strcpy(w.validation_workflow_git_blob, "c0816b71a7e4fd61ea6ad2025f1fdf6f84b16b24");
    strcpy(w.pass210_contract_git_blob, "ac46a61f568b0443794f854cf84e5a3cfc1bf908");
    return w;
}

int main(void) {
    HHSExactPass209RuntimeBootstrapWitnessV1 w = witness();
    HHSExactPass219InheritedPass209BindingV1 b;
    assert(hhs_exact_pass219_bind_pass209_runtime_bootstrap_gateway(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.pass_number == 209U);
    assert(b.nonblocking_bootstrap_bound == 1U);
    assert(b.persistent_status_cache_bound == 1U);
    assert(b.isolated_probe_bound == 1U);
    assert(b.warming_fail_open_to_projection_bound == 1U);
    assert(b.external_state_root_boundary_bound == 1U);
    assert(b.canonical_backend_authority_preserved == 1U);
    assert(b.pass210_successor_bound == 1U);
    assert(b.pass219_new_canonical_mutation_authority == 0U);
    assert(b.cxx_mutation_authority == 0U);
    assert(b.vm81_mutation_authority == 0U);
    assert(b.status_catalog_count == 9U);

    w.cache_projection_noncanonical = 0U;
    assert(hhs_exact_pass219_bind_pass209_runtime_bootstrap_gateway(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.pass210_inherits_pass209 = 0U;
    assert(hhs_exact_pass219_bind_pass209_runtime_bootstrap_gateway(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.production_gateway_git_blob[0] = '0';
    assert(hhs_exact_pass219_bind_pass209_runtime_bootstrap_gateway(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}

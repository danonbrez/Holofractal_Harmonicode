#include "../include/hhs_pass219_inherited_pass209_1_16.h"

#include <stddef.h>
#include <string.h>

static const char P209_VALIDATED_HEAD[] = "f14a03d1d7dee552efd8133b01dda63063b4a32e";
static const char P209_MAIN_MERGE[] = "c05cf860e4be5a0865813529baf9ad99e50dbe02";
static const char P209_RESTART_BLOB[] = "c0810c39f1aaeaf350512811b7390770986d223f";
static const char P209_CACHE_BLOB[] = "7efcf952aede8894162d54ecb0575a5aecd7cb83";
static const char P209_PROBE_BLOB[] = "5fcce879fe4a435da743e64d35e48c0132416d4f";
static const char P209_GATEWAY_BLOB[] = "c8b81218a84dc25ddc6b4d2b28b696085edbf707";
static const char P209_PRODUCTION_GATEWAY_BLOB[] = "4b2c4c0d8fa6bc75acd57a29cf1fbbd2bff3b25b";
static const char P209_SERVICE_BLOB[] = "d0ef21446e56602c2cea242622dbcc707fb59c1b";
static const char P209_GATEWAY_TEST_BLOB[] = "97f515056afb71fed25314402d74894ee4534170";
static const char P209_PRODUCTION_TEST_BLOB[] = "9de2afc05a3814167f69e7dcefedc738c6c93cfe";
static const char P209_WORKFLOW_BLOB[] = "c0816b71a7e4fd61ea6ad2025f1fdf6f84b16b24";
static const char P209_SUCCESSOR_P210_CONTRACT_BLOB[] = "ac46a61f568b0443794f854cf84e5a3cfc1bf908";

static uint32_t p209_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS209_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS209_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS209_VERSION_PATCH;
}

static int p209_text(const char *value, size_t size, const char *expected, size_t expected_len) {
    return value != NULL && expected != NULL && size == expected_len + 1U &&
           value[expected_len] == '\0' && memcmp(value, expected, expected_len) == 0;
}

static int p209_git(
    const char value[HHS_EXACT_PASS209_GIT_SHA_STRLEN],
    const char expected[HHS_EXACT_PASS209_GIT_SHA_STRLEN]
) {
    return p209_text(value, HHS_EXACT_PASS209_GIT_SHA_STRLEN, expected, HHS_EXACT_PASS209_GIT_SHA_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass209_version(void) { return p209_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass209_runtime_bootstrap_gateway(
    const HHSExactPass209RuntimeBootstrapWitnessV1 *witness,
    HHSExactPass219InheritedPass209BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p209_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (witness->runtime_verified != 1U ||
        witness->status_catalog_count != HHS_EXACT_PASS209_STATUS_CATALOG_COUNT ||
        witness->required_operation_count != HHS_EXACT_PASS209_REQUIRED_OPERATION_COUNT ||
        witness->persistent_cache_bound != 1U ||
        witness->stale_while_revalidate_bound != 1U ||
        witness->isolated_sequential_probe_bound != 1U ||
        witness->cold_miss_warming_projection_bound != 1U ||
        witness->direct_status_intercept_bound != 1U ||
        witness->browser_readiness_coordination_bound != 1U ||
        witness->external_state_roots_bound != 1U ||
        witness->repository_checkout_readonly_bound != 1U ||
        witness->canonical_backend_authority_preserved != 1U ||
        witness->cache_projection_noncanonical != 1U ||
        witness->pass210_inherits_pass209 != 1U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U ||
        witness->branch_validation_run != 31012056789ULL ||
        witness->branch_validation_job != 92326490304ULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!p209_git(witness->validated_branch_head, P209_VALIDATED_HEAD) ||
        !p209_git(witness->main_merge_head, P209_MAIN_MERGE) ||
        !p209_git(witness->restart_git_blob, P209_RESTART_BLOB) ||
        !p209_git(witness->cache_git_blob, P209_CACHE_BLOB) ||
        !p209_git(witness->probe_git_blob, P209_PROBE_BLOB) ||
        !p209_git(witness->gateway_git_blob, P209_GATEWAY_BLOB) ||
        !p209_git(witness->production_gateway_git_blob, P209_PRODUCTION_GATEWAY_BLOB) ||
        !p209_git(witness->service_git_blob, P209_SERVICE_BLOB) ||
        !p209_git(witness->gateway_test_git_blob, P209_GATEWAY_TEST_BLOB) ||
        !p209_git(witness->production_test_git_blob, P209_PRODUCTION_TEST_BLOB) ||
        !p209_git(witness->validation_workflow_git_blob, P209_WORKFLOW_BLOB) ||
        !p209_git(witness->pass210_contract_git_blob, P209_SUCCESSOR_P210_CONTRACT_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p209_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS209_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->nonblocking_bootstrap_bound = 1U;
    out_binding->persistent_status_cache_bound = 1U;
    out_binding->isolated_probe_bound = 1U;
    out_binding->warming_fail_open_to_projection_bound = 1U;
    out_binding->external_state_root_boundary_bound = 1U;
    out_binding->canonical_backend_authority_preserved = 1U;
    out_binding->pass210_successor_bound = 1U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    out_binding->status_catalog_count = witness->status_catalog_count;
    memcpy(out_binding->main_merge_head, witness->main_merge_head, HHS_EXACT_PASS209_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

#include "../include/hhs_pass219_inherited_pass196_1_30.h"

#include <stddef.h>
#include <string.h>

static const char P196_PRIMARY_MERGE[] = "37687d479f2a9f1d996d225a4ba3556d9db72a86";
static const char P196_TOPOLOGY_MERGE[] = "959729c9070399fcdf0015702cd8777079e05dcc";
static const char P196_FROZEN_I129[] = "40e6e07d5f4a401541a6255339223e853846e713";
static const char P196_HISTORICAL_V1_BLOB[] = "d2cff008db58a29bf27be20cb3547b9e0018f5e1";
static const char P196_REPAIRED_V2_BLOB[] = "196b1fbdbbb3610ccb47e7fd638d4c3f2cdc67f6";
static const char P196_REPAIRED_API_BLOB[] = "39187c3376591c64758019090d9b115c6a43f6ee";
static const char P196_REPAIRED_FRONTEND_BLOB[] = "1503903c844c9e601133853eed9ed597f6fd2274";
static const char P196_PROJECTION_REFRESH_BLOB[] = "44254e10f90e929a4f8c1a18a75b3ca14a2c05ed";
static const char P196_REPAIR_REGRESSION_BLOB[] = "55d1da0ea58044436646ccd8a331088135515c8f";
static const char P196_REPAIR_WORKFLOW_BLOB[] = "7a19d3e7faab6e7210e156026300e96550b9afcb";

static uint32_t p196_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS196_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS196_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS196_VERSION_PATCH;
}

static int p196_git(const char value[HHS_EXACT_PASS196_GIT_SHA_STRLEN], const char *expected) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS196_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS196_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass196_version(void) { return p196_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass196_repaired_integrated_environment(
    const HHSExactPass196RepairedIntegratedEnvironmentWitnessV1 *witness,
    HHSExactPass219InheritedPass196BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p196_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->primary_pull_request != HHS_EXACT_PASS196_PRIMARY_PR ||
        witness->topology_pull_request != HHS_EXACT_PASS196_TOPOLOGY_PR ||
        witness->review_finding_count != HHS_EXACT_PASS196_REVIEW_FINDING_COUNT ||
        witness->vm81_hash72_receipt_required_for_persistence != 1U ||
        witness->persisted_restart_lineage_restored != 1U ||
        witness->distinct_executable_evidence_required != 1U ||
        witness->validated_projection_refresh_bound != 1U ||
        witness->host_independent_manifest_identity != 1U ||
        witness->same_bytes_hash_and_classification != 1U ||
        witness->service_state_directory_preserved != 1U ||
        witness->strict_boolean_tool_ingress != 1U ||
        witness->failed_scan_quarantine != 1U ||
        witness->scan_error_mapping_parity != 1U ||
        witness->historical_v1_preserved != 1U ||
        witness->pass197_successor_preserved != 1U ||
        witness->vector_store_is_source_authority != 0U ||
        witness->browser_projection_is_authority != 0U ||
        witness->pass219_new_candidate_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p196_git(witness->accepted_primary_merge, P196_PRIMARY_MERGE) ||
        !p196_git(witness->accepted_topology_merge, P196_TOPOLOGY_MERGE) ||
        !p196_git(witness->frozen_i129_commit, P196_FROZEN_I129) ||
        !p196_git(witness->historical_v1_blob, P196_HISTORICAL_V1_BLOB) ||
        !p196_git(witness->repaired_v2_blob, P196_REPAIRED_V2_BLOB) ||
        !p196_git(witness->repaired_api_blob, P196_REPAIRED_API_BLOB) ||
        !p196_git(witness->repaired_frontend_blob, P196_REPAIRED_FRONTEND_BLOB) ||
        !p196_git(witness->projection_refresh_blob, P196_PROJECTION_REFRESH_BLOB) ||
        !p196_git(witness->repair_regression_blob, P196_REPAIR_REGRESSION_BLOB) ||
        !p196_git(witness->repair_workflow_blob, P196_REPAIR_WORKFLOW_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p196_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS196_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->inherited_findings_repaired = HHS_EXACT_PASS196_REVIEW_FINDING_COUNT;
    out_binding->vm81_receipt_admission_bound = 1U;
    out_binding->restart_lineage_bound = 1U;
    out_binding->executable_evidence_bound = 1U;
    out_binding->projection_refresh_bound = 1U;
    out_binding->reproducible_manifest_bound = 1U;
    out_binding->immutable_observation_bound = 1U;
    out_binding->service_topology_bound = 1U;
    out_binding->strict_tool_ingress_bound = 1U;
    out_binding->failure_quarantine_bound = 1U;
    out_binding->error_parity_bound = 1U;
    out_binding->pass197_successor_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->vector_store_is_source_authority = 0U;
    out_binding->browser_projection_is_authority = 0U;
    out_binding->pass219_new_candidate_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->accepted_primary_merge, witness->accepted_primary_merge, HHS_EXACT_PASS196_GIT_SHA_STRLEN);
    memcpy(out_binding->accepted_topology_merge, witness->accepted_topology_merge, HHS_EXACT_PASS196_GIT_SHA_STRLEN);
    memcpy(out_binding->frozen_i129_commit, witness->frozen_i129_commit, HHS_EXACT_PASS196_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

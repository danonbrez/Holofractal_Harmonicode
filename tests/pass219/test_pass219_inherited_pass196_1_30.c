#include "hhs_pass219_inherited_pass196_1_30.h"

#include <assert.h>
#include <string.h>

static HHSExactPass196RepairedIntegratedEnvironmentWitnessV1 witness(void) {
    HHSExactPass196RepairedIntegratedEnvironmentWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass196_version();
    w.primary_pull_request = HHS_EXACT_PASS196_PRIMARY_PR;
    w.topology_pull_request = HHS_EXACT_PASS196_TOPOLOGY_PR;
    w.review_finding_count = HHS_EXACT_PASS196_REVIEW_FINDING_COUNT;
    w.vm81_hash72_receipt_required_for_persistence = 1U;
    w.persisted_restart_lineage_restored = 1U;
    w.distinct_executable_evidence_required = 1U;
    w.validated_projection_refresh_bound = 1U;
    w.host_independent_manifest_identity = 1U;
    w.same_bytes_hash_and_classification = 1U;
    w.service_state_directory_preserved = 1U;
    w.strict_boolean_tool_ingress = 1U;
    w.failed_scan_quarantine = 1U;
    w.scan_error_mapping_parity = 1U;
    w.historical_v1_preserved = 1U;
    w.pass197_successor_preserved = 1U;
    strcpy(w.accepted_primary_merge, "37687d479f2a9f1d996d225a4ba3556d9db72a86");
    strcpy(w.accepted_topology_merge, "959729c9070399fcdf0015702cd8777079e05dcc");
    strcpy(w.frozen_i129_commit, "40e6e07d5f4a401541a6255339223e853846e713");
    strcpy(w.historical_v1_blob, "d2cff008db58a29bf27be20cb3547b9e0018f5e1");
    strcpy(w.repaired_v2_blob, "196b1fbdbbb3610ccb47e7fd638d4c3f2cdc67f6");
    strcpy(w.repaired_api_blob, "39187c3376591c64758019090d9b115c6a43f6ee");
    strcpy(w.repaired_frontend_blob, "1503903c844c9e601133853eed9ed597f6fd2274");
    strcpy(w.projection_refresh_blob, "44254e10f90e929a4f8c1a18a75b3ca14a2c05ed");
    strcpy(w.repair_regression_blob, "55d1da0ea58044436646ccd8a331088135515c8f");
    strcpy(w.repair_workflow_blob, "7a19d3e7faab6e7210e156026300e96550b9afcb");
    return w;
}

int main(void) {
    HHSExactPass196RepairedIntegratedEnvironmentWitnessV1 w = witness();
    HHSExactPass219InheritedPass196BindingV1 binding;
    assert(hhs_exact_pass219_bind_pass196_repaired_integrated_environment(&w, &binding) == HHS_EXACT_STATUS_OK);
    assert(binding.pass_number == 196U);
    assert(binding.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(binding.inherited_findings_repaired == 10U);
    assert(binding.vm81_receipt_admission_bound == 1U);
    assert(binding.restart_lineage_bound == 1U);
    assert(binding.projection_refresh_bound == 1U);
    assert(binding.failure_quarantine_bound == 1U);
    assert(binding.pass197_successor_bound == 1U);
    assert(binding.no_new_authority_bound == 1U);
    assert(binding.vector_store_is_source_authority == 0U);
    assert(binding.browser_projection_is_authority == 0U);
    assert(binding.pass219_new_candidate_authority == 0U);
    assert(binding.pass219_new_canonical_mutation_authority == 0U);
    assert(binding.pass219_new_persistence_authority == 0U);
    assert(binding.pass219_new_hash72_clock == 0U);
    assert(binding.cxx_mutation_authority == 0U);
    assert(binding.vm81_mutation_authority == 0U);

    w = witness();
    w.vm81_hash72_receipt_required_for_persistence = 0U;
    assert(hhs_exact_pass219_bind_pass196_repaired_integrated_environment(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.vector_store_is_source_authority = 1U;
    assert(hhs_exact_pass219_bind_pass196_repaired_integrated_environment(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.browser_projection_is_authority = 1U;
    assert(hhs_exact_pass219_bind_pass196_repaired_integrated_environment(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}

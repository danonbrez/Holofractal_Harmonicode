#include "hhs_pass219_inherited_pass196_1_30.hpp"

#include <cassert>
#include <cstring>

int main() {
    using Surface = hhs::rna::InheritedPass196RepairedIntegratedEnvironment;
    static_assert(!Surface::mutation_authority());
    static_assert(!Surface::new_persistence_authority());
    static_assert(!Surface::hash72_clock_authority());
    static_assert(!Surface::vm81_mutation_authority());
    static_assert(!Surface::candidate_authority());
    static_assert(!Surface::vector_store_source_authority());
    static_assert(!Surface::browser_projection_authority());
    static_assert(Surface::singleton_vm81_authority_remains_inherited());
    static_assert(Surface::vm81_receipt_required_for_persistence());
    static_assert(Surface::failed_scan_quarantines_current_success());

    HHSExactPass196RepairedIntegratedEnvironmentWitnessV1 w{};
    HHSExactPass219InheritedPass196BindingV1 binding{};
    w.struct_size = sizeof(w);
    w.version = Surface::version();
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
    std::strcpy(w.accepted_primary_merge, "37687d479f2a9f1d996d225a4ba3556d9db72a86");
    std::strcpy(w.accepted_topology_merge, "959729c9070399fcdf0015702cd8777079e05dcc");
    std::strcpy(w.frozen_i129_commit, "40e6e07d5f4a401541a6255339223e853846e713");
    std::strcpy(w.historical_v1_blob, "d2cff008db58a29bf27be20cb3547b9e0018f5e1");
    std::strcpy(w.repaired_v2_blob, "196b1fbdbbb3610ccb47e7fd638d4c3f2cdc67f6");
    std::strcpy(w.repaired_api_blob, "39187c3376591c64758019090d9b115c6a43f6ee");
    std::strcpy(w.repaired_frontend_blob, "1503903c844c9e601133853eed9ed597f6fd2274");
    std::strcpy(w.projection_refresh_blob, "44254e10f90e929a4f8c1a18a75b3ca14a2c05ed");
    std::strcpy(w.repair_regression_blob, "d0860d89cd8abe596f49c73b7e544511cdaba5d0");
    std::strcpy(w.repair_workflow_blob, "7a19d3e7faab6e7210e156026300e96550b9afcb");
    assert(Surface::bind(w, binding) == HHS_EXACT_STATUS_OK);
    assert(binding.pass_number == 196U);
    assert(binding.inherited_findings_repaired == 10U);
    return 0;
}

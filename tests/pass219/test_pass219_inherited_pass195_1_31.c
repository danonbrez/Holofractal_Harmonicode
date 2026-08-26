#include "hhs_pass219_inherited_pass195_1_31.h"

#include <assert.h>
#include <string.h>

static HHSExactPass195RepairedKimiK3ContentEngineWitnessV1 witness(void) {
    HHSExactPass195RepairedKimiK3ContentEngineWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass195_version();
    w.primary_pull_request = HHS_EXACT_PASS195_PRIMARY_PR;
    w.review_finding_count = HHS_EXACT_PASS195_REVIEW_FINDING_COUNT;
    w.provider_plan_schema_validation = 1U;
    w.input_content_receipt_binding = 1U;
    w.frontend_ingress_rejection = 1U;
    w.model_identity_bound_before_plan_hash = 1U;
    w.template_before_style_overrides = 1U;
    w.operator_authorization_and_throttle = 1U;
    w.bounded_constraint_prompt = 1U;
    w.storybook_handoff_bounds = 1U;
    w.storybook_style_range_alignment = 1U;
    w.image_analysis_capability_admission = 1U;
    w.authorized_tick_graph_binding = 1U;
    w.final_health_hash_binding = 1U;
    w.historical_v1_preserved = 1U;
    w.pass196_successor_preserved = 1U;
    strcpy(w.accepted_primary_merge, "8bcc0921555ecface13113c8a2620415ddb3fdf1");
    strcpy(w.frozen_i130_commit, "69743440249dd7a05aa2b4096482d248973f239e");
    strcpy(w.historical_v1_blob, "ea7041c026e63445034c7161268faafe436cd2d1");
    strcpy(w.repaired_v2_blob, "c1cf830a8ede708b62cc052610968f7fc498228d");
    strcpy(w.repaired_api_blob, "e62f59d5c8617a546908fd9ca2bd43998c62cd2e");
    strcpy(w.repaired_frontend_blob, "9153f922193ddadf2e208986e11dc9d57e12f817");
    strcpy(w.repair_regression_blob, "866a893e30dfd9565b712df9ff9c979395b25a3f");
    strcpy(w.repair_workflow_blob, "f43d6cdb62e8836e075cb4400d9525eaf8f4d491");
    return w;
}

int main(void) {
    HHSExactPass195RepairedKimiK3ContentEngineWitnessV1 w = witness();
    HHSExactPass219InheritedPass195BindingV1 binding;
    assert(hhs_exact_pass219_bind_pass195_repaired_kimi_k3_content_engine(&w, &binding) == HHS_EXACT_STATUS_OK);
    assert(binding.pass_number == 195U);
    assert(binding.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(binding.inherited_findings_repaired == 12U);
    assert(binding.strict_provider_plan_bound == 1U);
    assert(binding.exact_input_receipt_bound == 1U);
    assert(binding.governed_frontend_ingress_bound == 1U);
    assert(binding.model_provenance_bound == 1U);
    assert(binding.storybook_handoff_bound == 1U);
    assert(binding.paid_route_authorization_bound == 1U);
    assert(binding.multimodal_capability_bound == 1U);
    assert(binding.exact_tick_graph_bound == 1U);
    assert(binding.final_health_identity_bound == 1U);
    assert(binding.pass196_successor_bound == 1U);
    assert(binding.no_new_authority_bound == 1U);
    assert(binding.external_provider_is_canonical_authority == 0U);
    assert(binding.browser_handoff_is_canonical_authority == 0U);
    assert(binding.pass219_new_candidate_authority == 0U);
    assert(binding.pass219_new_canonical_mutation_authority == 0U);
    assert(binding.pass219_new_persistence_authority == 0U);
    assert(binding.pass219_new_hash72_clock == 0U);
    assert(binding.cxx_mutation_authority == 0U);
    assert(binding.vm81_mutation_authority == 0U);

    w = witness();
    w.provider_plan_schema_validation = 0U;
    assert(hhs_exact_pass219_bind_pass195_repaired_kimi_k3_content_engine(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.image_analysis_capability_admission = 0U;
    assert(hhs_exact_pass219_bind_pass195_repaired_kimi_k3_content_engine(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.external_provider_is_canonical_authority = 1U;
    assert(hhs_exact_pass219_bind_pass195_repaired_kimi_k3_content_engine(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.browser_handoff_is_canonical_authority = 1U;
    assert(hhs_exact_pass219_bind_pass195_repaired_kimi_k3_content_engine(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}

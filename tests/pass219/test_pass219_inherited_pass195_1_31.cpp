#include "hhs_pass219_inherited_pass195_1_31.hpp"

#include <cassert>
#include <cstring>

int main() {
    using Surface = hhs::rna::InheritedPass195RepairedKimiK3ContentEngine;
    static_assert(!Surface::mutation_authority());
    static_assert(!Surface::new_persistence_authority());
    static_assert(!Surface::hash72_clock_authority());
    static_assert(!Surface::vm81_mutation_authority());
    static_assert(!Surface::candidate_authority());
    static_assert(!Surface::external_provider_canonical_authority());
    static_assert(!Surface::browser_handoff_canonical_authority());
    static_assert(Surface::singleton_vm81_authority_remains_inherited());
    static_assert(Surface::strict_provider_plan_validation());
    static_assert(Surface::image_analysis_requires_capability_admission());
    static_assert(Surface::paid_generation_requires_operator_authorization());

    HHSExactPass195RepairedKimiK3ContentEngineWitnessV1 w{};
    HHSExactPass219InheritedPass195BindingV1 binding{};
    w.struct_size = sizeof(w);
    w.version = Surface::version();
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
    std::strcpy(w.accepted_primary_merge, "8bcc0921555ecface13113c8a2620415ddb3fdf1");
    std::strcpy(w.frozen_i130_commit, "69743440249dd7a05aa2b4096482d248973f239e");
    std::strcpy(w.historical_v1_blob, "ea7041c026e63445034c7161268faafe436cd2d1");
    std::strcpy(w.repaired_v2_blob, "d4382d00e06492b06fecc8a2df76c99c5e5f6b51");
    std::strcpy(w.repaired_api_blob, "e62f59d5c8617a546908fd9ca2bd43998c62cd2e");
    std::strcpy(w.repaired_frontend_blob, "9153f922193ddadf2e208986e11dc9d57e12f817");
    std::strcpy(w.repair_regression_blob, "866a893e30dfd9565b712df9ff9c979395b25a3f");
    std::strcpy(w.repair_workflow_blob, "271e2ec78d3e15cfedadf180bee3978ce80ba7f8");
    assert(Surface::bind(w, binding) == HHS_EXACT_STATUS_OK);
    assert(binding.pass_number == 195U);
    assert(binding.inherited_findings_repaired == 12U);
    assert(binding.multimodal_capability_bound == 1U);
    assert(binding.exact_tick_graph_bound == 1U);
    assert(binding.pass196_successor_bound == 1U);
    return 0;
}

#include "../include/hhs_pass219_inherited_pass195_1_31.h"

#include <stddef.h>
#include <string.h>

static const char P195_PRIMARY_MERGE[] = "8bcc0921555ecface13113c8a2620415ddb3fdf1";
static const char P195_FROZEN_I130[] = "69743440249dd7a05aa2b4096482d248973f239e";
static const char P195_HISTORICAL_V1_BLOB[] = "ea7041c026e63445034c7161268faafe436cd2d1";
static const char P195_REPAIRED_V2_BLOB[] = "d4382d00e06492b06fecc8a2df76c99c5e5f6b51";
static const char P195_REPAIRED_API_BLOB[] = "e62f59d5c8617a546908fd9ca2bd43998c62cd2e";
static const char P195_REPAIRED_FRONTEND_BLOB[] = "9153f922193ddadf2e208986e11dc9d57e12f817";
static const char P195_REPAIR_REGRESSION_BLOB[] = "866a893e30dfd9565b712df9ff9c979395b25a3f";
static const char P195_REPAIR_WORKFLOW_BLOB[] = "271e2ec78d3e15cfedadf180bee3978ce80ba7f8";

static uint32_t p195_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS195_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS195_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS195_VERSION_PATCH;
}

static int p195_git(const char value[HHS_EXACT_PASS195_GIT_SHA_STRLEN], const char *expected) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS195_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS195_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass195_version(void) { return p195_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass195_repaired_kimi_k3_content_engine(
    const HHSExactPass195RepairedKimiK3ContentEngineWitnessV1 *witness,
    HHSExactPass219InheritedPass195BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p195_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->primary_pull_request != HHS_EXACT_PASS195_PRIMARY_PR ||
        witness->review_finding_count != HHS_EXACT_PASS195_REVIEW_FINDING_COUNT ||
        witness->provider_plan_schema_validation != 1U ||
        witness->input_content_receipt_binding != 1U ||
        witness->frontend_ingress_rejection != 1U ||
        witness->model_identity_bound_before_plan_hash != 1U ||
        witness->template_before_style_overrides != 1U ||
        witness->operator_authorization_and_throttle != 1U ||
        witness->bounded_constraint_prompt != 1U ||
        witness->storybook_handoff_bounds != 1U ||
        witness->storybook_style_range_alignment != 1U ||
        witness->image_analysis_capability_admission != 1U ||
        witness->authorized_tick_graph_binding != 1U ||
        witness->final_health_hash_binding != 1U ||
        witness->historical_v1_preserved != 1U ||
        witness->pass196_successor_preserved != 1U ||
        witness->external_provider_is_canonical_authority != 0U ||
        witness->browser_handoff_is_canonical_authority != 0U ||
        witness->pass219_new_candidate_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p195_git(witness->accepted_primary_merge, P195_PRIMARY_MERGE) ||
        !p195_git(witness->frozen_i130_commit, P195_FROZEN_I130) ||
        !p195_git(witness->historical_v1_blob, P195_HISTORICAL_V1_BLOB) ||
        !p195_git(witness->repaired_v2_blob, P195_REPAIRED_V2_BLOB) ||
        !p195_git(witness->repaired_api_blob, P195_REPAIRED_API_BLOB) ||
        !p195_git(witness->repaired_frontend_blob, P195_REPAIRED_FRONTEND_BLOB) ||
        !p195_git(witness->repair_regression_blob, P195_REPAIR_REGRESSION_BLOB) ||
        !p195_git(witness->repair_workflow_blob, P195_REPAIR_WORKFLOW_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p195_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS195_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->inherited_findings_repaired = HHS_EXACT_PASS195_REVIEW_FINDING_COUNT;
    out_binding->strict_provider_plan_bound = 1U;
    out_binding->exact_input_receipt_bound = 1U;
    out_binding->governed_frontend_ingress_bound = 1U;
    out_binding->model_provenance_bound = 1U;
    out_binding->storybook_handoff_bound = 1U;
    out_binding->paid_route_authorization_bound = 1U;
    out_binding->multimodal_capability_bound = 1U;
    out_binding->exact_tick_graph_bound = 1U;
    out_binding->final_health_identity_bound = 1U;
    out_binding->pass196_successor_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->external_provider_is_canonical_authority = 0U;
    out_binding->browser_handoff_is_canonical_authority = 0U;
    out_binding->pass219_new_candidate_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->accepted_primary_merge, witness->accepted_primary_merge, HHS_EXACT_PASS195_GIT_SHA_STRLEN);
    memcpy(out_binding->frozen_i130_commit, witness->frozen_i130_commit, HHS_EXACT_PASS195_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

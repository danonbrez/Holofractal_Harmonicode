#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

static HHSExactPass219HNANClaimV1 claim_from_rule(uint32_t id) {
    HHSExactPass219HNANRuleV1 rule;
    HHSExactPass219HNANClaimV1 claim;
    memset(&rule, 0, sizeof(rule));
    memset(&claim, 0, sizeof(claim));
    assert(hhs_exact_pass219_hnan_global_rule(id, &rule) == HHS_EXACT_STATUS_OK);
    claim.struct_size = (uint32_t)sizeof(claim);
    claim.version = HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION;
    claim.rule_id = id;
    claim.lhs_node = rule.lhs_node;
    claim.rhs_node = rule.rhs_node;
    claim.relation = rule.relation;
    claim.source_order_preserved = 1U;
    claim.typed_identity_preserved = 1U;
    return claim;
}

int main(void) {
    HHSExactPass219HNANAuthorityV1 authority;
    HHSExactPass219HNANGlobalReceiptV1 receipt;
    HHSExactPass219HNANResolutionV1 resolution;
    HHSExactPass219HNANClaimV1 claim;
    HHSExactPass219Lane5MediationRequestV1 request;
    HHSExactPass219Lane5MediationReceiptV1 mediation;
    uint32_t i;

    memset(&authority, 0, sizeof(authority));
    assert(hhs_exact_pass219_hnan_global_authority(&authority) == HHS_EXACT_STATUS_OK);
    assert(authority.version == HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION);
    assert(authority.mandatory_rule_count == 15U);
    assert(authority.mandatory_rule_mask == HHS_EXACT_PASS219_HNAN_GLOBAL_ALL_RULES);
    assert(authority.system_wide_lane5_constraint == 1U);
    assert(authority.vm81_preflight_required == 1U);
    assert(authority.signed_environmental_preflight_required == 1U);
    assert(authority.canonical_vm81_mutation_authority == 0U);
    assert(authority.floating_point_canonical_authority == 0U);

    memset(&receipt, 0, sizeof(receipt));
    assert(hhs_exact_pass219_hnan_global_system_verify(&receipt) == HHS_EXACT_STATUS_OK);
    assert(receipt.decision == HHS_EXACT_HNAN_DECISION_VERIFIED);
    assert(receipt.verified_rule_mask == HHS_EXACT_PASS219_HNAN_GLOBAL_ALL_RULES);
    assert(receipt.rank_m01 == 3U);
    assert(receipt.nullity_m01 == 1U);
    assert(receipt.nullity_m01_squared == 2U);
    assert(receipt.jordan_depth2_verified == 1U);
    assert(receipt.minimal_polynomial_degree4_verified == 1U);
    assert(receipt.degree4_recurrence_verified == 1U);
    assert(receipt.ordered_zero_closure_preserved == 1U);
    assert(receipt.global_delta_denominator_preserved == 1U);
    assert(receipt.delta_cancellation_forbidden == 1U);
    assert(receipt.unbounded_carrier_symbolic == 1U);
    assert(receipt.u72_to_u0_closure_preserved == 1U);
    assert(receipt.xy_yx_distinct == 1U);
    assert(receipt.zw_wz_distinct == 1U);
    assert(receipt.system_signature64 != 0U);

    claim = claim_from_rule(6U);
    claim.lhs_node = HHS_EXACT_HNAN_NODE_DELTA;
    claim.rhs_node = HHS_EXACT_HNAN_NODE_INFINITY;
    memset(&resolution, 0, sizeof(resolution));
    assert(hhs_exact_pass219_hnan_resolve(&claim, &resolution) == HHS_EXACT_STATUS_OK);
    assert(resolution.decision == HHS_EXACT_HNAN_DECISION_REJECTED);
    assert(resolution.reason == HHS_EXACT_HNAN_REASON_SOURCE_ORDER);

    claim = claim_from_rule(9U);
    claim.delta_cancellation_requested = 1U;
    assert(hhs_exact_pass219_hnan_resolve(&claim, &resolution) == HHS_EXACT_STATUS_OK);
    assert(resolution.decision == HHS_EXACT_HNAN_DECISION_REJECTED);
    assert(resolution.reason == HHS_EXACT_HNAN_REASON_DELTA_CANCELLATION);

    claim = claim_from_rule(8U);
    claim.floating_infinity_requested = 1U;
    assert(hhs_exact_pass219_hnan_resolve(&claim, &resolution) == HHS_EXACT_STATUS_OK);
    assert(resolution.decision == HHS_EXACT_HNAN_DECISION_REJECTED);
    assert(resolution.reason == HHS_EXACT_HNAN_REASON_FLOAT_INFINITY);

    claim = claim_from_rule(12U);
    claim.commutation_requested = 1U;
    assert(hhs_exact_pass219_hnan_resolve(&claim, &resolution) == HHS_EXACT_STATUS_OK);
    assert(resolution.decision == HHS_EXACT_HNAN_DECISION_REJECTED);
    assert(resolution.reason == HHS_EXACT_HNAN_REASON_COMMUTATION);

    claim = claim_from_rule(1U);
    claim.scalar_substitution_requested = 1U;
    assert(hhs_exact_pass219_hnan_resolve(&claim, &resolution) == HHS_EXACT_STATUS_OK);
    assert(resolution.decision == HHS_EXACT_HNAN_DECISION_REJECTED);
    assert(resolution.reason == HHS_EXACT_HNAN_REASON_SCALARIZATION);

    memset(&request, 0, sizeof(request));
    request.struct_size = (uint32_t)sizeof(request);
    request.version = HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION;
    request.namespace_id = HHS_EXACT_PASS219_LANE5_NAMESPACE;
    request.hash216_reference_count = 1U;
    request.capability_reference_count = 1U;
    request.learning_stage = 4U;
    request.request_signature64 = 1U;
    request.candidate_signature64 = 2U;
    request.parent_hash216_signature64 = 3U;
    request.bigint_address_signature64 = 4U;
    request.hydration_signature64 = 5U;
    request.compression_signature64 = 6U;
    request.capability_registry_signature64 = 7U;
    request.learning_iteration_signature64 = 8U;
    request.rna_prepared_signature64 = 9U;
    request.rna_decision_signature64 = 10U;
    request.hash216_reference_signature64[0] = 11U;
    request.capability_reference_signature64[0] = 12U;
    memset(&mediation, 0, sizeof(mediation));
    assert(hhs_exact_pass219_lane5_mediate_candidate(&request, &mediation) == HHS_EXACT_STATUS_OK);
    assert(mediation.decision == HHS_EXACT_PASS219_LANE5_DECISION_CANDIDATE_READY);
    assert(mediation.zero_sum_closure_passed == 1U);
    assert(mediation.canonical_mutation_authority == 0U);
    assert(mediation.requires_environmental_admission == 1U);

    for (i = 1U; i <= 15U; ++i) {
        HHSExactPass219HNANRuleV1 rule;
        memset(&rule, 0, sizeof(rule));
        assert(hhs_exact_pass219_hnan_global_rule(i, &rule) == HHS_EXACT_STATUS_OK);
        assert(rule.rule_id == i);
        assert(rule.scalar_equality_authority == 0U);
        assert(rule.cancellation_authority == 0U);
        assert(rule.commutation_authority == 0U);
        assert(rule.floating_infinity_authority == 0U);
    }
    return 0;
}

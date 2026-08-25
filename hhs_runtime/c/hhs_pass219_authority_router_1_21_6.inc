#include "../include/hhs_pass219_authority_router_1_21_6.h"

#include <string.h>

static uint32_t hhs219_authority_router_version_word(void) {
    return (HHS_EXACT_PASS219_AUTHORITY_ROUTER_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_AUTHORITY_ROUTER_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_AUTHORITY_ROUTER_VERSION_PATCH;
}

static int hhs219_authority_flag(uint8_t value) {
    return value == 0U || value == 1U;
}

static int hhs219_authority_evidence_valid(
    const HHSExactPass219AuthorityEvidenceV1 *evidence
) {
    if (evidence == NULL)
        return 0;
    if (evidence->struct_size < sizeof(*evidence) ||
        evidence->version != hhs219_authority_router_version_word())
        return 0;
    if (!hhs219_authority_flag(evidence->source_identity_exact) ||
        !hhs219_authority_flag(evidence->pass159_source_pipeline_verified) ||
        !hhs219_authority_flag(evidence->pass159_vmir_identity_present) ||
        !hhs219_authority_flag(evidence->candidate_exact_execution_verified) ||
        !hhs219_authority_flag(evidence->candidate_exact_replay_verified) ||
        !hhs219_authority_flag(evidence->i1214_unresolved_composition_verified) ||
        !hhs219_authority_flag(evidence->pass191_inherited_manifold_verified) ||
        !hhs219_authority_flag(evidence->pass191_exact_context_scope_preserved) ||
        !hhs219_authority_flag(evidence->pass191_singleton_vm81_authority_verified) ||
        !hhs219_authority_flag(evidence->pass191_deterministic_replay_verified))
        return 0;

    if (evidence->source_identity_exact == 0U &&
        (evidence->pass159_source_pipeline_verified != 0U ||
         evidence->pass159_vmir_identity_present != 0U ||
         evidence->candidate_exact_execution_verified != 0U ||
         evidence->candidate_exact_replay_verified != 0U ||
         evidence->i1214_unresolved_composition_verified != 0U ||
         evidence->pass191_inherited_manifold_verified != 0U ||
         evidence->pass191_exact_context_scope_preserved != 0U ||
         evidence->pass191_singleton_vm81_authority_verified != 0U ||
         evidence->pass191_deterministic_replay_verified != 0U))
        return 0;

    if (evidence->pass159_vmir_identity_present != 0U &&
        evidence->pass159_source_pipeline_verified == 0U)
        return 0;

    if (evidence->candidate_exact_execution_verified !=
        evidence->candidate_exact_replay_verified)
        return 0;

    if (evidence->i1214_unresolved_composition_verified != 0U &&
        (evidence->pass159_source_pipeline_verified == 0U ||
         evidence->pass159_vmir_identity_present == 0U ||
         evidence->candidate_exact_execution_verified == 0U ||
         evidence->candidate_exact_replay_verified == 0U))
        return 0;

    if (evidence->pass191_inherited_manifold_verified != 0U) {
        if (evidence->pass191_exact_context_scope_preserved == 0U ||
            evidence->pass191_singleton_vm81_authority_verified == 0U ||
            evidence->pass191_deterministic_replay_verified == 0U)
            return 0;
    } else if (evidence->pass191_exact_context_scope_preserved != 0U ||
               evidence->pass191_singleton_vm81_authority_verified != 0U ||
               evidence->pass191_deterministic_replay_verified != 0U) {
        return 0;
    }

    return 1;
}

uint32_t hhs_exact_pass219_authority_router_version(void) {
    return hhs219_authority_router_version_word();
}

HHSExactStatus hhs_exact_pass219_authority_router_descriptor(
    HHSExactPass219AuthorityRouterDescriptorV1 *out_descriptor
) {
    HHSExactPass219MonolithicDescriptorV1 monolithic;

    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (hhs_exact_pass219_monolithic_descriptor(&monolithic) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = hhs219_authority_router_version_word();
    memcpy(out_descriptor->native_source_sha256,
           monolithic.native_source_sha256,
           HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES);
    out_descriptor->pass159_source_pipeline_role =
        HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS159_SOURCE_PIPELINE;
    out_descriptor->i1213_candidate_role =
        HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_I1213_CANDIDATE_DIAGNOSTIC;
    out_descriptor->i1214_composition_role =
        HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_I1214_UNRESOLVED_COMPOSITION;
    out_descriptor->pass191_inherited_role =
        HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS191_INHERITED_MANIFOLD;
    out_descriptor->pass169_canonical_role =
        HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS169_WHOLE_EXPRESSION;
    out_descriptor->raw_evidence_can_prove = 0U;
    out_descriptor->canonical_proven_decision_available = 0U;
    out_descriptor->floating_point_authority = 0U;
    out_descriptor->vm81_mutation_authority = 0U;
    out_descriptor->hash72_commit_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_authority_route_evidence(
    const HHSExactPass219AuthorityEvidenceV1 *evidence,
    HHSExactPass219AuthorityRouteV1 *out_route
) {
    uint8_t selected = HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_NONE;
    uint32_t reasons = HHS_EXACT_PASS219_AUTHORITY_REASON_PASS169_STILL_REQUIRED;

    if (evidence == NULL || out_route == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs219_authority_evidence_valid(evidence))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (evidence->source_identity_exact != 0U &&
        evidence->pass159_source_pipeline_verified != 0U) {
        selected = HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS159_SOURCE_PIPELINE;
        reasons |= HHS_EXACT_PASS219_AUTHORITY_REASON_SOURCE_PIPELINE;
    }
    if (evidence->candidate_exact_execution_verified != 0U &&
        evidence->candidate_exact_replay_verified != 0U) {
        selected = HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_I1213_CANDIDATE_DIAGNOSTIC;
        reasons |= HHS_EXACT_PASS219_AUTHORITY_REASON_CANDIDATE_DIAGNOSTIC;
    }
    if (evidence->i1214_unresolved_composition_verified != 0U) {
        selected = HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_I1214_UNRESOLVED_COMPOSITION;
        reasons |= HHS_EXACT_PASS219_AUTHORITY_REASON_UNRESOLVED_COMPOSITION;
    }
    if (evidence->pass191_inherited_manifold_verified != 0U) {
        selected = HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS191_INHERITED_MANIFOLD;
        reasons |= HHS_EXACT_PASS219_AUTHORITY_REASON_PASS191_MANIFOLD |
                   HHS_EXACT_PASS219_AUTHORITY_REASON_PASS191_CONTEXT_SCOPE |
                   HHS_EXACT_PASS219_AUTHORITY_REASON_PASS191_SINGLETON_VM81 |
                   HHS_EXACT_PASS219_AUTHORITY_REASON_PASS191_REPLAY;
    }

    memset(out_route, 0, sizeof(*out_route));
    out_route->struct_size = (uint32_t)sizeof(*out_route);
    out_route->version = hhs219_authority_router_version_word();
    out_route->decision = HHS_EXACT_PASS219_AUTHORITY_ROUTE_PASS169_REQUIRED;
    out_route->reason_mask = reasons;
    out_route->selected_evidence_role = selected;
    out_route->pass159_canonical_authority = 0U;
    out_route->candidate_adapter_canonical_authority = 0U;
    out_route->i1214_composition_canonical_authority = 0U;
    out_route->pass191_canonical_monolithic_authority = 0U;
    out_route->pass169_whole_expression_authority_required = 1U;
    out_route->whole_expression_semantics_resolved = 0U;
    out_route->canonical_monolithic_proof = 0U;
    out_route->floating_point_authority = 0U;
    out_route->vm81_mutation_authority = 0U;
    out_route->hash72_commit_authority = 0U;

    return HHS_EXACT_STATUS_OK;
}

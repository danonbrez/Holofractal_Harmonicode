#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

static HHSExactPass219AuthorityEvidenceV1 blank_evidence(void) {
    HHSExactPass219AuthorityEvidenceV1 evidence;
    memset(&evidence, 0, sizeof(evidence));
    evidence.struct_size = (uint32_t)sizeof(evidence);
    evidence.version = hhs_exact_pass219_authority_router_version();
    return evidence;
}

static void assert_pass169_boundary(const HHSExactPass219AuthorityRouteV1 *route) {
    assert(route != NULL);
    assert(route->decision == HHS_EXACT_PASS219_AUTHORITY_ROUTE_PASS169_REQUIRED);
    assert(route->pass159_canonical_authority == 0U);
    assert(route->candidate_adapter_canonical_authority == 0U);
    assert(route->i1214_composition_canonical_authority == 0U);
    assert(route->pass191_canonical_monolithic_authority == 0U);
    assert(route->pass169_whole_expression_authority_required == 1U);
    assert(route->whole_expression_semantics_resolved == 0U);
    assert(route->canonical_monolithic_proof == 0U);
    assert(route->floating_point_authority == 0U);
    assert(route->vm81_mutation_authority == 0U);
    assert(route->hash72_commit_authority == 0U);
    assert((route->reason_mask & HHS_EXACT_PASS219_AUTHORITY_REASON_PASS169_STILL_REQUIRED) != 0U);
}

int main(void) {
    HHSExactPass219AuthorityRouterDescriptorV1 descriptor;
    HHSExactPass219MonolithicDescriptorV1 monolithic;
    HHSExactPass219AuthorityEvidenceV1 evidence;
    HHSExactPass219AuthorityRouteV1 route;
    HHSExactStatus status;

    memset(&descriptor, 0, sizeof(descriptor));
    assert(hhs_exact_pass219_authority_router_descriptor(&descriptor) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_monolithic_descriptor(&monolithic) == HHS_EXACT_STATUS_OK);
    assert(descriptor.struct_size == sizeof(descriptor));
    assert(descriptor.version == hhs_exact_pass219_authority_router_version());
    assert(memcmp(descriptor.native_source_sha256,
                  monolithic.native_source_sha256,
                  HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES) == 0);
    assert(descriptor.pass159_source_pipeline_role ==
           HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS159_SOURCE_PIPELINE);
    assert(descriptor.i1213_candidate_role ==
           HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_I1213_CANDIDATE_DIAGNOSTIC);
    assert(descriptor.i1214_composition_role ==
           HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_I1214_UNRESOLVED_COMPOSITION);
    assert(descriptor.pass191_inherited_role ==
           HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS191_INHERITED_MANIFOLD);
    assert(descriptor.pass169_canonical_role ==
           HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS169_WHOLE_EXPRESSION);
    assert(descriptor.raw_evidence_can_prove == 0U);
    assert(descriptor.canonical_proven_decision_available == 0U);
    assert(descriptor.floating_point_authority == 0U);
    assert(descriptor.vm81_mutation_authority == 0U);
    assert(descriptor.hash72_commit_authority == 0U);

    evidence = blank_evidence();
    memset(&route, 0, sizeof(route));
    assert(hhs_exact_pass219_authority_route_evidence(&evidence, &route) == HHS_EXACT_STATUS_OK);
    assert(route.selected_evidence_role == HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_NONE);
    assert_pass169_boundary(&route);

    evidence = blank_evidence();
    evidence.source_identity_exact = 1U;
    evidence.pass159_source_pipeline_verified = 1U;
    evidence.pass159_vmir_identity_present = 1U;
    assert(hhs_exact_pass219_authority_route_evidence(&evidence, &route) == HHS_EXACT_STATUS_OK);
    assert(route.selected_evidence_role == HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS159_SOURCE_PIPELINE);
    assert((route.reason_mask & HHS_EXACT_PASS219_AUTHORITY_REASON_SOURCE_PIPELINE) != 0U);
    assert_pass169_boundary(&route);

    evidence.candidate_exact_execution_verified = 1U;
    evidence.candidate_exact_replay_verified = 1U;
    assert(hhs_exact_pass219_authority_route_evidence(&evidence, &route) == HHS_EXACT_STATUS_OK);
    assert(route.selected_evidence_role == HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_I1213_CANDIDATE_DIAGNOSTIC);
    assert((route.reason_mask & HHS_EXACT_PASS219_AUTHORITY_REASON_CANDIDATE_DIAGNOSTIC) != 0U);
    assert_pass169_boundary(&route);

    evidence.i1214_unresolved_composition_verified = 1U;
    assert(hhs_exact_pass219_authority_route_evidence(&evidence, &route) == HHS_EXACT_STATUS_OK);
    assert(route.selected_evidence_role == HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_I1214_UNRESOLVED_COMPOSITION);
    assert((route.reason_mask & HHS_EXACT_PASS219_AUTHORITY_REASON_UNRESOLVED_COMPOSITION) != 0U);
    assert_pass169_boundary(&route);

    evidence.pass191_inherited_manifold_verified = 1U;
    evidence.pass191_exact_context_scope_preserved = 1U;
    evidence.pass191_singleton_vm81_authority_verified = 1U;
    evidence.pass191_deterministic_replay_verified = 1U;
    assert(hhs_exact_pass219_authority_route_evidence(&evidence, &route) == HHS_EXACT_STATUS_OK);
    assert(route.selected_evidence_role == HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS191_INHERITED_MANIFOLD);
    assert((route.reason_mask & HHS_EXACT_PASS219_AUTHORITY_REASON_PASS191_MANIFOLD) != 0U);
    assert((route.reason_mask & HHS_EXACT_PASS219_AUTHORITY_REASON_PASS191_CONTEXT_SCOPE) != 0U);
    assert((route.reason_mask & HHS_EXACT_PASS219_AUTHORITY_REASON_PASS191_SINGLETON_VM81) != 0U);
    assert((route.reason_mask & HHS_EXACT_PASS219_AUTHORITY_REASON_PASS191_REPLAY) != 0U);
    assert_pass169_boundary(&route);

    /* Fail closed on inconsistent or caller-invented evidence bundles. */
    evidence = blank_evidence();
    evidence.pass159_source_pipeline_verified = 1U;
    status = hhs_exact_pass219_authority_route_evidence(&evidence, &route);
    assert(status == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    evidence = blank_evidence();
    evidence.source_identity_exact = 1U;
    evidence.candidate_exact_execution_verified = 1U;
    status = hhs_exact_pass219_authority_route_evidence(&evidence, &route);
    assert(status == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    evidence = blank_evidence();
    evidence.source_identity_exact = 1U;
    evidence.pass191_inherited_manifold_verified = 1U;
    status = hhs_exact_pass219_authority_route_evidence(&evidence, &route);
    assert(status == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    evidence = blank_evidence();
    evidence.source_identity_exact = 2U;
    status = hhs_exact_pass219_authority_route_evidence(&evidence, &route);
    assert(status == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    return 0;
}

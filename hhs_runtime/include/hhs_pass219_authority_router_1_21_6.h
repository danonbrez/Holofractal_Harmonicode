#ifndef HHS_PASS219_AUTHORITY_ROUTER_1_21_6_H
#define HHS_PASS219_AUTHORITY_ROUTER_1_21_6_H

#include "hhs_pass219_monolithic_constraint_abi_1_20.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_AUTHORITY_ROUTER_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_AUTHORITY_ROUTER_VERSION_MINOR 21U
#define HHS_EXACT_PASS219_AUTHORITY_ROUTER_VERSION_PATCH 6U

typedef enum HHSExactPass219AuthorityEvidenceRoleV1 {
    HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_NONE = 0,
    HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS159_SOURCE_PIPELINE = 1,
    HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_I1213_CANDIDATE_DIAGNOSTIC = 2,
    HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_I1214_UNRESOLVED_COMPOSITION = 3,
    HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS191_INHERITED_MANIFOLD = 4,
    HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS169_WHOLE_EXPRESSION = 5
} HHSExactPass219AuthorityEvidenceRoleV1;

typedef enum HHSExactPass219AuthorityRouteDecisionV1 {
    HHS_EXACT_PASS219_AUTHORITY_ROUTE_INVALID = 0,
    HHS_EXACT_PASS219_AUTHORITY_ROUTE_PASS169_REQUIRED = 1
} HHSExactPass219AuthorityRouteDecisionV1;

typedef enum HHSExactPass219AuthorityReasonV1 {
    HHS_EXACT_PASS219_AUTHORITY_REASON_SOURCE_PIPELINE = 1U << 0,
    HHS_EXACT_PASS219_AUTHORITY_REASON_CANDIDATE_DIAGNOSTIC = 1U << 1,
    HHS_EXACT_PASS219_AUTHORITY_REASON_UNRESOLVED_COMPOSITION = 1U << 2,
    HHS_EXACT_PASS219_AUTHORITY_REASON_PASS191_MANIFOLD = 1U << 3,
    HHS_EXACT_PASS219_AUTHORITY_REASON_PASS191_CONTEXT_SCOPE = 1U << 4,
    HHS_EXACT_PASS219_AUTHORITY_REASON_PASS191_SINGLETON_VM81 = 1U << 5,
    HHS_EXACT_PASS219_AUTHORITY_REASON_PASS191_REPLAY = 1U << 6,
    HHS_EXACT_PASS219_AUTHORITY_REASON_PASS169_STILL_REQUIRED = 1U << 7
} HHSExactPass219AuthorityReasonV1;

typedef struct HHSExactPass219AuthorityRouterDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t native_source_sha256[HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES];
    uint8_t pass159_source_pipeline_role;
    uint8_t i1213_candidate_role;
    uint8_t i1214_composition_role;
    uint8_t pass191_inherited_role;
    uint8_t pass169_canonical_role;
    uint8_t raw_evidence_can_prove;
    uint8_t canonical_proven_decision_available;
    uint8_t floating_point_authority;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t reserved0[2];
} HHSExactPass219AuthorityRouterDescriptorV1;

typedef struct HHSExactPass219AuthorityEvidenceV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t source_identity_exact;
    uint8_t pass159_source_pipeline_verified;
    uint8_t pass159_vmir_identity_present;
    uint8_t candidate_exact_execution_verified;
    uint8_t candidate_exact_replay_verified;
    uint8_t i1214_unresolved_composition_verified;
    uint8_t pass191_inherited_manifold_verified;
    uint8_t pass191_exact_context_scope_preserved;
    uint8_t pass191_singleton_vm81_authority_verified;
    uint8_t pass191_deterministic_replay_verified;
    uint8_t reserved0[2];
} HHSExactPass219AuthorityEvidenceV1;

typedef struct HHSExactPass219AuthorityRouteV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason_mask;
    uint8_t selected_evidence_role;
    uint8_t pass159_canonical_authority;
    uint8_t candidate_adapter_canonical_authority;
    uint8_t i1214_composition_canonical_authority;
    uint8_t pass191_canonical_monolithic_authority;
    uint8_t pass169_whole_expression_authority_required;
    uint8_t whole_expression_semantics_resolved;
    uint8_t canonical_monolithic_proof;
    uint8_t floating_point_authority;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t reserved0[1];
} HHSExactPass219AuthorityRouteV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_authority_router_version(void);

/*
 * Describe the fail-closed authority roles discovered by canonical-main census.
 * This descriptor never grants proof or mutation authority.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_authority_router_descriptor(
    HHSExactPass219AuthorityRouterDescriptorV1 *out_descriptor
);

/*
 * Classify independently verified evidence by role.
 *
 * This router is intentionally incapable of returning CANONICAL_PROVEN. Pass159
 * source-pipeline evidence, I121.3 candidate execution, I121.4 composition, and
 * frozen Pass191 exact-context manifold evidence are all upstream evidence only.
 * Canonical whole-expression closure remains the inherited Pass169 ordered
 * constraint-graph -> VMIR -> exact VM81 admission/commit -> Hash72/Hash216 ->
 * replay path.
 *
 * The input carries only evidence-presence flags. It cannot assert whole-expression
 * closure, VM81 mutation authority, or Hash72 commit authority.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_authority_route_evidence(
    const HHSExactPass219AuthorityEvidenceV1 *evidence,
    HHSExactPass219AuthorityRouteV1 *out_route
);

#ifdef __cplusplus
}
#endif

#endif

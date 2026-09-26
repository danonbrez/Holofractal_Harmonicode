#ifndef HHS_PASS219_LANE5_HNAN_GLOBAL_CONSTRAINT_1_63_H
#define HHS_PASS219_LANE5_HNAN_GLOBAL_CONSTRAINT_1_63_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION UINT32_C(0x0001003F)
#define HHS_EXACT_PASS219_HNAN_GLOBAL_NAMESPACE UINT32_C(0x0002193F)
#define HHS_EXACT_PASS219_HNAN_GLOBAL_RULE_COUNT UINT32_C(15)
#define HHS_EXACT_PASS219_HNAN_GLOBAL_ALL_RULES UINT32_C(0x00007FFF)

typedef enum HHSExactPass219HNANNodeV1 {
    HHS_EXACT_HNAN_NODE_NONE = 0,
    HHS_EXACT_HNAN_NODE_ZERO = 1,
    HHS_EXACT_HNAN_NODE_EMPTYSET = 2,
    HHS_EXACT_HNAN_NODE_AB_P4_EMPTYSET = 3,
    HHS_EXACT_HNAN_NODE_HNAN = 4,
    HHS_EXACT_HNAN_NODE_XYZW_SUM = 5,
    HHS_EXACT_HNAN_NODE_U72 = 6,
    HHS_EXACT_HNAN_NODE_U0 = 7,
    HHS_EXACT_HNAN_NODE_INFINITY = 8,
    HHS_EXACT_HNAN_NODE_DELTA = 9,
    HHS_EXACT_HNAN_NODE_X = 10,
    HHS_EXACT_HNAN_NODE_INFINITY_DELTA = 11,
    HHS_EXACT_HNAN_NODE_BX5184 = 12,
    HHS_EXACT_HNAN_NODE_P = 13,
    HHS_EXACT_HNAN_NODE_BX5184_OVER_DELTA = 14,
    HHS_EXACT_HNAN_NODE_ONE_OVER_ZERO = 15,
    HHS_EXACT_HNAN_NODE_HNAN_GATE = 16,
    HHS_EXACT_HNAN_NODE_J2_ZERO = 17,
    HHS_EXACT_HNAN_NODE_XY = 18,
    HHS_EXACT_HNAN_NODE_YX = 19,
    HHS_EXACT_HNAN_NODE_ZW = 20,
    HHS_EXACT_HNAN_NODE_WZ = 21,
    HHS_EXACT_HNAN_NODE_GAMMA_X = 22,
    HHS_EXACT_HNAN_NODE_ZERO_POWER4 = 23
} HHSExactPass219HNANNodeV1;

typedef enum HHSExactPass219HNANRelationV1 {
    HHS_EXACT_HNAN_REL_NONE = 0,
    HHS_EXACT_HNAN_REL_ORDERED_CLOSURE = 1,
    HHS_EXACT_HNAN_REL_TYPED_VIEW = 2,
    HHS_EXACT_HNAN_REL_PHASE_CLOSURE = 3,
    HHS_EXACT_HNAN_REL_DIRECTED_RECIPROCAL = 4,
    HHS_EXACT_HNAN_REL_UNBOUNDED_CARRIER = 5,
    HHS_EXACT_HNAN_REL_GLOBAL_DENOMINATOR = 6,
    HHS_EXACT_HNAN_REL_HNAN_BOUNDARY = 7,
    HHS_EXACT_HNAN_REL_JORDAN_CORRESPONDENCE = 8,
    HHS_EXACT_HNAN_REL_NONCOMMUTATIVE_DISTINCTION = 9,
    HHS_EXACT_HNAN_REL_DIRECTED_TYPED_IDENTITY = 10
} HHSExactPass219HNANRelationV1;

typedef enum HHSExactPass219HNANDecisionV1 {
    HHS_EXACT_HNAN_DECISION_INVALID = 0,
    HHS_EXACT_HNAN_DECISION_VERIFIED = 1,
    HHS_EXACT_HNAN_DECISION_REJECTED = 2,
    HHS_EXACT_HNAN_DECISION_UNRESOLVED = 3
} HHSExactPass219HNANDecisionV1;

typedef enum HHSExactPass219HNANReasonV1 {
    HHS_EXACT_HNAN_REASON_NONE = 0,
    HHS_EXACT_HNAN_REASON_INVALID_ARGUMENT = 1,
    HHS_EXACT_HNAN_REASON_UNKNOWN_RULE = 2,
    HHS_EXACT_HNAN_REASON_NODE_MISMATCH = 3,
    HHS_EXACT_HNAN_REASON_RELATION_MISMATCH = 4,
    HHS_EXACT_HNAN_REASON_SOURCE_ORDER = 5,
    HHS_EXACT_HNAN_REASON_TYPE_ERASURE = 6,
    HHS_EXACT_HNAN_REASON_SCALARIZATION = 7,
    HHS_EXACT_HNAN_REASON_DELTA_CANCELLATION = 8,
    HHS_EXACT_HNAN_REASON_FLOAT_INFINITY = 9,
    HHS_EXACT_HNAN_REASON_COMMUTATION = 10,
    HHS_EXACT_HNAN_REASON_EMPTYSET_CANCELLATION = 11,
    HHS_EXACT_HNAN_REASON_EQUALITY_REVERSAL = 12,
    HHS_EXACT_HNAN_REASON_JORDAN_FAILURE = 13,
    HHS_EXACT_HNAN_REASON_MANDATORY_INCOMPLETE = 14
} HHSExactPass219HNANReasonV1;

typedef struct HHSExactPass219HNANRuleV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t rule_id;
    uint32_t lhs_node;
    uint32_t rhs_node;
    uint32_t relation;
    uint8_t directional;
    uint8_t source_order_required;
    uint8_t typed_identity_required;
    uint8_t scalar_equality_authority;
    uint8_t cancellation_authority;
    uint8_t commutation_authority;
    uint8_t floating_infinity_authority;
    uint8_t reserved0;
} HHSExactPass219HNANRuleV1;

typedef struct HHSExactPass219HNANClaimV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t rule_id;
    uint32_t lhs_node;
    uint32_t rhs_node;
    uint32_t relation;
    uint8_t source_order_preserved;
    uint8_t typed_identity_preserved;
    uint8_t scalar_substitution_requested;
    uint8_t delta_cancellation_requested;
    uint8_t floating_infinity_requested;
    uint8_t commutation_requested;
    uint8_t emptyset_cancellation_requested;
    uint8_t equality_reversal_requested;
} HHSExactPass219HNANClaimV1;

typedef struct HHSExactPass219HNANResolutionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason;
    uint32_t rule_id;
    uint32_t lhs_node;
    uint32_t rhs_node;
    uint32_t relation;
    uint8_t exact_rule_match;
    uint8_t source_order_preserved;
    uint8_t typed_identity_preserved;
    uint8_t scalar_substitution_authority;
    uint8_t delta_cancellation_authority;
    uint8_t floating_infinity_authority;
    uint8_t commutation_authority;
    uint8_t emptyset_cancellation_authority;
    uint8_t equality_reversal_authority;
    uint8_t reserved0[7];
} HHSExactPass219HNANResolutionV1;

typedef struct HHSExactPass219HNANGlobalReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t decision;
    uint32_t reason;
    uint32_t required_rule_mask;
    uint32_t verified_rule_mask;
    uint32_t request_count;
    uint32_t first_rejected_index;
    uint32_t first_unresolved_index;
    uint32_t rank_m01;
    uint32_t nullity_m01;
    uint32_t nullity_m01_squared;
    uint64_t system_signature64;
    uint8_t jordan_depth2_verified;
    uint8_t minimal_polynomial_degree4_verified;
    uint8_t degree4_recurrence_verified;
    uint8_t hnan_channel_order_preserved;
    uint8_t ordered_zero_closure_preserved;
    uint8_t global_delta_denominator_preserved;
    uint8_t delta_cancellation_forbidden;
    uint8_t unbounded_carrier_symbolic;
    uint8_t u72_to_u0_closure_preserved;
    uint8_t xy_yx_distinct;
    uint8_t zw_wz_distinct;
    uint8_t candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t reserved0[8];
} HHSExactPass219HNANGlobalReceiptV1;

typedef struct HHSExactPass219HNANAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t mandatory_rule_count;
    uint32_t mandatory_rule_mask;
    uint8_t system_wide_lane5_constraint;
    uint8_t vm81_preflight_required;
    uint8_t signed_environmental_preflight_required;
    uint8_t exact_integer_only;
    uint8_t ordered_source_preserving;
    uint8_t typed_projection_only;
    uint8_t contradiction_resolution_fail_closed;
    uint8_t jordan_hnan_correspondence;
    uint8_t delta_global_denominator;
    uint8_t infinity_symbolic_unbounded_carrier;
    uint8_t bx5184_relation_preserved;
    uint8_t u0_phase_closure_preserved;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t floating_point_canonical_authority;
} HHSExactPass219HNANAuthorityV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_hnan_global_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hnan_global_authority(
    HHSExactPass219HNANAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hnan_global_rule(
    uint32_t rule_id,
    HHSExactPass219HNANRuleV1 *out_rule
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hnan_resolve(
    const HHSExactPass219HNANClaimV1 *claim,
    HHSExactPass219HNANResolutionV1 *out_resolution
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hnan_resolve_set(
    const HHSExactPass219HNANClaimV1 *claims,
    size_t claim_count,
    HHSExactPass219HNANGlobalReceiptV1 *out_receipt
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hnan_global_system_verify(
    HHSExactPass219HNANGlobalReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif

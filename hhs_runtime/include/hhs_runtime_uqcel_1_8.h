#ifndef HHS_RUNTIME_UQCEL_1_8_H
#define HHS_RUNTIME_UQCEL_1_8_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN ((HHSExactStatus)6)
#define HHS_EXACT_STATUS_CONSTRAINT_REJECTED ((HHSExactStatus)7)

#define HHS_EXACT_UQCEL_VERSION_MAJOR 1U
#define HHS_EXACT_UQCEL_VERSION_MINOR 0U
#define HHS_EXACT_UQCEL_VERSION_PATCH 0U
#define HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES 32U
#define HHS_EXACT_UQCEL_MAX_P_BYTES HHS_EXACT_VM81_FRAME_BYTES
#define HHS_EXACT_UQCEL_MAX_AB_BYTES (HHS_EXACT_VM81_FRAME_BYTES * 2U)
#define HHS_EXACT_UQCEL_MAX_DERIVED_BYTES (HHS_EXACT_VM81_FRAME_BYTES * 4U)
#define HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES 8192U
#define HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN 216U
#define HHS_EXACT_UQCEL_HASH216_STRLEN 217U

#define HHS_UQCEL_CONSTRAINT_SOURCE UINT64_C(0x0001)
#define HHS_UQCEL_CONSTRAINT_BIGINT_CANONICAL UINT64_C(0x0002)
#define HHS_UQCEL_CONSTRAINT_LOSHU UINT64_C(0x0004)
#define HHS_UQCEL_CONSTRAINT_METRIC UINT64_C(0x0008)
#define HHS_UQCEL_CONSTRAINT_P_DELTA UINT64_C(0x0010)
#define HHS_UQCEL_CONSTRAINT_AB_SYMMETRIC UINT64_C(0x0020)
#define HHS_UQCEL_CONSTRAINT_AB_QUARTIC UINT64_C(0x0040)
#define HHS_UQCEL_CONSTRAINT_QR_DOMAIN UINT64_C(0x0080)
#define HHS_UQCEL_CONSTRAINT_QR_PHASE UINT64_C(0x0100)
#define HHS_UQCEL_CONSTRAINT_VM5184 UINT64_C(0x0200)
#define HHS_UQCEL_CONSTRAINT_CORE_REQUIRED UINT64_C(0x03FF)

#define HHS_UQCEL_RESIDUAL_T_M_HARMONIC UINT64_C(0x0001)
#define HHS_UQCEL_RESIDUAL_TENSOR_S_F_AT_BT UINT64_C(0x0002)
#define HHS_UQCEL_RESIDUAL_DELTA_P_ROOT UINT64_C(0x0004)
#define HHS_UQCEL_RESIDUAL_MOD_F_U UINT64_C(0x0008)
#define HHS_UQCEL_RESIDUAL_DIAGNOSTIC_SOURCE UINT64_C(0x000F)
#define HHS_UQCEL_RESIDUAL_MONOLITHIC_EQUALITY_CHAIN UINT64_C(0x0010)
#define HHS_UQCEL_RESIDUAL_FULL_SOURCE UINT64_C(0x001F)

/*
 * ABI compatibility note (Pass 219 1.15 repair-forward clarification):
 * InputV1.A and InputV1.B are integer/symmetric compatibility-projection
 * witnesses for HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1. They do not
 * define the source-level A/B symbols of the full symbolic monolithic UCE.
 * For the full source equation, A denotes the complete LHS and B the complete
 * RHS; neither is definitionally P^2.
 */
#define HHS_EXACT_UQCEL_V1_AB_COMPATIBILITY_PROJECTION 1U

typedef enum HHSExactUQCELProfile {
    HHS_EXACT_UQCEL_PROFILE_NONE = 0,
    HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1 = 1,
    HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1 = 2
} HHSExactUQCELProfile;

typedef enum HHSExactUQCELDecision {
    HHS_EXACT_UQCEL_DECISION_UNRESOLVED = 0,
    HHS_EXACT_UQCEL_DECISION_ADMIT = 1,
    HHS_EXACT_UQCEL_DECISION_REJECT = 2,
    HHS_EXACT_UQCEL_DECISION_UNSUPPORTED_DOMAIN = 3
} HHSExactUQCELDecision;

typedef enum HHSExactUQCELRejectReason {
    HHS_EXACT_UQCEL_REASON_NONE = 0,
    HHS_EXACT_UQCEL_REASON_SOURCE_HASH = 1,
    HHS_EXACT_UQCEL_REASON_BIGINT_ENCODING = 2,
    HHS_EXACT_UQCEL_REASON_P_DELTA = 3,
    HHS_EXACT_UQCEL_REASON_AB_SYMMETRY = 4,
    HHS_EXACT_UQCEL_REASON_AB_QUARTIC = 5,
    HHS_EXACT_UQCEL_REASON_QR_DOMAIN = 6,
    HHS_EXACT_UQCEL_REASON_QR_PHASE = 7,
    HHS_EXACT_UQCEL_REASON_VM5184 = 8,
    HHS_EXACT_UQCEL_REASON_FULL_SYMBOLIC_RESIDUAL = 9
} HHSExactUQCELRejectReason;

typedef struct HHSExactBigUIntView {
    uint32_t struct_size;
    uint32_t byte_length;
    const uint8_t *bytes_be;
} HHSExactBigUIntView;

typedef struct HHSExactUQCELInputV1 {
    uint32_t struct_size;
    uint32_t uqcel_version;
    uint32_t profile;
    uint32_t flags;
    HHSExactBigUIntView P;
    HHSExactBigUIntView p;
    HHSExactBigUIntView q;
    HHSExactBigUIntView delta;
    HHSExactBigUIntView A;
    HHSExactBigUIntView B;
    uint8_t cell81;
    uint8_t left_basis8;
    uint8_t right_basis8;
    uint8_t reserved0;
    uint8_t source_envelope_sha256[HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES];
    char previous_hash72[HHS_EXACT_HASH72_STRLEN];
} HHSExactUQCELInputV1;

typedef struct HHSExactUQCELAdmissionV1 {
    uint32_t struct_size;
    uint32_t uqcel_version;
    uint32_t profile;
    uint32_t decision;
    uint32_t reject_reason;
    uint32_t reserved0;
    uint64_t required_mask;
    uint64_t satisfied_mask;
    uint64_t failed_mask;
    uint64_t residual_mask;
    uint16_t vm5184_address;
    uint16_t ordered_tag;
    uint8_t qr_bit;
    uint8_t expected_lane;
    uint8_t expected_phase;
    uint8_t observed_phase;
    uint8_t source_hash_match;
    uint8_t bigint_domain_exact;
    uint8_t frame_committed;
    uint8_t reserved1;
    int64_t primitive_metric_numerator;
    uint64_t primitive_metric_denominator;
    int64_t full_cycle_metric_exponent;
    uint64_t metric_power;
    char change_hash72[HHS_EXACT_HASH72_STRLEN];
    char receipt_hash72[HHS_EXACT_HASH72_STRLEN];
    char hash216_triplet[HHS_EXACT_UQCEL_HASH216_STRLEN];
    char hash216_identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
} HHSExactUQCELAdmissionV1;

HHS_EXACT_API uint32_t hhs_exact_uqcel_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_uqcel_source_sha256(
    uint8_t out_sha256[HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES]
);
HHS_EXACT_API HHSExactStatus hhs_exact_uqcel_validate(
    const HHSExactUQCELInputV1 *input,
    HHSExactUQCELAdmissionV1 *out_admission
);
HHS_EXACT_API HHSExactStatus hhs_exact_uqcel_receipt_material(
    const HHSExactUQCELInputV1 *input,
    const HHSExactUQCELAdmissionV1 *admission,
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
);
HHS_EXACT_API HHSExactStatus hhs_exact_vm81_admit_uqcel(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    HHSExactVM81Frame *out_committed_frame,
    HHSExactUQCELAdmissionV1 *out_admission
);

#ifdef __cplusplus
}
#endif

#endif

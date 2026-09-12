#ifndef HHS_PASS219_VM81_PQC_SIGNATURE_1_31_H
#define HHS_PASS219_VM81_PQC_SIGNATURE_1_31_H

#include "hhs_pass219_vm81_pqc_firewall_1_30.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32)
#define HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_INTERNAL_API
#else
#define HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_INTERNAL_API __attribute__((visibility("hidden")))
#endif

#define HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERSION UINT32_C(0x0001001F)
#define HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_SHA256_BYTES UINT32_C(32)
#define HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65 UINT32_C(1)
#define HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_SLH_DSA_SHA2_192S UINT32_C(2)

typedef enum HHSExactPass219VM81PQCSignatureDecisionV1 {
    HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_INVALID = 0,
    HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERIFIED = 1,
    HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_PROVIDER_UNAVAILABLE = 2,
    HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_KEY_DERIVATION_FAILED = 3,
    HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_SIGN_FAILED = 4,
    HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERIFY_FAILED = 5
} HHSExactPass219VM81PQCSignatureDecisionV1;

typedef struct HHSExactPass219VM81PQCSignatureReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t algorithm;
    uint32_t decision;
    uint32_t signature_length;
    uint8_t provider_available;
    uint8_t key_derived_from_kernel_root;
    uint8_t signature_generated_inside_kernel;
    uint8_t signature_verified_before_vm81;
    uint8_t external_key_authority;
    uint8_t external_signature_authority;
    uint8_t signature_is_canonical_receipt;
    uint8_t reserved0;
    uint8_t public_key_sha256[HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_SHA256_BYTES];
    uint8_t signed_message_sha256[HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_SHA256_BYTES];
    uint8_t signature_sha256[HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_SHA256_BYTES];
} HHSExactPass219VM81PQCSignatureReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_vm81_pqc_signature_version(void);
HHS_EXACT_API uint32_t hhs_exact_pass219_vm81_pqc_signature_provider_available(
    uint32_t algorithm
);

/*
 * 1.31 remains an internal signed primitive beneath the 1.32 environmental
 * successor.  It must not remain an independent production dynamic mutation
 * surface after Pass 219 environmental authority reconciliation.
 */
HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_INTERNAL_API HHSExactStatus
hhs_exact_pass219_vm81_pqc_admit_signed(
    uint32_t pass_number,
    uint32_t signature_algorithm,
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    int8_t lo_shu_group,
    uint16_t g243,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactVM81Frame *out_committed_frame,
    HHSExactPass219RNAAdmissionV1 *out_admission,
    HHSExactPass219VM81PQCFirewallReceiptV1 *out_firewall_receipt,
    HHSExactPass219VM81PQCSignatureReceiptV1 *out_signature_receipt
);

#ifdef __cplusplus
}
#endif

#endif

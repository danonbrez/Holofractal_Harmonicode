#ifndef HHS_PASS219_VM81_PQC_FIREWALL_1_30_H
#define HHS_PASS219_VM81_PQC_FIREWALL_1_30_H

#include "hhs_pass219_rna_transcription_1_10.h"
#include "hhs_pass219_core_holographic_four_lane_1_24.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32)
#define HHS_EXACT_PASS219_VM81_PQC_INTERNAL_API
#else
#define HHS_EXACT_PASS219_VM81_PQC_INTERNAL_API __attribute__((visibility("hidden")))
#endif

#define HHS_EXACT_PASS219_VM81_PQC_VERSION UINT32_C(0x0001001E)
#define HHS_EXACT_PASS219_VM81_PQC_MIN_PASS UINT32_C(220)
#define HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES UINT32_C(64)
#define HHS_EXACT_PASS219_VM81_PQC_TAG_BYTES UINT32_C(64)
#define HHS_EXACT_PASS219_VM81_PQC_KEY_HEX_CHARS UINT32_C(128)
#define HHS_EXACT_PASS219_VM81_PQC_KEY_ENV "HHS_VM81_PQC_FIREWALL_KEY_HEX"

typedef enum HHSExactPass219VM81PQCHaltReasonV1 {
    HHS_EXACT_PASS219_VM81_PQC_HALT_NONE = 0,
    HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_KEY = 1,
    HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_PASS_PATH = 2,
    HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_CELL_WALL_PATH = 3,
    HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_HASH216_REFERENCE = 4,
    HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_HASH_LINEAGE = 5,
    HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_CANDIDATE_HASH = 6,
    HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_PQC_AUTHENTICATOR = 7,
    HHS_EXACT_PASS219_VM81_PQC_HALT_AUTHORITY_ESCALATION = 8,
    HHS_EXACT_PASS219_VM81_PQC_HALT_CHILD_HASH216_INVARIANT = 9,
    HHS_EXACT_PASS219_VM81_PQC_HALT_LATCHED = 10,
    HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_PQC_SIGNATURE_PROFILE = 11,
    HHS_EXACT_PASS219_VM81_PQC_HALT_PQC_SIGNATURE_PROVIDER_UNAVAILABLE = 12,
    HHS_EXACT_PASS219_VM81_PQC_HALT_PQC_SIGNATURE_GENERATION_FAILED = 13,
    HHS_EXACT_PASS219_VM81_PQC_HALT_PQC_SIGNATURE_VERIFICATION_FAILED = 14
} HHSExactPass219VM81PQCHaltReasonV1;

typedef enum HHSExactPass219VM81PQCFirewallDecisionV1 {
    HHS_EXACT_PASS219_VM81_PQC_DECISION_INVALID = 0,
    HHS_EXACT_PASS219_VM81_PQC_DECISION_CANONICAL_REJECTED = 1,
    HHS_EXACT_PASS219_VM81_PQC_DECISION_COMMITTED = 2,
    HHS_EXACT_PASS219_VM81_PQC_DECISION_HALTED = 3
} HHSExactPass219VM81PQCFirewallDecisionV1;

typedef struct HHSExactPass219VM81PQCFirewallReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t decision;
    uint32_t halt_reason;
    uint32_t reserved0;
    uint64_t instruction_sequence;
    char candidate_hash72[HHS_EXACT_HASH72_STRLEN];
    char cell_wall_path_hash216[HHS_EXACT_UQCEL_HASH216_STRLEN];
    char parent_hash216_identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
    char child_hash216_identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
    uint64_t graph_signature64;
    uint64_t tensor_signature64;
    uint64_t decision_signature64;
    uint8_t pqc_tag[HHS_EXACT_PASS219_VM81_PQC_TAG_BYTES];
    uint8_t selected_lane;
    uint8_t parent_hash216_verified;
    uint8_t child_hash216_verified;
    uint8_t rna_cell_wall_routed;
    uint8_t pqc_authenticated;
    uint8_t inherited_rna_authority_invoked;
    uint8_t canonical_receipt_owned_by_inherited_authority;
    uint8_t firewall_is_canonical_authority;
    uint8_t halted;
    uint8_t reserved1[7];
} HHSExactPass219VM81PQCFirewallReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_vm81_pqc_firewall_version(void);

/*
 * Build/verify a canonical Hash216 reference using the firewall-owned
 * positional SHA-256 resolver. These functions are non-mutating and may be
 * used by callers to obtain a parent reference for a subsequent guarded
 * request. The transition identity is derived from the three Hash72 lanes;
 * it is never caller-authoritative.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_pqc_hash216_reference_init(
    const char previous_hash72[HHS_EXACT_HASH72_STRLEN],
    const char change_hash72[HHS_EXACT_HASH72_STRLEN],
    const char receipt_hash72[HHS_EXACT_HASH72_STRLEN],
    HHSExactPass219Hash216TransitionViewV1 *out_reference
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(
    HHSExactPass219Hash216TransitionViewV1 *out_reference
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_pqc_hash216_reference_verify(
    const HHSExactPass219Hash216TransitionViewV1 *reference
);

HHS_EXACT_API uint32_t hhs_exact_pass219_vm81_pqc_firewall_halted(void);
HHS_EXACT_API uint32_t hhs_exact_pass219_vm81_pqc_firewall_halt_reason(void);

/*
 * Internal unsigned predecessor retained only so the signed 1.31 successor
 * can reuse the already-verified HMAC/Hash216 machinery during migration.
 * It is deliberately hidden from the dynamic ABI.  Production callers must
 * use hhs_exact_pass219_vm81_pqc_admit_signed from the 1.31 successor.
 */
HHS_EXACT_PASS219_VM81_PQC_INTERNAL_API HHSExactStatus hhs_exact_pass219_vm81_pqc_admit(
    uint32_t pass_number,
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    int8_t lo_shu_group,
    uint16_t g243,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactVM81Frame *out_committed_frame,
    HHSExactPass219RNAAdmissionV1 *out_admission,
    HHSExactPass219VM81PQCFirewallReceiptV1 *out_firewall_receipt
);

#ifdef __cplusplus
}
#endif

#endif

#ifndef HHS_PASS219_PASS213_RECOVERY_BRIDGE_1_33_H
#define HHS_PASS219_PASS213_RECOVERY_BRIDGE_1_33_H

#include "hhs_pass219_vm81_environmental_recovery_1_32.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_PASS213_RECOVERY_VERSION UINT32_C(0x00010021)
#define HHS_EXACT_PASS219_PASS213_ROOT_BYTES UINT32_C(32)
#define HHS_EXACT_PASS219_PASS213_AUTH_BYTES UINT32_C(64)

typedef enum HHSExactPass219Pass213RecoveryDecisionV1 {
    HHS_EXACT_PASS219_PASS213_RECOVERY_DECISION_INVALID = 0,
    HHS_EXACT_PASS219_PASS213_RECOVERY_DECISION_AUTHENTICATED = 1,
    HHS_EXACT_PASS219_PASS213_RECOVERY_DECISION_CANDIDATE_RECOVERED = 2,
    HHS_EXACT_PASS219_PASS213_RECOVERY_DECISION_REJECTED = 3
} HHSExactPass219Pass213RecoveryDecisionV1;

typedef enum HHSExactPass219Pass213RecoveryReasonV1 {
    HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_NONE = 0,
    HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_STRUCTURE = 1,
    HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_SEQUENCE = 2,
    HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_ROOT = 3,
    HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_AUTHENTICATOR = 4,
    HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_NATIVE_RECOVERY = 5
} HHSExactPass219Pass213RecoveryReasonV1;

/*
 * Exact Pass213 evidence roots after the Pass213 runtime has validated:
 *   persistent inventory checkpoint,
 *   dual ML-DSA/SLH-DSA signed checkpoint,
 *   RFC3161 trusted timestamp anchor and trust bundle.
 *
 * The bridge authenticator is not a caller assertion.  It is an HMAC-SHA-512
 * under a domain-separated key derived from the existing VM81 firewall root.
 * It additionally binds the native 1.32 checkpoint root, ordered registry root,
 * and candidate Hash72 before native recovery can run.
 */
typedef struct HHSExactPass219Pass213RecoveryEvidenceV1 {
    uint32_t struct_size;
    uint32_t version;
    uint64_t signed_sequence;
    uint64_t checkpoint_sequence;
    uint8_t inventory_checkpoint_root_hash216[HHS_EXACT_PASS219_PASS213_ROOT_BYTES];
    uint8_t inventory_root_hash216[HHS_EXACT_PASS219_PASS213_ROOT_BYTES];
    uint8_t signed_checkpoint_root_hash216[HHS_EXACT_PASS219_PASS213_ROOT_BYTES];
    uint8_t verifier_bundle_root_hash216[HHS_EXACT_PASS219_PASS213_ROOT_BYTES];
    uint8_t timestamp_intent_root_hash216[HHS_EXACT_PASS219_PASS213_ROOT_BYTES];
    uint8_t timestamp_evidence_root_hash216[HHS_EXACT_PASS219_PASS213_ROOT_BYTES];
    uint8_t timestamp_anchor_root_hash216[HHS_EXACT_PASS219_PASS213_ROOT_BYTES];
    uint8_t timestamp_verification_receipt_hash216[HHS_EXACT_PASS219_PASS213_ROOT_BYTES];
    uint8_t hash216_lineage_root[HHS_EXACT_PASS219_PASS213_ROOT_BYTES];
    uint8_t prior_anchor_root_hash216[HHS_EXACT_PASS219_PASS213_ROOT_BYTES];
    uint8_t trust_bundle_sha256[HHS_EXACT_PASS219_PASS213_ROOT_BYTES];
    uint8_t message_imprint_sha256[HHS_EXACT_PASS219_PASS213_ROOT_BYTES];
    uint8_t bridge_authenticator[HHS_EXACT_PASS219_PASS213_AUTH_BYTES];
} HHSExactPass219Pass213RecoveryEvidenceV1;

typedef struct HHSExactPass219Pass213RecoveryReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason;
    uint64_t signed_sequence;
    uint64_t checkpoint_sequence;
    uint8_t inventory_bound;
    uint8_t pqc_checkpoint_bound;
    uint8_t rfc3161_anchor_bound;
    uint8_t hash216_lineage_bound;
    uint8_t native_checkpoint_bound;
    uint8_t bridge_authenticator_verified;
    uint8_t recovery_candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_receipt_authority;
    uint8_t reserved0[7];
    uint8_t evidence_root_sha256[HHS_EXACT_PASS219_PASS213_ROOT_BYTES];
} HHSExactPass219Pass213RecoveryReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_pass213_recovery_version(void);

/*
 * Public successor recovery boundary.  On success this returns only a verified
 * candidate frame; that candidate must still traverse ordinary 1.32 canonical
 * admission.  No Pass213 evidence, signature, timestamp, or recovery artifact
 * becomes VM81/Hash72/Hash216 mutation or receipt authority.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_environment_recover_pass213_candidate(
    const HHSExactPass219VM81RecoveryCheckpointV1 *checkpoint,
    const HHSExactPass219VM81Hash216RegistryEntryV1 *registry_entries,
    size_t registry_entry_count,
    const HHSExactPass219Pass213RecoveryEvidenceV1 *evidence,
    HHSExactVM81Frame *out_candidate_frame,
    HHSExactPass219VM81EnvironmentReceiptV1 *out_environment_receipt,
    HHSExactPass219Pass213RecoveryReceiptV1 *out_pass213_receipt
);

#ifdef __cplusplus
}
#endif

#endif

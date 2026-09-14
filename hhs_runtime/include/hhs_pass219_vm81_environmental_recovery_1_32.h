#ifndef HHS_PASS219_VM81_ENVIRONMENTAL_RECOVERY_1_32_H
#define HHS_PASS219_VM81_ENVIRONMENTAL_RECOVERY_1_32_H

#include "hhs_pass219_vm81_pqc_signature_1_31.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32)
#define HHS_EXACT_PASS219_VM81_ENV_INTERNAL_API
#else
#define HHS_EXACT_PASS219_VM81_ENV_INTERNAL_API __attribute__((visibility("hidden")))
#endif

#define HHS_EXACT_PASS219_VM81_ENV_VERSION UINT32_C(0x00010020)
#define HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES UINT32_C(32)
#define HHS_EXACT_PASS219_VM81_ENV_HMAC_BYTES UINT32_C(64)
#define HHS_EXACT_PASS219_VM81_ENV_MAX_REGISTRY_ENTRIES UINT32_C(216)
#define HHS_EXACT_PASS219_VM81_ENV_SECURITY_EPOCH UINT64_C(1)

typedef enum HHSExactPass219VM81EnvironmentStateV1 {
    HHS_EXACT_PASS219_VM81_ENV_STATE_UNINITIALIZED = 0,
    HHS_EXACT_PASS219_VM81_ENV_STATE_RUNNING = 1,
    HHS_EXACT_PASS219_VM81_ENV_STATE_FROZEN = 2,
    HHS_EXACT_PASS219_VM81_ENV_STATE_RECOVERING = 3,
    HHS_EXACT_PASS219_VM81_ENV_STATE_RECOVERY_HALTED = 4
} HHSExactPass219VM81EnvironmentStateV1;

typedef enum HHSExactPass219VM81EnvironmentDecisionV1 {
    HHS_EXACT_PASS219_VM81_ENV_DECISION_INVALID = 0,
    HHS_EXACT_PASS219_VM81_ENV_DECISION_READY = 1,
    HHS_EXACT_PASS219_VM81_ENV_DECISION_FROZEN = 2,
    HHS_EXACT_PASS219_VM81_ENV_DECISION_RECOVERED_CANDIDATE = 3,
    HHS_EXACT_PASS219_VM81_ENV_DECISION_RECOVERY_REJECTED = 4
} HHSExactPass219VM81EnvironmentDecisionV1;

typedef enum HHSExactPass219VM81EnvironmentReasonV1 {
    HHS_EXACT_PASS219_VM81_ENV_REASON_NONE = 0,
    HHS_EXACT_PASS219_VM81_ENV_REASON_KERNEL_ROOT_UNAVAILABLE = 1,
    HHS_EXACT_PASS219_VM81_ENV_REASON_GENESIS_ROOT_MISMATCH = 2,
    HHS_EXACT_PASS219_VM81_ENV_REASON_WITNESS_FAILURE = 3,
    HHS_EXACT_PASS219_VM81_ENV_REASON_CHECKPOINT_AUTHENTICATION = 4,
    HHS_EXACT_PASS219_VM81_ENV_REASON_ANTI_ROLLBACK = 5,
    HHS_EXACT_PASS219_VM81_ENV_REASON_HASH216_REGISTRY = 6,
    HHS_EXACT_PASS219_VM81_ENV_REASON_CANDIDATE_IDENTITY = 7,
    HHS_EXACT_PASS219_VM81_ENV_REASON_ENVIRONMENT_SIGNATURE = 8,
    HHS_EXACT_PASS219_VM81_ENV_REASON_LATCHED = 9
} HHSExactPass219VM81EnvironmentReasonV1;

typedef struct HHSExactPass219VM81Hash216RegistryEntryV1 {
    uint32_t position;
    uint8_t tombstoned;
    uint8_t reserved0[3];
    uint8_t identity_sha256[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
    uint8_t lineage_sha256[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
} HHSExactPass219VM81Hash216RegistryEntryV1;

typedef struct HHSExactPass219VM81RecoveryCheckpointV1 {
    uint32_t struct_size;
    uint32_t version;
    uint64_t security_epoch;
    uint64_t checkpoint_sequence;
    uint64_t anti_rollback_floor;
    uint32_t expected_registry_count;
    uint32_t reserved0;
    char expected_candidate_hash72[HHS_EXACT_HASH72_STRLEN];
    uint8_t expected_registry_root_sha256[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
    HHSExactVM81Frame candidate_frame;
    uint8_t checkpoint_root_sha256[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
    uint8_t checkpoint_authenticator[HHS_EXACT_PASS219_VM81_ENV_HMAC_BYTES];
} HHSExactPass219VM81RecoveryCheckpointV1;

typedef struct HHSExactPass219VM81EnvironmentReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t state;
    uint32_t decision;
    uint32_t reason;
    uint32_t signature_algorithm;
    uint64_t security_epoch;
    uint64_t witness_sequence;
    uint64_t checkpoint_sequence;
    uint64_t anti_rollback_floor;
    uint32_t registry_entry_count;
    uint32_t reserved0;
    uint8_t genesis_root_sha256[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
    uint8_t prior_witness_sha256[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
    uint8_t witness_sha256[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
    uint8_t registry_root_sha256[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
    uint8_t environment_signature_sha256[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
    uint8_t genesis_verified;
    uint8_t witness_verified;
    uint8_t registry_reconciled;
    uint8_t anti_rollback_verified;
    uint8_t environment_signature_verified;
    uint8_t recovery_candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_receipt_authority;
} HHSExactPass219VM81EnvironmentReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_vm81_environment_version(void);
HHS_EXACT_API uint32_t hhs_exact_pass219_vm81_environment_state(void);
HHS_EXACT_API uint64_t hhs_exact_pass219_vm81_environment_anti_rollback_floor(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_environment_genesis_root(
    uint8_t out_sha256[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES]
);

/* Pure verifier: cache/registry data never gains mutation authority. */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_environment_hash216_registry_root(
    const HHSExactPass219VM81Hash216RegistryEntryV1 *entries,
    size_t entry_count,
    uint8_t out_sha256[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES]
);

/*
 * Recovery verifies an internally authenticated checkpoint, anti-rollback
 * floor, full ordered Hash216 registry, and deterministic candidate identity.
 * On success it returns a candidate only.  The candidate MUST still traverse
 * hhs_exact_pass219_vm81_environment_admit_signed before canonical mutation.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_environment_recover_candidate(
    const HHSExactPass219VM81RecoveryCheckpointV1 *checkpoint,
    const HHSExactPass219VM81Hash216RegistryEntryV1 *registry_entries,
    size_t registry_entry_count,
    HHSExactVM81Frame *out_candidate_frame,
    HHSExactPass219VM81EnvironmentReceiptV1 *out_environment_receipt
);

/* Internal checkpoint creator for trusted recovery machinery only. */
HHS_EXACT_PASS219_VM81_ENV_INTERNAL_API HHSExactStatus
hhs_exact_pass219_vm81_environment_checkpoint_seal(
    uint64_t checkpoint_sequence,
    uint64_t anti_rollback_floor,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactPass219VM81Hash216RegistryEntryV1 *registry_entries,
    size_t registry_entry_count,
    HHSExactPass219VM81RecoveryCheckpointV1 *out_checkpoint
);

/*
 * Production 1.32 successor.  It verifies and PQ-signs the environmental
 * witness before delegating to the hidden 1.31 signed firewall.  Recovery and
 * environment code never owns VM81 or canonical receipt authority.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_environment_admit_signed(
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
    HHSExactPass219VM81PQCSignatureReceiptV1 *out_signature_receipt,
    HHSExactPass219VM81EnvironmentReceiptV1 *out_environment_receipt
);

#ifdef __cplusplus
}
#endif

#endif

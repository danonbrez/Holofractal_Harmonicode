#include "../include/hhs_pass219_pass213_recovery_bridge_1_33.h"

#include <openssl/crypto.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>

#include <string.h>

static const uint8_t HHS_P219_PASS213_BRIDGE_KEY_DOMAIN[] =
    "HHS-P219-PASS213-RECOVERY-BRIDGE-KEY-V1";
static const uint8_t HHS_P219_PASS213_BRIDGE_AUTH_DOMAIN[] =
    "HHS-P219-PASS213-RECOVERY-BRIDGE-AUTH-V1";
static const uint8_t HHS_P219_PASS213_BRIDGE_EVIDENCE_DOMAIN[] =
    "HHS-P219-PASS213-RECOVERY-EVIDENCE-V1";

static void hhs_p219_pass213_zero_receipt(
    HHSExactPass219Pass213RecoveryReceiptV1 *receipt
) {
    if (receipt == NULL)
        return;
    memset(receipt, 0, sizeof(*receipt));
    receipt->struct_size = (uint32_t)sizeof(*receipt);
    receipt->version = HHS_EXACT_PASS219_PASS213_RECOVERY_VERSION;
    receipt->recovery_candidate_only = 1U;
    receipt->canonical_mutation_authority = 0U;
    receipt->canonical_receipt_authority = 0U;
}

static int hhs_p219_pass213_nonzero_root(const uint8_t root[32]) {
    uint8_t aggregate = 0U;
    size_t i;
    if (root == NULL)
        return 0;
    for (i = 0U; i < 32U; ++i)
        aggregate |= root[i];
    return aggregate != 0U;
}

static void hhs_p219_pass213_fail_closed(
    HHSExactPass219Pass213RecoveryReceiptV1 *receipt,
    uint32_t reason
) {
    if (receipt != NULL) {
        receipt->decision = HHS_EXACT_PASS219_PASS213_RECOVERY_DECISION_REJECTED;
        receipt->reason = reason;
    }
    atomic_store(&hhs_p219_env_state, HHS_EXACT_PASS219_VM81_ENV_STATE_RECOVERY_HALTED);
    atomic_store(&hhs_p219_pqc_halt_reason,
                 HHS_EXACT_PASS219_VM81_PQC_HALT_PASS213_RECOVERY_EVIDENCE_FAILED);
    atomic_store(&hhs_p219_pqc_halted, 1U);
}

static int hhs_p219_pass213_derive_bridge_key(
    const uint8_t root_key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES],
    uint8_t out_key[HHS_EXACT_PASS219_PASS213_AUTH_BYTES]
) {
    unsigned int written = 0U;
    return root_key != NULL && out_key != NULL &&
           HMAC(EVP_sha512(), root_key, HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES,
                HHS_P219_PASS213_BRIDGE_KEY_DOMAIN,
                sizeof(HHS_P219_PASS213_BRIDGE_KEY_DOMAIN) - 1U,
                out_key, &written) != NULL &&
           written == HHS_EXACT_PASS219_PASS213_AUTH_BYTES;
}

static size_t hhs_p219_pass213_append_evidence(
    uint8_t *out,
    size_t capacity,
    const HHSExactPass219Pass213RecoveryEvidenceV1 *evidence,
    const HHSExactPass219VM81RecoveryCheckpointV1 *checkpoint
) {
    size_t cursor = 0U;
    const uint8_t *roots[] = {
        evidence->inventory_checkpoint_root_hash216,
        evidence->inventory_root_hash216,
        evidence->signed_checkpoint_root_hash216,
        evidence->verifier_bundle_root_hash216,
        evidence->timestamp_intent_root_hash216,
        evidence->timestamp_evidence_root_hash216,
        evidence->timestamp_anchor_root_hash216,
        evidence->timestamp_verification_receipt_hash216,
        evidence->hash216_lineage_root,
        evidence->prior_anchor_root_hash216,
        evidence->trust_bundle_sha256,
        evidence->message_imprint_sha256
    };
    size_t i;

    cursor = hhs_p219_pqc_append(
        out, capacity, cursor,
        HHS_P219_PASS213_BRIDGE_EVIDENCE_DOMAIN,
        sizeof(HHS_P219_PASS213_BRIDGE_EVIDENCE_DOMAIN) - 1U);
    cursor = hhs_p219_pqc_append_u32_be(
        out, capacity, cursor, HHS_EXACT_PASS219_PASS213_RECOVERY_VERSION);
    cursor = hhs_p219_pqc_append_u64_be(
        out, capacity, cursor, evidence->signed_sequence);
    cursor = hhs_p219_pqc_append_u64_be(
        out, capacity, cursor, evidence->checkpoint_sequence);
    for (i = 0U; i < sizeof(roots) / sizeof(roots[0]); ++i)
        cursor = hhs_p219_pqc_append(out, capacity, cursor, roots[i], 32U);
    cursor = hhs_p219_pqc_append(
        out, capacity, cursor,
        checkpoint->checkpoint_root_sha256,
        HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    cursor = hhs_p219_pqc_append(
        out, capacity, cursor,
        checkpoint->expected_registry_root_sha256,
        HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    cursor = hhs_p219_pqc_append(
        out, capacity, cursor,
        checkpoint->expected_candidate_hash72,
        HHS_EXACT_HASH72_LEN);
    return cursor;
}

static HHSExactStatus hhs_p219_pass213_verify_evidence(
    const HHSExactPass219VM81RecoveryCheckpointV1 *checkpoint,
    const HHSExactPass219Pass213RecoveryEvidenceV1 *evidence,
    HHSExactPass219Pass213RecoveryReceiptV1 *receipt
) {
    uint8_t root_key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES];
    uint8_t bridge_key[HHS_EXACT_PASS219_PASS213_AUTH_BYTES];
    uint8_t material[1024];
    uint8_t auth_material[1100];
    uint8_t expected_auth[HHS_EXACT_PASS219_PASS213_AUTH_BYTES];
    uint8_t evidence_root[HHS_EXACT_PASS219_PASS213_ROOT_BYTES];
    size_t cursor;
    size_t auth_cursor = 0U;
    unsigned int written = 0U;
    int ok = 0;

    memset(root_key, 0, sizeof(root_key));
    memset(bridge_key, 0, sizeof(bridge_key));
    memset(expected_auth, 0, sizeof(expected_auth));
    memset(evidence_root, 0, sizeof(evidence_root));

    if (checkpoint == NULL || evidence == NULL || receipt == NULL ||
        evidence->struct_size != sizeof(*evidence) ||
        evidence->version != HHS_EXACT_PASS219_PASS213_RECOVERY_VERSION) {
        hhs_p219_pass213_fail_closed(
            receipt, HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_STRUCTURE);
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    if (evidence->signed_sequence == 0U || evidence->checkpoint_sequence == 0U ||
        evidence->checkpoint_sequence != checkpoint->checkpoint_sequence ||
        evidence->signed_sequence > evidence->checkpoint_sequence) {
        hhs_p219_pass213_fail_closed(
            receipt, HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_SEQUENCE);
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    if (!hhs_p219_pass213_nonzero_root(evidence->inventory_checkpoint_root_hash216) ||
        !hhs_p219_pass213_nonzero_root(evidence->inventory_root_hash216) ||
        !hhs_p219_pass213_nonzero_root(evidence->signed_checkpoint_root_hash216) ||
        !hhs_p219_pass213_nonzero_root(evidence->verifier_bundle_root_hash216) ||
        !hhs_p219_pass213_nonzero_root(evidence->timestamp_intent_root_hash216) ||
        !hhs_p219_pass213_nonzero_root(evidence->timestamp_evidence_root_hash216) ||
        !hhs_p219_pass213_nonzero_root(evidence->timestamp_anchor_root_hash216) ||
        !hhs_p219_pass213_nonzero_root(evidence->timestamp_verification_receipt_hash216) ||
        !hhs_p219_pass213_nonzero_root(evidence->hash216_lineage_root) ||
        !hhs_p219_pass213_nonzero_root(evidence->trust_bundle_sha256) ||
        !hhs_p219_pass213_nonzero_root(evidence->message_imprint_sha256)) {
        hhs_p219_pass213_fail_closed(
            receipt, HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_ROOT);
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    cursor = hhs_p219_pass213_append_evidence(
        material, sizeof(material), evidence, checkpoint);
    if (cursor == SIZE_MAX ||
        EVP_Digest(material, cursor, evidence_root, &written, EVP_sha256(), NULL) != 1 ||
        written != HHS_EXACT_PASS219_PASS213_ROOT_BYTES ||
        !hhs_p219_pqc_load_key(root_key) ||
        !hhs_p219_pass213_derive_bridge_key(root_key, bridge_key))
        goto done;

    auth_cursor = hhs_p219_pqc_append(
        auth_material, sizeof(auth_material), auth_cursor,
        HHS_P219_PASS213_BRIDGE_AUTH_DOMAIN,
        sizeof(HHS_P219_PASS213_BRIDGE_AUTH_DOMAIN) - 1U);
    auth_cursor = hhs_p219_pqc_append(
        auth_material, sizeof(auth_material), auth_cursor, material, cursor);
    if (auth_cursor == SIZE_MAX ||
        HMAC(EVP_sha512(), bridge_key, sizeof(bridge_key),
             auth_material, auth_cursor, expected_auth, &written) == NULL ||
        written != HHS_EXACT_PASS219_PASS213_AUTH_BYTES ||
        CRYPTO_memcmp(expected_auth, evidence->bridge_authenticator,
                      HHS_EXACT_PASS219_PASS213_AUTH_BYTES) != 0)
        goto done;

    memcpy(receipt->evidence_root_sha256, evidence_root, sizeof(evidence_root));
    receipt->signed_sequence = evidence->signed_sequence;
    receipt->checkpoint_sequence = evidence->checkpoint_sequence;
    receipt->inventory_bound = 1U;
    receipt->pqc_checkpoint_bound = 1U;
    receipt->rfc3161_anchor_bound = 1U;
    receipt->hash216_lineage_bound = 1U;
    receipt->native_checkpoint_bound = 1U;
    receipt->bridge_authenticator_verified = 1U;
    receipt->decision = HHS_EXACT_PASS219_PASS213_RECOVERY_DECISION_AUTHENTICATED;
    receipt->reason = HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_NONE;
    ok = 1;

done:
    OPENSSL_cleanse(root_key, sizeof(root_key));
    OPENSSL_cleanse(bridge_key, sizeof(bridge_key));
    OPENSSL_cleanse(expected_auth, sizeof(expected_auth));
    if (!ok) {
        hhs_p219_pass213_fail_closed(
            receipt, HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_AUTHENTICATOR);
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

uint32_t hhs_exact_pass219_pass213_recovery_version(void) {
    return HHS_EXACT_PASS219_PASS213_RECOVERY_VERSION;
}

HHSExactStatus hhs_exact_pass219_vm81_environment_recover_pass213_candidate(
    const HHSExactPass219VM81RecoveryCheckpointV1 *checkpoint,
    const HHSExactPass219VM81Hash216RegistryEntryV1 *registry_entries,
    size_t registry_entry_count,
    const HHSExactPass219Pass213RecoveryEvidenceV1 *evidence,
    HHSExactVM81Frame *out_candidate_frame,
    HHSExactPass219VM81EnvironmentReceiptV1 *out_environment_receipt,
    HHSExactPass219Pass213RecoveryReceiptV1 *out_pass213_receipt
) {
    HHSExactStatus status;
    if (out_candidate_frame == NULL || out_environment_receipt == NULL ||
        out_pass213_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_candidate_frame, 0, sizeof(*out_candidate_frame));
    memset(out_environment_receipt, 0, sizeof(*out_environment_receipt));
    hhs_p219_pass213_zero_receipt(out_pass213_receipt);

    status = hhs_p219_pass213_verify_evidence(
        checkpoint, evidence, out_pass213_receipt);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219_vm81_environment_recover_candidate(
        checkpoint, registry_entries, registry_entry_count,
        out_candidate_frame, out_environment_receipt);
    if (status != HHS_EXACT_STATUS_OK) {
        out_pass213_receipt->decision =
            HHS_EXACT_PASS219_PASS213_RECOVERY_DECISION_REJECTED;
        out_pass213_receipt->reason =
            HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_NATIVE_RECOVERY;
        return status;
    }
    out_pass213_receipt->decision =
        HHS_EXACT_PASS219_PASS213_RECOVERY_DECISION_CANDIDATE_RECOVERED;
    out_pass213_receipt->reason = HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_NONE;
    return HHS_EXACT_STATUS_OK;
}

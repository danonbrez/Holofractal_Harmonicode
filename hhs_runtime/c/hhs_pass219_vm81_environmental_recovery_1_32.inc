#include "../include/hhs_pass219_vm81_environmental_recovery_1_32.h"

#include <openssl/crypto.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>

#include <stdatomic.h>
#include <string.h>

static const uint8_t HHS_P219_ENV_GENESIS_DOMAIN[] =
    "HHS-P219-VM81-ENV-GENESIS-ROOT-V1";
static const uint8_t HHS_P219_ENV_WITNESS_DOMAIN[] =
    "HHS-P219-VM81-ENV-WITNESS-V1";
static const uint8_t HHS_P219_ENV_REGISTRY_DOMAIN[] =
    "HHS-P219-VM81-HASH216-REGISTRY-V1";
static const uint8_t HHS_P219_ENV_CHECKPOINT_DOMAIN[] =
    "HHS-P219-VM81-RECOVERY-CHECKPOINT-V1";
static const uint8_t HHS_P219_ENV_CHECKPOINT_AUTH_DOMAIN[] =
    "HHS-P219-VM81-RECOVERY-CHECKPOINT-AUTH-V1";

static atomic_uint hhs_p219_env_state =
    ATOMIC_VAR_INIT(HHS_EXACT_PASS219_VM81_ENV_STATE_UNINITIALIZED);
static atomic_uint_fast64_t hhs_p219_env_witness_sequence = ATOMIC_VAR_INIT(UINT64_C(0));
static atomic_uint_fast64_t hhs_p219_env_anti_rollback_floor = ATOMIC_VAR_INIT(UINT64_C(0));
static atomic_flag hhs_p219_env_lock = ATOMIC_FLAG_INIT;
static uint8_t hhs_p219_env_genesis_root[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
static uint8_t hhs_p219_env_prior_witness[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];

static void hhs_p219_env_lock_acquire(void) {
    while (atomic_flag_test_and_set_explicit(&hhs_p219_env_lock, memory_order_acquire)) {
        /* bounded critical sections only */
    }
}

static void hhs_p219_env_lock_release(void) {
    atomic_flag_clear_explicit(&hhs_p219_env_lock, memory_order_release);
}

static void hhs_p219_env_zero_receipt(
    HHSExactPass219VM81EnvironmentReceiptV1 *receipt,
    uint32_t signature_algorithm
) {
    if (receipt == NULL)
        return;
    memset(receipt, 0, sizeof(*receipt));
    receipt->struct_size = (uint32_t)sizeof(*receipt);
    receipt->version = HHS_EXACT_PASS219_VM81_ENV_VERSION;
    receipt->state = atomic_load(&hhs_p219_env_state);
    receipt->signature_algorithm = signature_algorithm;
    receipt->security_epoch = HHS_EXACT_PASS219_VM81_ENV_SECURITY_EPOCH;
    receipt->anti_rollback_floor = atomic_load(&hhs_p219_env_anti_rollback_floor);
    receipt->recovery_candidate_only = 1U;
    receipt->canonical_mutation_authority = 0U;
    receipt->canonical_receipt_authority = 0U;
}

static int hhs_p219_env_hmac_sha256(
    const uint8_t key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES],
    const uint8_t *material,
    size_t material_length,
    uint8_t out[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES]
) {
    unsigned int written = 0U;
    return key != NULL && material != NULL && out != NULL &&
           HMAC(EVP_sha256(), key, HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES,
                material, material_length, out, &written) != NULL &&
           written == HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES;
}

static int hhs_p219_env_hmac_sha512(
    const uint8_t key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES],
    const uint8_t *material,
    size_t material_length,
    uint8_t out[HHS_EXACT_PASS219_VM81_ENV_HMAC_BYTES]
) {
    unsigned int written = 0U;
    return key != NULL && material != NULL && out != NULL &&
           HMAC(EVP_sha512(), key, HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES,
                material, material_length, out, &written) != NULL &&
           written == HHS_EXACT_PASS219_VM81_ENV_HMAC_BYTES;
}

static int hhs_p219_env_compute_genesis_root(
    const uint8_t key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES],
    uint8_t out[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES]
) {
    uint8_t material[1024];
    size_t cursor = 0U;
    const char *openssl_version = OpenSSL_version(OPENSSL_VERSION);
    const uint32_t frame_bytes = HHS_EXACT_VM81_FRAME_BYTES;

    if (key == NULL || out == NULL || openssl_version == NULL)
        return 0;
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor,
        HHS_P219_ENV_GENESIS_DOMAIN, sizeof(HHS_P219_ENV_GENESIS_DOMAIN) - 1U);
    cursor = hhs_p219_pqc_append_u32_be(
        material, sizeof(material), cursor, HHS_EXACT_PASS219_VM81_PQC_VERSION);
    cursor = hhs_p219_pqc_append_u32_be(
        material, sizeof(material), cursor, HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERSION);
    cursor = hhs_p219_pqc_append_u32_be(
        material, sizeof(material), cursor, HHS_EXACT_PASS219_VM81_ENV_VERSION);
    cursor = hhs_p219_pqc_append_u32_be(
        material, sizeof(material), cursor, hhs_exact_pass219_rna_version());
    cursor = hhs_p219_pqc_append_u32_be(material, sizeof(material), cursor, frame_bytes);
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor,
        openssl_version, strlen(openssl_version));
    if (cursor == SIZE_MAX)
        return 0;
    return hhs_p219_env_hmac_sha256(key, material, cursor, out);
}

static int hhs_p219_env_ensure_initialized(
    const uint8_t key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES]
) {
    uint8_t root[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
    if (key == NULL)
        return 0;
    if (atomic_load(&hhs_p219_env_state) != HHS_EXACT_PASS219_VM81_ENV_STATE_UNINITIALIZED)
        return 1;
    if (!hhs_p219_env_compute_genesis_root(key, root))
        return 0;
    hhs_p219_env_lock_acquire();
    if (atomic_load(&hhs_p219_env_state) == HHS_EXACT_PASS219_VM81_ENV_STATE_UNINITIALIZED) {
        memcpy(hhs_p219_env_genesis_root, root, sizeof(root));
        memset(hhs_p219_env_prior_witness, 0, sizeof(hhs_p219_env_prior_witness));
        atomic_store(&hhs_p219_env_state, HHS_EXACT_PASS219_VM81_ENV_STATE_RUNNING);
    }
    hhs_p219_env_lock_release();
    OPENSSL_cleanse(root, sizeof(root));
    return 1;
}

static int hhs_p219_env_measurement_matches(
    const uint8_t key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES]
) {
    uint8_t current[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
    int ok;
    if (!hhs_p219_env_compute_genesis_root(key, current))
        return 0;
    ok = CRYPTO_memcmp(current, hhs_p219_env_genesis_root, sizeof(current)) == 0;
    OPENSSL_cleanse(current, sizeof(current));
    return ok;
}

uint32_t hhs_exact_pass219_vm81_environment_version(void) {
    return HHS_EXACT_PASS219_VM81_ENV_VERSION;
}

uint32_t hhs_exact_pass219_vm81_environment_state(void) {
    return atomic_load(&hhs_p219_env_state);
}

uint64_t hhs_exact_pass219_vm81_environment_anti_rollback_floor(void) {
    return atomic_load(&hhs_p219_env_anti_rollback_floor);
}

HHSExactStatus hhs_exact_pass219_vm81_environment_genesis_root(
    uint8_t out_sha256[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES]
) {
    uint8_t key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES];
    if (out_sha256 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_p219_pqc_load_key(key))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!hhs_p219_env_ensure_initialized(key)) {
        OPENSSL_cleanse(key, sizeof(key));
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    memcpy(out_sha256, hhs_p219_env_genesis_root, HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    OPENSSL_cleanse(key, sizeof(key));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_vm81_environment_hash216_registry_root(
    const HHSExactPass219VM81Hash216RegistryEntryV1 *entries,
    size_t entry_count,
    uint8_t out_sha256[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES]
) {
    EVP_MD_CTX *ctx = NULL;
    uint8_t count_be[4];
    unsigned int written = 0U;
    size_t i;
    if (out_sha256 == NULL || entry_count > HHS_EXACT_PASS219_VM81_ENV_MAX_REGISTRY_ENTRIES ||
        (entry_count != 0U && entries == NULL))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    count_be[0] = (uint8_t)(entry_count >> 24U);
    count_be[1] = (uint8_t)(entry_count >> 16U);
    count_be[2] = (uint8_t)(entry_count >> 8U);
    count_be[3] = (uint8_t)entry_count;
    ctx = EVP_MD_CTX_new();
    if (ctx == NULL || EVP_DigestInit_ex(ctx, EVP_sha256(), NULL) != 1 ||
        EVP_DigestUpdate(ctx, HHS_P219_ENV_REGISTRY_DOMAIN,
                         sizeof(HHS_P219_ENV_REGISTRY_DOMAIN) - 1U) != 1 ||
        EVP_DigestUpdate(ctx, count_be, sizeof(count_be)) != 1)
        goto failed;
    for (i = 0U; i < entry_count; ++i) {
        uint8_t position_be[4];
        if (entries[i].position != (uint32_t)i || entries[i].tombstoned > 1U)
            goto failed;
        position_be[0] = (uint8_t)(entries[i].position >> 24U);
        position_be[1] = (uint8_t)(entries[i].position >> 16U);
        position_be[2] = (uint8_t)(entries[i].position >> 8U);
        position_be[3] = (uint8_t)entries[i].position;
        if (EVP_DigestUpdate(ctx, position_be, sizeof(position_be)) != 1 ||
            EVP_DigestUpdate(ctx, &entries[i].tombstoned, 1U) != 1 ||
            EVP_DigestUpdate(ctx, entries[i].identity_sha256,
                             HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES) != 1 ||
            EVP_DigestUpdate(ctx, entries[i].lineage_sha256,
                             HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES) != 1)
            goto failed;
    }
    if (EVP_DigestFinal_ex(ctx, out_sha256, &written) != 1 ||
        written != HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES)
        goto failed;
    EVP_MD_CTX_free(ctx);
    return HHS_EXACT_STATUS_OK;

failed:
    EVP_MD_CTX_free(ctx);
    memset(out_sha256, 0, HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

static HHSExactStatus hhs_p219_env_checkpoint_root(
    const HHSExactPass219VM81RecoveryCheckpointV1 *checkpoint,
    uint8_t out_root[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES]
) {
    uint8_t material[2048];
    uint8_t frame_bytes[HHS_EXACT_VM81_FRAME_BYTES];
    size_t frame_length = 0U;
    size_t cursor = 0U;
    HHSExactStatus status;
    if (checkpoint == NULL || out_root == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_vm81_frame_export_le(
        &checkpoint->candidate_frame, frame_bytes, sizeof(frame_bytes), &frame_length);
    if (status != HHS_EXACT_STATUS_OK || frame_length != sizeof(frame_bytes))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor,
        HHS_P219_ENV_CHECKPOINT_DOMAIN, sizeof(HHS_P219_ENV_CHECKPOINT_DOMAIN) - 1U);
    cursor = hhs_p219_pqc_append_u64_be(material, sizeof(material), cursor,
                                        checkpoint->security_epoch);
    cursor = hhs_p219_pqc_append_u64_be(material, sizeof(material), cursor,
                                        checkpoint->checkpoint_sequence);
    cursor = hhs_p219_pqc_append_u64_be(material, sizeof(material), cursor,
                                        checkpoint->anti_rollback_floor);
    cursor = hhs_p219_pqc_append_u32_be(material, sizeof(material), cursor,
                                        checkpoint->expected_registry_count);
    cursor = hhs_p219_pqc_append(material, sizeof(material), cursor,
        checkpoint->expected_candidate_hash72, HHS_EXACT_HASH72_LEN);
    cursor = hhs_p219_pqc_append(material, sizeof(material), cursor,
        checkpoint->expected_registry_root_sha256,
        HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    cursor = hhs_p219_pqc_append(material, sizeof(material), cursor,
        frame_bytes, sizeof(frame_bytes));
    if (cursor == SIZE_MAX || !hhs_p219_pqc_sha256(material, cursor, out_root))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_vm81_environment_checkpoint_seal(
    uint64_t checkpoint_sequence,
    uint64_t anti_rollback_floor,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactPass219VM81Hash216RegistryEntryV1 *registry_entries,
    size_t registry_entry_count,
    HHSExactPass219VM81RecoveryCheckpointV1 *out_checkpoint
) {
    uint8_t key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES];
    uint8_t auth_material[128];
    size_t cursor = 0U;
    HHSExactStatus status;
    if (candidate_frame == NULL || out_checkpoint == NULL ||
        registry_entry_count > HHS_EXACT_PASS219_VM81_ENV_MAX_REGISTRY_ENTRIES ||
        checkpoint_sequence < anti_rollback_floor ||
        anti_rollback_floor < atomic_load(&hhs_p219_env_anti_rollback_floor))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_p219_pqc_load_key(key) || !hhs_p219_env_ensure_initialized(key)) {
        OPENSSL_cleanse(key, sizeof(key));
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    memset(out_checkpoint, 0, sizeof(*out_checkpoint));
    out_checkpoint->struct_size = (uint32_t)sizeof(*out_checkpoint);
    out_checkpoint->version = HHS_EXACT_PASS219_VM81_ENV_VERSION;
    out_checkpoint->security_epoch = HHS_EXACT_PASS219_VM81_ENV_SECURITY_EPOCH;
    out_checkpoint->checkpoint_sequence = checkpoint_sequence;
    out_checkpoint->anti_rollback_floor = anti_rollback_floor;
    out_checkpoint->expected_registry_count = (uint32_t)registry_entry_count;
    memcpy(&out_checkpoint->candidate_frame, candidate_frame, sizeof(*candidate_frame));
    status = hhs_exact_pass219_vm81_environment_hash216_registry_root(
        registry_entries, registry_entry_count,
        out_checkpoint->expected_registry_root_sha256);
    if (status != HHS_EXACT_STATUS_OK ||
        hhs_p219_pqc_candidate_hash72(candidate_frame,
            out_checkpoint->expected_candidate_hash72) != HHS_EXACT_STATUS_OK ||
        hhs_p219_env_checkpoint_root(out_checkpoint,
            out_checkpoint->checkpoint_root_sha256) != HHS_EXACT_STATUS_OK) {
        OPENSSL_cleanse(key, sizeof(key));
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    cursor = hhs_p219_pqc_append(auth_material, sizeof(auth_material), cursor,
        HHS_P219_ENV_CHECKPOINT_AUTH_DOMAIN,
        sizeof(HHS_P219_ENV_CHECKPOINT_AUTH_DOMAIN) - 1U);
    cursor = hhs_p219_pqc_append(auth_material, sizeof(auth_material), cursor,
        out_checkpoint->checkpoint_root_sha256,
        HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    if (cursor == SIZE_MAX || !hhs_p219_env_hmac_sha512(
            key, auth_material, cursor, out_checkpoint->checkpoint_authenticator)) {
        OPENSSL_cleanse(key, sizeof(key));
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    OPENSSL_cleanse(key, sizeof(key));
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus hhs_p219_env_verify_checkpoint(
    const uint8_t key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES],
    const HHSExactPass219VM81RecoveryCheckpointV1 *checkpoint,
    const HHSExactPass219VM81Hash216RegistryEntryV1 *registry_entries,
    size_t registry_entry_count,
    HHSExactPass219VM81EnvironmentReceiptV1 *receipt
) {
    uint8_t registry_root[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
    uint8_t checkpoint_root[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
    uint8_t expected_auth[HHS_EXACT_PASS219_VM81_ENV_HMAC_BYTES];
    uint8_t auth_material[128];
    char candidate_hash72[HHS_EXACT_HASH72_STRLEN];
    size_t cursor = 0U;
    if (checkpoint == NULL || receipt == NULL ||
        checkpoint->struct_size != sizeof(*checkpoint) ||
        checkpoint->version != HHS_EXACT_PASS219_VM81_ENV_VERSION ||
        checkpoint->security_epoch != HHS_EXACT_PASS219_VM81_ENV_SECURITY_EPOCH ||
        checkpoint->checkpoint_sequence < checkpoint->anti_rollback_floor ||
        checkpoint->checkpoint_sequence < atomic_load(&hhs_p219_env_anti_rollback_floor) ||
        checkpoint->expected_registry_count != registry_entry_count)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (hhs_exact_pass219_vm81_environment_hash216_registry_root(
            registry_entries, registry_entry_count, registry_root) != HHS_EXACT_STATUS_OK ||
        CRYPTO_memcmp(registry_root, checkpoint->expected_registry_root_sha256,
                      sizeof(registry_root)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    receipt->registry_reconciled = 1U;
    receipt->registry_entry_count = (uint32_t)registry_entry_count;
    memcpy(receipt->registry_root_sha256, registry_root, sizeof(registry_root));
    receipt->anti_rollback_verified = 1U;

    if (hhs_p219_pqc_candidate_hash72(
            &checkpoint->candidate_frame, candidate_hash72) != HHS_EXACT_STATUS_OK ||
        memcmp(candidate_hash72, checkpoint->expected_candidate_hash72,
               HHS_EXACT_HASH72_STRLEN) != 0 ||
        hhs_p219_env_checkpoint_root(checkpoint, checkpoint_root) != HHS_EXACT_STATUS_OK ||
        CRYPTO_memcmp(checkpoint_root, checkpoint->checkpoint_root_sha256,
                      sizeof(checkpoint_root)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    cursor = hhs_p219_pqc_append(auth_material, sizeof(auth_material), cursor,
        HHS_P219_ENV_CHECKPOINT_AUTH_DOMAIN,
        sizeof(HHS_P219_ENV_CHECKPOINT_AUTH_DOMAIN) - 1U);
    cursor = hhs_p219_pqc_append(auth_material, sizeof(auth_material), cursor,
        checkpoint_root, sizeof(checkpoint_root));
    if (cursor == SIZE_MAX || !hhs_p219_env_hmac_sha512(key, auth_material, cursor, expected_auth) ||
        CRYPTO_memcmp(expected_auth, checkpoint->checkpoint_authenticator,
                      sizeof(expected_auth)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    receipt->checkpoint_sequence = checkpoint->checkpoint_sequence;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_vm81_environment_recover_candidate(
    const HHSExactPass219VM81RecoveryCheckpointV1 *checkpoint,
    const HHSExactPass219VM81Hash216RegistryEntryV1 *registry_entries,
    size_t registry_entry_count,
    HHSExactVM81Frame *out_candidate_frame,
    HHSExactPass219VM81EnvironmentReceiptV1 *out_environment_receipt
) {
    uint8_t key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES];
    uint8_t current_root[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
    uint32_t prior_state;
    HHSExactStatus status;
    if (out_candidate_frame == NULL || out_environment_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_candidate_frame, 0, sizeof(*out_candidate_frame));
    hhs_p219_env_zero_receipt(out_environment_receipt, 0U);
    prior_state = atomic_load(&hhs_p219_env_state);
    if (prior_state != HHS_EXACT_PASS219_VM81_ENV_STATE_FROZEN &&
        prior_state != HHS_EXACT_PASS219_VM81_ENV_STATE_RECOVERY_HALTED &&
        atomic_load(&hhs_p219_pqc_halted) == 0U) {
        out_environment_receipt->decision = HHS_EXACT_PASS219_VM81_ENV_DECISION_RECOVERY_REJECTED;
        out_environment_receipt->reason = HHS_EXACT_PASS219_VM81_ENV_REASON_LATCHED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    if (!hhs_p219_pqc_load_key(key) || !hhs_p219_env_ensure_initialized(key)) {
        out_environment_receipt->reason = HHS_EXACT_PASS219_VM81_ENV_REASON_KERNEL_ROOT_UNAVAILABLE;
        atomic_store(&hhs_p219_env_state, HHS_EXACT_PASS219_VM81_ENV_STATE_RECOVERY_HALTED);
        OPENSSL_cleanse(key, sizeof(key));
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    atomic_store(&hhs_p219_env_state, HHS_EXACT_PASS219_VM81_ENV_STATE_RECOVERING);
    status = hhs_p219_env_verify_checkpoint(
        key, checkpoint, registry_entries, registry_entry_count, out_environment_receipt);
    if (status != HHS_EXACT_STATUS_OK) {
        out_environment_receipt->decision = HHS_EXACT_PASS219_VM81_ENV_DECISION_RECOVERY_REJECTED;
        out_environment_receipt->reason = HHS_EXACT_PASS219_VM81_ENV_REASON_CHECKPOINT_AUTHENTICATION;
        atomic_store(&hhs_p219_env_state, HHS_EXACT_PASS219_VM81_ENV_STATE_RECOVERY_HALTED);
        OPENSSL_cleanse(key, sizeof(key));
        return status;
    }
    if (!hhs_p219_env_compute_genesis_root(key, current_root) ||
        CRYPTO_memcmp(current_root, hhs_p219_env_genesis_root, sizeof(current_root)) != 0) {
        out_environment_receipt->decision = HHS_EXACT_PASS219_VM81_ENV_DECISION_RECOVERY_REJECTED;
        out_environment_receipt->reason = HHS_EXACT_PASS219_VM81_ENV_REASON_GENESIS_ROOT_MISMATCH;
        atomic_store(&hhs_p219_env_state, HHS_EXACT_PASS219_VM81_ENV_STATE_RECOVERY_HALTED);
        OPENSSL_cleanse(current_root, sizeof(current_root));
        OPENSSL_cleanse(key, sizeof(key));
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    OPENSSL_cleanse(current_root, sizeof(current_root));
    memcpy(out_candidate_frame, &checkpoint->candidate_frame, sizeof(*out_candidate_frame));
    /* Recovery restores only a candidate and clears latches only after all proofs pass. */
    atomic_store(&hhs_p219_env_anti_rollback_floor, checkpoint->checkpoint_sequence);
    atomic_store(&hhs_p219_pqc_halt_reason, HHS_EXACT_PASS219_VM81_PQC_HALT_NONE);
    atomic_store(&hhs_p219_pqc_halted, 0U);
    atomic_store(&hhs_p219_env_state, HHS_EXACT_PASS219_VM81_ENV_STATE_RUNNING);
    out_environment_receipt->state = HHS_EXACT_PASS219_VM81_ENV_STATE_RUNNING;
    out_environment_receipt->decision = HHS_EXACT_PASS219_VM81_ENV_DECISION_RECOVERED_CANDIDATE;
    out_environment_receipt->reason = HHS_EXACT_PASS219_VM81_ENV_REASON_NONE;
    out_environment_receipt->anti_rollback_floor = checkpoint->checkpoint_sequence;
    out_environment_receipt->genesis_verified = 1U;
    memcpy(out_environment_receipt->genesis_root_sha256,
           hhs_p219_env_genesis_root, HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    OPENSSL_cleanse(key, sizeof(key));
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus hhs_p219_env_gate(
    const uint8_t key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES],
    uint32_t signature_algorithm,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    HHSExactPass219VM81EnvironmentReceiptV1 *receipt
) {
    uint8_t message[1024];
    uint8_t candidate_hash72[HHS_EXACT_HASH72_STRLEN];
    uint8_t witness[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES];
    uint8_t env_signature_message[1100];
    size_t cursor = 0U;
    size_t signature_cursor = 0U;
    uint64_t witness_sequence;
    uint64_t floor;
    HHSExactPass219VM81PQCSignatureReceiptV1 env_signature;
    HHSExactStatus status;

    if (key == NULL || candidate_frame == NULL || parent_hash216_reference == NULL || receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_p219_env_ensure_initialized(key)) {
        receipt->reason = HHS_EXACT_PASS219_VM81_ENV_REASON_KERNEL_ROOT_UNAVAILABLE;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    if (atomic_load(&hhs_p219_env_state) != HHS_EXACT_PASS219_VM81_ENV_STATE_RUNNING) {
        receipt->decision = HHS_EXACT_PASS219_VM81_ENV_DECISION_FROZEN;
        receipt->reason = HHS_EXACT_PASS219_VM81_ENV_REASON_LATCHED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    if (!hhs_p219_env_measurement_matches(key)) {
        atomic_store(&hhs_p219_env_state, HHS_EXACT_PASS219_VM81_ENV_STATE_FROZEN);
        receipt->state = HHS_EXACT_PASS219_VM81_ENV_STATE_FROZEN;
        receipt->decision = HHS_EXACT_PASS219_VM81_ENV_DECISION_FROZEN;
        receipt->reason = HHS_EXACT_PASS219_VM81_ENV_REASON_GENESIS_ROOT_MISMATCH;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    if (hhs_p219_pqc_candidate_hash72(candidate_frame, (char *)candidate_hash72) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    hhs_p219_env_lock_acquire();
    witness_sequence = atomic_load(&hhs_p219_env_witness_sequence) + UINT64_C(1);
    floor = atomic_load(&hhs_p219_env_anti_rollback_floor);
    cursor = hhs_p219_pqc_append(message, sizeof(message), cursor,
        HHS_P219_ENV_WITNESS_DOMAIN, sizeof(HHS_P219_ENV_WITNESS_DOMAIN) - 1U);
    cursor = hhs_p219_pqc_append(message, sizeof(message), cursor,
        hhs_p219_env_genesis_root, HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    cursor = hhs_p219_pqc_append(message, sizeof(message), cursor,
        hhs_p219_env_prior_witness, HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    cursor = hhs_p219_pqc_append_u64_be(message, sizeof(message), cursor, witness_sequence);
    cursor = hhs_p219_pqc_append_u64_be(message, sizeof(message), cursor, floor);
    cursor = hhs_p219_pqc_append(message, sizeof(message), cursor,
        parent_hash216_reference->transition_identity216,
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    cursor = hhs_p219_pqc_append(message, sizeof(message), cursor,
        candidate_hash72, HHS_EXACT_HASH72_LEN);
    if (cursor == SIZE_MAX || !hhs_p219_env_hmac_sha256(key, message, cursor, witness)) {
        hhs_p219_env_lock_release();
        receipt->reason = HHS_EXACT_PASS219_VM81_ENV_REASON_WITNESS_FAILURE;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    signature_cursor = hhs_p219_pqc_append(env_signature_message, sizeof(env_signature_message),
        signature_cursor, message, cursor);
    signature_cursor = hhs_p219_pqc_append(env_signature_message, sizeof(env_signature_message),
        signature_cursor, witness, sizeof(witness));
    memset(&env_signature, 0, sizeof(env_signature));
    hhs_p219_pqc_signature_zero_receipt(&env_signature, signature_algorithm);
    status = signature_cursor == SIZE_MAX
        ? HHS_EXACT_STATUS_INVARIANT_FAILURE
        : hhs_p219_pqc_signature_sign_verify(
            signature_algorithm, key, env_signature_message, signature_cursor, &env_signature);
    if (status != HHS_EXACT_STATUS_OK ||
        env_signature.signature_verified_before_vm81 != 1U) {
        hhs_p219_env_lock_release();
        atomic_store(&hhs_p219_env_state, HHS_EXACT_PASS219_VM81_ENV_STATE_FROZEN);
        receipt->state = HHS_EXACT_PASS219_VM81_ENV_STATE_FROZEN;
        receipt->decision = HHS_EXACT_PASS219_VM81_ENV_DECISION_FROZEN;
        receipt->reason = HHS_EXACT_PASS219_VM81_ENV_REASON_ENVIRONMENT_SIGNATURE;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    memcpy(receipt->genesis_root_sha256, hhs_p219_env_genesis_root,
           HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    memcpy(receipt->prior_witness_sha256, hhs_p219_env_prior_witness,
           HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    memcpy(receipt->witness_sha256, witness,
           HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    memcpy(receipt->environment_signature_sha256, env_signature.signature_sha256,
           HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    memcpy(hhs_p219_env_prior_witness, witness,
           HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    atomic_store(&hhs_p219_env_witness_sequence, witness_sequence);
    hhs_p219_env_lock_release();

    receipt->state = HHS_EXACT_PASS219_VM81_ENV_STATE_RUNNING;
    receipt->decision = HHS_EXACT_PASS219_VM81_ENV_DECISION_READY;
    receipt->reason = HHS_EXACT_PASS219_VM81_ENV_REASON_NONE;
    receipt->witness_sequence = witness_sequence;
    receipt->anti_rollback_floor = floor;
    receipt->genesis_verified = 1U;
    receipt->witness_verified = 1U;
    receipt->environment_signature_verified = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_vm81_environment_admit_signed(
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
) {
    uint8_t key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES];
    HHSExactStatus status;
    if (out_committed_frame == NULL || out_admission == NULL ||
        out_firewall_receipt == NULL || out_signature_receipt == NULL ||
        out_environment_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_committed_frame, 0, sizeof(*out_committed_frame));
    memset(out_admission, 0, sizeof(*out_admission));
    hhs_p219_pqc_zero_receipt(out_firewall_receipt, pass_number);
    hhs_p219_pqc_signature_zero_receipt(out_signature_receipt, signature_algorithm);
    hhs_p219_env_zero_receipt(out_environment_receipt, signature_algorithm);

    if (!hhs_p219_pqc_load_key(key)) {
        out_environment_receipt->reason = HHS_EXACT_PASS219_VM81_ENV_REASON_KERNEL_ROOT_UNAVAILABLE;
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_KEY,
            out_committed_frame, out_firewall_receipt);
    }
    status = hhs_p219_env_gate(
        key, signature_algorithm, candidate_frame,
        parent_hash216_reference, out_environment_receipt);
    OPENSSL_cleanse(key, sizeof(key));
    if (status != HHS_EXACT_STATUS_OK) {
        atomic_store(&hhs_p219_env_state, HHS_EXACT_PASS219_VM81_ENV_STATE_FROZEN);
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_ENVIRONMENT_DIVERGENCE,
            out_committed_frame, out_firewall_receipt);
    }

    status = hhs_exact_pass219_vm81_pqc_admit_signed(
        pass_number, signature_algorithm, input, candidate_frame,
        parent_hash216_reference, lo_shu_group, g243,
        feedback_lane, feedback_trinary,
        out_committed_frame, out_admission,
        out_firewall_receipt, out_signature_receipt);
    if (out_firewall_receipt->decision == HHS_EXACT_PASS219_VM81_PQC_DECISION_HALTED) {
        atomic_store(&hhs_p219_env_state, HHS_EXACT_PASS219_VM81_ENV_STATE_FROZEN);
        out_environment_receipt->state = HHS_EXACT_PASS219_VM81_ENV_STATE_FROZEN;
        out_environment_receipt->decision = HHS_EXACT_PASS219_VM81_ENV_DECISION_FROZEN;
        out_environment_receipt->reason = HHS_EXACT_PASS219_VM81_ENV_REASON_LATCHED;
    }
    return status;
}

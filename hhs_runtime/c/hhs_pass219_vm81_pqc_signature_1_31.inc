#include "../include/hhs_pass219_vm81_pqc_signature_1_31.h"

#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/params.h>
#include <openssl/crypto.h>

#include <limits.h>
#include <string.h>

static const uint8_t HHS_P219_PQC_SIGNATURE_DOMAIN[] =
    "HHS-P219-VM81-PQC-SIGNATURE-V1";
static const uint8_t HHS_P219_PQC_SIGNATURE_SEED_DOMAIN[] =
    "HHS-P219-VM81-PQC-SIGNATURE-SEED-V1";

static void hhs_p219_pqc_signature_zero_receipt(
    HHSExactPass219VM81PQCSignatureReceiptV1 *receipt,
    uint32_t algorithm
) {
    if (receipt == NULL)
        return;
    memset(receipt, 0, sizeof(*receipt));
    receipt->struct_size = (uint32_t)sizeof(*receipt);
    receipt->version = HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERSION;
    receipt->algorithm = algorithm;
    receipt->external_key_authority = 0U;
    receipt->external_signature_authority = 0U;
    receipt->signature_is_canonical_receipt = 0U;
}

static const char *hhs_p219_pqc_signature_algorithm_name(
    uint32_t algorithm,
    size_t *out_seed_length
) {
    if (out_seed_length == NULL)
        return NULL;
    switch (algorithm) {
        case HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65:
            *out_seed_length = 32U;
            return "ML-DSA-65";
        case HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_SLH_DSA_SHA2_192S:
            *out_seed_length = 72U; /* FIPS 205: seed = SK.seed || SK.prf || PK.seed, 3 * n. */
            return "SLH-DSA-SHA2-192s";
        default:
            *out_seed_length = 0U;
            return NULL;
    }
}

uint32_t hhs_exact_pass219_vm81_pqc_signature_version(void) {
    return HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERSION;
}

uint32_t hhs_exact_pass219_vm81_pqc_signature_provider_available(
    uint32_t algorithm
) {
    size_t seed_length = 0U;
    const char *name = hhs_p219_pqc_signature_algorithm_name(algorithm, &seed_length);
    EVP_PKEY_CTX *ctx;
    if (name == NULL || seed_length == 0U)
        return 0U;
    ctx = EVP_PKEY_CTX_new_from_name(NULL, name, NULL);
    if (ctx == NULL)
        return 0U;
    EVP_PKEY_CTX_free(ctx);
    return 1U;
}

static int hhs_p219_pqc_signature_expand_seed(
    const uint8_t root_key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES],
    uint32_t algorithm,
    uint8_t *out_seed,
    size_t seed_length
) {
    uint8_t material[128];
    uint8_t digest[EVP_MAX_MD_SIZE];
    size_t written = 0U;
    uint32_t counter = 1U;

    if (root_key == NULL || out_seed == NULL || seed_length == 0U)
        return 0;
    while (written < seed_length) {
        size_t cursor = 0U;
        unsigned int digest_length = 0U;
        size_t take;
        cursor = hhs_p219_pqc_append(
            material, sizeof(material), cursor,
            HHS_P219_PQC_SIGNATURE_SEED_DOMAIN,
            sizeof(HHS_P219_PQC_SIGNATURE_SEED_DOMAIN) - 1U);
        cursor = hhs_p219_pqc_append_u32_be(
            material, sizeof(material), cursor, algorithm);
        cursor = hhs_p219_pqc_append_u32_be(
            material, sizeof(material), cursor, counter);
        if (cursor == SIZE_MAX ||
            HMAC(EVP_sha512(), root_key, HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES,
                 material, cursor, digest, &digest_length) == NULL ||
            digest_length != 64U) {
            OPENSSL_cleanse(digest, sizeof(digest));
            return 0;
        }
        take = seed_length - written;
        if (take > digest_length)
            take = digest_length;
        memcpy(out_seed + written, digest, take);
        written += take;
        ++counter;
    }
    OPENSSL_cleanse(digest, sizeof(digest));
    return 1;
}

static EVP_PKEY *hhs_p219_pqc_signature_generate_key(
    uint32_t algorithm,
    const uint8_t root_key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES]
) {
    size_t seed_length = 0U;
    const char *name = hhs_p219_pqc_signature_algorithm_name(algorithm, &seed_length);
    uint8_t seed[96];
    EVP_PKEY_CTX *ctx = NULL;
    EVP_PKEY *pkey = NULL;
    OSSL_PARAM params[2];

    if (name == NULL || seed_length == 0U || seed_length > sizeof(seed) ||
        !hhs_p219_pqc_signature_expand_seed(root_key, algorithm, seed, seed_length))
        return NULL;

    ctx = EVP_PKEY_CTX_new_from_name(NULL, name, NULL);
    if (ctx == NULL || EVP_PKEY_keygen_init(ctx) <= 0)
        goto done;
    params[0] = OSSL_PARAM_construct_octet_string("seed", seed, seed_length);
    params[1] = OSSL_PARAM_construct_end();
    if (EVP_PKEY_CTX_set_params(ctx, params) <= 0 ||
        EVP_PKEY_generate(ctx, &pkey) <= 0) {
        EVP_PKEY_free(pkey);
        pkey = NULL;
    }

done:
    OPENSSL_cleanse(seed, sizeof(seed));
    EVP_PKEY_CTX_free(ctx);
    return pkey;
}

static int hhs_p219_pqc_signature_parent_index_root(
    const HHSExactPass219Hash216TransitionViewV1 *parent,
    uint8_t out_sha256[HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_SHA256_BYTES]
) {
    EVP_MD_CTX *ctx = NULL;
    unsigned int length = 0U;
    size_t i;
    int ok = 0;
    if (parent == NULL || out_sha256 == NULL)
        return 0;
    ctx = EVP_MD_CTX_new();
    if (ctx == NULL || EVP_DigestInit_ex(ctx, EVP_sha256(), NULL) != 1)
        goto done;
    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++i) {
        if (EVP_DigestUpdate(
                ctx,
                parent->occurrences[i].sha256_index_record,
                HHS_EXACT_PASS219_HASH216_SHA256_BYTES) != 1)
            goto done;
    }
    if (EVP_DigestFinal_ex(ctx, out_sha256, &length) != 1 ||
        length != HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_SHA256_BYTES)
        goto done;
    ok = 1;

done:
    EVP_MD_CTX_free(ctx);
    return ok;
}

static HHSExactStatus hhs_p219_pqc_signature_build_message(
    uint32_t pass_number,
    uint32_t algorithm,
    uint64_t sequence,
    const HHSExactVM81Frame *candidate,
    const char candidate_hash72[HHS_EXACT_HASH72_STRLEN],
    const char path_hash216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    const HHSExactPass219Hash216TransitionViewV1 *parent,
    const HHSExactPass219Holo4PreparedV1 *prepared,
    const HHSExactPass219Holo4DecisionV1 *decision,
    const uint8_t hmac_tag[HHS_EXACT_PASS219_VM81_PQC_TAG_BYTES],
    uint8_t *out_message,
    size_t capacity,
    size_t *out_length,
    uint8_t out_message_sha256[HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_SHA256_BYTES]
) {
    uint8_t frame_bytes[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t index_root[HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_SHA256_BYTES];
    size_t frame_length = 0U;
    size_t cursor = 0U;
    unsigned int digest_length = 0U;
    HHSExactStatus status;

    if (candidate == NULL || candidate_hash72 == NULL || path_hash216 == NULL ||
        parent == NULL || prepared == NULL || decision == NULL || hmac_tag == NULL ||
        out_message == NULL || out_length == NULL || out_message_sha256 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_vm81_frame_export_le(
        candidate, frame_bytes, sizeof(frame_bytes), &frame_length);
    if (status != HHS_EXACT_STATUS_OK || frame_length != sizeof(frame_bytes) ||
        !hhs_p219_pqc_signature_parent_index_root(parent, index_root))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    cursor = hhs_p219_pqc_append(
        out_message, capacity, cursor,
        HHS_P219_PQC_SIGNATURE_DOMAIN,
        sizeof(HHS_P219_PQC_SIGNATURE_DOMAIN) - 1U);
    cursor = hhs_p219_pqc_append_u32_be(out_message, capacity, cursor, pass_number);
    cursor = hhs_p219_pqc_append_u32_be(out_message, capacity, cursor, algorithm);
    cursor = hhs_p219_pqc_append_u64_be(out_message, capacity, cursor, sequence);
    cursor = hhs_p219_pqc_append(
        out_message, capacity, cursor, candidate_hash72, HHS_EXACT_HASH72_LEN);
    cursor = hhs_p219_pqc_append(
        out_message, capacity, cursor, path_hash216,
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    cursor = hhs_p219_pqc_append(
        out_message, capacity, cursor, parent->transition_identity216,
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    cursor = hhs_p219_pqc_append(
        out_message, capacity, cursor, index_root, sizeof(index_root));
    cursor = hhs_p219_pqc_append(
        out_message, capacity, cursor, frame_bytes, sizeof(frame_bytes));
    cursor = hhs_p219_pqc_append_u64_be(
        out_message, capacity, cursor, prepared->graph_signature64);
    cursor = hhs_p219_pqc_append_u64_be(
        out_message, capacity, cursor, prepared->tensor_signature64);
    cursor = hhs_p219_pqc_append_u64_be(
        out_message, capacity, cursor, decision->decision_signature64);
    cursor = hhs_p219_pqc_append(
        out_message, capacity, cursor, &decision->selected_lane, 1U);
    cursor = hhs_p219_pqc_append(
        out_message, capacity, cursor, hmac_tag,
        HHS_EXACT_PASS219_VM81_PQC_TAG_BYTES);
    if (cursor == SIZE_MAX)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (EVP_Digest(
            out_message, cursor,
            out_message_sha256, &digest_length,
            EVP_sha256(), NULL) != 1 ||
        digest_length != HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_SHA256_BYTES)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    *out_length = cursor;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus hhs_p219_pqc_signature_sign_verify(
    uint32_t algorithm,
    const uint8_t root_key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES],
    const uint8_t *message,
    size_t message_length,
    HHSExactPass219VM81PQCSignatureReceiptV1 *receipt
) {
    size_t seed_length = 0U;
    const char *name = hhs_p219_pqc_signature_algorithm_name(algorithm, &seed_length);
    EVP_PKEY *pkey = NULL;
    EVP_MD_CTX *sign_ctx = NULL;
    EVP_MD_CTX *verify_ctx = NULL;
    uint8_t *signature = NULL;
    uint8_t *pub = NULL;
    size_t signature_length = 0U;
    size_t public_length = 0U;
    unsigned int digest_length = 0U;
    HHSExactStatus status = HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (receipt == NULL || root_key == NULL || message == NULL || message_length == 0U ||
        name == NULL || seed_length == 0U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    if (!hhs_exact_pass219_vm81_pqc_signature_provider_available(algorithm)) {
        receipt->decision = HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_PROVIDER_UNAVAILABLE;
        return HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN;
    }
    receipt->provider_available = 1U;

    pkey = hhs_p219_pqc_signature_generate_key(algorithm, root_key);
    if (pkey == NULL || EVP_PKEY_is_a(pkey, name) != 1) {
        receipt->decision = HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_KEY_DERIVATION_FAILED;
        goto done;
    }
    receipt->key_derived_from_kernel_root = 1U;

    if (EVP_PKEY_get_octet_string_param(pkey, "pub", NULL, 0U, &public_length) != 1 ||
        public_length == 0U)
        goto key_failed;
    pub = OPENSSL_malloc(public_length);
    if (pub == NULL ||
        EVP_PKEY_get_octet_string_param(pkey, "pub", pub, public_length, &public_length) != 1)
        goto key_failed;
    if (EVP_Digest(pub, public_length,
                   receipt->public_key_sha256, &digest_length,
                   EVP_sha256(), NULL) != 1 ||
        digest_length != HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_SHA256_BYTES)
        goto key_failed;

    sign_ctx = EVP_MD_CTX_new();
    if (sign_ctx == NULL ||
        EVP_DigestSignInit_ex(sign_ctx, NULL, NULL, NULL, NULL, pkey, NULL) != 1 ||
        EVP_DigestSign(sign_ctx, NULL, &signature_length, message, message_length) != 1 ||
        signature_length == 0U || signature_length > UINT32_MAX)
        goto sign_failed;
    signature = OPENSSL_malloc(signature_length);
    if (signature == NULL ||
        EVP_DigestSign(sign_ctx, signature, &signature_length, message, message_length) != 1)
        goto sign_failed;
    receipt->signature_generated_inside_kernel = 1U;
    receipt->signature_length = (uint32_t)signature_length;
    if (EVP_Digest(signature, signature_length,
                   receipt->signature_sha256, &digest_length,
                   EVP_sha256(), NULL) != 1 ||
        digest_length != HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_SHA256_BYTES)
        goto sign_failed;

    verify_ctx = EVP_MD_CTX_new();
    if (verify_ctx == NULL ||
        EVP_DigestVerifyInit_ex(verify_ctx, NULL, NULL, NULL, NULL, pkey, NULL) != 1 ||
        EVP_DigestVerify(verify_ctx, signature, signature_length,
                         message, message_length) != 1)
        goto verify_failed;

    receipt->signature_verified_before_vm81 = 1U;
    receipt->decision = HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERIFIED;
    status = HHS_EXACT_STATUS_OK;
    goto done;

key_failed:
    receipt->decision = HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_KEY_DERIVATION_FAILED;
    goto done;
sign_failed:
    receipt->decision = HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_SIGN_FAILED;
    goto done;
verify_failed:
    receipt->decision = HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERIFY_FAILED;

done:
    if (signature != NULL) {
        OPENSSL_cleanse(signature, signature_length);
        OPENSSL_free(signature);
    }
    if (pub != NULL)
        OPENSSL_free(pub);
    EVP_MD_CTX_free(sign_ctx);
    EVP_MD_CTX_free(verify_ctx);
    EVP_PKEY_free(pkey);
    return status;
}

HHSExactStatus hhs_exact_pass219_vm81_pqc_admit_signed(
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
) {
    HHSExactPass219Holo4PreparedV1 prepared;
    HHSExactPass219Holo4DecisionV1 decision;
    HHSExactVM81Frame staged_committed;
    HHSExactPass219RNAAdmissionV1 staged_admission;
    HHSP219PQCIndexContext child_index_context;
    uint8_t key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES];
    uint8_t signature_message[2048];
    size_t signature_message_length = 0U;
    uint64_t sequence;
    HHSExactStatus status;

    if (out_committed_frame == NULL || out_admission == NULL ||
        out_firewall_receipt == NULL || out_signature_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_committed_frame, 0, sizeof(*out_committed_frame));
    memset(out_admission, 0, sizeof(*out_admission));
    hhs_p219_pqc_zero_receipt(out_firewall_receipt, pass_number);
    hhs_p219_pqc_signature_zero_receipt(out_signature_receipt, signature_algorithm);

    if (hhs_p219_pqc_signature_algorithm_name(signature_algorithm, &signature_message_length) == NULL)
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_PQC_SIGNATURE_PROFILE,
            out_committed_frame, out_firewall_receipt);
    signature_message_length = 0U;

    if (atomic_load(&hhs_p219_pqc_halted) != 0U) {
        out_firewall_receipt->halt_reason = atomic_load(&hhs_p219_pqc_halt_reason);
        out_firewall_receipt->decision = HHS_EXACT_PASS219_VM81_PQC_DECISION_HALTED;
        out_firewall_receipt->halted = 1U;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    if (input == NULL || candidate_frame == NULL || parent_hash216_reference == NULL)
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_CELL_WALL_PATH,
            out_committed_frame, out_firewall_receipt);
    if (pass_number < HHS_EXACT_PASS219_VM81_PQC_MIN_PASS)
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_PASS_PATH,
            out_committed_frame, out_firewall_receipt);
    if (!hhs_p219_pqc_load_key(key))
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_KEY,
            out_committed_frame, out_firewall_receipt);
    if (hhs_exact_pass219_vm81_pqc_hash216_reference_verify(parent_hash216_reference) !=
        HHS_EXACT_STATUS_OK) {
        OPENSSL_cleanse(key, sizeof(key));
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_HASH216_REFERENCE,
            out_committed_frame, out_firewall_receipt);
    }

    out_firewall_receipt->parent_hash216_verified = 1U;
    memcpy(out_firewall_receipt->parent_hash216_identity,
           parent_hash216_reference->transition_identity216,
           HHS_EXACT_UQCEL_HASH216_STRLEN);

    if (memcmp(input->previous_hash72,
               parent_hash216_reference->receipt_hash72,
               HHS_EXACT_HASH72_STRLEN) != 0) {
        OPENSSL_cleanse(key, sizeof(key));
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_HASH_LINEAGE,
            out_committed_frame, out_firewall_receipt);
    }

    memset(&prepared, 0, sizeof(prepared));
    memset(&decision, 0, sizeof(decision));
    status = hhs_pass219_vm81_pqc_route_cpp_cell_wall(
        input, candidate_frame, parent_hash216_reference,
        feedback_lane, feedback_trinary, &prepared, &decision);
    if (status != HHS_EXACT_STATUS_OK ||
        !hhs_p219_pqc_route_evidence_valid(&prepared, &decision, parent_hash216_reference)) {
        OPENSSL_cleanse(key, sizeof(key));
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_CELL_WALL_PATH,
            out_committed_frame, out_firewall_receipt);
    }

    sequence = atomic_fetch_add(&hhs_p219_pqc_sequence, UINT64_C(1)) + UINT64_C(1);
    out_firewall_receipt->instruction_sequence = sequence;
    out_firewall_receipt->rna_cell_wall_routed = 1U;
    out_firewall_receipt->graph_signature64 = prepared.graph_signature64;
    out_firewall_receipt->tensor_signature64 = prepared.tensor_signature64;
    out_firewall_receipt->decision_signature64 = decision.decision_signature64;
    out_firewall_receipt->selected_lane = decision.selected_lane;

    status = hhs_p219_pqc_candidate_hash72(
        candidate_frame, out_firewall_receipt->candidate_hash72);
    if (status != HHS_EXACT_STATUS_OK) {
        OPENSSL_cleanse(key, sizeof(key));
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_CANDIDATE_HASH,
            out_committed_frame, out_firewall_receipt);
    }

    status = hhs_p219_pqc_build_path_hash(
        pass_number, sequence,
        out_firewall_receipt->candidate_hash72,
        parent_hash216_reference, &prepared, &decision,
        out_firewall_receipt->cell_wall_path_hash216);
    if (status != HHS_EXACT_STATUS_OK) {
        OPENSSL_cleanse(key, sizeof(key));
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_CELL_WALL_PATH,
            out_committed_frame, out_firewall_receipt);
    }

    status = hhs_p219_pqc_authenticate(
        key, pass_number, sequence, candidate_frame,
        out_firewall_receipt->candidate_hash72,
        out_firewall_receipt->cell_wall_path_hash216,
        parent_hash216_reference, &prepared, &decision,
        out_firewall_receipt->pqc_tag);
    if (status != HHS_EXACT_STATUS_OK) {
        OPENSSL_cleanse(key, sizeof(key));
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_PQC_AUTHENTICATOR,
            out_committed_frame, out_firewall_receipt);
    }
    out_firewall_receipt->pqc_authenticated = 1U;

    status = hhs_p219_pqc_signature_build_message(
        pass_number, signature_algorithm, sequence,
        candidate_frame,
        out_firewall_receipt->candidate_hash72,
        out_firewall_receipt->cell_wall_path_hash216,
        parent_hash216_reference, &prepared, &decision,
        out_firewall_receipt->pqc_tag,
        signature_message, sizeof(signature_message), &signature_message_length,
        out_signature_receipt->signed_message_sha256);
    if (status != HHS_EXACT_STATUS_OK) {
        OPENSSL_cleanse(key, sizeof(key));
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_PQC_SIGNATURE_GENERATION_FAILED,
            out_committed_frame, out_firewall_receipt);
    }

    status = hhs_p219_pqc_signature_sign_verify(
        signature_algorithm, key,
        signature_message, signature_message_length,
        out_signature_receipt);
    OPENSSL_cleanse(key, sizeof(key));
    OPENSSL_cleanse(signature_message, sizeof(signature_message));
    if (status != HHS_EXACT_STATUS_OK) {
        const uint32_t reason =
            out_signature_receipt->decision == HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_PROVIDER_UNAVAILABLE
                ? HHS_EXACT_PASS219_VM81_PQC_HALT_PQC_SIGNATURE_PROVIDER_UNAVAILABLE
                : (out_signature_receipt->decision == HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERIFY_FAILED
                    ? HHS_EXACT_PASS219_VM81_PQC_HALT_PQC_SIGNATURE_VERIFICATION_FAILED
                    : HHS_EXACT_PASS219_VM81_PQC_HALT_PQC_SIGNATURE_GENERATION_FAILED);
        return hhs_p219_pqc_halt_result(reason, out_committed_frame, out_firewall_receipt);
    }

    /* The asymmetric signature is verified before hidden RNA/VM81 authority is invoked. */
    memset(&staged_committed, 0, sizeof(staged_committed));
    memset(&staged_admission, 0, sizeof(staged_admission));
    memset(&child_index_context, 0, sizeof(child_index_context));
    out_firewall_receipt->inherited_rna_authority_invoked = 1U;
    status = hhs_exact_pass219_rna_admit_composed(
        input, candidate_frame, lo_shu_group, g243,
        hhs_p219_pqc_index_resolver, &child_index_context,
        &staged_committed, &staged_admission);
    memcpy(out_admission, &staged_admission, sizeof(staged_admission));

    if (status != HHS_EXACT_STATUS_OK) {
        HHSExactVM81Frame zero_frame;
        memset(&zero_frame, 0, sizeof(zero_frame));
        if (memcmp(&staged_committed, &zero_frame, sizeof(zero_frame)) != 0 ||
            (status != HHS_EXACT_STATUS_CONSTRAINT_REJECTED &&
             status != HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN))
            return hhs_p219_pqc_halt_result(
                HHS_EXACT_PASS219_VM81_PQC_HALT_CHILD_HASH216_INVARIANT,
                out_committed_frame, out_firewall_receipt);
        out_firewall_receipt->decision =
            HHS_EXACT_PASS219_VM81_PQC_DECISION_CANONICAL_REJECTED;
        return status;
    }

    if (child_index_context.expected_position != HHS_EXACT_PASS219_HASH216_OCCURRENCES ||
        hhs_exact_pass219_vm81_pqc_hash216_reference_verify(
            &staged_admission.transition) != HHS_EXACT_STATUS_OK ||
        memcmp(&staged_committed, candidate_frame, sizeof(staged_committed)) != 0)
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_CHILD_HASH216_INVARIANT,
            out_committed_frame, out_firewall_receipt);

    memcpy(out_firewall_receipt->child_hash216_identity,
           staged_admission.transition.transition_identity216,
           HHS_EXACT_UQCEL_HASH216_STRLEN);
    out_firewall_receipt->child_hash216_verified = 1U;
    out_firewall_receipt->decision = HHS_EXACT_PASS219_VM81_PQC_DECISION_COMMITTED;
    memcpy(out_committed_frame, &staged_committed, sizeof(staged_committed));
    return HHS_EXACT_STATUS_OK;
}

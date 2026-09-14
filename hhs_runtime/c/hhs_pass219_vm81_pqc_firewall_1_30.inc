#include "../include/hhs_pass219_vm81_pqc_firewall_1_30.h"
#include "../include/hhs_hash216_bytes.h"

#include <openssl/crypto.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>

#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#define HHS_P219_PQC_INTERNAL
#else
#define HHS_P219_PQC_INTERNAL __attribute__((visibility("hidden")))
#endif

extern HHS_P219_PQC_INTERNAL HHSExactStatus
hhs_pass219_vm81_pqc_route_cpp_cell_wall(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219Holo4PreparedV1 *out_prepared,
    HHSExactPass219Holo4DecisionV1 *out_decision
);

static atomic_uint hhs_p219_pqc_halted = ATOMIC_VAR_INIT(0U);
static atomic_uint hhs_p219_pqc_halt_reason =
    ATOMIC_VAR_INIT(HHS_EXACT_PASS219_VM81_PQC_HALT_NONE);
static atomic_uint_fast64_t hhs_p219_pqc_sequence = ATOMIC_VAR_INIT(UINT64_C(0));

static const uint8_t HHS_P219_PQC_INDEX_DOMAIN[] =
    "HHS-P219-VM81-PQC-HASH216-INDEX-V1";
static const uint8_t HHS_P219_PQC_PATH_DOMAIN[] =
    "HHS-P219-VM81-PQC-CELL-WALL-PATH-V1";
static const uint8_t HHS_P219_PQC_AUTH_DOMAIN[] =
    "HHS-P219-VM81-PQC-INSTRUCTION-AUTH-V1";

typedef struct HHSP219PQCIndexContext {
    uint16_t expected_position;
    uint8_t prior_sha256[HHS_EXACT_PASS219_HASH216_SHA256_BYTES];
} HHSP219PQCIndexContext;

static void hhs_p219_pqc_zero_receipt(
    HHSExactPass219VM81PQCFirewallReceiptV1 *receipt,
    uint32_t pass_number
) {
    if (receipt == NULL)
        return;
    memset(receipt, 0, sizeof(*receipt));
    receipt->struct_size = (uint32_t)sizeof(*receipt);
    receipt->version = HHS_EXACT_PASS219_VM81_PQC_VERSION;
    receipt->pass_number = pass_number;
    receipt->canonical_receipt_owned_by_inherited_authority = 1U;
    receipt->firewall_is_canonical_authority = 0U;
}

static void hhs_p219_pqc_latch(uint32_t reason) {
    uint32_t expected = 0U;
    if (atomic_compare_exchange_strong(&hhs_p219_pqc_halted, &expected, 1U))
        atomic_store(&hhs_p219_pqc_halt_reason, reason);
}

static HHSExactStatus hhs_p219_pqc_halt_result(
    uint32_t reason,
    HHSExactVM81Frame *out_committed_frame,
    HHSExactPass219VM81PQCFirewallReceiptV1 *receipt
) {
    hhs_p219_pqc_latch(reason);
    if (out_committed_frame != NULL)
        memset(out_committed_frame, 0, sizeof(*out_committed_frame));
    if (receipt != NULL) {
        receipt->decision = HHS_EXACT_PASS219_VM81_PQC_DECISION_HALTED;
        receipt->halt_reason = reason;
        receipt->halted = 1U;
    }
    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

static int hhs_p219_pqc_hash72_valid(
    const char value[HHS_EXACT_HASH72_STRLEN]
) {
    size_t i;
    if (value == NULL || value[HHS_EXACT_HASH72_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i) {
        if (strchr(HHS_EXACT_HASH72_ALPHABET, value[i]) == NULL)
            return 0;
    }
    return 1;
}

static int hhs_p219_pqc_hash216_valid(
    const char value[HHS_EXACT_UQCEL_HASH216_STRLEN]
) {
    size_t i;
    if (value == NULL || value[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
        if (strchr(HHS_EXACT_HASH72_ALPHABET, value[i]) == NULL)
            return 0;
    }
    return 1;
}

static size_t hhs_p219_pqc_append(
    uint8_t *out,
    size_t capacity,
    size_t cursor,
    const void *data,
    size_t length
) {
    if (out == NULL || data == NULL || cursor > capacity || length > capacity - cursor)
        return SIZE_MAX;
    if (length != 0U)
        memcpy(out + cursor, data, length);
    return cursor + length;
}

static size_t hhs_p219_pqc_append_u16_be(
    uint8_t *out,
    size_t capacity,
    size_t cursor,
    uint16_t value
) {
    uint8_t bytes[2] = {
        (uint8_t)(value >> 8U),
        (uint8_t)(value & UINT16_C(0xFF))
    };
    return hhs_p219_pqc_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static size_t hhs_p219_pqc_append_u32_be(
    uint8_t *out,
    size_t capacity,
    size_t cursor,
    uint32_t value
) {
    uint8_t bytes[4] = {
        (uint8_t)(value >> 24U),
        (uint8_t)(value >> 16U),
        (uint8_t)(value >> 8U),
        (uint8_t)value
    };
    return hhs_p219_pqc_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static size_t hhs_p219_pqc_append_u64_be(
    uint8_t *out,
    size_t capacity,
    size_t cursor,
    uint64_t value
) {
    uint8_t bytes[8];
    size_t i;
    for (i = 0U; i < 8U; ++i)
        bytes[7U - i] = (uint8_t)(value >> (8U * i));
    return hhs_p219_pqc_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static int hhs_p219_pqc_sha256(
    const uint8_t *material,
    size_t material_length,
    uint8_t out_sha256[HHS_EXACT_PASS219_HASH216_SHA256_BYTES]
) {
    unsigned int digest_length = 0U;
    if (material == NULL || out_sha256 == NULL)
        return 0;
    if (EVP_Digest(
            material,
            material_length,
            out_sha256,
            &digest_length,
            EVP_sha256(),
            NULL) != 1)
        return 0;
    return digest_length == HHS_EXACT_PASS219_HASH216_SHA256_BYTES;
}

static HHSExactStatus hhs_p219_pqc_index_resolver(
    const char transition_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    uint8_t lane_role,
    uint8_t lane_position72,
    uint16_t absolute_position216,
    uint8_t glyph,
    uint8_t out_sha256[HHS_EXACT_PASS219_HASH216_SHA256_BYTES],
    void *context
) {
    HHSP219PQCIndexContext *ctx = (HHSP219PQCIndexContext *)context;
    uint8_t material[512];
    size_t cursor = 0U;

    if (ctx == NULL || transition_identity216 == NULL || out_sha256 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (absolute_position216 != ctx->expected_position ||
        lane_role >= 3U || lane_position72 >= HHS_EXACT_HASH72_LEN ||
        absolute_position216 != (uint16_t)((uint16_t)lane_role * HHS_EXACT_HASH72_LEN +
                                           (uint16_t)lane_position72))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor,
        HHS_P219_PQC_INDEX_DOMAIN, sizeof(HHS_P219_PQC_INDEX_DOMAIN) - 1U);
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor,
        transition_identity216, HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor, &lane_role, sizeof(lane_role));
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor, &lane_position72, sizeof(lane_position72));
    cursor = hhs_p219_pqc_append_u16_be(
        material, sizeof(material), cursor, absolute_position216);
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor, &glyph, sizeof(glyph));
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor,
        ctx->prior_sha256, sizeof(ctx->prior_sha256));
    if (cursor == SIZE_MAX ||
        !hhs_p219_pqc_sha256(material, cursor, out_sha256))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memcpy(ctx->prior_sha256, out_sha256, sizeof(ctx->prior_sha256));
    ctx->expected_position = (uint16_t)(ctx->expected_position + 1U);
    return HHS_EXACT_STATUS_OK;
}

static int hhs_p219_pqc_reference_fields_equal(
    const HHSExactPass219Hash216TransitionViewV1 *left,
    const HHSExactPass219Hash216TransitionViewV1 *right
) {
    size_t i;
    if (left == NULL || right == NULL)
        return 0;
    if (left->struct_size != right->struct_size ||
        left->version != right->version ||
        left->resolved_index_count != right->resolved_index_count ||
        memcmp(left->previous_hash72, right->previous_hash72, HHS_EXACT_HASH72_STRLEN) != 0 ||
        memcmp(left->change_hash72, right->change_hash72, HHS_EXACT_HASH72_STRLEN) != 0 ||
        memcmp(left->receipt_hash72, right->receipt_hash72, HHS_EXACT_HASH72_STRLEN) != 0 ||
        memcmp(left->transition_word216, right->transition_word216,
               HHS_EXACT_UQCEL_HASH216_STRLEN) != 0 ||
        memcmp(left->transition_identity216, right->transition_identity216,
               HHS_EXACT_UQCEL_HASH216_STRLEN) != 0)
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++i) {
        const HHSExactPass219Hash72TokenOccurrenceV1 *a = &left->occurrences[i];
        const HHSExactPass219Hash72TokenOccurrenceV1 *b = &right->occurrences[i];
        if (a->struct_size != b->struct_size || a->version != b->version ||
            a->absolute_position216 != b->absolute_position216 ||
            a->lane_role != b->lane_role ||
            a->lane_position72 != b->lane_position72 ||
            a->glyph != b->glyph ||
            a->sha256_index_present != b->sha256_index_present ||
            CRYPTO_memcmp(a->sha256_index_record, b->sha256_index_record,
                          HHS_EXACT_PASS219_HASH216_SHA256_BYTES) != 0)
            return 0;
    }
    return 1;
}

uint32_t hhs_exact_pass219_vm81_pqc_firewall_version(void) {
    return HHS_EXACT_PASS219_VM81_PQC_VERSION;
}

HHSExactStatus hhs_exact_pass219_vm81_pqc_hash216_reference_init(
    const char previous_hash72[HHS_EXACT_HASH72_STRLEN],
    const char change_hash72[HHS_EXACT_HASH72_STRLEN],
    const char receipt_hash72[HHS_EXACT_HASH72_STRLEN],
    HHSExactPass219Hash216TransitionViewV1 *out_reference
) {
    char triplet[HHS_EXACT_UQCEL_HASH216_STRLEN];
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
    HHSP219PQCIndexContext context;
    HHSExactStatus status;

    if (out_reference == NULL ||
        !hhs_p219_pqc_hash72_valid(previous_hash72) ||
        !hhs_p219_pqc_hash72_valid(change_hash72) ||
        !hhs_p219_pqc_hash72_valid(receipt_hash72))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memcpy(triplet, previous_hash72, HHS_EXACT_HASH72_LEN);
    memcpy(triplet + HHS_EXACT_HASH72_LEN, change_hash72, HHS_EXACT_HASH72_LEN);
    memcpy(triplet + (2U * HHS_EXACT_HASH72_LEN), receipt_hash72, HHS_EXACT_HASH72_LEN);
    triplet[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
    hhs_hash216_compute_bytes(
        triplet, HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN, identity);

    status = hhs_exact_pass219_hash216_transition_init(
        previous_hash72, change_hash72, receipt_hash72, identity, out_reference);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(&context, 0, sizeof(context));
    status = hhs_exact_pass219_hash216_resolve_indexes(
        out_reference, hhs_p219_pqc_index_resolver, &context);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (context.expected_position != HHS_EXACT_PASS219_HASH216_OCCURRENCES)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return hhs_exact_pass219_hash216_indexes_complete(out_reference);
}

HHSExactStatus hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(
    HHSExactPass219Hash216TransitionViewV1 *out_reference
) {
    char zero[HHS_EXACT_HASH72_STRLEN];
    if (out_reference == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(zero, '0', HHS_EXACT_HASH72_LEN);
    zero[HHS_EXACT_HASH72_LEN] = '\0';
    return hhs_exact_pass219_vm81_pqc_hash216_reference_init(
        zero, zero, zero, out_reference);
}

HHSExactStatus hhs_exact_pass219_vm81_pqc_hash216_reference_verify(
    const HHSExactPass219Hash216TransitionViewV1 *reference
) {
    HHSExactPass219Hash216TransitionViewV1 expected;
    HHSExactStatus status;
    if (reference == NULL ||
        reference->struct_size != sizeof(*reference) ||
        reference->version != hhs_exact_pass219_rna_version() ||
        !hhs_p219_pqc_hash72_valid(reference->previous_hash72) ||
        !hhs_p219_pqc_hash72_valid(reference->change_hash72) ||
        !hhs_p219_pqc_hash72_valid(reference->receipt_hash72) ||
        !hhs_p219_pqc_hash216_valid(reference->transition_word216) ||
        !hhs_p219_pqc_hash216_valid(reference->transition_identity216) ||
        hhs_exact_pass219_hash216_indexes_complete(reference) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(&expected, 0, sizeof(expected));
    status = hhs_exact_pass219_vm81_pqc_hash216_reference_init(
        reference->previous_hash72,
        reference->change_hash72,
        reference->receipt_hash72,
        &expected);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return hhs_p219_pqc_reference_fields_equal(reference, &expected)
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

uint32_t hhs_exact_pass219_vm81_pqc_firewall_halted(void) {
    return atomic_load(&hhs_p219_pqc_halted);
}

uint32_t hhs_exact_pass219_vm81_pqc_firewall_halt_reason(void) {
    return atomic_load(&hhs_p219_pqc_halt_reason);
}

static int hhs_p219_pqc_hex_nibble(char value, uint8_t *out) {
    if (out == NULL)
        return 0;
    if (value >= '0' && value <= '9') {
        *out = (uint8_t)(value - '0');
        return 1;
    }
    if (value >= 'a' && value <= 'f') {
        *out = (uint8_t)(10 + value - 'a');
        return 1;
    }
    if (value >= 'A' && value <= 'F') {
        *out = (uint8_t)(10 + value - 'A');
        return 1;
    }
    return 0;
}

static int hhs_p219_pqc_load_key(
    uint8_t out_key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES]
) {
    const char *hex = getenv(HHS_EXACT_PASS219_VM81_PQC_KEY_ENV);
    size_t i;
    uint8_t hi;
    uint8_t lo;
    uint8_t nonzero = 0U;
    if (hex == NULL || strlen(hex) != HHS_EXACT_PASS219_VM81_PQC_KEY_HEX_CHARS)
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES; ++i) {
        if (!hhs_p219_pqc_hex_nibble(hex[2U * i], &hi) ||
            !hhs_p219_pqc_hex_nibble(hex[2U * i + 1U], &lo))
            return 0;
        out_key[i] = (uint8_t)((hi << 4U) | lo);
        nonzero = (uint8_t)(nonzero | out_key[i]);
    }
    return nonzero != 0U;
}

static HHSExactStatus hhs_p219_pqc_candidate_hash72(
    const HHSExactVM81Frame *candidate,
    char out_hash72[HHS_EXACT_HASH72_STRLEN]
) {
    uint8_t bytes[HHS_EXACT_VM81_FRAME_BYTES];
    size_t written = 0U;
    HHSExactStatus status;
    if (candidate == NULL || out_hash72 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_vm81_frame_export_le(
        candidate, bytes, sizeof(bytes), &written);
    if (status != HHS_EXACT_STATUS_OK || written != sizeof(bytes))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    hhs_hash72_compute_bytes(bytes, sizeof(bytes), out_hash72);
    return hhs_p219_pqc_hash72_valid(out_hash72)
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

static int hhs_p219_pqc_route_evidence_valid(
    const HHSExactPass219Holo4PreparedV1 *prepared,
    const HHSExactPass219Holo4DecisionV1 *decision,
    const HHSExactPass219Hash216TransitionViewV1 *parent
) {
    if (prepared == NULL || decision == NULL || parent == NULL)
        return 0;
    return prepared->struct_size == sizeof(*prepared) &&
           prepared->version == HHS_EXACT_PASS219_HOLO4_VERSION &&
           decision->struct_size == sizeof(*decision) &&
           decision->version == HHS_EXACT_PASS219_HOLO4_VERSION &&
           prepared->hash216_positions_complete == 1U &&
           prepared->candidate_only == 1U && prepared->exact_integer_only == 1U &&
           prepared->canonical_mutation_authority == 0U &&
           prepared->canonical_hash72_authority == 0U &&
           prepared->canonical_hash216_authority == 0U &&
           prepared->canonical_persistence_authority == 0U &&
           prepared->floating_point_authority == 0U &&
           decision->candidate_only == 1U && decision->exact_integer_only == 1U &&
           decision->canonical_mutation_authority == 0U &&
           decision->canonical_hash72_authority == 0U &&
           decision->canonical_hash216_authority == 0U &&
           decision->canonical_persistence_authority == 0U &&
           decision->floating_point_authority == 0U &&
           memcmp(prepared->source_transition_identity216,
                  parent->transition_identity216,
                  HHS_EXACT_UQCEL_HASH216_STRLEN) == 0 &&
           memcmp(decision->source_transition_identity216,
                  parent->transition_identity216,
                  HHS_EXACT_UQCEL_HASH216_STRLEN) == 0;
}

static HHSExactStatus hhs_p219_pqc_build_path_hash(
    uint32_t pass_number,
    uint64_t sequence,
    const char candidate_hash72[HHS_EXACT_HASH72_STRLEN],
    const HHSExactPass219Hash216TransitionViewV1 *parent,
    const HHSExactPass219Holo4PreparedV1 *prepared,
    const HHSExactPass219Holo4DecisionV1 *decision,
    char out_hash216[HHS_EXACT_UQCEL_HASH216_STRLEN]
) {
    uint8_t material[1024];
    size_t cursor = 0U;
    if (candidate_hash72 == NULL || parent == NULL || prepared == NULL ||
        decision == NULL || out_hash216 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor,
        HHS_P219_PQC_PATH_DOMAIN, sizeof(HHS_P219_PQC_PATH_DOMAIN) - 1U);
    cursor = hhs_p219_pqc_append_u32_be(material, sizeof(material), cursor, pass_number);
    cursor = hhs_p219_pqc_append_u64_be(material, sizeof(material), cursor, sequence);
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor, candidate_hash72, HHS_EXACT_HASH72_LEN);
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor,
        parent->transition_identity216, HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    cursor = hhs_p219_pqc_append_u64_be(
        material, sizeof(material), cursor, prepared->graph_signature64);
    cursor = hhs_p219_pqc_append_u64_be(
        material, sizeof(material), cursor, prepared->tensor_signature64);
    cursor = hhs_p219_pqc_append_u64_be(
        material, sizeof(material), cursor, decision->decision_signature64);
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor, &decision->selected_lane, 1U);
    if (cursor == SIZE_MAX)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    hhs_hash216_compute_bytes(material, cursor, out_hash216);
    return hhs_p219_pqc_hash216_valid(out_hash216)
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

static HHSExactStatus hhs_p219_pqc_authenticate(
    const uint8_t key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES],
    uint32_t pass_number,
    uint64_t sequence,
    const HHSExactVM81Frame *candidate,
    const char candidate_hash72[HHS_EXACT_HASH72_STRLEN],
    const char path_hash216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    const HHSExactPass219Hash216TransitionViewV1 *parent,
    const HHSExactPass219Holo4PreparedV1 *prepared,
    const HHSExactPass219Holo4DecisionV1 *decision,
    uint8_t out_tag[HHS_EXACT_PASS219_VM81_PQC_TAG_BYTES]
) {
    uint8_t material[16384];
    uint8_t frame_bytes[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t verify_tag[HHS_EXACT_PASS219_VM81_PQC_TAG_BYTES];
    size_t frame_length = 0U;
    size_t cursor = 0U;
    size_t i;
    unsigned int tag_length = 0U;
    unsigned int verify_length = 0U;
    HHSExactStatus status;

    if (key == NULL || candidate == NULL || candidate_hash72 == NULL ||
        path_hash216 == NULL || parent == NULL || prepared == NULL ||
        decision == NULL || out_tag == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_vm81_frame_export_le(
        candidate, frame_bytes, sizeof(frame_bytes), &frame_length);
    if (status != HHS_EXACT_STATUS_OK || frame_length != sizeof(frame_bytes))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor,
        HHS_P219_PQC_AUTH_DOMAIN, sizeof(HHS_P219_PQC_AUTH_DOMAIN) - 1U);
    cursor = hhs_p219_pqc_append_u32_be(material, sizeof(material), cursor, pass_number);
    cursor = hhs_p219_pqc_append_u64_be(material, sizeof(material), cursor, sequence);
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor, candidate_hash72, HHS_EXACT_HASH72_LEN);
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor, path_hash216,
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor, frame_bytes, sizeof(frame_bytes));
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor,
        parent->transition_word216, HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor,
        parent->transition_identity216, HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES && cursor != SIZE_MAX; ++i) {
        cursor = hhs_p219_pqc_append(
            material, sizeof(material), cursor,
            parent->occurrences[i].sha256_index_record,
            HHS_EXACT_PASS219_HASH216_SHA256_BYTES);
    }
    cursor = hhs_p219_pqc_append_u64_be(
        material, sizeof(material), cursor, prepared->graph_signature64);
    cursor = hhs_p219_pqc_append_u64_be(
        material, sizeof(material), cursor, prepared->tensor_signature64);
    cursor = hhs_p219_pqc_append_u64_be(
        material, sizeof(material), cursor, decision->decision_signature64);
    cursor = hhs_p219_pqc_append(
        material, sizeof(material), cursor, &decision->selected_lane, 1U);
    if (cursor == SIZE_MAX)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (HMAC(EVP_sha512(), key, HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES,
             material, cursor, out_tag, &tag_length) == NULL ||
        tag_length != HHS_EXACT_PASS219_VM81_PQC_TAG_BYTES)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (HMAC(EVP_sha512(), key, HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES,
             material, cursor, verify_tag, &verify_length) == NULL ||
        verify_length != HHS_EXACT_PASS219_VM81_PQC_TAG_BYTES ||
        CRYPTO_memcmp(out_tag, verify_tag, HHS_EXACT_PASS219_VM81_PQC_TAG_BYTES) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_vm81_pqc_admit(
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
) {
    HHSExactPass219Holo4PreparedV1 prepared;
    HHSExactPass219Holo4DecisionV1 decision;
    HHSExactVM81Frame staged_committed;
    HHSExactPass219RNAAdmissionV1 staged_admission;
    HHSP219PQCIndexContext child_index_context;
    uint8_t key[HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES];
    uint64_t sequence;
    HHSExactStatus status;

    if (out_committed_frame == NULL || out_admission == NULL ||
        out_firewall_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_committed_frame, 0, sizeof(*out_committed_frame));
    memset(out_admission, 0, sizeof(*out_admission));
    hhs_p219_pqc_zero_receipt(out_firewall_receipt, pass_number);

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
        HHS_EXACT_STATUS_OK)
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_HASH216_REFERENCE,
            out_committed_frame, out_firewall_receipt);

    out_firewall_receipt->parent_hash216_verified = 1U;
    memcpy(out_firewall_receipt->parent_hash216_identity,
           parent_hash216_reference->transition_identity216,
           HHS_EXACT_UQCEL_HASH216_STRLEN);

    if (memcmp(input->previous_hash72,
               parent_hash216_reference->receipt_hash72,
               HHS_EXACT_HASH72_STRLEN) != 0)
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_HASH_LINEAGE,
            out_committed_frame, out_firewall_receipt);

    memset(&prepared, 0, sizeof(prepared));
    memset(&decision, 0, sizeof(decision));
    status = hhs_pass219_vm81_pqc_route_cpp_cell_wall(
        input,
        candidate_frame,
        parent_hash216_reference,
        feedback_lane,
        feedback_trinary,
        &prepared,
        &decision);
    if (status != HHS_EXACT_STATUS_OK ||
        !hhs_p219_pqc_route_evidence_valid(
            &prepared, &decision, parent_hash216_reference))
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_CELL_WALL_PATH,
            out_committed_frame, out_firewall_receipt);

    sequence = atomic_fetch_add(&hhs_p219_pqc_sequence, UINT64_C(1)) + UINT64_C(1);
    out_firewall_receipt->instruction_sequence = sequence;
    out_firewall_receipt->rna_cell_wall_routed = 1U;
    out_firewall_receipt->graph_signature64 = prepared.graph_signature64;
    out_firewall_receipt->tensor_signature64 = prepared.tensor_signature64;
    out_firewall_receipt->decision_signature64 = decision.decision_signature64;
    out_firewall_receipt->selected_lane = decision.selected_lane;

    status = hhs_p219_pqc_candidate_hash72(
        candidate_frame, out_firewall_receipt->candidate_hash72);
    if (status != HHS_EXACT_STATUS_OK)
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_CANDIDATE_HASH,
            out_committed_frame, out_firewall_receipt);

    status = hhs_p219_pqc_build_path_hash(
        pass_number,
        sequence,
        out_firewall_receipt->candidate_hash72,
        parent_hash216_reference,
        &prepared,
        &decision,
        out_firewall_receipt->cell_wall_path_hash216);
    if (status != HHS_EXACT_STATUS_OK)
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_CELL_WALL_PATH,
            out_committed_frame, out_firewall_receipt);

    status = hhs_p219_pqc_authenticate(
        key,
        pass_number,
        sequence,
        candidate_frame,
        out_firewall_receipt->candidate_hash72,
        out_firewall_receipt->cell_wall_path_hash216,
        parent_hash216_reference,
        &prepared,
        &decision,
        out_firewall_receipt->pqc_tag);
    OPENSSL_cleanse(key, sizeof(key));
    if (status != HHS_EXACT_STATUS_OK)
        return hhs_p219_pqc_halt_result(
            HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_PQC_AUTHENTICATOR,
            out_committed_frame, out_firewall_receipt);
    out_firewall_receipt->pqc_authenticated = 1U;

    memset(&staged_committed, 0, sizeof(staged_committed));
    memset(&staged_admission, 0, sizeof(staged_admission));
    memset(&child_index_context, 0, sizeof(child_index_context));
    out_firewall_receipt->inherited_rna_authority_invoked = 1U;
    status = hhs_exact_pass219_rna_admit_composed(
        input,
        candidate_frame,
        lo_shu_group,
        g243,
        hhs_p219_pqc_index_resolver,
        &child_index_context,
        &staged_committed,
        &staged_admission);
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

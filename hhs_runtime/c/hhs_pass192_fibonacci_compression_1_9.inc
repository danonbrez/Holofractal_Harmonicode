#include "../include/hhs_pass192_fibonacci_compression_1_9.h"

#include <string.h>

typedef struct HHSExactFibBig {
    uint8_t bytes[HHS_EXACT_VM81_FRAME_BYTES];
    size_t length;
} HHSExactFibBig;

static uint32_t hhs_exact_pass192_fib_version_word(void) {
    return (HHS_EXACT_PASS192_FIB_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS192_FIB_VERSION_MINOR << 8) |
           HHS_EXACT_PASS192_FIB_VERSION_PATCH;
}

static uint32_t hhs_exact_pass219_composed_version_word(void) {
    return (HHS_EXACT_PASS219_COMPOSED_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_COMPOSED_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_COMPOSED_VERSION_PATCH;
}

static void hhs_exact_fib_set_small(HHSExactFibBig *out, uint8_t value) {
    memset(out, 0, sizeof(*out));
    out->bytes[0] = value;
    out->length = 1U;
}

static int hhs_exact_fib_add(
    const HHSExactFibBig *a,
    const HHSExactFibBig *b,
    HHSExactFibBig *out
) {
    uint8_t reverse[HHS_EXACT_VM81_FRAME_BYTES];
    size_t max_length;
    size_t i;
    uint16_t carry = 0U;

    if (a == NULL || b == NULL || out == NULL)
        return 0;
    max_length = a->length > b->length ? a->length : b->length;
    if (max_length >= HHS_EXACT_VM81_FRAME_BYTES)
        return 0;
    memset(reverse, 0, sizeof(reverse));

    for (i = 0U; i < max_length; ++i) {
        uint16_t av = i < a->length ? a->bytes[a->length - 1U - i] : 0U;
        uint16_t bv = i < b->length ? b->bytes[b->length - 1U - i] : 0U;
        uint16_t sum = (uint16_t)(av + bv + carry);
        reverse[i] = (uint8_t)(sum & UINT16_C(0xFF));
        carry = (uint16_t)(sum >> 8U);
    }
    if (carry != 0U) {
        if (max_length >= HHS_EXACT_VM81_FRAME_BYTES)
            return 0;
        reverse[max_length++] = (uint8_t)carry;
    }

    memset(out, 0, sizeof(*out));
    out->length = max_length;
    for (i = 0U; i < max_length; ++i)
        out->bytes[max_length - 1U - i] = reverse[i];
    return 1;
}

static int hhs_exact_fib_pair(
    uint32_t depth,
    HHSExactFibBig *out_fd,
    HHSExactFibBig *out_fd1
) {
    HHSExactFibBig a;
    HHSExactFibBig b;
    HHSExactFibBig next;
    uint32_t i;

    if (out_fd == NULL || out_fd1 == NULL || depth > HHS_EXACT_PASS192_FIB_MAX_DEPTH)
        return 0;
    hhs_exact_fib_set_small(&a, 1U);
    hhs_exact_fib_set_small(&b, 2U);
    for (i = 0U; i < depth; ++i) {
        if (!hhs_exact_fib_add(&a, &b, &next))
            return 0;
        a = b;
        b = next;
    }
    *out_fd = a;
    *out_fd1 = b;
    return 1;
}

static int hhs_exact_fib_append_big(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    const HHSExactFibBig *value
) {
    if (value == NULL || value->length > UINT16_MAX)
        return 0;
    return hhs_exact_uqcel_append_u16(out, capacity, cursor, (uint16_t)value->length) &&
           hhs_exact_uqcel_append(out, capacity, cursor, value->bytes, value->length);
}

uint32_t hhs_exact_pass192_fibonacci_version(void) {
    return hhs_exact_pass192_fib_version_word();
}

HHSExactStatus hhs_exact_pass192_fibonacci_compress(
    uint32_t depth,
    uint8_t *out_descriptor,
    size_t capacity,
    size_t *out_length,
    HHSExactPass192FibonacciCompressionV1 *out_compression
) {
    static const uint8_t domain[] = "HHS-P192-NESTED-MODULAR-FIBONACCI-COMPRESSION-V1";
    HHSExactFibBig fd;
    HHSExactFibBig fd1;
    size_t cursor = 0U;

    if (out_descriptor == NULL || out_length == NULL || out_compression == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_compression, 0, sizeof(*out_compression));
    out_compression->struct_size = sizeof(*out_compression);
    out_compression->version = hhs_exact_pass192_fib_version_word();
    out_compression->depth = depth;
    out_compression->lo_shu_cell_count = HHS_EXACT_PASS192_FIB_LO_SHU_CELLS;
    out_compression->shared_schedule_count = HHS_EXACT_PASS192_FIB_SHARED_SCHEDULES;
    out_compression->expanded_schedule_count = HHS_EXACT_PASS192_FIB_LO_SHU_CELLS;
    out_compression->outer_modulus = HHS_EXACT_PASS192_FIB_OUTER_MODULUS;

    if (depth > HHS_EXACT_PASS192_FIB_MAX_DEPTH || depth == UINT32_MAX)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (!hhs_exact_fib_pair(depth, &fd, &fd1))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    out_compression->membrane_modulus = depth + 1U;
    out_compression->membrane_residue = depth % (depth + 1U);
    out_compression->compression_applied = 1U;
    out_compression->shared_schedule_deduplicated = 1U;
    out_compression->membrane_preserved =
        (uint8_t)(out_compression->membrane_residue == depth);
    out_compression->outer_modulus_preserved = 1U;

    /*
     * Lossless compressed descriptor.  The seeds plus depth reconstruct every
     * F_n, every F_n/F_(n+1) transition, every cumulative 1/F_n scale, and
     * every local n mod (n+1)=n membrane witness.  F_depth/F_(depth+1) are
     * retained as terminal verification witnesses; the outer hydration modulus
     * is recorded as a namespace identity and is never applied destructively.
     */
    if (!hhs_exact_uqcel_append(out_descriptor, capacity, &cursor, domain, sizeof(domain) - 1U) ||
        !hhs_exact_uqcel_append_u32(out_descriptor, capacity, &cursor, out_compression->version) ||
        !hhs_exact_uqcel_append_u32(out_descriptor, capacity, &cursor, 1U) ||
        !hhs_exact_uqcel_append_u32(out_descriptor, capacity, &cursor, 2U) ||
        !hhs_exact_uqcel_append_u32(out_descriptor, capacity, &cursor, depth) ||
        !hhs_exact_uqcel_append_u32(out_descriptor, capacity, &cursor, HHS_EXACT_PASS192_FIB_LO_SHU_CELLS) ||
        !hhs_exact_uqcel_append_u32(out_descriptor, capacity, &cursor, HHS_EXACT_PASS192_FIB_SHARED_SCHEDULES) ||
        !hhs_exact_uqcel_append_u32(out_descriptor, capacity, &cursor, HHS_EXACT_PASS192_FIB_OUTER_MODULUS) ||
        !hhs_exact_uqcel_append_u32(out_descriptor, capacity, &cursor, depth + 1U) ||
        !hhs_exact_uqcel_append_u32(out_descriptor, capacity, &cursor, depth) ||
        !hhs_exact_fib_append_big(out_descriptor, capacity, &cursor, &fd) ||
        !hhs_exact_fib_append_big(out_descriptor, capacity, &cursor, &fd1)) {
        *out_length = cursor;
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    }

    out_compression->descriptor_length = (uint32_t)cursor;
    *out_length = cursor;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass192_fibonacci_validate_descriptor(
    uint32_t depth,
    const uint8_t *descriptor,
    size_t descriptor_length
) {
    uint8_t expected[HHS_EXACT_PASS192_FIB_MAX_DESCRIPTOR_BYTES];
    size_t expected_length = 0U;
    HHSExactPass192FibonacciCompressionV1 metadata;
    HHSExactStatus status;

    if (descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass192_fibonacci_compress(
        depth, expected, sizeof(expected), &expected_length, &metadata);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (descriptor_length != expected_length || memcmp(descriptor, expected, expected_length) != 0)
        return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
    if (!metadata.compression_applied || !metadata.shared_schedule_deduplicated ||
        !metadata.membrane_preserved || !metadata.outer_modulus_preserved)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_admit_composed(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    HHSExactVM81Frame *out_committed_frame,
    HHSExactPass219ComposedAdmissionV1 *out_admission
) {
    static const uint8_t domain[] = "HHS-P219-UCE-UQCEL-P192-FIBONACCI-COMPOSED-V1";
    HHSExactVM81Frame provisional;
    HHSExactStatus base_status;
    HHSExactStatus fib_status;
    uint8_t descriptor[HHS_EXACT_PASS192_FIB_MAX_DESCRIPTOR_BYTES];
    size_t descriptor_length = 0U;
    uint8_t base_material[HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES];
    size_t base_material_length = 0U;
    uint8_t material[HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES + HHS_EXACT_PASS192_FIB_MAX_DESCRIPTOR_BYTES + 256U];
    size_t material_length = 0U;
    char receipt[HHS_EXACT_HASH72_STRLEN];
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN];

    if (input == NULL || candidate_frame == NULL || out_committed_frame == NULL || out_admission == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_committed_frame, 0, sizeof(*out_committed_frame));
    memset(out_admission, 0, sizeof(*out_admission));
    out_admission->struct_size = sizeof(*out_admission);
    out_admission->version = hhs_exact_pass219_composed_version_word();

    base_status = hhs_exact_vm81_admit_uqcel(
        input, candidate_frame, &provisional, &out_admission->uqcel);
    if (base_status != HHS_EXACT_STATUS_OK ||
        out_admission->uqcel.decision != HHS_EXACT_UQCEL_DECISION_ADMIT) {
        out_admission->uqcel.frame_committed = 0U;
        return base_status;
    }

    fib_status = hhs_exact_pass192_fibonacci_compress(
        HHS_EXACT_PASS219_UCE_FIBONACCI_DEPTH,
        descriptor, sizeof(descriptor), &descriptor_length, &out_admission->fibonacci);
    if (fib_status != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass192_fibonacci_validate_descriptor(
            HHS_EXACT_PASS219_UCE_FIBONACCI_DEPTH, descriptor, descriptor_length) != HHS_EXACT_STATUS_OK) {
        out_admission->uqcel.frame_committed = 0U;
        return fib_status == HHS_EXACT_STATUS_OK ? HHS_EXACT_STATUS_INVARIANT_FAILURE : fib_status;
    }

    if (hhs_exact_uqcel_receipt_material(
            input, &out_admission->uqcel,
            base_material, sizeof(base_material), &base_material_length) != HHS_EXACT_STATUS_OK) {
        out_admission->uqcel.frame_committed = 0U;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (!hhs_exact_uqcel_append(material, sizeof(material), &material_length, domain, sizeof(domain) - 1U) ||
        !hhs_exact_uqcel_append_u32(material, sizeof(material), &material_length, out_admission->version) ||
        !hhs_exact_uqcel_append_u32(material, sizeof(material), &material_length, (uint32_t)base_material_length) ||
        !hhs_exact_uqcel_append(material, sizeof(material), &material_length, base_material, base_material_length) ||
        !hhs_exact_uqcel_append_u32(material, sizeof(material), &material_length, (uint32_t)descriptor_length) ||
        !hhs_exact_uqcel_append(material, sizeof(material), &material_length, descriptor, descriptor_length)) {
        out_admission->uqcel.frame_committed = 0U;
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    }

    hhs_exact_uqcel_hash72_bytes(material, material_length, receipt);
    memcpy(out_admission->final_receipt_hash72, receipt, HHS_EXACT_HASH72_STRLEN);
    memcpy(out_admission->final_hash216_triplet, input->previous_hash72, HHS_EXACT_HASH72_LEN);
    memcpy(out_admission->final_hash216_triplet + HHS_EXACT_HASH72_LEN,
           out_admission->uqcel.change_hash72, HHS_EXACT_HASH72_LEN);
    memcpy(out_admission->final_hash216_triplet + (2U * HHS_EXACT_HASH72_LEN),
           out_admission->final_receipt_hash72, HHS_EXACT_HASH72_LEN);
    out_admission->final_hash216_triplet[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
    hhs_exact_uqcel_hash216_bytes(
        out_admission->final_hash216_triplet,
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN,
        identity);
    memcpy(out_admission->final_hash216_identity, identity, HHS_EXACT_UQCEL_HASH216_STRLEN);

    memcpy(out_committed_frame, &provisional, sizeof(*out_committed_frame));
    out_admission->uqcel.frame_committed = 1U;
    return HHS_EXACT_STATUS_OK;
}

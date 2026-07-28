#include "hhs_p163_vmrc.h"

#include <string.h>

static const char HHS_P163_BASE64[] =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

static int hhs_p163_base64_value(unsigned char c) {
    if (c >= (unsigned char)'A' && c <= (unsigned char)'Z') {
        return (int)(c - (unsigned char)'A');
    }
    if (c >= (unsigned char)'a' && c <= (unsigned char)'z') {
        return 26 + (int)(c - (unsigned char)'a');
    }
    if (c >= (unsigned char)'0' && c <= (unsigned char)'9') {
        return 52 + (int)(c - (unsigned char)'0');
    }
    if (c == (unsigned char)'+') return 62;
    if (c == (unsigned char)'/') return 63;
    return -1;
}

static hhs_p163_vmrc_status hhs_p163_coordinate(
    uint32_t position,
    uint32_t thread,
    size_t *byte_index,
    uint8_t *mask
) {
    uint32_t coordinate;
    uint32_t bit_index;
    if (byte_index == NULL || mask == NULL) {
        return HHS_P163_VMRC_INVALID_ARGUMENT;
    }
    if (
        position >= HHS_P163_VMRC_POSITIONS
        || thread >= HHS_P163_VMRC_THREADS
    ) {
        return HHS_P163_VMRC_OUT_OF_RANGE;
    }
    coordinate = position * HHS_P163_VMRC_THREADS + thread;
    *byte_index = (size_t)(coordinate / UINT32_C(8));
    bit_index = coordinate % UINT32_C(8);
    *mask = (uint8_t)(UINT8_C(1) << (UINT32_C(7) - bit_index));
    return HHS_P163_VMRC_OK;
}

hhs_p163_vmrc_status hhs_p163_vmrc_snapshot_init(
    hhs_p163_vmrc_snapshot *snapshot
) {
    if (snapshot == NULL) return HHS_P163_VMRC_INVALID_ARGUMENT;
    snapshot->abi_version = HHS_P163_VMRC_ABI_VERSION;
    (void)memset(snapshot->bytes, 0, sizeof(snapshot->bytes));
    return HHS_P163_VMRC_OK;
}

hhs_p163_vmrc_status hhs_p163_vmrc_snapshot_get(
    const hhs_p163_vmrc_snapshot *snapshot,
    uint32_t position,
    uint32_t thread,
    uint8_t *value_out
) {
    size_t byte_index;
    uint8_t mask;
    hhs_p163_vmrc_status status;
    if (snapshot == NULL || value_out == NULL) {
        return HHS_P163_VMRC_INVALID_ARGUMENT;
    }
    if (snapshot->abi_version != HHS_P163_VMRC_ABI_VERSION) {
        return HHS_P163_VMRC_INVALID_ARGUMENT;
    }
    status = hhs_p163_coordinate(position, thread, &byte_index, &mask);
    if (status != HHS_P163_VMRC_OK) return status;
    *value_out = (uint8_t)(
        (snapshot->bytes[byte_index] & mask) != UINT8_C(0)
    );
    return HHS_P163_VMRC_OK;
}

hhs_p163_vmrc_status hhs_p163_vmrc_snapshot_authority_set(
    hhs_p163_vmrc_snapshot *snapshot,
    uint32_t position,
    uint32_t thread,
    uint8_t value,
    const void *authority_token,
    const void *expected_authority_token
) {
    size_t byte_index;
    uint8_t mask;
    hhs_p163_vmrc_status status;
    if (
        snapshot == NULL
        || authority_token == NULL
        || expected_authority_token == NULL
    ) {
        return HHS_P163_VMRC_INVALID_ARGUMENT;
    }
    if (authority_token != expected_authority_token) {
        return HHS_P163_VMRC_DIRECT_MUTATION_DENIED;
    }
    if (
        snapshot->abi_version != HHS_P163_VMRC_ABI_VERSION
        || value > UINT8_C(1)
    ) {
        return HHS_P163_VMRC_INVALID_ARGUMENT;
    }
    status = hhs_p163_coordinate(position, thread, &byte_index, &mask);
    if (status != HHS_P163_VMRC_OK) return status;
    if (value == UINT8_C(1)) {
        snapshot->bytes[byte_index] = (uint8_t)(
            snapshot->bytes[byte_index] | mask
        );
    } else {
        snapshot->bytes[byte_index] = (uint8_t)(
            snapshot->bytes[byte_index] & (uint8_t)(~mask)
        );
    }
    return HHS_P163_VMRC_OK;
}

hhs_p163_vmrc_status hhs_p163_vmrc_base64_encode(
    const hhs_p163_vmrc_snapshot *snapshot,
    char *output,
    size_t output_capacity,
    size_t *output_length
) {
    size_t source_index;
    size_t target_index = 0U;
    if (
        snapshot == NULL
        || output == NULL
        || output_length == NULL
    ) {
        return HHS_P163_VMRC_INVALID_ARGUMENT;
    }
    if (snapshot->abi_version != HHS_P163_VMRC_ABI_VERSION) {
        return HHS_P163_VMRC_INVALID_ARGUMENT;
    }
    if (
        output_capacity
        < (size_t)HHS_P163_VMRC_BASE64_SYMBOLS + 1U
    ) {
        return HHS_P163_VMRC_BUFFER_TOO_SMALL;
    }
    for (
        source_index = 0U;
        source_index < (size_t)HHS_P163_VMRC_SNAPSHOT_BYTES;
        source_index += 3U
    ) {
        uint32_t value =
            ((uint32_t)snapshot->bytes[source_index] << 16)
            | ((uint32_t)snapshot->bytes[source_index + 1U] << 8)
            | (uint32_t)snapshot->bytes[source_index + 2U];
        output[target_index++] = HHS_P163_BASE64[
            (value >> 18) & UINT32_C(63)
        ];
        output[target_index++] = HHS_P163_BASE64[
            (value >> 12) & UINT32_C(63)
        ];
        output[target_index++] = HHS_P163_BASE64[
            (value >> 6) & UINT32_C(63)
        ];
        output[target_index++] = HHS_P163_BASE64[
            value & UINT32_C(63)
        ];
    }
    output[target_index] = '\0';
    *output_length = target_index;
    return target_index == (size_t)HHS_P163_VMRC_BASE64_SYMBOLS
        ? HHS_P163_VMRC_OK
        : HHS_P163_VMRC_INVALID_ARGUMENT;
}

hhs_p163_vmrc_status hhs_p163_vmrc_base64_decode(
    const char *input,
    size_t input_length,
    hhs_p163_vmrc_snapshot *snapshot_out
) {
    size_t source_index;
    size_t target_index = 0U;
    char canonical[HHS_P163_VMRC_BASE64_SYMBOLS + 1U];
    size_t canonical_length = 0U;
    if (input == NULL || snapshot_out == NULL) {
        return HHS_P163_VMRC_INVALID_ARGUMENT;
    }
    if (input_length != (size_t)HHS_P163_VMRC_BASE64_SYMBOLS) {
        return HHS_P163_VMRC_MALFORMED_BASE64;
    }
    if (hhs_p163_vmrc_snapshot_init(snapshot_out) != HHS_P163_VMRC_OK) {
        return HHS_P163_VMRC_INVALID_ARGUMENT;
    }
    for (
        source_index = 0U;
        source_index < input_length;
        source_index += 4U
    ) {
        int a = hhs_p163_base64_value(
            (unsigned char)input[source_index]
        );
        int b = hhs_p163_base64_value(
            (unsigned char)input[source_index + 1U]
        );
        int c = hhs_p163_base64_value(
            (unsigned char)input[source_index + 2U]
        );
        int d = hhs_p163_base64_value(
            (unsigned char)input[source_index + 3U]
        );
        uint32_t value;
        if (a < 0 || b < 0 || c < 0 || d < 0) {
            return HHS_P163_VMRC_MALFORMED_BASE64;
        }
        value =
            ((uint32_t)a << 18)
            | ((uint32_t)b << 12)
            | ((uint32_t)c << 6)
            | (uint32_t)d;
        snapshot_out->bytes[target_index++] = (uint8_t)(
            (value >> 16) & UINT32_C(255)
        );
        snapshot_out->bytes[target_index++] = (uint8_t)(
            (value >> 8) & UINT32_C(255)
        );
        snapshot_out->bytes[target_index++] = (uint8_t)(
            value & UINT32_C(255)
        );
    }
    if (target_index != (size_t)HHS_P163_VMRC_SNAPSHOT_BYTES) {
        return HHS_P163_VMRC_MALFORMED_BASE64;
    }
    if (
        hhs_p163_vmrc_base64_encode(
            snapshot_out,
            canonical,
            sizeof(canonical),
            &canonical_length
        ) != HHS_P163_VMRC_OK
    ) {
        return HHS_P163_VMRC_INVALID_ARGUMENT;
    }
    if (
        canonical_length != input_length
        || memcmp(canonical, input, input_length) != 0
    ) {
        return HHS_P163_VMRC_NONCANONICAL_BASE64;
    }
    return HHS_P163_VMRC_OK;
}

#include "hhs_p174_runtime.h"

#include <limits.h>
#include <string.h>

#define ROTR32(value, bits) (((value) >> (bits)) | ((value) << (32U - (bits))))
#define CH(x, y, z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x) (ROTR32((x), 2U) ^ ROTR32((x), 13U) ^ ROTR32((x), 22U))
#define EP1(x) (ROTR32((x), 6U) ^ ROTR32((x), 11U) ^ ROTR32((x), 25U))
#define SIG0(x) (ROTR32((x), 7U) ^ ROTR32((x), 18U) ^ ((x) >> 3U))
#define SIG1(x) (ROTR32((x), 17U) ^ ROTR32((x), 19U) ^ ((x) >> 10U))

typedef struct hhs_p174_sha256_context {
    uint8_t data[64];
    uint32_t data_length;
    uint64_t bit_length;
    uint32_t state[8];
} hhs_p174_sha256_context;

static const uint32_t HHS_P174_SHA256_K[64] = {
    UINT32_C(0x428a2f98), UINT32_C(0x71374491), UINT32_C(0xb5c0fbcf), UINT32_C(0xe9b5dba5),
    UINT32_C(0x3956c25b), UINT32_C(0x59f111f1), UINT32_C(0x923f82a4), UINT32_C(0xab1c5ed5),
    UINT32_C(0xd807aa98), UINT32_C(0x12835b01), UINT32_C(0x243185be), UINT32_C(0x550c7dc3),
    UINT32_C(0x72be5d74), UINT32_C(0x80deb1fe), UINT32_C(0x9bdc06a7), UINT32_C(0xc19bf174),
    UINT32_C(0xe49b69c1), UINT32_C(0xefbe4786), UINT32_C(0x0fc19dc6), UINT32_C(0x240ca1cc),
    UINT32_C(0x2de92c6f), UINT32_C(0x4a7484aa), UINT32_C(0x5cb0a9dc), UINT32_C(0x76f988da),
    UINT32_C(0x983e5152), UINT32_C(0xa831c66d), UINT32_C(0xb00327c8), UINT32_C(0xbf597fc7),
    UINT32_C(0xc6e00bf3), UINT32_C(0xd5a79147), UINT32_C(0x06ca6351), UINT32_C(0x14292967),
    UINT32_C(0x27b70a85), UINT32_C(0x2e1b2138), UINT32_C(0x4d2c6dfc), UINT32_C(0x53380d13),
    UINT32_C(0x650a7354), UINT32_C(0x766a0abb), UINT32_C(0x81c2c92e), UINT32_C(0x92722c85),
    UINT32_C(0xa2bfe8a1), UINT32_C(0xa81a664b), UINT32_C(0xc24b8b70), UINT32_C(0xc76c51a3),
    UINT32_C(0xd192e819), UINT32_C(0xd6990624), UINT32_C(0xf40e3585), UINT32_C(0x106aa070),
    UINT32_C(0x19a4c116), UINT32_C(0x1e376c08), UINT32_C(0x2748774c), UINT32_C(0x34b0bcb5),
    UINT32_C(0x391c0cb3), UINT32_C(0x4ed8aa4a), UINT32_C(0x5b9cca4f), UINT32_C(0x682e6ff3),
    UINT32_C(0x748f82ee), UINT32_C(0x78a5636f), UINT32_C(0x84c87814), UINT32_C(0x8cc70208),
    UINT32_C(0x90befffa), UINT32_C(0xa4506ceb), UINT32_C(0xbef9a3f7), UINT32_C(0xc67178f2)
};

static void hhs_p174_sha256_transform(hhs_p174_sha256_context *context, const uint8_t block[64]) {
    uint32_t words[64];
    uint32_t a;
    uint32_t b;
    uint32_t c;
    uint32_t d;
    uint32_t e;
    uint32_t f;
    uint32_t g;
    uint32_t h;
    uint32_t t1;
    uint32_t t2;
    uint32_t i;

    for (i = 0U; i < 16U; ++i) {
        const uint32_t offset = i * 4U;
        words[i] = ((uint32_t)block[offset] << 24U)
            | ((uint32_t)block[offset + 1U] << 16U)
            | ((uint32_t)block[offset + 2U] << 8U)
            | (uint32_t)block[offset + 3U];
    }
    for (i = 16U; i < 64U; ++i) {
        words[i] = SIG1(words[i - 2U]) + words[i - 7U] + SIG0(words[i - 15U]) + words[i - 16U];
    }

    a = context->state[0];
    b = context->state[1];
    c = context->state[2];
    d = context->state[3];
    e = context->state[4];
    f = context->state[5];
    g = context->state[6];
    h = context->state[7];

    for (i = 0U; i < 64U; ++i) {
        t1 = h + EP1(e) + CH(e, f, g) + HHS_P174_SHA256_K[i] + words[i];
        t2 = EP0(a) + MAJ(a, b, c);
        h = g;
        g = f;
        f = e;
        e = d + t1;
        d = c;
        c = b;
        b = a;
        a = t1 + t2;
    }

    context->state[0] += a;
    context->state[1] += b;
    context->state[2] += c;
    context->state[3] += d;
    context->state[4] += e;
    context->state[5] += f;
    context->state[6] += g;
    context->state[7] += h;
}

static void hhs_p174_sha256_init(hhs_p174_sha256_context *context) {
    context->data_length = 0U;
    context->bit_length = UINT64_C(0);
    context->state[0] = UINT32_C(0x6a09e667);
    context->state[1] = UINT32_C(0xbb67ae85);
    context->state[2] = UINT32_C(0x3c6ef372);
    context->state[3] = UINT32_C(0xa54ff53a);
    context->state[4] = UINT32_C(0x510e527f);
    context->state[5] = UINT32_C(0x9b05688c);
    context->state[6] = UINT32_C(0x1f83d9ab);
    context->state[7] = UINT32_C(0x5be0cd19);
}

static void hhs_p174_sha256_update(hhs_p174_sha256_context *context, const uint8_t *data, size_t length) {
    size_t i;
    for (i = 0U; i < length; ++i) {
        context->data[context->data_length] = data[i];
        ++context->data_length;
        if (context->data_length == 64U) {
            hhs_p174_sha256_transform(context, context->data);
            context->bit_length += UINT64_C(512);
            context->data_length = 0U;
        }
    }
}

static void hhs_p174_sha256_final(hhs_p174_sha256_context *context, uint8_t digest[32]) {
    uint32_t i = context->data_length;
    uint64_t final_bit_length;

    context->data[i++] = UINT8_C(0x80);
    if (i > 56U) {
        while (i < 64U) {
            context->data[i++] = UINT8_C(0);
        }
        hhs_p174_sha256_transform(context, context->data);
        i = 0U;
    }
    while (i < 56U) {
        context->data[i++] = UINT8_C(0);
    }

    final_bit_length = context->bit_length + ((uint64_t)context->data_length * UINT64_C(8));
    context->data[63] = (uint8_t)final_bit_length;
    context->data[62] = (uint8_t)(final_bit_length >> 8U);
    context->data[61] = (uint8_t)(final_bit_length >> 16U);
    context->data[60] = (uint8_t)(final_bit_length >> 24U);
    context->data[59] = (uint8_t)(final_bit_length >> 32U);
    context->data[58] = (uint8_t)(final_bit_length >> 40U);
    context->data[57] = (uint8_t)(final_bit_length >> 48U);
    context->data[56] = (uint8_t)(final_bit_length >> 56U);
    hhs_p174_sha256_transform(context, context->data);

    for (i = 0U; i < 4U; ++i) {
        digest[i] = (uint8_t)(context->state[0] >> (24U - i * 8U));
        digest[i + 4U] = (uint8_t)(context->state[1] >> (24U - i * 8U));
        digest[i + 8U] = (uint8_t)(context->state[2] >> (24U - i * 8U));
        digest[i + 12U] = (uint8_t)(context->state[3] >> (24U - i * 8U));
        digest[i + 16U] = (uint8_t)(context->state[4] >> (24U - i * 8U));
        digest[i + 20U] = (uint8_t)(context->state[5] >> (24U - i * 8U));
        digest[i + 24U] = (uint8_t)(context->state[6] >> (24U - i * 8U));
        digest[i + 28U] = (uint8_t)(context->state[7] >> (24U - i * 8U));
    }
}

static void hhs_p174_sha256_domain(
    const char *domain,
    const uint8_t *first,
    size_t first_length,
    const uint8_t *second,
    size_t second_length,
    const uint8_t *third,
    size_t third_length,
    uint8_t digest[32]
) {
    static const uint8_t separator = UINT8_C(0);
    hhs_p174_sha256_context context;
    hhs_p174_sha256_init(&context);
    hhs_p174_sha256_update(&context, (const uint8_t *)domain, strlen(domain));
    hhs_p174_sha256_update(&context, &separator, 1U);
    if (first != NULL && first_length > 0U) {
        hhs_p174_sha256_update(&context, first, first_length);
    }
    if (second != NULL && second_length > 0U) {
        hhs_p174_sha256_update(&context, second, second_length);
    }
    if (third != NULL && third_length > 0U) {
        hhs_p174_sha256_update(&context, third, third_length);
    }
    hhs_p174_sha256_final(&context, digest);
}

hhs_p174_status hhs_p174_phase_at(
    uint64_t logical_step,
    hhs_p174_phase_coordinate *coordinate_out
) {
    if (coordinate_out == NULL) {
        return HHS_P174_INVALID_ARGUMENT;
    }
    coordinate_out->abi_version = HHS_P174_ABI_VERSION;
    coordinate_out->logical_step = logical_step;
    coordinate_out->phase64 = (uint32_t)(logical_step % HHS_P174_PHASE_64);
    coordinate_out->phase72 = (uint32_t)(logical_step % HHS_P174_PHASE_72);
    coordinate_out->phase81 = (uint32_t)(logical_step % HHS_P174_PHASE_81);
    coordinate_out->phase5184 = (uint32_t)(logical_step % HHS_P174_PHASE_LOCK_PERIOD);
    coordinate_out->lock64_72 = (uint8_t)(logical_step > 0U && (logical_step % UINT64_C(576)) == 0U);
    coordinate_out->lock72_81 = (uint8_t)(logical_step > 0U && (logical_step % UINT64_C(648)) == 0U);
    coordinate_out->full_phase_lock = (uint8_t)(logical_step > 0U && (logical_step % HHS_P174_PHASE_LOCK_PERIOD) == 0U);
    return HHS_P174_OK;
}

hhs_p174_status hhs_p174_build_candidate_frame(
    const hhs_p163_vmrc_snapshot *source,
    const hhs_p174_frame_write *writes,
    size_t write_count,
    const void *authority_token,
    const void *expected_authority_token,
    hhs_p163_vmrc_snapshot *candidate_out
) {
    size_t i;
    size_t j;
    if (source == NULL || candidate_out == NULL || (write_count > 0U && writes == NULL)) {
        return HHS_P174_INVALID_ARGUMENT;
    }
    if (source->abi_version != HHS_P163_VMRC_ABI_VERSION || write_count > HHS_P174_MAX_WRITES) {
        return HHS_P174_OUT_OF_RANGE;
    }
    if (authority_token == NULL || expected_authority_token == NULL || authority_token != expected_authority_token) {
        return HHS_P174_AUTHORITY_DENIED;
    }
    for (i = 0U; i < write_count; ++i) {
        if (writes[i].position >= HHS_P163_VMRC_POSITIONS
            || writes[i].thread >= HHS_P163_VMRC_THREADS
            || writes[i].value > UINT8_C(1)) {
            return HHS_P174_OUT_OF_RANGE;
        }
        for (j = 0U; j < i; ++j) {
            if (writes[i].position == writes[j].position && writes[i].thread == writes[j].thread
                && writes[i].value != writes[j].value) {
                return HHS_P174_OVERLAPPING_WRITE_CONFLICT;
            }
        }
    }
    memcpy(candidate_out, source, sizeof(*candidate_out));
    for (i = 0U; i < write_count; ++i) {
        const hhs_p163_vmrc_status status = hhs_p163_vmrc_snapshot_authority_set(
            candidate_out,
            writes[i].position,
            writes[i].thread,
            writes[i].value,
            authority_token,
            expected_authority_token
        );
        if (status == HHS_P163_VMRC_DIRECT_MUTATION_DENIED) {
            return HHS_P174_AUTHORITY_DENIED;
        }
        if (status != HHS_P163_VMRC_OK) {
            return HHS_P174_OUT_OF_RANGE;
        }
    }
    return HHS_P174_OK;
}

hhs_p174_status hhs_p174_hash216_join(
    const char *predecessor,
    size_t predecessor_length,
    const char *current,
    size_t current_length,
    const char *successor,
    size_t successor_length,
    char *combined_out,
    size_t combined_capacity
) {
    if (predecessor == NULL || current == NULL || successor == NULL || combined_out == NULL) {
        return HHS_P174_INVALID_ARGUMENT;
    }
    if (predecessor_length != HHS_P174_HASH72_CHARACTERS
        || current_length != HHS_P174_HASH72_CHARACTERS
        || successor_length != HHS_P174_HASH72_CHARACTERS) {
        return HHS_P174_HASH216_LENGTH_MISMATCH;
    }
    if (combined_capacity < HHS_P174_HASH216_CHARACTERS) {
        return HHS_P174_BUFFER_TOO_SMALL;
    }
    memcpy(combined_out, predecessor, HHS_P174_HASH72_CHARACTERS);
    memcpy(combined_out + HHS_P174_HASH72_CHARACTERS, current, HHS_P174_HASH72_CHARACTERS);
    memcpy(combined_out + HHS_P174_HASH72_CHARACTERS * 2U, successor, HHS_P174_HASH72_CHARACTERS);
    return HHS_P174_OK;
}

hhs_p174_status hhs_p174_hash216_indexes(
    const char *combined,
    size_t combined_length,
    const uint8_t logical_identity[HHS_P174_SHA256_BYTES],
    uint8_t indexes_out[HHS_P174_HASH216_CHARACTERS][HHS_P174_SHA256_BYTES],
    uint8_t index_root_out[HHS_P174_SHA256_BYTES]
) {
    uint8_t prior[HHS_P174_SHA256_BYTES] = {0};
    uint8_t position_bytes[4];
    uint32_t position;
    hhs_p174_sha256_context root_context;
    static const char character_domain[] = "HHS-P174-HASH216-CHARACTER-V1";
    static const char root_domain[] = "HHS-P174-HASH216-INDEX-ROOT-V1";
    static const uint8_t separator = UINT8_C(0);

    if (combined == NULL || logical_identity == NULL || indexes_out == NULL || index_root_out == NULL) {
        return HHS_P174_INVALID_ARGUMENT;
    }
    if (combined_length != HHS_P174_HASH216_CHARACTERS) {
        return HHS_P174_HASH216_LENGTH_MISMATCH;
    }
    for (position = 0U; position < HHS_P174_HASH216_CHARACTERS; ++position) {
        hhs_p174_sha256_context context;
        position_bytes[0] = (uint8_t)(position >> 24U);
        position_bytes[1] = (uint8_t)(position >> 16U);
        position_bytes[2] = (uint8_t)(position >> 8U);
        position_bytes[3] = (uint8_t)position;
        hhs_p174_sha256_init(&context);
        hhs_p174_sha256_update(&context, (const uint8_t *)character_domain, strlen(character_domain));
        hhs_p174_sha256_update(&context, &separator, 1U);
        hhs_p174_sha256_update(&context, logical_identity, HHS_P174_SHA256_BYTES);
        hhs_p174_sha256_update(&context, prior, HHS_P174_SHA256_BYTES);
        hhs_p174_sha256_update(&context, position_bytes, sizeof(position_bytes));
        hhs_p174_sha256_update(&context, (const uint8_t *)&combined[position], 1U);
        hhs_p174_sha256_final(&context, indexes_out[position]);
        memcpy(prior, indexes_out[position], HHS_P174_SHA256_BYTES);
    }
    hhs_p174_sha256_init(&root_context);
    hhs_p174_sha256_update(&root_context, (const uint8_t *)root_domain, strlen(root_domain));
    hhs_p174_sha256_update(&root_context, &separator, 1U);
    hhs_p174_sha256_update(
        &root_context,
        (const uint8_t *)indexes_out,
        HHS_P174_HASH216_CHARACTERS * HHS_P174_SHA256_BYTES
    );
    hhs_p174_sha256_final(&root_context, index_root_out);
    return HHS_P174_OK;
}

hhs_p174_status hhs_p174_select_execution_path(
    uint64_t direct_cost_units,
    uint64_t retrieval_cost_units,
    hhs_p174_execution_path *path_out,
    int64_t *retrieval_advantage_out
) {
    uint64_t magnitude;
    if (path_out == NULL || retrieval_advantage_out == NULL) {
        return HHS_P174_INVALID_ARGUMENT;
    }
    if (direct_cost_units > retrieval_cost_units) {
        magnitude = direct_cost_units - retrieval_cost_units;
        if (magnitude > (uint64_t)INT64_MAX) {
            return HHS_P174_OUT_OF_RANGE;
        }
        *path_out = HHS_P174_EXECUTE_RETRIEVAL;
        *retrieval_advantage_out = (int64_t)magnitude;
    } else if (direct_cost_units < retrieval_cost_units) {
        magnitude = retrieval_cost_units - direct_cost_units;
        if (magnitude > (uint64_t)INT64_MAX) {
            return HHS_P174_OUT_OF_RANGE;
        }
        *path_out = HHS_P174_EXECUTE_DIRECT;
        *retrieval_advantage_out = -(int64_t)magnitude;
    } else {
        *path_out = HHS_P174_EXECUTE_EQUAL_COST_DIRECT;
        *retrieval_advantage_out = INT64_C(0);
    }
    return HHS_P174_OK;
}

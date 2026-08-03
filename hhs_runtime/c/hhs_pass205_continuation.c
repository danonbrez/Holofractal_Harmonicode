#include "hhs_pass205_continuation.h"

#include <string.h>

#define HHS_PASS205_TOKEN_BUFFER_SIZE \
    (7u * HHS_HASH216_LEN + HHS_HASH72_LEN + 8u)

static uint64_t rotl64(uint64_t value, unsigned shift) {
    shift &= 63u;
    if (shift == 0u) {
        return value;
    }
    return (value << shift) | (value >> (64u - shift));
}

static uint64_t rotr64(uint64_t value, unsigned shift) {
    shift &= 63u;
    if (shift == 0u) {
        return value;
    }
    return (value >> shift) | (value << (64u - shift));
}

static uint32_t fold32(uint64_t value) {
    value ^= value >> 33;
    value *= 0xff51afd7ed558ccdULL;
    value ^= value >> 33;
    value *= 0xc4ceb9fe1a85ec53ULL;
    value ^= value >> 33;
    return (uint32_t)(value ^ (value >> 32));
}

static uint32_t projection_word(
    const HHSPass205State* state,
    uint32_t channel,
    uint32_t cell
) {
    const uint32_t left = (cell + HHS_PASS205_CELL_COUNT - 1u) % HHS_PASS205_CELL_COUNT;
    const uint32_t right = (cell + 1u) % HHS_PASS205_CELL_COUNT;
    const uint32_t vertical = (cell + 9u) % HHS_PASS205_CELL_COUNT;
    uint64_t mixed = state->cells[cell];
    mixed ^= rotl64(state->cells[left], (channel + 1u) & 63u);
    mixed ^= rotr64(state->cells[right], (channel * 3u + 5u) & 63u);
    mixed ^= rotl64(state->cells[vertical], (channel * 5u + 7u) & 63u);
    mixed ^= ((uint64_t)(channel + 1u) * 0x9E3779B97F4A7C15ULL);
    mixed ^= ((uint64_t)(cell + 1u) * 0x517cc1b727220a95ULL);
    return fold32(mixed);
}

static void write_u16_le(uint8_t* out, uint16_t value) {
    out[0] = (uint8_t)(value & 0xffu);
    out[1] = (uint8_t)((value >> 8) & 0xffu);
}

static void write_u32_le(uint8_t* out, uint32_t value) {
    for (uint32_t i = 0u; i < 4u; ++i) {
        out[i] = (uint8_t)((value >> (8u * i)) & 0xffu);
    }
}

static void write_u64_le(uint8_t* out, uint64_t value) {
    for (uint32_t i = 0u; i < 8u; ++i) {
        out[i] = (uint8_t)((value >> (8u * i)) & 0xffu);
    }
}

uint32_t hhs_pass205_q_address(uint16_t s, uint8_t g, uint8_t* ok) {
    const uint8_t valid = (uint8_t)(s < HHS_PASS205_STATE_BITS && g < HHS_PASS205_CONTROL_COUNT);
    if (ok != NULL) {
        *ok = valid;
    }
    if (!valid) {
        return UINT32_MAX;
    }
    return ((uint32_t)s * HHS_PASS205_CONTROL_COUNT) + (uint32_t)g;
}

uint8_t hhs_pass205_q_decode(uint32_t q, uint16_t* out_s, uint8_t* out_g) {
    if (q >= HHS_PASS205_Q_COUNT || out_s == NULL || out_g == NULL) {
        return 0u;
    }
    *out_s = (uint16_t)(q / HHS_PASS205_CONTROL_COUNT);
    *out_g = (uint8_t)(q % HHS_PASS205_CONTROL_COUNT);
    return 1u;
}

void hhs_pass205_state_clear(HHSPass205State* state) {
    if (state != NULL) {
        memset(state, 0, sizeof(*state));
    }
}

void hhs_pass205_projection_clear(HHSPass205Projection* projection) {
    if (projection != NULL) {
        memset(projection, 0, sizeof(*projection));
    }
}

void hhs_pass205_frontier_clear(HHSPass205Frontier* frontier) {
    if (frontier != NULL) {
        memset(frontier, 0, sizeof(*frontier));
    }
}

uint8_t hhs_pass205_validate_delta(const HHSPass205Delta* delta) {
    uint8_t seen[HHS_PASS205_CELL_COUNT];
    if (delta == NULL || delta->count > HHS_PASS205_CELL_COUNT) {
        return 0u;
    }
    memset(seen, 0, sizeof(seen));
    for (uint16_t i = 0u; i < delta->count; ++i) {
        const uint8_t cell = delta->cell_index[i];
        if (cell >= HHS_PASS205_CELL_COUNT || delta->control_g[i] >= HHS_PASS205_CONTROL_COUNT) {
            return 0u;
        }
        if (delta->xor_mask[i] == 0u || seen[cell] != 0u) {
            return 0u;
        }
        seen[cell] = 1u;
    }
    return 1u;
}

uint8_t hhs_pass205_apply_delta(
    const HHSPass205State* parent,
    const HHSPass205Delta* delta,
    HHSPass205State* child
) {
    if (parent == NULL || child == NULL || !hhs_pass205_validate_delta(delta)) {
        return 0u;
    }
    memcpy(child, parent, sizeof(*child));
    for (uint16_t i = 0u; i < delta->count; ++i) {
        child->cells[delta->cell_index[i]] ^= delta->xor_mask[i];
    }
    return 1u;
}

uint8_t hhs_pass205_build_required_frontier(
    const HHSPass205Delta* delta,
    HHSPass205Frontier* frontier
) {
    if (frontier == NULL || !hhs_pass205_validate_delta(delta)) {
        return 0u;
    }
    hhs_pass205_frontier_clear(frontier);
    for (uint16_t i = 0u; i < delta->count; ++i) {
        const uint32_t changed = delta->cell_index[i];
        const uint32_t affected[4] = {
            changed,
            (changed + 1u) % HHS_PASS205_CELL_COUNT,
            (changed + HHS_PASS205_CELL_COUNT - 1u) % HHS_PASS205_CELL_COUNT,
            (changed + HHS_PASS205_CELL_COUNT - 9u) % HHS_PASS205_CELL_COUNT,
        };
        for (uint32_t j = 0u; j < 4u; ++j) {
            frontier->cell[affected[j]] = 1u;
        }
    }
    return 1u;
}

uint8_t hhs_pass205_validate_frontier(
    const HHSPass205Delta* delta,
    const HHSPass205Frontier* frontier
) {
    HHSPass205Frontier required;
    if (frontier == NULL || !hhs_pass205_build_required_frontier(delta, &required)) {
        return 0u;
    }
    for (uint32_t i = 0u; i < HHS_PASS205_CELL_COUNT; ++i) {
        if (required.cell[i] != 0u && frontier->cell[i] == 0u) {
            return 0u;
        }
        if (frontier->cell[i] > 1u) {
            return 0u;
        }
    }
    return 1u;
}

void hhs_pass205_project_full(
    const HHSPass205State* state,
    HHSPass205Projection* projection
) {
    if (state == NULL || projection == NULL) {
        return;
    }
    for (uint32_t channel = 0u; channel < HHS_PASS205_PROJECTION_CHANNELS; ++channel) {
        for (uint32_t cell = 0u; cell < HHS_PASS205_CELL_COUNT; ++cell) {
            projection->channel[channel][cell] = projection_word(state, channel, cell);
        }
    }
}

uint8_t hhs_pass205_project_sparse(
    const HHSPass205State* child,
    const HHSPass205Projection* parent_projection,
    const HHSPass205Frontier* frontier,
    HHSPass205Projection* child_projection
) {
    if (child == NULL || parent_projection == NULL || frontier == NULL || child_projection == NULL) {
        return 0u;
    }
    memcpy(child_projection, parent_projection, sizeof(*child_projection));
    for (uint32_t cell = 0u; cell < HHS_PASS205_CELL_COUNT; ++cell) {
        if (frontier->cell[cell] == 0u) {
            continue;
        }
        if (frontier->cell[cell] != 1u) {
            return 0u;
        }
        for (uint32_t channel = 0u; channel < HHS_PASS205_PROJECTION_CHANNELS; ++channel) {
            child_projection->channel[channel][cell] = projection_word(child, channel, cell);
        }
    }
    return 1u;
}

uint8_t hhs_pass205_projection_equal(
    const HHSPass205Projection* a,
    const HHSPass205Projection* b
) {
    if (a == NULL || b == NULL) {
        return 0u;
    }
    return (uint8_t)(memcmp(a, b, sizeof(*a)) == 0);
}

void hhs_pass205_state_hash216(const HHSPass205State* state, HHSHash216* out_hash) {
    uint8_t buffer[HHS_PASS205_CELL_COUNT * 8u];
    if (state == NULL || out_hash == NULL) {
        return;
    }
    for (uint32_t i = 0u; i < HHS_PASS205_CELL_COUNT; ++i) {
        write_u64_le(&buffer[i * 8u], state->cells[i]);
    }
    hhs_hash216_compute(buffer, sizeof(buffer), out_hash);
}

void hhs_pass205_delta_hash216(const HHSPass205Delta* delta, HHSHash216* out_hash) {
    uint8_t buffer[2u + HHS_PASS205_CELL_COUNT * 10u];
    size_t offset = 0u;
    if (out_hash == NULL || !hhs_pass205_validate_delta(delta)) {
        return;
    }
    memset(buffer, 0, sizeof(buffer));
    write_u16_le(buffer, delta->count);
    offset = 2u;
    for (uint16_t i = 0u; i < delta->count; ++i) {
        buffer[offset++] = delta->cell_index[i];
        buffer[offset++] = delta->control_g[i];
        write_u64_le(&buffer[offset], delta->xor_mask[i]);
        offset += 8u;
    }
    hhs_hash216_compute(buffer, offset, out_hash);
}

void hhs_pass205_hydration_hash216(const HHSPass205Delta* delta, HHSHash216* out_hash) {
    uint8_t buffer[2u + HHS_PASS205_STATE_BITS * 4u];
    size_t offset = 2u;
    uint16_t q_count = 0u;
    if (out_hash == NULL || !hhs_pass205_validate_delta(delta)) {
        return;
    }
    memset(buffer, 0, sizeof(buffer));
    for (uint16_t i = 0u; i < delta->count; ++i) {
        for (uint32_t bit = 0u; bit < HHS_PASS205_BITS_PER_CELL; ++bit) {
            if ((delta->xor_mask[i] & (1ULL << bit)) == 0u) {
                continue;
            }
            const uint32_t s = ((uint32_t)delta->cell_index[i] * HHS_PASS205_BITS_PER_CELL) + bit;
            uint8_t ok = 0u;
            const uint32_t q = hhs_pass205_q_address((uint16_t)s, delta->control_g[i], &ok);
            if (!ok || q_count >= HHS_PASS205_STATE_BITS) {
                return;
            }
            write_u32_le(&buffer[offset], q);
            offset += 4u;
            q_count += 1u;
        }
    }
    write_u16_le(buffer, q_count);
    hhs_hash216_compute(buffer, offset, out_hash);
}

void hhs_pass205_frontier_hash216(const HHSPass205Frontier* frontier, HHSHash216* out_hash) {
    if (frontier == NULL || out_hash == NULL) {
        return;
    }
    hhs_hash216_compute(frontier->cell, HHS_PASS205_CELL_COUNT, out_hash);
}

void hhs_pass205_projection_hash216(
    const HHSPass205Projection* projection,
    HHSHash216* out_hash
) {
    uint8_t buffer[HHS_PASS205_PROJECTION_CHANNELS * HHS_PASS205_CELL_COUNT * 4u];
    size_t offset = 0u;
    if (projection == NULL || out_hash == NULL) {
        return;
    }
    for (uint32_t channel = 0u; channel < HHS_PASS205_PROJECTION_CHANNELS; ++channel) {
        for (uint32_t cell = 0u; cell < HHS_PASS205_CELL_COUNT; ++cell) {
            write_u32_le(&buffer[offset], projection->channel[channel][cell]);
            offset += 4u;
        }
    }
    hhs_hash216_compute(buffer, sizeof(buffer), out_hash);
}

void hhs_pass205_hash216_bytes(const uint8_t* data, size_t size, HHSHash216* out_hash) {
    if (out_hash == NULL || (data == NULL && size != 0u)) {
        return;
    }
    hhs_hash216_compute(data, size, out_hash);
}

uint8_t hhs_pass205_build_token(
    const HHSHash216* parent_root,
    const HHSHash216* content_root,
    const HHSHash216* delta_root,
    const HHSHash216* hydration_root,
    const HHSHash216* dependency_root,
    const HHSHash216* projection_root,
    const HHSHash216* learning_root,
    const HHSHash72* parent_receipt,
    uint64_t generation,
    HHSPass205Token* out_token
) {
    uint8_t buffer[HHS_PASS205_TOKEN_BUFFER_SIZE];
    size_t offset = 0u;
    if (parent_root == NULL || content_root == NULL || delta_root == NULL || hydration_root == NULL
        || dependency_root == NULL || projection_root == NULL || learning_root == NULL
        || parent_receipt == NULL || out_token == NULL) {
        return 0u;
    }
    memset(out_token, 0, sizeof(*out_token));
    out_token->parent_root = *parent_root;
    out_token->content_root = *content_root;
    out_token->delta_root = *delta_root;
    out_token->hydration_root = *hydration_root;
    out_token->dependency_root = *dependency_root;
    out_token->projection_root = *projection_root;
    out_token->learning_root = *learning_root;
    out_token->parent_receipt = *parent_receipt;
    out_token->generation = generation;

    const HHSHash216* roots[7] = {
        parent_root,
        content_root,
        delta_root,
        hydration_root,
        dependency_root,
        projection_root,
        learning_root,
    };
    for (uint32_t i = 0u; i < 7u; ++i) {
        memcpy(&buffer[offset], roots[i]->value, HHS_HASH216_LEN);
        offset += HHS_HASH216_LEN;
    }
    memcpy(&buffer[offset], parent_receipt->value, HHS_HASH72_LEN);
    offset += HHS_HASH72_LEN;
    write_u64_le(&buffer[offset], generation);
    offset += 8u;
    hhs_hash216_compute(buffer, offset, &out_token->continuation_root);
    hhs_hash72_compute(buffer, offset, &out_token->receipt);
    return 1u;
}

size_t hhs_pass205_sizeof_state(void) { return sizeof(HHSPass205State); }
size_t hhs_pass205_sizeof_delta(void) { return sizeof(HHSPass205Delta); }
size_t hhs_pass205_sizeof_frontier(void) { return sizeof(HHSPass205Frontier); }
size_t hhs_pass205_sizeof_projection(void) { return sizeof(HHSPass205Projection); }
size_t hhs_pass205_sizeof_token(void) { return sizeof(HHSPass205Token); }

#include "hhs_pass207_gpu_driver.h"

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t rotl64(uint64_t value, uint32_t shift) {
    shift &= 63u;
    return shift == 0u ? value : ((value << shift) | (value >> (64u - shift)));
}

static uint64_t rotr64(uint64_t value, uint32_t shift) {
    shift &= 63u;
    return shift == 0u ? value : ((value >> shift) | (value << (64u - shift)));
}

static uint32_t fold32(uint64_t value) {
    value ^= value >> 33;
    value *= UINT64_C(0xff51afd7ed558ccd);
    value ^= value >> 33;
    value *= UINT64_C(0xc4ceb9fe1a85ec53);
    value ^= value >> 33;
    return (uint32_t)(value ^ (value >> 32));
}

static uint32_t projection_word(const uint64_t* state, uint32_t batch_size, uint32_t batch, uint32_t channel, uint32_t cell) {
    uint32_t left = (cell + 80u) % 81u;
    uint32_t right = (cell + 1u) % 81u;
    uint32_t vertical = (cell + 9u) % 81u;
    uint64_t mixed = state[(size_t)cell * batch_size + batch];
    mixed ^= rotl64(state[(size_t)left * batch_size + batch], (channel + 1u) & 63u);
    mixed ^= rotr64(state[(size_t)right * batch_size + batch], (channel * 3u + 5u) & 63u);
    mixed ^= rotl64(state[(size_t)vertical * batch_size + batch], (channel * 5u + 7u) & 63u);
    mixed ^= ((uint64_t)(channel + 1u) * UINT64_C(0x9E3779B97F4A7C15));
    mixed ^= ((uint64_t)(cell + 1u) * UINT64_C(0x517cc1b727220a95));
    return fold32(mixed);
}

int main(void) {
    enum { BATCH = 2 };
    size_t state_count = 81u * BATCH;
    size_t projection_count = 32u * 81u * BATCH;
    uint64_t* state = calloc(state_count, sizeof(*state));
    uint32_t* projection = calloc(projection_count, sizeof(*projection));
    uint64_t* child = calloc(state_count, sizeof(*child));
    uint32_t* child_projection = calloc(projection_count, sizeof(*child_projection));
    uint8_t* frontier = calloc(state_count, sizeof(*frontier));
    uint8_t hydration_valid[BATCH] = {0u, 0u};
    uint32_t delta_offsets[3] = {0u, 1u, 2u};
    uint32_t delta_cells[2] = {0u, 80u};
    uint8_t delta_controls[2] = {7u, 242u};
    uint64_t delta_masks[2] = {UINT64_C(1), UINT64_C(1) << 63u};
    uint32_t hydration_offsets[3] = {0u, 1u, 2u};
    uint32_t hydration_q[2] = {7u, ((80u * 64u + 63u) * 243u) + 242u};
    uint8_t input_key[32];
    uint8_t output_key[32];
    HHSPass207GPUConfig config = hhs_pass207_gpu_default_config();
    HHSPass207GPUDriver* driver = NULL;
    HHSPass207Batch batch;
    HHSPass207BatchOutput output;
    HHSPass207GPUStatus status;
    HHSPass207Status rc;
    uint32_t i;

    assert(state != NULL && projection != NULL && child != NULL && child_projection != NULL && frontier != NULL);
    {
        uint8_t seen[HHS_PASS207_LOGICAL_LANES];
        uint32_t lane;
        memset(seen, 0, sizeof(seen));
        for (lane = 0u; lane < HHS_PASS207_LOGICAL_LANES; ++lane) {
            uint8_t cell = 0u;
            uint8_t hyperthread = 0u;
            uint8_t row = 0u;
            uint8_t column = 0u;
            uint8_t ok = 0u;
            uint16_t encoded;
            assert(hhs_pass207_lane_decode((uint16_t)lane, &cell, &hyperthread) == 1u);
            encoded = hhs_pass207_lane_address(cell, hyperthread, &ok);
            assert(ok == 1u && encoded == lane && seen[encoded] == 0u);
            seen[encoded] = 1u;
            assert(hhs_pass207_lane_phase_coordinate((uint16_t)lane, &row, &column) == 1u);
            assert((uint32_t)row * HHS_PASS207_PHASE_DIMENSION + column == lane);
        }
        assert(hhs_pass207_lane_decode(HHS_PASS207_LOGICAL_LANES, NULL, NULL) == 0u);
    }
    memset(input_key, 0x11, sizeof(input_key));
    memset(output_key, 0x22, sizeof(output_key));
    config.requested_backend = HHS_PASS207_BACKEND_CPU_REFERENCE;
    config.cache_capacity_bytes = 16u * 1024u * 1024u;
    config.cache_capacity_entries = 32u;
    rc = hhs_pass207_gpu_create(&config, &driver);
    assert(rc == HHS_PASS207_OK && driver != NULL);

    for (i = 0u; i < state_count; ++i) {
        state[i] = UINT64_C(0x100000000) + i;
    }
    for (i = 0u; i < 32u; ++i) {
        uint32_t cell;
        for (cell = 0u; cell < 81u; ++cell) {
            uint32_t b;
            for (b = 0u; b < BATCH; ++b) {
                projection[((size_t)i * 81u + cell) * BATCH + b] = projection_word(state, BATCH, b, i, cell);
            }
        }
    }

    memset(&batch, 0, sizeof(batch));
    batch.batch_size = BATCH;
    batch.state_soa = state;
    batch.projection_soa = projection;
    batch.delta_offsets = delta_offsets;
    batch.delta_cells = delta_cells;
    batch.delta_controls = delta_controls;
    batch.delta_xor_masks = delta_masks;
    batch.hydration_offsets = hydration_offsets;
    batch.hydration_q = hydration_q;
    batch.delta_count = 2u;
    batch.hydration_count = 2u;
    batch.input_cache_key = input_key;
    batch.output_cache_key = output_key;
    batch.reuse_cached_inputs = 1u;
    batch.retain_outputs = 1u;

    output.child_state_soa = child;
    output.child_projection_soa = child_projection;
    output.frontier_soa = frontier;
    output.hydration_valid = hydration_valid;

    rc = hhs_pass207_gpu_dispatch(driver, &batch, &output);
    assert(rc == HHS_PASS207_OK);
    assert(child[0u * BATCH + 0u] == (state[0u * BATCH + 0u] ^ UINT64_C(1)));
    assert(child[80u * BATCH + 1u] == (state[80u * BATCH + 1u] ^ (UINT64_C(1) << 63u)));
    assert(frontier[0u * BATCH + 0u] == 1u);
    assert(frontier[1u * BATCH + 0u] == 1u);
    assert(frontier[72u * BATCH + 0u] == 1u);
    assert(frontier[80u * BATCH + 0u] == 1u);
    assert(hydration_valid[0] == 1u && hydration_valid[1] == 1u);
    assert(child_projection[(0u * 81u + 0u) * BATCH + 0u] == projection_word(child, BATCH, 0u, 0u, 0u));

    memset(state, 0, state_count * sizeof(*state));
    memset(projection, 0, projection_count * sizeof(*projection));
    memset(child, 0, state_count * sizeof(*child));
    memset(child_projection, 0, projection_count * sizeof(*child_projection));
    memset(frontier, 0, state_count * sizeof(*frontier));
    rc = hhs_pass207_gpu_dispatch(driver, &batch, &output);
    assert(rc == HHS_PASS207_OK);
    assert(child[0u * BATCH + 0u] != UINT64_C(1));
    assert(hhs_pass207_gpu_get_status(driver, &status) == HHS_PASS207_OK);
    assert(status.cache_input_hit == 1u);
    assert(status.cache_hits >= 2u);
    assert(status.logical_hyperthreads_per_cell == 64u);
    assert(status.logical_lanes_per_batch == 5184u);
    assert(status.physical_workgroup_size == 64u);
    assert(status.stable_lane_identity == 1u);
    assert(status.disjoint_lane_writes == 1u);
    assert(status.canonical_reduction_order == 1u);

    {
        uint8_t query[72];
        uint8_t candidates[3u * 72u];
        uint32_t distances[3];
        uint8_t matrix_key[32];
        memset(matrix_key, 0x33, sizeof(matrix_key));
        for (i = 0u; i < 72u; ++i) {
            query[i] = (uint8_t)i;
            candidates[i] = (uint8_t)i;
            candidates[72u + i] = (uint8_t)((i + 1u) % 72u);
            candidates[144u + i] = (uint8_t)((i + 36u) % 72u);
        }
        rc = hhs_pass207_gpu_vector_distance72(driver, query, candidates, 3u, matrix_key, 1u, distances);
        assert(rc == HHS_PASS207_OK);
        assert(distances[0] == 0u);
        assert(distances[1] == 72u);
        assert(distances[2] == 72u * 36u);
        memset(candidates, 0, sizeof(candidates));
        rc = hhs_pass207_gpu_vector_distance72(driver, query, NULL, 3u, matrix_key, 1u, distances);
        assert(rc == HHS_PASS207_OK && distances[0] == 0u);
    }

    hydration_q[0] += 1u;
    rc = hhs_pass207_gpu_dispatch(driver, &batch, &output);
    assert(rc == HHS_PASS207_ERR_HYDRATION_MISMATCH);

    hhs_pass207_gpu_destroy(driver);
    free(frontier);
    free(child_projection);
    free(child);
    free(projection);
    free(state);
    puts("pass207_gpu_driver: PASS");
    return 0;
}

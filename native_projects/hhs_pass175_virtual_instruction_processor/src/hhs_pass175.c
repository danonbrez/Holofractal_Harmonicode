#include "hhs_pass175.h"

static const uint8_t HHS175_PHASE_TABLE[HHS175_OPERATIONS_PER_CELL] = {
    0,0,36,0,54,0,54,18,36,36,18,18,36,54,54,54,
    54,54,36,36,54,36,18,54,54,0,36,0,18,36,36,0,
    54,0,0,0,54,36,18,18,0,18,54,36,18,18,0,18,
    0,36,36,54,18,18,54,36,36,18,18,0,36,54,18,36
};

static uint64_t hhs175_mix64(uint64_t value) {
    value ^= value >> 30;
    value *= UINT64_C(0xbf58476d1ce4e5b9);
    value ^= value >> 27;
    value *= UINT64_C(0x94d049bb133111eb);
    value ^= value >> 31;
    return value;
}

int hhs175_address_encode(uint32_t cell, uint32_t operation, uint32_t *state_out) {
    if (state_out == NULL || cell >= HHS175_VM81_CELLS || operation >= HHS175_OPERATIONS_PER_CELL) return -1;
    *state_out = cell * HHS175_OPERATIONS_PER_CELL + operation;
    return 0;
}

int hhs175_address_decode(uint32_t state, HHS175Address *address_out) {
    if (address_out == NULL || state >= HHS175_INSTRUCTION_COUNT) return -1;
    address_out->state = state;
    address_out->cell = (uint16_t)(state / HHS175_OPERATIONS_PER_CELL);
    address_out->operation = (uint8_t)(state % HHS175_OPERATIONS_PER_CELL);
    address_out->phase = HHS175_PHASE_TABLE[address_out->operation];
    return 0;
}

int hhs175_projected_encode(uint32_t state, uint32_t control, uint32_t *projected_out) {
    if (projected_out == NULL || state >= HHS175_INSTRUCTION_COUNT || control >= HHS175_CONTROL_COUNT) return -1;
    *projected_out = state * HHS175_CONTROL_COUNT + control;
    return 0;
}

int hhs175_projected_decode(uint32_t projected, uint32_t *state_out, uint32_t *control_out) {
    if (state_out == NULL || control_out == NULL || projected >= HHS175_PROJECTED_COUNT) return -1;
    *state_out = projected / HHS175_CONTROL_COUNT;
    *control_out = projected % HHS175_CONTROL_COUNT;
    return 0;
}

int hhs175_control_encode(const uint8_t trits[HHS175_CONTROL_TRITS], uint16_t *control_out) {
    uint32_t value = 0;
    size_t index;
    if (trits == NULL || control_out == NULL) return -1;
    for (index = 0; index < HHS175_CONTROL_TRITS; ++index) {
        if (trits[index] > 2u) return -1;
        value = value * 3u + trits[index];
    }
    *control_out = (uint16_t)value;
    return 0;
}

int hhs175_control_decode(uint32_t control, uint8_t trits_out[HHS175_CONTROL_TRITS]) {
    int index;
    if (trits_out == NULL || control >= HHS175_CONTROL_COUNT) return -1;
    for (index = (int)HHS175_CONTROL_TRITS - 1; index >= 0; --index) {
        trits_out[index] = (uint8_t)(control % 3u);
        control /= 3u;
    }
    return 0;
}

uint8_t hhs175_phase_for_operation(uint32_t operation) {
    return operation < HHS175_OPERATIONS_PER_CELL ? HHS175_PHASE_TABLE[operation] : UINT8_MAX;
}

int hhs175_candidate_conflict(const uint8_t left_read[HHS175_VM81_CELLS],
                              const uint8_t left_write[HHS175_VM81_CELLS],
                              const uint8_t right_read[HHS175_VM81_CELLS],
                              const uint8_t right_write[HHS175_VM81_CELLS]) {
    size_t index;
    if (left_read == NULL || left_write == NULL || right_read == NULL || right_write == NULL) return -1;
    for (index = 0; index < HHS175_VM81_CELLS; ++index) {
        if ((left_write[index] && right_write[index]) ||
            (left_write[index] && right_read[index]) ||
            (right_write[index] && left_read[index])) return 1;
    }
    return 0;
}

uint64_t hhs175_candidate_identity(uint64_t epoch, uint32_t sequence, uint32_t thread_id,
                                   uint32_t state, uint32_t control, uint32_t write_cell,
                                   int32_t write_value) {
    uint64_t packed = epoch;
    packed ^= ((uint64_t)sequence << 48);
    packed ^= ((uint64_t)thread_id << 40);
    packed ^= ((uint64_t)state << 24);
    packed ^= ((uint64_t)control << 16);
    packed ^= ((uint64_t)write_cell << 8);
    packed ^= (uint8_t)(write_value + 1);
    return hhs175_mix64(packed ^ UINT64_C(0x1755184243));
}

int hhs175_candidate_build(uint64_t epoch, uint32_t sequence, uint32_t thread_id,
                           uint32_t state, uint32_t control, uint32_t write_cell,
                           int32_t write_value, HHS175Candidate *candidate_out) {
    HHS175Address address;
    if (candidate_out == NULL || thread_id >= 64u || write_cell >= HHS175_VM81_CELLS || write_value < -1 || write_value > 1) return -1;
    if (control >= HHS175_CONTROL_COUNT || hhs175_address_decode(state, &address) != 0) return -1;
    candidate_out->epoch = epoch;
    candidate_out->sequence = sequence;
    candidate_out->thread_id = (uint16_t)thread_id;
    candidate_out->reserved = 0;
    candidate_out->state = state;
    candidate_out->control = (uint16_t)control;
    candidate_out->write_cell = (uint16_t)write_cell;
    candidate_out->write_value = (int8_t)write_value;
    candidate_out->phase = address.phase;
    candidate_out->reserved2 = 0;
    candidate_out->identity = hhs175_candidate_identity(epoch, sequence, thread_id, state, control, write_cell, write_value);
    return 0;
}

uint64_t hhs175_singular_commit_root(uint64_t prior_root,
                                     const HHS175Candidate *candidates,
                                     size_t candidate_count) {
    uint64_t root = hhs175_mix64(prior_root ^ UINT64_C(0x484153483732));
    size_t index;
    if (candidates == NULL && candidate_count != 0u) return 0;
    for (index = 0; index < candidate_count; ++index) {
        root = hhs175_mix64(root ^ candidates[index].identity ^ ((uint64_t)index << 32));
    }
    return root;
}

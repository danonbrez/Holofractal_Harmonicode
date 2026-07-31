#include "vm81_invariant_kernel.h"

#include <string.h>

static const uint8_t HHS175_PHASE_TABLE[HHS175_KERNEL_OPERATIONS_PER_CELL] = {
    0,0,36,0,54,0,54,18,36,36,18,18,36,54,54,54,
    54,54,36,36,54,36,18,54,54,0,36,0,18,36,36,0,
    54,0,0,0,54,36,18,18,0,18,54,36,18,18,0,18,
    0,36,36,54,18,18,54,36,36,18,18,0,36,54,18,36
};

static const uint8_t HHS175_SCALAR_LO[8] = {0,1,0,1,10,11,1,0};
static const uint8_t HHS175_SCALAR_HI[8] = {1,0,11,10,1,0,0,111};

static uint64_t hhs175_mix64(uint64_t value) {
    value ^= value >> 30;
    value *= UINT64_C(0xbf58476d1ce4e5b9);
    value ^= value >> 27;
    value *= UINT64_C(0x94d049bb133111eb);
    value ^= value >> 31;
    return value;
}

static uint64_t hhs175_candidate_identity(const HHS175KernelCandidateInput *input) {
    uint64_t value = input->epoch;
    value = hhs175_mix64(value ^ ((uint64_t)input->sequence << 32));
    value = hhs175_mix64(value ^ ((uint64_t)input->thread_id << 48));
    value = hhs175_mix64(value ^ ((uint64_t)input->state << 16));
    value = hhs175_mix64(value ^ ((uint64_t)input->control << 8));
    value = hhs175_mix64(value ^ ((uint64_t)input->write_cell << 1));
    value = hhs175_mix64(value ^ (uint8_t)(input->write_value + 1));
    value = hhs175_mix64(value ^ input->instruction_identity);
    value = hhs175_mix64(value ^ input->read_set.words[0] ^ input->read_set.words[1]);
    value = hhs175_mix64(value ^ input->write_set.words[0] ^ input->write_set.words[1]);
    return value;
}

uint32_t hhs175_kernel_abi_version(void) {
    return HHS175_KERNEL_ABI_VERSION;
}

const uint8_t *hhs175_kernel_scalar_lo(size_t *length_out) {
    if (length_out != NULL) *length_out = sizeof(HHS175_SCALAR_LO);
    return HHS175_SCALAR_LO;
}

const uint8_t *hhs175_kernel_scalar_hi(size_t *length_out) {
    if (length_out != NULL) *length_out = sizeof(HHS175_SCALAR_HI);
    return HHS175_SCALAR_HI;
}

int hhs175_kernel_address_encode(uint32_t cell, uint32_t operation, uint32_t *state_out) {
    if (state_out == NULL) return HHS175_KERNEL_INVALID_ARGUMENT;
    if (cell >= HHS175_KERNEL_VM81_CELLS || operation >= HHS175_KERNEL_OPERATIONS_PER_CELL) {
        return HHS175_KERNEL_ADDRESS_RANGE;
    }
    *state_out = cell * HHS175_KERNEL_OPERATIONS_PER_CELL + operation;
    return HHS175_KERNEL_OK;
}

int hhs175_kernel_address_decode(uint32_t state, HHS175KernelAddress *address_out) {
    if (address_out == NULL) return HHS175_KERNEL_INVALID_ARGUMENT;
    if (state >= HHS175_KERNEL_STATE_COUNT) return HHS175_KERNEL_ADDRESS_RANGE;
    address_out->state = state;
    address_out->cell = (uint16_t)(state / HHS175_KERNEL_OPERATIONS_PER_CELL);
    address_out->operation = (uint8_t)(state % HHS175_KERNEL_OPERATIONS_PER_CELL);
    address_out->phase = HHS175_PHASE_TABLE[address_out->operation];
    return HHS175_KERNEL_OK;
}

int hhs175_kernel_projected_encode(uint32_t state, uint32_t control, uint32_t *projected_out) {
    if (projected_out == NULL) return HHS175_KERNEL_INVALID_ARGUMENT;
    if (state >= HHS175_KERNEL_STATE_COUNT) return HHS175_KERNEL_ADDRESS_RANGE;
    if (control >= HHS175_KERNEL_CONTROL_COUNT) return HHS175_KERNEL_CONTROL_RANGE;
    *projected_out = state * HHS175_KERNEL_CONTROL_COUNT + control;
    return HHS175_KERNEL_OK;
}

int hhs175_kernel_projected_decode(uint32_t projected, uint32_t *state_out, uint32_t *control_out) {
    if (state_out == NULL || control_out == NULL) return HHS175_KERNEL_INVALID_ARGUMENT;
    if (projected >= HHS175_KERNEL_STATE_COUNT * HHS175_KERNEL_CONTROL_COUNT) {
        return HHS175_KERNEL_ADDRESS_RANGE;
    }
    *state_out = projected / HHS175_KERNEL_CONTROL_COUNT;
    *control_out = projected % HHS175_KERNEL_CONTROL_COUNT;
    return HHS175_KERNEL_OK;
}

int hhs175_kernel_control_encode(const uint8_t trits[HHS175_KERNEL_CONTROL_TRITS], uint16_t *control_out) {
    uint32_t value = 0;
    size_t index;
    if (trits == NULL || control_out == NULL) return HHS175_KERNEL_INVALID_ARGUMENT;
    for (index = 0; index < HHS175_KERNEL_CONTROL_TRITS; ++index) {
        if (trits[index] > 2u) return HHS175_KERNEL_CONTROL_RANGE;
        value = value * 3u + trits[index];
    }
    *control_out = (uint16_t)value;
    return HHS175_KERNEL_OK;
}

int hhs175_kernel_control_decode(uint32_t control, uint8_t trits_out[HHS175_KERNEL_CONTROL_TRITS]) {
    int index;
    if (trits_out == NULL) return HHS175_KERNEL_INVALID_ARGUMENT;
    if (control >= HHS175_KERNEL_CONTROL_COUNT) return HHS175_KERNEL_CONTROL_RANGE;
    for (index = (int)HHS175_KERNEL_CONTROL_TRITS - 1; index >= 0; --index) {
        trits_out[index] = (uint8_t)(control % 3u);
        control /= 3u;
    }
    return HHS175_KERNEL_OK;
}

void hhs175_kernel_bitset_clear(HHS175KernelBitset *set) {
    if (set != NULL) {
        set->words[0] = 0;
        set->words[1] = 0;
    }
}

int hhs175_kernel_bitset_add(HHS175KernelBitset *set, uint32_t cell) {
    if (set == NULL) return HHS175_KERNEL_INVALID_ARGUMENT;
    if (cell >= HHS175_KERNEL_VM81_CELLS) return HHS175_KERNEL_ADDRESS_RANGE;
    set->words[cell / 64u] |= UINT64_C(1) << (cell % 64u);
    return HHS175_KERNEL_OK;
}

int hhs175_kernel_bitset_intersects(const HHS175KernelBitset *left, const HHS175KernelBitset *right) {
    if (left == NULL || right == NULL) return HHS175_KERNEL_INVALID_ARGUMENT;
    return ((left->words[0] & right->words[0]) != 0u ||
            (left->words[1] & right->words[1]) != 0u) ? 1 : 0;
}

int hhs175_kernel_candidate_conflict(
    const HHS175KernelCandidateInput *left,
    const HHS175KernelCandidateInput *right
) {
    int result;
    if (left == NULL || right == NULL) return HHS175_KERNEL_INVALID_ARGUMENT;
    result = hhs175_kernel_bitset_intersects(&left->write_set, &right->write_set);
    if (result != 0) return result;
    result = hhs175_kernel_bitset_intersects(&left->write_set, &right->read_set);
    if (result != 0) return result;
    return hhs175_kernel_bitset_intersects(&right->write_set, &left->read_set);
}

int hhs175_kernel_prepare_candidates(
    const HHS175KernelCandidateInput *inputs,
    size_t input_count,
    HHS175KernelCandidate *candidates_out
) {
    size_t index;
    if ((inputs == NULL && input_count != 0u) || candidates_out == NULL) {
        return HHS175_KERNEL_INVALID_ARGUMENT;
    }
    if (input_count > HHS175_KERNEL_MAX_BATCH) return HHS175_KERNEL_INVALID_ARGUMENT;
    for (index = 0; index < input_count; ++index) {
        HHS175KernelAddress address;
        uint32_t projected;
        if (inputs[index].thread_id >= 64u ||
            inputs[index].write_cell >= HHS175_KERNEL_VM81_CELLS ||
            inputs[index].write_value < -1 ||
            inputs[index].write_value > 1) {
            return HHS175_KERNEL_INVALID_ARGUMENT;
        }
        if (hhs175_kernel_address_decode(inputs[index].state, &address) != HHS175_KERNEL_OK) {
            return HHS175_KERNEL_ADDRESS_RANGE;
        }
        if (hhs175_kernel_projected_encode(
                inputs[index].state, inputs[index].control, &projected
            ) != HHS175_KERNEL_OK) {
            return HHS175_KERNEL_CONTROL_RANGE;
        }
        candidates_out[index].input = inputs[index];
        candidates_out[index].projected_address = projected;
        candidates_out[index].phase = address.phase;
        candidates_out[index].reserved = 0;
        if (hhs175_kernel_control_decode(
                inputs[index].control, candidates_out[index].control_trits
            ) != HHS175_KERNEL_OK) {
            return HHS175_KERNEL_CONTROL_RANGE;
        }
        candidates_out[index].candidate_identity = hhs175_candidate_identity(&inputs[index]);
    }
    return HHS175_KERNEL_OK;
}

static int hhs175_candidate_compare(
    const HHS175KernelCandidate *left,
    const HHS175KernelCandidate *right
) {
    if (left->input.epoch != right->input.epoch) {
        return left->input.epoch < right->input.epoch ? -1 : 1;
    }
    if (left->input.sequence != right->input.sequence) {
        return left->input.sequence < right->input.sequence ? -1 : 1;
    }
    if (left->input.thread_id != right->input.thread_id) {
        return left->input.thread_id < right->input.thread_id ? -1 : 1;
    }
    if (left->input.state != right->input.state) {
        return left->input.state < right->input.state ? -1 : 1;
    }
    if (left->input.control != right->input.control) {
        return left->input.control < right->input.control ? -1 : 1;
    }
    if (left->candidate_identity != right->candidate_identity) {
        return left->candidate_identity < right->candidate_identity ? -1 : 1;
    }
    return 0;
}

int hhs175_kernel_sort_candidates(
    HHS175KernelCandidate *candidates,
    size_t candidate_count
) {
    size_t index;
    if (candidates == NULL && candidate_count != 0u) return HHS175_KERNEL_INVALID_ARGUMENT;
    if (candidate_count > HHS175_KERNEL_MAX_BATCH) return HHS175_KERNEL_INVALID_ARGUMENT;
    for (index = 1; index < candidate_count; ++index) {
        HHS175KernelCandidate item = candidates[index];
        size_t position = index;
        while (position > 0u && hhs175_candidate_compare(&item, &candidates[position - 1u]) < 0) {
            candidates[position] = candidates[position - 1u];
            --position;
        }
        candidates[position] = item;
    }
    return HHS175_KERNEL_OK;
}

void hhs175_kernel_state_reset(HHS175KernelState *state) {
    if (state != NULL) memset(state, 0, sizeof(*state));
}

int hhs175_kernel_commit_candidates(
    const HHS175KernelCandidate *ordered_candidates,
    size_t candidate_count,
    HHS175KernelState *canonical_state,
    HHS175VM81AdmitFn vm81_admit,
    void *vm81_context,
    uint64_t *hash72_receipt_token_out
) {
    size_t left;
    HHS175KernelState successor;
    uint64_t receipt = 0;
    int admission;
    if ((ordered_candidates == NULL && candidate_count != 0u) ||
        canonical_state == NULL ||
        vm81_admit == NULL ||
        hash72_receipt_token_out == NULL) {
        return HHS175_KERNEL_INVALID_ARGUMENT;
    }
    if (candidate_count > HHS175_KERNEL_MAX_BATCH) return HHS175_KERNEL_INVALID_ARGUMENT;
    for (left = 0; left < candidate_count; ++left) {
        size_t right;
        if (left > 0u && hhs175_candidate_compare(
                &ordered_candidates[left - 1u], &ordered_candidates[left]
            ) > 0) {
            return HHS175_KERNEL_ORDER;
        }
        for (right = left + 1u; right < candidate_count; ++right) {
            int conflict = hhs175_kernel_candidate_conflict(
                &ordered_candidates[left].input, &ordered_candidates[right].input
            );
            if (conflict < 0) return conflict;
            if (conflict > 0) return HHS175_KERNEL_CONFLICT;
        }
    }
    successor = *canonical_state;
    admission = vm81_admit(
        vm81_context,
        ordered_candidates,
        candidate_count,
        canonical_state,
        &successor,
        &receipt
    );
    if (admission != 0) {
        canonical_state->rejected_candidates += candidate_count;
        return HHS175_KERNEL_VM81_REJECTED;
    }
    successor.epoch = canonical_state->epoch + 1u;
    successor.admitted_candidates = canonical_state->admitted_candidates + candidate_count;
    successor.rejected_candidates = canonical_state->rejected_candidates;
    successor.ordered_commit_root = hhs175_mix64(
        canonical_state->ordered_commit_root ^ receipt ^ (uint64_t)candidate_count
    );
    *canonical_state = successor;
    *hash72_receipt_token_out = receipt;
    return HHS175_KERNEL_OK;
}

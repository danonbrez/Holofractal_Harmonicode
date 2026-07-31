#include "vm81_invariant_kernel.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static int admit(
    void *context,
    const HHS175KernelCandidate *candidates,
    size_t candidate_count,
    const HHS175KernelState *predecessor,
    HHS175KernelState *successor,
    uint64_t *receipt
) {
    size_t index;
    (void)context;
    *successor = *predecessor;
    for (index = 0; index < candidate_count; ++index) {
        uint16_t cell = candidates[index].input.write_cell;
        successor->cells[cell] = candidates[index].input.write_value;
        *receipt ^= candidates[index].candidate_identity;
    }
    *receipt ^= UINT64_C(0x483732);
    return 0;
}

static void test_addresses(void) {
    uint32_t state;
    uint32_t projected;
    uint32_t decoded_state;
    uint32_t decoded_control;
    HHS175KernelAddress address;
    uint32_t cell;
    uint32_t operation;
    for (cell = 0; cell < 81u; ++cell) {
        for (operation = 0; operation < 64u; ++operation) {
            assert(hhs175_kernel_address_encode(cell, operation, &state) == 0);
            assert(hhs175_kernel_address_decode(state, &address) == 0);
            assert(address.cell == cell);
            assert(address.operation == operation);
        }
    }
    assert(state == 5183u);
    for (state = 0; state < 5184u; ++state) {
        uint32_t control;
        for (control = 0; control < 243u; ++control) {
            assert(hhs175_kernel_projected_encode(state, control, &projected) == 0);
            assert(hhs175_kernel_projected_decode(projected, &decoded_state, &decoded_control) == 0);
            assert(decoded_state == state);
            assert(decoded_control == control);
        }
    }
    assert(projected == 1259711u);
}

static void test_controls(void) {
    uint32_t control;
    for (control = 0; control < 243u; ++control) {
        uint8_t trits[5];
        uint16_t encoded;
        assert(hhs175_kernel_control_decode(control, trits) == 0);
        assert(hhs175_kernel_control_encode(trits, &encoded) == 0);
        assert(encoded == control);
    }
}

static void test_scalars(void) {
    static const uint8_t expected_lo[8] = {0,1,0,1,10,11,1,0};
    static const uint8_t expected_hi[8] = {1,0,11,10,1,0,0,111};
    size_t length;
    const uint8_t *value = hhs175_kernel_scalar_lo(&length);
    assert(length == 8u);
    assert(memcmp(value, expected_lo, 8u) == 0);
    value = hhs175_kernel_scalar_hi(&length);
    assert(length == 8u);
    assert(memcmp(value, expected_hi, 8u) == 0);
}

static void test_candidates(void) {
    HHS175KernelCandidateInput inputs[2];
    HHS175KernelCandidate candidates[2];
    HHS175KernelState state;
    HHS175KernelBitset left;
    HHS175KernelBitset right;
    uint64_t receipt;
    memset(inputs, 0, sizeof(inputs));
    hhs175_kernel_bitset_clear(&left);
    hhs175_kernel_bitset_clear(&right);
    assert(hhs175_kernel_bitset_add(&left, 1u) == 0);
    assert(hhs175_kernel_bitset_add(&right, 2u) == 0);
    inputs[0].epoch = 0;
    inputs[0].sequence = 1;
    inputs[0].thread_id = 1;
    inputs[0].state = 1;
    inputs[0].control = 1;
    inputs[0].write_cell = 1;
    inputs[0].write_value = 1;
    inputs[0].write_set = left;
    inputs[0].instruction_identity = 11;
    inputs[1].epoch = 0;
    inputs[1].sequence = 0;
    inputs[1].thread_id = 2;
    inputs[1].state = 2;
    inputs[1].control = 2;
    inputs[1].write_cell = 2;
    inputs[1].write_value = -1;
    inputs[1].write_set = right;
    inputs[1].instruction_identity = 22;
    assert(hhs175_kernel_prepare_candidates(inputs, 2u, candidates) == 0);
    assert(hhs175_kernel_sort_candidates(candidates, 2u) == 0);
    assert(candidates[0].input.sequence == 0u);
    assert(hhs175_kernel_candidate_conflict(&inputs[0], &inputs[1]) == 0);
    hhs175_kernel_state_reset(&state);
    assert(hhs175_kernel_commit_candidates(candidates, 2u, &state, admit, NULL, &receipt) == 0);
    assert(state.epoch == 1u);
    assert(state.cells[1] == 1);
    assert(state.cells[2] == -1);
    assert(state.admitted_candidates == 2u);
    assert(receipt != 0u);
}

static void test_conflict_rejection(void) {
    HHS175KernelCandidateInput inputs[2];
    HHS175KernelCandidate candidates[2];
    HHS175KernelState state;
    HHS175KernelBitset write;
    uint64_t receipt;
    memset(inputs, 0, sizeof(inputs));
    hhs175_kernel_bitset_clear(&write);
    assert(hhs175_kernel_bitset_add(&write, 7u) == 0);
    inputs[0].state = 0;
    inputs[0].control = 0;
    inputs[0].write_cell = 7;
    inputs[0].write_value = 1;
    inputs[0].write_set = write;
    inputs[1] = inputs[0];
    inputs[1].sequence = 1;
    inputs[1].write_value = -1;
    assert(hhs175_kernel_prepare_candidates(inputs, 2u, candidates) == 0);
    assert(hhs175_kernel_sort_candidates(candidates, 2u) == 0);
    hhs175_kernel_state_reset(&state);
    assert(hhs175_kernel_commit_candidates(candidates, 2u, &state, admit, NULL, &receipt) == HHS175_KERNEL_CONFLICT);
    assert(state.epoch == 0u);
}

int main(void) {
    assert(hhs175_kernel_abi_version() == HHS175_KERNEL_ABI_VERSION);
    test_addresses();
    test_controls();
    test_scalars();
    test_candidates();
    test_conflict_rejection();
    puts("HHS_PASS_175_INVARIANT_KERNEL_TEST_PASS");
    return 0;
}

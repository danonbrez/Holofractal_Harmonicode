#include "hhs_pass219_harmonic36_nested_vm_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>

static uint64_t enc(uint16_t op, uint8_t ac, uint32_t e) {
    uint64_t word = 0U;
    assert(hhs_exact_pass219_h36_instruction_encode(
        op, ac, 0U, 0U, e, &word) == HHS_EXACT_STATUS_OK);
    return word;
}

static void init(HHSExactPass219H36VMStateV1 *vm) {
    assert(hhs_exact_pass219_h36_vm_init(vm) == HHS_EXACT_STATUS_OK);
}

static HHSExactStatus one(
    HHSExactPass219H36VMStateV1 *vm, uint64_t instruction
) {
    vm->memory[0] = instruction;
    vm->pc18 = 0U;
    return hhs_exact_pass219_h36_vm_step(vm);
}

static uint64_t neg36(uint64_t magnitude) {
    return ((~magnitude) + UINT64_C(1)) &
           HHS_EXACT_PASS219_H36_WORD_MASK;
}

int main(void) {
    HHSExactPass219H36VMStateV1 vm;
    const uint64_t sign = UINT64_C(1) << 35U;

    /* MULI: positive product occupies 70-bit arithmetic field. */
    init(&vm);
    vm.accumulators[1] = 3U;
    assert(one(&vm, enc(UINT16_C(0225), 1U, 4U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] == 0U);
    assert(vm.accumulators[2] == 12U);
    assert(vm.legacy_overflow == 0U);

    /* Negative product duplicates sign and stores 70-bit two's complement. */
    init(&vm);
    vm.accumulators[1] = neg36(2U);
    assert(one(&vm, enc(UINT16_C(0225), 1U, 3U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] == HHS_EXACT_PASS219_H36_WORD_MASK);
    assert(vm.accumulators[2] == neg36(6U));

    /* -2^35 * -2^35 overflows positive range and stores -2^70. */
    init(&vm);
    vm.accumulators[1] = sign;
    vm.memory[100] = sign;
    assert(one(&vm, enc(UINT16_C(0224), 1U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.legacy_overflow == 1U);
    assert(vm.accumulators[1] == sign);
    assert(vm.accumulators[2] == sign);

    /* MULM stores only the high word; MULB stores high to AC and memory. */
    init(&vm);
    vm.accumulators[3] = 8U;
    vm.memory[100] = 9U;
    vm.accumulators[4] = 123U;
    assert(one(&vm, enc(UINT16_C(0226), 3U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.memory[100] == 0U);
    assert(vm.accumulators[3] == 8U);
    assert(vm.accumulators[4] == 123U);

    init(&vm);
    vm.accumulators[3] = 8U;
    vm.memory[100] = 9U;
    assert(one(&vm, enc(UINT16_C(0227), 3U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[3] == 0U);
    assert(vm.accumulators[4] == 72U);
    assert(vm.memory[100] == 0U);

    /* DIVI: high/low 0,12 divided by 3 gives quotient 4 remainder 0. */
    init(&vm);
    vm.accumulators[5] = 0U;
    vm.accumulators[6] = 12U;
    assert(one(&vm, enc(UINT16_C(0235), 5U, 3U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[5] == 4U);
    assert(vm.accumulators[6] == 0U);
    assert(vm.legacy_no_divide == 0U);

    /* Negative dividend: -10 / 3 = -3 remainder -1. */
    init(&vm);
    vm.accumulators[5] = neg36(1U);
    vm.accumulators[6] = neg36(10U);
    assert(one(&vm, enc(UINT16_C(0235), 5U, 3U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[5] == neg36(3U));
    assert(vm.accumulators[6] == neg36(1U));

    /* No-divide leaves both words unchanged. */
    init(&vm);
    vm.accumulators[5] = 1U;
    vm.accumulators[6] = 0U;
    {
        uint64_t hi = vm.accumulators[5];
        uint64_t lo = vm.accumulators[6];
        assert(one(&vm, enc(UINT16_C(0235), 5U, 1U)) ==
               HHS_EXACT_STATUS_OK);
        assert(vm.legacy_no_divide == 1U);
        assert(vm.legacy_overflow == 1U);
        assert(vm.accumulators[5] == hi);
        assert(vm.accumulators[6] == lo);
    }

    /* LSHC moves across the word boundary. */
    init(&vm);
    vm.accumulators[7] = 0U;
    vm.accumulators[8] = UINT64_C(1) << 35U;
    assert(one(&vm, enc(UINT16_C(0246), 7U, 1U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[7] == 1U);
    assert(vm.accumulators[8] == 0U);

    /* ROTC recycles upper bit into low-word least significant bit. */
    init(&vm);
    vm.accumulators[7] = UINT64_C(1) << 35U;
    vm.accumulators[8] = 0U;
    assert(one(&vm, enc(UINT16_C(0245), 7U, 1U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[7] == 0U);
    assert(vm.accumulators[8] == 1U);

    /* ASHC preserves duplicated sign across the 70 arithmetic bits. */
    init(&vm);
    vm.accumulators[9] = HHS_EXACT_PASS219_H36_WORD_MASK;
    vm.accumulators[10] = neg36(4U);
    assert(one(&vm, enc(UINT16_C(0244), 9U, UINT32_C(0x20001))) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[9] == HHS_EXACT_PASS219_H36_WORD_MASK);
    assert(vm.accumulators[10] == neg36(2U));
    assert((vm.accumulators[9] & sign) != 0U);
    assert((vm.accumulators[10] & sign) != 0U);

    puts("PASS219 Harmonic36 two-word ISA 1.2 conformance: PASS");
    return 0;
}

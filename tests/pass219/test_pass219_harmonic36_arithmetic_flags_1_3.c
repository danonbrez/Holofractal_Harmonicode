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
    HHSExactPass219H36VMStateV1 *vm,
    uint64_t instruction
) {
    vm->memory[0] = instruction;
    vm->pc18 = 0U;
    vm->trap = HHS_EXACT_PASS219_H36_TRAP_NONE;
    return hhs_exact_pass219_h36_vm_step(vm);
}

int main(void) {
    HHSExactPass219H36VMStateV1 vm;
    const uint64_t sign = UINT64_C(1) << 35U;
    const uint64_t maxpos = sign - UINT64_C(1);
    const uint64_t negone = HHS_EXACT_PASS219_H36_WORD_MASK;

    /* Positive overflow: max positive + 1 => max negative, CRY1 + AROV. */
    init(&vm);
    vm.accumulators[1] = maxpos;
    assert(one(&vm, enc(UINT16_C(0271), 1U, 1U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] == sign);
    assert(vm.legacy_carry0 == 0U);
    assert(vm.legacy_carry1 == 1U);
    assert(vm.legacy_overflow == 1U);

    /* JFCL observes the arithmetic-produced flag and clears only selection. */
    vm.memory[0] = enc(UINT16_C(0255), 8U, 20U);
    vm.pc18 = 0U;
    assert(hhs_exact_pass219_h36_vm_step(&vm) == HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 20U);
    assert(vm.legacy_overflow == 0U);
    assert(vm.legacy_carry1 == 1U);

    /* -1 + 1 => 0 sets both carries without overflow. */
    init(&vm);
    vm.accumulators[1] = negone;
    assert(one(&vm, enc(UINT16_C(0271), 1U, 1U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] == 0U);
    assert(vm.legacy_carry0 == 1U);
    assert(vm.legacy_carry1 == 1U);
    assert(vm.legacy_overflow == 0U);

    /* Minimum negative - 1 => maximum positive, CRY0 + AROV. */
    init(&vm);
    vm.accumulators[1] = sign;
    assert(one(&vm, enc(UINT16_C(0275), 1U, 1U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] == maxpos);
    assert(vm.legacy_carry0 == 1U);
    assert(vm.legacy_carry1 == 0U);
    assert(vm.legacy_overflow == 1U);

    /* AOJA and SOJA set the historical increment/decrement flags. */
    init(&vm);
    vm.accumulators[2] = maxpos;
    assert(one(&vm, enc(UINT16_C(0344), 2U, 10U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[2] == sign);
    assert(vm.legacy_carry1 == 1U);
    assert(vm.legacy_overflow == 1U);

    init(&vm);
    vm.accumulators[2] = sign;
    assert(one(&vm, enc(UINT16_C(0364), 2U, 10U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[2] == maxpos);
    assert(vm.legacy_carry0 == 1U);
    assert(vm.legacy_overflow == 1U);

    /* MOVNI zero sets both carries; MOVN/MOVM of -2^35 overflow. */
    init(&vm);
    assert(one(&vm, enc(UINT16_C(0211), 3U, 0U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[3] == 0U);
    assert(vm.legacy_carry0 == 1U);
    assert(vm.legacy_carry1 == 1U);

    init(&vm);
    vm.memory[100] = sign;
    assert(one(&vm, enc(UINT16_C(0210), 3U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[3] == sign);
    assert(vm.legacy_carry1 == 1U);
    assert(vm.legacy_overflow == 1U);

    init(&vm);
    vm.memory[100] = sign;
    assert(one(&vm, enc(UINT16_C(0214), 3U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[3] == sign);
    assert(vm.legacy_carry1 == 1U);
    assert(vm.legacy_overflow == 1U);

    /* Flags are sticky until a flag-clearing instruction acts on them. */
    init(&vm);
    vm.legacy_carry0 = 1U;
    vm.accumulators[4] = 1U;
    assert(one(&vm, enc(UINT16_C(0271), 4U, 1U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[4] == 2U);
    assert(vm.legacy_carry0 == 1U);

    puts("PASS219 Harmonic36 arithmetic flags 1.3 conformance: PASS");
    return 0;
}

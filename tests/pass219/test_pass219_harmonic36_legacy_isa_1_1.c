#include "hhs_pass219_harmonic36_nested_vm_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint64_t enc(uint16_t op, uint8_t ac, uint32_t e) {
    uint64_t word = 0U;
    assert(hhs_exact_pass219_h36_instruction_encode(
        op, ac, 0U, 0U, e, &word) == HHS_EXACT_STATUS_OK);
    return word;
}

static uint64_t pointer_word(
    uint8_t p, uint8_t s, uint8_t indirect, uint8_t index, uint32_t y
) {
    return (((uint64_t)p & UINT64_C(077)) << 30U) |
           (((uint64_t)s & UINT64_C(077)) << 24U) |
           (((uint64_t)indirect & UINT64_C(1)) << 22U) |
           (((uint64_t)index & UINT64_C(017)) << 18U) |
           ((uint64_t)y & UINT64_C(0777777));
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

int main(void) {
    HHSExactPass219H36VMStateV1 vm;

    /* POINT 7 style: P=36, S=7; ILDB increments to P=29 first. */
    init(&vm);
    vm.memory[100] = pointer_word(36U, 7U, 0U, 0U, 101U);
    vm.memory[101] = UINT64_C(0x41) << 29U;
    assert(one(&vm, enc(UINT16_C(0134), 1U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] == UINT64_C(0x41));
    assert(((vm.memory[100] >> 30U) & UINT64_C(077)) == 29U);

    /* LDB does not increment; DPB preserves all non-byte bits. */
    init(&vm);
    vm.memory[100] = pointer_word(29U, 7U, 0U, 0U, 101U);
    vm.memory[101] = (UINT64_C(0x55) << 29U) | UINT64_C(01234567);
    assert(one(&vm, enc(UINT16_C(0135), 2U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[2] == UINT64_C(0x55));
    assert(((vm.memory[100] >> 30U) & UINT64_C(077)) == 29U);

    vm.trap = HHS_EXACT_PASS219_H36_TRAP_NONE;
    vm.accumulators[2] = UINT64_C(0x2A);
    {
        uint64_t before_low = vm.memory[101] & ((UINT64_C(1) << 29U) - 1U);
        assert(one(&vm, enc(UINT16_C(0137), 2U, 100U)) ==
               HHS_EXACT_STATUS_OK);
        assert(((vm.memory[101] >> 29U) & UINT64_C(0177)) ==
               UINT64_C(0x2A));
        assert((vm.memory[101] & ((UINT64_C(1) << 29U) - 1U)) ==
               before_low);
    }

    /* IBP at the final in-word byte moves to the next word. */
    init(&vm);
    vm.memory[100] = pointer_word(0U, 6U, 0U, 0U, 101U);
    assert(one(&vm, enc(UINT16_C(0133), 0U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(((vm.memory[100] >> 30U) & UINT64_C(077)) == 30U);
    assert((vm.memory[100] & UINT64_C(0777777)) == 102U);

    /* IMULI exact low word and overflow witness. */
    init(&vm);
    vm.accumulators[1] = 5U;
    assert(one(&vm, enc(UINT16_C(0221), 1U, 7U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] == 35U);
    assert(vm.legacy_overflow == 0U);

    init(&vm);
    vm.accumulators[1] = UINT64_C(1) << 34U;
    assert(one(&vm, enc(UINT16_C(0221), 1U, 4U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] == 0U);
    assert(vm.legacy_overflow == 1U);

    /* IDIVI quotient/remainder and no-divide preserves the operands. */
    init(&vm);
    vm.accumulators[3] = 100U;
    assert(one(&vm, enc(UINT16_C(0231), 3U, 7U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[3] == 14U);
    assert(vm.accumulators[4] == 2U);
    assert(vm.legacy_no_divide == 0U);

    init(&vm);
    vm.accumulators[3] = 100U;
    vm.accumulators[4] = 77U;
    assert(one(&vm, enc(UINT16_C(0231), 3U, 0U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[3] == 100U);
    assert(vm.accumulators[4] == 77U);
    assert(vm.legacy_no_divide == 1U);
    assert(vm.legacy_overflow == 1U);

    /* Arithmetic shifts preserve sign; logical shifts and rotates do not. */
    init(&vm);
    vm.accumulators[1] = UINT64_C(1);
    assert(one(&vm, enc(UINT16_C(0242), 1U, 1U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] == 2U);

    init(&vm);
    vm.accumulators[1] = UINT64_C(2);
    assert(one(&vm, enc(UINT16_C(0242), 1U, UINT32_C(0x20001))) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] == 1U);

    init(&vm);
    vm.accumulators[1] =
        (HHS_EXACT_PASS219_H36_WORD_MASK + 1U - UINT64_C(4)) &
        HHS_EXACT_PASS219_H36_WORD_MASK;
    assert(one(&vm, enc(UINT16_C(0240), 1U, UINT32_C(0x20001))) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] ==
           ((HHS_EXACT_PASS219_H36_WORD_MASK + 1U - UINT64_C(2)) &
            HHS_EXACT_PASS219_H36_WORD_MASK));

    init(&vm);
    vm.accumulators[1] = UINT64_C(1) << 35U;
    assert(one(&vm, enc(UINT16_C(0241), 1U, 1U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] == 1U);

    /* JFFO counts from PDP bit 0/sign end; negative is the documented special case. */
    init(&vm);
    vm.accumulators[5] = UINT64_C(1) << 30U;
    vm.accumulators[6] = 99U;
    assert(one(&vm, enc(UINT16_C(0243), 5U, 20U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[6] == 5U);
    assert(vm.pc18 == 20U);

    init(&vm);
    vm.accumulators[5] = UINT64_C(1) << 35U;
    vm.accumulators[6] = 99U;
    assert(one(&vm, enc(UINT16_C(0243), 5U, 20U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[6] == 0U);
    assert(vm.pc18 == 1U);

    /* Halfword immediate rules: HLLI/HLRI source left is zero; HRLI/HRRI use E. */
    init(&vm);
    vm.accumulators[1] =
        (UINT64_C(0777777) << 18U) | UINT64_C(0123456);
    assert(one(&vm, enc(UINT16_C(0501), 1U, UINT32_C(0765432))) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] == UINT64_C(0123456));

    init(&vm);
    vm.accumulators[1] = UINT64_C(0123456);
    assert(one(&vm, enc(UINT16_C(0505), 1U, UINT32_C(0765432))) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] ==
           ((UINT64_C(0765432) << 18U) | UINT64_C(0123456)));

    init(&vm);
    vm.accumulators[1] = UINT64_C(0777777) << 18U;
    assert(one(&vm, enc(UINT16_C(0541), 1U, UINT32_C(0123456))) ==
           HHS_EXACT_STATUS_OK);
    assert((vm.accumulators[1] & UINT64_C(0777777)) ==
           UINT64_C(0123456));

    init(&vm);
    vm.accumulators[1] =
        (UINT64_C(0765432) << 18U) | UINT64_C(0777777);
    assert(one(&vm, enc(UINT16_C(0545), 1U, UINT32_C(0123456))) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[1] == (UINT64_C(0765432) << 18U));

    /* Z/O/E suffixes modify the other destination half exactly. */
    init(&vm);
    vm.memory[100] = UINT64_C(0400000) << 18U;
    assert(one(&vm, enc(UINT16_C(0530), 1U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert((vm.accumulators[1] & UINT64_C(0777777)) ==
           UINT64_C(0777777));

    /* TRNE: right immediate mask, skip if all masked bits are zero. */
    init(&vm);
    vm.accumulators[1] = 0U;
    assert(one(&vm, enc(UINT16_C(0602), 1U, UINT32_C(1))) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 2U);

    /* TRZN: evaluate before zeroing, skip on nonzero, then clear masked bit. */
    init(&vm);
    vm.accumulators[1] = UINT64_C(1);
    assert(one(&vm, enc(UINT16_C(0626), 1U, UINT32_C(1))) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 2U);
    assert((vm.accumulators[1] & UINT64_C(1)) == 0U);

    /* TLON: left immediate mask; modification is OR and condition sees old bits. */
    init(&vm);
    vm.accumulators[1] = 0U;
    assert(one(&vm, enc(UINT16_C(0667), 1U, UINT32_C(2))) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 1U);
    assert((vm.accumulators[1] & (UINT64_C(2) << 18U)) != 0U);

    /* TDZ uses full memory mask and no-skip mode. */
    init(&vm);
    vm.memory[100] = UINT64_C(0777);
    vm.accumulators[1] = UINT64_C(0777777);
    assert(one(&vm, enc(UINT16_C(0630), 1U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert((vm.accumulators[1] & UINT64_C(0777)) == 0U);
    assert(vm.pc18 == 1U);

    /* Double-length duplicated-sign families remain explicit fail-closed gaps. */
    init(&vm);
    vm.accumulators[1] = 2U;
    vm.memory[100] = 3U;
    assert(one(&vm, enc(UINT16_C(0224), 1U, 100U)) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(vm.trap == HHS_EXACT_PASS219_H36_TRAP_UNIMPLEMENTED_OPCODE);

    init(&vm);
    assert(one(&vm, enc(UINT16_C(0244), 1U, 1U)) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(vm.trap == HHS_EXACT_PASS219_H36_TRAP_UNIMPLEMENTED_OPCODE);

    puts("PASS219 Harmonic36 legacy ISA 1.1 conformance: PASS");
    return 0;
}

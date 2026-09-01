#include "hhs_pass219_harmonic36_nested_vm_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>

static uint64_t xwd(uint32_t left, uint32_t right) {
    return ((((uint64_t)left) & HHS_EXACT_PASS219_H36_HALF_MASK) << 18U) |
           (((uint64_t)right) & HHS_EXACT_PASS219_H36_HALF_MASK);
}

static uint64_t enc(uint16_t op, uint8_t ac, uint32_t e) {
    uint64_t word = 0U;
    assert(hhs_exact_pass219_h36_instruction_encode(
        op, ac, 0U, 0U, e, &word) == HHS_EXACT_STATUS_OK);
    return word;
}

static uint64_t ioenc(uint8_t dev, uint8_t fn, uint32_t e) {
    uint64_t word = 0U;
    assert(hhs_exact_pass219_h36_io_instruction_encode(
        dev, fn, 0U, 0U, e, &word) == HHS_EXACT_STATUS_OK);
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
    HHSExactPass219H36IOInstructionV1 io;
    uint64_t status;
    uint64_t data;

    /* BLT moves lowest source first through destination E and advances AC. */
    init(&vm);
    vm.accumulators[1] = xwd(10U, 20U);
    vm.memory[10] = UINT64_C(0111);
    vm.memory[11] = UINT64_C(0222);
    vm.memory[12] = UINT64_C(0333);
    assert(one(&vm, enc(UINT16_C(0251), 1U, 22U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.memory[20] == UINT64_C(0111));
    assert(vm.memory[21] == UINT64_C(0222));
    assert(vm.memory[22] == UINT64_C(0333));
    assert(vm.accumulators[1] == xwd(13U, 23U));

    /* AOBJP/AOBJN add 1,,1 before signed branch testing. */
    init(&vm);
    vm.accumulators[2] = 0U;
    assert(one(&vm, enc(UINT16_C(0252), 2U, 30U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[2] == xwd(1U, 1U));
    assert(vm.pc18 == 30U);

    init(&vm);
    vm.accumulators[2] = xwd(UINT32_C(0400000), 0U);
    assert(one(&vm, enc(UINT16_C(0253), 2U, 31U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 31U);

    /* JFCL selector 10 octal means arithmetic overflow. */
    init(&vm);
    vm.legacy_overflow = 1U;
    vm.legacy_carry0 = 1U;
    assert(one(&vm, enc(UINT16_C(0255), 8U, 40U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 40U);
    assert(vm.legacy_overflow == 0U);
    assert(vm.legacy_carry0 == 1U);

    /* JRST selector 1 enters the historical user-mode state. */
    init(&vm);
    assert(one(&vm, enc(UINT16_C(0254), 1U, 5U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 5U);
    assert(vm.legacy_user_mode == 1U);

    /* PUSH then POP round-trip through the pushdown pointer. */
    init(&vm);
    vm.accumulators[3] = xwd(UINT32_C(0777776), 49U);
    vm.memory[100] = UINT64_C(012345670123);
    assert(one(&vm, enc(UINT16_C(0261), 3U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[3] == xwd(UINT32_C(0777777), 50U));
    assert(vm.memory[50] == UINT64_C(012345670123));

    vm.memory[0] = enc(UINT16_C(0262), 3U, 101U);
    vm.pc18 = 0U;
    assert(hhs_exact_pass219_h36_vm_step(&vm) == HHS_EXACT_STATUS_OK);
    assert(vm.memory[101] == UINT64_C(012345670123));
    assert(vm.accumulators[3] == xwd(UINT32_C(0777776), 49U));

    /* PUSHJ stores PC word and flags; POPJ returns via its right half. */
    init(&vm);
    vm.accumulators[4] = xwd(UINT32_C(0777777), 59U);
    vm.legacy_overflow = 1U;
    vm.legacy_no_divide = 1U;
    assert(one(&vm, enc(UINT16_C(0260), 4U, 70U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[4] == xwd(0U, 60U));
    assert(vm.legacy_pushdown_overflow == 1U);
    assert((vm.memory[60] & HHS_EXACT_PASS219_H36_HALF_MASK) == 1U);
    assert(((vm.memory[60] >> 18U) & UINT64_C(0400000)) != 0U);
    assert(((vm.memory[60] >> 18U) & UINT64_C(0000040)) != 0U);
    assert(vm.pc18 == 70U);

    vm.memory[0] = enc(UINT16_C(0263), 4U, 0U);
    vm.pc18 = 0U;
    vm.trap = HHS_EXACT_PASS219_H36_TRAP_NONE;
    assert(hhs_exact_pass219_h36_vm_step(&vm) == HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 1U);
    assert(vm.accumulators[4] == xwd(UINT32_C(0777777), 59U));

    /* JSR/JSP/JSA/JRA retain their distinct historical save layouts. */
    init(&vm);
    vm.legacy_carry1 = 1U;
    assert(one(&vm, enc(UINT16_C(0264), 0U, 20U)) ==
           HHS_EXACT_STATUS_OK);
    assert((vm.memory[20] & HHS_EXACT_PASS219_H36_HALF_MASK) == 1U);
    assert(((vm.memory[20] >> 18U) & UINT64_C(0100000)) != 0U);
    assert(vm.pc18 == 21U);

    init(&vm);
    vm.legacy_carry0 = 1U;
    assert(one(&vm, enc(UINT16_C(0265), 5U, 30U)) ==
           HHS_EXACT_STATUS_OK);
    assert((vm.accumulators[5] & HHS_EXACT_PASS219_H36_HALF_MASK) == 1U);
    assert(((vm.accumulators[5] >> 18U) & UINT64_C(0200000)) != 0U);
    assert(vm.pc18 == 30U);

    init(&vm);
    vm.accumulators[6] = UINT64_C(076543210765);
    assert(one(&vm, enc(UINT16_C(0266), 6U, 20U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.memory[20] == UINT64_C(076543210765));
    assert(vm.accumulators[6] == xwd(20U, 1U));
    assert(vm.pc18 == 21U);

    vm.memory[20] = UINT64_C(012345670123);
    vm.memory[0] = enc(UINT16_C(0267), 6U, 33U);
    vm.pc18 = 0U;
    assert(hhs_exact_pass219_h36_vm_step(&vm) == HHS_EXACT_STATUS_OK);
    assert(vm.accumulators[6] == UINT64_C(012345670123));
    assert(vm.pc18 == 33U);

    /* Literal I/O format: 111 | device7 | function3 | I | X | Y. */
    {
        uint64_t w = ioenc(UINT8_C(012), 2U, 100U);
        assert(hhs_exact_pass219_h36_io_instruction_decode(w, &io) ==
               HHS_EXACT_STATUS_OK);
        assert(io.device7 == UINT8_C(012));
        assert(io.function3 == 2U);
        assert(io.address18 == 100U);
        assert(((w >> 33U) & UINT64_C(7)) == UINT64_C(7));
    }

    /* DATAI / DATAO. */
    init(&vm);
    assert(hhs_exact_pass219_h36_io_device_set(
        &vm, UINT8_C(012), UINT64_C(0123), UINT64_C(045670123456)) ==
        HHS_EXACT_STATUS_OK);
    assert(one(&vm, ioenc(UINT8_C(012), 2U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.memory[100] == UINT64_C(045670123456));

    vm.memory[101] = UINT64_C(076543210123);
    assert(one(&vm, ioenc(UINT8_C(012), 3U, 101U)) ==
           HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_io_device_get(
        &vm, UINT8_C(012), &status, &data) == HHS_EXACT_STATUS_OK);
    assert(data == UINT64_C(076543210123));

    /* CONO / CONI and condition skips. */
    assert(one(&vm, ioenc(UINT8_C(012), 4U, UINT32_C(01234))) ==
           HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_io_device_get(
        &vm, UINT8_C(012), &status, &data) == HHS_EXACT_STATUS_OK);
    assert(status == UINT64_C(01234));

    assert(one(&vm, ioenc(UINT8_C(012), 5U, 102U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.memory[102] == UINT64_C(01234));

    vm.pc18 = 0U;
    vm.memory[0] = ioenc(UINT8_C(012), 6U, UINT32_C(04000));
    assert(hhs_exact_pass219_h36_vm_step(&vm) == HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 2U);

    vm.pc18 = 0U;
    vm.memory[0] = ioenc(UINT8_C(012), 7U, UINT32_C(01000));
    assert(hhs_exact_pass219_h36_vm_step(&vm) == HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 2U);

    /* BLKI/BLKO increment IOWD count/address before transfer. */
    init(&vm);
    assert(hhs_exact_pass219_h36_io_device_set(
        &vm, UINT8_C(013), UINT64_C(0), UINT64_C(0777)) ==
        HHS_EXACT_STATUS_OK);
    vm.memory[100] = xwd(UINT32_C(0777776), 109U);
    assert(one(&vm, ioenc(UINT8_C(013), 0U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.memory[110] == UINT64_C(0777));
    assert(vm.memory[100] == xwd(UINT32_C(0777777), 110U));
    assert(vm.pc18 == 2U);

    vm.memory[111] = UINT64_C(0555);
    vm.memory[100] = xwd(UINT32_C(0777776), 110U);
    vm.pc18 = 0U;
    vm.memory[0] = ioenc(UINT8_C(013), 1U, 100U);
    assert(hhs_exact_pass219_h36_vm_step(&vm) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_io_device_get(
        &vm, UINT8_C(013), &status, &data) == HHS_EXACT_STATUS_OK);
    assert(data == UINT64_C(0555));
    assert(vm.memory[100] == xwd(UINT32_C(0777777), 111U));
    assert(vm.pc18 == 2U);

    assert(vm.canonical_mutation_authority == 0U);
    assert(vm.canonical_hash72_authority == 0U);
    assert(vm.canonical_persistence_authority == 0U);
    assert(vm.floating_point_authority == 0U);

    puts("PASS219 Harmonic36 control/stack/I-O ISA 1.3 conformance: PASS");
    return 0;
}

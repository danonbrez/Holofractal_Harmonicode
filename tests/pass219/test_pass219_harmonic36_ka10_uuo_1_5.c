#include "hhs_pass219_harmonic36_nested_vm_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint64_t enc(
    uint16_t op,
    uint8_t ac,
    uint8_t indirect,
    uint8_t index,
    uint32_t e
) {
    uint64_t word = 0U;
    assert(hhs_exact_pass219_h36_instruction_encode(
        op, ac, indirect, index, e, &word) == HHS_EXACT_STATUS_OK);
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
    assert(vm->legacy_uuo_mode ==
           HHS_EXACT_PASS219_H36_UUO_MODE_HHS_MICROKERNEL);
}

static HHSExactStatus step0(
    HHSExactPass219H36VMStateV1 *vm,
    uint64_t word
) {
    vm->memory[0] = word;
    vm->pc18 = 0U;
    vm->trap = HHS_EXACT_PASS219_H36_TRAP_NONE;
    vm->halted = 0U;
    return hhs_exact_pass219_h36_vm_step(vm);
}

int main(void) {
    HHSExactPass219H36VMStateV1 vm;
    uint64_t expected = 0U;

    /* Default HHS microkernel mode remains unchanged. */
    init(&vm);
    vm.accumulators[1] =
        UINT64_C(HHS_EXACT_PASS219_H36_RULE_I_MAJOR) |
        (UINT64_C(0) << 8U) |
        (UINT64_C(20) << 12U);
    assert(step0(&vm, enc(UINT16_C(0001), 1U, 0U, 0U, 0U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.memory[20] != 0U);
    assert(vm.legacy_uuo_dispatch_count == 0U);

    /* Historical KA10 mode is explicit and validated. */
    init(&vm);
    assert(hhs_exact_pass219_h36_legacy_uuo_mode_set(
        &vm, HHS_EXACT_PASS219_H36_UUO_MODE_KA10_HISTORICAL) ==
        HHS_EXACT_STATUS_OK);

    /* User LUUO 001 stores opcode/AC/E in 40 and executes 41. */
    vm.legacy_user_mode = 1U;
    vm.memory[UINT32_C(041)] =
        enc(UINT16_C(0254), 0U, 0U, 0U, 70U);
    assert(step0(&vm, enc(UINT16_C(0001), 3U, 0U, 0U, 10U)) ==
           HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_instruction_encode(
        UINT16_C(0001), 3U, 0U, 0U, 10U, &expected) ==
        HHS_EXACT_STATUS_OK);
    assert(vm.memory[UINT32_C(040)] == expected);
    assert(vm.pc18 == 70U);
    assert(vm.legacy_user_mode == 1U);
    assert(vm.legacy_uuo_last_class ==
           HHS_EXACT_PASS219_H36_UUO_CLASS_LUUO);
    assert(vm.legacy_uuo_last_vector18 == UINT32_C(040));
    assert((vm.legacy_uuo_saved_pc_word &
            HHS_EXACT_PASS219_H36_HALF_MASK) == 1U);
    assert(vm.legacy_uuo_dispatch_count == 1U);

    /* MUUO 040 uses the same 40/41 pair but enters executive handling. */
    init(&vm);
    assert(hhs_exact_pass219_h36_legacy_uuo_mode_set(
        &vm, HHS_EXACT_PASS219_H36_UUO_MODE_KA10_HISTORICAL) ==
        HHS_EXACT_STATUS_OK);
    vm.legacy_user_mode = 1U;
    vm.legacy_user_io = 1U;
    vm.memory[UINT32_C(041)] =
        enc(UINT16_C(0254), 0U, 0U, 0U, 71U);
    assert(step0(&vm, enc(UINT16_C(0040), 4U, 0U, 0U, 11U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 71U);
    assert(vm.legacy_user_mode == 0U);
    assert(vm.legacy_user_io == 0U);
    assert(vm.legacy_uuo_last_class ==
           HHS_EXACT_PASS219_H36_UUO_CLASS_MUUO);
    assert(vm.legacy_uuo_last_vector18 == UINT32_C(040));

    /* Opcode 000 follows monitor UUO handling in historical mode. */
    init(&vm);
    assert(hhs_exact_pass219_h36_legacy_uuo_mode_set(
        &vm, HHS_EXACT_PASS219_H36_UUO_MODE_KA10_HISTORICAL) ==
        HHS_EXACT_STATUS_OK);
    vm.memory[UINT32_C(041)] =
        enc(UINT16_C(0254), 0U, 0U, 0U, 73U);
    assert(step0(&vm, enc(UINT16_C(0000), 0U, 0U, 0U, 0U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 73U);
    assert(vm.legacy_uuo_last_class ==
           HHS_EXACT_PASS219_H36_UUO_CLASS_MUUO);

    /* Unassigned 100-127 use 60/61. */
    init(&vm);
    assert(hhs_exact_pass219_h36_legacy_uuo_mode_set(
        &vm, HHS_EXACT_PASS219_H36_UUO_MODE_KA10_HISTORICAL) ==
        HHS_EXACT_STATUS_OK);
    vm.memory[UINT32_C(061)] =
        enc(UINT16_C(0254), 0U, 0U, 0U, 72U);
    assert(step0(&vm, enc(UINT16_C(0100), 5U, 0U, 0U, 12U)) ==
           HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_instruction_encode(
        UINT16_C(0100), 5U, 0U, 0U, 12U, &expected) ==
        HHS_EXACT_STATUS_OK);
    assert(vm.memory[UINT32_C(060)] == expected);
    assert(vm.pc18 == 72U);
    assert(vm.legacy_uuo_last_class ==
           HHS_EXACT_PASS219_H36_UUO_CLASS_UNASSIGNED);
    assert(vm.legacy_uuo_last_vector18 == UINT32_C(060));

    /* User I/O restriction acts as MUUO in historical KA10 mode. */
    init(&vm);
    assert(hhs_exact_pass219_h36_legacy_uuo_mode_set(
        &vm, HHS_EXACT_PASS219_H36_UUO_MODE_KA10_HISTORICAL) ==
        HHS_EXACT_STATUS_OK);
    vm.legacy_user_mode = 1U;
    vm.legacy_user_io = 0U;
    vm.memory[UINT32_C(041)] =
        enc(UINT16_C(0254), 0U, 0U, 0U, 74U);
    assert(step0(&vm, ioenc(UINT8_C(012), 2U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 74U);
    assert(vm.trap == HHS_EXACT_PASS219_H36_TRAP_NONE);
    assert(vm.legacy_user_io_trap == 1U);
    assert(vm.legacy_user_mode == 0U);
    assert(vm.legacy_uuo_last_class ==
           HHS_EXACT_PASS219_H36_UUO_CLASS_IO_RESTRICTION);
    assert(vm.legacy_uuo_last_vector18 == UINT32_C(040));

    /* The same restriction remains fail-closed in HHS microkernel mode. */
    init(&vm);
    vm.legacy_user_mode = 1U;
    vm.legacy_user_io = 0U;
    assert(step0(&vm, ioenc(UINT8_C(012), 2U, 100U)) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(vm.trap == HHS_EXACT_PASS219_H36_TRAP_LEGACY_PRIVILEGE);

    /* KA10 247/257 remain reserved special slots, not later MAP semantics. */
    init(&vm);
    assert(hhs_exact_pass219_h36_legacy_uuo_mode_set(
        &vm, HHS_EXACT_PASS219_H36_UUO_MODE_KA10_HISTORICAL) ==
        HHS_EXACT_STATUS_OK);
    assert(step0(&vm, enc(UINT16_C(0247), 0U, 0U, 0U, 0U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.legacy_special_247_seen == 1U);
    assert(vm.legacy_uuo_dispatch_count == 0U);

    assert(step0(&vm, enc(UINT16_C(0257), 0U, 0U, 0U, 0U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.legacy_special_257_seen == 1U);
    assert(vm.legacy_uuo_dispatch_count == 0U);

    assert(hhs_exact_pass219_h36_legacy_uuo_mode_set(
        &vm, 2U) == HHS_EXACT_STATUS_RANGE_ERROR);

    assert(vm.canonical_mutation_authority == 0U);
    assert(vm.canonical_hash72_authority == 0U);
    assert(vm.canonical_persistence_authority == 0U);
    assert(vm.floating_point_authority == 0U);

    puts("PASS219 Harmonic36 KA10 UUO 1.5 conformance: PASS");
    return 0;
}

#include "hhs_pass219_harmonic36_nested_vm_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#define PC_AROV UINT32_C(0400000)
#define PC_USER UINT32_C(0010000)
#define PC_UIOT UINT32_C(0004000)

static uint64_t xwd(uint32_t left, uint32_t right) {
    return ((((uint64_t)left) & HHS_EXACT_PASS219_H36_HALF_MASK) << 18U) |
           (((uint64_t)right) & HHS_EXACT_PASS219_H36_HALF_MASK);
}

static uint64_t enc(
    uint16_t op,
    uint8_t ac,
    uint8_t indirect,
    uint32_t e
) {
    uint64_t word = 0U;
    assert(hhs_exact_pass219_h36_instruction_encode(
        op, ac, indirect, 0U, e, &word) == HHS_EXACT_STATUS_OK);
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
    vm->halted = 0U;
    return hhs_exact_pass219_h36_vm_step(vm);
}

int main(void) {
    HHSExactPass219H36VMStateV1 vm;

    /* JRST 1,E enters user mode without inventing extra authority. */
    init(&vm);
    assert(one(&vm, enc(UINT16_C(0254), UINT8_C(01), 0U, 20U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 20U);
    assert(vm.legacy_user_mode == 1U);
    assert(vm.legacy_user_io == 0U);

    /* Executive JRSTF restores USER/UIOT and arithmetic flags from
       the final indirect word used during address calculation. */
    init(&vm);
    vm.memory[100] = xwd(PC_USER | PC_UIOT | PC_AROV, 30U);
    assert(one(&vm, enc(UINT16_C(0254), UINT8_C(02), 1U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 30U);
    assert(vm.legacy_user_mode == 1U);
    assert(vm.legacy_user_io == 1U);
    assert(vm.legacy_overflow == 1U);

    /* Once in user mode, JRSTF cannot elevate UIOT from zero. */
    init(&vm);
    vm.legacy_user_mode = 1U;
    vm.legacy_user_io = 0U;
    vm.memory[100] = xwd(PC_USER | PC_UIOT, 31U);
    assert(one(&vm, enc(UINT16_C(0254), UINT8_C(02), 1U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 31U);
    assert(vm.legacy_user_mode == 1U);
    assert(vm.legacy_user_io == 0U);

    /* User JRSTF may clear UIOT but cannot clear USER. */
    init(&vm);
    vm.legacy_user_mode = 1U;
    vm.legacy_user_io = 1U;
    vm.memory[100] = xwd(0U, 32U);
    assert(one(&vm, enc(UINT16_C(0254), UINT8_C(02), 1U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 32U);
    assert(vm.legacy_user_mode == 1U);
    assert(vm.legacy_user_io == 0U);

    /* HALT is executive-only. */
    init(&vm);
    assert(one(&vm, enc(UINT16_C(0254), UINT8_C(04), 0U, 40U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.halted == 1U);
    assert(vm.pc18 == 40U);

    init(&vm);
    vm.legacy_user_mode = 1U;
    assert(one(&vm, enc(UINT16_C(0254), UINT8_C(04), 0U, 40U)) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(vm.trap == HHS_EXACT_PASS219_H36_TRAP_LEGACY_PRIVILEGE);
    assert(vm.halted == 0U);

    /* Priority channel 2 interrupts user execution and saves USER/UIOT. */
    init(&vm);
    vm.pc18 = 12U;
    vm.legacy_user_mode = 1U;
    vm.legacy_user_io = 1U;
    assert(hhs_exact_pass219_h36_priority_enable_mask(
        &vm, UINT8_C(0x7F)) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_priority_request(
        &vm, 2U, 50U) == HHS_EXACT_STATUS_OK);
    {
        uint8_t channel = 0U;
        assert(hhs_exact_pass219_h36_priority_enter(
            &vm, &channel) == HHS_EXACT_STATUS_OK);
        assert(channel == 2U);
    }
    assert(vm.pc18 == 50U);
    assert(vm.legacy_priority_active_channel == 2U);
    assert(vm.legacy_interrupt_cycle == 1U);
    assert(vm.legacy_user_mode == 0U);
    assert(vm.legacy_user_io == 0U);
    assert((vm.legacy_priority_saved_pc_word[1] &
            HHS_EXACT_PASS219_H36_HALF_MASK) == 12U);
    assert(((vm.legacy_priority_saved_pc_word[1] >> 18U) &
            PC_USER) != 0U);
    assert(((vm.legacy_priority_saved_pc_word[1] >> 18U) &
            PC_UIOT) != 0U);

    /* A lower priority cannot preempt channel 2; channel 1 can. */
    assert(hhs_exact_pass219_h36_priority_request(
        &vm, 5U, 55U) == HHS_EXACT_STATUS_OK);
    {
        uint8_t channel = 99U;
        assert(hhs_exact_pass219_h36_priority_enter(
            &vm, &channel) == HHS_EXACT_STATUS_OK);
        assert(channel == 0U);
    }
    assert(hhs_exact_pass219_h36_priority_request(
        &vm, 1U, 45U) == HHS_EXACT_STATUS_OK);
    {
        uint8_t channel = 0U;
        assert(hhs_exact_pass219_h36_priority_enter(
            &vm, &channel) == HHS_EXACT_STATUS_OK);
        assert(channel == 1U);
    }
    assert(vm.legacy_priority_active_channel == 1U);
    assert(vm.pc18 == 45U);

    /* JRST 10 dismisses the current PI and resumes the lower active level. */
    vm.memory[0] = enc(UINT16_C(0254), UINT8_C(010), 0U, 60U);
    vm.pc18 = 0U;
    assert(hhs_exact_pass219_h36_vm_step(&vm) == HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 60U);
    assert(vm.legacy_priority_active_channel == 2U);
    assert(vm.legacy_interrupt_cycle == 1U);

    /* JEN (JRST 12) dismisses channel 2 and restores its saved USER/UIOT. */
    vm.memory[100] = vm.legacy_priority_saved_pc_word[1];
    vm.memory[0] = enc(UINT16_C(0254), UINT8_C(012), 1U, 100U);
    vm.pc18 = 0U;
    assert(hhs_exact_pass219_h36_vm_step(&vm) == HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 12U);
    assert(vm.legacy_priority_active_channel == 0U);
    assert(vm.legacy_interrupt_cycle == 0U);
    assert(vm.legacy_user_mode == 1U);
    assert(vm.legacy_user_io == 1U);

    /* JEN/dismiss is privileged and traps from ordinary user execution. */
    init(&vm);
    vm.legacy_user_mode = 1U;
    assert(one(&vm, enc(UINT16_C(0254), UINT8_C(010), 0U, 10U)) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(vm.trap == HHS_EXACT_PASS219_H36_TRAP_LEGACY_PRIVILEGE);

    /* I/O in user mode requires previously granted user-I/O privilege. */
    init(&vm);
    vm.legacy_user_mode = 1U;
    vm.legacy_user_io = 0U;
    assert(hhs_exact_pass219_h36_io_device_set(
        &vm, UINT8_C(012), 0U, UINT64_C(0777)) ==
        HHS_EXACT_STATUS_OK);
    assert(one(&vm, ioenc(UINT8_C(012), 2U, 100U)) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(vm.trap == HHS_EXACT_PASS219_H36_TRAP_LEGACY_PRIVILEGE);
    assert(vm.legacy_user_io_trap == 1U);

    init(&vm);
    vm.legacy_user_mode = 1U;
    vm.legacy_user_io = 1U;
    assert(hhs_exact_pass219_h36_io_device_set(
        &vm, UINT8_C(012), 0U, UINT64_C(0777)) ==
        HHS_EXACT_STATUS_OK);
    assert(one(&vm, ioenc(UINT8_C(012), 2U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.memory[100] == UINT64_C(0777));

    /* Interrupt-cycle I/O is explicitly witnessed. */
    init(&vm);
    vm.legacy_interrupt_cycle = 1U;
    assert(hhs_exact_pass219_h36_io_device_set(
        &vm, UINT8_C(013), 0U, UINT64_C(01234)) ==
        HHS_EXACT_STATUS_OK);
    assert(one(&vm, ioenc(UINT8_C(013), 2U, 100U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.legacy_last_io_interrupt_cycle == 1U);

    /* KA10 special opcodes are no-ops when optional special hardware
       is absent; presence without a modeled extension fails closed. */
    init(&vm);
    assert(one(&vm, enc(UINT16_C(0247), 0U, 0U, 0U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.legacy_special_247_seen == 1U);

    assert(one(&vm, enc(UINT16_C(0257), 0U, 0U, 0U)) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.legacy_special_257_seen == 1U);

    init(&vm);
    vm.legacy_special_hardware_present = 1U;
    assert(one(&vm, enc(UINT16_C(0257), 0U, 0U, 0U)) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(vm.trap == HHS_EXACT_PASS219_H36_TRAP_UNIMPLEMENTED_OPCODE);

    assert(vm.canonical_mutation_authority == 0U);
    assert(vm.canonical_hash72_authority == 0U);
    assert(vm.canonical_persistence_authority == 0U);
    assert(vm.floating_point_authority == 0U);

    puts("PASS219 Harmonic36 privilege/PI 1.4 conformance: PASS");
    return 0;
}

#include "hhs_pass219_harmonic36_nested_vm_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#define MBIT(n) (UINT32_C(1) << (35U - (uint32_t)(n)))

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

static uint32_t select_channel(uint8_t channel) {
    assert(channel >= 1U && channel <= 7U);
    return MBIT(28U + channel);
}

int main(void) {
    HHSExactPass219H36VMStateV1 vm;
    uint64_t status = 0U;

    /* PI 1.4 compatibility remains active by default. */
    init(&vm);
    assert(vm.legacy_priority_system_on == 1U);

    /*
     * PI CONO: enable channel 3 and activate the system.
     * APR CONO: assign APR to channel 3 and enable arithmetic-overflow PI.
     */
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PI, 4U,
        MBIT(25U) | MBIT(28U) | select_channel(3U))) ==
        HHS_EXACT_STATUS_OK);
    assert((vm.legacy_priority_enabled_mask & UINT8_C(0x04)) != 0U);
    assert(vm.legacy_priority_system_on == 1U);

    vm.legacy_overflow = 1U;
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_APR, 4U,
        MBIT(31U) | UINT32_C(3))) == HHS_EXACT_STATUS_OK);
    assert(vm.legacy_apr_channel == 3U);
    assert(vm.legacy_apr_overflow_interrupt_enable == 1U);
    assert((vm.legacy_priority_external_request_mask &
            UINT8_C(0x04)) != 0U);

    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_APR, 5U, 100U)) ==
        HHS_EXACT_STATUS_OK);
    status = vm.memory[100];
    assert((status & MBIT(32U)) != 0U);
    assert((status & MBIT(31U)) != 0U);
    assert((status & UINT64_C(07)) == UINT64_C(3));

    vm.legacy_priority_vector18[2] = 50U;
    {
        uint8_t channel = 0U;
        assert(hhs_exact_pass219_h36_priority_enter(
            &vm, &channel) == HHS_EXACT_STATUS_OK);
        assert(channel == 3U);
        assert(vm.pc18 == 50U);
    }

    /*
     * KA10 divide failure is routed by the arithmetic-overflow interrupt
     * enable; there is deliberately no invented divide-check enable bit.
     */
    init(&vm);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PI, 4U,
        MBIT(25U) | select_channel(4U))) ==
        HHS_EXACT_STATUS_OK);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_APR, 4U,
        MBIT(31U) | UINT32_C(4))) == HHS_EXACT_STATUS_OK);
    vm.legacy_no_divide = 1U;
    vm.legacy_overflow = 1U;
    assert(hhs_exact_pass219_h36_internal_interrupt_refresh(&vm) ==
           HHS_EXACT_STATUS_OK);
    assert((vm.legacy_priority_external_request_mask &
            UINT8_C(0x08)) != 0U);

    /* Pushdown overflow requests APR PI without a separate enable. */
    init(&vm);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PI, 4U,
        MBIT(25U) | select_channel(2U))) ==
        HHS_EXACT_STATUS_OK);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_APR, 4U,
        UINT32_C(2))) == HHS_EXACT_STATUS_OK);
    vm.legacy_pushdown_overflow = 1U;
    assert(hhs_exact_pass219_h36_internal_interrupt_refresh(&vm) ==
           HHS_EXACT_STATUS_OK);
    assert((vm.legacy_priority_external_request_mask &
            UINT8_C(0x02)) != 0U);

    /* APR I/O reset clears peripheral control but not the PI system. */
    vm.tty_output_done = 1U;
    vm.tty_pi_channel = 2U;
    {
        uint8_t enabled_before = vm.legacy_priority_enabled_mask;
        uint8_t system_before = vm.legacy_priority_system_on;
        uint32_t reset_count = vm.legacy_apr_io_reset_count;
        assert(one(&vm, ioenc(
            HHS_EXACT_PASS219_H36_DEVICE_APR, 4U,
            MBIT(19U) | MBIT(18U) | UINT32_C(2))) ==
            HHS_EXACT_STATUS_OK);
        assert(vm.legacy_apr_io_reset_count == reset_count + 1U);
        assert(vm.tty_output_done == 0U);
        assert(vm.legacy_pushdown_overflow == 0U);
        assert(vm.legacy_priority_enabled_mask == enabled_before);
        assert(vm.legacy_priority_system_on == system_before);
    }

    /* APR DATAI/DATAO keep the documented console/register surface. */
    init(&vm);
    vm.legacy_console_data_switches36 = UINT64_C(012345670123);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_APR, 2U, 100U)) ==
        HHS_EXACT_STATUS_OK);
    assert(vm.memory[100] == UINT64_C(012345670123));

    vm.memory[100] =
        (UINT64_C(012) << 28U) | (UINT64_C(034) << 10U);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_APR, 3U, 100U)) ==
        HHS_EXACT_STATUS_OK);
    assert(vm.legacy_protection8 == UINT8_C(012));
    assert(vm.legacy_relocation8 == UINT8_C(034));

    /*
     * Program PI requests are distinct from hardware requests and force
     * acceptance even if their selected channel is disabled.
     */
    init(&vm);
    vm.legacy_priority_vector18[5] = 66U;
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PI, 4U,
        MBIT(24U) | select_channel(6U))) ==
        HHS_EXACT_STATUS_OK);
    assert((vm.legacy_priority_enabled_mask & UINT8_C(0x20)) == 0U);
    assert((vm.legacy_priority_program_request_mask &
            UINT8_C(0x20)) != 0U);

    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PI, 5U, 100U)) ==
        HHS_EXACT_STATUS_OK);
    status = vm.memory[100];
    assert((status & (UINT64_C(1) << (35U - 16U))) != 0U);
    assert((status & MBIT(28U)) != 0U);

    {
        uint8_t channel = 0U;
        assert(hhs_exact_pass219_h36_priority_enter(
            &vm, &channel) == HHS_EXACT_STATUS_OK);
        assert(channel == 6U);
        assert(vm.pc18 == 66U);
    }

    /*
     * Clearing a software request must not erase an external TTY request
     * on the same channel.
     */
    init(&vm);
    vm.tty_pi_channel = 5U;
    vm.tty_output_done = 1U;
    assert(hhs_exact_pass219_h36_internal_interrupt_refresh(&vm) ==
           HHS_EXACT_STATUS_OK);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PI, 4U,
        MBIT(24U) | select_channel(5U))) ==
        HHS_EXACT_STATUS_OK);
    assert((vm.legacy_priority_program_request_mask &
            UINT8_C(0x10)) != 0U);
    assert((vm.legacy_priority_external_request_mask &
            UINT8_C(0x10)) != 0U);

    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PI, 4U,
        MBIT(22U) | select_channel(5U))) ==
        HHS_EXACT_STATUS_OK);
    assert((vm.legacy_priority_program_request_mask &
            UINT8_C(0x10)) == 0U);
    assert((vm.legacy_priority_external_request_mask &
            UINT8_C(0x10)) != 0U);
    assert((vm.legacy_priority_request_mask & UINT8_C(0x10)) != 0U);

    /* Deactivated PI retains requests but cannot enter until reactivated. */
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PI, 4U,
        MBIT(25U) | select_channel(5U) | MBIT(27U))) ==
        HHS_EXACT_STATUS_OK);
    {
        uint8_t channel = 99U;
        assert(hhs_exact_pass219_h36_priority_enter(
            &vm, &channel) == HHS_EXACT_STATUS_OK);
        assert(channel == 0U);
    }
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PI, 4U,
        MBIT(28U))) == HHS_EXACT_STATUS_OK);
    vm.legacy_priority_vector18[4] = 75U;
    {
        uint8_t channel = 0U;
        assert(hhs_exact_pass219_h36_priority_enter(
            &vm, &channel) == HHS_EXACT_STATUS_OK);
        assert(channel == 5U);
    }

    /* PI reset dismisses held levels and turns the system/channels off. */
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PI, 4U,
        MBIT(23U))) == HHS_EXACT_STATUS_OK);
    assert(vm.legacy_priority_system_on == 0U);
    assert(vm.legacy_priority_enabled_mask == 0U);
    assert(vm.legacy_priority_active_mask == 0U);
    assert(vm.legacy_priority_active_channel == 0U);
    assert(vm.legacy_priority_program_request_mask == 0U);

    /* PI DATAI stores zero; DATAO is a bounded console-display witness. */
    vm.memory[100] = HHS_EXACT_PASS219_H36_WORD_MASK;
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PI, 2U, 100U)) ==
        HHS_EXACT_STATUS_OK);
    assert(vm.memory[100] == 0U);

    vm.memory[100] = UINT64_C(076543210765);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PI, 3U, 100U)) ==
        HHS_EXACT_STATUS_OK);
    assert(vm.legacy_pi_console_display36 == UINT64_C(076543210765));

    /* Contradictory set/clear control pairs fail closed. */
    init(&vm);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_APR, 4U,
        MBIT(30U) | MBIT(31U))) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE);
    init(&vm);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PI, 4U,
        MBIT(27U) | MBIT(28U))) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE);

    assert(vm.canonical_mutation_authority == 0U);
    assert(vm.canonical_hash72_authority == 0U);
    assert(vm.canonical_persistence_authority == 0U);
    assert(vm.floating_point_authority == 0U);

    puts("PASS219 Harmonic36 KA10 APR/PI 1.8: PASS");
    return 0;
}

#undef MBIT

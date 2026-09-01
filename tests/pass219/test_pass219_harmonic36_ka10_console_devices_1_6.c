#include "hhs_pass219_harmonic36_nested_vm_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

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

    /* TTY keyboard -> DATAI. */
    init(&vm);
    {
        const uint8_t input[] = { UINT8_C(0x41) };
        assert(hhs_exact_pass219_h36_tty_feed_input(
            &vm, input, 1U) == HHS_EXACT_STATUS_OK);
        assert(hhs_exact_pass219_h36_devices_step(&vm) ==
               HHS_EXACT_STATUS_OK);
        assert(vm.tty_input_done == 1U);
        assert(vm.tty_input_buffer == UINT8_C(0x41));
        assert(one(&vm, ioenc(
            HHS_EXACT_PASS219_H36_DEVICE_TTY, 2U, 100U)) ==
            HHS_EXACT_STATUS_OK);
        assert(vm.memory[100] == UINT64_C(0x41));
        assert(vm.tty_input_done == 0U);
    }

    /* TTY output Busy -> deterministic device completion -> Done + PI. */
    init(&vm);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_TTY, 4U, 2U)) ==
        HHS_EXACT_STATUS_OK);
    vm.memory[100] = UINT64_C(0x42);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_TTY, 3U, 100U)) ==
        HHS_EXACT_STATUS_OK);
    assert(vm.tty_output_busy == 1U);
    assert(vm.tty_output_done == 0U);
    assert(hhs_exact_pass219_h36_devices_step(&vm) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.tty_output_busy == 0U);
    assert(vm.tty_output_done == 1U);
    assert((vm.legacy_priority_request_mask & UINT8_C(0x02)) != 0U);
    {
        uint8_t out[4] = {0};
        size_t count = 0U;
        assert(hhs_exact_pass219_h36_tty_copy_output(
            &vm, out, sizeof(out), &count) == HHS_EXACT_STATUS_OK);
        assert(count == 1U);
        assert(out[0] == UINT8_C(0x42));
    }

    /* TTY test mode loops output directly into input. */
    init(&vm);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_TTY, 4U,
        (1U << 11U) | 3U)) == HHS_EXACT_STATUS_OK);
    vm.memory[100] = UINT64_C(0x43);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_TTY, 3U, 100U)) ==
        HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_devices_step(&vm) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.tty_input_done == 1U);
    assert(vm.tty_input_buffer == UINT8_C(0x43));
    assert(vm.tty_output_done == 1U);

    /* PTR alphanumeric mode: one 8-bit tape frame per read. */
    init(&vm);
    {
        const uint8_t tape[] = { UINT8_C(0x51), UINT8_C(0x52) };
        assert(hhs_exact_pass219_h36_ptr_load_tape(
            &vm, tape, 2U) == HHS_EXACT_STATUS_OK);
        assert(one(&vm, ioenc(
            HHS_EXACT_PASS219_H36_DEVICE_PTR, 4U,
            (1U << 4U) | 2U)) == HHS_EXACT_STATUS_OK);
        assert(vm.ptr_busy == 1U);
        assert(hhs_exact_pass219_h36_devices_step(&vm) ==
               HHS_EXACT_STATUS_OK);
        assert(vm.ptr_done == 1U);
        assert(vm.ptr_buffer36 == UINT64_C(0x51));
        assert(one(&vm, ioenc(
            HHS_EXACT_PASS219_H36_DEVICE_PTR, 2U, 100U)) ==
            HHS_EXACT_STATUS_OK);
        assert(vm.memory[100] == UINT64_C(0x51));
        assert(vm.ptr_done == 0U);
        assert(vm.ptr_busy == 1U);
        assert(hhs_exact_pass219_h36_devices_step(&vm) ==
               HHS_EXACT_STATUS_OK);
        assert(vm.ptr_buffer36 == UINT64_C(0x52));
    }

    /* PTR binary mode: six channel-8 frames -> one 36-bit word. */
    init(&vm);
    {
        const uint8_t tape[] = {
            UINT8_C(0x81), UINT8_C(0x82), UINT8_C(0x83),
            UINT8_C(0x84), UINT8_C(0x85), UINT8_C(0x86)
        };
        uint64_t expected = 0U;
        uint32_t i;
        for (i = 1U; i <= 6U; ++i)
            expected = (expected << 6U) | i;

        assert(hhs_exact_pass219_h36_ptr_load_tape(
            &vm, tape, 6U) == HHS_EXACT_STATUS_OK);
        assert(one(&vm, ioenc(
            HHS_EXACT_PASS219_H36_DEVICE_PTR, 4U,
            (1U << 5U) | (1U << 4U) | 1U)) ==
            HHS_EXACT_STATUS_OK);
        assert(hhs_exact_pass219_h36_devices_step(&vm) ==
               HHS_EXACT_STATUS_OK);
        assert(vm.ptr_done == 1U);
        assert(vm.ptr_buffer36 == expected);
        assert(one(&vm, ioenc(
            HHS_EXACT_PASS219_H36_DEVICE_PTR, 2U, 100U)) ==
            HHS_EXACT_STATUS_OK);
        assert(vm.memory[100] == expected);
    }

    /* PTP binary mode forces channel 8, clears channel 7, uses low six. */
    init(&vm);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PTP, 4U,
        (1U << 5U) | 4U)) == HHS_EXACT_STATUS_OK);
    vm.memory[100] = UINT64_C(0x6A);
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PTP, 3U, 100U)) ==
        HHS_EXACT_STATUS_OK);
    assert(vm.ptp_busy == 1U);
    assert(hhs_exact_pass219_h36_devices_step(&vm) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.ptp_done == 1U);
    assert((vm.legacy_priority_request_mask & UINT8_C(0x08)) != 0U);
    {
        uint8_t tape[4] = {0};
        size_t count = 0U;
        assert(hhs_exact_pass219_h36_ptp_copy_tape(
            &vm, tape, sizeof(tape), &count) == HHS_EXACT_STATUS_OK);
        assert(count == 1U);
        assert(tape[0] == UINT8_C(0xAA));
    }

    /* CONI and CONSO see the device's real Done state. */
    assert(one(&vm, ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PTP, 5U, 100U)) ==
        HHS_EXACT_STATUS_OK);
    assert((vm.memory[100] & UINT64_C(8)) != 0U);

    vm.memory[0] = ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PTP, 7U, 8U);
    vm.pc18 = 0U;
    assert(hhs_exact_pass219_h36_vm_step(&vm) ==
           HHS_EXACT_STATUS_OK);
    assert(vm.pc18 == 2U);

    assert(vm.canonical_mutation_authority == 0U);
    assert(vm.canonical_hash72_authority == 0U);
    assert(vm.canonical_persistence_authority == 0U);
    assert(vm.floating_point_authority == 0U);

    puts("PASS219 Harmonic36 KA10 console devices 1.6: PASS");
    return 0;
}

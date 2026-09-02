#include "hhs_pass219_harmonic36_ka10_monitor_profile_1_9.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define EXEC_CELL UINT32_C(0120)
#define DATA_CELL UINT32_C(0121)

static uint64_t ioenc(uint8_t device, uint8_t fn, uint32_t e) {
    uint64_t word = 0U;
    assert(hhs_exact_pass219_h36_io_instruction_encode(
        device, fn, 0U, 0U, e, &word) == HHS_EXACT_STATUS_OK);
    return word;
}

static void exec_io(
    HHSExactPass219H36VMStateV1 *vm,
    uint64_t instruction
) {
    vm->memory[EXEC_CELL] = instruction;
    vm->pc18 = EXEC_CELL;
    vm->trap = HHS_EXACT_PASS219_H36_TRAP_NONE;
    vm->halted = 0U;
    assert(hhs_exact_pass219_h36_vm_step(vm) ==
           HHS_EXACT_STATUS_OK);
    vm->pc18 = HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18;
}

static void emit_word(
    uint64_t word,
    uint8_t frames[6]
) {
    int shift;
    size_t off = 0U;
    for (shift = 30; shift >= 0; shift -= 6) {
        frames[off++] = (uint8_t)(
            UINT8_C(0x80) |
            (uint8_t)((word >> (uint32_t)shift) & UINT64_C(0x3F))
        );
    }
}

static void exercise(
    HHSExactPass219H36VMStateV1 *vm,
    HHSExactPass219H36MonitorStateV1 *monitor,
    HHSExactPass219H36MonitorReceiptV1 *receipt
) {
    uint32_t steps = 0U;
    uint8_t tty_in = (uint8_t)'A';
    uint8_t tty_out[8] = {0};
    size_t tty_out_count = 0U;
    uint8_t ptr_frames[6] = {0};
    uint64_t ptr_word = UINT64_C(012345670123);
    uint8_t ptp_frames[8] = {0};
    size_t ptp_count = 0U;

    assert(hhs_exact_pass219_h36_tty_feed_input(
        vm, &tty_in, 1U) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_ka10_monitor_drive(
        vm, monitor, 3U, &steps) == HHS_EXACT_STATUS_OK);
    assert(steps == 3U);
    assert(vm->memory[
        HHS_EXACT_PASS219_H36_MONITOR_TTY_SCRATCH18] ==
        (uint64_t)tty_in);
    assert(monitor->tty_service_count == 1U);

    vm->memory[DATA_CELL] = (uint64_t)'B';
    exec_io(
        vm,
        ioenc(
            HHS_EXACT_PASS219_H36_DEVICE_TTY,
            3U,
            DATA_CELL
        )
    );
    assert(hhs_exact_pass219_h36_ka10_monitor_drive(
        vm, monitor, 3U, &steps) == HHS_EXACT_STATUS_OK);
    assert(steps == 3U);
    assert(monitor->tty_service_count == 2U);
    assert(hhs_exact_pass219_h36_tty_copy_output(
        vm, tty_out, sizeof(tty_out), &tty_out_count) ==
        HHS_EXACT_STATUS_OK);
    assert(tty_out_count == 1U);
    assert(tty_out[0] == (uint8_t)'B');

    emit_word(ptr_word, ptr_frames);
    assert(hhs_exact_pass219_h36_ptr_load_tape(
        vm, ptr_frames, sizeof(ptr_frames)) ==
        HHS_EXACT_STATUS_OK);
    exec_io(
        vm,
        ioenc(
            HHS_EXACT_PASS219_H36_DEVICE_PTR,
            4U,
            (UINT32_C(1) << 5U) | (UINT32_C(1) << 4U) |
                UINT32_C(2)
        )
    );
    assert(hhs_exact_pass219_h36_ka10_monitor_drive(
        vm, monitor, 2U, &steps) == HHS_EXACT_STATUS_OK);
    assert(steps == 2U);
    assert(vm->memory[
        HHS_EXACT_PASS219_H36_MONITOR_PTR_SCRATCH18] ==
        ptr_word);
    assert(monitor->ptr_service_count == 1U);

    vm->memory[DATA_CELL] = (uint64_t)'C';
    exec_io(
        vm,
        ioenc(
            HHS_EXACT_PASS219_H36_DEVICE_PTP,
            3U,
            DATA_CELL
        )
    );
    assert(hhs_exact_pass219_h36_ka10_monitor_drive(
        vm, monitor, 2U, &steps) == HHS_EXACT_STATUS_OK);
    assert(steps == 2U);
    assert(monitor->ptp_service_count == 1U);
    assert(hhs_exact_pass219_h36_ptp_copy_tape(
        vm, ptp_frames, sizeof(ptp_frames), &ptp_count) ==
        HHS_EXACT_STATUS_OK);
    assert(ptp_count == 1U);
    assert(ptp_frames[0] == (uint8_t)'C');

    assert(hhs_exact_pass219_h36_ka10_monitor_drive(
        vm, monitor, 4U, &steps) == HHS_EXACT_STATUS_OK);
    assert(steps == 4U);
    assert(monitor->dispatch_count == 4U);
    assert(monitor->queue_cursor == 0U);
    assert(monitor->uuo_service_count == 4U);
    assert(vm->legacy_uuo_dispatch_count == 4U);
    assert(vm->pc18 ==
           HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18);

    assert(hhs_exact_pass219_h36_ka10_monitor_receipt_capture(
        vm, monitor, receipt) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_ka10_monitor_receipt_validate(
        vm, monitor, receipt) == HHS_EXACT_STATUS_OK);
}

int main(void) {
    HHSExactPass219H36VMStateV1 vm;
    HHSExactPass219H36VMStateV1 replay;
    HHSExactPass219H36MonitorStateV1 monitor;
    HHSExactPass219H36MonitorStateV1 replay_monitor;
    HHSExactPass219H36MonitorReceiptV1 initial;
    HHSExactPass219H36MonitorReceiptV1 replay_initial;
    HHSExactPass219H36MonitorReceiptV1 final_receipt;
    HHSExactPass219H36MonitorReceiptV1 replay_receipt;

    assert(hhs_exact_pass219_h36_ka10_monitor_bootstrap(
        &vm, &monitor, &initial) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_ka10_monitor_bootstrap(
        &replay, &replay_monitor, &replay_initial) ==
        HHS_EXACT_STATUS_OK);

    assert(memcmp(
        &initial, &replay_initial, sizeof(initial)) == 0);
    assert(initial.rim_receipt.exact_replayable == 1U);
    assert(initial.rim_receipt.first_loaded_address18 ==
           HHS_EXACT_PASS219_H36_MONITOR_IMAGE_START18);
    assert(initial.rim_receipt.last_loaded_address18 ==
           HHS_EXACT_PASS219_H36_MONITOR_IMAGE_LAST18);
    assert(initial.rim_receipt.loaded_word_count ==
           HHS_EXACT_PASS219_H36_MONITOR_IMAGE_WORDS);
    assert(initial.workload.feature_mask ==
           HHS_EXACT_PASS219_H36_MONITOR_FEATURE_MASK);
    assert(initial.workload.candidate_stack_only == 1U);
    assert(initial.workload.image_signature36 != 0U);

    assert(vm.legacy_priority_system_on == 1U);
    assert((vm.legacy_priority_enabled_mask & UINT8_C(0x0F)) ==
           UINT8_C(0x0F));
    assert(vm.legacy_apr_channel == 4U);
    assert(vm.legacy_apr_overflow_interrupt_enable == 1U);
    assert(vm.tty_pi_channel == 1U);
    assert(vm.ptr_pi_channel == 2U);
    assert(vm.ptp_pi_channel == 3U);
    assert(vm.memory[UINT32_C(042)] ==
           HHS_EXACT_PASS219_H36_MONITOR_TTY_ISR18);
    assert(vm.memory[UINT32_C(043)] ==
           HHS_EXACT_PASS219_H36_MONITOR_PTR_ISR18);
    assert(vm.memory[UINT32_C(044)] ==
           HHS_EXACT_PASS219_H36_MONITOR_PTP_ISR18);
    assert(vm.memory[UINT32_C(045)] ==
           HHS_EXACT_PASS219_H36_MONITOR_APR_ISR18);
    assert(vm.memory[UINT32_C(046)] ==
           HHS_EXACT_PASS219_H36_MONITOR_TASK0_18);
    assert(vm.memory[UINT32_C(047)] ==
           HHS_EXACT_PASS219_H36_MONITOR_TASK1_18);

    exercise(&vm, &monitor, &final_receipt);
    exercise(&replay, &replay_monitor, &replay_receipt);

    assert(memcmp(
        &final_receipt,
        &replay_receipt,
        sizeof(final_receipt)) == 0);
    assert(final_receipt.tty_service_count == 2U);
    assert(final_receipt.ptr_service_count == 1U);
    assert(final_receipt.ptp_service_count == 1U);
    assert(final_receipt.apr_service_count == 0U);
    assert(final_receipt.uuo_service_count == 4U);
    assert(final_receipt.dispatch_count == 4U);
    assert(final_receipt.exact_replayable == 1U);
    assert(final_receipt.candidate_stack_only == 1U);
    assert(final_receipt.canonical_mutation_authority == 0U);
    assert(final_receipt.canonical_hash72_authority == 0U);
    assert(final_receipt.canonical_hash216_authority == 0U);
    assert(final_receipt.canonical_persistence_authority == 0U);
    assert(final_receipt.floating_point_authority == 0U);

    puts("PASS219 Harmonic36 KA10 monitor profile 1.9: PASS");
    return 0;
}

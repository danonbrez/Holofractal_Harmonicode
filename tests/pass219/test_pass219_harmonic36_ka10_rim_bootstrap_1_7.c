#include "hhs_pass219_harmonic36_nested_vm_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint64_t enc(uint16_t op, uint8_t ac, uint32_t e) {
    uint64_t w = 0U;
    assert(hhs_exact_pass219_h36_instruction_encode(
        op, ac, 0U, 0U, e, &w) == HHS_EXACT_STATUS_OK);
    return w;
}

static uint64_t iowd(uint32_t count, uint32_t address_minus_one) {
    uint32_t neg = ((UINT32_C(1) << 18U) - count) &
                   HHS_EXACT_PASS219_H36_HALF_MASK;
    return (((uint64_t)neg) << 18U) |
           ((uint64_t)address_minus_one &
            HHS_EXACT_PASS219_H36_HALF_MASK);
}

static void emit_word(uint64_t word, uint8_t *frames, size_t *offset) {
    int shift;
    for (shift = 30; shift >= 0; shift -= 6) {
        frames[*offset] = (uint8_t)(
            UINT8_C(0x80) |
            (uint8_t)((word >> (uint32_t)shift) & UINT64_C(0x3F))
        );
        *offset += 1U;
    }
}

static void build_tape(
    uint8_t *frames,
    size_t *count,
    uint64_t *out_pointer,
    uint64_t *out_terminal
) {
    size_t off = 0U;
    const uint32_t first = 100U;
    const uint32_t words = 3U;
    uint64_t pointer = iowd(words, first - 1U);
    uint64_t data0 = UINT64_C(012345670123);
    uint64_t data1 = UINT64_C(076543210765);
    uint64_t terminal = enc(UINT16_C(0254), 0U, 120U);

    emit_word(pointer, frames, &off);
    emit_word(data0, frames, &off);
    emit_word(data1, frames, &off);
    emit_word(terminal, frames, &off);

    *count = off;
    *out_pointer = pointer;
    *out_terminal = terminal;
}

static void preset_dirty_flags(HHSExactPass219H36VMStateV1 *vm) {
    vm->legacy_overflow = 1U;
    vm->legacy_carry0 = 1U;
    vm->legacy_carry1 = 1U;
    vm->legacy_floating_overflow = 1U;
    vm->legacy_no_divide = 1U;
    vm->legacy_pushdown_overflow = 1U;
    vm->legacy_user_mode = 1U;
    vm->legacy_user_io = 1U;
    vm->legacy_priority_enabled_mask = UINT8_C(0x7F);
    vm->legacy_priority_request_mask = UINT8_C(0x7F);
    vm->legacy_priority_active_mask = UINT8_C(0x01);
    vm->legacy_priority_active_channel = 1U;
    vm->tty_output_busy = 1U;
    vm->tty_output_done = 1U;
    vm->ptp_busy = 1U;
    vm->ptp_done = 1U;
}

int main(void) {
    HHSExactPass219H36VMStateV1 vm;
    HHSExactPass219H36VMStateV1 replay;
    HHSExactPass219H36RIMReceiptV1 receipt;
    HHSExactPass219H36RIMReceiptV1 replay_receipt;
    uint8_t tape[64] = {0};
    size_t tape_count = 0U;
    uint64_t pointer = 0U;
    uint64_t terminal = 0U;

    build_tape(tape, &tape_count, &pointer, &terminal);
    assert(tape_count == 24U);

    assert(hhs_exact_pass219_h36_vm_init(&vm) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_ptr_load_tape(
        &vm, tape, tape_count) == HHS_EXACT_STATUS_OK);
    preset_dirty_flags(&vm);

    assert(hhs_exact_pass219_h36_rim_bootstrap(
        &vm, &receipt) == HHS_EXACT_STATUS_OK);

    assert(receipt.device7 == HHS_EXACT_PASS219_H36_DEVICE_PTR);
    assert(receipt.reset_witness == 1U);
    assert(receipt.pointer_valid == 1U);
    assert(receipt.terminal_executed == 1U);
    assert(receipt.declared_word_count == 3U);
    assert(receipt.loaded_word_count == 3U);
    assert(receipt.first_loaded_address18 == 100U);
    assert(receipt.last_loaded_address18 == 102U);
    assert(receipt.initial_iowd36 == pointer);
    assert(((receipt.final_iowd36 >> 18U) &
            HHS_EXACT_PASS219_H36_HALF_MASK) == 0U);
    assert((receipt.final_iowd36 &
            HHS_EXACT_PASS219_H36_HALF_MASK) == 102U);
    assert(receipt.terminal_word36 == terminal);
    assert(receipt.final_pc18 == 120U);
    assert(receipt.ptr_start_position == 0U);
    assert(receipt.ptr_end_position == 24U);
    assert(receipt.exact_replayable == 1U);

    assert(vm.memory[100] == UINT64_C(012345670123));
    assert(vm.memory[101] == UINT64_C(076543210765));
    assert(vm.memory[102] == terminal);
    assert(vm.pc18 == 120U);

    assert(vm.legacy_overflow == 0U);
    assert(vm.legacy_carry0 == 0U);
    assert(vm.legacy_carry1 == 0U);
    assert(vm.legacy_floating_overflow == 0U);
    assert(vm.legacy_no_divide == 0U);
    assert(vm.legacy_pushdown_overflow == 0U);
    assert(vm.legacy_user_mode == 0U);
    assert(vm.legacy_user_io == 0U);
    assert(vm.legacy_priority_enabled_mask == 0U);
    assert(vm.legacy_priority_request_mask == 0U);
    assert(vm.legacy_priority_active_mask == 0U);
    assert(vm.legacy_priority_active_channel == 0U);
    assert(vm.tty_output_busy == 0U);
    assert(vm.tty_output_done == 0U);
    assert(vm.ptp_busy == 0U);
    assert(vm.ptp_done == 0U);

    assert(hhs_exact_pass219_h36_rim_receipt_validate(
        &vm, &receipt) == HHS_EXACT_STATUS_OK);

    /* Exact replay from identical media and initialized VM. */
    assert(hhs_exact_pass219_h36_vm_init(&replay) ==
           HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_ptr_load_tape(
        &replay, tape, tape_count) == HHS_EXACT_STATUS_OK);
    preset_dirty_flags(&replay);
    assert(hhs_exact_pass219_h36_rim_bootstrap(
        &replay, &replay_receipt) == HHS_EXACT_STATUS_OK);

    assert(replay.memory[0] == vm.memory[0]);
    assert(replay.memory[100] == vm.memory[100]);
    assert(replay.memory[101] == vm.memory[101]);
    assert(replay.memory[102] == vm.memory[102]);
    assert(replay.pc18 == vm.pc18);
    assert(memcmp(&receipt, &replay_receipt, sizeof(receipt)) == 0);

    /* Invalid non-negative pointer fails closed. */
    {
        HHSExactPass219H36VMStateV1 bad;
        HHSExactPass219H36RIMReceiptV1 bad_receipt;
        uint8_t bad_tape[12] = {0};
        size_t off = 0U;
        emit_word(UINT64_C(1), bad_tape, &off);
        emit_word(terminal, bad_tape, &off);
        assert(hhs_exact_pass219_h36_vm_init(&bad) ==
               HHS_EXACT_STATUS_OK);
        assert(hhs_exact_pass219_h36_ptr_load_tape(
            &bad, bad_tape, off) == HHS_EXACT_STATUS_OK);
        assert(hhs_exact_pass219_h36_rim_bootstrap(
            &bad, &bad_receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    }

    assert(receipt.canonical_mutation_authority == 0U);
    assert(receipt.canonical_hash72_authority == 0U);
    assert(receipt.canonical_persistence_authority == 0U);
    assert(receipt.floating_point_authority == 0U);

    puts("PASS219 Harmonic36 KA10 RIM bootstrap 1.7: PASS");
    return 0;
}

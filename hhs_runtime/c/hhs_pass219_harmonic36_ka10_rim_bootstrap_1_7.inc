/*
 * KA10 hardware Read-In Mode (RIM) bootstrap.
 * Reuses concrete PTR 0104 and processor DATAI/BLKI semantics.
 */

static int32_t h36_rim_signed18(uint32_t value) {
    uint32_t v = value & UINT32_C(0777777);
    if ((v & UINT32_C(0400000)) != 0U)
        return (int32_t)(v | UINT32_C(0xFFFC0000));
    return (int32_t)v;
}

static void h36_rim_reset_controls(
    HHSExactPass219H36VMStateV1 *state
) {
    state->pc18 = 0U;
    state->halted = 0U;
    state->trap = HHS_EXACT_PASS219_H36_TRAP_NONE;
    state->legacy_overflow = 0U;
    state->legacy_carry0 = 0U;
    state->legacy_carry1 = 0U;
    state->legacy_floating_overflow = 0U;
    state->legacy_no_divide = 0U;
    state->legacy_pushdown_overflow = 0U;
    state->legacy_user_mode = 0U;
    state->legacy_user_io = 0U;
    state->legacy_user_io_trap = 0U;
    state->legacy_interrupt_cycle = 0U;
    state->legacy_last_io_interrupt_cycle = 0U;
    state->legacy_priority_enabled_mask = 0U;
    state->legacy_priority_request_mask = 0U;
    state->legacy_priority_active_mask = 0U;
    state->legacy_priority_active_channel = 0U;

    state->tty_test = 0U;
    state->tty_input_busy = 0U;
    state->tty_input_done = 0U;
    state->tty_output_busy = 0U;
    state->tty_output_done = 0U;
    state->tty_pi_channel = 0U;

    state->ptr_binary = 1U;
    state->ptr_busy = 0U;
    state->ptr_done = 0U;
    state->ptr_pi_channel = 0U;

    state->ptp_binary = 0U;
    state->ptp_busy = 0U;
    state->ptp_done = 0U;
    state->ptp_pi_channel = 0U;

    memset(state->io_status, 0, sizeof(state->io_status));
    memset(state->io_data, 0, sizeof(state->io_data));
}

static HHSExactStatus h36_rim_issue_io(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t function3
) {
    uint64_t word = 0U;
    HHSExactPass219H36InstructionV1 ins;
    HHSExactStatus status;

    status = hhs_exact_pass219_h36_io_instruction_encode(
        HHS_EXACT_PASS219_H36_DEVICE_PTR,
        function3,
        0U,
        0U,
        0U,
        &word
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_h36_instruction_decode(word, &ins);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return h36_execute(state, &ins, 0U);
}

HHSExactStatus hhs_exact_pass219_h36_rim_bootstrap(
    HHSExactPass219H36VMStateV1 *state,
    HHSExactPass219H36RIMReceiptV1 *out_receipt
) {
    uint16_t ptr_start;
    uint64_t iowd;
    uint32_t left;
    uint32_t right;
    int32_t signed_count;
    uint32_t count;
    uint32_t first;
    uint32_t last;
    uint32_t i;
    HHSExactPass219H36InstructionV1 terminal;
    HHSExactStatus status;

    if (state == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (state->struct_size != sizeof(*state) ||
        state->version != hhs_exact_pass219_h36_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    ptr_start = state->ptr_tape_position;
    h36_rim_reset_controls(state);

    state->ptr_busy = 1U;
    status = hhs_exact_pass219_h36_devices_step(state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (state->ptr_done == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = h36_rim_issue_io(state, 2U);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    iowd = state->memory[0] & HHS_EXACT_PASS219_H36_WORD_MASK;
    left = (uint32_t)((iowd >> 18U) &
                      HHS_EXACT_PASS219_H36_HALF_MASK);
    right = (uint32_t)(iowd & HHS_EXACT_PASS219_H36_HALF_MASK);
    signed_count = h36_rim_signed18(left);
    if (signed_count >= 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    count = (uint32_t)(-signed_count);
    first = (right + 1U) & UINT32_C(0777777);
    if (count == 0U ||
        first >= HHS_EXACT_PASS219_H36_WORD_COUNT ||
        count > HHS_EXACT_PASS219_H36_WORD_COUNT ||
        first + count > HHS_EXACT_PASS219_H36_WORD_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    last = first + count - 1U;

    for (i = 0U; i < count; ++i) {
        status = hhs_exact_pass219_h36_devices_step(state);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        if (state->ptr_done == 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        status = h36_rim_issue_io(state, 0U);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
    }

    if (((state->memory[0] >> 18U) &
         HHS_EXACT_PASS219_H36_HALF_MASK) != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_h36_instruction_decode(
        state->memory[last], &terminal
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    state->pc18 = 0U;
    status = h36_execute(state, &terminal, 0U);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = (uint32_t)sizeof(*out_receipt);
    out_receipt->version = hhs_exact_pass219_h36_version();
    out_receipt->device7 = HHS_EXACT_PASS219_H36_DEVICE_PTR;
    out_receipt->reset_witness = 1U;
    out_receipt->pointer_valid = 1U;
    out_receipt->terminal_executed = 1U;
    out_receipt->declared_word_count = count;
    out_receipt->loaded_word_count = count;
    out_receipt->first_loaded_address18 = first;
    out_receipt->last_loaded_address18 = last;
    out_receipt->initial_iowd36 = iowd;
    out_receipt->final_iowd36 = state->memory[0];
    out_receipt->terminal_word36 = state->memory[last];
    out_receipt->final_pc18 = state->pc18;
    out_receipt->ptr_start_position = ptr_start;
    out_receipt->ptr_end_position = state->ptr_tape_position;
    out_receipt->exact_replayable = 1U;
    out_receipt->canonical_mutation_authority = 0U;
    out_receipt->canonical_hash72_authority = 0U;
    out_receipt->canonical_persistence_authority = 0U;
    out_receipt->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_rim_receipt_validate(
    const HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36RIMReceiptV1 *receipt
) {
    if (state == NULL || receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (receipt->struct_size != sizeof(*receipt) ||
        receipt->version != hhs_exact_pass219_h36_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (receipt->device7 != HHS_EXACT_PASS219_H36_DEVICE_PTR ||
        receipt->reset_witness != 1U ||
        receipt->pointer_valid != 1U ||
        receipt->terminal_executed != 1U ||
        receipt->exact_replayable != 1U ||
        receipt->loaded_word_count != receipt->declared_word_count ||
        receipt->loaded_word_count == 0U ||
        receipt->last_loaded_address18 !=
            receipt->first_loaded_address18 +
            receipt->loaded_word_count - 1U ||
        receipt->last_loaded_address18 >=
            HHS_EXACT_PASS219_H36_WORD_COUNT ||
        receipt->final_iowd36 != state->memory[0] ||
        receipt->terminal_word36 !=
            state->memory[receipt->last_loaded_address18] ||
        receipt->final_pc18 != state->pc18 ||
        receipt->ptr_end_position != state->ptr_tape_position ||
        receipt->canonical_mutation_authority != 0U ||
        receipt->canonical_hash72_authority != 0U ||
        receipt->canonical_persistence_authority != 0U ||
        receipt->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

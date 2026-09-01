/*
 * KA10 internal APR/PI device programming layer.
 *
 * Device 000 (APR) exposes processor-condition control/status.
 * Device 004 (PI) exposes priority-interrupt system control/status.
 * All state remains emulator-local and carries no HHS canonical authority.
 */

#define H36_INT_BIT(machine_bit)     (UINT64_C(1) << (35U - (uint32_t)(machine_bit)))

static HHSExactStatus h36_internal_memory_required(
    HHSExactPass219H36VMStateV1 *state,
    uint32_t address
) {
    if (address >= HHS_EXACT_PASS219_H36_WORD_COUNT) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_RANGE;
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    return HHS_EXACT_STATUS_OK;
}

static uint8_t h36_pi_selected_channels(uint32_t e) {
    uint8_t mask = 0U;
    uint8_t channel;
    for (channel = 1U; channel <= HHS_EXACT_PASS219_H36_PI_CHANNELS;
         ++channel) {
        uint32_t bit = (uint32_t)H36_INT_BIT(28U + channel);
        if ((e & bit) != 0U)
            mask = (uint8_t)(mask | (uint8_t)(1U << (channel - 1U)));
    }
    return mask;
}

static uint64_t h36_pi_channels_to_word(
    uint8_t channels,
    uint32_t first_machine_bit
) {
    uint64_t word = 0U;
    uint8_t channel;
    for (channel = 1U; channel <= HHS_EXACT_PASS219_H36_PI_CHANNELS;
         ++channel) {
        if ((channels & (uint8_t)(1U << (channel - 1U))) != 0U)
            word |= H36_INT_BIT(first_machine_bit + channel - 1U);
    }
    return word;
}

static void h36_apr_peripheral_io_reset(
    HHSExactPass219H36VMStateV1 *state
) {
    state->tty_test = 0U;
    state->tty_input_busy = 0U;
    state->tty_input_done = 0U;
    state->tty_output_busy = 0U;
    state->tty_output_done = 0U;
    state->tty_pi_channel = 0U;
    state->tty_input_buffer = 0U;
    state->tty_output_buffer = 0U;

    state->ptr_binary = 0U;
    state->ptr_busy = 0U;
    state->ptr_done = 0U;
    state->ptr_pi_channel = 0U;
    state->ptr_buffer36 = 0U;

    state->ptp_binary = 0U;
    state->ptp_busy = 0U;
    state->ptp_done = 0U;
    state->ptp_pi_channel = 0U;
    state->ptp_buffer8 = 0U;

    memset(state->io_status, 0, sizeof(state->io_status));
    memset(state->io_data, 0, sizeof(state->io_data));
    state->legacy_apr_io_reset_count += 1U;
    h36_device_sync_io(state);
}

static int h36_apr_interrupt_condition(
    const HHSExactPass219H36VMStateV1 *state
) {
    if (state->legacy_pushdown_overflow != 0U)
        return 1;
    if (state->legacy_apr_address_break != 0U)
        return 1;
    if (state->legacy_apr_memory_protection != 0U)
        return 1;
    if (state->legacy_apr_nonexistent_memory != 0U)
        return 1;
    if (state->legacy_apr_clock_flag != 0U &&
        state->legacy_apr_clock_interrupt_enable != 0U)
        return 1;
    if (state->legacy_floating_overflow != 0U &&
        state->legacy_apr_floating_overflow_interrupt_enable != 0U)
        return 1;
    if (state->legacy_overflow != 0U &&
        state->legacy_apr_overflow_interrupt_enable != 0U)
        return 1;
    if (state->legacy_power_failure != 0U)
        return 1;
    if (state->legacy_parity_error != 0U &&
        state->legacy_parity_interrupt_enable != 0U)
        return 1;
    return 0;
}

HHSExactStatus hhs_exact_pass219_h36_internal_interrupt_refresh(
    HHSExactPass219H36VMStateV1 *state
) {
    uint8_t external = state == NULL ? 0U :
        state->legacy_priority_manual_request_mask;

    if (state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    if (state->tty_pi_channel >= 1U &&
        state->tty_pi_channel <= HHS_EXACT_PASS219_H36_PI_CHANNELS &&
        (state->tty_input_done != 0U || state->tty_output_done != 0U))
        external = (uint8_t)(
            external | (uint8_t)(1U << (state->tty_pi_channel - 1U)));

    if (state->ptr_pi_channel >= 1U &&
        state->ptr_pi_channel <= HHS_EXACT_PASS219_H36_PI_CHANNELS &&
        state->ptr_done != 0U)
        external = (uint8_t)(
            external | (uint8_t)(1U << (state->ptr_pi_channel - 1U)));

    if (state->ptp_pi_channel >= 1U &&
        state->ptp_pi_channel <= HHS_EXACT_PASS219_H36_PI_CHANNELS &&
        state->ptp_done != 0U)
        external = (uint8_t)(
            external | (uint8_t)(1U << (state->ptp_pi_channel - 1U)));

    if (state->legacy_apr_channel >= 1U &&
        state->legacy_apr_channel <= HHS_EXACT_PASS219_H36_PI_CHANNELS &&
        h36_apr_interrupt_condition(state))
        external = (uint8_t)(
            external | (uint8_t)(1U << (state->legacy_apr_channel - 1U)));

    state->legacy_priority_external_request_mask =
        (uint8_t)(external & UINT8_C(0x7F));
    state->legacy_priority_request_mask = (uint8_t)(
        state->legacy_priority_external_request_mask |
        state->legacy_priority_program_request_mask
    );
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_apr_status(
    const HHSExactPass219H36VMStateV1 *state,
    uint64_t *out_status36
) {
    uint64_t status;
    if (state == NULL || out_status36 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = (uint64_t)(state->legacy_apr_channel & UINT8_C(07));
    if (state->legacy_overflow != 0U)
        status |= H36_INT_BIT(32U);
    if (state->legacy_apr_overflow_interrupt_enable != 0U)
        status |= H36_INT_BIT(31U);
    if (state->legacy_apr_trap_offset != 0U)
        status |= H36_INT_BIT(30U);
    if (state->legacy_floating_overflow != 0U)
        status |= H36_INT_BIT(29U);
    if (state->legacy_apr_floating_overflow_interrupt_enable != 0U)
        status |= H36_INT_BIT(28U);
    if (state->legacy_apr_clock_interrupt_enable != 0U)
        status |= H36_INT_BIT(27U);
    if (state->legacy_apr_clock_flag != 0U)
        status |= H36_INT_BIT(26U);
    if (state->legacy_apr_nonexistent_memory != 0U)
        status |= H36_INT_BIT(23U);
    if (state->legacy_apr_memory_protection != 0U)
        status |= H36_INT_BIT(22U);
    if (state->legacy_apr_address_break != 0U)
        status |= H36_INT_BIT(21U);
    if (state->legacy_user_io != 0U)
        status |= H36_INT_BIT(20U);
    if (state->legacy_pushdown_overflow != 0U)
        status |= H36_INT_BIT(19U);

    *out_status36 = status & HHS_EXACT_PASS219_H36_WORD_MASK;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_pi_status(
    const HHSExactPass219H36VMStateV1 *state,
    uint64_t *out_status36
) {
    uint64_t status = 0U;
    if (state == NULL || out_status36 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status |= h36_pi_channels_to_word(
        state->legacy_priority_program_request_mask, 11U);
    if (state->legacy_power_failure != 0U)
        status |= H36_INT_BIT(18U);
    if (state->legacy_parity_error != 0U)
        status |= H36_INT_BIT(19U);
    if (state->legacy_parity_interrupt_enable != 0U)
        status |= H36_INT_BIT(20U);
    status |= h36_pi_channels_to_word(
        state->legacy_priority_active_mask, 21U);
    if (state->legacy_priority_system_on != 0U)
        status |= H36_INT_BIT(28U);
    status |= h36_pi_channels_to_word(
        state->legacy_priority_enabled_mask, 29U);

    *out_status36 = status & HHS_EXACT_PASS219_H36_WORD_MASK;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_apr_cono(
    HHSExactPass219H36VMStateV1 *state,
    uint32_t e
) {
    int clock_disable = (e & (uint32_t)H36_INT_BIT(24U)) != 0U;
    int clock_enable = (e & (uint32_t)H36_INT_BIT(25U)) != 0U;
    int fov_disable = (e & (uint32_t)H36_INT_BIT(27U)) != 0U;
    int fov_enable = (e & (uint32_t)H36_INT_BIT(28U)) != 0U;
    int ov_disable = (e & (uint32_t)H36_INT_BIT(30U)) != 0U;
    int ov_enable = (e & (uint32_t)H36_INT_BIT(31U)) != 0U;

    if ((clock_disable && clock_enable) ||
        (fov_disable && fov_enable) ||
        (ov_disable && ov_enable))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    state->legacy_apr_channel = (uint8_t)(e & UINT32_C(07));

    if ((e & (uint32_t)H36_INT_BIT(32U)) != 0U)
        state->legacy_overflow = 0U;
    if (ov_disable)
        state->legacy_apr_overflow_interrupt_enable = 0U;
    if (ov_enable)
        state->legacy_apr_overflow_interrupt_enable = 1U;

    if ((e & (uint32_t)H36_INT_BIT(29U)) != 0U)
        state->legacy_floating_overflow = 0U;
    if (fov_disable)
        state->legacy_apr_floating_overflow_interrupt_enable = 0U;
    if (fov_enable)
        state->legacy_apr_floating_overflow_interrupt_enable = 1U;

    if ((e & (uint32_t)H36_INT_BIT(26U)) != 0U)
        state->legacy_apr_clock_flag = 0U;
    if (clock_disable)
        state->legacy_apr_clock_interrupt_enable = 0U;
    if (clock_enable)
        state->legacy_apr_clock_interrupt_enable = 1U;

    if ((e & (uint32_t)H36_INT_BIT(23U)) != 0U)
        state->legacy_apr_nonexistent_memory = 0U;
    if ((e & (uint32_t)H36_INT_BIT(22U)) != 0U)
        state->legacy_apr_memory_protection = 0U;
    if ((e & (uint32_t)H36_INT_BIT(21U)) != 0U)
        state->legacy_apr_address_break = 0U;
    if ((e & (uint32_t)H36_INT_BIT(19U)) != 0U)
        h36_apr_peripheral_io_reset(state);
    if ((e & (uint32_t)H36_INT_BIT(18U)) != 0U)
        state->legacy_pushdown_overflow = 0U;

    return hhs_exact_pass219_h36_internal_interrupt_refresh(state);
}

static HHSExactStatus h36_pi_cono(
    HHSExactPass219H36VMStateV1 *state,
    uint32_t e
) {
    uint8_t selected = h36_pi_selected_channels(e);
    int parity_disable = (e & (uint32_t)H36_INT_BIT(20U)) != 0U;
    int parity_enable = (e & (uint32_t)H36_INT_BIT(21U)) != 0U;
    int clear_program = (e & (uint32_t)H36_INT_BIT(22U)) != 0U;
    int reset_system = (e & (uint32_t)H36_INT_BIT(23U)) != 0U;
    int request_program = (e & (uint32_t)H36_INT_BIT(24U)) != 0U;
    int channels_on = (e & (uint32_t)H36_INT_BIT(25U)) != 0U;
    int channels_off = (e & (uint32_t)H36_INT_BIT(26U)) != 0U;
    int deactivate = (e & (uint32_t)H36_INT_BIT(27U)) != 0U;
    int activate = (e & (uint32_t)H36_INT_BIT(28U)) != 0U;

    if ((parity_disable && parity_enable) ||
        (clear_program && request_program) ||
        (channels_on && channels_off) ||
        (deactivate && activate))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if ((e & (uint32_t)H36_INT_BIT(18U)) != 0U)
        state->legacy_power_failure = 0U;
    if ((e & (uint32_t)H36_INT_BIT(19U)) != 0U)
        state->legacy_parity_error = 0U;
    if (parity_disable)
        state->legacy_parity_interrupt_enable = 0U;
    if (parity_enable)
        state->legacy_parity_interrupt_enable = 1U;

    if (reset_system) {
        state->legacy_priority_system_on = 0U;
        state->legacy_priority_enabled_mask = 0U;
        state->legacy_priority_program_request_mask = 0U;
        state->legacy_priority_manual_request_mask = 0U;
        state->legacy_priority_external_request_mask = 0U;
        state->legacy_priority_request_mask = 0U;
        state->legacy_priority_active_mask = 0U;
        state->legacy_priority_active_channel = 0U;
        state->legacy_interrupt_cycle = 0U;
    }

    if (clear_program)
        state->legacy_priority_program_request_mask =
            (uint8_t)(state->legacy_priority_program_request_mask &
                      (uint8_t)~selected);
    if (request_program)
        state->legacy_priority_program_request_mask =
            (uint8_t)(state->legacy_priority_program_request_mask |
                      selected);
    if (channels_on)
        state->legacy_priority_enabled_mask =
            (uint8_t)(state->legacy_priority_enabled_mask | selected);
    if (channels_off)
        state->legacy_priority_enabled_mask =
            (uint8_t)(state->legacy_priority_enabled_mask &
                      (uint8_t)~selected);
    if (deactivate)
        state->legacy_priority_system_on = 0U;
    if (activate)
        state->legacy_priority_system_on = 1U;

    return hhs_exact_pass219_h36_internal_interrupt_refresh(state);
}

static HHSExactStatus h36_internal_conditions(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t device,
    uint8_t fn,
    uint32_t e
) {
    uint64_t status = 0U;
    HHSExactStatus result;

    result = device == HHS_EXACT_PASS219_H36_DEVICE_APR
        ? hhs_exact_pass219_h36_apr_status(state, &status)
        : hhs_exact_pass219_h36_pi_status(state, &status);
    if (result != HHS_EXACT_STATUS_OK)
        return result;

    if (fn == 6U && (status & (uint64_t)e) == 0U)
        state->pc18 = (state->pc18 + 1U) & UINT32_C(0777777);
    if (fn == 7U && (status & (uint64_t)e) != 0U)
        state->pc18 = (state->pc18 + 1U) & UINT32_C(0777777);
    return HHS_EXACT_STATUS_OK;
}

static int h36_execute_internal_apr_pi(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e,
    HHSExactStatus *out_status
) {
    HHSExactPass219H36IOInstructionV1 io;
    uint8_t device;
    uint8_t fn;
    HHSExactStatus status;
    uint64_t status_word = 0U;

    if (state == NULL || ins == NULL || out_status == NULL)
        return 0;

    status = hhs_exact_pass219_h36_io_instruction_decode(
        ins->word36, &io);
    if (status != HHS_EXACT_STATUS_OK)
        return 0;

    device = io.device7;
    fn = io.function3;
    if (device != HHS_EXACT_PASS219_H36_DEVICE_APR &&
        device != HHS_EXACT_PASS219_H36_DEVICE_PI)
        return 0;

    if (fn == 0U || fn == 1U) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_LEGACY_IO;
        *out_status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
        return 1;
    }

    if (fn == 2U) {
        status = h36_internal_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) {
            *out_status = status;
            return 1;
        }
        state->memory[e] =
            device == HHS_EXACT_PASS219_H36_DEVICE_APR
                ? (state->legacy_console_data_switches36 &
                   HHS_EXACT_PASS219_H36_WORD_MASK)
                : 0U;
        *out_status = HHS_EXACT_STATUS_OK;
        return 1;
    }

    if (fn == 3U) {
        status = h36_internal_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) {
            *out_status = status;
            return 1;
        }
        if (device == HHS_EXACT_PASS219_H36_DEVICE_APR) {
            uint64_t value = state->memory[e];
            state->legacy_relocation8 =
                (uint8_t)((value >> 10U) & UINT64_C(0xFF));
            state->legacy_protection8 =
                (uint8_t)((value >> 28U) & UINT64_C(0xFF));
        } else {
            state->legacy_pi_console_display36 =
                state->memory[e] & HHS_EXACT_PASS219_H36_WORD_MASK;
        }
        *out_status = HHS_EXACT_STATUS_OK;
        return 1;
    }

    if (fn == 4U) {
        *out_status =
            device == HHS_EXACT_PASS219_H36_DEVICE_APR
                ? h36_apr_cono(state, e)
                : h36_pi_cono(state, e);
        return 1;
    }

    if (fn == 5U) {
        status = h36_internal_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) {
            *out_status = status;
            return 1;
        }
        status = device == HHS_EXACT_PASS219_H36_DEVICE_APR
            ? hhs_exact_pass219_h36_apr_status(state, &status_word)
            : hhs_exact_pass219_h36_pi_status(state, &status_word);
        if (status == HHS_EXACT_STATUS_OK)
            state->memory[e] = status_word;
        *out_status = status;
        return 1;
    }

    if (fn == 6U || fn == 7U) {
        *out_status = h36_internal_conditions(
            state, device, fn, e);
        return 1;
    }

    state->trap = HHS_EXACT_PASS219_H36_TRAP_LEGACY_IO;
    *out_status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return 1;
}

#undef H36_INT_BIT

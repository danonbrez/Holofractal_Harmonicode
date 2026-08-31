/*
 * KA10 standard console/paper-tape peripheral devices.
 * Device state is emulator-local and never carries canonical HHS authority.
 */

#define H36_DEV_BIT(n) (UINT64_C(1) << (35U - (n)))
#define H36_DEV_XWD_ONE_ONE ((UINT64_C(1) << 18U) | UINT64_C(1))

static HHSExactStatus h36_device_memory(
    HHSExactPass219H36VMStateV1 *state,
    uint32_t address
) {
    if (address >= HHS_EXACT_PASS219_H36_WORD_COUNT) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_RANGE;
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    return HHS_EXACT_STATUS_OK;
}

static uint64_t h36_device_add_both(uint64_t word) {
    return (word + H36_DEV_XWD_ONE_ONE) &
           HHS_EXACT_PASS219_H36_WORD_MASK;
}

static uint32_t h36_device_left18(uint64_t word) {
    return (uint32_t)((word >> 18U) &
                      HHS_EXACT_PASS219_H36_HALF_MASK);
}

static uint32_t h36_device_right18(uint64_t word) {
    return (uint32_t)(word & HHS_EXACT_PASS219_H36_HALF_MASK);
}

static void h36_device_request_pi(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t channel
) {
    if (channel >= 1U && channel <= HHS_EXACT_PASS219_H36_PI_CHANNELS) {
        state->legacy_priority_request_mask =
            (uint8_t)(state->legacy_priority_request_mask |
                      (uint8_t)(1U << (channel - 1U)));
    }
}

static uint64_t h36_tty_status(
    const HHSExactPass219H36VMStateV1 *state
) {
    uint64_t status = (uint64_t)(state->tty_pi_channel & 7U);
    if (state->tty_test) status |= H36_DEV_BIT(24U);
    if (state->tty_input_busy) status |= H36_DEV_BIT(29U);
    if (state->tty_input_done) status |= H36_DEV_BIT(30U);
    if (state->tty_output_busy) status |= H36_DEV_BIT(31U);
    if (state->tty_output_done) status |= H36_DEV_BIT(32U);
    return status & HHS_EXACT_PASS219_H36_WORD_MASK;
}

static uint64_t h36_ptr_status(
    const HHSExactPass219H36VMStateV1 *state
) {
    uint64_t status = (uint64_t)(state->ptr_pi_channel & 7U);
    if (state->ptr_tape_present) status |= H36_DEV_BIT(27U);
    if (state->ptr_binary) status |= H36_DEV_BIT(30U);
    if (state->ptr_busy) status |= H36_DEV_BIT(31U);
    if (state->ptr_done) status |= H36_DEV_BIT(32U);
    return status & HHS_EXACT_PASS219_H36_WORD_MASK;
}

static uint64_t h36_ptp_status(
    const HHSExactPass219H36VMStateV1 *state
) {
    uint64_t status = (uint64_t)(state->ptp_pi_channel & 7U);
    if (state->ptp_no_tape) status |= H36_DEV_BIT(29U);
    if (state->ptp_binary) status |= H36_DEV_BIT(30U);
    if (state->ptp_busy) status |= H36_DEV_BIT(31U);
    if (state->ptp_done) status |= H36_DEV_BIT(32U);
    return status & HHS_EXACT_PASS219_H36_WORD_MASK;
}

static void h36_device_sync_io(HHSExactPass219H36VMStateV1 *state) {
    state->io_status[HHS_EXACT_PASS219_H36_DEVICE_TTY] =
        h36_tty_status(state);
    state->io_data[HHS_EXACT_PASS219_H36_DEVICE_TTY] =
        (uint64_t)state->tty_input_buffer;

    state->io_status[HHS_EXACT_PASS219_H36_DEVICE_PTR] =
        h36_ptr_status(state);
    state->io_data[HHS_EXACT_PASS219_H36_DEVICE_PTR] =
        state->ptr_buffer36 & HHS_EXACT_PASS219_H36_WORD_MASK;

    state->io_status[HHS_EXACT_PASS219_H36_DEVICE_PTP] =
        h36_ptp_status(state);
    state->io_data[HHS_EXACT_PASS219_H36_DEVICE_PTP] =
        (uint64_t)state->ptp_buffer8;
}

HHSExactStatus hhs_exact_pass219_h36_tty_feed_input(
    HHSExactPass219H36VMStateV1 *state,
    const uint8_t *bytes,
    size_t count
) {
    size_t i;
    if (state == NULL || (bytes == NULL && count != 0U))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if ((size_t)state->tty_input_count + count >
        HHS_EXACT_PASS219_H36_DEVICE_BUFFER_CAPACITY)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;

    for (i = 0U; i < count; ++i) {
        uint16_t slot = (uint16_t)(
            (state->tty_input_head + state->tty_input_count) %
            HHS_EXACT_PASS219_H36_DEVICE_BUFFER_CAPACITY
        );
        state->tty_input_queue[slot] = bytes[i];
        state->tty_input_count++;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_tty_copy_output(
    const HHSExactPass219H36VMStateV1 *state,
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_count
) {
    if (state == NULL || out_count == NULL ||
        (out_bytes == NULL && capacity != 0U))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (capacity < state->tty_output_count)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    if (state->tty_output_count != 0U)
        memcpy(out_bytes, state->tty_output_queue,
               state->tty_output_count);
    *out_count = state->tty_output_count;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_ptr_load_tape(
    HHSExactPass219H36VMStateV1 *state,
    const uint8_t *frames,
    size_t count
) {
    if (state == NULL || (frames == NULL && count != 0U))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (count > HHS_EXACT_PASS219_H36_DEVICE_BUFFER_CAPACITY)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;

    memset(state->ptr_tape, 0, sizeof(state->ptr_tape));
    if (count != 0U)
        memcpy(state->ptr_tape, frames, count);
    state->ptr_tape_position = 0U;
    state->ptr_tape_count = (uint16_t)count;
    state->ptr_tape_present = (uint8_t)(count != 0U);
    state->ptr_busy = 0U;
    state->ptr_done = 0U;
    state->ptr_buffer36 = 0U;
    h36_device_sync_io(state);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_ptp_copy_tape(
    const HHSExactPass219H36VMStateV1 *state,
    uint8_t *out_frames,
    size_t capacity,
    size_t *out_count
) {
    if (state == NULL || out_count == NULL ||
        (out_frames == NULL && capacity != 0U))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (capacity < state->ptp_tape_count)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    if (state->ptp_tape_count != 0U)
        memcpy(out_frames, state->ptp_tape, state->ptp_tape_count);
    *out_count = state->ptp_tape_count;
    return HHS_EXACT_STATUS_OK;
}

static void h36_tty_step(HHSExactPass219H36VMStateV1 *state) {
    if (state->tty_output_busy != 0U) {
        if (state->tty_test != 0U) {
            state->tty_input_buffer = state->tty_output_buffer;
            state->tty_input_busy = 0U;
            state->tty_input_done = 1U;
            h36_device_request_pi(state, state->tty_pi_channel);
        } else if (state->tty_output_count <
                   HHS_EXACT_PASS219_H36_DEVICE_BUFFER_CAPACITY) {
            state->tty_output_queue[state->tty_output_count++] =
                state->tty_output_buffer;
        }
        state->tty_output_busy = 0U;
        state->tty_output_done = 1U;
        h36_device_request_pi(state, state->tty_pi_channel);
    }

    if (state->tty_input_done == 0U &&
        state->tty_input_count != 0U) {
        state->tty_input_busy = 1U;
        state->tty_input_buffer =
            state->tty_input_queue[state->tty_input_head];
        state->tty_input_head = (uint16_t)(
            (state->tty_input_head + 1U) %
            HHS_EXACT_PASS219_H36_DEVICE_BUFFER_CAPACITY
        );
        state->tty_input_count--;
        state->tty_input_busy = 0U;
        state->tty_input_done = 1U;
        h36_device_request_pi(state, state->tty_pi_channel);
    }
}

static void h36_ptr_step(HHSExactPass219H36VMStateV1 *state) {
    if (state->ptr_busy == 0U)
        return;

    state->ptr_buffer36 = 0U;
    if (state->ptr_binary == 0U) {
        if (state->ptr_tape_position >= state->ptr_tape_count) {
            state->ptr_tape_present = 0U;
            state->ptr_busy = 0U;
            state->ptr_done = 0U;
            return;
        }
        state->ptr_buffer36 =
            state->ptr_tape[state->ptr_tape_position++];
    } else {
        uint8_t gathered = 0U;
        while (state->ptr_tape_position < state->ptr_tape_count &&
               gathered < 6U) {
            uint8_t frame =
                state->ptr_tape[state->ptr_tape_position++];
            if ((frame & UINT8_C(0x80)) == 0U)
                continue;
            state->ptr_buffer36 =
                ((state->ptr_buffer36 << 6U) |
                 (uint64_t)(frame & UINT8_C(0x3F))) &
                HHS_EXACT_PASS219_H36_WORD_MASK;
            gathered++;
        }
        if (gathered != 6U) {
            state->ptr_tape_present = 0U;
            state->ptr_busy = 0U;
            state->ptr_done = 0U;
            state->ptr_buffer36 = 0U;
            return;
        }
    }

    state->ptr_tape_present =
        (uint8_t)(state->ptr_tape_position < state->ptr_tape_count);
    state->ptr_busy = 0U;
    state->ptr_done = 1U;
    h36_device_request_pi(state, state->ptr_pi_channel);
}

static void h36_ptp_step(HHSExactPass219H36VMStateV1 *state) {
    uint8_t frame;
    if (state->ptp_busy == 0U)
        return;

    if (state->ptp_tape_count >=
        HHS_EXACT_PASS219_H36_DEVICE_BUFFER_CAPACITY) {
        state->ptp_no_tape = 1U;
        state->ptp_busy = 0U;
        state->ptp_done = 0U;
        return;
    }

    frame = state->ptp_binary
        ? (uint8_t)(UINT8_C(0x80) |
                    (state->ptp_buffer8 & UINT8_C(0x3F)))
        : state->ptp_buffer8;
    state->ptp_tape[state->ptp_tape_count++] = frame;
    state->ptp_busy = 0U;
    state->ptp_done = 1U;
    h36_device_request_pi(state, state->ptp_pi_channel);
}

HHSExactStatus hhs_exact_pass219_h36_devices_step(
    HHSExactPass219H36VMStateV1 *state
) {
    if (state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    h36_tty_step(state);
    h36_ptr_step(state);
    h36_ptp_step(state);
    h36_device_sync_io(state);
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_device_coni(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t device,
    uint32_t e
) {
    HHSExactStatus status = h36_device_memory(state, e);
    if (status != HHS_EXACT_STATUS_OK) return status;
    h36_device_sync_io(state);
    state->memory[e] = state->io_status[device];
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_device_conditions(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t device,
    uint8_t fn,
    uint32_t e
) {
    uint64_t status;
    h36_device_sync_io(state);
    status = state->io_status[device];
    if (fn == 6U && (status & (uint64_t)e) == 0U)
        state->pc18 = (state->pc18 + 1U) & UINT32_C(0777777);
    if (fn == 7U && (status & (uint64_t)e) != 0U)
        state->pc18 = (state->pc18 + 1U) & UINT32_C(0777777);
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_device_block(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t device,
    uint8_t fn,
    uint32_t e
) {
    uint64_t pointer;
    uint32_t target;
    uint32_t left;
    HHSExactStatus status = h36_device_memory(state, e);
    if (status != HHS_EXACT_STATUS_OK) return status;

    pointer = h36_device_add_both(state->memory[e]);
    state->memory[e] = pointer;
    target = h36_device_right18(pointer);
    left = h36_device_left18(pointer);
    status = h36_device_memory(state, target);
    if (status != HHS_EXACT_STATUS_OK) return status;

    if (fn == 0U) {
        if (device == HHS_EXACT_PASS219_H36_DEVICE_PTP)
            state->memory[target] = 0U;
        else if (device == HHS_EXACT_PASS219_H36_DEVICE_PTR) {
            state->memory[target] = state->ptr_buffer36;
            state->ptr_done = 0U;
            state->ptr_busy = 1U;
        } else {
            state->memory[target] = state->tty_input_buffer;
            state->tty_input_done = 0U;
        }
    } else {
        if (device == HHS_EXACT_PASS219_H36_DEVICE_PTR) {
            /* Reader is input-only. */
        } else if (device == HHS_EXACT_PASS219_H36_DEVICE_PTP) {
            state->ptp_buffer8 =
                (uint8_t)(state->memory[target] & UINT64_C(0xFF));
            state->ptp_done = 0U;
            state->ptp_busy = 1U;
        } else {
            state->tty_output_buffer =
                (uint8_t)(state->memory[target] & UINT64_C(0xFF));
            state->tty_output_done = 0U;
            state->tty_output_busy = 1U;
        }
    }

    if (left != 0U)
        state->pc18 = (state->pc18 + 1U) & UINT32_C(0777777);
    h36_device_sync_io(state);
    return HHS_EXACT_STATUS_OK;
}

static int h36_execute_builtin_device(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e,
    HHSExactStatus *out_status
) {
    HHSExactPass219H36IOInstructionV1 io;
    uint8_t device;
    uint8_t fn;
    HHSExactStatus status;

    if (state == NULL || ins == NULL || out_status == NULL)
        return 0;
    status = hhs_exact_pass219_h36_io_instruction_decode(
        ins->word36, &io);
    if (status != HHS_EXACT_STATUS_OK)
        return 0;

    device = io.device7;
    fn = io.function3;
    if (device != HHS_EXACT_PASS219_H36_DEVICE_TTY &&
        device != HHS_EXACT_PASS219_H36_DEVICE_PTR &&
        device != HHS_EXACT_PASS219_H36_DEVICE_PTP)
        return 0;

    if (fn <= 1U) {
        *out_status = h36_device_block(state, device, fn, e);
        return 1;
    }

    if (fn == 2U) {
        status = h36_device_memory(state, e);
        if (status != HHS_EXACT_STATUS_OK) {
            *out_status = status;
            return 1;
        }
        if (device == HHS_EXACT_PASS219_H36_DEVICE_TTY) {
            state->memory[e] = (uint64_t)state->tty_input_buffer;
            state->tty_input_done = 0U;
        } else if (device == HHS_EXACT_PASS219_H36_DEVICE_PTR) {
            state->memory[e] = state->ptr_buffer36;
            state->ptr_done = 0U;
            state->ptr_busy = 1U;
        } else {
            state->memory[e] = 0U;
        }
        h36_device_sync_io(state);
        *out_status = HHS_EXACT_STATUS_OK;
        return 1;
    }

    if (fn == 3U) {
        status = h36_device_memory(state, e);
        if (status != HHS_EXACT_STATUS_OK) {
            *out_status = status;
            return 1;
        }
        if (device == HHS_EXACT_PASS219_H36_DEVICE_TTY) {
            state->tty_output_buffer =
                (uint8_t)(state->memory[e] & UINT64_C(0xFF));
            state->tty_output_done = 0U;
            state->tty_output_busy = 1U;
        } else if (device == HHS_EXACT_PASS219_H36_DEVICE_PTP) {
            state->ptp_buffer8 =
                (uint8_t)(state->memory[e] & UINT64_C(0xFF));
            state->ptp_done = 0U;
            state->ptp_busy = 1U;
        }
        h36_device_sync_io(state);
        *out_status = HHS_EXACT_STATUS_OK;
        return 1;
    }

    if (fn == 4U) {
        if (device == HHS_EXACT_PASS219_H36_DEVICE_TTY) {
            state->tty_test = (uint8_t)((e & (1U << 11U)) != 0U);
            if ((e & (1U << 10U)) != 0U) state->tty_input_busy = 0U;
            if ((e & (1U << 9U)) != 0U) state->tty_input_done = 0U;
            if ((e & (1U << 8U)) != 0U) state->tty_output_busy = 0U;
            if ((e & (1U << 7U)) != 0U) state->tty_output_done = 0U;
            if ((e & (1U << 6U)) != 0U) state->tty_input_busy = 1U;
            if ((e & (1U << 5U)) != 0U) state->tty_input_done = 1U;
            if ((e & (1U << 4U)) != 0U) state->tty_output_busy = 1U;
            if ((e & (1U << 3U)) != 0U) state->tty_output_done = 1U;
            state->tty_pi_channel = (uint8_t)(e & 7U);
        } else if (device == HHS_EXACT_PASS219_H36_DEVICE_PTR) {
            state->ptr_binary = (uint8_t)((e & (1U << 5U)) != 0U);
            state->ptr_busy = (uint8_t)((e & (1U << 4U)) != 0U);
            state->ptr_done = (uint8_t)((e & (1U << 3U)) != 0U);
            state->ptr_pi_channel = (uint8_t)(e & 7U);
        } else {
            state->ptp_binary = (uint8_t)((e & (1U << 5U)) != 0U);
            state->ptp_busy = (uint8_t)((e & (1U << 4U)) != 0U);
            state->ptp_done = (uint8_t)((e & (1U << 3U)) != 0U);
            state->ptp_pi_channel = (uint8_t)(e & 7U);
        }
        h36_device_sync_io(state);
        *out_status = HHS_EXACT_STATUS_OK;
        return 1;
    }

    if (fn == 5U) {
        *out_status = h36_device_coni(state, device, e);
        return 1;
    }
    if (fn == 6U || fn == 7U) {
        *out_status = h36_device_conditions(state, device, fn, e);
        return 1;
    }

    return 0;
}

#undef H36_DEV_BIT
#undef H36_DEV_XWD_ONE_ONE

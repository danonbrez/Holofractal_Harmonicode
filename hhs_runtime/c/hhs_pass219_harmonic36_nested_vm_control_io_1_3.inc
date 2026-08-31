/*
 * PDP-10 KA10 program-control, pushdown, and generic I/O-bus execution.
 * Canonical HHS authority remains outside this nested VM; I/O device state
 * is an emulator-local register surface and never commits VM81/Hash72.
 */

#define H36_XWD_ONE_ONE ((UINT64_C(1) << 18U) | UINT64_C(1))
#define H36_PC_AROV UINT32_C(0400000)
#define H36_PC_CRY0 UINT32_C(0200000)
#define H36_PC_CRY1 UINT32_C(0100000)
#define H36_PC_FOV  UINT32_C(0040000)
#define H36_PC_USER UINT32_C(0010000)
#define H36_PC_UIOT UINT32_C(0004000)
#define H36_PC_DCK  UINT32_C(0000040)

static uint32_t h36_left18(uint64_t word) {
    return (uint32_t)((word >> 18U) & HHS_EXACT_PASS219_H36_HALF_MASK);
}

static uint32_t h36_right18(uint64_t word) {
    return (uint32_t)(word & HHS_EXACT_PASS219_H36_HALF_MASK);
}

static uint64_t h36_xwd(uint32_t left, uint32_t right) {
    return ((((uint64_t)left) & HHS_EXACT_PASS219_H36_HALF_MASK) << 18U) |
           (((uint64_t)right) & HHS_EXACT_PASS219_H36_HALF_MASK);
}

static uint64_t h36_add_both(uint64_t word) {
    return (word + H36_XWD_ONE_ONE) &
           HHS_EXACT_PASS219_H36_WORD_MASK;
}

static uint64_t h36_sub_both(uint64_t word) {
    return (word - H36_XWD_ONE_ONE) &
           HHS_EXACT_PASS219_H36_WORD_MASK;
}

static uint32_t h36_pc_flags_left18(
    const HHSExactPass219H36VMStateV1 *state
) {
    uint32_t flags = 0U;
    if (state->legacy_overflow != 0U) flags |= H36_PC_AROV;
    if (state->legacy_carry0 != 0U) flags |= H36_PC_CRY0;
    if (state->legacy_carry1 != 0U) flags |= H36_PC_CRY1;
    if (state->legacy_floating_overflow != 0U) flags |= H36_PC_FOV;
    if (state->legacy_user_mode != 0U) flags |= H36_PC_USER;
    if (state->legacy_user_io != 0U) flags |= H36_PC_UIOT;
    if (state->legacy_no_divide != 0U) flags |= H36_PC_DCK;
    return flags & (uint32_t)HHS_EXACT_PASS219_H36_HALF_MASK;
}

static uint64_t h36_pc_word(
    const HHSExactPass219H36VMStateV1 *state
) {
    return h36_xwd(h36_pc_flags_left18(state), state->pc18);
}

static int h36_selected_flags_active(
    const HHSExactPass219H36VMStateV1 *state,
    uint8_t selector
) {
    if ((selector & 8U) != 0U && state->legacy_overflow != 0U) return 1;
    if ((selector & 4U) != 0U && state->legacy_carry0 != 0U) return 1;
    if ((selector & 2U) != 0U && state->legacy_carry1 != 0U) return 1;
    if ((selector & 1U) != 0U &&
        state->legacy_floating_overflow != 0U) return 1;
    return 0;
}

static void h36_clear_selected_flags(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t selector
) {
    if ((selector & 8U) != 0U) state->legacy_overflow = 0U;
    if ((selector & 4U) != 0U) state->legacy_carry0 = 0U;
    if ((selector & 2U) != 0U) state->legacy_carry1 = 0U;
    if ((selector & 1U) != 0U) state->legacy_floating_overflow = 0U;
}

HHSExactStatus hhs_exact_pass219_h36_io_instruction_encode(
    uint8_t device7,
    uint8_t function3,
    uint8_t indirect1,
    uint8_t index4,
    uint32_t address18,
    uint64_t *out_word36
) {
    if (out_word36 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (device7 >= HHS_EXACT_PASS219_H36_IO_DEVICE_COUNT ||
        function3 > 7U || indirect1 > 1U || index4 > 15U ||
        address18 > UINT32_C(0777777))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    *out_word36 =
        (UINT64_C(7) << 33U) |
        ((uint64_t)device7 << 26U) |
        ((uint64_t)function3 << 23U) |
        ((uint64_t)indirect1 << 22U) |
        ((uint64_t)index4 << 18U) |
        (uint64_t)address18;
    *out_word36 &= HHS_EXACT_PASS219_H36_WORD_MASK;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_io_instruction_decode(
    uint64_t word36,
    HHSExactPass219H36IOInstructionV1 *out
) {
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if ((word36 & ~HHS_EXACT_PASS219_H36_WORD_MASK) != 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (((word36 >> 33U) & UINT64_C(7)) != UINT64_C(7))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out, 0, sizeof(*out));
    out->word36 = word36;
    out->device7 = (uint8_t)((word36 >> 26U) & UINT64_C(0177));
    out->function3 = (uint8_t)((word36 >> 23U) & UINT64_C(07));
    out->indirect1 = (uint8_t)((word36 >> 22U) & UINT64_C(01));
    out->index4 = (uint8_t)((word36 >> 18U) & UINT64_C(017));
    out->address18 =
        (uint32_t)(word36 & HHS_EXACT_PASS219_H36_HALF_MASK);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_io_device_set(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t device7,
    uint64_t status36,
    uint64_t data36
) {
    if (state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (device7 >= HHS_EXACT_PASS219_H36_IO_DEVICE_COUNT ||
        (status36 & ~HHS_EXACT_PASS219_H36_WORD_MASK) != 0U ||
        (data36 & ~HHS_EXACT_PASS219_H36_WORD_MASK) != 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    state->io_status[device7] = status36;
    state->io_data[device7] = data36;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_io_device_get(
    const HHSExactPass219H36VMStateV1 *state,
    uint8_t device7,
    uint64_t *out_status36,
    uint64_t *out_data36
) {
    if (state == NULL || out_status36 == NULL || out_data36 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (device7 >= HHS_EXACT_PASS219_H36_IO_DEVICE_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    *out_status36 = state->io_status[device7];
    *out_data36 = state->io_data[device7];
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_execute_blt(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t ac,
    uint32_t e
) {
    uint32_t source = h36_left18(state->accumulators[ac]);
    uint32_t destination = h36_right18(state->accumulators[ac]);
    uint32_t count;
    uint32_t i;

    if (destination > e)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    count = e - destination + 1U;
    if (source >= HHS_EXACT_PASS219_H36_WORD_COUNT ||
        destination >= HHS_EXACT_PASS219_H36_WORD_COUNT ||
        e >= HHS_EXACT_PASS219_H36_WORD_COUNT ||
        source + count > HHS_EXACT_PASS219_H36_WORD_COUNT) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_RANGE;
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }

    state->accumulators[ac] = h36_xwd(
        source + count, destination + count);
    for (i = 0U; i < count; ++i)
        state->memory[destination + i] = state->memory[source + i];
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_execute_pushdown(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e
) {
    uint8_t ac = ins->accumulator4;
    uint16_t op = ins->opcode9;
    uint64_t pointer = state->accumulators[ac];
    uint32_t stack_address;
    HHSExactStatus status;

    if (op == UINT16_C(0260) || op == UINT16_C(0261)) {
        pointer = h36_add_both(pointer);
        state->accumulators[ac] = pointer;
        if (h36_left18(pointer) == 0U)
            state->legacy_pushdown_overflow = 1U;
        stack_address = h36_right18(pointer);
        status = h36_legacy_memory_required(state, stack_address);
        if (status != HHS_EXACT_STATUS_OK) return status;

        if (op == UINT16_C(0260)) {
            state->memory[stack_address] = h36_pc_word(state);
            state->pc18 = e;
        } else {
            status = h36_legacy_memory_required(state, e);
            if (status != HHS_EXACT_STATUS_OK) return status;
            state->memory[stack_address] = state->memory[e];
        }
        return HHS_EXACT_STATUS_OK;
    }

    stack_address = h36_right18(pointer);
    status = h36_legacy_memory_required(state, stack_address);
    if (status != HHS_EXACT_STATUS_OK) return status;

    if (op == UINT16_C(0262)) {
        status = h36_legacy_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        state->memory[e] = state->memory[stack_address];
    } else if (op == UINT16_C(0263)) {
        state->pc18 = h36_right18(state->memory[stack_address]);
    } else {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    pointer = h36_sub_both(pointer);
    state->accumulators[ac] = pointer;
    if (h36_left18(pointer) == UINT32_C(0777777))
        state->legacy_pushdown_overflow = 1U;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_execute_subroutine(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e
) {
    uint16_t op = ins->opcode9;
    uint8_t ac = ins->accumulator4;
    HHSExactStatus status;

    if (op == UINT16_C(0264)) {
        status = h36_legacy_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        state->memory[e] = h36_pc_word(state);
        state->pc18 = (e + 1U) & UINT32_C(0777777);
        return HHS_EXACT_STATUS_OK;
    }
    if (op == UINT16_C(0265)) {
        state->accumulators[ac] = h36_pc_word(state);
        state->pc18 = e;
        return HHS_EXACT_STATUS_OK;
    }
    if (op == UINT16_C(0266)) {
        status = h36_legacy_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        {
            uint64_t old_ac = state->accumulators[ac];
            state->memory[e] = old_ac;
            state->accumulators[ac] = h36_xwd(e, state->pc18);
        }
        state->pc18 = (e + 1U) & UINT32_C(0777777);
        return HHS_EXACT_STATUS_OK;
    }
    if (op == UINT16_C(0267)) {
        uint32_t restore_address = h36_left18(state->accumulators[ac]);
        status = h36_legacy_memory_required(state, restore_address);
        if (status != HHS_EXACT_STATUS_OK) return status;
        state->accumulators[ac] = state->memory[restore_address];
        state->pc18 = e;
        return HHS_EXACT_STATUS_OK;
    }
    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

static HHSExactStatus h36_execute_io(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e
) {
    HHSExactPass219H36IOInstructionV1 io;
    uint8_t device;
    uint8_t fn;
    HHSExactStatus status;

    status = hhs_exact_pass219_h36_io_instruction_decode(ins->word36, &io);
    if (status != HHS_EXACT_STATUS_OK) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_LEGACY_IO;
        return status;
    }
    device = io.device7;
    fn = io.function3;

    state->legacy_last_io_interrupt_cycle =
        state->legacy_interrupt_cycle;
    if (state->legacy_user_mode != 0U &&
        state->legacy_user_io == 0U) {
        state->legacy_user_io_trap = 1U;
        if (state->legacy_uuo_mode ==
            HHS_EXACT_PASS219_H36_UUO_MODE_KA10_HISTORICAL) {
            return h36_ka10_uuo_dispatch(
                state,
                ins,
                e,
                HHS_EXACT_PASS219_H36_UUO_CLASS_IO_RESTRICTION,
                0U
            );
        }
        state->trap = HHS_EXACT_PASS219_H36_TRAP_LEGACY_PRIVILEGE;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (h36_execute_builtin_device(state, ins, e, &status))
        return status;

    if (fn == 0U || fn == 1U) {
        uint64_t pointer;
        uint32_t target;
        uint32_t left;
        status = h36_legacy_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        pointer = h36_add_both(state->memory[e]);
        state->memory[e] = pointer;
        target = h36_right18(pointer);
        left = h36_left18(pointer);
        status = h36_legacy_memory_required(state, target);
        if (status != HHS_EXACT_STATUS_OK) return status;
        if (fn == 0U)
            state->memory[target] = state->io_data[device];
        else
            state->io_data[device] = state->memory[target];
        if (left != 0U)
            state->pc18 = (state->pc18 + 1U) & UINT32_C(0777777);
        return HHS_EXACT_STATUS_OK;
    }

    if (fn == 2U) {
        status = h36_legacy_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        state->memory[e] = state->io_data[device];
        return HHS_EXACT_STATUS_OK;
    }
    if (fn == 3U) {
        status = h36_legacy_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        state->io_data[device] = state->memory[e];
        return HHS_EXACT_STATUS_OK;
    }
    if (fn == 4U) {
        state->io_status[device] =
            ((uint64_t)e) & HHS_EXACT_PASS219_H36_HALF_MASK;
        return HHS_EXACT_STATUS_OK;
    }
    if (fn == 5U) {
        status = h36_legacy_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        state->memory[e] = state->io_status[device];
        return HHS_EXACT_STATUS_OK;
    }
    if (fn == 6U) {
        if ((state->io_status[device] & (uint64_t)e) == 0U)
            state->pc18 = (state->pc18 + 1U) & UINT32_C(0777777);
        return HHS_EXACT_STATUS_OK;
    }
    if (fn == 7U) {
        if ((state->io_status[device] & (uint64_t)e) != 0U)
            state->pc18 = (state->pc18 + 1U) & UINT32_C(0777777);
        return HHS_EXACT_STATUS_OK;
    }

    state->trap = HHS_EXACT_PASS219_H36_TRAP_LEGACY_IO;
    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

static int h36_execute_legacy_control_io(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e,
    HHSExactStatus *out_status
) {
    uint16_t op = ins->opcode9;
    uint8_t ac = ins->accumulator4;
    if (out_status == NULL) return 0;

    if (op == UINT16_C(0251)) {
        *out_status = h36_execute_blt(state, ac, e);
        return 1;
    }
    if (op == UINT16_C(0252) || op == UINT16_C(0253)) {
        state->accumulators[ac] = h36_add_both(state->accumulators[ac]);
        if ((op == UINT16_C(0252) &&
             h36_signed(state->accumulators[ac]) >= 0) ||
            (op == UINT16_C(0253) &&
             h36_signed(state->accumulators[ac]) < 0))
            state->pc18 = e;
        *out_status = HHS_EXACT_STATUS_OK;
        return 1;
    }
    if (op == UINT16_C(0254)) {
        *out_status = h36_priv_execute_jrst(state, ins);
        return 1;
    }
    if (op == UINT16_C(0255)) {
        if (h36_selected_flags_active(state, ac)) {
            h36_clear_selected_flags(state, ac);
            state->pc18 = e;
        }
        *out_status = HHS_EXACT_STATUS_OK;
        return 1;
    }
    if (op == UINT16_C(0247) || op == UINT16_C(0257)) {
        *out_status = h36_priv_execute_special_system(state, op);
        return 1;
    }
    if (op >= UINT16_C(0260) && op <= UINT16_C(0263)) {
        *out_status = h36_execute_pushdown(state, ins, e);
        return 1;
    }
    if (op >= UINT16_C(0264) && op <= UINT16_C(0267)) {
        *out_status = h36_execute_subroutine(state, ins, e);
        return 1;
    }
    if (op >= UINT16_C(0700)) {
        *out_status = h36_execute_io(state, ins, e);
        return 1;
    }
    return 0;
}

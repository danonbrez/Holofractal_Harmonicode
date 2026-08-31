/*
 * KA10 privilege/JRST/priority-interrupt compatibility membrane.
 * All state here is emulator-local and carries no HHS canonical authority.
 */

#define H36_PRIV_PC_AROV UINT32_C(0400000)
#define H36_PRIV_PC_CRY0 UINT32_C(0200000)
#define H36_PRIV_PC_CRY1 UINT32_C(0100000)
#define H36_PRIV_PC_FOV  UINT32_C(0040000)
#define H36_PRIV_PC_USER UINT32_C(0010000)
#define H36_PRIV_PC_UIOT UINT32_C(0004000)
#define H36_PRIV_PC_DCK  UINT32_C(0000040)

static uint32_t h36_priv_left18(uint64_t word) {
    return (uint32_t)(
        (word >> 18U) & HHS_EXACT_PASS219_H36_HALF_MASK
    );
}

static uint64_t h36_priv_xwd(uint32_t left, uint32_t right) {
    return (
        (((uint64_t)left & HHS_EXACT_PASS219_H36_HALF_MASK) << 18U) |
        ((uint64_t)right & HHS_EXACT_PASS219_H36_HALF_MASK)
    ) & HHS_EXACT_PASS219_H36_WORD_MASK;
}

static uint32_t h36_priv_pc_flags_left18(
    const HHSExactPass219H36VMStateV1 *state
) {
    uint32_t flags = 0U;
    if (state->legacy_overflow != 0U) flags |= H36_PRIV_PC_AROV;
    if (state->legacy_carry0 != 0U) flags |= H36_PRIV_PC_CRY0;
    if (state->legacy_carry1 != 0U) flags |= H36_PRIV_PC_CRY1;
    if (state->legacy_floating_overflow != 0U) flags |= H36_PRIV_PC_FOV;
    if (state->legacy_user_mode != 0U) flags |= H36_PRIV_PC_USER;
    if (state->legacy_user_io != 0U) flags |= H36_PRIV_PC_UIOT;
    if (state->legacy_no_divide != 0U) flags |= H36_PRIV_PC_DCK;
    return flags & (uint32_t)HHS_EXACT_PASS219_H36_HALF_MASK;
}

static uint64_t h36_priv_pc_word(
    const HHSExactPass219H36VMStateV1 *state
) {
    return h36_priv_xwd(
        h36_priv_pc_flags_left18(state),
        state->pc18
    );
}

static void h36_priv_restore_flags(
    HHSExactPass219H36VMStateV1 *state,
    uint32_t flags_left18
) {
    uint8_t was_user = state->legacy_user_mode;
    uint8_t old_user_io = state->legacy_user_io;

    state->legacy_overflow =
        (uint8_t)((flags_left18 & H36_PRIV_PC_AROV) != 0U);
    state->legacy_carry0 =
        (uint8_t)((flags_left18 & H36_PRIV_PC_CRY0) != 0U);
    state->legacy_carry1 =
        (uint8_t)((flags_left18 & H36_PRIV_PC_CRY1) != 0U);
    state->legacy_floating_overflow =
        (uint8_t)((flags_left18 & H36_PRIV_PC_FOV) != 0U);
    state->legacy_no_divide =
        (uint8_t)((flags_left18 & H36_PRIV_PC_DCK) != 0U);

    if (was_user != 0U) {
        state->legacy_user_mode = 1U;
        if ((flags_left18 & H36_PRIV_PC_UIOT) == 0U)
            state->legacy_user_io = 0U;
        else
            state->legacy_user_io = old_user_io;
    } else {
        state->legacy_user_mode =
            (uint8_t)((flags_left18 & H36_PRIV_PC_USER) != 0U);
        state->legacy_user_io =
            (uint8_t)((flags_left18 & H36_PRIV_PC_UIOT) != 0U);
    }
}

static HHSExactStatus h36_priv_jrst_effective_address(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t *out_e,
    uint32_t *out_flags_left18
) {
    uint32_t y;
    uint8_t indirect;
    uint8_t index;
    uint32_t depth = 0U;
    int used_indirection = 0;
    uint32_t last_flags = 0U;

    if (state == NULL || ins == NULL ||
        out_e == NULL || out_flags_left18 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    y = ins->address18;
    indirect = ins->indirect1;
    index = ins->index4;

    if (indirect == 0U) {
        uint32_t e = y;
        if (index != 0U) {
            e = (
                e +
                (uint32_t)(
                    state->accumulators[index] &
                    HHS_EXACT_PASS219_H36_HALF_MASK
                )
            ) & UINT32_C(0777777);
            last_flags = h36_priv_left18(state->accumulators[index]);
        } else {
            last_flags = h36_priv_left18(ins->word36);
        }
        *out_e = e;
        *out_flags_left18 = last_flags;
        return HHS_EXACT_STATUS_OK;
    }

    while (1) {
        uint32_t e = y;
        HHSExactPass219H36InstructionV1 pointer;
        HHSExactStatus status;

        if (index != 0U) {
            e = (
                e +
                (uint32_t)(
                    state->accumulators[index] &
                    HHS_EXACT_PASS219_H36_HALF_MASK
                )
            ) & UINT32_C(0777777);
        }

        if (e >= HHS_EXACT_PASS219_H36_WORD_COUNT) {
            state->trap = HHS_EXACT_PASS219_H36_TRAP_RANGE;
            return HHS_EXACT_STATUS_RANGE_ERROR;
        }
        if (++depth > 32U) {
            state->trap = HHS_EXACT_PASS219_H36_TRAP_INDIRECT_LIMIT;
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }

        used_indirection = 1;
        last_flags = h36_priv_left18(state->memory[e]);
        status = hhs_exact_pass219_h36_instruction_decode(
            state->memory[e], &pointer
        );
        if (status != HHS_EXACT_STATUS_OK)
            return status;

        y = pointer.address18;
        indirect = pointer.indirect1;
        index = pointer.index4;

        if (indirect == 0U) {
            uint32_t final_e = y;
            if (index != 0U) {
                final_e = (
                    final_e +
                    (uint32_t)(
                        state->accumulators[index] &
                        HHS_EXACT_PASS219_H36_HALF_MASK
                    )
                ) & UINT32_C(0777777);
            }
            *out_e = final_e;
            *out_flags_left18 = last_flags;
            return used_indirection != 0
                ? HHS_EXACT_STATUS_OK
                : HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }
}

static void h36_priv_priority_dismiss(
    HHSExactPass219H36VMStateV1 *state
) {
    uint8_t channel = state->legacy_priority_active_channel;
    uint8_t next = 0U;
    uint8_t i;

    if (channel != 0U && channel <= HHS_EXACT_PASS219_H36_PI_CHANNELS) {
        uint8_t bit = (uint8_t)(1U << (channel - 1U));
        state->legacy_priority_active_mask =
            (uint8_t)(state->legacy_priority_active_mask & ~bit);
    }

    for (i = 1U; i <= HHS_EXACT_PASS219_H36_PI_CHANNELS; ++i) {
        uint8_t bit = (uint8_t)(1U << (i - 1U));
        if ((state->legacy_priority_active_mask & bit) != 0U) {
            next = i;
            break;
        }
    }

    state->legacy_priority_active_channel = next;
    state->legacy_interrupt_cycle = (uint8_t)(next != 0U);
}

HHSExactStatus hhs_exact_pass219_h36_priority_enable_mask(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t enabled_mask7
) {
    if (state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if ((enabled_mask7 & UINT8_C(0x80)) != 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    state->legacy_priority_enabled_mask = enabled_mask7;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_priority_request(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t channel1_7,
    uint32_t vector18
) {
    uint8_t bit;
    if (state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (channel1_7 == 0U ||
        channel1_7 > HHS_EXACT_PASS219_H36_PI_CHANNELS ||
        vector18 > UINT32_C(0777777))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    bit = (uint8_t)(1U << (channel1_7 - 1U));
    state->legacy_priority_vector18[channel1_7 - 1U] = vector18;
    state->legacy_priority_request_mask =
        (uint8_t)(state->legacy_priority_request_mask | bit);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_priority_enter(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t *out_channel1_7
) {
    uint8_t pending;
    uint8_t current;
    uint8_t chosen = 0U;
    uint8_t i;

    if (state == NULL || out_channel1_7 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    pending = (uint8_t)(
        state->legacy_priority_request_mask &
        state->legacy_priority_enabled_mask &
        UINT8_C(0x7F)
    );
    current = state->legacy_priority_active_channel;

    for (i = 1U; i <= HHS_EXACT_PASS219_H36_PI_CHANNELS; ++i) {
        uint8_t bit = (uint8_t)(1U << (i - 1U));
        if ((pending & bit) == 0U)
            continue;
        if (current != 0U && i >= current)
            continue;
        chosen = i;
        break;
    }

    *out_channel1_7 = chosen;
    if (chosen == 0U)
        return HHS_EXACT_STATUS_OK;

    {
        uint8_t bit = (uint8_t)(1U << (chosen - 1U));
        state->legacy_priority_saved_pc_word[chosen - 1U] =
            h36_priv_pc_word(state);
        state->legacy_priority_request_mask =
            (uint8_t)(state->legacy_priority_request_mask & ~bit);
        state->legacy_priority_active_mask =
            (uint8_t)(state->legacy_priority_active_mask | bit);
        state->legacy_priority_active_channel = chosen;
        state->legacy_interrupt_cycle = 1U;
        state->legacy_user_mode = 0U;
        state->legacy_user_io = 0U;
        state->pc18 = state->legacy_priority_vector18[chosen - 1U];
    }
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_priv_execute_jrst(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins
) {
    uint8_t selector = ins->accumulator4;
    uint32_t e;
    uint32_t flags;
    HHSExactStatus status;

    status = h36_priv_jrst_effective_address(
        state, ins, &e, &flags
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (state->legacy_user_mode != 0U &&
        ((selector & UINT8_C(04)) != 0U ||
         (selector & UINT8_C(010)) != 0U)) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_LEGACY_PRIVILEGE;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if ((selector & UINT8_C(010)) != 0U)
        h36_priv_priority_dismiss(state);

    if ((selector & UINT8_C(02)) != 0U)
        h36_priv_restore_flags(state, flags);

    if ((selector & UINT8_C(01)) != 0U)
        state->legacy_user_mode = 1U;

    state->pc18 = e;

    if ((selector & UINT8_C(04)) != 0U)
        state->halted = 1U;

    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_priv_execute_special_system(
    HHSExactPass219H36VMStateV1 *state,
    uint16_t opcode
) {
    if (state->legacy_special_hardware_present != 0U) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_UNIMPLEMENTED_OPCODE;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (opcode == UINT16_C(0247)) {
        state->legacy_special_247_seen = 1U;
        return HHS_EXACT_STATUS_OK;
    }
    if (opcode == UINT16_C(0257)) {
        state->legacy_special_257_seen = 1U;
        return HHS_EXACT_STATUS_OK;
    }
    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

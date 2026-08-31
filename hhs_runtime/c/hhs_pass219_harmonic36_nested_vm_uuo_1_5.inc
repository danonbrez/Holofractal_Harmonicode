/*
 * KA10 historical UUO compatibility membrane.
 *
 * This mode is explicit because HHS uses the same 001-077 opcode space for
 * its nested harmonic microkernel.  Historical KA10 mode never changes HHS
 * VM81/Hash72/persistence authority.
 */

#define H36_KA10_LUUO_WORD UINT32_C(040)
#define H36_KA10_LUUO_EXEC UINT32_C(041)
#define H36_KA10_UNASSIGNED_WORD UINT32_C(060)
#define H36_KA10_UNASSIGNED_EXEC UINT32_C(061)

static HHSExactStatus h36_execute(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t depth
);

static uint64_t h36_ka10_uuo_word(
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e
) {
    uint64_t word =
        ((uint64_t)ins->opcode9 << 27U) |
        ((uint64_t)ins->accumulator4 << 23U) |
        ((uint64_t)e & HHS_EXACT_PASS219_H36_HALF_MASK);
    return word & HHS_EXACT_PASS219_H36_WORD_MASK;
}

HHSExactStatus hhs_exact_pass219_h36_legacy_uuo_mode_set(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t mode
) {
    if (state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (mode != HHS_EXACT_PASS219_H36_UUO_MODE_HHS_MICROKERNEL &&
        mode != HHS_EXACT_PASS219_H36_UUO_MODE_KA10_HISTORICAL)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    state->legacy_uuo_mode = mode;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_ka10_uuo_dispatch(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e,
    uint8_t uuo_class,
    uint32_t depth
) {
    uint32_t vector_word;
    uint32_t vector_exec;
    HHSExactPass219H36InstructionV1 handler;
    HHSExactStatus status;

    if (state == NULL || ins == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (state->legacy_uuo_mode !=
        HHS_EXACT_PASS219_H36_UUO_MODE_KA10_HISTORICAL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (depth > 32U) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_INDIRECT_LIMIT;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (uuo_class == HHS_EXACT_PASS219_H36_UUO_CLASS_UNASSIGNED) {
        vector_word = H36_KA10_UNASSIGNED_WORD;
        vector_exec = H36_KA10_UNASSIGNED_EXEC;
    } else if (
        uuo_class == HHS_EXACT_PASS219_H36_UUO_CLASS_LUUO ||
        uuo_class == HHS_EXACT_PASS219_H36_UUO_CLASS_MUUO ||
        uuo_class == HHS_EXACT_PASS219_H36_UUO_CLASS_IO_RESTRICTION
    ) {
        vector_word = H36_KA10_LUUO_WORD;
        vector_exec = H36_KA10_LUUO_EXEC;
    } else {
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }

    if (vector_exec >= HHS_EXACT_PASS219_H36_WORD_COUNT) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_RANGE;
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }

    state->legacy_uuo_instruction_word = h36_ka10_uuo_word(ins, e);
    state->memory[vector_word] = state->legacy_uuo_instruction_word;
    state->legacy_uuo_saved_pc_word = h36_priv_pc_word(state);
    state->legacy_uuo_last_class = uuo_class;
    state->legacy_uuo_last_vector18 = vector_word;
    state->legacy_uuo_dispatch_count =
        (uint16_t)(state->legacy_uuo_dispatch_count + 1U);

    /*
     * KA10 MUUOs, unassigned instructions, and I/O restrictions transfer
     * into monitor/executive handling.  A user LUUO remains local to the
     * user's virtual 40/41 pair; this bounded VM has one 144-word image, so
     * the same numeric pair is used while preserving the user-mode witness.
     */
    if (uuo_class != HHS_EXACT_PASS219_H36_UUO_CLASS_LUUO) {
        state->legacy_user_mode = 0U;
        state->legacy_user_io = 0U;
    }

    status = hhs_exact_pass219_h36_instruction_decode(
        state->memory[vector_exec], &handler
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return h36_execute(state, &handler, depth + 1U);
}

static int h36_ka10_should_dispatch_uuo(
    const HHSExactPass219H36VMStateV1 *state,
    uint16_t opcode,
    uint8_t *out_class
) {
    if (state == NULL || out_class == NULL)
        return 0;
    if (state->legacy_uuo_mode !=
        HHS_EXACT_PASS219_H36_UUO_MODE_KA10_HISTORICAL)
        return 0;

    if (opcode >= UINT16_C(0001) && opcode <= UINT16_C(0037)) {
        *out_class = HHS_EXACT_PASS219_H36_UUO_CLASS_LUUO;
        return 1;
    }
    if (opcode == UINT16_C(0000) ||
        (opcode >= UINT16_C(0040) && opcode <= UINT16_C(0077))) {
        *out_class = HHS_EXACT_PASS219_H36_UUO_CLASS_MUUO;
        return 1;
    }
    if (opcode >= UINT16_C(0100) && opcode <= UINT16_C(0127)) {
        *out_class = HHS_EXACT_PASS219_H36_UUO_CLASS_UNASSIGNED;
        return 1;
    }
    return 0;
}

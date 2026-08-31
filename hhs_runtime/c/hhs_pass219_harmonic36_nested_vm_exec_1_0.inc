static HHSExactStatus h36_memory_required(
    HHSExactPass219H36VMStateV1 *state,
    uint32_t address
) {
    if (address >= HHS_EXACT_PASS219_H36_WORD_COUNT) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_RANGE;
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    return HHS_EXACT_STATUS_OK;
}

static uint64_t h36_move_transform(uint16_t opcode, uint64_t value) {
    uint16_t family = (uint16_t)(opcode & UINT16_C(0774));
    uint64_t v = value & HHS_EXACT_PASS219_H36_WORD_MASK;
    if (family == UINT16_C(0204)) {
        return ((v & HHS_EXACT_PASS219_H36_HALF_MASK) << 18U) |
               ((v >> 18U) & HHS_EXACT_PASS219_H36_HALF_MASK);
    }
    if (family == UINT16_C(0210))
        return h36_wrap_i64(-h36_signed(v));
    if (family == UINT16_C(0214)) {
        int64_t s = h36_signed(v);
        return h36_wrap_i64(s < 0 ? -s : s);
    }
    return v;
}

static HHSExactStatus h36_execute(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t depth
) {
    uint16_t op = ins->opcode9;
    uint8_t ac = ins->accumulator4;
    uint32_t e = 0U;
    HHSExactStatus status;

    if (depth > 32U) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_INDIRECT_LIMIT;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    status = h36_effective_address(state, ins, &e);
    if (status != HHS_EXACT_STATUS_OK) return status;
    state->last_effective_address18 = e;
    state->last_opcode9 = op;

    if (op < UINT16_C(0100)) {
        if (op == UINT16_C(0001)) {
            uint64_t request = state->accumulators[ac];
            uint16_t rule = (uint16_t)(request & UINT64_C(0xFF));
            uint8_t tonic = (uint8_t)((request >> 8U) & UINT64_C(0x0F));
            uint32_t destination =
                (uint32_t)((request >> 12U) & UINT64_C(0xFF));
            uint64_t rendered;
            if (destination >= HHS_EXACT_PASS219_H36_WORD_COUNT) {
                state->trap = HHS_EXACT_PASS219_H36_TRAP_RANGE;
                return HHS_EXACT_STATUS_RANGE_ERROR;
            }
            status = hhs_exact_pass219_h36_harmonic_render(
                rule, tonic, &rendered);
            if (status != HHS_EXACT_STATUS_OK) {
                state->trap = HHS_EXACT_PASS219_H36_TRAP_HARMONIC_RULE;
                return status;
            }
            state->memory[destination] = rendered;
            return HHS_EXACT_STATUS_OK;
        }
        if (op == UINT16_C(0002)) {
            uint64_t transposed;
            status = h36_memory_required(state, e);
            if (status != HHS_EXACT_STATUS_OK) return status;
            status = hhs_exact_pass219_h36_harmonic_transpose(
                state->memory[e],
                (uint8_t)(state->accumulators[ac] & UINT64_C(0x0F)),
                &transposed);
            if (status != HHS_EXACT_STATUS_OK) {
                state->trap = HHS_EXACT_PASS219_H36_TRAP_HARMONIC_RULE;
                return status;
            }
            state->memory[e] = transposed;
            return HHS_EXACT_STATUS_OK;
        }
        if (op == UINT16_C(0003)) {
            uint32_t source =
                (uint32_t)(state->accumulators[ac] & UINT64_C(0xFF));
            HHSExactPass219H36HarmonicTransitionV1 t;
            uint64_t packed;
            if (source >= HHS_EXACT_PASS219_H36_WORD_COUNT) {
                state->trap = HHS_EXACT_PASS219_H36_TRAP_RANGE;
                return HHS_EXACT_STATUS_RANGE_ERROR;
            }
            status = h36_memory_required(state, e);
            if (status != HHS_EXACT_STATUS_OK) return status;
            status = hhs_exact_pass219_h36_harmonic_transition(
                state->memory[source], state->memory[e], &t);
            if (status != HHS_EXACT_STATUS_OK) {
                state->trap = HHS_EXACT_PASS219_H36_TRAP_HARMONIC_RULE;
                return status;
            }
            packed =
                ((uint64_t)(t.common_tones & UINT16_C(0x3F))) |
                ((uint64_t)(t.semitone_resolutions & UINT16_C(0x3F)) << 6U) |
                ((uint64_t)(t.exact_voice_leading_cost & UINT16_C(0x0FFF))
                    << 12U) |
                ((uint64_t)(t.source_pitch_count & UINT16_C(0x3F)) << 24U) |
                ((uint64_t)(t.target_pitch_count & UINT16_C(0x3F)) << 30U);
            state->accumulators[ac] =
                packed & HHS_EXACT_PASS219_H36_WORD_MASK;
            return HHS_EXACT_STATUS_OK;
        }
        if (op == UINT16_C(0004)) {
            HHSExactPass219H36CoordinateV1 c;
            uint64_t packed;
            if (e >= HHS_EXACT_PASS219_H36_FRAME_BITS) {
                state->trap = HHS_EXACT_PASS219_H36_TRAP_RANGE;
                return HHS_EXACT_STATUS_RANGE_ERROR;
            }
            status = hhs_exact_pass219_h36_coordinate((uint16_t)e, &c);
            if (status != HHS_EXACT_STATUS_OK) return status;
            packed =
                ((uint64_t)c.vm81_cell81) |
                ((uint64_t)c.vm81_operation64 << 7U) |
                ((uint64_t)c.hash72_row72 << 13U) |
                ((uint64_t)c.hash72_col72 << 20U) |
                ((uint64_t)c.phase_left8 << 27U) |
                ((uint64_t)c.phase_right8 << 30U) |
                ((uint64_t)c.et_bank3 << 33U);
            state->accumulators[ac] =
                packed & HHS_EXACT_PASS219_H36_WORD_MASK;
            return HHS_EXACT_STATUS_OK;
        }
        if (op == UINT16_C(0077)) {
            state->halted = 1U;
            return HHS_EXACT_STATUS_OK;
        }
        state->trap = HHS_EXACT_PASS219_H36_TRAP_UNIMPLEMENTED_UUO;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if ((op >= UINT16_C(0100) && op <= UINT16_C(0132)) ||
        (op >= UINT16_C(0140) && op <= UINT16_C(0177))) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_NONCANONICAL_FLOAT;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (h36_execute_legacy_extended(state, ins, e, &status))
        return status;

    if (op >= UINT16_C(0200) && op <= UINT16_C(0217)) {
        uint8_t mode = (uint8_t)(op & 3U);
        uint64_t input;
        uint64_t result;

        if (mode == 1U) input = (uint64_t)e;
        else if (mode == 2U) input = state->accumulators[ac];
        else {
            status = h36_memory_required(state, e);
            if (status != HHS_EXACT_STATUS_OK) return status;
            input = state->memory[e];
        }
        result = h36_move_transform(op, input);

        if (mode == 0U || mode == 1U)
            state->accumulators[ac] = result;
        else if (mode == 2U)
            state->memory[e] = result;
        else {
            state->accumulators[ac] = result;
            state->memory[e] = result;
        }
        return HHS_EXACT_STATUS_OK;
    }

    if (op == UINT16_C(0250)) {
        uint64_t tmp;
        status = h36_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        tmp = state->memory[e];
        state->memory[e] =
            state->accumulators[ac] & HHS_EXACT_PASS219_H36_WORD_MASK;
        state->accumulators[ac] = tmp;
        return HHS_EXACT_STATUS_OK;
    }

    if (op == UINT16_C(0254)) {
        state->pc18 = e;
        return HHS_EXACT_STATUS_OK;
    }

    if (op == UINT16_C(0256)) {
        HHSExactPass219H36InstructionV1 nested;
        status = h36_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        status = hhs_exact_pass219_h36_instruction_decode(
            state->memory[e], &nested);
        if (status != HHS_EXACT_STATUS_OK) return status;
        return h36_execute(state, &nested, depth + 1U);
    }

    if (op >= UINT16_C(0270) && op <= UINT16_C(0277)) {
        uint8_t mode = (uint8_t)(op & 3U);
        int subtract = (op >= UINT16_C(0274));
        uint64_t operand;
        int64_t result;

        if (mode == 1U) operand = (uint64_t)e;
        else {
            status = h36_memory_required(state, e);
            if (status != HHS_EXACT_STATUS_OK) return status;
            operand = state->memory[e];
        }
        result = subtract
            ? h36_signed(state->accumulators[ac]) - h36_signed(operand)
            : h36_signed(state->accumulators[ac]) + h36_signed(operand);

        if (mode == 0U || mode == 1U)
            state->accumulators[ac] = h36_wrap_i64(result);
        else if (mode == 2U)
            state->memory[e] = h36_wrap_i64(result);
        else {
            state->accumulators[ac] = h36_wrap_i64(result);
            state->memory[e] = h36_wrap_i64(result);
        }
        return HHS_EXACT_STATUS_OK;
    }

    if (op >= UINT16_C(0300) && op <= UINT16_C(0377)) {
        uint16_t family = (uint16_t)(op & UINT16_C(0770));
        uint8_t condition = (uint8_t)(op & 7U);
        int64_t value;

        if (family == UINT16_C(0300)) {
            if (h36_condition(
                    condition, h36_signed(state->accumulators[ac]),
                    (int64_t)e))
                state->pc18 = (state->pc18 + 1U) & UINT32_C(0x3FFFF);
            return HHS_EXACT_STATUS_OK;
        }
        if (family == UINT16_C(0310)) {
            status = h36_memory_required(state, e);
            if (status != HHS_EXACT_STATUS_OK) return status;
            if (h36_condition(
                    condition, h36_signed(state->accumulators[ac]),
                    h36_signed(state->memory[e])))
                state->pc18 = (state->pc18 + 1U) & UINT32_C(0x3FFFF);
            return HHS_EXACT_STATUS_OK;
        }
        if (family == UINT16_C(0320)) {
            if (h36_condition(
                    condition, h36_signed(state->accumulators[ac]), 0))
                state->pc18 = e;
            return HHS_EXACT_STATUS_OK;
        }
        if (family == UINT16_C(0330)) {
            status = h36_memory_required(state, e);
            if (status != HHS_EXACT_STATUS_OK) return status;
            if (h36_condition(condition, h36_signed(state->memory[e]), 0))
                state->pc18 = (state->pc18 + 1U) & UINT32_C(0x3FFFF);
            return HHS_EXACT_STATUS_OK;
        }
        if (family == UINT16_C(0340) || family == UINT16_C(0360)) {
            int64_t delta =
                family == UINT16_C(0340) ? INT64_C(1) : -INT64_C(1);
            value = h36_signed(state->accumulators[ac]) + delta;
            state->accumulators[ac] = h36_wrap_i64(value);
            if (h36_condition(condition, value, 0))
                state->pc18 = e;
            return HHS_EXACT_STATUS_OK;
        }
        if (family == UINT16_C(0350) || family == UINT16_C(0370)) {
            int64_t delta =
                family == UINT16_C(0350) ? INT64_C(1) : -INT64_C(1);
            status = h36_memory_required(state, e);
            if (status != HHS_EXACT_STATUS_OK) return status;
            value = h36_signed(state->memory[e]) + delta;
            state->memory[e] = h36_wrap_i64(value);
            state->accumulators[ac] = h36_wrap_i64(value);
            if (h36_condition(condition, value, 0))
                state->pc18 = (state->pc18 + 1U) & UINT32_C(0x3FFFF);
            return HHS_EXACT_STATUS_OK;
        }
    }

    if (op >= UINT16_C(0400) && op <= UINT16_C(0477)) {
        uint8_t fn = (uint8_t)((op - UINT16_C(0400)) >> 2U);
        uint8_t mode = (uint8_t)(op & 3U);
        uint64_t operand;
        uint64_t result;

        if (mode == 1U) operand = (uint64_t)e;
        else {
            status = h36_memory_required(state, e);
            if (status != HHS_EXACT_STATUS_OK) return status;
            operand = state->memory[e];
        }
        result = h36_bool_fn(fn, state->accumulators[ac], operand);

        if (mode == 0U || mode == 1U)
            state->accumulators[ac] = result;
        else if (mode == 2U)
            state->memory[e] = result;
        else {
            state->accumulators[ac] = result;
            state->memory[e] = result;
        }
        return HHS_EXACT_STATUS_OK;
    }

    state->trap = HHS_EXACT_PASS219_H36_TRAP_UNIMPLEMENTED_OPCODE;
    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_h36_vm_step(
    HHSExactPass219H36VMStateV1 *state
) {
    HHSExactPass219H36InstructionV1 ins;
    HHSExactStatus status;
    if (state == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (state->struct_size != sizeof(*state) ||
        state->version != h36_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (state->halted != 0U) return HHS_EXACT_STATUS_OK;
    if (state->trap != HHS_EXACT_PASS219_H36_TRAP_NONE)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (state->pc18 >= HHS_EXACT_PASS219_H36_WORD_COUNT) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_RANGE;
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }

    status = hhs_exact_pass219_h36_instruction_decode(
        state->memory[state->pc18], &ins);
    if (status != HHS_EXACT_STATUS_OK) return status;

    state->pc18 = (state->pc18 + 1U) & UINT32_C(0x3FFFF);
    status = h36_execute(state, &ins, 0U);
    state->steps += 1U;
    return status;
}

HHSExactStatus hhs_exact_pass219_h36_vm_run(
    HHSExactPass219H36VMStateV1 *state,
    uint32_t max_steps,
    uint32_t *out_steps
) {
    uint32_t start_steps;
    HHSExactStatus status = HHS_EXACT_STATUS_OK;
    if (state == NULL || out_steps == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    start_steps = state->steps;

    while (state->halted == 0U &&
           state->trap == HHS_EXACT_PASS219_H36_TRAP_NONE &&
           (state->steps - start_steps) < max_steps) {
        status = hhs_exact_pass219_h36_vm_step(state);
        if (status != HHS_EXACT_STATUS_OK) break;
    }

    *out_steps = state->steps - start_steps;
    return status;
}

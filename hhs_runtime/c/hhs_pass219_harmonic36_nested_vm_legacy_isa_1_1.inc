/*
 * PDP-10/KA10-compatible exact integer/byte/halfword/test extension.
 *
 * This module intentionally does not approximate the duplicated-sign
 * two-word arithmetic format. MUL/DIV and combined shifts remain fail-closed
 * until their 70-bit magnitude + duplicated sign representation is
 * implemented explicitly.
 */

static void h36_legacy_add_flags(
    HHSExactPass219H36VMStateV1 *state,
    uint64_t a,
    uint64_t b,
    uint64_t result
) {
    uint64_t sign = UINT64_C(1) << 35U;
    a &= HHS_EXACT_PASS219_H36_WORD_MASK;
    b &= HHS_EXACT_PASS219_H36_WORD_MASK;
    result &= HHS_EXACT_PASS219_H36_WORD_MASK;

    if ((a & sign) != 0U && (b & sign) != 0U) {
        if ((result & sign) != 0U) {
            state->legacy_carry0 = 1U;
            state->legacy_carry1 = 1U;
        } else {
            state->legacy_carry0 = 1U;
            state->legacy_overflow = 1U;
        }
        return;
    }
    if ((a & sign) == 0U && (b & sign) == 0U) {
        if ((result & sign) != 0U) {
            state->legacy_carry1 = 1U;
            state->legacy_overflow = 1U;
        }
        return;
    }
    if ((result & sign) == 0U) {
        state->legacy_carry0 = 1U;
        state->legacy_carry1 = 1U;
    }
}

static void h36_legacy_sub_flags(
    HHSExactPass219H36VMStateV1 *state,
    uint64_t a,
    uint64_t b,
    uint64_t result
) {
    uint64_t sign = UINT64_C(1) << 35U;
    a &= HHS_EXACT_PASS219_H36_WORD_MASK;
    b &= HHS_EXACT_PASS219_H36_WORD_MASK;
    result &= HHS_EXACT_PASS219_H36_WORD_MASK;

    if ((a & sign) != 0U && (b & sign) == 0U) {
        if ((result & sign) != 0U) {
            state->legacy_carry0 = 1U;
            state->legacy_carry1 = 1U;
        } else {
            state->legacy_carry0 = 1U;
            state->legacy_overflow = 1U;
        }
        return;
    }
    if ((a & sign) == 0U && (b & sign) != 0U) {
        if ((result & sign) != 0U) {
            state->legacy_carry1 = 1U;
            state->legacy_overflow = 1U;
        }
        return;
    }
    if ((result & sign) == 0U) {
        state->legacy_carry0 = 1U;
        state->legacy_carry1 = 1U;
    }
}

static void h36_legacy_increment_flags(
    HHSExactPass219H36VMStateV1 *state,
    uint64_t result
) {
    const uint64_t max_negative = UINT64_C(1) << 35U;
    result &= HHS_EXACT_PASS219_H36_WORD_MASK;
    if (result == 0U) {
        state->legacy_carry0 = 1U;
        state->legacy_carry1 = 1U;
    } else if (result == max_negative) {
        state->legacy_carry1 = 1U;
        state->legacy_overflow = 1U;
    }
}

static void h36_legacy_decrement_flags(
    HHSExactPass219H36VMStateV1 *state,
    uint64_t result
) {
    const uint64_t max_positive = (UINT64_C(1) << 35U) - UINT64_C(1);
    result &= HHS_EXACT_PASS219_H36_WORD_MASK;
    if (result == max_positive) {
        state->legacy_carry0 = 1U;
        state->legacy_overflow = 1U;
    } else if (result != HHS_EXACT_PASS219_H36_WORD_MASK) {
        state->legacy_carry0 = 1U;
        state->legacy_carry1 = 1U;
    }
}

static void h36_legacy_negate_flags(
    HHSExactPass219H36VMStateV1 *state,
    uint64_t source,
    int magnitude_only
) {
    const uint64_t max_negative = UINT64_C(1) << 35U;
    source &= HHS_EXACT_PASS219_H36_WORD_MASK;
    if (source == max_negative) {
        state->legacy_carry1 = 1U;
        state->legacy_overflow = 1U;
    } else if (magnitude_only == 0 && source == 0U) {
        state->legacy_carry0 = 1U;
        state->legacy_carry1 = 1U;
    }
}

static HHSExactStatus h36_legacy_memory_required(
    HHSExactPass219H36VMStateV1 *state,
    uint32_t address
) {
    if (address >= HHS_EXACT_PASS219_H36_WORD_COUNT) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_RANGE;
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    return HHS_EXACT_STATUS_OK;
}

static uint8_t h36_ac_next(uint8_t ac) {
    return (uint8_t)((ac + 1U) & 15U);
}

static uint64_t h36_abs36(int64_t value) {
    return value < 0 ? (uint64_t)(-value) : (uint64_t)value;
}

static int h36_imul_overflow(int64_t a, int64_t b) {
    uint64_t ma = h36_abs36(a);
    uint64_t mb = h36_abs36(b);
    int negative = ((a < 0) != (b < 0));
    uint64_t limit = negative ? (UINT64_C(1) << 35U)
                              : ((UINT64_C(1) << 35U) - 1U);
    if (ma == 0U || mb == 0U) return 0;
    return mb > limit / ma;
}

static int32_t h36_shift_count(uint32_t e) {
    int32_t magnitude = (int32_t)(e & UINT32_C(0xFF));
    return (e & UINT32_C(0x20000)) != 0U ? -magnitude : magnitude;
}

static uint64_t h36_rotate36(uint64_t value, int32_t count) {
    uint64_t v = value & HHS_EXACT_PASS219_H36_WORD_MASK;
    uint32_t amount;
    if (count == 0) return v;
    amount = (uint32_t)(count < 0 ? -count : count) % 36U;
    if (amount == 0U) return v;
    if (count > 0) {
        return ((v << amount) | (v >> (36U - amount))) &
               HHS_EXACT_PASS219_H36_WORD_MASK;
    }
    return ((v >> amount) | (v << (36U - amount))) &
           HHS_EXACT_PASS219_H36_WORD_MASK;
}

static uint64_t h36_logical_shift36(uint64_t value, int32_t count) {
    uint64_t v = value & HHS_EXACT_PASS219_H36_WORD_MASK;
    uint32_t amount = (uint32_t)(count < 0 ? -count : count);
    if (amount >= 36U) return 0U;
    if (count > 0)
        return (v << amount) & HHS_EXACT_PASS219_H36_WORD_MASK;
    if (count < 0)
        return v >> amount;
    return v;
}

static uint64_t h36_arithmetic_shift36(
    HHSExactPass219H36VMStateV1 *state,
    uint64_t value,
    int32_t count
) {
    const uint64_t sign_mask = UINT64_C(1) << 35U;
    const uint64_t magnitude_mask = sign_mask - 1U;
    uint64_t v = value & HHS_EXACT_PASS219_H36_WORD_MASK;
    uint64_t sign = v & sign_mask;
    uint32_t amount = (uint32_t)(count < 0 ? -count : count);
    uint32_t i;

    if (count > 0) {
        for (i = 0U; i < amount; ++i) {
            uint64_t bit1 = v & (UINT64_C(1) << 34U);
            if ((sign == 0U && bit1 != 0U) ||
                (sign != 0U && bit1 == 0U))
                state->legacy_overflow = 1U;
            v = sign | (((v & magnitude_mask) << 1U) & magnitude_mask);
        }
    } else if (count < 0) {
        for (i = 0U; i < amount; ++i) {
            uint64_t magnitude = (v & magnitude_mask) >> 1U;
            if (sign != 0U)
                magnitude |= UINT64_C(1) << 34U;
            v = sign | magnitude;
        }
    }
    return v & HHS_EXACT_PASS219_H36_WORD_MASK;
}

typedef struct H36BytePointer {
    uint8_t p;
    uint8_t s;
    uint8_t reserved;
    uint8_t indirect;
    uint8_t index;
    uint32_t address;
} H36BytePointer;

static HHSExactStatus h36_byte_pointer_decode(
    HHSExactPass219H36VMStateV1 *state,
    uint64_t word,
    H36BytePointer *out
) {
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    word &= HHS_EXACT_PASS219_H36_WORD_MASK;
    out->p = (uint8_t)((word >> 30U) & UINT64_C(077));
    out->s = (uint8_t)((word >> 24U) & UINT64_C(077));
    out->reserved = (uint8_t)((word >> 23U) & UINT64_C(1));
    out->indirect = (uint8_t)((word >> 22U) & UINT64_C(1));
    out->index = (uint8_t)((word >> 18U) & UINT64_C(017));
    out->address = (uint32_t)(word & HHS_EXACT_PASS219_H36_HALF_MASK);
    if (out->reserved != 0U || out->s == 0U || out->s > 36U ||
        out->p > 36U) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_LEGACY_POINTER;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

static uint64_t h36_byte_pointer_set_p(uint64_t word, uint8_t p) {
    return (word & ~(UINT64_C(077) << 30U)) |
           (((uint64_t)p & UINT64_C(077)) << 30U);
}

static HHSExactStatus h36_byte_pointer_increment(
    HHSExactPass219H36VMStateV1 *state,
    uint32_t pointer_address,
    H36BytePointer *out_pointer
) {
    uint64_t pointer_word;
    H36BytePointer pointer;
    HHSExactStatus status;

    status = h36_legacy_memory_required(state, pointer_address);
    if (status != HHS_EXACT_STATUS_OK) return status;
    pointer_word = state->memory[pointer_address];

    status = h36_byte_pointer_decode(state, pointer_word, &pointer);
    if (status != HHS_EXACT_STATUS_OK) return status;

    if (pointer.p >= pointer.s) {
        pointer.p = (uint8_t)(pointer.p - pointer.s);
        pointer_word = h36_byte_pointer_set_p(pointer_word, pointer.p);
    } else {
        pointer_word = (pointer_word + UINT64_C(1)) &
                       HHS_EXACT_PASS219_H36_WORD_MASK;
        pointer.p = (uint8_t)(36U - pointer.s);
        pointer_word = h36_byte_pointer_set_p(pointer_word, pointer.p);
    }

    state->memory[pointer_address] = pointer_word;
    return h36_byte_pointer_decode(state, pointer_word, out_pointer);
}

static HHSExactStatus h36_byte_target_address(
    HHSExactPass219H36VMStateV1 *state,
    const H36BytePointer *pointer,
    uint32_t *out_address
) {
    HHSExactPass219H36InstructionV1 pseudo;
    if (pointer == NULL || out_address == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&pseudo, 0, sizeof(pseudo));
    pseudo.indirect1 = pointer->indirect;
    pseudo.index4 = pointer->index;
    pseudo.address18 = pointer->address;
    return h36_effective_address(state, &pseudo, out_address);
}

static HHSExactStatus h36_byte_load_or_deposit(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t ac,
    const H36BytePointer *pointer,
    int deposit
) {
    uint32_t target;
    uint64_t byte_mask;
    uint64_t shifted_mask;
    HHSExactStatus status;

    if (pointer->p + pointer->s > 36U) {
        state->trap = HHS_EXACT_PASS219_H36_TRAP_LEGACY_POINTER;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    status = h36_byte_target_address(state, pointer, &target);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = h36_legacy_memory_required(state, target);
    if (status != HHS_EXACT_STATUS_OK) return status;

    byte_mask = pointer->s == 36U
        ? HHS_EXACT_PASS219_H36_WORD_MASK
        : ((UINT64_C(1) << pointer->s) - 1U);
    shifted_mask = (byte_mask << pointer->p) &
                   HHS_EXACT_PASS219_H36_WORD_MASK;

    if (deposit) {
        uint64_t source = state->accumulators[ac] & byte_mask;
        state->memory[target] =
            (state->memory[target] & ~shifted_mask) |
            ((source << pointer->p) & shifted_mask);
    } else {
        state->accumulators[ac] =
            (state->memory[target] >> pointer->p) & byte_mask;
    }
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_execute_byte(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e
) {
    H36BytePointer pointer;
    HHSExactStatus status;
    uint16_t op = ins->opcode9;
    uint8_t ac = ins->accumulator4;

    if (op == UINT16_C(0133)) {
        return h36_byte_pointer_increment(state, e, &pointer);
    }

    status = h36_legacy_memory_required(state, e);
    if (status != HHS_EXACT_STATUS_OK) return status;

    if (op == UINT16_C(0134) || op == UINT16_C(0136)) {
        status = h36_byte_pointer_increment(state, e, &pointer);
        if (status != HHS_EXACT_STATUS_OK) return status;
    } else {
        status = h36_byte_pointer_decode(state, state->memory[e], &pointer);
        if (status != HHS_EXACT_STATUS_OK) return status;
    }

    return h36_byte_load_or_deposit(
        state, ac, &pointer,
        op == UINT16_C(0136) || op == UINT16_C(0137));
}

static HHSExactStatus h36_execute_imul_idiv(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e
) {
    uint16_t op = ins->opcode9;
    uint8_t mode = (uint8_t)(op & 3U);
    uint8_t ac = ins->accumulator4;
    uint8_t ac1 = h36_ac_next(ac);
    uint64_t operand;
    HHSExactStatus status;

    if (mode == 1U) {
        operand = (uint64_t)e;
    } else {
        status = h36_legacy_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        operand = state->memory[e];
    }

    if (op >= UINT16_C(0220) && op <= UINT16_C(0223)) {
        int64_t a = h36_signed(state->accumulators[ac]);
        int64_t b = h36_signed(operand);
        uint64_t result =
            (state->accumulators[ac] * operand) &
            HHS_EXACT_PASS219_H36_WORD_MASK;
        state->legacy_overflow =
            (uint8_t)(h36_imul_overflow(a, b) ? 1U : 0U);

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

    if (op >= UINT16_C(0230) && op <= UINT16_C(0233)) {
        int64_t dividend = h36_signed(state->accumulators[ac]);
        int64_t divisor = h36_signed(operand);
        int64_t quotient;
        int64_t remainder;

        state->legacy_no_divide = 0U;
        if (divisor == 0 ||
            (dividend == -(INT64_C(1) << 35U) && divisor == -1)) {
            state->legacy_overflow = 1U;
            state->legacy_no_divide = 1U;
            return HHS_EXACT_STATUS_OK;
        }

        quotient = dividend / divisor;
        remainder = dividend % divisor;

        if (mode == 0U || mode == 1U) {
            state->accumulators[ac] = h36_wrap_i64(quotient);
            state->accumulators[ac1] = h36_wrap_i64(remainder);
        } else if (mode == 2U) {
            state->memory[e] = h36_wrap_i64(quotient);
        } else {
            state->accumulators[ac] = h36_wrap_i64(quotient);
            state->accumulators[ac1] = h36_wrap_i64(remainder);
            state->memory[e] = h36_wrap_i64(quotient);
        }
        return HHS_EXACT_STATUS_OK;
    }

    state->trap = HHS_EXACT_PASS219_H36_TRAP_UNIMPLEMENTED_OPCODE;
    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

static HHSExactStatus h36_execute_shift_jffo(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e
) {
    uint16_t op = ins->opcode9;
    uint8_t ac = ins->accumulator4;
    int32_t count = h36_shift_count(e);

    if (op == UINT16_C(0240)) {
        state->accumulators[ac] = h36_arithmetic_shift36(
            state, state->accumulators[ac], count);
        return HHS_EXACT_STATUS_OK;
    }
    if (op == UINT16_C(0241)) {
        state->accumulators[ac] =
            h36_rotate36(state->accumulators[ac], count);
        return HHS_EXACT_STATUS_OK;
    }
    if (op == UINT16_C(0242)) {
        state->accumulators[ac] =
            h36_logical_shift36(state->accumulators[ac], count);
        return HHS_EXACT_STATUS_OK;
    }
    if (op == UINT16_C(0243)) {
        uint64_t v = state->accumulators[ac] &
                     HHS_EXACT_PASS219_H36_WORD_MASK;
        uint8_t ac1 = h36_ac_next(ac);
        uint32_t count_zero = 0U;
        int32_t bit;

        if (v == 0U || (v & (UINT64_C(1) << 35U)) != 0U) {
            state->accumulators[ac1] = 0U;
            return HHS_EXACT_STATUS_OK;
        }
        for (bit = 35; bit >= 0; --bit) {
            if ((v & (UINT64_C(1) << (uint32_t)bit)) != 0U)
                break;
            ++count_zero;
        }
        state->accumulators[ac1] = count_zero;
        state->pc18 = e;
        return HHS_EXACT_STATUS_OK;
    }

    state->trap = HHS_EXACT_PASS219_H36_TRAP_UNIMPLEMENTED_OPCODE;
    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

static uint64_t h36_halfword_apply(
    uint64_t destination,
    uint32_t moved_half,
    int destination_right,
    uint8_t other_operation
) {
    uint64_t moved = (uint64_t)moved_half & HHS_EXACT_PASS219_H36_HALF_MASK;
    uint64_t other;
    uint64_t result = destination & HHS_EXACT_PASS219_H36_WORD_MASK;

    if (other_operation == 0U) {
        other = destination_right
            ? ((result >> 18U) & HHS_EXACT_PASS219_H36_HALF_MASK)
            : (result & HHS_EXACT_PASS219_H36_HALF_MASK);
    } else if (other_operation == 1U) {
        other = 0U;
    } else if (other_operation == 2U) {
        other = HHS_EXACT_PASS219_H36_HALF_MASK;
    } else {
        other = (moved & (UINT64_C(1) << 17U)) != 0U
            ? HHS_EXACT_PASS219_H36_HALF_MASK : 0U;
    }

    if (destination_right)
        return ((other << 18U) | moved) &
               HHS_EXACT_PASS219_H36_WORD_MASK;
    return ((moved << 18U) | other) &
           HHS_EXACT_PASS219_H36_WORD_MASK;
}

static HHSExactStatus h36_execute_halfword(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e
) {
    uint16_t op = ins->opcode9;
    uint8_t ac = ins->accumulator4;
    uint8_t mode = (uint8_t)(op & 3U);
    int destination_right = (op & UINT16_C(0040)) != 0U;
    int orientation_bit = (op & UINT16_C(0004)) != 0U;
    int source_right = destination_right ? !orientation_bit : orientation_bit;
    uint8_t other_operation = (uint8_t)((op >> 3U) & 3U);
    uint64_t source_word;
    uint64_t destination_word;
    uint32_t moved_half;
    uint64_t result;
    HHSExactStatus status;

    if (mode == 1U) {
        source_word = (uint64_t)e;
        destination_word = state->accumulators[ac];
    } else if (mode == 2U) {
        status = h36_legacy_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        source_word = state->accumulators[ac];
        destination_word = state->memory[e];
    } else {
        status = h36_legacy_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        source_word = state->memory[e];
        destination_word = mode == 0U
            ? state->accumulators[ac] : state->memory[e];
    }

    moved_half = source_right
        ? (uint32_t)(source_word & HHS_EXACT_PASS219_H36_HALF_MASK)
        : (uint32_t)((source_word >> 18U) &
                     HHS_EXACT_PASS219_H36_HALF_MASK);
    result = h36_halfword_apply(
        destination_word, moved_half, destination_right, other_operation);

    if (mode == 0U || mode == 1U)
        state->accumulators[ac] = result;
    else
        state->memory[e] = result;
    return HHS_EXACT_STATUS_OK;
}

static int h36_test_skip(uint8_t mode, uint64_t masked) {
    switch (mode) {
        case 0U: return 0;
        case 1U: return masked == 0U;
        case 2U: return 1;
        case 3U: return masked != 0U;
        default: return 0;
    }
}

static HHSExactStatus h36_execute_test_bits(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e
) {
    uint16_t op = ins->opcode9;
    uint8_t ac = ins->accumulator4;
    uint8_t pair = (uint8_t)(op & 1U);
    uint8_t skip_mode = (uint8_t)((op >> 1U) & 3U);
    uint8_t modification = (uint8_t)((op >> 4U) & 3U);
    uint8_t direct_group = (uint8_t)((op >> 3U) & 1U);
    uint64_t mask;
    uint64_t before = state->accumulators[ac] &
                      HHS_EXACT_PASS219_H36_WORD_MASK;
    uint64_t masked;
    HHSExactStatus status;

    if (direct_group == 0U) {
        mask = pair == 0U
            ? ((uint64_t)e & HHS_EXACT_PASS219_H36_HALF_MASK)
            : (((uint64_t)e & HHS_EXACT_PASS219_H36_HALF_MASK) << 18U);
    } else {
        status = h36_legacy_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        mask = state->memory[e] & HHS_EXACT_PASS219_H36_WORD_MASK;
        if (pair != 0U)
            mask = ((mask & HHS_EXACT_PASS219_H36_HALF_MASK) << 18U) |
                   ((mask >> 18U) & HHS_EXACT_PASS219_H36_HALF_MASK);
    }

    masked = before & mask;
    if (modification == 1U)
        state->accumulators[ac] = before & ~mask &
            HHS_EXACT_PASS219_H36_WORD_MASK;
    else if (modification == 2U)
        state->accumulators[ac] = (before ^ mask) &
            HHS_EXACT_PASS219_H36_WORD_MASK;
    else if (modification == 3U)
        state->accumulators[ac] = (before | mask) &
            HHS_EXACT_PASS219_H36_WORD_MASK;

    if (h36_test_skip(skip_mode, masked))
        state->pc18 = (state->pc18 + 1U) & UINT32_C(0x3FFFF);
    return HHS_EXACT_STATUS_OK;
}

static int h36_execute_legacy_extended(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e,
    HHSExactStatus *out_status
) {
    uint16_t op = ins->opcode9;
    if (out_status == NULL) return 0;

    if (op >= UINT16_C(0133) && op <= UINT16_C(0137)) {
        *out_status = h36_execute_byte(state, ins, e);
        return 1;
    }
    if (op >= UINT16_C(0220) && op <= UINT16_C(0223)) {
        *out_status = h36_execute_imul_idiv(state, ins, e);
        return 1;
    }
    if (op >= UINT16_C(0230) && op <= UINT16_C(0233)) {
        *out_status = h36_execute_imul_idiv(state, ins, e);
        return 1;
    }
    if (op >= UINT16_C(0240) && op <= UINT16_C(0243)) {
        *out_status = h36_execute_shift_jffo(state, ins, e);
        return 1;
    }
    if (op >= UINT16_C(0500) && op <= UINT16_C(0577)) {
        *out_status = h36_execute_halfword(state, ins, e);
        return 1;
    }
    if (op >= UINT16_C(0600) && op <= UINT16_C(0677)) {
        *out_status = h36_execute_test_bits(state, ins, e);
        return 1;
    }
    return 0;
}

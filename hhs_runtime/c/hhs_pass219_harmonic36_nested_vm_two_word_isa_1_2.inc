/*
 * Exact PDP-10 two-word fixed arithmetic.
 *
 * Arithmetic values use two 36-bit words. The arithmetic field is the
 * 70-bit string formed by bits 1-35 of both words; bit 0 of the lower
 * word mirrors the sign in bit 0 of the upper word.
 */

#define H36_SIGN_MASK (UINT64_C(1) << 35U)
#define H36_MAG35_MASK (H36_SIGN_MASK - UINT64_C(1))

typedef struct H36TwoWordMagnitude {
    uint8_t negative;
    uint8_t minimum_value;
    uint64_t high35;
    uint64_t low35;
} H36TwoWordMagnitude;

static void h36_negate70(uint64_t *high35, uint64_t *low35) {
    uint64_t low = ((~(*low35)) & H36_MAG35_MASK) + UINT64_C(1);
    uint64_t carry = low >> 35U;
    *low35 = low & H36_MAG35_MASK;
    *high35 = (((~(*high35)) & H36_MAG35_MASK) + carry) &
              H36_MAG35_MASK;
}

static HHSExactStatus h36_decode_two_word(
    uint64_t high_word,
    uint64_t low_word,
    H36TwoWordMagnitude *out
) {
    uint8_t high_sign;
    uint8_t low_sign;
    uint64_t high35;
    uint64_t low35;

    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    high_word &= HHS_EXACT_PASS219_H36_WORD_MASK;
    low_word &= HHS_EXACT_PASS219_H36_WORD_MASK;
    high_sign = (uint8_t)((high_word & H36_SIGN_MASK) != 0U);
    low_sign = (uint8_t)((low_word & H36_SIGN_MASK) != 0U);
    if (high_sign != low_sign)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    high35 = high_word & H36_MAG35_MASK;
    low35 = low_word & H36_MAG35_MASK;
    memset(out, 0, sizeof(*out));
    out->negative = high_sign;

    if (high_sign != 0U) {
        if (high35 == 0U && low35 == 0U) {
            out->minimum_value = 1U;
            return HHS_EXACT_STATUS_OK;
        }
        h36_negate70(&high35, &low35);
    }
    out->high35 = high35;
    out->low35 = low35;
    return HHS_EXACT_STATUS_OK;
}

static void h36_pack_two_word(
    uint8_t negative,
    uint64_t high35,
    uint64_t low35,
    uint64_t *out_high,
    uint64_t *out_low
) {
    high35 &= H36_MAG35_MASK;
    low35 &= H36_MAG35_MASK;
    if (negative != 0U && (high35 != 0U || low35 != 0U))
        h36_negate70(&high35, &low35);

    *out_high = high35;
    *out_low = low35;
    if (negative != 0U) {
        *out_high |= H36_SIGN_MASK;
        *out_low |= H36_SIGN_MASK;
    }
}

static uint64_t h36_pack_signed_magnitude36(
    uint8_t negative,
    uint64_t magnitude
) {
    if (magnitude == 0U)
        return 0U;
    if (negative == 0U)
        return magnitude & HHS_EXACT_PASS219_H36_WORD_MASK;
    return ((~magnitude) + UINT64_C(1)) &
           HHS_EXACT_PASS219_H36_WORD_MASK;
}

static void h36_multiply35(
    uint64_t a,
    uint64_t b,
    uint64_t *out_high,
    uint64_t *out_low
) {
    const uint64_t limb_mask = (UINT64_C(1) << 18U) - UINT64_C(1);
    uint64_t a0 = a & limb_mask;
    uint64_t a1 = a >> 18U;
    uint64_t b0 = b & limb_mask;
    uint64_t b1 = b >> 18U;
    uint64_t p0 = a0 * b0;
    uint64_t p1 = a0 * b1 + a1 * b0;
    uint64_t p2 = a1 * b1;
    uint64_t low_wide = p0 + (p1 << 18U);
    uint64_t carry = low_wide >> 35U;

    *out_low = low_wide & H36_MAG35_MASK;
    *out_high = (p2 << 1U) + carry;
}

static HHSExactStatus h36_execute_mul(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e
) {
    uint8_t ac = ins->accumulator4;
    uint8_t ac1 = h36_ac_next(ac);
    uint8_t mode = (uint8_t)(ins->opcode9 & 3U);
    int64_t left = h36_signed(state->accumulators[ac]);
    uint64_t operand;
    int64_t right;
    uint64_t high35;
    uint64_t low35;
    uint64_t high_word;
    uint64_t low_word;
    uint64_t left_mag;
    uint64_t right_mag;
    uint8_t negative;
    HHSExactStatus status;

    if (mode == 1U) {
        operand = (uint64_t)e;
    } else {
        status = h36_legacy_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        operand = state->memory[e];
    }
    right = h36_signed(operand);
    left_mag = h36_abs36(left);
    right_mag = h36_abs36(right);
    negative = (uint8_t)((left < 0) != (right < 0));
    h36_multiply35(left_mag, right_mag, &high35, &low35);

    state->legacy_overflow = 0U;
    if (high35 == H36_SIGN_MASK) {
        state->legacy_overflow = 1U;
        high_word = H36_SIGN_MASK;
        low_word = H36_SIGN_MASK;
    } else {
        h36_pack_two_word(
            negative, high35, low35, &high_word, &low_word);
    }

    if (mode == 0U || mode == 1U) {
        state->accumulators[ac] = high_word;
        state->accumulators[ac1] = low_word;
    } else if (mode == 2U) {
        state->memory[e] = high_word;
    } else {
        state->accumulators[ac] = high_word;
        state->accumulators[ac1] = low_word;
        state->memory[e] = high_word;
    }
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_divide70_by35(
    const H36TwoWordMagnitude *dividend,
    uint64_t divisor,
    uint64_t *out_quotient,
    uint64_t *out_remainder
) {
    uint64_t remainder = 0U;
    uint64_t quotient = 0U;
    int32_t bit;

    if (dividend == NULL || out_quotient == NULL || out_remainder == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (divisor == 0U || dividend->minimum_value != 0U ||
        dividend->high35 >= divisor)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (bit = 69; bit >= 0; --bit) {
        uint64_t incoming;
        uint8_t take;
        if (bit >= 35)
            incoming = (dividend->high35 >> (uint32_t)(bit - 35)) & 1U;
        else
            incoming = (dividend->low35 >> (uint32_t)bit) & 1U;

        remainder = (remainder << 1U) | incoming;
        take = (uint8_t)(remainder >= divisor);
        if (take != 0U)
            remainder -= divisor;

        if (bit < 35)
            quotient = (quotient << 1U) | take;
        else if (take != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    *out_quotient = quotient;
    *out_remainder = remainder;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_execute_div(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e
) {
    uint8_t ac = ins->accumulator4;
    uint8_t ac1 = h36_ac_next(ac);
    uint8_t mode = (uint8_t)(ins->opcode9 & 3U);
    H36TwoWordMagnitude dividend;
    uint64_t operand;
    int64_t divisor_signed;
    uint64_t divisor_mag;
    uint64_t quotient_mag;
    uint64_t remainder_mag;
    uint8_t quotient_negative;
    uint64_t quotient_word;
    uint64_t remainder_word;
    HHSExactStatus status;

    if (mode == 1U) {
        operand = (uint64_t)e;
    } else {
        status = h36_legacy_memory_required(state, e);
        if (status != HHS_EXACT_STATUS_OK) return status;
        operand = state->memory[e];
    }
    divisor_signed = h36_signed(operand);
    divisor_mag = h36_abs36(divisor_signed);

    status = h36_decode_two_word(
        state->accumulators[ac], state->accumulators[ac1], &dividend);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    state->legacy_no_divide = 0U;
    if (divisor_mag == 0U || dividend.minimum_value != 0U ||
        dividend.high35 >= divisor_mag) {
        state->legacy_overflow = 1U;
        state->legacy_no_divide = 1U;
        return HHS_EXACT_STATUS_OK;
    }

    status = h36_divide70_by35(
        &dividend, divisor_mag, &quotient_mag, &remainder_mag);
    if (status != HHS_EXACT_STATUS_OK) {
        state->legacy_overflow = 1U;
        state->legacy_no_divide = 1U;
        return HHS_EXACT_STATUS_OK;
    }

    quotient_negative = (uint8_t)(
        dividend.negative != (uint8_t)(divisor_signed < 0));
    quotient_word = h36_pack_signed_magnitude36(
        quotient_negative, quotient_mag);
    remainder_word = h36_pack_signed_magnitude36(
        dividend.negative, remainder_mag);

    if (mode == 0U || mode == 1U) {
        state->accumulators[ac] = quotient_word;
        state->accumulators[ac1] = remainder_word;
    } else if (mode == 2U) {
        state->memory[e] = quotient_word;
    } else {
        state->accumulators[ac] = quotient_word;
        state->accumulators[ac1] = remainder_word;
        state->memory[e] = quotient_word;
    }
    return HHS_EXACT_STATUS_OK;
}

static void h36_shift_pair_left_one(uint64_t *high, uint64_t *low) {
    uint64_t carry = (*low >> 35U) & UINT64_C(1);
    *low = (*low << 1U) & HHS_EXACT_PASS219_H36_WORD_MASK;
    *high = ((*high << 1U) | carry) &
            HHS_EXACT_PASS219_H36_WORD_MASK;
}

static void h36_shift_pair_right_one(uint64_t *high, uint64_t *low) {
    uint64_t carry = *high & UINT64_C(1);
    *high >>= 1U;
    *low = (*low >> 1U) | (carry << 35U);
}

static HHSExactStatus h36_execute_logical_combined(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t ac,
    int32_t count,
    int rotate
) {
    uint8_t ac1 = h36_ac_next(ac);
    uint64_t high = state->accumulators[ac] &
                    HHS_EXACT_PASS219_H36_WORD_MASK;
    uint64_t low = state->accumulators[ac1] &
                   HHS_EXACT_PASS219_H36_WORD_MASK;
    uint32_t amount = (uint32_t)(count < 0 ? -count : count);
    uint32_t i;

    if (rotate != 0)
        amount %= 72U;
    else if (amount > 72U)
        amount = 72U;

    for (i = 0U; i < amount; ++i) {
        if (count > 0) {
            uint64_t wrap = (high >> 35U) & UINT64_C(1);
            h36_shift_pair_left_one(&high, &low);
            if (rotate != 0)
                low |= wrap;
        } else if (count < 0) {
            uint64_t wrap = low & UINT64_C(1);
            h36_shift_pair_right_one(&high, &low);
            if (rotate != 0)
                high |= wrap << 35U;
        }
    }
    state->accumulators[ac] = high;
    state->accumulators[ac1] = low;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_execute_arithmetic_combined(
    HHSExactPass219H36VMStateV1 *state,
    uint8_t ac,
    int32_t count
) {
    uint8_t ac1 = h36_ac_next(ac);
    uint64_t high_word = state->accumulators[ac] &
                         HHS_EXACT_PASS219_H36_WORD_MASK;
    uint64_t low_word = state->accumulators[ac1] &
                        HHS_EXACT_PASS219_H36_WORD_MASK;
    uint64_t sign = high_word & H36_SIGN_MASK;
    uint64_t high35 = high_word & H36_MAG35_MASK;
    uint64_t low35 = low_word & H36_MAG35_MASK;
    uint32_t amount = (uint32_t)(count < 0 ? -count : count);
    uint32_t i;

    if (count == 0)
        return HHS_EXACT_STATUS_OK;

    for (i = 0U; i < amount; ++i) {
        if (count > 0) {
            uint64_t bit1 = high35 & (UINT64_C(1) << 34U);
            uint64_t carry = (low35 >> 34U) & UINT64_C(1);
            if ((sign == 0U && bit1 != 0U) ||
                (sign != 0U && bit1 == 0U))
                state->legacy_overflow = 1U;
            high35 = ((high35 << 1U) | carry) & H36_MAG35_MASK;
            low35 = (low35 << 1U) & H36_MAG35_MASK;
        } else {
            uint64_t carry = high35 & UINT64_C(1);
            low35 = (low35 >> 1U) | (carry << 34U);
            high35 >>= 1U;
            if (sign != 0U)
                high35 |= UINT64_C(1) << 34U;
        }
    }

    state->accumulators[ac] = sign | high35;
    state->accumulators[ac1] = sign | low35;
    return HHS_EXACT_STATUS_OK;
}

static int h36_execute_legacy_two_word(
    HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36InstructionV1 *ins,
    uint32_t e,
    HHSExactStatus *out_status
) {
    uint16_t op = ins->opcode9;
    int32_t count;
    if (out_status == NULL) return 0;

    if (op >= UINT16_C(0224) && op <= UINT16_C(0227)) {
        *out_status = h36_execute_mul(state, ins, e);
        return 1;
    }
    if (op >= UINT16_C(0234) && op <= UINT16_C(0237)) {
        *out_status = h36_execute_div(state, ins, e);
        return 1;
    }

    count = h36_shift_count(e);
    if (op == UINT16_C(0244)) {
        *out_status = h36_execute_arithmetic_combined(
            state, ins->accumulator4, count);
        return 1;
    }
    if (op == UINT16_C(0245)) {
        *out_status = h36_execute_logical_combined(
            state, ins->accumulator4, count, 1);
        return 1;
    }
    if (op == UINT16_C(0246)) {
        *out_status = h36_execute_logical_combined(
            state, ins->accumulator4, count, 0);
        return 1;
    }
    return 0;
}

static uint64_t h36_reverse36(uint64_t value) {
    uint64_t in = value & HHS_EXACT_PASS219_H36_WORD_MASK;
    uint64_t out = 0U;
    uint32_t i;
    for (i = 0U; i < HHS_EXACT_PASS219_H36_WORD_BITS; ++i) {
        out |= ((in >> i) & UINT64_C(1)) << (35U - i);
    }
    return out;
}

static uint32_t h36_distance12(uint8_t a, uint8_t b) {
    uint32_t forward = (uint32_t)((b + 12U - a) % 12U);
    uint32_t reverse = (uint32_t)((a + 12U - b) % 12U);
    return forward < reverse ? forward : reverse;
}

uint32_t hhs_exact_pass219_h36_version(void) {
    return h36_version_word();
}

HHSExactStatus hhs_exact_pass219_h36_validate(void) {
    uint32_t i;
    if (HHS_EXACT_PASS219_H36_WORD_COUNT * HHS_EXACT_PASS219_H36_WORD_BITS !=
        HHS_EXACT_PASS219_H36_FRAME_BITS)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (HHS_EXACT_VM81_CELLS * HHS_EXACT_PASS219_H36_RULE_COUNT !=
        HHS_EXACT_PASS219_H36_FRAME_BITS)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (72U * 72U != HHS_EXACT_PASS219_H36_FRAME_BITS)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (HHS_EXACT_PASS219_H36_ET_CLASSES * HHS_EXACT_PASS219_H36_ET_CLASSES *
        HHS_EXACT_PASS219_H36_ET_BANKS != HHS_EXACT_PASS219_H36_FRAME_BITS)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (i = 1U; i <= HHS_EXACT_PASS219_H36_RULE_COUNT; ++i) {
        HHSExactPass219H36HarmonicRuleDescriptorV1 rule;
        if (hhs_exact_pass219_h36_harmonic_rule((uint16_t)i, &rule) !=
            HHS_EXACT_STATUS_OK)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if ((rule.core_mask12 | rule.tension_mask12 |
             rule.resolution_mask12 | rule.scale_mask12) & UINT16_C(0xF000))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_coordinate(
    uint16_t linear5184,
    HHSExactPass219H36CoordinateV1 *out
) {
    uint8_t operation;
    if (out == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (linear5184 >= HHS_EXACT_PASS219_H36_FRAME_BITS)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out, 0, sizeof(*out));
    out->linear5184 = linear5184;
    out->word144 = (uint8_t)(linear5184 / HHS_EXACT_PASS219_H36_WORD_BITS);
    out->bit36 = (uint8_t)(linear5184 % HHS_EXACT_PASS219_H36_WORD_BITS);
    out->et_bank3 = (uint8_t)(out->bit36 / HHS_EXACT_PASS219_H36_ET_CLASSES);
    out->et_pitch12 = (uint8_t)(out->bit36 % HHS_EXACT_PASS219_H36_ET_CLASSES);
    out->q144_row12 = (uint8_t)(out->word144 / HHS_EXACT_PASS219_H36_ET_CLASSES);
    out->q144_col12 = (uint8_t)(out->word144 % HHS_EXACT_PASS219_H36_ET_CLASSES);
    out->vm81_cell81 = (uint8_t)(linear5184 / HHS_EXACT_PASS219_H36_RULE_COUNT);
    operation = (uint8_t)(linear5184 % HHS_EXACT_PASS219_H36_RULE_COUNT);
    out->vm81_operation64 = operation;
    out->hash72_row72 = (uint8_t)(linear5184 / HHS_EXACT_HASH72_LEN);
    out->hash72_col72 = (uint8_t)(linear5184 % HHS_EXACT_HASH72_LEN);
    out->phase_left8 = (uint8_t)(operation / HHS_EXACT_PHASE_BASIS_COUNT);
    out->phase_right8 = (uint8_t)(operation % HHS_EXACT_PHASE_BASIS_COUNT);
    out->harmonic_rule64 = (uint8_t)(operation + 1U);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_instruction_encode(
    uint16_t opcode9,
    uint8_t ac4,
    uint8_t indirect1,
    uint8_t index4,
    uint32_t address18,
    uint64_t *out_word36
) {
    if (out_word36 == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (opcode9 > UINT16_C(0x1FF) || ac4 > 15U || indirect1 > 1U ||
        index4 > 15U || address18 > UINT32_C(0x3FFFF))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    *out_word36 =
        (((uint64_t)opcode9) << 27U) |
        (((uint64_t)ac4) << 23U) |
        (((uint64_t)indirect1) << 22U) |
        (((uint64_t)index4) << 18U) |
        (uint64_t)address18;
    *out_word36 &= HHS_EXACT_PASS219_H36_WORD_MASK;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_instruction_decode(
    uint64_t word36,
    HHSExactPass219H36InstructionV1 *out
) {
    uint64_t w;
    if (out == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if ((word36 & ~HHS_EXACT_PASS219_H36_WORD_MASK) != 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    w = word36 & HHS_EXACT_PASS219_H36_WORD_MASK;
    memset(out, 0, sizeof(*out));
    out->word36 = w;
    out->opcode9 = (uint16_t)((w >> 27U) & UINT64_C(0x1FF));
    out->accumulator4 = (uint8_t)((w >> 23U) & UINT64_C(0x0F));
    out->indirect1 = (uint8_t)((w >> 22U) & UINT64_C(0x01));
    out->index4 = (uint8_t)((w >> 18U) & UINT64_C(0x0F));
    out->address18 = (uint32_t)(w & HHS_EXACT_PASS219_H36_HALF_MASK);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_import_vm81(
    const HHSExactVM81Frame *frame,
    HHSExactPass219H36VMStateV1 *state
) {
    uint32_t word_index;
    HHSExactStatus status;
    if (frame == NULL || state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_pass219_h36_vm_init(state);
    if (status != HHS_EXACT_STATUS_OK) return status;

    for (word_index = 0U; word_index < HHS_EXACT_PASS219_H36_WORD_COUNT;
         ++word_index) {
        uint32_t start = word_index * HHS_EXACT_PASS219_H36_WORD_BITS;
        uint32_t source_word = start / 64U;
        uint32_t source_bit = start % 64U;
        uint64_t chunk = frame->words[source_word] >> source_bit;

        if (source_bit > 28U) {
            chunk |= frame->words[source_word + 1U] << (64U - source_bit);
        }
        state->memory[word_index] =
            h36_reverse36(chunk & HHS_EXACT_PASS219_H36_WORD_MASK);
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_export_vm81(
    const HHSExactPass219H36VMStateV1 *state,
    HHSExactVM81Frame *frame
) {
    uint32_t word_index;
    if (state == NULL || frame == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(frame, 0, sizeof(*frame));
    for (word_index = 0U; word_index < HHS_EXACT_PASS219_H36_WORD_COUNT;
         ++word_index) {
        uint32_t start = word_index * HHS_EXACT_PASS219_H36_WORD_BITS;
        uint32_t target_word = start / 64U;
        uint32_t target_bit = start % 64U;
        uint64_t chunk =
            h36_reverse36(state->memory[word_index]) &
            HHS_EXACT_PASS219_H36_WORD_MASK;

        frame->words[target_word] |= chunk << target_bit;
        if (target_bit > 28U) {
            frame->words[target_word + 1U] |= chunk >> (64U - target_bit);
        }
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_equal_temperament_seed(
    HHSExactPass219H36VMStateV1 *state
) {
    uint32_t root;
    uint32_t interval;
    HHSExactStatus status;
    if (state == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_pass219_h36_vm_init(state);
    if (status != HHS_EXACT_STATUS_OK) return status;

    for (root = 0U; root < 12U; ++root) {
        for (interval = 0U; interval < 12U; ++interval) {
            uint16_t source = (uint16_t)(UINT16_C(1) << root);
            uint16_t forward =
                (uint16_t)(UINT16_C(1) << ((root + interval) % 12U));
            uint16_t inverse =
                (uint16_t)(UINT16_C(1) << ((root + 12U - interval) % 12U));
            state->memory[root * 12U + interval] =
                h36_pack_harmonic(source, forward, inverse);
        }
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_harmonic_pack(
    uint16_t core_mask12,
    uint16_t tension_mask12,
    uint16_t resolution_mask12,
    uint64_t *out_word36
) {
    if (out_word36 == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if ((core_mask12 | tension_mask12 | resolution_mask12) & UINT16_C(0xF000))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    *out_word36 = h36_pack_harmonic(
        core_mask12, tension_mask12, resolution_mask12);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_harmonic_unpack(
    uint64_t word36,
    uint16_t *out_core_mask12,
    uint16_t *out_tension_mask12,
    uint16_t *out_resolution_mask12
) {
    if (out_core_mask12 == NULL || out_tension_mask12 == NULL ||
        out_resolution_mask12 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if ((word36 & ~HHS_EXACT_PASS219_H36_WORD_MASK) != 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    *out_core_mask12 = (uint16_t)((word36 >> 24U) & UINT64_C(0x0FFF));
    *out_tension_mask12 = (uint16_t)((word36 >> 12U) & UINT64_C(0x0FFF));
    *out_resolution_mask12 = (uint16_t)(word36 & UINT64_C(0x0FFF));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_harmonic_rule(
    uint16_t rule_id,
    HHSExactPass219H36HarmonicRuleDescriptorV1 *out
) {
    const H36RuleSeed *seed;
    if (out == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (rule_id == 0U || rule_id > HHS_EXACT_PASS219_H36_RULE_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    seed = &H36_RULES[rule_id];
    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->version = h36_version_word();
    out->rule_id = rule_id;
    out->era = seed->era;
    out->function_class = seed->function_class;
    out->core_mask12 = seed->core;
    out->tension_mask12 = seed->tension;
    out->resolution_mask12 = seed->resolution;
    out->scale_mask12 = seed->scale;
    out->preferred_bass_pc12 = seed->bass;
    out->flags = seed->flags;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_harmonic_render(
    uint16_t rule_id,
    uint8_t tonic_pc12,
    uint64_t *out_word36
) {
    HHSExactPass219H36HarmonicRuleDescriptorV1 rule;
    HHSExactStatus status;
    if (out_word36 == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (tonic_pc12 >= 12U) return HHS_EXACT_STATUS_RANGE_ERROR;

    status = hhs_exact_pass219_h36_harmonic_rule(rule_id, &rule);
    if (status != HHS_EXACT_STATUS_OK) return status;
    *out_word36 = h36_pack_harmonic(
        h36_rotate12(rule.core_mask12, tonic_pc12),
        h36_rotate12(rule.tension_mask12, tonic_pc12),
        h36_rotate12(rule.resolution_mask12, tonic_pc12));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_harmonic_transpose(
    uint64_t word36,
    uint8_t semitones,
    uint64_t *out_word36
) {
    uint16_t core;
    uint16_t tension;
    uint16_t resolution;
    HHSExactStatus status;
    if (out_word36 == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_pass219_h36_harmonic_unpack(
        word36, &core, &tension, &resolution);
    if (status != HHS_EXACT_STATUS_OK) return status;
    *out_word36 = h36_pack_harmonic(
        h36_rotate12(core, semitones),
        h36_rotate12(tension, semitones),
        h36_rotate12(resolution, semitones));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_harmonic_transition(
    uint64_t source_word36,
    uint64_t target_word36,
    HHSExactPass219H36HarmonicTransitionV1 *out
) {
    uint16_t sc, st, sr, tc, tt, tr;
    uint16_t source_active;
    uint16_t target_active;
    uint32_t p;
    uint32_t cost = 0U;
    uint32_t semitone = 0U;
    HHSExactStatus status;

    if (out == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_h36_harmonic_unpack(
        source_word36, &sc, &st, &sr);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_exact_pass219_h36_harmonic_unpack(
        target_word36, &tc, &tt, &tr);
    if (status != HHS_EXACT_STATUS_OK) return status;
    (void)tr;

    source_active = (uint16_t)(sc | st);
    target_active = (uint16_t)(tc | tt);

    for (p = 0U; p < 12U; ++p) {
        if ((source_active & (UINT16_C(1) << p)) != 0U) {
            uint32_t q;
            uint32_t best = 12U;
            for (q = 0U; q < 12U; ++q) {
                if ((target_active & (UINT16_C(1) << q)) != 0U) {
                    uint32_t d = h36_distance12((uint8_t)p, (uint8_t)q);
                    if (d < best) best = d;
                }
            }
            if (best != 12U) cost += best;
        }
        if ((sr & (UINT16_C(1) << p)) != 0U) {
            uint8_t up = (uint8_t)((p + 1U) % 12U);
            uint8_t down = (uint8_t)((p + 11U) % 12U);
            if ((tc & (UINT16_C(1) << up)) != 0U ||
                (tc & (UINT16_C(1) << down)) != 0U)
                ++semitone;
        }
    }

    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->version = h36_version_word();
    out->common_tones = (uint16_t)h36_popcount12(
        (uint16_t)(source_active & target_active));
    out->semitone_resolutions = (uint16_t)semitone;
    out->exact_voice_leading_cost = (uint16_t)cost;
    out->source_pitch_count = (uint16_t)h36_popcount12(source_active);
    out->target_pitch_count = (uint16_t)h36_popcount12(target_active);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_vm_init(
    HHSExactPass219H36VMStateV1 *state
) {
    if (state == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(state, 0, sizeof(*state));
    state->struct_size = (uint32_t)sizeof(*state);
    state->version = h36_version_word();
    state->canonical_mutation_authority = 0U;
    state->canonical_hash72_authority = 0U;
    state->canonical_persistence_authority = 0U;
    state->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

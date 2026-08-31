#include "../include/hhs_pass219_harmonic36_composition_grammar_1_0.h"

#include <string.h>

#define H36_VOICE_MIN_BASS 36U
#define H36_VOICE_MAX_BASS 60U
#define H36_VOICE_MIN_TENOR 43U
#define H36_VOICE_MAX_TENOR 67U
#define H36_VOICE_MIN_ALTO 50U
#define H36_VOICE_MAX_ALTO 76U
#define H36_VOICE_MIN_SOPRANO 55U
#define H36_VOICE_MAX_SOPRANO 84U

static uint32_t h36_comp_version_word(void) {
    return (HHS_EXACT_PASS219_H36_COMPOSITION_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_H36_COMPOSITION_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_H36_COMPOSITION_VERSION_PATCH;
}

static uint8_t h36_pc(uint8_t absolute_pitch) {
    return (uint8_t)(absolute_pitch % 12U);
}

static uint16_t h36_popcount_mask12(uint16_t mask) {
    uint16_t count = 0U;
    mask &= UINT16_C(0x0FFF);
    while (mask != 0U) {
        count = (uint16_t)(count + (mask & 1U));
        mask = (uint16_t)(mask >> 1U);
    }
    return count;
}

static uint8_t h36_nth_pc(uint16_t mask, uint8_t n) {
    uint8_t pc;
    uint8_t count = 0U;
    mask &= UINT16_C(0x0FFF);
    for (pc = 0U; pc < 12U; ++pc) {
        if ((mask & (uint16_t)(UINT16_C(1) << pc)) != 0U) {
            if (count == n) return pc;
            ++count;
        }
    }
    return 0U;
}

static uint8_t h36_nearest_pitch(
    uint16_t mask12,
    uint8_t minimum,
    uint8_t maximum,
    uint8_t anchor,
    uint8_t floor_pitch
) {
    uint16_t best_distance = UINT16_MAX;
    uint8_t best = minimum;
    uint16_t p;
    if (floor_pitch > minimum) minimum = floor_pitch;
    for (p = minimum; p <= maximum; ++p) {
        uint8_t pc = (uint8_t)(p % 12U);
        if ((mask12 & (uint16_t)(UINT16_C(1) << pc)) != 0U) {
            uint16_t d = p >= anchor
                ? (uint16_t)(p - anchor) : (uint16_t)(anchor - p);
            if (d < best_distance || (d == best_distance && p < best)) {
                best_distance = d;
                best = (uint8_t)p;
            }
        }
    }
    return best;
}

static uint16_t h36_context_for_rule(uint16_t rule) {
    uint16_t flags = 0U;
    if (rule == HHS_EXACT_PASS219_H36_RULE_SECONDARY_V_OF_V ||
        rule == HHS_EXACT_PASS219_H36_RULE_SECONDARY_VII_OF_V ||
        rule == HHS_EXACT_PASS219_H36_RULE_EXTENDED_DOMINANT_CHAIN ||
        rule == HHS_EXACT_PASS219_H36_RULE_RELATED_II_TRITONE)
        flags |= HHS_EXACT_PASS219_H36_CONTEXT_SECONDARY_FUNCTION;
    if (rule == HHS_EXACT_PASS219_H36_RULE_BORROWED_IV_MINOR ||
        rule == HHS_EXACT_PASS219_H36_RULE_BORROWED_BVI_MAJOR ||
        rule == HHS_EXACT_PASS219_H36_RULE_MINOR_PLAGAL)
        flags |= HHS_EXACT_PASS219_H36_CONTEXT_MODAL_INTERCHANGE;
    if (rule >= HHS_EXACT_PASS219_H36_RULE_V7_ALTERED &&
        rule <= HHS_EXACT_PASS219_H36_RULE_V7_WHOLE_TONE)
        flags |= HHS_EXACT_PASS219_H36_CONTEXT_ALTERED_DOMINANT;
    if (rule == HHS_EXACT_PASS219_H36_RULE_UPPER_STRUCTURE_II_OVER_V7 ||
        rule == HHS_EXACT_PASS219_H36_RULE_UPPER_STRUCTURE_BIII_OVER_V7)
        flags |= HHS_EXACT_PASS219_H36_CONTEXT_UPPER_STRUCTURE;
    if (rule == HHS_EXACT_PASS219_H36_RULE_POLYCHORD_DOMINANT)
        flags |= HHS_EXACT_PASS219_H36_CONTEXT_POLYCHORD;
    if (rule == HHS_EXACT_PASS219_H36_RULE_CONSTANT_STRUCTURE_MAJOR7 ||
        rule == HHS_EXACT_PASS219_H36_RULE_PARALLEL_CHROMATIC_SEQUENCE)
        flags |= HHS_EXACT_PASS219_H36_CONTEXT_CONSTANT_STRUCTURE;
    if (rule == HHS_EXACT_PASS219_H36_RULE_PIVOT_CHORD_MODULATION ||
        rule == HHS_EXACT_PASS219_H36_RULE_ENHARMONIC_DIM7_MODULATION ||
        rule == HHS_EXACT_PASS219_H36_RULE_ENHARMONIC_GER6_DOM7)
        flags |= HHS_EXACT_PASS219_H36_CONTEXT_MODULATION;
    if (rule >= HHS_EXACT_PASS219_H36_RULE_DORIAN_MODAL_TONIC &&
        rule <= HHS_EXACT_PASS219_H36_RULE_QUARTAL_MODAL)
        flags |= HHS_EXACT_PASS219_H36_CONTEXT_MODAL;
    if (rule == HHS_EXACT_PASS219_H36_RULE_EQUAL_DIVISION_MAJOR_THIRDS ||
        rule == HHS_EXACT_PASS219_H36_RULE_EQUAL_DIVISION_MINOR_THIRDS ||
        rule == HHS_EXACT_PASS219_H36_RULE_COLTRANE_THREE_TONIC ||
        rule == HHS_EXACT_PASS219_H36_RULE_FOUR_TONIC_MINOR_THIRDS)
        flags |= HHS_EXACT_PASS219_H36_CONTEXT_SYMMETRIC;
    return flags;
}

static uint32_t h36_relation_for_rules(uint16_t source, uint16_t target) {
    (void)target;
    if (source == HHS_EXACT_PASS219_H36_RULE_NEAPOLITAN6)
        return HHS_EXACT_PASS219_H36_RELATION_NEAPOLITAN;
    if (source >= HHS_EXACT_PASS219_H36_RULE_ITALIAN_AUG6 &&
        source <= HHS_EXACT_PASS219_H36_RULE_SWISS_AUG6)
        return HHS_EXACT_PASS219_H36_RELATION_AUGMENTED_SIXTH;
    if (source == HHS_EXACT_PASS219_H36_RULE_TRITONE_SUB_BII7 ||
        source == HHS_EXACT_PASS219_H36_RULE_RELATED_II_TRITONE)
        return HHS_EXACT_PASS219_H36_RELATION_TRITONE_SUBSTITUTION;
    if (source == HHS_EXACT_PASS219_H36_RULE_BACKDOOR_BVII7)
        return HHS_EXACT_PASS219_H36_RELATION_BACKDOOR;
    if (source >= HHS_EXACT_PASS219_H36_RULE_CHROMATIC_MEDIANT_BIII &&
        source <= HHS_EXACT_PASS219_H36_RULE_CHROMATIC_MEDIANT_VI)
        return HHS_EXACT_PASS219_H36_RELATION_CHROMATIC_MEDIANT;
    if (source == HHS_EXACT_PASS219_H36_RULE_ENHARMONIC_DIM7_MODULATION ||
        source == HHS_EXACT_PASS219_H36_RULE_ENHARMONIC_GER6_DOM7)
        return HHS_EXACT_PASS219_H36_RELATION_ENHARMONIC_REINTERPRETATION;
    if (source == HHS_EXACT_PASS219_H36_RULE_EQUAL_DIVISION_MAJOR_THIRDS ||
        source == HHS_EXACT_PASS219_H36_RULE_EQUAL_DIVISION_MINOR_THIRDS ||
        source == HHS_EXACT_PASS219_H36_RULE_COLTRANE_THREE_TONIC ||
        source == HHS_EXACT_PASS219_H36_RULE_FOUR_TONIC_MINOR_THIRDS)
        return HHS_EXACT_PASS219_H36_RELATION_EQUAL_DIVISION;
    if (source == HHS_EXACT_PASS219_H36_RULE_CONSTANT_STRUCTURE_MAJOR7 ||
        source == HHS_EXACT_PASS219_H36_RULE_PARALLEL_CHROMATIC_SEQUENCE)
        return HHS_EXACT_PASS219_H36_RELATION_CONSTANT_STRUCTURE;
    if (source >= HHS_EXACT_PASS219_H36_RULE_DORIAN_MODAL_TONIC &&
        source <= HHS_EXACT_PASS219_H36_RULE_QUARTAL_MODAL)
        return HHS_EXACT_PASS219_H36_RELATION_MODAL;
    if (source >= HHS_EXACT_PASS219_H36_RULE_V7_ALTERED &&
        source <= HHS_EXACT_PASS219_H36_RULE_V7_WHOLE_TONE)
        return HHS_EXACT_PASS219_H36_RELATION_JAZZ_CHORD_SCALE;
    if (source == HHS_EXACT_PASS219_H36_RULE_UPPER_STRUCTURE_II_OVER_V7 ||
        source == HHS_EXACT_PASS219_H36_RULE_UPPER_STRUCTURE_BIII_OVER_V7 ||
        source == HHS_EXACT_PASS219_H36_RULE_POLYCHORD_DOMINANT)
        return HHS_EXACT_PASS219_H36_RELATION_UPPER_STRUCTURE;
    if (source == HHS_EXACT_PASS219_H36_RULE_SECONDARY_V_OF_V ||
        source == HHS_EXACT_PASS219_H36_RULE_SECONDARY_VII_OF_V ||
        source == HHS_EXACT_PASS219_H36_RULE_EXTENDED_DOMINANT_CHAIN)
        return HHS_EXACT_PASS219_H36_RELATION_SECONDARY_FUNCTION;
    if (source == HHS_EXACT_PASS219_H36_RULE_BORROWED_IV_MINOR ||
        source == HHS_EXACT_PASS219_H36_RULE_BORROWED_BVI_MAJOR ||
        source == HHS_EXACT_PASS219_H36_RULE_MINOR_PLAGAL)
        return HHS_EXACT_PASS219_H36_RELATION_MODAL_INTERCHANGE;
    if (source == HHS_EXACT_PASS219_H36_RULE_COMMON_TONE_DIM7 ||
        source == HHS_EXACT_PASS219_H36_RULE_DIMINISHED_PASSING_TO_II)
        return HHS_EXACT_PASS219_H36_RELATION_SYMMETRIC;
    return HHS_EXACT_PASS219_H36_RELATION_FUNCTIONAL;
}

static int h36_rule_is_tonic(uint16_t rule) {
    return rule == HHS_EXACT_PASS219_H36_RULE_I_MAJOR ||
           rule == HHS_EXACT_PASS219_H36_RULE_JAZZ_I_MAJOR7 ||
           rule == HHS_EXACT_PASS219_H36_RULE_MINOR_I_MINMAJ7 ||
           rule == HHS_EXACT_PASS219_H36_RULE_MAJOR6_TONIC ||
           rule == HHS_EXACT_PASS219_H36_RULE_MINOR6_TONIC ||
           rule == HHS_EXACT_PASS219_H36_RULE_MAJOR69_TONIC ||
           rule == HHS_EXACT_PASS219_H36_RULE_MINOR69_TONIC;
}

static int h36_rule_is_dominant(uint16_t rule) {
    return rule == HHS_EXACT_PASS219_H36_RULE_V7 ||
           rule == HHS_EXACT_PASS219_H36_RULE_JAZZ_V7 ||
           rule == HHS_EXACT_PASS219_H36_RULE_MINOR_V7_B9 ||
           rule == HHS_EXACT_PASS219_H36_RULE_TRITONE_SUB_BII7 ||
           rule == HHS_EXACT_PASS219_H36_RULE_BACKDOOR_BVII7 ||
           (rule >= HHS_EXACT_PASS219_H36_RULE_V7_ALTERED &&
            rule <= HHS_EXACT_PASS219_H36_RULE_V7_WHOLE_TONE) ||
           rule == HHS_EXACT_PASS219_H36_RULE_POLYCHORD_DOMINANT;
}

static uint32_t h36_cadence_for(
    const HHSExactPass219H36CompositionStateV1 *source,
    const HHSExactPass219H36CompositionStateV1 *target
) {
    if (h36_rule_is_dominant(source->harmonic_rule64) &&
        h36_rule_is_tonic(target->harmonic_rule64)) {
        if (source->harmonic_rule64 ==
            HHS_EXACT_PASS219_H36_RULE_BACKDOOR_BVII7)
            return HHS_EXACT_PASS219_H36_CADENCE_BACKDOOR;
        if (target->inversion == 0U &&
            target->soprano_pc12 == target->tonic_pc12)
            return HHS_EXACT_PASS219_H36_CADENCE_PERFECT_AUTHENTIC;
        return HHS_EXACT_PASS219_H36_CADENCE_IMPERFECT_AUTHENTIC;
    }
    if (h36_rule_is_dominant(source->harmonic_rule64) &&
        target->harmonic_rule64 == HHS_EXACT_PASS219_H36_RULE_VI_MINOR7)
        return HHS_EXACT_PASS219_H36_CADENCE_DECEPTIVE;
    if ((source->harmonic_rule64 ==
         HHS_EXACT_PASS219_H36_RULE_BORROWED_IV_MINOR ||
         source->harmonic_rule64 ==
         HHS_EXACT_PASS219_H36_RULE_MINOR_PLAGAL) &&
        h36_rule_is_tonic(target->harmonic_rule64))
        return HHS_EXACT_PASS219_H36_CADENCE_PLAGAL;
    if (!h36_rule_is_dominant(source->harmonic_rule64) &&
        h36_rule_is_dominant(target->harmonic_rule64))
        return HHS_EXACT_PASS219_H36_CADENCE_HALF;
    if ((source->context_flags | target->context_flags) &
        HHS_EXACT_PASS219_H36_CONTEXT_MODAL)
        return HHS_EXACT_PASS219_H36_CADENCE_MODAL;
    return HHS_EXACT_PASS219_H36_CADENCE_NONE;
}

static int h36_progression_allowed(uint16_t source, uint16_t target) {
    if (source == target) return 1;

    if (source == HHS_EXACT_PASS219_H36_RULE_JAZZ_II_MINOR7)
        return target == HHS_EXACT_PASS219_H36_RULE_JAZZ_V7 ||
               target == HHS_EXACT_PASS219_H36_RULE_TRITONE_SUB_BII7 ||
               target == HHS_EXACT_PASS219_H36_RULE_V7_ALTERED;
    if (source == HHS_EXACT_PASS219_H36_RULE_JAZZ_V7 ||
        (source >= HHS_EXACT_PASS219_H36_RULE_V7_ALTERED &&
         source <= HHS_EXACT_PASS219_H36_RULE_V7_WHOLE_TONE))
        return h36_rule_is_tonic(target) ||
               target == HHS_EXACT_PASS219_H36_RULE_VI_MINOR7;
    if (source == HHS_EXACT_PASS219_H36_RULE_MINOR_II_HALFDIM7)
        return target == HHS_EXACT_PASS219_H36_RULE_MINOR_V7_B9;
    if (source == HHS_EXACT_PASS219_H36_RULE_MINOR_V7_B9)
        return target == HHS_EXACT_PASS219_H36_RULE_MINOR_I_MINMAJ7;
    if (source == HHS_EXACT_PASS219_H36_RULE_TRITONE_SUB_BII7 ||
        source == HHS_EXACT_PASS219_H36_RULE_BACKDOOR_BVII7)
        return h36_rule_is_tonic(target);
    if (source == HHS_EXACT_PASS219_H36_RULE_NEAPOLITAN6 ||
        (source >= HHS_EXACT_PASS219_H36_RULE_ITALIAN_AUG6 &&
         source <= HHS_EXACT_PASS219_H36_RULE_SWISS_AUG6))
        return h36_rule_is_dominant(target);
    if (source == HHS_EXACT_PASS219_H36_RULE_SECONDARY_V_OF_V ||
        source == HHS_EXACT_PASS219_H36_RULE_SECONDARY_VII_OF_V)
        return h36_rule_is_dominant(target);
    if (source == HHS_EXACT_PASS219_H36_RULE_RELATED_II_TRITONE)
        return target == HHS_EXACT_PASS219_H36_RULE_TRITONE_SUB_BII7;
    if (source == HHS_EXACT_PASS219_H36_RULE_MINOR_PLAGAL ||
        source == HHS_EXACT_PASS219_H36_RULE_BORROWED_IV_MINOR)
        return h36_rule_is_tonic(target);
    if (source == HHS_EXACT_PASS219_H36_RULE_DIMINISHED_PASSING_TO_II)
        return target == HHS_EXACT_PASS219_H36_RULE_JAZZ_II_MINOR7 ||
               target == HHS_EXACT_PASS219_H36_RULE_II_MINOR7;
    if (source == HHS_EXACT_PASS219_H36_RULE_COLTRANE_THREE_TONIC ||
        source == HHS_EXACT_PASS219_H36_RULE_FOUR_TONIC_MINOR_THIRDS ||
        source == HHS_EXACT_PASS219_H36_RULE_CONSTANT_STRUCTURE_MAJOR7 ||
        source == HHS_EXACT_PASS219_H36_RULE_PARALLEL_CHROMATIC_SEQUENCE)
        return 1;
    return 1;
}

static uint16_t h36_parallel_perfects(
    const HHSExactPass219H36CompositionStateV1 *a,
    const HHSExactPass219H36CompositionStateV1 *b
) {
    uint16_t count = 0U;
    uint8_t i;
    uint8_t j;
    for (i = 0U; i < 4U; ++i) {
        for (j = (uint8_t)(i + 1U); j < 4U; ++j) {
            int a_motion = (int)b->voices[i] - (int)a->voices[i];
            int b_motion = (int)b->voices[j] - (int)a->voices[j];
            uint8_t old_interval =
                (uint8_t)((a->voices[j] - a->voices[i]) % 12U);
            uint8_t new_interval =
                (uint8_t)((b->voices[j] - b->voices[i]) % 12U);
            if (a_motion != 0 && b_motion != 0 &&
                ((a_motion > 0 && b_motion > 0) ||
                 (a_motion < 0 && b_motion < 0)) &&
                (old_interval == 0U || old_interval == 7U) &&
                new_interval == old_interval)
                ++count;
        }
    }
    return count;
}

static uint16_t h36_contrary_pairs(
    const HHSExactPass219H36CompositionStateV1 *a,
    const HHSExactPass219H36CompositionStateV1 *b
) {
    uint16_t count = 0U;
    uint8_t i;
    uint8_t j;
    for (i = 0U; i < 4U; ++i) {
        for (j = (uint8_t)(i + 1U); j < 4U; ++j) {
            int x = (int)b->voices[i] - (int)a->voices[i];
            int y = (int)b->voices[j] - (int)a->voices[j];
            if ((x < 0 && y > 0) || (x > 0 && y < 0))
                ++count;
        }
    }
    return count;
}

static uint16_t h36_unresolved_tendencies(
    const HHSExactPass219H36CompositionStateV1 *a,
    const HHSExactPass219H36CompositionStateV1 *b
) {
    uint16_t unresolved = 0U;
    uint8_t v;
    for (v = 0U; v < 4U; ++v) {
        uint8_t source_pc = h36_pc(a->voices[v]);
        uint8_t target_pc = h36_pc(b->voices[v]);
        if ((a->tendency_mask12 &
             (uint16_t)(UINT16_C(1) << source_pc)) != 0U) {
            uint8_t up = (uint8_t)((source_pc + 1U) % 12U);
            uint8_t down = (uint8_t)((source_pc + 11U) % 12U);
            if (target_pc != source_pc &&
                target_pc != up && target_pc != down)
                ++unresolved;
        }
    }
    return unresolved;
}

uint32_t hhs_exact_pass219_h36_composition_version(void) {
    return h36_comp_version_word();
}

HHSExactStatus hhs_exact_pass219_h36_composition_state(
    uint16_t harmonic_rule64,
    uint8_t tonic_pc12,
    uint8_t key_center_pc12,
    uint8_t mode,
    uint8_t inversion,
    uint8_t secondary_target_pc12,
    uint8_t target_key_center_pc12,
    uint16_t context_flags,
    const HHSExactPass219H36CompositionStateV1 *previous,
    HHSExactPass219H36CompositionStateV1 *out_state
) {
    HHSExactPass219H36HarmonicRuleDescriptorV1 rule;
    uint16_t core;
    uint16_t tension;
    uint16_t resolution;
    uint16_t active;
    uint16_t chord_count;
    uint8_t bass_pc;
    uint8_t anchors[4] = {48U, 55U, 60U, 67U};
    uint8_t mins[4] = {
        H36_VOICE_MIN_BASS, H36_VOICE_MIN_TENOR,
        H36_VOICE_MIN_ALTO, H36_VOICE_MIN_SOPRANO
    };
    uint8_t maxs[4] = {
        H36_VOICE_MAX_BASS, H36_VOICE_MAX_TENOR,
        H36_VOICE_MAX_ALTO, H36_VOICE_MAX_SOPRANO
    };
    uint8_t i;
    HHSExactStatus status;

    if (out_state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (harmonic_rule64 == 0U ||
        harmonic_rule64 > HHS_EXACT_PASS219_H36_RULE_COUNT ||
        tonic_pc12 >= 12U || key_center_pc12 >= 12U ||
        mode < HHS_EXACT_PASS219_H36_MODE_MAJOR ||
        mode > HHS_EXACT_PASS219_H36_MODE_CHROMATIC ||
        inversion > 3U ||
        (secondary_target_pc12 != HHS_EXACT_PASS219_H36_NO_SECONDARY_TARGET &&
         secondary_target_pc12 >= 12U) ||
        target_key_center_pc12 >= 12U)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    status = hhs_exact_pass219_h36_harmonic_rule(
        harmonic_rule64, &rule);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_h36_harmonic_render(
        harmonic_rule64, tonic_pc12, &out_state->rendered_word36);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_h36_harmonic_unpack(
        out_state->rendered_word36, &core, &tension, &resolution);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    active = (uint16_t)(core | tension);
    chord_count = h36_popcount_mask12(core);
    if (chord_count == 0U)
        chord_count = h36_popcount_mask12(active);
    if (chord_count == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    bass_pc = h36_nth_pc(
        core != 0U ? core : active,
        (uint8_t)(inversion % chord_count));

    memset(out_state, 0, sizeof(*out_state));
    out_state->struct_size = (uint32_t)sizeof(*out_state);
    out_state->version = h36_comp_version_word();
    out_state->tonic_pc12 = tonic_pc12;
    out_state->key_center_pc12 = key_center_pc12;
    out_state->mode = mode;
    out_state->harmonic_rule64 = (uint8_t)harmonic_rule64;
    out_state->inversion = inversion;
    out_state->voice_count = HHS_EXACT_PASS219_H36_COMPOSITION_VOICES;
    out_state->secondary_target_pc12 = secondary_target_pc12;
    out_state->target_key_center_pc12 = target_key_center_pc12;
    out_state->context_flags =
        (uint16_t)(context_flags | h36_context_for_rule(harmonic_rule64));
    out_state->tendency_mask12 = resolution;
    out_state->chord_mask12 = active;
    out_state->scale_mask12 = rule.scale_mask12;
    status = hhs_exact_pass219_h36_harmonic_render(
        harmonic_rule64, tonic_pc12, &out_state->rendered_word36);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (previous != NULL) {
        if (previous->struct_size != sizeof(*previous) ||
            previous->version != h36_comp_version_word())
            return HHS_EXACT_STATUS_VERSION_MISMATCH;
        memcpy(anchors, previous->voices, sizeof(anchors));
    }

    {
        uint16_t bass_mask = (uint16_t)(UINT16_C(1) << bass_pc);
        out_state->voices[0] = h36_nearest_pitch(
            bass_mask, mins[0], maxs[0], anchors[0], mins[0]);
    }
    for (i = 1U; i < 4U; ++i) {
        uint8_t floor_pitch = (uint8_t)(out_state->voices[i - 1U] + 1U);
        out_state->voices[i] = h36_nearest_pitch(
            active, mins[i], maxs[i], anchors[i], floor_pitch);
    }

    out_state->bass_pc12 = h36_pc(out_state->voices[0]);
    out_state->soprano_pc12 = h36_pc(out_state->voices[3]);
    out_state->voice_order_valid =
        (uint8_t)(out_state->voices[0] < out_state->voices[1] &&
                  out_state->voices[1] < out_state->voices[2] &&
                  out_state->voices[2] < out_state->voices[3]);
    out_state->inversion_valid =
        (uint8_t)(out_state->bass_pc12 == bass_pc);
    out_state->fixed_operation64_preserved = 1U;
    out_state->canonical_mutation_authority = 0U;
    out_state->canonical_hash72_authority = 0U;
    out_state->canonical_persistence_authority = 0U;
    out_state->floating_point_authority = 0U;

    if (out_state->voice_order_valid == 0U ||
        out_state->inversion_valid == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_composition_transition(
    const HHSExactPass219H36CompositionStateV1 *source,
    const HHSExactPass219H36CompositionStateV1 *target,
    HHSExactPass219H36CompositionTransitionV1 *out_transition
) {
    HHSExactPass219H36HarmonicTransitionV1 base;
    uint16_t cost = 0U;
    uint8_t i;
    uint16_t unresolved;
    uint16_t parallels;
    HHSExactStatus status;

    if (source == NULL || target == NULL || out_transition == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (source->struct_size != sizeof(*source) ||
        target->struct_size != sizeof(*target) ||
        source->version != h36_comp_version_word() ||
        target->version != h36_comp_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (source->fixed_operation64_preserved != 1U ||
        target->fixed_operation64_preserved != 1U ||
        source->canonical_mutation_authority != 0U ||
        target->canonical_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_h36_harmonic_transition(
        source->rendered_word36, target->rendered_word36, &base);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    for (i = 0U; i < 4U; ++i) {
        cost = (uint16_t)(cost +
            (source->voices[i] >= target->voices[i]
                ? source->voices[i] - target->voices[i]
                : target->voices[i] - source->voices[i]));
    }
    unresolved = h36_unresolved_tendencies(source, target);
    parallels = h36_parallel_perfects(source, target);

    memset(out_transition, 0, sizeof(*out_transition));
    out_transition->struct_size = (uint32_t)sizeof(*out_transition);
    out_transition->version = h36_comp_version_word();
    out_transition->source = *source;
    out_transition->target = *target;
    out_transition->relation =
        h36_relation_for_rules(
            source->harmonic_rule64, target->harmonic_rule64);
    out_transition->cadence = h36_cadence_for(source, target);
    out_transition->exact_voice_leading_cost = cost;
    out_transition->common_tones = base.common_tones;
    out_transition->semitone_resolutions = base.semitone_resolutions;
    out_transition->contrary_motion_pairs =
        h36_contrary_pairs(source, target);
    out_transition->unresolved_tendency_count = unresolved;
    out_transition->parallel_perfect_count = parallels;
    out_transition->progression_allowed = (uint8_t)h36_progression_allowed(
        source->harmonic_rule64, target->harmonic_rule64);
    out_transition->cadence_match =
        (uint8_t)(out_transition->cadence !=
                  HHS_EXACT_PASS219_H36_CADENCE_NONE);
    out_transition->tendency_resolution_valid =
        (uint8_t)(unresolved == 0U);
    out_transition->voice_leading_valid =
        (uint8_t)(source->voice_order_valid != 0U &&
                  target->voice_order_valid != 0U);
    out_transition->modulation_observed =
        (uint8_t)(source->key_center_pc12 != target->key_center_pc12 ||
                  source->target_key_center_pc12 !=
                  target->target_key_center_pc12 ||
                  ((source->context_flags | target->context_flags) &
                   HHS_EXACT_PASS219_H36_CONTEXT_MODULATION) != 0U);
    out_transition->grammar_penalty =
        (uint16_t)((out_transition->progression_allowed ? 0U : 1000U) +
                   unresolved * 100U +
                   parallels * 50U);
    out_transition->fixed_operation64_preserved = 1U;
    out_transition->canonical_mutation_authority = 0U;
    out_transition->canonical_hash72_authority = 0U;
    out_transition->canonical_persistence_authority = 0U;
    out_transition->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_composition_candidate(
    uint32_t candidate_id,
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *source_occurrence,
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *target_occurrence,
    const HHSExactPass219H36CompositionTransitionV1 *transition,
    HHSExactPass219H36CompositionCandidateV1 *out_candidate
) {
    HHSExactStatus status;
    uint32_t score;

    if (source_occurrence == NULL || target_occurrence == NULL ||
        transition == NULL || out_candidate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (transition->struct_size != sizeof(*transition) ||
        transition->version != h36_comp_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (source_occurrence->harmonic_rule64 !=
        transition->source.harmonic_rule64 ||
        target_occurrence->harmonic_rule64 !=
        transition->target.harmonic_rule64)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_candidate, 0, sizeof(*out_candidate));
    out_candidate->struct_size = (uint32_t)sizeof(*out_candidate);
    out_candidate->version = h36_comp_version_word();
    out_candidate->candidate_id = candidate_id;
    out_candidate->composition = *transition;

    status = hhs_exact_pass219_h36_branch_candidate(
        candidate_id,
        transition->source.tonic_pc12,
        source_occurrence,
        target_occurrence,
        &out_candidate->directional_branch);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    score =
        (uint32_t)transition->grammar_penalty * 100000U +
        (uint32_t)transition->unresolved_tendency_count * 10000U +
        (uint32_t)transition->parallel_perfect_count * 1000U +
        (uint32_t)transition->exact_voice_leading_cost * 10U +
        (uint32_t)out_candidate->directional_branch.phase_distance;
    out_candidate->exact_rank_score = score;
    out_candidate->candidate_only = 1U;
    out_candidate->hash216_direction_preserved = 1U;
    out_candidate->pass128_evidence_compatible = 1U;
    out_candidate->singleton_vm81_admission_required = 1U;
    out_candidate->canonical_mutation_authority = 0U;
    out_candidate->canonical_hash72_authority = 0U;
    out_candidate->canonical_persistence_authority = 0U;
    out_candidate->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

static int h36_comp_candidate_less(
    const HHSExactPass219H36CompositionCandidateV1 *a,
    const HHSExactPass219H36CompositionCandidateV1 *b
) {
    if (a->composition.progression_allowed !=
        b->composition.progression_allowed)
        return a->composition.progression_allowed >
               b->composition.progression_allowed;
    if (a->composition.unresolved_tendency_count !=
        b->composition.unresolved_tendency_count)
        return a->composition.unresolved_tendency_count <
               b->composition.unresolved_tendency_count;
    if (a->composition.parallel_perfect_count !=
        b->composition.parallel_perfect_count)
        return a->composition.parallel_perfect_count <
               b->composition.parallel_perfect_count;
    if (a->exact_rank_score != b->exact_rank_score)
        return a->exact_rank_score < b->exact_rank_score;
    return a->candidate_id < b->candidate_id;
}

static const HHSExactPass219H36CompositionCandidateV1 *h36_comp_find(
    const HHSExactPass219H36CompositionCandidateV1 *candidates,
    size_t count,
    uint32_t id
) {
    size_t i;
    for (i = 0U; i < count; ++i)
        if (candidates[i].candidate_id == id)
            return &candidates[i];
    return NULL;
}

HHSExactStatus hhs_exact_pass219_h36_composition_rank(
    const HHSExactPass219H36CompositionCandidateV1 *candidates,
    size_t candidate_count,
    HHSExactPass219H36CompositionRankingV1 *out_ranking
) {
    size_t i;
    if (candidates == NULL || out_ranking == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (candidate_count == 0U ||
        candidate_count > HHS_EXACT_PASS219_H36_COMPOSITION_MAX_CANDIDATES)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_ranking, 0, sizeof(*out_ranking));
    out_ranking->struct_size = (uint32_t)sizeof(*out_ranking);
    out_ranking->version = h36_comp_version_word();
    out_ranking->candidate_count = (uint32_t)candidate_count;

    for (i = 0U; i < candidate_count; ++i) {
        size_t j;
        if (candidates[i].struct_size != sizeof(candidates[i]) ||
            candidates[i].version != h36_comp_version_word())
            return HHS_EXACT_STATUS_VERSION_MISMATCH;
        if (candidates[i].candidate_only != 1U ||
            candidates[i].canonical_mutation_authority != 0U ||
            candidates[i].floating_point_authority != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        for (j = 0U; j < i; ++j)
            if (candidates[j].candidate_id == candidates[i].candidate_id)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        out_ranking->ranked_candidate_ids[i] = candidates[i].candidate_id;
    }

    for (i = 1U; i < candidate_count; ++i) {
        uint32_t key = out_ranking->ranked_candidate_ids[i];
        const HHSExactPass219H36CompositionCandidateV1 *key_candidate =
            h36_comp_find(candidates, candidate_count, key);
        size_t j = i;
        while (j > 0U) {
            const HHSExactPass219H36CompositionCandidateV1 *prior =
                h36_comp_find(
                    candidates, candidate_count,
                    out_ranking->ranked_candidate_ids[j - 1U]);
            if (key_candidate == NULL || prior == NULL)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            if (!h36_comp_candidate_less(key_candidate, prior))
                break;
            out_ranking->ranked_candidate_ids[j] =
                out_ranking->ranked_candidate_ids[j - 1U];
            --j;
        }
        out_ranking->ranked_candidate_ids[j] = key;
    }

    out_ranking->grammar_first = 1U;
    out_ranking->exact_integer_ranking = 1U;
    out_ranking->stable_candidate_id_tie_break = 1U;
    out_ranking->candidate_only = 1U;
    out_ranking->canonical_mutation_authority = 0U;
    out_ranking->canonical_hash72_authority = 0U;
    out_ranking->canonical_persistence_authority = 0U;
    out_ranking->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_composition_ranking_validate(
    const HHSExactPass219H36CompositionCandidateV1 *candidates,
    size_t candidate_count,
    const HHSExactPass219H36CompositionRankingV1 *ranking
) {
    HHSExactPass219H36CompositionRankingV1 expected;
    HHSExactStatus status;

    if (ranking == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (ranking->struct_size != sizeof(*ranking) ||
        ranking->version != h36_comp_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    status = hhs_exact_pass219_h36_composition_rank(
        candidates, candidate_count, &expected);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return memcmp(ranking, &expected, sizeof(expected)) == 0
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

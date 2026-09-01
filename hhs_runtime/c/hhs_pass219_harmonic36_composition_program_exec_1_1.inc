#include "../include/hhs_pass219_harmonic36_composition_grammar_1_0.h"

uint32_t hhs_exact_pass219_h36_composition_template_count(void) {
    return HHS_EXACT_PASS219_H36_COMPOSITION_TEMPLATE_COUNT;
}

HHSExactStatus hhs_exact_pass219_h36_composition_program_build(
    uint32_t template_id,
    uint8_t root_tonic_pc12,
    HHSExactPass219H36CompositionProgramV1 *out_program
) {
    const H36CompositionProgramTemplateSeed *seed;
    const HHSExactPass219H36CompositionStateV1 *previous = NULL;
    uint32_t i;

    if (out_program == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (template_id == 0U ||
        template_id > HHS_EXACT_PASS219_H36_COMPOSITION_TEMPLATE_COUNT ||
        root_tonic_pc12 >= 12U)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    seed = &H36_COMPOSITION_TEMPLATES[template_id];
    if (seed->step_count < 2U ||
        seed->step_count > HHS_EXACT_PASS219_H36_COMPOSITION_MAX_PROGRAM_STEPS)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_program, 0, sizeof(*out_program));
    out_program->struct_size = (uint32_t)sizeof(*out_program);
    out_program->version = hhs_exact_pass219_h36_composition_version();
    out_program->template_id = template_id;
    out_program->root_tonic_pc12 = root_tonic_pc12;
    out_program->step_count = seed->step_count;

    for (i = 0U; i < seed->step_count; ++i) {
        const H36CompositionProgramStepSeed *step = &seed->steps[i];
        uint8_t tonic =
            (uint8_t)((root_tonic_pc12 + step->tonic_offset12) % 12U);
        uint8_t secondary = HHS_EXACT_PASS219_H36_NO_SECONDARY_TARGET;
        HHSExactStatus status;

        if (step->secondary_target_offset12 >= 0) {
            secondary = (uint8_t)(
                (root_tonic_pc12 +
                 (uint8_t)step->secondary_target_offset12) % 12U
            );
        }

        status = hhs_exact_pass219_h36_composition_state(
            step->rule64,
            tonic,
            tonic,
            step->mode,
            step->inversion,
            secondary,
            tonic,
            step->context_flags,
            previous,
            &out_program->states[i]
        );
        if (status != HHS_EXACT_STATUS_OK)
            return status;

        if (i > 0U) {
            HHSExactPass219H36CompositionTransitionV1 *transition =
                &out_program->transitions[i - 1U];

            status = hhs_exact_pass219_h36_composition_transition(
                &out_program->states[i - 1U],
                &out_program->states[i],
                transition
            );
            if (status != HHS_EXACT_STATUS_OK)
                return status;

            out_program->exact_total_voice_leading_cost =
                (uint16_t)(
                    out_program->exact_total_voice_leading_cost +
                    transition->exact_voice_leading_cost
                );
            out_program->total_grammar_penalty =
                (uint16_t)(
                    out_program->total_grammar_penalty +
                    transition->grammar_penalty
                );
            out_program->total_unresolved_tendencies =
                (uint16_t)(
                    out_program->total_unresolved_tendencies +
                    transition->unresolved_tendency_count
                );
            out_program->total_parallel_perfects =
                (uint16_t)(
                    out_program->total_parallel_perfects +
                    transition->parallel_perfect_count
                );
            if (transition->modulation_observed != 0U)
                out_program->modulation_count += 1U;
        }

        previous = &out_program->states[i];
    }

    out_program->fixed_operation64_preserved = 1U;
    out_program->deterministic_replay = 1U;
    out_program->canonical_mutation_authority = 0U;
    out_program->canonical_hash72_authority = 0U;
    out_program->canonical_persistence_authority = 0U;
    out_program->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_composition_program_validate(
    const HHSExactPass219H36CompositionProgramV1 *program
) {
    HHSExactPass219H36CompositionProgramV1 expected;
    HHSExactStatus status;

    if (program == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (program->struct_size != sizeof(*program) ||
        program->version != hhs_exact_pass219_h36_composition_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (program->fixed_operation64_preserved != 1U ||
        program->deterministic_replay != 1U ||
        program->canonical_mutation_authority != 0U ||
        program->canonical_hash72_authority != 0U ||
        program->canonical_persistence_authority != 0U ||
        program->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_h36_composition_program_build(
        program->template_id,
        program->root_tonic_pc12,
        &expected
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return memcmp(program, &expected, sizeof(expected)) == 0
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

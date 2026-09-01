#include "hhs_pass219_harmonic36_composition_grammar_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>

int main(void) {
    uint32_t template_id;
    uint8_t tonic;

    assert(hhs_exact_pass219_h36_composition_template_count() ==
           HHS_EXACT_PASS219_H36_COMPOSITION_TEMPLATE_COUNT);

    for (template_id = 1U;
         template_id <= HHS_EXACT_PASS219_H36_COMPOSITION_TEMPLATE_COUNT;
         ++template_id) {
        for (tonic = 0U; tonic < 12U; ++tonic) {
            HHSExactPass219H36CompositionProgramV1 program;
            uint32_t i;

            assert(hhs_exact_pass219_h36_composition_program_build(
                template_id, tonic, &program) == HHS_EXACT_STATUS_OK);
            assert(hhs_exact_pass219_h36_composition_program_validate(
                &program) == HHS_EXACT_STATUS_OK);

            assert(program.template_id == template_id);
            assert(program.root_tonic_pc12 == tonic);
            assert(program.step_count >= 2U);
            assert(program.step_count <=
                   HHS_EXACT_PASS219_H36_COMPOSITION_MAX_PROGRAM_STEPS);
            assert(program.fixed_operation64_preserved == 1U);
            assert(program.deterministic_replay == 1U);
            assert(program.canonical_mutation_authority == 0U);
            assert(program.canonical_hash72_authority == 0U);
            assert(program.canonical_persistence_authority == 0U);
            assert(program.floating_point_authority == 0U);

            for (i = 0U; i < program.step_count; ++i) {
                const HHSExactPass219H36CompositionStateV1 *state =
                    &program.states[i];
                assert(state->harmonic_rule64 >= 1U);
                assert(state->harmonic_rule64 <= 64U);
                assert(state->voice_count == 4U);
                assert(state->voice_order_valid == 1U);
                assert(state->inversion_valid == 1U);
                assert(state->fixed_operation64_preserved == 1U);
                assert(state->canonical_mutation_authority == 0U);
                assert(state->canonical_hash72_authority == 0U);
                assert(state->canonical_persistence_authority == 0U);
                assert(state->floating_point_authority == 0U);

                if (i > 0U) {
                    const HHSExactPass219H36CompositionTransitionV1 *t =
                        &program.transitions[i - 1U];
                    assert(t->progression_allowed == 1U);
                    assert(t->voice_leading_valid == 1U);
                    assert(t->fixed_operation64_preserved == 1U);
                    assert(t->canonical_mutation_authority == 0U);
                    assert(t->canonical_hash72_authority == 0U);
                    assert(t->canonical_persistence_authority == 0U);
                    assert(t->floating_point_authority == 0U);
                }
            }
        }
    }

    {
        HHSExactPass219H36CompositionProgramV1 p;

        assert(hhs_exact_pass219_h36_composition_program_build(
            HHS_EXACT_PASS219_H36_TEMPLATE_DIATONIC_AUTHENTIC,
            0U, &p) == HHS_EXACT_STATUS_OK);
        assert(p.step_count == 3U);
        assert(p.states[0].harmonic_rule64 ==
               HHS_EXACT_PASS219_H36_RULE_II_MINOR7);
        assert(p.states[1].harmonic_rule64 ==
               HHS_EXACT_PASS219_H36_RULE_V7);
        assert(p.states[2].harmonic_rule64 ==
               HHS_EXACT_PASS219_H36_RULE_I_MAJOR);

        assert(hhs_exact_pass219_h36_composition_program_build(
            HHS_EXACT_PASS219_H36_TEMPLATE_MINOR_AUTHENTIC,
            9U, &p) == HHS_EXACT_STATUS_OK);
        assert(p.states[0].harmonic_rule64 ==
               HHS_EXACT_PASS219_H36_RULE_MINOR_II_HALFDIM7);
        assert(p.states[1].harmonic_rule64 ==
               HHS_EXACT_PASS219_H36_RULE_MINOR_V7_B9);
        assert(p.states[2].harmonic_rule64 ==
               HHS_EXACT_PASS219_H36_RULE_MINOR_I_MINMAJ7);

        assert(hhs_exact_pass219_h36_composition_program_build(
            HHS_EXACT_PASS219_H36_TEMPLATE_SECONDARY_DOMINANT_CHAIN,
            0U, &p) == HHS_EXACT_STATUS_OK);
        assert(p.states[0].secondary_target_pc12 == 7U);
        assert((p.states[0].context_flags &
                HHS_EXACT_PASS219_H36_CONTEXT_SECONDARY_FUNCTION) != 0U);

        assert(hhs_exact_pass219_h36_composition_program_build(
            HHS_EXACT_PASS219_H36_TEMPLATE_COLTRANE_THREE_TONIC,
            0U, &p) == HHS_EXACT_STATUS_OK);
        assert(p.step_count == 4U);
        assert(p.states[0].tonic_pc12 == 0U);
        assert(p.states[1].tonic_pc12 == 4U);
        assert(p.states[2].tonic_pc12 == 8U);
        assert(p.modulation_count >= 2U);

        assert(hhs_exact_pass219_h36_composition_program_build(
            HHS_EXACT_PASS219_H36_TEMPLATE_FOUR_TONIC_MINOR_THIRDS,
            1U, &p) == HHS_EXACT_STATUS_OK);
        assert(p.step_count == 5U);
        assert(p.states[0].tonic_pc12 == 1U);
        assert(p.states[1].tonic_pc12 == 4U);
        assert(p.states[2].tonic_pc12 == 7U);
        assert(p.states[3].tonic_pc12 == 10U);
        assert(p.states[4].tonic_pc12 == 1U);
        assert(p.modulation_count >= 3U);
    }

    {
        HHSExactPass219H36CompositionProgramV1 p;
        assert(hhs_exact_pass219_h36_composition_program_build(
            0U, 0U, &p) == HHS_EXACT_STATUS_RANGE_ERROR);
        assert(hhs_exact_pass219_h36_composition_program_build(
            HHS_EXACT_PASS219_H36_COMPOSITION_TEMPLATE_COUNT + 1U,
            0U, &p) == HHS_EXACT_STATUS_RANGE_ERROR);
        assert(hhs_exact_pass219_h36_composition_program_build(
            HHS_EXACT_PASS219_H36_TEMPLATE_DIATONIC_AUTHENTIC,
            12U, &p) == HHS_EXACT_STATUS_RANGE_ERROR);
    }

    puts("PASS219 Harmonic36 composition programs 1.1 conformance: PASS");
    return 0;
}

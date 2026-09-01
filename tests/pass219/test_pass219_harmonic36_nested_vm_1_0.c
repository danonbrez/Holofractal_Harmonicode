#include "hhs_pass219_harmonic36_nested_vm_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint64_t enc(uint16_t op, uint8_t ac, uint8_t ind, uint8_t ix, uint32_t y) {
    uint64_t word = 0U;
    assert(hhs_exact_pass219_h36_instruction_encode(op, ac, ind, ix, y, &word) ==
           HHS_EXACT_STATUS_OK);
    return word;
}

static uint64_t next64(uint64_t *x) {
    *x ^= *x << 13U;
    *x ^= *x >> 7U;
    *x ^= *x << 17U;
    return *x;
}

int main(void) {
    uint32_t i;
    uint64_t seed = UINT64_C(0x9E3779B97F4A7C15);

    assert(hhs_exact_pass219_h36_validate() == HHS_EXACT_STATUS_OK);

    {
        uint64_t word = 0U;
        HHSExactPass219H36InstructionV1 d;
        assert(hhs_exact_pass219_h36_instruction_encode(
            UINT16_C(0213), 0U, 0U, 0U, UINT32_C(02570), &word) ==
            HHS_EXACT_STATUS_OK);
        assert(word == UINT64_C(0213000002570));
        assert(hhs_exact_pass219_h36_instruction_decode(word, &d) ==
               HHS_EXACT_STATUS_OK);
        assert(d.opcode9 == UINT16_C(0213));
        assert(d.address18 == UINT32_C(02570));

        assert(hhs_exact_pass219_h36_instruction_encode(
            UINT16_C(0213), 0U, 1U, 0U, UINT32_C(02570), &word) ==
            HHS_EXACT_STATUS_OK);
        assert(word == UINT64_C(0213020002570));
    }

    for (i = 0U; i < HHS_EXACT_PASS219_H36_FRAME_BITS; ++i) {
        HHSExactPass219H36CoordinateV1 c;
        assert(hhs_exact_pass219_h36_coordinate((uint16_t)i, &c) ==
               HHS_EXACT_STATUS_OK);
        assert((uint32_t)c.word144 * 36U + c.bit36 == i);
        assert((uint32_t)c.vm81_cell81 * 64U + c.vm81_operation64 == i);
        assert((uint32_t)c.hash72_row72 * 72U + c.hash72_col72 == i);
        assert((uint32_t)c.phase_left8 * 8U + c.phase_right8 ==
               c.vm81_operation64);
        assert(c.harmonic_rule64 == (uint8_t)(c.vm81_operation64 + 1U));
        assert(c.et_bank3 < 3U);
        assert(c.et_pitch12 < 12U);
    }

    for (i = 0U; i < 64U; ++i) {
        HHSExactVM81Frame in;
        HHSExactVM81Frame out;
        HHSExactPass219H36VMStateV1 vm;
        uint32_t w;

        for (w = 0U; w < HHS_EXACT_VM81_CELLS; ++w)
            in.words[w] = next64(&seed);

        assert(hhs_exact_pass219_h36_import_vm81(&in, &vm) ==
               HHS_EXACT_STATUS_OK);
        assert(hhs_exact_pass219_h36_export_vm81(&vm, &out) ==
               HHS_EXACT_STATUS_OK);
        assert(memcmp(&in, &out, sizeof(in)) == 0);
    }

    {
        HHSExactPass219H36VMStateV1 et;
        assert(hhs_exact_pass219_h36_equal_temperament_seed(&et) ==
               HHS_EXACT_STATUS_OK);
        for (i = 0U; i < 144U; ++i)
            assert((et.memory[i] & ~HHS_EXACT_PASS219_H36_WORD_MASK) == 0U);
    }

    for (i = 1U; i <= HHS_EXACT_PASS219_H36_RULE_COUNT; ++i) {
        HHSExactPass219H36HarmonicRuleDescriptorV1 r;
        uint32_t tonic;
        assert(hhs_exact_pass219_h36_harmonic_rule((uint16_t)i, &r) ==
               HHS_EXACT_STATUS_OK);
        assert(r.rule_id == i);
        assert(r.era >= HHS_EXACT_PASS219_H36_ERA_DIATONIC);
        assert(r.era <= HHS_EXACT_PASS219_H36_ERA_MODERN_JAZZ);
        for (tonic = 0U; tonic < 12U; ++tonic) {
            uint64_t rendered;
            uint64_t back;
            assert(hhs_exact_pass219_h36_harmonic_render(
                (uint16_t)i, (uint8_t)tonic, &rendered) ==
                HHS_EXACT_STATUS_OK);
            assert(hhs_exact_pass219_h36_harmonic_transpose(
                rendered, (uint8_t)(12U - tonic), &back) ==
                HHS_EXACT_STATUS_OK);
            {
                uint64_t root;
                assert(hhs_exact_pass219_h36_harmonic_render(
                    (uint16_t)i, 0U, &root) == HHS_EXACT_STATUS_OK);
                assert(back == root);
            }
        }
    }

    {
        HHSExactPass219H36HarmonicRuleDescriptorV1 german;
        HHSExactPass219H36HarmonicRuleDescriptorV1 swiss;
        assert(hhs_exact_pass219_h36_harmonic_rule(
            HHS_EXACT_PASS219_H36_RULE_GERMAN_AUG6, &german) ==
            HHS_EXACT_STATUS_OK);
        assert(hhs_exact_pass219_h36_harmonic_rule(
            HHS_EXACT_PASS219_H36_RULE_SWISS_AUG6, &swiss) ==
            HHS_EXACT_STATUS_OK);
        assert(german.rule_id != swiss.rule_id);
        assert(german.core_mask12 == swiss.core_mask12);
        assert(german.flags != swiss.flags);
    }

    {
        HHSExactPass219H36VMStateV1 vm;
        uint32_t steps = 0U;
        uint64_t rendered_v7;
        uint64_t rendered_i;

        assert(hhs_exact_pass219_h36_vm_init(&vm) == HHS_EXACT_STATUS_OK);
        vm.memory[0] = enc(UINT16_C(0201), 1U, 0U, 0U, 5U);
        vm.memory[1] = enc(UINT16_C(0271), 1U, 0U, 0U, 7U);
        vm.memory[2] = enc(UINT16_C(0431), 1U, 0U, 0U, 3U);

        vm.accumulators[2] =
            (uint64_t)HHS_EXACT_PASS219_H36_RULE_JAZZ_V7 |
            (UINT64_C(0) << 8U) |
            (UINT64_C(20) << 12U);
        vm.memory[3] = enc(UINT16_C(0001), 2U, 0U, 0U, 0U);

        vm.accumulators[3] =
            (uint64_t)HHS_EXACT_PASS219_H36_RULE_JAZZ_I_MAJOR7 |
            (UINT64_C(0) << 8U) |
            (UINT64_C(21) << 12U);
        vm.memory[4] = enc(UINT16_C(0001), 3U, 0U, 0U, 0U);

        vm.accumulators[4] = 20U;
        vm.memory[5] = enc(UINT16_C(0003), 4U, 0U, 0U, 21U);
        vm.memory[6] = enc(UINT16_C(0004), 5U, 0U, 0U, 5183U);
        vm.memory[7] = enc(UINT16_C(0077), 0U, 0U, 0U, 0U);

        assert(hhs_exact_pass219_h36_vm_run(&vm, 32U, &steps) ==
               HHS_EXACT_STATUS_OK);
        assert(vm.halted == 1U);
        assert(steps == 8U);
        assert(vm.accumulators[1] == 15U);
        assert(vm.canonical_mutation_authority == 0U);
        assert(vm.canonical_hash72_authority == 0U);
        assert(vm.canonical_persistence_authority == 0U);
        assert(vm.floating_point_authority == 0U);

        assert(hhs_exact_pass219_h36_harmonic_render(
            HHS_EXACT_PASS219_H36_RULE_JAZZ_V7, 0U, &rendered_v7) ==
            HHS_EXACT_STATUS_OK);
        assert(hhs_exact_pass219_h36_harmonic_render(
            HHS_EXACT_PASS219_H36_RULE_JAZZ_I_MAJOR7, 0U, &rendered_i) ==
            HHS_EXACT_STATUS_OK);
        assert(vm.memory[20] == rendered_v7);
        assert(vm.memory[21] == rendered_i);
        assert(vm.accumulators[4] != 0U);
        assert(vm.accumulators[5] != 0U);
    }

    {
        HHSExactPass219H36VMStateV1 vm;
        assert(hhs_exact_pass219_h36_vm_init(&vm) == HHS_EXACT_STATUS_OK);
        vm.memory[0] = enc(UINT16_C(0140), 1U, 0U, 0U, 1U);
        assert(hhs_exact_pass219_h36_vm_step(&vm) ==
               HHS_EXACT_STATUS_INVARIANT_FAILURE);
        assert(vm.trap == HHS_EXACT_PASS219_H36_TRAP_NONCANONICAL_FLOAT);
    }

    puts("PASS219 Harmonic36 nested VM conformance: PASS");
    return 0;
}

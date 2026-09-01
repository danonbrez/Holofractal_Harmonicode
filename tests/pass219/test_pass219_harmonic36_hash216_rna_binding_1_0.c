#include "hhs_pass219_harmonic36_hash216_rna_binding_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static HHSExactStatus test_index_resolver(
    const char transition_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    uint8_t lane_role,
    uint8_t lane_position72,
    uint16_t absolute_position216,
    uint8_t glyph,
    uint8_t out_sha256[HHS_EXACT_PASS219_HASH216_SHA256_BYTES],
    void *context
) {
    uint32_t i;
    (void)transition_identity216;
    (void)context;
    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_SHA256_BYTES; ++i) {
        out_sha256[i] = (uint8_t)(
            glyph ^ lane_role ^ lane_position72 ^
            (uint8_t)absolute_position216 ^ (uint8_t)i);
    }
    return HHS_EXACT_STATUS_OK;
}

int main(void) {
    char previous[HHS_EXACT_HASH72_STRLEN];
    char change[HHS_EXACT_HASH72_STRLEN];
    char receipt[HHS_EXACT_HASH72_STRLEN];
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
    HHSExactPass219Hash216TransitionViewV1 transition;
    HHSExactPass219H36Hash216TransitionBindingV1 binding;
    uint32_t i;

    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i) {
        previous[i] = HHS_EXACT_HASH72_ALPHABET[0];
        change[i] = HHS_EXACT_HASH72_ALPHABET[i % 4U];
        receipt[i] = HHS_EXACT_HASH72_ALPHABET[i];
    }
    previous[HHS_EXACT_HASH72_LEN] = '\0';
    change[HHS_EXACT_HASH72_LEN] = '\0';
    receipt[HHS_EXACT_HASH72_LEN] = '\0';
    memset(identity, 'I', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    identity[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';

    assert(hhs_exact_pass219_hash216_transition_init(
        previous, change, receipt, identity, &transition) ==
        HHS_EXACT_STATUS_OK);

    assert(hhs_exact_pass219_h36_hash216_transition_bind(
        &transition, &binding) == HHS_EXACT_STATUS_OK);
    assert(binding.lane_unique_symbol_count[0] == 1U);
    assert(binding.lane_repeat_count[0] == 71U);
    assert(binding.lane_unique_symbol_count[1] == 4U);
    assert(binding.lane_repeat_count[1] == 68U);
    assert(binding.lane_unique_symbol_count[2] == 72U);
    assert(binding.lane_repeat_count[2] == 0U);
    assert(binding.repeat_allowed_manifold == 1U);
    assert(binding.no_repeat_core_recognized == 1U);
    assert(binding.vector_indexes_complete == 0U);

    assert(hhs_exact_pass219_hash216_resolve_indexes(
        &transition, test_index_resolver, NULL) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_hash216_indexes_complete(&transition) ==
        HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_hash216_transition_bind(
        &transition, &binding) == HHS_EXACT_STATUS_OK);
    assert(binding.vector_indexes_complete == 1U);
    assert(binding.resolved_index_count ==
           HHS_EXACT_PASS219_HASH216_OCCURRENCES);
    assert(hhs_exact_pass219_h36_hash216_transition_binding_validate(
        &transition, &binding) == HHS_EXACT_STATUS_OK);

    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++i) {
        const HHSExactPass219H36Hash216OccurrenceBindingV1 *o =
            &binding.occurrences[i];
        assert((uint32_t)o->lane_position72 * 72U +
               o->symbol_index72 == o->native_hash72_linear5184);
        assert((uint32_t)o->h36_word144 * 36U + o->h36_bit36 ==
               o->native_hash72_linear5184);
        assert((uint32_t)o->vm81_cell81 * 64U + o->vm81_operation64 ==
               o->native_hash72_linear5184);
        assert(o->directional_identity_preserved == 1U);
        assert(o->canonical_mutation_authority == 0U);
    }

    {
        HHSExactPass219HydrationCoordinateV1 coordinate;
        HHSExactPass219H36RNAOperationBindingV1 op;

        assert(hhs_exact_pass219_coordinate_from_pass189(
            80U, 0, 63U, 242U, &coordinate) == HHS_EXACT_STATUS_OK);
        assert(hhs_exact_pass219_h36_rna_operation_bind(
            &coordinate, &op) == HHS_EXACT_STATUS_OK);
        assert(op.vm81_linear5184 == 5183U);
        assert(op.h36_word144 == 143U);
        assert(op.h36_bit36 == 35U);
        assert(op.phase_left8 == 7U);
        assert(op.phase_right8 == 7U);
        assert(op.harmonic_rule64 == 64U);
        assert(op.hydration_slot5184 == coordinate.slot5184);
        assert(op.factorization_identity_preserved == 1U);
        assert(op.hydration_axis_preserved == 1U);
    }

    puts("PASS219 Harmonic36 Hash216/RNA binding: PASS");
    return 0;
}

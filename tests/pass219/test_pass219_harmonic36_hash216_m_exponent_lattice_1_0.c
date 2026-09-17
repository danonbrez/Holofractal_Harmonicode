#include "hhs_pass219_harmonic36_hash216_m_exponent_lattice_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static void assert_coordinate(
    const HHSExactPass219MExponentCoordinateV1 *coordinate,
    uint16_t exp2,
    uint16_t exp3
) {
    assert(coordinate->exp2 == exp2);
    assert(coordinate->exp3 == exp3);
}

int main(void) {
    char previous[HHS_EXACT_HASH72_STRLEN];
    char change[HHS_EXACT_HASH72_STRLEN];
    char receipt[HHS_EXACT_HASH72_STRLEN];
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
    HHSExactPass219Hash216TransitionViewV1 transition;
    HHSExactPass219H36Hash216TransitionBindingV1 binding;
    HHSExactPass219H36Hash216MExponentWitnessV1 witness;
    uint32_t i;

    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i) {
        previous[i] = HHS_EXACT_HASH72_ALPHABET[i];
        change[i] = HHS_EXACT_HASH72_ALPHABET[(i + 1U) % HHS_EXACT_HASH72_LEN];
        receipt[i] = HHS_EXACT_HASH72_ALPHABET[(i + 2U) % HHS_EXACT_HASH72_LEN];
    }
    previous[HHS_EXACT_HASH72_LEN] = '\0';
    change[HHS_EXACT_HASH72_LEN] = '\0';
    receipt[HHS_EXACT_HASH72_LEN] = '\0';
    memset(identity, 'M', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    identity[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';

    assert(hhs_exact_pass219_hash216_transition_init(
        previous, change, receipt, identity, &transition) ==
        HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_hash216_transition_bind(
        &transition, &binding) == HHS_EXACT_STATUS_OK);

    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++i) {
        const HHSExactPass219H36Hash216OccurrenceBindingV1 *occurrence =
            &binding.occurrences[i];

        assert(hhs_exact_pass219_h36_hash216_m_exponent_bind(
            occurrence, &witness) == HHS_EXACT_STATUS_OK);
        assert(hhs_exact_pass219_h36_hash216_m_exponent_validate(
            occurrence, &witness) == HHS_EXACT_STATUS_OK);

        assert(witness.native_hash72_linear5184 ==
               occurrence->native_hash72_linear5184);
        assert((uint32_t)witness.h36_word144 * 36U + witness.h36_bit36 ==
               witness.native_hash72_linear5184);
        assert((uint32_t)witness.vm81_cell81 * 64U + witness.vm81_operation64 ==
               witness.native_hash72_linear5184);

        assert_coordinate(&witness.unit1, 0U, 0U);
        assert_coordinate(&witness.binary2, 1U, 0U);
        assert_coordinate(&witness.ternary3, 0U, 1U);
        assert_coordinate(&witness.loshu4, 2U, 0U);
        assert_coordinate(&witness.loshu6, 1U, 1U);
        assert_coordinate(&witness.loshu8, 3U, 0U);
        assert_coordinate(&witness.p4_9, 0U, 2U);
        assert_coordinate(&witness.h36_36, 2U, 2U);
        assert_coordinate(&witness.hash72_72, 3U, 2U);
        assert_coordinate(&witness.hash216_216, 3U, 3U);
        assert_coordinate(&witness.vm5184, 6U, 4U);
        assert_coordinate(&witness.manifold_m, 216U, 144U);

        assert(witness.h36_depth36 == 36U);
        assert(witness.hash72_depth72 == 72U);
        assert(witness.same_linear5184_identity == 1U);
        assert(witness.factor_support_2_3_only == 1U);
        assert(witness.h36_to_hash72_binary_step == 1U);
        assert(witness.hash72_to_hash216_ternary_step == 1U);
        assert(witness.vm5184_h36_depth_closes_m == 1U);
        assert(witness.hash72_depth_closes_m == 1U);
        assert(witness.loshu_binary_ladder_from_one == 1U);
        assert(witness.loshu_six_is_binary_ternary_product == 1U);
        assert(witness.p4_is_ternary_square == 1U);
        assert(witness.ab_equals_p4_projection == 1U);
        assert(witness.one_is_p4_over9_projection == 1U);
        assert(witness.direct_shared_m_binding == 1U);
        assert(witness.translator_required == 0U);
        assert(witness.canonical_mutation_authority == 0U);
        assert(witness.canonical_hash72_authority == 0U);
        assert(witness.canonical_hash216_authority == 0U);
        assert(witness.canonical_persistence_authority == 0U);
        assert(witness.floating_point_authority == 0U);
    }

    /* Negative: break the already-proven shared 5,184 address. */
    {
        HHSExactPass219H36Hash216OccurrenceBindingV1 bad = binding.occurrences[0];
        bad.h36_bit36 = (uint8_t)((bad.h36_bit36 + 1U) % 36U);
        assert(hhs_exact_pass219_h36_hash216_m_exponent_bind(
            &bad, &witness) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    }

    /* Negative: mutate an exponent coordinate after construction. */
    assert(hhs_exact_pass219_h36_hash216_m_exponent_bind(
        &binding.occurrences[0], &witness) == HHS_EXACT_STATUS_OK);
    witness.manifold_m.exp2 = 215U;
    assert(hhs_exact_pass219_h36_hash216_m_exponent_validate(
        &binding.occurrences[0], &witness) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    /* Negative: a semantic translator is not part of this native binding. */
    assert(hhs_exact_pass219_h36_hash216_m_exponent_bind(
        &binding.occurrences[0], &witness) == HHS_EXACT_STATUS_OK);
    witness.translator_required = 1U;
    assert(hhs_exact_pass219_h36_hash216_m_exponent_validate(
        &binding.occurrences[0], &witness) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    puts("PASS219 H36/Hash216 M exponent lattice: PASS");
    return 0;
}

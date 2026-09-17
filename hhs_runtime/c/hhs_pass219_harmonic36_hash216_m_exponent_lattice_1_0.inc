#include "../include/hhs_pass219_harmonic36_hash216_m_exponent_lattice_1_0.h"

#include <string.h>

static uint32_t h36_m_exponent_lattice_version_word(void) {
    return (HHS_EXACT_PASS219_H36_M_LATTICE_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_H36_M_LATTICE_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_H36_M_LATTICE_VERSION_PATCH;
}

static void h36_m_set_coordinate(
    HHSExactPass219MExponentCoordinateV1 *coordinate,
    uint16_t exp2,
    uint16_t exp3
) {
    coordinate->exp2 = exp2;
    coordinate->exp3 = exp3;
}

uint32_t hhs_exact_pass219_h36_m_exponent_lattice_version(void) {
    return h36_m_exponent_lattice_version_word();
}

HHSExactStatus hhs_exact_pass219_h36_hash216_m_exponent_bind(
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *occurrence,
    HHSExactPass219H36Hash216MExponentWitnessV1 *out_witness
) {
    uint16_t hash72_linear;
    uint16_t h36_linear;
    uint16_t vm81_linear;

    if (occurrence == NULL || out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (occurrence->struct_size < sizeof(*occurrence) ||
        occurrence->version != hhs_exact_pass219_h36_rna_binding_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (occurrence->lane_position72 >= 72U ||
        occurrence->symbol_index72 >= 72U ||
        occurrence->h36_word144 >= 144U ||
        occurrence->h36_bit36 >= 36U ||
        occurrence->vm81_cell81 >= 81U ||
        occurrence->vm81_operation64 >= 64U ||
        occurrence->native_hash72_linear5184 >= 5184U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    hash72_linear = (uint16_t)(
        (uint16_t)occurrence->lane_position72 * 72U +
        (uint16_t)occurrence->symbol_index72);
    h36_linear = (uint16_t)(
        (uint16_t)occurrence->h36_word144 * 36U +
        (uint16_t)occurrence->h36_bit36);
    vm81_linear = (uint16_t)(
        (uint16_t)occurrence->vm81_cell81 * 64U +
        (uint16_t)occurrence->vm81_operation64);

    if (hash72_linear != occurrence->native_hash72_linear5184 ||
        h36_linear != occurrence->native_hash72_linear5184 ||
        vm81_linear != occurrence->native_hash72_linear5184)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_witness, 0, sizeof(*out_witness));
    out_witness->struct_size = (uint32_t)sizeof(*out_witness);
    out_witness->version = h36_m_exponent_lattice_version_word();
    out_witness->native_hash72_linear5184 = occurrence->native_hash72_linear5184;
    out_witness->h36_word144 = occurrence->h36_word144;
    out_witness->h36_bit36 = occurrence->h36_bit36;
    out_witness->vm81_cell81 = occurrence->vm81_cell81;
    out_witness->vm81_operation64 = occurrence->vm81_operation64;

    /* Local generator and Lo Shu projection coordinates in the exact 2,3 lattice. */
    h36_m_set_coordinate(&out_witness->unit1, 0U, 0U);
    h36_m_set_coordinate(&out_witness->binary2, 1U, 0U);
    h36_m_set_coordinate(&out_witness->ternary3, 0U, 1U);
    h36_m_set_coordinate(&out_witness->loshu4, 2U, 0U);
    h36_m_set_coordinate(&out_witness->loshu6, 1U, 1U);
    h36_m_set_coordinate(&out_witness->loshu8, 3U, 0U);
    h36_m_set_coordinate(&out_witness->p4_9, 0U, 2U);

    /* Shared native cardinalities. */
    h36_m_set_coordinate(&out_witness->h36_36, 2U, 2U);
    h36_m_set_coordinate(&out_witness->hash72_72, 3U, 2U);
    h36_m_set_coordinate(&out_witness->hash216_216, 3U, 3U);
    h36_m_set_coordinate(&out_witness->vm5184, 6U, 4U);
    h36_m_set_coordinate(&out_witness->manifold_m, 216U, 144U);

    out_witness->h36_depth36 = 36U;
    out_witness->hash72_depth72 = 72U;

    out_witness->same_linear5184_identity = 1U;
    out_witness->factor_support_2_3_only = 1U;
    out_witness->h36_to_hash72_binary_step =
        (uint8_t)(2U + 1U == 3U && 2U == 2U);
    out_witness->hash72_to_hash216_ternary_step =
        (uint8_t)(3U == 3U && 2U + 1U == 3U);
    out_witness->vm5184_h36_depth_closes_m =
        (uint8_t)(6U * 36U == 216U && 4U * 36U == 144U);
    out_witness->hash72_depth_closes_m =
        (uint8_t)(3U * 72U == 216U && 2U * 72U == 144U);
    out_witness->loshu_binary_ladder_from_one =
        (uint8_t)(1U * 2U == 2U && 2U * 2U == 4U && 4U * 2U == 8U);
    out_witness->loshu_six_is_binary_ternary_product =
        (uint8_t)(2U * 3U == 6U);
    out_witness->p4_is_ternary_square =
        (uint8_t)(3U * 3U == 9U);
    out_witness->ab_equals_p4_projection = 1U;
    out_witness->one_is_p4_over9_projection =
        (uint8_t)(9U / 9U == 1U);
    out_witness->direct_shared_m_binding = 1U;
    out_witness->translator_required = 0U;

    out_witness->canonical_mutation_authority = 0U;
    out_witness->canonical_hash72_authority = 0U;
    out_witness->canonical_hash216_authority = 0U;
    out_witness->canonical_persistence_authority = 0U;
    out_witness->floating_point_authority = 0U;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_hash216_m_exponent_validate(
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *occurrence,
    const HHSExactPass219H36Hash216MExponentWitnessV1 *witness
) {
    HHSExactPass219H36Hash216MExponentWitnessV1 expected;
    HHSExactStatus status;

    if (occurrence == NULL || witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size != sizeof(*witness) ||
        witness->version != h36_m_exponent_lattice_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    status = hhs_exact_pass219_h36_hash216_m_exponent_bind(
        occurrence, &expected);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return memcmp(witness, &expected, sizeof(expected)) == 0
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

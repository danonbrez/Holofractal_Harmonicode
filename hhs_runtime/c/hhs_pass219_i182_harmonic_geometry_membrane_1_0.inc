#include "../include/hhs_pass219_i182_harmonic_geometry_membrane_1_0.h"

#include <string.h>

static uint32_t hhs_exact_pass219_i182_geometry_version_word(void) {
    return (HHS_EXACT_PASS219_I182_GEOMETRY_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_I182_GEOMETRY_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_I182_GEOMETRY_VERSION_PATCH;
}

static int hhs_exact_pass219_i182_platonic_pair_admissible(uint32_t p, uint32_t q) {
    if (p == 3U && (q == 3U || q == 4U || q == 5U))
        return 1;
    if ((p == 4U || p == 5U) && q == 3U)
        return 1;
    return 0;
}

static HHSExactStatus hhs_exact_pass219_i182_div_exact(
    uint32_t numerator,
    uint32_t denominator,
    uint32_t *out
) {
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (denominator == 0U || numerator % denominator != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    *out = numerator / denominator;
    return HHS_EXACT_STATUS_OK;
}

uint32_t hhs_exact_pass219_i182_geometry_membrane_version(void) {
    return hhs_exact_pass219_i182_geometry_version_word();
}

HHSExactStatus hhs_exact_pass219_i182_geometry_factor_witness(
    uint32_t left,
    uint32_t right,
    HHSExactPass219I182GeometryFactorWitnessV1 *out_witness
) {
    const uint64_t product = (uint64_t)left * (uint64_t)right;

    if (out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (product != HHS_EXACT_PASS219_I182_GEOMETRY_Q_H)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_witness, 0, sizeof(*out_witness));
    out_witness->struct_size = (uint32_t)sizeof(*out_witness);
    out_witness->version = hhs_exact_pass219_i182_geometry_version_word();
    out_witness->left = left;
    out_witness->right = right;
    out_witness->product = (uint32_t)product;
    out_witness->exact = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_i182_pentagonal_witness(
    HHSExactPass219I182PentagonalWitnessV1 *out_witness
) {
    const uint32_t sides = HHS_EXACT_PASS219_I182_GEOMETRY_PENTAGON_SIDES;
    const uint32_t half_sector = HHS_EXACT_PASS219_I182_GEOMETRY_PENTAGON_HALF_SECTOR;
    const uint32_t external = HHS_EXACT_PASS219_I182_GEOMETRY_PENTAGON_EXTERNAL;
    const uint32_t interior = HHS_EXACT_PASS219_I182_GEOMETRY_PENTAGON_INTERIOR;
    const uint32_t supplementary = HHS_EXACT_PASS219_I182_GEOMETRY_PENTAGON_SUPPLEMENTARY;
    const uint32_t cycle = HHS_EXACT_PASS219_I182_GEOMETRY_FULL_CYCLE;

    if (out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (sides * external != cycle ||
        3U * half_sector != interior ||
        180U - external != interior ||
        180U - half_sector != supplementary)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_witness, 0, sizeof(*out_witness));
    out_witness->struct_size = (uint32_t)sizeof(*out_witness);
    out_witness->version = hhs_exact_pass219_i182_geometry_version_word();
    out_witness->hydration_quantum = HHS_EXACT_PASS219_I182_GEOMETRY_Q_H;
    out_witness->sides = sides;
    out_witness->half_sector = half_sector;
    out_witness->external = external;
    out_witness->interior = interior;
    out_witness->supplementary = supplementary;
    out_witness->cycle = cycle;
    out_witness->zero_phase_closure = (sides * external) % cycle;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_i182_derive_platonic_closure(
    uint32_t p,
    uint32_t q,
    HHSExactPass219I182PlatonicClosureV1 *out_closure
) {
    int32_t denominator;
    uint32_t edges;
    uint32_t vertices;
    uint32_t faces;
    int32_t euler;
    HHSExactStatus status;

    if (out_closure == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_exact_pass219_i182_platonic_pair_admissible(p, q))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    denominator = (int32_t)(2U * p + 2U * q) - (int32_t)(p * q);
    if (denominator <= 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_i182_div_exact(
        2U * p * q, (uint32_t)denominator, &edges);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_i182_div_exact(2U * edges, q, &vertices);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_i182_div_exact(2U * edges, p, &faces);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    euler = (int32_t)vertices - (int32_t)edges + (int32_t)faces;
    if (p * faces != 2U * edges ||
        q * vertices != 2U * edges ||
        euler != 2)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_closure, 0, sizeof(*out_closure));
    out_closure->struct_size = (uint32_t)sizeof(*out_closure);
    out_closure->version = hhs_exact_pass219_i182_geometry_version_word();
    out_closure->p = p;
    out_closure->q = q;
    out_closure->vertices = vertices;
    out_closure->edges = edges;
    out_closure->faces = faces;
    out_closure->euler = (uint32_t)euler;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_i182_validate_platonic_candidate(
    const HHSExactPass219I182PlatonicClosureV1 *candidate
) {
    HHSExactPass219I182PlatonicClosureV1 expected;
    HHSExactStatus status;

    if (candidate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (candidate->struct_size != sizeof(*candidate) ||
        candidate->version != hhs_exact_pass219_i182_geometry_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    status = hhs_exact_pass219_i182_derive_platonic_closure(
        candidate->p, candidate->q, &expected);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return memcmp(candidate, &expected, sizeof(expected)) == 0
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_i182_derive_dodecahedral_closure(
    HHSExactPass219I182PlatonicClosureV1 *out_closure
) {
    HHSExactStatus status;

    if (out_closure == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_pass219_i182_derive_platonic_closure(5U, 3U, out_closure);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (out_closure->p * out_closure->faces != 2U * out_closure->edges ||
        out_closure->q * out_closure->vertices != 2U * out_closure->edges ||
        out_closure->euler != 2U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_i182_geometry_membrane_build(
    HHSExactPass219I182GeometryMembraneWitnessV1 *out_witness
) {
    static const uint32_t factor_left[
        HHS_EXACT_PASS219_I182_GEOMETRY_FACTOR_WITNESS_COUNT
    ] = {72U, 64U, 36U, 48U};
    static const uint32_t factor_right[
        HHS_EXACT_PASS219_I182_GEOMETRY_FACTOR_WITNESS_COUNT
    ] = {72U, 81U, 144U, 108U};
    static const uint32_t platonic_p[
        HHS_EXACT_PASS219_I182_GEOMETRY_PLATONIC_BRANCH_COUNT
    ] = {3U, 3U, 3U, 4U, 5U};
    static const uint32_t platonic_q[
        HHS_EXACT_PASS219_I182_GEOMETRY_PLATONIC_BRANCH_COUNT
    ] = {3U, 4U, 5U, 3U, 3U};
    uint32_t i;
    HHSExactStatus status;

    if (out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_witness, 0, sizeof(*out_witness));
    out_witness->struct_size = (uint32_t)sizeof(*out_witness);
    out_witness->version = hhs_exact_pass219_i182_geometry_version_word();
    out_witness->iteration = HHS_EXACT_PASS219_I182_GEOMETRY_ITERATION;
    out_witness->hydration_quantum = HHS_EXACT_PASS219_I182_GEOMETRY_Q_H;

    for (i = 0U; i < HHS_EXACT_PASS219_I182_GEOMETRY_FACTOR_WITNESS_COUNT; ++i) {
        status = hhs_exact_pass219_i182_geometry_factor_witness(
            factor_left[i], factor_right[i], &out_witness->factor_witnesses[i]);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
    }

    status = hhs_exact_pass219_i182_pentagonal_witness(&out_witness->pentagon);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    for (i = 0U; i < HHS_EXACT_PASS219_I182_GEOMETRY_PLATONIC_BRANCH_COUNT; ++i) {
        status = hhs_exact_pass219_i182_derive_platonic_closure(
            platonic_p[i], platonic_q[i], &out_witness->platonic_closures[i]);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
    }

    status = hhs_exact_pass219_i182_derive_dodecahedral_closure(
        &out_witness->dodecahedron);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_witness->factorization_conservation = 1U;
    out_witness->all_platonic_closures_valid = 1U;
    out_witness->dodecahedral_closure_valid = 1U;
    out_witness->canonical_integer_authority = 1U;
    out_witness->canonical_float_authority = 0U;
    out_witness->authoritative_vertex_table_used = 0U;
    out_witness->singleton_vm81_authority_preserved = 1U;
    out_witness->vm81_authority_minted = 0U;
    out_witness->vm81_direct_mutation_authority = 0U;
    out_witness->hash72_authority_minted = 0U;
    out_witness->hash216_persistence_authority = 0U;
    out_witness->cxx_mutation_authority = 0U;
    out_witness->public_operation_authority = 0U;
    out_witness->capability_binding_authority = 0U;
    out_witness->rendering_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_i182_geometry_membrane_validate(
    const HHSExactPass219I182GeometryMembraneWitnessV1 *witness
) {
    HHSExactPass219I182GeometryMembraneWitnessV1 expected;
    HHSExactStatus status;

    if (witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size != sizeof(*witness) ||
        witness->version != hhs_exact_pass219_i182_geometry_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (witness->iteration != HHS_EXACT_PASS219_I182_GEOMETRY_ITERATION ||
        witness->hydration_quantum != HHS_EXACT_PASS219_I182_GEOMETRY_Q_H ||
        witness->factorization_conservation != 1U ||
        witness->all_platonic_closures_valid != 1U ||
        witness->dodecahedral_closure_valid != 1U ||
        witness->canonical_integer_authority != 1U ||
        witness->canonical_float_authority != 0U ||
        witness->authoritative_vertex_table_used != 0U ||
        witness->singleton_vm81_authority_preserved != 1U ||
        witness->vm81_authority_minted != 0U ||
        witness->vm81_direct_mutation_authority != 0U ||
        witness->hash72_authority_minted != 0U ||
        witness->hash216_persistence_authority != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->public_operation_authority != 0U ||
        witness->capability_binding_authority != 0U ||
        witness->rendering_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_i182_geometry_membrane_build(&expected);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return memcmp(witness, &expected, sizeof(expected)) == 0
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

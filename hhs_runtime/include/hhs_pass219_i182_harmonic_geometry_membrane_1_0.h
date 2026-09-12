#ifndef HHS_PASS219_I182_HARMONIC_GEOMETRY_MEMBRANE_1_0_H
#define HHS_PASS219_I182_HARMONIC_GEOMETRY_MEMBRANE_1_0_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_I182_GEOMETRY_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_I182_GEOMETRY_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_I182_GEOMETRY_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_I182_GEOMETRY_ITERATION 182U

#define HHS_EXACT_PASS219_I182_GEOMETRY_Q_H 5184U
#define HHS_EXACT_PASS219_I182_GEOMETRY_FACTOR_WITNESS_COUNT 4U
#define HHS_EXACT_PASS219_I182_GEOMETRY_PLATONIC_BRANCH_COUNT 5U
#define HHS_EXACT_PASS219_I182_GEOMETRY_FULL_CYCLE 360U
#define HHS_EXACT_PASS219_I182_GEOMETRY_PENTAGON_SIDES 5U
#define HHS_EXACT_PASS219_I182_GEOMETRY_PENTAGON_HALF_SECTOR 36U
#define HHS_EXACT_PASS219_I182_GEOMETRY_PENTAGON_EXTERNAL 72U
#define HHS_EXACT_PASS219_I182_GEOMETRY_PENTAGON_INTERIOR 108U
#define HHS_EXACT_PASS219_I182_GEOMETRY_PENTAGON_SUPPLEMENTARY 144U

typedef struct HHSExactPass219I182GeometryFactorWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t left;
    uint32_t right;
    uint32_t product;
    uint32_t exact;
} HHSExactPass219I182GeometryFactorWitnessV1;

typedef struct HHSExactPass219I182PentagonalWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t hydration_quantum;
    uint32_t sides;
    uint32_t half_sector;
    uint32_t external;
    uint32_t interior;
    uint32_t supplementary;
    uint32_t cycle;
    uint32_t zero_phase_closure;
} HHSExactPass219I182PentagonalWitnessV1;

typedef struct HHSExactPass219I182PlatonicClosureV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t p;
    uint32_t q;
    uint32_t vertices;
    uint32_t edges;
    uint32_t faces;
    uint32_t euler;
} HHSExactPass219I182PlatonicClosureV1;

typedef struct HHSExactPass219I182GeometryMembraneWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t iteration;
    uint32_t hydration_quantum;
    HHSExactPass219I182GeometryFactorWitnessV1 factor_witnesses[
        HHS_EXACT_PASS219_I182_GEOMETRY_FACTOR_WITNESS_COUNT
    ];
    HHSExactPass219I182PentagonalWitnessV1 pentagon;
    HHSExactPass219I182PlatonicClosureV1 platonic_closures[
        HHS_EXACT_PASS219_I182_GEOMETRY_PLATONIC_BRANCH_COUNT
    ];
    HHSExactPass219I182PlatonicClosureV1 dodecahedron;
    uint32_t factorization_conservation;
    uint32_t all_platonic_closures_valid;
    uint32_t dodecahedral_closure_valid;
    uint32_t canonical_integer_authority;
    uint32_t canonical_float_authority;
    uint32_t authoritative_vertex_table_used;
    uint32_t singleton_vm81_authority_preserved;
    uint32_t vm81_authority_minted;
    uint32_t vm81_direct_mutation_authority;
    uint32_t hash72_authority_minted;
    uint32_t hash216_persistence_authority;
    uint32_t cxx_mutation_authority;
    uint32_t public_operation_authority;
    uint32_t capability_binding_authority;
    uint32_t rendering_authority;
} HHSExactPass219I182GeometryMembraneWitnessV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_i182_geometry_membrane_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_i182_geometry_factor_witness(
    uint32_t left,
    uint32_t right,
    HHSExactPass219I182GeometryFactorWitnessV1 *out_witness
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_i182_pentagonal_witness(
    HHSExactPass219I182PentagonalWitnessV1 *out_witness
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_i182_derive_platonic_closure(
    uint32_t p,
    uint32_t q,
    HHSExactPass219I182PlatonicClosureV1 *out_closure
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_i182_validate_platonic_candidate(
    const HHSExactPass219I182PlatonicClosureV1 *candidate
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_i182_derive_dodecahedral_closure(
    HHSExactPass219I182PlatonicClosureV1 *out_closure
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_i182_geometry_membrane_build(
    HHSExactPass219I182GeometryMembraneWitnessV1 *out_witness
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_i182_geometry_membrane_validate(
    const HHSExactPass219I182GeometryMembraneWitnessV1 *witness
);

#ifdef __cplusplus
}
#endif

#endif

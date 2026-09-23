#ifndef HHS_PASS220_G72_EPSILON_LO_SHU_GEAR_1_0_H
#define HHS_PASS220_G72_EPSILON_LO_SHU_GEAR_1_0_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS220_G72_VERSION UINT32_C(0x00010000)
#define HHS_EXACT_PASS220_G72_RADICAND UINT32_C(2)
#define HHS_EXACT_PASS220_G72_ROOT_ORDER UINT32_C(72)
#define HHS_EXACT_PASS220_G72_HARMONIC_CELLS UINT32_C(144)
#define HHS_EXACT_PASS220_G72_LO_SHU_CELLS UINT32_C(9)
#define HHS_EXACT_PASS220_G72_VM5184 UINT32_C(5184)
#define HHS_EXACT_PASS220_G72_FRACTAL_ORBIT UINT32_C(10368)

typedef struct HHSExactPass220G72DescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t radicand;
    uint32_t root_order;
    uint32_t harmonic_cells;
    uint32_t lo_shu_cells;
    uint32_t vm5184;
    uint32_t fractal_orbit;
    uint8_t immutable_generator;
    uint8_t noncommutative_ordered_transition;
    uint8_t scalar_evaluation_allowed;
    uint8_t epsilon_symbolic_magnitude;
    uint8_t lo_shu_route_required;
    uint8_t exact_integer_only;
    uint8_t floating_point_authority;
    uint8_t canonical_admission_authority;
} HHSExactPass220G72DescriptorV1;

typedef struct HHSExactPass220G72StateV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t tooth_index;
    uint32_t completed_routes;
    uint64_t route_signature64;
    uint8_t generator_unresolved;
    uint8_t epsilon_symbol;
    uint8_t epsilon_magnitude_unresolved;
    uint8_t closure_emitted;
    uint8_t floating_point_authority;
    uint8_t reserved0[3];
} HHSExactPass220G72StateV1;

typedef struct HHSExactPass220G72RouteWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t from_tooth;
    uint32_t to_tooth;
    int8_t epsilon_signs[3];
    int8_t lo_shu_coefficients[9];
    int16_t lo_shu_row_sums[3];
    int16_t lo_shu_column_sums[3];
    int16_t lo_shu_diagonal_sums[2];
    int16_t lo_shu_total;
    uint64_t previous_route_signature64;
    uint64_t route_signature64;
    uint8_t generator_unresolved_before;
    uint8_t generator_unresolved_after;
    uint8_t epsilon_magnitude_unresolved;
    uint8_t local_zero_sum;
    uint8_t lo_shu_zero_sum;
    uint8_t scalar_resolution_performed;
    uint8_t floating_point_authority;
    uint8_t reserved0;
} HHSExactPass220G72RouteWitnessV1;

typedef struct HHSExactPass220G72ClosureV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t routed_cycles;
    uint32_t required_cycles;
    uint32_t emergent_binary_coefficient;
    uint32_t u_exponent;
    uint32_t f_exponent;
    uint64_t final_route_signature64;
    uint8_t exact_closure;
    uint8_t generator_still_unresolved;
    uint8_t premature_scalar_resolution;
    uint8_t epsilon_orientation_preserved;
    uint8_t lo_shu_routing_preserved;
    uint8_t floating_point_authority;
    uint8_t canonical_admission_authority;
    uint8_t reserved0;
} HHSExactPass220G72ClosureV1;

HHS_EXACT_API uint32_t hhs_exact_pass220_g72_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_g72_descriptor(
    HHSExactPass220G72DescriptorV1 *out_descriptor
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_g72_state_init(
    HHSExactPass220G72StateV1 *out_state
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_g72_advance(
    const HHSExactPass220G72StateV1 *state,
    HHSExactPass220G72StateV1 *out_next_state,
    HHSExactPass220G72RouteWitnessV1 *out_route
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_g72_close(
    const HHSExactPass220G72StateV1 *state,
    HHSExactPass220G72ClosureV1 *out_closure
);

#ifdef __cplusplus
}
#endif

#endif

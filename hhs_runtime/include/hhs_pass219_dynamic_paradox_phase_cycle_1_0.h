#ifndef HHS_PASS219_DYNAMIC_PARADOX_PHASE_CYCLE_1_0_H
#define HHS_PASS219_DYNAMIC_PARADOX_PHASE_CYCLE_1_0_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_PARADOX_VERSION 1U
#define HHS_EXACT_PASS219_PARADOX_MAX_OPTIONS 16U
#define HHS_EXACT_PASS219_PARADOX_MAX_TRAJECTORY 18U
#define HHS_EXACT_PASS219_PARADOX_MAX_COMPONENT 1000000U
#define HHS_EXACT_PASS219_PARADOX_H36_VALUE 36U
#define HHS_EXACT_PASS219_PARADOX_MANIFOLD_BASE 5184U
#define HHS_EXACT_PASS219_PARADOX_MANIFOLD_POWER 4U
#define HHS_EXACT_PASS219_PARADOX_MANIFOLD_CARDINALITY UINT64_C(722204136308736)

typedef enum HHSExactPass219ParadoxStatusV1 {
    HHS_EXACT_PASS219_PARADOX_OK = 0,
    HHS_EXACT_PASS219_PARADOX_NULL = 1,
    HHS_EXACT_PASS219_PARADOX_RANGE_ERROR = 2,
    HHS_EXACT_PASS219_PARADOX_DENOMINATOR_ZERO = 3,
    HHS_EXACT_PASS219_PARADOX_BOUND_ERROR = 4,
    HHS_EXACT_PASS219_PARADOX_TYPE_LEVEL_CONFLATION = 5,
    HHS_EXACT_PASS219_PARADOX_NO_FINITE_CLOSURE = 6,
    HHS_EXACT_PASS219_PARADOX_WITNESS_ERROR = 7
} HHSExactPass219ParadoxStatusV1;

typedef struct HHSExactPass219RationalV1 {
    uint32_t numerator;
    uint32_t denominator;
} HHSExactPass219RationalV1;

typedef struct HHSExactPass219ParadoxProblemV1 {
    uint32_t version;
    uint8_t option_count;
    uint8_t seed_option_index;
    uint8_t permit_meta_closure;
    uint8_t promote_meta_zero_to_object_correct;
    uint8_t declared_visit_bound;
    uint8_t reserved0;
    uint16_t reserved1;
    HHSExactPass219RationalV1 options[HHS_EXACT_PASS219_PARADOX_MAX_OPTIONS];
} HHSExactPass219ParadoxProblemV1;

typedef struct HHSExactPass219ParadoxWitnessV1 {
    uint32_t version;
    uint8_t option_count;
    uint8_t seed_option_index;
    uint8_t object_has_fixed_point;
    uint8_t object_valid_option_count;
    uint8_t seed_option_object_correct;
    uint8_t cycle_detected;
    uint8_t fixed_point_reached;
    uint8_t preperiod;
    uint8_t period;
    uint8_t trajectory_count;
    uint8_t finite_visit_bound;
    uint8_t meta_empty_valid_set;
    uint8_t meta_probability_zero;
    int8_t seed_candidate_trinary;
    int8_t cycle_motion_trinary;
    int8_t meta_closure_trinary;
    uint8_t typed_level_separation_preserved;
    uint8_t bounded_closure;
    uint8_t ordered_trajectory_preserved;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    HHSExactPass219RationalV1 meta_probability;
    HHSExactPass219RationalV1 trajectory[HHS_EXACT_PASS219_PARADOX_MAX_TRAJECTORY];
} HHSExactPass219ParadoxWitnessV1;

typedef struct HHSExactPass219H36ClosureWitnessV1 {
    uint32_t version;
    uint32_t a2;
    uint32_t b2;
    uint32_t c2;
    uint32_t b4;
    uint32_t b6;
    uint32_t c4;
    uint32_t denominator;
    uint32_t lhs_numerator;
    uint32_t lhs_denominator;
    uint32_t lhs_value;
    uint32_t rhs_value;
    uint32_t h36_value;
    uint32_t manifold_base;
    uint32_t manifold_power;
    uint64_t manifold_cardinality;
    uint8_t identity_equal;
    uint8_t manifold_cardinality_equal;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36ClosureWitnessV1;

HHSExactPass219ParadoxStatusV1
hhs_exact_pass219_paradox_analyze(
    const HHSExactPass219ParadoxProblemV1 *problem,
    HHSExactPass219ParadoxWitnessV1 *out);

HHSExactPass219ParadoxStatusV1
hhs_exact_pass219_paradox_witness_validate(
    const HHSExactPass219ParadoxProblemV1 *problem,
    const HHSExactPass219ParadoxWitnessV1 *witness);

HHSExactPass219ParadoxStatusV1
hhs_exact_pass219_h36_closure_identity(
    HHSExactPass219H36ClosureWitnessV1 *out);

HHSExactPass219ParadoxStatusV1
hhs_exact_pass219_h36_closure_identity_validate(
    const HHSExactPass219H36ClosureWitnessV1 *witness);

#ifdef __cplusplus
}
#endif

#endif

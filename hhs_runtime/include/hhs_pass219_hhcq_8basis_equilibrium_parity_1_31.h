#ifndef HHS_PASS219_HHCQ_8BASIS_EQUILIBRIUM_PARITY_1_31_H
#define HHS_PASS219_HHCQ_8BASIS_EQUILIBRIUM_PARITY_1_31_H

#include "hhs_pass219_hhcq_prime_rational_expansion_1_30.h"
#include "hhs_pass219_octonion_runtime_1_19.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_VERSION UINT32_C(0x0001001F)
#define HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SOURCE_BYTES UINT32_C(700)
#define HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SHA256_BYTES UINT32_C(32)
#define HHS_EXACT_PASS219_HHCQ_8BASIS_COUNT UINT32_C(8)

typedef enum HHSExactPass219HHCQParityOrientationV1 {
    HHS_EXACT_PASS219_HHCQ_PARITY_ORIENTATION_INVALID = 0,
    HHS_EXACT_PASS219_HHCQ_PARITY_ORIENTATION_DIRECT = 1,
    HHS_EXACT_PASS219_HHCQ_PARITY_ORIENTATION_REVERSED = 2
} HHSExactPass219HHCQParityOrientationV1;

typedef struct HHSExactPass219HHCQ8BasisParityDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t source_bytes;
    uint32_t inherited_policy_state_bytes;
    uint32_t a2;
    uint32_t b2;
    uint32_t c2;
    uint32_t update_quantum;
    uint32_t phase_modulus;
    uint32_t parameter_count;
    uint32_t basis_count;
    uint8_t source_sha256[HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SHA256_BYTES];
    uint8_t verbatim_source_preserved;
    uint8_t basis_constants_derived;
    uint8_t complete_8basis_equilibrium;
    uint8_t ordered_noncommutative_products_preserved;
    uint8_t exact_rational_macro_p;
    uint8_t independent_equilibrium_validator;
    uint8_t candidate_transport_delta_only;
    uint8_t squared_coordinate_orientation_gate;
    uint8_t x2_parity_equals_x_parity;
    uint8_t symbolic_exponent_retained;
    uint8_t native_zero_over_zero_u0_closure;
    uint8_t ordinary_negative_base_exponent_evaluated;
    uint8_t matrix_order_contract_preserved;
    uint8_t phase10_prime_rational_semantics_inherited;
    uint8_t eval_under_vm81_constraint_intersection;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[2];
} HHSExactPass219HHCQ8BasisParityDescriptorV1;

typedef struct HHSExactPass219HHCQ8BasisEquilibriumV1 {
    uint32_t struct_size;
    uint32_t version;
    uint16_t prime_p;
    uint16_t prime_q;
    HHSExactPass219OctonionStateV1 phase_state;
    uint16_t phase_sum;
    uint16_t reserved0;
    uint64_t macro_p_numerator;
    uint64_t macro_p_denominator;
    int64_t transport_delta_numerator;
    uint64_t transport_delta_denominator;
    uint8_t macro_p_constructed_from_phase_state;
    uint8_t macro_p_supplied_independently;
    uint8_t equilibrium_exact;
    uint8_t transport_reconciliation_required;
    uint8_t transport_delta_integral;
    uint8_t ordered_products_preserved;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
    uint8_t reserved1[6];
    uint64_t equilibrium_signature64;
} HHSExactPass219HHCQ8BasisEquilibriumV1;

typedef struct HHSExactPass219HHCQParityGateV1 {
    uint32_t struct_size;
    uint32_t version;
    uint16_t prime_p;
    uint16_t prime_q;
    uint8_t x_phase72;
    uint8_t y_phase72;
    uint8_t x_squared_mod72;
    uint8_t x_squared_parity;
    uint8_t orientation;
    int8_t orientation_sign;
    uint8_t ordered_xy_phase;
    uint8_t ordered_yx_phase;
    uint8_t ordered_zw_phase;
    uint8_t ordered_wz_phase;
    uint8_t matrix_order_exact;
    uint8_t symbolic_exponent_retained;
    uint8_t native_zero_over_zero_u0_closure;
    uint8_t phase10_expansion_executed;
    uint8_t prime_rational_constructor_closure_exact;
    uint8_t polynomial_or_native_closure_exact;
    uint8_t ordinary_negative_base_exponent_evaluated;
    uint8_t x2_parity_identity_exact;
    uint8_t effective_resolution_index;
    uint8_t resolution_noncoarsening;
    uint16_t effective_resolution_parameters;
    uint16_t effective_region_count;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
    HHSExactPass219HHCQPrimeRationalExpansionV1 expansion;
    uint64_t parity_signature64;
} HHSExactPass219HHCQParityGateV1;

typedef struct HHSExactPass219HHCQ8BasisManifoldV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219HHCQ8BasisEquilibriumV1 equilibrium;
    HHSExactPass219HHCQParityGateV1 parity_gate;
    uint8_t octonion_state_valid;
    uint8_t full_octonion_surface_validated;
    uint8_t phase10_product_closure_valid;
    uint8_t native_zero_over_zero_u0_closure;
    uint8_t prime_macro_closure_valid;
    uint8_t polynomial_or_native_closure_valid;
    uint8_t matrix_order_exact;
    uint8_t equilibrium_exact;
    uint8_t parity_orientation_exact;
    uint8_t resolution_noncoarsening;
    uint8_t constraint_intersection_satisfied;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[6];
    uint64_t manifold_signature64;
} HHSExactPass219HHCQ8BasisManifoldV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_hhcq_8basis_parity_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_8basis_parity_descriptor(
    HHSExactPass219HHCQ8BasisParityDescriptorV1 *out_descriptor);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_8basis_parity_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_8basis_equilibrium_construct(
    uint16_t prime_p,
    uint16_t prime_q,
    const HHSExactPass219OctonionStateV1 *phase_state,
    HHSExactPass219HHCQ8BasisEquilibriumV1 *out_equilibrium);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_8basis_equilibrium_validate(
    uint16_t prime_p,
    uint16_t prime_q,
    const HHSExactPass219OctonionStateV1 *phase_state,
    uint64_t macro_p_numerator,
    uint64_t macro_p_denominator,
    HHSExactPass219HHCQ8BasisEquilibriumV1 *out_equilibrium);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_parity_gate(
    uint16_t prime_p,
    uint16_t prime_q,
    const HHSExactPass219OctonionStateV1 *phase_state,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQParityGateV1 *out_gate);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_8basis_manifold_evaluate(
    uint16_t prime_p,
    uint16_t prime_q,
    const HHSExactPass219OctonionStateV1 *phase_state,
    uint64_t macro_p_numerator,
    uint64_t macro_p_denominator,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQ8BasisManifoldV1 *out_manifold);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_8basis_from_vm81(
    const HHSExactVM81Frame *frame,
    uint8_t x_cell,
    uint8_t y_cell,
    uint8_t z_cell,
    uint8_t w_cell,
    uint16_t prime_p,
    uint16_t prime_q,
    uint64_t macro_p_numerator,
    uint64_t macro_p_denominator,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQ8BasisManifoldV1 *out_manifold);

#ifdef __cplusplus
}
#endif

#endif

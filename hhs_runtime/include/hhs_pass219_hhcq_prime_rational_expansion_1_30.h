#ifndef HHS_PASS219_HHCQ_PRIME_RATIONAL_EXPANSION_1_30_H
#define HHS_PASS219_HHCQ_PRIME_RATIONAL_EXPANSION_1_30_H

#include "hhs_pass219_hhcq_reciprocal_economy_1_29.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_VERSION UINT32_C(0x0001001E)
#define HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SOURCE_BYTES UINT32_C(135)
#define HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SHA256_BYTES UINT32_C(32)
#define HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_MAX_PRIME UINT32_C(65521)
#define HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_MAX_CANDIDATES UINT32_C(16)

typedef enum HHSExactPass219HHCQPrimeRationalDecisionV1 {
    HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_INVALID = 0,
    HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_REJECTED = 1,
    HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_ADMITTED = 2
} HHSExactPass219HHCQPrimeRationalDecisionV1;

typedef struct HHSExactPass219HHCQPrimeRationalDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t inherited_policy_state_bytes;
    uint32_t source_bytes;
    uint64_t economy_parity_units;
    uint32_t phase_modulus;
    uint32_t divisor_count;
    uint8_t verbatim_extension_source_preserved;
    uint8_t two_prime_rational_boundary;
    uint8_t ab_equals_p4_constructor;
    uint8_t reciprocal_ab_ba_closure;
    uint8_t normalized_product_scale_witness;
    uint8_t symbolic_polynomial_root_retained;
    uint8_t exact_rational_cross_multiplication;
    uint8_t monotone_resolution_expansion;
    uint8_t exact_one_to_one_information_closure;
    uint8_t phase5_resolution_locked;
    uint8_t fixed_size_policy_state;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[2];
    uint8_t source_sha256[HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SHA256_BYTES];
} HHSExactPass219HHCQPrimeRationalDescriptorV1;

typedef struct HHSExactPass219HHCQPrimeRationalExpansionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint16_t prime_p;
    uint16_t prime_q;
    uint8_t x_phase72;
    uint8_t y_phase72;
    uint8_t base_resolution_index;
    uint8_t polynomial_resolution_index;
    uint8_t expanded_resolution_index;
    uint8_t expansion_phase72;
    uint16_t expanded_resolution_parameters;
    uint16_t expanded_region_count;
    uint64_t a_over_b_numerator;
    uint64_t a_over_b_denominator;
    uint64_t b_over_a_numerator;
    uint64_t b_over_a_denominator;
    int32_t polynomial_base;
    uint32_t reserved1;
    uint64_t polynomial_numerator;
    uint64_t polynomial_denominator;
    uint8_t product_ab_equals_p4;
    uint8_t sqrt_ab_equals_p2;
    uint8_t reciprocal_product_equals_one;
    uint8_t polynomial_fraction_reduced;
    uint8_t symbolic_sqrt_ab_retained;
    uint8_t noncoarsening;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
    uint8_t reserved2[6];
    uint64_t expansion_signature64;
} HHSExactPass219HHCQPrimeRationalExpansionV1;

typedef struct HHSExactPass219HHCQPrimeRationalCandidateV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t route_id;
    uint16_t prime_p;
    uint16_t prime_q;
    uint8_t x_phase72;
    uint8_t y_phase72;
    uint8_t intrinsic_resolution_index;
    uint8_t effective_resolution_index;
    uint8_t required_resolution_index;
    uint8_t reserved0;

    uint64_t latency_units;
    uint64_t memory_units;
    uint64_t compression_units;
    uint64_t translation_units;

    uint64_t redundancy_spend_units;
    uint64_t ecc_spend_units;
    uint64_t precision_spend_units;
    uint64_t learning_spend_units;

    uint32_t lossy_information_units;
    uint32_t recovered_information_units;

    uint8_t exact_semantic_closure;
    uint8_t exact_reconstruction;
    uint8_t all_native_modalities_translatable;
    uint8_t one_step_translation;
    uint8_t phase5_resolution_locked;
    uint8_t candidate_only;
    uint8_t canonical_authority_requested;
    uint8_t floating_point_authority_requested;
} HHSExactPass219HHCQPrimeRationalCandidateV1;

typedef struct HHSExactPass219HHCQPrimeRationalResultV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t route_id;
    uint32_t decision;
    HHSExactPass219HHCQPrimeRationalExpansionV1 expansion;

    uint64_t latency_credit_units;
    uint64_t memory_credit_units;
    uint64_t compression_credit_units;
    uint64_t translation_credit_units;
    uint64_t latency_debt_units;
    uint64_t memory_debt_units;
    uint64_t compression_debt_units;
    uint64_t translation_debt_units;
    uint64_t total_savings_units;
    uint64_t total_axis_debt_units;
    uint64_t total_spend_units;
    int64_t net_budget_units;

    uint32_t lossy_information_units;
    uint32_t recovered_information_units;
    uint8_t rational_bounds_met;
    uint8_t information_one_to_one;
    uint8_t expanded_resolution_met;
    uint8_t lower_resolution_recovered;
    uint8_t exact_semantic_closure;
    uint8_t exact_reconstruction;
    uint8_t all_native_modalities_translatable;
    uint8_t one_step_translation;
    uint8_t phase5_resolution_locked;
    uint8_t budget_nonnegative;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
    uint8_t reserved0[2];
    uint64_t result_signature64;
} HHSExactPass219HHCQPrimeRationalResultV1;

typedef struct HHSExactPass219HHCQPrimeRationalSelectionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t candidate_count;
    uint32_t admitted_count;
    uint32_t selected_route_id;
    uint32_t selected_candidate_index;
    uint8_t selected_expanded_resolution_index;
    uint8_t selected_intrinsic_resolution_index;
    uint16_t selected_expanded_resolution_parameters;
    int64_t selected_net_budget_units;
    uint64_t selection_signature64;
    uint8_t exact_integer_only;
    uint8_t candidate_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
    uint8_t reserved0[4];
} HHSExactPass219HHCQPrimeRationalSelectionV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_hhcq_prime_rational_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_prime_rational_descriptor(
    HHSExactPass219HHCQPrimeRationalDescriptorV1 *out_descriptor);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_prime_rational_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_prime_rational_expand(
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t x_phase72,
    uint8_t y_phase72,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQPrimeRationalExpansionV1 *out_expansion);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_prime_rational_evaluate(
    const HHSExactPass219HHCQPrimeRationalCandidateV1 *candidate,
    HHSExactPass219HHCQPrimeRationalResultV1 *out_result);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_prime_rational_select(
    const HHSExactPass219HHCQPrimeRationalCandidateV1 *candidates,
    size_t candidate_count,
    HHSExactPass219HHCQPrimeRationalSelectionV1 *out_selection);

#ifdef __cplusplus
}
#endif

#endif

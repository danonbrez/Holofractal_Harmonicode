#ifndef HHS_PASS219_LANE5_EXACT_BOUNDARY_QUANTUM_THERMO_1_35_H
#define HHS_PASS219_LANE5_EXACT_BOUNDARY_QUANTUM_THERMO_1_35_H

#include "hhs_pass219_lane5_global_holographic_nucleus_1_34.h"
#include "hhs_pass219_core_constraint_dynamic_circuit_1_23.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_BOUNDARY_QT_VERSION UINT32_C(0x00010023)
#define HHS_EXACT_PASS219_LANE5_BOUNDARY_SOURCE_BYTES UINT32_C(681)
#define HHS_EXACT_PASS219_LANE5_BOUNDARY_SHA256_BYTES UINT32_C(32)
#define HHS_EXACT_PASS219_LANE5_BOUNDARY_MAX_BIGINT_BYTES HHS_EXACT_VM81_FRAME_BYTES

typedef enum HHSExactPass219Lane5BoundaryClassV1 {
    HHS_EXACT_PASS219_LANE5_BOUNDARY_REJECT = -1,
    HHS_EXACT_PASS219_LANE5_BOUNDARY_UNRESOLVED = 0,
    HHS_EXACT_PASS219_LANE5_BOUNDARY_ADMIT = 1
} HHSExactPass219Lane5BoundaryClassV1;

typedef enum HHSExactPass219Lane5BoundaryReasonV1 {
    HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_NONE = 0,
    HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_SOURCE_IDENTITY = 1,
    HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_LANE5_MEDIATION = 2,
    HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FACTORIAL_ENCODING = 3,
    HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FACTORIAL_DENOMINATOR_ZERO = 4,
    HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FACTORIAL_NONINTEGRAL = 5,
    HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_SYMBOLIC_TRANSCENDENTAL = 6,
    HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FLOAT_CANONICAL_REQUEST = 7,
    HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FULL_RESIDUAL_UNRESOLVED = 8,
    HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FULL_RESIDUAL_NONZERO = 9,
    HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_EVALUATOR_PROVENANCE = 10
} HHSExactPass219Lane5BoundaryReasonV1;

typedef struct HHSExactPass219Lane5BoundaryQTAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t boundary_source_bytes;
    uint8_t boundary_source_sha256[HHS_EXACT_PASS219_LANE5_BOUNDARY_SHA256_BYTES];
    uint8_t verbatim_boundary_preserved;
    uint8_t indivisible_constraint_surface;
    uint8_t mod72_72_5184_exact_zero;
    uint8_t factorial_bigint_domain_exact;
    uint8_t symbolic_transcendentals_required;
    uint8_t pass117_exact_quantum_semantics_bound;
    uint8_t pass118_symbolic_harmonicode_bound;
    uint8_t quantum_probability_candidate_only;
    uint8_t hyperbolic_projection_candidate_only;
    uint8_t thermodynamic_witness_candidate_only;
    uint8_t deterministic_sampling_replayable;
    uint8_t physical_quantum_execution_claim;
    uint8_t exact_integer_canonical_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_lane5_mediation;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t initial_full_residual_evaluator_available;
    uint8_t reserved0[9];
} HHSExactPass219Lane5BoundaryQTAuthorityV1;

typedef struct HHSExactPass219Lane5FactorialDomainV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactBigUIntView numerator;
    HHSExactBigUIntView denominator;
} HHSExactPass219Lane5FactorialDomainV1;

typedef struct HHSExactPass219Lane5BoundaryPreflightV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t boundary_source_sha256[HHS_EXACT_PASS219_LANE5_BOUNDARY_SHA256_BYTES];
    HHSExactPass219Lane5MediationRequestV1 lane5_request;
    HHSExactPass219Lane5MediationReceiptV1 lane5_receipt;
    HHSExactPass219Lane5FactorialDomainV1 factorial_domain;
    uint8_t symbolic_transcendentals_preserved;
    uint8_t floating_point_canonical_requested;
    uint8_t exact_full_residual_evaluator_receipt_present;
    int8_t exact_full_residual_classification;
    uint64_t exact_full_residual_evaluator_signature64;
    uint64_t quantum_witness_signature64;
    uint64_t hyperbolic_witness_signature64;
    uint64_t thermodynamic_witness_signature64;
    uint64_t deterministic_sampling_signature64;
} HHSExactPass219Lane5BoundaryPreflightV1;

typedef struct HHSExactPass219Lane5BoundaryReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    int32_t boundary_class;
    uint32_t reason;
    uint32_t mod72_72_5184;
    uint8_t source_identity_verified;
    uint8_t lane5_mediation_recomputed;
    uint8_t factorial_encoding_canonical;
    uint8_t factorial_denominator_nonzero;
    uint8_t factorial_argument_integral;
    uint8_t symbolic_transcendentals_preserved;
    uint8_t full_residual_unresolved;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t requires_environmental_admission;
    uint8_t reserved0[3];
    uint64_t lane5_mediation_signature64;
    uint64_t boundary_witness_signature64;
    uint64_t exploration_witness_signature64;
} HHSExactPass219Lane5BoundaryReceiptV1;

typedef struct HHSExactPass219ThermoReciprocalInputV1 {
    uint32_t struct_size;
    uint32_t version;
    uint64_t g_numerator;
    uint64_t g_denominator;
} HHSExactPass219ThermoReciprocalInputV1;

typedef struct HHSExactPass219ThermoReciprocalReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint64_t reduced_numerator;
    uint64_t reduced_denominator;
    uint8_t positive_domain;
    uint8_t reciprocal_equilibrium;
    uint8_t logarithm_cancelled_symbolically;
    uint8_t exact_rational;
    uint8_t candidate_only;
    uint8_t floating_point_authority;
    uint8_t canonical_mutation_authority;
    uint8_t reserved0;
    uint64_t witness_signature64;
} HHSExactPass219ThermoReciprocalReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_boundary_qt_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_boundary_qt_authority(
    HHSExactPass219Lane5BoundaryQTAuthorityV1 *out_authority
);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_boundary_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_boundary_source_sha256(
    uint8_t out_sha256[HHS_EXACT_PASS219_LANE5_BOUNDARY_SHA256_BYTES]
);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_boundary_mod_anchor(
    uint32_t *out_remainder
);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_factorial_domain_check(
    const HHSExactPass219Lane5FactorialDomainV1 *domain,
    uint8_t *out_encoding_canonical,
    uint8_t *out_denominator_nonzero,
    uint8_t *out_integral
);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_boundary_preflight(
    const HHSExactPass219Lane5BoundaryPreflightV1 *request,
    HHSExactPass219Lane5BoundaryReceiptV1 *out_receipt
);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_thermo_reciprocal_closure(
    const HHSExactPass219ThermoReciprocalInputV1 *input,
    HHSExactPass219ThermoReciprocalReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif

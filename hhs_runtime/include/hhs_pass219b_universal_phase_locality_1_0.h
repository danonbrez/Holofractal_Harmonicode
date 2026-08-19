#ifndef HHS_PASS219B_UNIVERSAL_PHASE_LOCALITY_1_0_H
#define HHS_PASS219B_UNIVERSAL_PHASE_LOCALITY_1_0_H

#include "hhs_pass219b_phase_quantized_hydration_1_0.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219B_PHASE_LOCALITY_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219B_PHASE_LOCALITY_VERSION_MINOR 0U
#define HHS_EXACT_PASS219B_PHASE_LOCALITY_VERSION_PATCH 0U
#define HHS_EXACT_PASS219B_PHASE_LOCALITY_MAX_DEPTH 9U

typedef enum HHSExactPass219BPhaseLocalityRoute {
    HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_NONE = 0,
    HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_LOCAL = 1,
    HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_DENSE_REQUIRED = 2,
    HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_AUDIT_DENSE = 3
} HHSExactPass219BPhaseLocalityRoute;

typedef struct HHSExactPass219BPhaseLocalityDimensionV1 {
    uint64_t potential_q;
    uint64_t selected_s;
} HHSExactPass219BPhaseLocalityDimensionV1;

typedef struct HHSExactPass219BPhaseLocalityPlanV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t depth;
    uint32_t route;
    uint32_t exact_selector_available;
    uint32_t audit_dense_authorized;
    uint32_t stable_identity_required;
    uint32_t exact_selected_equality_required;
    uint64_t potential_phase_volume;
    uint64_t materialized_phase_volume;
    uint64_t reduction_numerator;
    uint64_t reduction_denominator;
    uint64_t base_units;
    uint64_t required_realized_units;
    uint8_t dense_realization_forbidden;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_persistence_authority;
    uint8_t canonical_hash72_authority;
    uint8_t reserved0[4];
} HHSExactPass219BPhaseLocalityPlanV1;

HHS_EXACT_API uint32_t hhs_exact_pass219b_phase_locality_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_phase_locality_plan(
    const HHSExactPass219BPhaseLocalityDimensionV1 *dimensions,
    size_t depth,
    uint32_t exact_selector_available,
    uint32_t audit_dense_authorized,
    uint64_t base_units,
    HHSExactPass219BPhaseLocalityPlanV1 *out_plan
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_phase_locality_verify_realization(
    const HHSExactPass219BPhaseLocalityPlanV1 *plan,
    uint64_t realized_units,
    uint32_t original_identity_preserved,
    uint32_t exact_selected_equal,
    uint32_t canonical_authority_requested
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_phase_locality_original_identity(
    const uint64_t *origins,
    const uint64_t *radices,
    size_t depth,
    uint64_t family,
    uint64_t family_count,
    uint64_t *out_identity
);

#ifdef __cplusplus
}
#endif

#endif

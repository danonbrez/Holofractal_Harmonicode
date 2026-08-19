#include "../include/hhs_pass219b_universal_phase_locality_1_0.h"

#include <limits.h>
#include <string.h>

static uint32_t hhs_exact_pass219b_phase_locality_version_word(void) {
    return (HHS_EXACT_PASS219B_PHASE_LOCALITY_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219B_PHASE_LOCALITY_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219B_PHASE_LOCALITY_VERSION_PATCH;
}

static int hhs_exact_pass219b_mul_u64(uint64_t a, uint64_t b, uint64_t *out) {
    if (out == NULL)
        return 0;
    if (a != 0U && b > UINT64_MAX / a)
        return 0;
    *out = a * b;
    return 1;
}

static int hhs_exact_pass219b_add_u64(uint64_t a, uint64_t b, uint64_t *out) {
    if (out == NULL || b > UINT64_MAX - a)
        return 0;
    *out = a + b;
    return 1;
}

static uint64_t hhs_exact_pass219b_gcd_u64(uint64_t a, uint64_t b) {
    while (b != 0U) {
        uint64_t t = a % b;
        a = b;
        b = t;
    }
    return a;
}

uint32_t hhs_exact_pass219b_phase_locality_version(void) {
    return hhs_exact_pass219b_phase_locality_version_word();
}

HHSExactStatus hhs_exact_pass219b_phase_locality_plan(
    const HHSExactPass219BPhaseLocalityDimensionV1 *dimensions,
    size_t depth,
    uint32_t exact_selector_available,
    uint32_t audit_dense_authorized,
    uint64_t base_units,
    HHSExactPass219BPhaseLocalityPlanV1 *out_plan
) {
    uint64_t q_product = 1U;
    uint64_t s_product = 1U;
    uint64_t required_units;
    uint64_t gcd;
    size_t i;

    if (dimensions == NULL || out_plan == NULL || base_units == 0U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (depth == 0U || depth > HHS_EXACT_PASS219B_PHASE_LOCALITY_MAX_DEPTH)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (exact_selector_available > 1U || audit_dense_authorized > 1U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    for (i = 0U; i < depth; ++i) {
        if (dimensions[i].potential_q == 0U || dimensions[i].selected_s == 0U ||
            dimensions[i].selected_s > dimensions[i].potential_q)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        if (!hhs_exact_pass219b_mul_u64(q_product, dimensions[i].potential_q, &q_product) ||
            !hhs_exact_pass219b_mul_u64(s_product, dimensions[i].selected_s, &s_product))
            return HHS_EXACT_STATUS_RANGE_ERROR;
    }

    memset(out_plan, 0, sizeof(*out_plan));
    out_plan->struct_size = (uint32_t)sizeof(*out_plan);
    out_plan->version = hhs_exact_pass219b_phase_locality_version_word();
    out_plan->depth = (uint32_t)depth;
    out_plan->exact_selector_available = exact_selector_available;
    out_plan->audit_dense_authorized = audit_dense_authorized;
    out_plan->stable_identity_required = 1U;
    out_plan->exact_selected_equality_required = 1U;
    out_plan->potential_phase_volume = q_product;
    out_plan->materialized_phase_volume = s_product;
    out_plan->base_units = base_units;

    gcd = hhs_exact_pass219b_gcd_u64(q_product, s_product);
    if (gcd == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_plan->reduction_numerator = q_product / gcd;
    out_plan->reduction_denominator = s_product / gcd;

    if (audit_dense_authorized != 0U) {
        out_plan->route = HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_AUDIT_DENSE;
        out_plan->dense_realization_forbidden = 0U;
        if (!hhs_exact_pass219b_mul_u64(base_units, q_product, &required_units))
            return HHS_EXACT_STATUS_RANGE_ERROR;
    } else if (exact_selector_available != 0U) {
        out_plan->route = HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_LOCAL;
        out_plan->dense_realization_forbidden = (uint8_t)(s_product < q_product ? 1U : 0U);
        if (!hhs_exact_pass219b_mul_u64(base_units, s_product, &required_units))
            return HHS_EXACT_STATUS_RANGE_ERROR;
    } else {
        out_plan->route = HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_DENSE_REQUIRED;
        out_plan->dense_realization_forbidden = 0U;
        if (!hhs_exact_pass219b_mul_u64(base_units, q_product, &required_units))
            return HHS_EXACT_STATUS_RANGE_ERROR;
    }

    out_plan->required_realized_units = required_units;
    out_plan->canonical_mutation_authority = 0U;
    out_plan->canonical_persistence_authority = 0U;
    out_plan->canonical_hash72_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219b_phase_locality_verify_realization(
    const HHSExactPass219BPhaseLocalityPlanV1 *plan,
    uint64_t realized_units,
    uint32_t original_identity_preserved,
    uint32_t exact_selected_equal,
    uint32_t canonical_authority_requested
) {
    if (plan == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (plan->struct_size != sizeof(*plan) ||
        plan->version != hhs_exact_pass219b_phase_locality_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (original_identity_preserved > 1U || exact_selected_equal > 1U ||
        canonical_authority_requested > 1U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (canonical_authority_requested != 0U ||
        plan->canonical_mutation_authority != 0U ||
        plan->canonical_persistence_authority != 0U ||
        plan->canonical_hash72_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (original_identity_preserved == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (realized_units != plan->required_realized_units)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (plan->route == HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_LOCAL &&
        exact_selected_equal == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (plan->route != HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_LOCAL &&
        plan->route != HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_DENSE_REQUIRED &&
        plan->route != HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_AUDIT_DENSE)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219b_phase_locality_original_identity(
    const uint64_t *origins,
    const uint64_t *radices,
    size_t depth,
    uint64_t family,
    uint64_t family_count,
    uint64_t *out_identity
) {
    uint64_t identity;
    uint64_t next;
    size_t i;

    if (origins == NULL || radices == NULL || out_identity == NULL || family_count == 0U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (depth == 0U || depth > HHS_EXACT_PASS219B_PHASE_LOCALITY_MAX_DEPTH)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (family >= family_count || origins[0] >= radices[0] || radices[0] == 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    identity = origins[0];
    for (i = 1U; i < depth; ++i) {
        if (radices[i] == 0U || origins[i] >= radices[i])
            return HHS_EXACT_STATUS_RANGE_ERROR;
        if (!hhs_exact_pass219b_mul_u64(identity, radices[i], &next) ||
            !hhs_exact_pass219b_add_u64(next, origins[i], &identity))
            return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    if (!hhs_exact_pass219b_mul_u64(identity, family_count, &next) ||
        !hhs_exact_pass219b_add_u64(next, family, &identity))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    *out_identity = identity;
    return HHS_EXACT_STATUS_OK;
}

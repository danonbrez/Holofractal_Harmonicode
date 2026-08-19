#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>

int main(void) {
    const HHSExactPass219BPhaseLocalityDimensionV1 local_dims[2] = {
        {81U, 1U}, {81U, 1U}
    };
    const HHSExactPass219BPhaseLocalityDimensionV1 dense_dims[2] = {
        {81U, 81U}, {81U, 81U}
    };
    HHSExactPass219BPhaseLocalityPlanV1 plan;
    uint64_t origins[2] = {37U, 53U};
    uint64_t radices[2] = {81U, 81U};
    uint64_t id0 = 0U;
    uint64_t id1 = 0U;

    assert(hhs_exact_pass219b_phase_locality_plan(
        local_dims, 2U, 1U, 0U, 10368U, &plan) == HHS_EXACT_STATUS_OK);
    assert(plan.route == HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_LOCAL);
    assert(plan.potential_phase_volume == 6561U);
    assert(plan.materialized_phase_volume == 1U);
    assert(plan.reduction_numerator == 6561U);
    assert(plan.reduction_denominator == 1U);
    assert(plan.required_realized_units == 10368U);
    assert(plan.dense_realization_forbidden == 1U);
    assert(plan.stable_identity_required == 1U);
    assert(plan.exact_selected_equality_required == 1U);
    assert(plan.canonical_mutation_authority == 0U);
    assert(plan.canonical_persistence_authority == 0U);
    assert(plan.canonical_hash72_authority == 0U);

    assert(hhs_exact_pass219b_phase_locality_verify_realization(
        &plan, 10368U, 1U, 1U, 0U) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219b_phase_locality_verify_realization(
        &plan, 68024448U, 1U, 1U, 0U) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(hhs_exact_pass219b_phase_locality_verify_realization(
        &plan, 10368U, 0U, 1U, 0U) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(hhs_exact_pass219b_phase_locality_verify_realization(
        &plan, 10368U, 1U, 0U, 0U) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(hhs_exact_pass219b_phase_locality_verify_realization(
        &plan, 10368U, 1U, 1U, 1U) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    assert(hhs_exact_pass219b_phase_locality_plan(
        local_dims, 2U, 0U, 0U, 10368U, &plan) == HHS_EXACT_STATUS_OK);
    assert(plan.route == HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_DENSE_REQUIRED);
    assert(plan.required_realized_units == 68024448U);
    assert(plan.dense_realization_forbidden == 0U);

    assert(hhs_exact_pass219b_phase_locality_plan(
        local_dims, 2U, 1U, 1U, 10368U, &plan) == HHS_EXACT_STATUS_OK);
    assert(plan.route == HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_AUDIT_DENSE);
    assert(plan.required_realized_units == 68024448U);

    assert(hhs_exact_pass219b_phase_locality_plan(
        dense_dims, 2U, 1U, 0U, 10368U, &plan) == HHS_EXACT_STATUS_OK);
    assert(plan.route == HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_LOCAL);
    assert(plan.dense_realization_forbidden == 0U);
    assert(plan.reduction_numerator == 1U && plan.reduction_denominator == 1U);

    assert(hhs_exact_pass219b_phase_locality_original_identity(
        origins, radices, 2U, 0U, 2U, &id0) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219b_phase_locality_original_identity(
        origins, radices, 2U, 1U, 2U, &id1) == HHS_EXACT_STATUS_OK);
    assert(id0 == ((37U * 81U + 53U) * 2U));
    assert(id1 == id0 + 1U);

    {
        HHSExactPass219BPhaseLocalityDimensionV1 bad[1] = {{81U, 82U}};
        assert(hhs_exact_pass219b_phase_locality_plan(
            bad, 1U, 1U, 0U, 1U, &plan) == HHS_EXACT_STATUS_RANGE_ERROR);
    }
    {
        HHSExactPass219BPhaseLocalityDimensionV1 overflow[2] = {
            {UINT64_MAX, UINT64_MAX}, {2U, 1U}
        };
        assert(hhs_exact_pass219b_phase_locality_plan(
            overflow, 2U, 1U, 0U, 1U, &plan) == HHS_EXACT_STATUS_RANGE_ERROR);
    }

    return 0;
}

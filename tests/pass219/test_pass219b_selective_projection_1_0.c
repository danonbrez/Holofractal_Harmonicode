#include "../../hhs_runtime/include/hhs_pass219b_selective_projection_1_0.h"

#include <assert.h>
#include <stddef.h>
#include <stdint.h>

static void assert_full_benchmark_counts(void) {
    static const struct {
        uint32_t p;
        uint32_t q;
        uint64_t expected;
    } cases[] = {
        {1U, 3U, 5875200ULL},
        {7U, 20U, 6168960ULL},
        {5U, 14U, 6294860ULL},
        {4U, 11U, 6409311ULL},
        {3U, 8U, 6609600ULL},
        {2U, 5U, 7050240ULL},
        {5U, 12U, 7344000ULL}
    };
    size_t i;
    for (i = 0U; i < sizeof(cases) / sizeof(cases[0]); ++i) {
        uint64_t selected = 0U;
        assert(hhs_exact_pass219b_selective_projection_selected_count(
            17625600ULL, cases[i].p, cases[i].q, &selected) == HHS_EXACT_STATUS_OK);
        assert(selected == cases[i].expected);
    }
}

int main(void) {
    HHSExactPass219BSelectiveProjectionPlanV1 plan;
    HHSExactPass219BProjectionCellRangeV1 ranges[81];
    uint32_t ids[1728];
    uint32_t small[10];
    uint64_t selected = 0U;
    size_t count = 0U;
    size_t i;

    assert_full_benchmark_counts();

    assert(hhs_exact_pass219b_selective_projection_plan(
        17625600ULL, 1U, 3U, &plan) == HHS_EXACT_STATUS_OK);
    assert(plan.selected_count == 5875200ULL);
    assert(plan.avoided_count == 11750400ULL);
    assert(plan.precomputed_id_buffer_required == 1U);
    assert(plan.precomputed_cell_ranges_required == 1U);
    assert(plan.measured_hot_path_division_forbidden == 1U);
    assert(plan.measured_hot_path_modulo_forbidden == 1U);
    assert(plan.projection_only == 1U);
    assert(plan.canonical_mutation_authority == 0U);
    assert(plan.canonical_persistence_authority == 0U);
    assert(plan.canonical_hash72_authority == 0U);

    assert(hhs_exact_pass219b_selective_projection_build_ids_u32(
        5184ULL, 1U, 3U, ids, 1728U, &count) == HHS_EXACT_STATUS_OK);
    assert(count == 1728U);
    assert(ids[0] == 0U);
    assert(ids[1] == 3U);
    assert(ids[count - 1U] == 5181U);
    assert(hhs_exact_pass219b_selective_projection_validate_ids_u32(
        5184ULL, 1U, 3U, ids, count) == HHS_EXACT_STATUS_OK);
    for (i = 1U; i < count; ++i) {
        assert(ids[i] > ids[i - 1U]);
        assert(ids[i] % 3U == 0U);
    }

    ids[17] += 1U;
    assert(hhs_exact_pass219b_selective_projection_validate_ids_u32(
        5184ULL, 1U, 3U, ids, count) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    ids[17] -= 1U;

    assert(hhs_exact_pass219b_selective_projection_build_equal_cell_ranges(
        ids, count, 5184ULL, 81U, ranges, 81U) == HHS_EXACT_STATUS_OK);
    assert(ranges[0].first_selected == 0U);
    assert(ranges[80].end_selected == 1728U);
    for (i = 1U; i < 81U; ++i) {
        assert(ranges[i].first_selected == ranges[i - 1U].end_selected);
        assert(ranges[i].end_selected >= ranges[i].first_selected);
    }

    assert(hhs_exact_pass219b_selective_projection_verify(
        &plan, plan.selected_count, 1U, 1U, 1U, 0U) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219b_selective_projection_verify(
        &plan, plan.selected_count, 1U, 1U, 1U, 1U) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(hhs_exact_pass219b_selective_projection_verify(
        &plan, plan.selected_count, 1U, 1U, 0U, 0U) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    assert(hhs_exact_pass219b_selective_projection_selected_count(
        81ULL, 0U, 3U, &selected) == HHS_EXACT_STATUS_RANGE_ERROR);
    assert(hhs_exact_pass219b_selective_projection_selected_count(
        81ULL, 4U, 3U, &selected) == HHS_EXACT_STATUS_RANGE_ERROR);
    assert(hhs_exact_pass219b_selective_projection_build_ids_u32(
        81ULL, 1U, 3U, small, 10U, &count) == HHS_EXACT_STATUS_BUFFER_TOO_SMALL);
    assert(count == 27U);
    assert(hhs_exact_pass219b_selective_projection_build_equal_cell_ranges(
        ids, 1728U, 5184ULL, 80U, ranges, 81U) == HHS_EXACT_STATUS_RANGE_ERROR);

    assert(hhs_exact_pass219b_selective_projection_plan(
        4183503552ULL, 1U, 1U, &plan) == HHS_EXACT_STATUS_OK);
    assert(plan.selected_count == 4183503552ULL);

    return 0;
}

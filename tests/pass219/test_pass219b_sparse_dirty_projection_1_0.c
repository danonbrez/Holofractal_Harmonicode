#include "../../hhs_runtime/include/hhs_pass219b_sparse_dirty_projection_1_0.h"

#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static void apply_spans_u8(
    uint8_t *destination,
    const uint8_t *current,
    const HHSExactPass219BSparseProjectionSpanV1 *spans,
    size_t span_count
) {
    size_t i;
    for (i = 0U; i < span_count; ++i) {
        size_t first = (size_t)spans[i].first_selected;
        size_t length = (size_t)(spans[i].end_selected - spans[i].first_selected);
        memcpy(destination + first, current + first, length);
    }
}

static void assert_exhaustive_small_models(void) {
    uint32_t cell_count;
    uint32_t variant;

    for (variant = 0U; variant < 5U; ++variant) {
        for (cell_count = 1U; cell_count <= 8U; ++cell_count) {
            HHSExactPass219BProjectionCellRangeV1 ranges[8];
            uint64_t selected_count = 0U;
            uint32_t cell;
            uint32_t mask;

            for (cell = 0U; cell < cell_count; ++cell) {
                uint64_t length = (uint64_t)((cell * 3U + variant) % 5U);
                ranges[cell].first_selected = selected_count;
                selected_count += length;
                ranges[cell].end_selected = selected_count;
            }
            assert(hhs_exact_pass219b_sparse_dirty_projection_validate_ranges(
                ranges, cell_count, selected_count) == HHS_EXACT_STATUS_OK);

            for (mask = 0U; mask < (1U << cell_count); ++mask) {
                uint32_t dirty_cells[8];
                size_t dirty_count = 0U;
                HHSExactPass219BSparseProjectionSpanV1 spans[8];
                HHSExactPass219BSparseDirtyProjectionPlanV1 plan;
                uint64_t expected_update = 0U;
                uint8_t direct[64] = {0U};
                uint8_t sparse[64] = {0U};
                size_t i;

                for (cell = 0U; cell < cell_count; ++cell) {
                    if ((mask & (1U << cell)) != 0U) {
                        uint64_t pos;
                        dirty_cells[dirty_count++] = cell;
                        expected_update += ranges[cell].end_selected - ranges[cell].first_selected;
                        for (pos = ranges[cell].first_selected; pos < ranges[cell].end_selected; ++pos) {
                            direct[(size_t)pos] = 1U;
                        }
                    }
                }

                assert(hhs_exact_pass219b_sparse_dirty_projection_build_spans(
                    ranges,
                    cell_count,
                    selected_count,
                    dirty_cells,
                    dirty_count,
                    spans,
                    8U,
                    &plan) == HHS_EXACT_STATUS_OK);
                assert(plan.selected_count == selected_count);
                assert(plan.update_selected_count == expected_update);
                assert(plan.avoided_selected_count == selected_count - expected_update);
                assert(plan.span_count <= dirty_count);
                assert(plan.dirty_set_completeness_required == 1U);
                assert(plan.projection_only == 1U);
                assert(plan.canonical_mutation_authority == 0U);
                assert(plan.canonical_persistence_authority == 0U);
                assert(plan.canonical_hash72_authority == 0U);

                for (i = 0U; i < (size_t)plan.span_count; ++i) {
                    uint64_t pos;
                    for (pos = spans[i].first_selected; pos < spans[i].end_selected; ++pos) {
                        sparse[(size_t)pos] = 1U;
                    }
                }
                assert(memcmp(direct, sparse, (size_t)selected_count) == 0);
                assert(hhs_exact_pass219b_sparse_dirty_projection_verify(
                    &plan,
                    spans,
                    (size_t)plan.span_count,
                    expected_update,
                    1U,
                    1U,
                    0U) == HHS_EXACT_STATUS_OK);
            }
        }
    }
}

static void assert_i7_range_integration_and_sparse_equivalence(void) {
    HHSExactPass219BProjectionCellRangeV1 ranges[81];
    HHSExactPass219BProjectionCellRangeV1 bad_ranges[81];
    HHSExactPass219BSparseProjectionSpanV1 spans[81];
    HHSExactPass219BSparseDirtyProjectionPlanV1 plan;
    uint32_t ids[1728];
    const uint32_t dirty_cells[7] = {0U, 1U, 7U, 21U, 22U, 40U, 80U};
    const uint32_t unsorted_dirty[2] = {2U, 1U};
    const uint32_t duplicate_dirty[2] = {2U, 2U};
    uint8_t previous[1728];
    uint8_t current[1728];
    uint8_t sparse[1728];
    uint64_t expected_update = 0U;
    size_t selected_count = 0U;
    size_t i;

    assert(hhs_exact_pass219b_selective_projection_build_ids_u32(
        5184ULL, 1U, 3U, ids, 1728U, &selected_count) == HHS_EXACT_STATUS_OK);
    assert(selected_count == 1728U);
    assert(hhs_exact_pass219b_selective_projection_build_equal_cell_ranges(
        ids, selected_count, 5184ULL, 81U, ranges, 81U) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219b_sparse_dirty_projection_validate_ranges(
        ranges, 81U, 1728ULL) == HHS_EXACT_STATUS_OK);

    for (i = 0U; i < 7U; ++i) {
        expected_update += ranges[dirty_cells[i]].end_selected -
                           ranges[dirty_cells[i]].first_selected;
    }

    assert(hhs_exact_pass219b_sparse_dirty_projection_build_spans(
        ranges,
        81U,
        1728ULL,
        dirty_cells,
        7U,
        spans,
        81U,
        &plan) == HHS_EXACT_STATUS_OK);
    assert(plan.dirty_cell_count == 7U);
    assert(plan.span_count == 5U);
    assert(plan.update_selected_count == expected_update);
    assert(plan.avoided_selected_count == 1728ULL - expected_update);
    assert(plan.precomputed_cell_ranges_required == 1U);
    assert(plan.dirty_cells_sorted_unique_required == 1U);
    assert(plan.dirty_set_completeness_required == 1U);
    assert(plan.contiguous_selected_spans_coalesced == 1U);
    assert(plan.measured_hot_path_division_forbidden == 1U);
    assert(plan.measured_hot_path_modulo_forbidden == 1U);

    for (i = 0U; i < selected_count; ++i) {
        previous[i] = (uint8_t)(i % 251U);
        current[i] = previous[i];
    }
    for (i = 0U; i < 7U; ++i) {
        uint64_t pos;
        for (pos = ranges[dirty_cells[i]].first_selected;
             pos < ranges[dirty_cells[i]].end_selected;
             ++pos) {
            current[(size_t)pos] ^= 0x5AU;
        }
    }
    memcpy(sparse, previous, sizeof(sparse));
    apply_spans_u8(sparse, current, spans, (size_t)plan.span_count);
    assert(memcmp(sparse, current, sizeof(current)) == 0);
    assert(hhs_exact_pass219b_sparse_dirty_projection_verify(
        &plan,
        spans,
        (size_t)plan.span_count,
        expected_update,
        1U,
        1U,
        0U) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219b_sparse_dirty_projection_verify(
        &plan,
        spans,
        (size_t)plan.span_count,
        expected_update,
        0U,
        1U,
        0U) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(hhs_exact_pass219b_sparse_dirty_projection_verify(
        &plan,
        spans,
        (size_t)plan.span_count,
        expected_update,
        1U,
        0U,
        0U) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(hhs_exact_pass219b_sparse_dirty_projection_verify(
        &plan,
        spans,
        (size_t)plan.span_count,
        expected_update,
        1U,
        1U,
        1U) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    assert(hhs_exact_pass219b_sparse_dirty_projection_build_spans(
        ranges, 81U, 1728ULL, dirty_cells, 7U, spans, 4U, &plan) ==
        HHS_EXACT_STATUS_BUFFER_TOO_SMALL);
    assert(plan.span_count == 5U);

    assert(hhs_exact_pass219b_sparse_dirty_projection_build_spans(
        ranges, 81U, 1728ULL, unsorted_dirty, 2U, spans, 81U, &plan) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(hhs_exact_pass219b_sparse_dirty_projection_build_spans(
        ranges, 81U, 1728ULL, duplicate_dirty, 2U, spans, 81U, &plan) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE);

    memcpy(bad_ranges, ranges, sizeof(ranges));
    bad_ranges[80].end_selected -= 1U;
    assert(hhs_exact_pass219b_sparse_dirty_projection_build_spans(
        bad_ranges, 81U, 1728ULL, dirty_cells, 7U, spans, 81U, &plan) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE);

    memcpy(bad_ranges, ranges, sizeof(ranges));
    bad_ranges[17].first_selected += 1U;
    assert(hhs_exact_pass219b_sparse_dirty_projection_build_spans(
        bad_ranges, 81U, 1728ULL, dirty_cells, 7U, spans, 81U, &plan) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

int main(void) {
    assert_exhaustive_small_models();
    assert_i7_range_integration_and_sparse_equivalence();
    return 0;
}

#include "hhs_pass219b_sparse_dirty_projection_1_0.h"

#include <string.h>

static uint32_t hhs_exact_pass219b_sparse_dirty_projection_pack_version(void) {
    return (HHS_EXACT_PASS219B_SPARSE_DIRTY_PROJECTION_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219B_SPARSE_DIRTY_PROJECTION_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219B_SPARSE_DIRTY_PROJECTION_VERSION_PATCH;
}

static HHSExactStatus hhs_exact_pass219b_sparse_dirty_projection_validate_dirty_cells(
    const uint32_t *dirty_cells,
    size_t dirty_cell_count,
    uint32_t cell_count
) {
    size_t i;

    if (dirty_cell_count > (size_t)cell_count) {
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    if (dirty_cell_count != 0U && dirty_cells == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    for (i = 0U; i < dirty_cell_count; ++i) {
        if (dirty_cells[i] >= cell_count) {
            return HHS_EXACT_STATUS_RANGE_ERROR;
        }
        if (i != 0U && dirty_cells[i] <= dirty_cells[i - 1U]) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }
    return HHS_EXACT_STATUS_OK;
}

HHS_EXACT_API uint32_t hhs_exact_pass219b_sparse_dirty_projection_version(void) {
    return hhs_exact_pass219b_sparse_dirty_projection_pack_version();
}

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_sparse_dirty_projection_validate_ranges(
    const HHSExactPass219BProjectionCellRangeV1 *cell_ranges,
    uint32_t cell_count,
    uint64_t selected_count
) {
    uint32_t cell;

    if (cell_ranges == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    if (cell_count == 0U || cell_count > HHS_EXACT_PASS219B_SPARSE_DIRTY_PROJECTION_MAX_CELLS) {
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    if (cell_ranges[0].first_selected != 0U) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    for (cell = 0U; cell < cell_count; ++cell) {
        if (cell_ranges[cell].end_selected < cell_ranges[cell].first_selected ||
            cell_ranges[cell].end_selected > selected_count) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        if (cell != 0U &&
            cell_ranges[cell].first_selected != cell_ranges[cell - 1U].end_selected) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }
    if (cell_ranges[cell_count - 1U].end_selected != selected_count) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_sparse_dirty_projection_build_spans(
    const HHSExactPass219BProjectionCellRangeV1 *cell_ranges,
    uint32_t cell_count,
    uint64_t selected_count,
    const uint32_t *dirty_cells,
    size_t dirty_cell_count,
    HHSExactPass219BSparseProjectionSpanV1 *out_spans,
    size_t span_capacity,
    HHSExactPass219BSparseDirtyProjectionPlanV1 *out_plan
) {
    uint64_t update_selected_count = 0U;
    uint64_t prior_span_end = 0U;
    size_t required_spans = 0U;
    size_t i;
    HHSExactStatus status;
    uint32_t have_prior_span = 0U;

    if (cell_ranges == NULL || out_plan == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    memset(out_plan, 0, sizeof(*out_plan));
    status = hhs_exact_pass219b_sparse_dirty_projection_validate_ranges(
        cell_ranges, cell_count, selected_count);
    if (status != HHS_EXACT_STATUS_OK) {
        return status;
    }
    status = hhs_exact_pass219b_sparse_dirty_projection_validate_dirty_cells(
        dirty_cells, dirty_cell_count, cell_count);
    if (status != HHS_EXACT_STATUS_OK) {
        return status;
    }

    for (i = 0U; i < dirty_cell_count; ++i) {
        const HHSExactPass219BProjectionCellRangeV1 *range = &cell_ranges[dirty_cells[i]];
        uint64_t length;
        if (range->first_selected == range->end_selected) {
            continue;
        }
        length = range->end_selected - range->first_selected;
        update_selected_count += length;
        if (have_prior_span == 0U || range->first_selected != prior_span_end) {
            ++required_spans;
        }
        prior_span_end = range->end_selected;
        have_prior_span = 1U;
    }

    out_plan->struct_size = (uint32_t)sizeof(*out_plan);
    out_plan->version = hhs_exact_pass219b_sparse_dirty_projection_pack_version();
    out_plan->cell_count = cell_count;
    out_plan->dirty_cell_count = (uint32_t)dirty_cell_count;
    out_plan->span_count = (uint32_t)required_spans;
    out_plan->selected_count = selected_count;
    out_plan->update_selected_count = update_selected_count;
    out_plan->avoided_selected_count = selected_count - update_selected_count;
    out_plan->precomputed_cell_ranges_required = 1U;
    out_plan->dirty_cells_sorted_unique_required = 1U;
    out_plan->dirty_set_completeness_required = 1U;
    out_plan->contiguous_selected_spans_coalesced = 1U;
    out_plan->measured_hot_path_division_forbidden = 1U;
    out_plan->measured_hot_path_modulo_forbidden = 1U;
    out_plan->canonical_mutation_authority = 0U;
    out_plan->canonical_persistence_authority = 0U;
    out_plan->canonical_hash72_authority = 0U;
    out_plan->projection_only = 1U;

    if (required_spans > span_capacity || (required_spans != 0U && out_spans == NULL)) {
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    }

    if (required_spans != 0U) {
        size_t cursor = 0U;
        for (i = 0U; i < dirty_cell_count; ++i) {
            const HHSExactPass219BProjectionCellRangeV1 *range = &cell_ranges[dirty_cells[i]];
            if (range->first_selected == range->end_selected) {
                continue;
            }
            if (cursor != 0U && out_spans[cursor - 1U].end_selected == range->first_selected) {
                out_spans[cursor - 1U].end_selected = range->end_selected;
            } else {
                out_spans[cursor].first_selected = range->first_selected;
                out_spans[cursor].end_selected = range->end_selected;
                ++cursor;
            }
        }
        if (cursor != required_spans) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }

    return HHS_EXACT_STATUS_OK;
}

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_sparse_dirty_projection_verify(
    const HHSExactPass219BSparseDirtyProjectionPlanV1 *plan,
    const HHSExactPass219BSparseProjectionSpanV1 *spans,
    size_t span_count,
    uint64_t realized_update_selected_count,
    uint32_t dirty_set_complete,
    uint32_t exact_projection_equal,
    uint32_t canonical_authority_requested
) {
    uint64_t counted = 0U;
    size_t i;

    if (plan == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    if (plan->struct_size != (uint32_t)sizeof(*plan) ||
        plan->version != hhs_exact_pass219b_sparse_dirty_projection_pack_version()) {
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    }
    if (span_count != (size_t)plan->span_count) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    if (span_count != 0U && spans == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    if (canonical_authority_requested != 0U ||
        plan->canonical_mutation_authority != 0U ||
        plan->canonical_persistence_authority != 0U ||
        plan->canonical_hash72_authority != 0U ||
        plan->projection_only != 1U ||
        plan->precomputed_cell_ranges_required != 1U ||
        plan->dirty_cells_sorted_unique_required != 1U ||
        plan->dirty_set_completeness_required != 1U ||
        plan->contiguous_selected_spans_coalesced != 1U ||
        plan->measured_hot_path_division_forbidden != 1U ||
        plan->measured_hot_path_modulo_forbidden != 1U) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    for (i = 0U; i < span_count; ++i) {
        if (spans[i].end_selected <= spans[i].first_selected ||
            spans[i].end_selected > plan->selected_count) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        if (i != 0U && spans[i - 1U].end_selected >= spans[i].first_selected) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        counted += spans[i].end_selected - spans[i].first_selected;
    }
    if (counted != plan->update_selected_count ||
        realized_update_selected_count != plan->update_selected_count ||
        plan->avoided_selected_count != plan->selected_count - plan->update_selected_count ||
        dirty_set_complete != 1U ||
        exact_projection_equal != 1U) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

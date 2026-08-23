#include "hhs_pass219b_selective_projection_1_0.h"

#include <limits.h>
#include <string.h>

static uint32_t hhs_exact_pass219b_selective_projection_pack_version(void) {
    return (HHS_EXACT_PASS219B_SELECTIVE_PROJECTION_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219B_SELECTIVE_PROJECTION_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219B_SELECTIVE_PROJECTION_VERSION_PATCH;
}

static HHSExactStatus hhs_exact_pass219b_selective_projection_validate_ratio(
    uint32_t numerator_p,
    uint32_t denominator_q
) {
    if (numerator_p == 0U || denominator_q == 0U || numerator_p > denominator_q) {
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    return HHS_EXACT_STATUS_OK;
}

HHS_EXACT_API uint32_t hhs_exact_pass219b_selective_projection_version(void) {
    return hhs_exact_pass219b_selective_projection_pack_version();
}

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_selective_projection_selected_count(
    uint64_t source_count,
    uint32_t numerator_p,
    uint32_t denominator_q,
    uint64_t *out_selected_count
) {
    uint64_t blocks;
    uint64_t remainder;
    uint64_t selected;
    HHSExactStatus status;

    if (out_selected_count == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    *out_selected_count = 0U;
    status = hhs_exact_pass219b_selective_projection_validate_ratio(
        numerator_p, denominator_q);
    if (status != HHS_EXACT_STATUS_OK) {
        return status;
    }

    blocks = source_count / (uint64_t)denominator_q;
    remainder = source_count % (uint64_t)denominator_q;
    selected = blocks * (uint64_t)numerator_p;
    selected += remainder < (uint64_t)numerator_p
        ? remainder
        : (uint64_t)numerator_p;
    *out_selected_count = selected;
    return HHS_EXACT_STATUS_OK;
}

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_selective_projection_plan(
    uint64_t source_count,
    uint32_t numerator_p,
    uint32_t denominator_q,
    HHSExactPass219BSelectiveProjectionPlanV1 *out_plan
) {
    uint64_t selected = 0U;
    HHSExactStatus status;

    if (out_plan == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    memset(out_plan, 0, sizeof(*out_plan));
    status = hhs_exact_pass219b_selective_projection_selected_count(
        source_count, numerator_p, denominator_q, &selected);
    if (status != HHS_EXACT_STATUS_OK) {
        return status;
    }

    out_plan->struct_size = (uint32_t)sizeof(*out_plan);
    out_plan->version = hhs_exact_pass219b_selective_projection_pack_version();
    out_plan->numerator_p = numerator_p;
    out_plan->denominator_q = denominator_q;
    out_plan->source_count = source_count;
    out_plan->selected_count = selected;
    out_plan->avoided_count = source_count - selected;
    out_plan->precomputed_id_buffer_required = 1U;
    out_plan->precomputed_cell_ranges_required = 1U;
    out_plan->measured_hot_path_division_forbidden = 1U;
    out_plan->measured_hot_path_modulo_forbidden = 1U;
    out_plan->canonical_mutation_authority = 0U;
    out_plan->canonical_persistence_authority = 0U;
    out_plan->canonical_hash72_authority = 0U;
    out_plan->projection_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_selective_projection_build_ids_u32(
    uint64_t source_count,
    uint32_t numerator_p,
    uint32_t denominator_q,
    uint32_t *out_ids,
    size_t capacity,
    size_t *out_count
) {
    uint64_t selected64 = 0U;
    uint64_t base;
    size_t required;
    size_t cursor = 0U;
    uint32_t remainder;
    HHSExactStatus status;

    if (out_count == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    *out_count = 0U;
    status = hhs_exact_pass219b_selective_projection_selected_count(
        source_count, numerator_p, denominator_q, &selected64);
    if (status != HHS_EXACT_STATUS_OK) {
        return status;
    }
    if (source_count > (uint64_t)UINT32_MAX) {
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    if (selected64 > (uint64_t)SIZE_MAX) {
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    required = (size_t)selected64;
    if (required != 0U && out_ids == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    if (capacity < required) {
        *out_count = required;
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    }

    for (base = 0U; base < source_count; base += (uint64_t)denominator_q) {
        for (remainder = 0U; remainder < numerator_p; ++remainder) {
            uint64_t id = base + (uint64_t)remainder;
            if (id >= source_count) {
                break;
            }
            out_ids[cursor++] = (uint32_t)id;
        }
    }
    if (cursor != required) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    *out_count = cursor;
    return HHS_EXACT_STATUS_OK;
}

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_selective_projection_validate_ids_u32(
    uint64_t source_count,
    uint32_t numerator_p,
    uint32_t denominator_q,
    const uint32_t *selected_ids,
    size_t selected_count
) {
    uint64_t selected64 = 0U;
    uint64_t base;
    size_t cursor = 0U;
    uint32_t remainder;
    HHSExactStatus status;

    status = hhs_exact_pass219b_selective_projection_selected_count(
        source_count, numerator_p, denominator_q, &selected64);
    if (status != HHS_EXACT_STATUS_OK) {
        return status;
    }
    if (source_count > (uint64_t)UINT32_MAX || selected64 > (uint64_t)SIZE_MAX) {
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    if (selected_count != (size_t)selected64) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    if (selected_count != 0U && selected_ids == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }

    for (base = 0U; base < source_count; base += (uint64_t)denominator_q) {
        for (remainder = 0U; remainder < numerator_p; ++remainder) {
            uint64_t expected = base + (uint64_t)remainder;
            if (expected >= source_count) {
                break;
            }
            if (cursor >= selected_count || selected_ids[cursor] != (uint32_t)expected) {
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            }
            ++cursor;
        }
    }
    return cursor == selected_count
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_selective_projection_build_equal_cell_ranges(
    const uint32_t *selected_ids,
    size_t selected_count,
    uint64_t source_count,
    uint32_t cell_count,
    HHSExactPass219BProjectionCellRangeV1 *out_ranges,
    size_t range_capacity
) {
    uint64_t cell_span;
    size_t cursor = 0U;
    size_t i;
    uint32_t cell;

    if ((selected_count != 0U && selected_ids == NULL) || out_ranges == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    if (cell_count == 0U || cell_count > HHS_EXACT_PASS219B_SELECTIVE_PROJECTION_MAX_CELL_RANGES) {
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    if (range_capacity < (size_t)cell_count) {
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    }
    if (source_count == 0U || source_count % (uint64_t)cell_count != 0U) {
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    for (i = 0U; i < selected_count; ++i) {
        if ((uint64_t)selected_ids[i] >= source_count ||
            (i != 0U && selected_ids[i] <= selected_ids[i - 1U])) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }
    cell_span = source_count / (uint64_t)cell_count;

    for (cell = 0U; cell < cell_count; ++cell) {
        uint64_t lo = (uint64_t)cell * cell_span;
        uint64_t hi = lo + cell_span;
        size_t first;
        while (cursor < selected_count && (uint64_t)selected_ids[cursor] < lo) {
            ++cursor;
        }
        first = cursor;
        while (cursor < selected_count && (uint64_t)selected_ids[cursor] < hi) {
            ++cursor;
        }
        out_ranges[cell].first_selected = (uint64_t)first;
        out_ranges[cell].end_selected = (uint64_t)cursor;
    }
    if (cursor != selected_count) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_selective_projection_verify(
    const HHSExactPass219BSelectiveProjectionPlanV1 *plan,
    uint64_t realized_selected_count,
    uint32_t ids_strictly_increasing,
    uint32_t original_identity_preserved,
    uint32_t exact_state_digest_equal,
    uint32_t canonical_authority_requested
) {
    if (plan == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    if (plan->struct_size != (uint32_t)sizeof(*plan) ||
        plan->version != hhs_exact_pass219b_selective_projection_pack_version()) {
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    }
    if (canonical_authority_requested != 0U ||
        plan->canonical_mutation_authority != 0U ||
        plan->canonical_persistence_authority != 0U ||
        plan->canonical_hash72_authority != 0U ||
        plan->projection_only != 1U) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    if (realized_selected_count != plan->selected_count ||
        ids_strictly_increasing != 1U ||
        original_identity_preserved != 1U ||
        exact_state_digest_equal != 1U) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

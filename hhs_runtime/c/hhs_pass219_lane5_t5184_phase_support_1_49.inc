#include "../include/hhs_pass219_lane5_t5184_phase_support_1_49.h"

#include <limits.h>
#include <string.h>

static const uint8_t HHS_P219_LANE5_T5184_SUPPORT_LOCAL64_149[
    HHS_EXACT_PASS219_LANE5_T5184_SUPPORT_PER_CELL
] = {
    UINT8_C(4), UINT8_C(5), UINT8_C(6), UINT8_C(7),
    UINT8_C(16), UINT8_C(17), UINT8_C(18), UINT8_C(19),
    UINT8_C(44), UINT8_C(45), UINT8_C(46), UINT8_C(47),
    UINT8_C(56), UINT8_C(57), UINT8_C(58), UINT8_C(59)
};

static uint32_t hhs_p219_lane5_t5184_support_ordinal(uint32_t local64) {
    uint32_t ordinal;
    for (ordinal = 0U; ordinal < HHS_EXACT_PASS219_LANE5_T5184_SUPPORT_PER_CELL; ++ordinal) {
        if ((uint32_t)HHS_P219_LANE5_T5184_SUPPORT_LOCAL64_149[ordinal] == local64)
            return ordinal;
    }
    return UINT32_MAX;
}

uint32_t hhs_exact_pass219_lane5_t5184_phase_support_version(void) {
    return HHS_EXACT_PASS219_LANE5_T5184_PHASE_SUPPORT_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_t5184_phase_support_authority(
    HHSExactPass219Lane5T5184PhaseSupportAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5T5184PhaseSupportAuthorityV1 authority;

    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(&authority, 0, sizeof(authority));
    authority.struct_size = (uint32_t)sizeof(authority);
    authority.version = HHS_EXACT_PASS219_LANE5_T5184_PHASE_SUPPORT_VERSION;
    authority.namespace_id = HHS_EXACT_PASS219_LANE5_T5184_PHASE_SUPPORT_NAMESPACE;
    authority.operation64 = HHS_EXACT_PASS219_LANE5_T5184_OPERATION64;
    authority.vm81_cells = HHS_EXACT_PASS219_LANE5_T5184_VM81_CELLS;
    authority.total_positions = HHS_EXACT_PASS219_LANE5_T5184_TOTAL_POSITIONS;
    authority.support_per_cell = HHS_EXACT_PASS219_LANE5_T5184_SUPPORT_PER_CELL;
    authority.bypass_per_cell = HHS_EXACT_PASS219_LANE5_T5184_BYPASS_PER_CELL;
    authority.support_vm81 = HHS_EXACT_PASS219_LANE5_T5184_SUPPORT_VM81;
    authority.bypass_vm81 = HHS_EXACT_PASS219_LANE5_T5184_BYPASS_VM81;
    authority.pair_count_vm81 = HHS_EXACT_PASS219_LANE5_T5184_PAIR_COUNT_VM81;
    authority.phase_support_mask64 = HHS_EXACT_PASS219_LANE5_T5184_PHASE_SUPPORT_MASK;
    authority.one_quarter_phase_support = 1U;
    authority.three_quarter_phase_bypass = 1U;
    authority.support_equals_36_squared = 1U;
    authority.support_equals_18_times_72 = 1U;
    authority.pair_count_equals_18_squared = 1U;
    authority.ordered_products_preserved = 1U;
    authority.wire_mirror_xy_equals_zw = 1U;
    authority.wire_mirror_yx_equals_wz = 1U;
    authority.q_minus_one_sign_preserved = 1U;
    authority.support_table_direct_iteration = 1U;
    authority.full_state_identity_still_required = 1U;
    authority.serialized_operand_binding_still_required = 1U;
    authority.candidate_only = 1U;
    authority.requires_exact_cpu_vm81_replay = 1U;
    authority.canonical_vm81_mutation_authority = 0U;
    authority.canonical_hash72_authority = 0U;
    authority.canonical_hash216_authority = 0U;
    authority.canonical_persistence_authority = 0U;
    authority.floating_point_canonical_authority = 0U;

    *out_authority = authority;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_t5184_phase_support_local64(
    uint32_t support_ordinal,
    uint32_t *out_local64
) {
    if (out_local64 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (support_ordinal >= HHS_EXACT_PASS219_LANE5_T5184_SUPPORT_PER_CELL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    *out_local64 = (uint32_t)HHS_P219_LANE5_T5184_SUPPORT_LOCAL64_149[support_ordinal];
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_t5184_phase_support_classify(
    uint32_t vm81_cell,
    uint32_t local64,
    HHSExactPass219Lane5T5184PhaseSlotV1 *out_slot
) {
    HHSExactPass219Lane5T5184PhaseSlotV1 slot;
    uint32_t ordinal;

    if (out_slot == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (vm81_cell >= HHS_EXACT_PASS219_LANE5_T5184_VM81_CELLS ||
        local64 >= HHS_EXACT_PASS219_LANE5_T5184_OPERATION64)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(&slot, 0, sizeof(slot));
    slot.struct_size = (uint32_t)sizeof(slot);
    slot.version = HHS_EXACT_PASS219_LANE5_T5184_PHASE_SUPPORT_VERSION;
    slot.vm81_cell = vm81_cell;
    slot.local64 = local64;
    slot.global5184 = vm81_cell * HHS_EXACT_PASS219_LANE5_T5184_OPERATION64 + local64;
    slot.support_ordinal = UINT32_MAX;
    slot.full_state_identity_required = 1U;
    slot.candidate_only = 1U;

    ordinal = hhs_p219_lane5_t5184_support_ordinal(local64);
    if (ordinal != UINT32_MAX) {
        slot.support_ordinal = ordinal;
        slot.phase_bearing = 1U;
        slot.requires_phase_specific_check = 1U;

        if (local64 >= 4U && local64 <= 7U) {
            slot.phase_code = HHS_EXACT_PASS219_LANE5_T5184_PHASE_XY;
            slot.phase_sign = 1;
            slot.representative_phase_code = HHS_EXACT_PASS219_LANE5_T5184_PHASE_XY;
        } else if (local64 >= 16U && local64 <= 19U) {
            slot.phase_code = HHS_EXACT_PASS219_LANE5_T5184_PHASE_YX;
            slot.phase_sign = -1;
            slot.representative_phase_code = HHS_EXACT_PASS219_LANE5_T5184_PHASE_YX;
        } else if (local64 >= 44U && local64 <= 47U) {
            slot.phase_code = HHS_EXACT_PASS219_LANE5_T5184_PHASE_ZW;
            slot.phase_sign = 1;
            slot.representative_phase_code = HHS_EXACT_PASS219_LANE5_T5184_PHASE_XY;
        } else {
            slot.phase_code = HHS_EXACT_PASS219_LANE5_T5184_PHASE_WZ;
            slot.phase_sign = -1;
            slot.representative_phase_code = HHS_EXACT_PASS219_LANE5_T5184_PHASE_YX;
        }
    }

    *out_slot = slot;
    return HHS_EXACT_STATUS_OK;
}

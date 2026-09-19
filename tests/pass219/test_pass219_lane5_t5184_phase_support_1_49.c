#include "hhs_runtime_exact_abi.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

int main(void) {
    HHSExactPass219Lane5T5184PhaseSupportAuthorityV1 authority;
    HHSExactPass219Lane5T5184PhaseSlotV1 slot;
    uint32_t support_table[HHS_EXACT_PASS219_LANE5_T5184_SUPPORT_PER_CELL];
    uint32_t pair_counts[5] = {0U, 0U, 0U, 0U, 0U};
    uint32_t support_count = 0U;
    uint32_t bypass_count = 0U;
    uint32_t cell;
    uint32_t local64;
    uint32_t ordinal;
    uint64_t rebuilt_mask = UINT64_C(0);

    CHECK(hhs_exact_pass219_lane5_t5184_phase_support_version() ==
          HHS_EXACT_PASS219_LANE5_T5184_PHASE_SUPPORT_VERSION);
    CHECK(hhs_exact_pass219_lane5_t5184_phase_support_authority(&authority) ==
          HHS_EXACT_STATUS_OK);
    CHECK(authority.struct_size == sizeof(authority));
    CHECK(authority.operation64 == 64U);
    CHECK(authority.vm81_cells == 81U);
    CHECK(authority.total_positions == 5184U);
    CHECK(authority.support_per_cell == 16U);
    CHECK(authority.bypass_per_cell == 48U);
    CHECK(authority.support_vm81 == 1296U);
    CHECK(authority.bypass_vm81 == 3888U);
    CHECK(authority.pair_count_vm81 == 324U);
    CHECK(authority.phase_support_mask64 == UINT64_C(0x0f00f000000f00f0));
    CHECK(authority.one_quarter_phase_support == 1U);
    CHECK(authority.three_quarter_phase_bypass == 1U);
    CHECK(authority.support_equals_36_squared == 1U);
    CHECK(authority.support_equals_18_times_72 == 1U);
    CHECK(authority.pair_count_equals_18_squared == 1U);
    CHECK(authority.ordered_products_preserved == 1U);
    CHECK(authority.wire_mirror_xy_equals_zw == 1U);
    CHECK(authority.wire_mirror_yx_equals_wz == 1U);
    CHECK(authority.q_minus_one_sign_preserved == 1U);
    CHECK(authority.support_table_direct_iteration == 1U);
    CHECK(authority.full_state_identity_still_required == 1U);
    CHECK(authority.serialized_operand_binding_still_required == 1U);
    CHECK(authority.candidate_only == 1U);
    CHECK(authority.requires_exact_cpu_vm81_replay == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.canonical_persistence_authority == 0U);
    CHECK(authority.floating_point_canonical_authority == 0U);

    for (ordinal = 0U; ordinal < HHS_EXACT_PASS219_LANE5_T5184_SUPPORT_PER_CELL; ++ordinal) {
        CHECK(hhs_exact_pass219_lane5_t5184_phase_support_local64(
            ordinal, &support_table[ordinal]
        ) == HHS_EXACT_STATUS_OK);
        if (ordinal > 0U)
            CHECK(support_table[ordinal - 1U] < support_table[ordinal]);
        rebuilt_mask |= UINT64_C(1) << support_table[ordinal];
        CHECK(hhs_exact_pass219_lane5_t5184_phase_support_classify(
            0U, support_table[ordinal], &slot
        ) == HHS_EXACT_STATUS_OK);
        CHECK(slot.phase_bearing == 1U);
        CHECK(slot.requires_phase_specific_check == 1U);
        CHECK(slot.support_ordinal == ordinal);
    }
    CHECK(rebuilt_mask == HHS_EXACT_PASS219_LANE5_T5184_PHASE_SUPPORT_MASK);

    for (cell = 0U; cell < HHS_EXACT_PASS219_LANE5_T5184_VM81_CELLS; ++cell) {
        for (local64 = 0U; local64 < HHS_EXACT_PASS219_LANE5_T5184_OPERATION64; ++local64) {
            CHECK(hhs_exact_pass219_lane5_t5184_phase_support_classify(
                cell, local64, &slot
            ) == HHS_EXACT_STATUS_OK);
            CHECK(slot.global5184 == cell * 64U + local64);
            CHECK(slot.global5184 < 5184U);
            CHECK(slot.full_state_identity_required == 1U);
            CHECK(slot.candidate_only == 1U);

            if (slot.phase_bearing == 1U) {
                ++support_count;
                CHECK(slot.phase_code >= HHS_EXACT_PASS219_LANE5_T5184_PHASE_XY);
                CHECK(slot.phase_code <= HHS_EXACT_PASS219_LANE5_T5184_PHASE_WZ);
                ++pair_counts[slot.phase_code];
                CHECK(slot.phase_sign == 1 || slot.phase_sign == -1);
                if (slot.phase_code == HHS_EXACT_PASS219_LANE5_T5184_PHASE_ZW)
                    CHECK(slot.representative_phase_code ==
                          HHS_EXACT_PASS219_LANE5_T5184_PHASE_XY);
                if (slot.phase_code == HHS_EXACT_PASS219_LANE5_T5184_PHASE_WZ)
                    CHECK(slot.representative_phase_code ==
                          HHS_EXACT_PASS219_LANE5_T5184_PHASE_YX);
            } else {
                ++bypass_count;
                CHECK(slot.requires_phase_specific_check == 0U);
                CHECK(slot.phase_code == HHS_EXACT_PASS219_LANE5_T5184_PHASE_NONE);
            }
        }
    }

    CHECK(support_count == 1296U);
    CHECK(bypass_count == 3888U);
    CHECK(support_count + bypass_count == 5184U);
    CHECK(pair_counts[HHS_EXACT_PASS219_LANE5_T5184_PHASE_XY] == 324U);
    CHECK(pair_counts[HHS_EXACT_PASS219_LANE5_T5184_PHASE_YX] == 324U);
    CHECK(pair_counts[HHS_EXACT_PASS219_LANE5_T5184_PHASE_ZW] == 324U);
    CHECK(pair_counts[HHS_EXACT_PASS219_LANE5_T5184_PHASE_WZ] == 324U);
    CHECK(pair_counts[HHS_EXACT_PASS219_LANE5_T5184_PHASE_XY] +
          pair_counts[HHS_EXACT_PASS219_LANE5_T5184_PHASE_ZW] == 648U);
    CHECK(pair_counts[HHS_EXACT_PASS219_LANE5_T5184_PHASE_YX] +
          pair_counts[HHS_EXACT_PASS219_LANE5_T5184_PHASE_WZ] == 648U);

    CHECK(hhs_exact_pass219_lane5_t5184_phase_support_classify(
        81U, 0U, &slot
    ) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(hhs_exact_pass219_lane5_t5184_phase_support_classify(
        0U, 64U, &slot
    ) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(hhs_exact_pass219_lane5_t5184_phase_support_local64(
        16U, &local64
    ) == HHS_EXACT_STATUS_INVALID_ARGUMENT);

    printf(
        "{\"result\":\"PASS\",\"full_state_positions\":5184,"
        "\"phase_specific_checks\":%u,\"phase_specific_slots_skipped\":%u,"
        "\"support_fraction\":\"1/4\",\"bypass_fraction\":\"3/4\","
        "\"support_mask_hex\":\"0f00f000000f00f0\","
        "\"pair_count_each\":324,\"candidate_only\":true,"
        "\"full_state_identity_still_required\":true}\n",
        support_count,
        bypass_count
    );
    puts("PASS219_LANE5_T5184_PHASE_SUPPORT_1_49_PASS");
    return 0;
}

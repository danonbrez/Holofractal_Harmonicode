#include "hhs_pass219_lane5_pythagorean_phase_geometry_1_49.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { if (!(expr)) { fprintf(stderr, "CHECK failed: %s at %s:%d\n", #expr, __FILE__, __LINE__); return 1; } } while (0)

static HHSExactPass219Lane5PythagoreanPhaseInputV1 make_input(
    uint32_t pair_kind,
    uint32_t orientation,
    uint32_t phase_slot,
    uint32_t lo_shu_cell_index,
    uint32_t fibonacci_depth,
    uint64_t projected_p4
) {
    HHSExactPass219Lane5PythagoreanPhaseInputV1 input;
    memset(&input, 0, sizeof(input));
    input.struct_size = (uint32_t)sizeof(input);
    input.version = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PHASE_GEOMETRY_VERSION;
    input.pair_kind = pair_kind;
    input.orientation = orientation;
    input.phase_slot = phase_slot;
    input.lo_shu_cell_index = lo_shu_cell_index;
    input.fibonacci_depth = fibonacci_depth;
    input.projected_p4 = projected_p4;
    return input;
}

int main(void) {
    static const uint32_t phases[4] = {0U, 18U, 36U, 54U};
    static const uint32_t inverse_phases[4] = {36U, 54U, 0U, 18U};
    static const uint32_t lo_shu[9] = {4U, 9U, 2U, 3U, 5U, 7U, 8U, 1U, 6U};
    HHSExactPass219Lane5PythagoreanPhaseAuthorityV1 authority;
    HHSExactPass219Lane5PythagoreanPhaseReceiptV1 receipt;
    HHSExactPass219Lane5PythagoreanPhaseInputV1 input;
    uint32_t pair_kind;
    uint32_t orientation;
    uint32_t phase_index;
    uint32_t cell;
    uint32_t admitted = 0U;

    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_pythagorean_phase_geometry_version() ==
          HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PHASE_GEOMETRY_VERSION);
    CHECK(hhs_exact_pass219_lane5_pythagorean_phase_geometry_authority(&authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.a2 == 1U);
    CHECK(authority.b2 == 2U);
    CHECK(authority.c2 == 3U);
    CHECK(authority.c4 == 9U);
    CHECK(authority.lo_shu_line_sum == 15U);
    CHECK(authority.lo_shu_center == 5U);
    CHECK(authority.phase_cycle == 72U);
    CHECK(authority.phase_quarter == 18U);
    CHECK(authority.phase_half == 36U);
    CHECK(authority.pair_kind_count == 4U);
    CHECK(authority.pass192_fibonacci_max_depth == HHS_EXACT_PASS192_FIB_MAX_DEPTH);
    CHECK(authority.pythagorean_constant_projection_exact == 1U);
    CHECK(authority.reciprocal_phase_involution_exact == 1U);
    CHECK(authority.directional_pair_involution_exact == 1U);
    CHECK(authority.shared_fourth_power_is_typed_projection == 1U);
    CHECK(authority.pass192_fibonacci_schedule_reused == 1U);
    CHECK(authority.candidate_only == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.canonical_persistence_authority == 0U);
    CHECK(authority.floating_point_canonical_authority == 0U);

    for (pair_kind = 0U; pair_kind < 4U; ++pair_kind) {
        for (orientation = 0U; orientation < 2U; ++orientation) {
            for (phase_index = 0U; phase_index < 4U; ++phase_index) {
                for (cell = 0U; cell < 9U; ++cell) {
                    input = make_input(pair_kind, orientation, phases[phase_index], cell, 10U, UINT64_C(9));
                    memset(&receipt, 0, sizeof(receipt));
                    CHECK(hhs_exact_pass219_lane5_pythagorean_phase_project(&input, &receipt) == HHS_EXACT_STATUS_OK);
                    CHECK(receipt.pair_kind == pair_kind);
                    CHECK(receipt.orientation == orientation);
                    CHECK(receipt.inverse_orientation == (orientation ^ 1U));
                    CHECK(receipt.phase_slot == phases[phase_index]);
                    CHECK(receipt.inverse_phase_slot == inverse_phases[phase_index]);
                    CHECK(receipt.lo_shu_denominator == lo_shu[cell]);
                    CHECK(receipt.a2 + receipt.b2 == receipt.c2);
                    CHECK(receipt.c2 * receipt.c2 == receipt.c4);
                    CHECK(receipt.c4 == 9U);
                    CHECK(receipt.projected_p4 == UINT64_C(9));
                    CHECK(receipt.pythagorean_identity_verified == 1U);
                    CHECK(receipt.phase_involution_verified == 1U);
                    CHECK(receipt.pair_involution_verified == 1U);
                    CHECK(receipt.lo_shu_cell_verified == 1U);
                    CHECK(receipt.fibonacci_depth_within_pass192 == 1U);
                    CHECK(receipt.shared_fourth_power_match == 1U);
                    CHECK(receipt.collapse_candidate_admissible == 1U);
                    CHECK(receipt.candidate_only == 1U);
                    CHECK(receipt.canonical_mutation_authority == 0U);
                    CHECK(receipt.canonical_hash72_authority == 0U);
                    CHECK(receipt.canonical_hash216_authority == 0U);
                    CHECK(receipt.canonical_persistence_authority == 0U);
                    ++admitted;
                }
            }
        }
    }

    CHECK(admitted == 288U);

    input = make_input(HHS_EXACT_PASS219_LANE5_PAIR_PQ, 0U, 0U, 4U, 10U, UINT64_C(1));
    CHECK(hhs_exact_pass219_lane5_pythagorean_phase_project(&input, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.shared_fourth_power_match == 0U);
    CHECK(receipt.collapse_candidate_admissible == 0U);

    input = make_input(HHS_EXACT_PASS219_LANE5_PAIR_PQ, 0U, 1U, 4U, 10U, UINT64_C(9));
    CHECK(hhs_exact_pass219_lane5_pythagorean_phase_project(&input, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    input = make_input(4U, 0U, 0U, 4U, 10U, UINT64_C(9));
    CHECK(hhs_exact_pass219_lane5_pythagorean_phase_project(&input, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    input = make_input(HHS_EXACT_PASS219_LANE5_PAIR_AB, 2U, 0U, 4U, 10U, UINT64_C(9));
    CHECK(hhs_exact_pass219_lane5_pythagorean_phase_project(&input, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    input = make_input(HHS_EXACT_PASS219_LANE5_PAIR_AB, 0U, 0U, 9U, 10U, UINT64_C(9));
    CHECK(hhs_exact_pass219_lane5_pythagorean_phase_project(&input, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    input = make_input(HHS_EXACT_PASS219_LANE5_PAIR_AB, 0U, 0U, 4U, 0U, UINT64_C(9));
    CHECK(hhs_exact_pass219_lane5_pythagorean_phase_project(&input, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    input = make_input(HHS_EXACT_PASS219_LANE5_PAIR_AB, 0U, 0U, 4U, HHS_EXACT_PASS192_FIB_MAX_DEPTH + 1U, UINT64_C(9));
    CHECK(hhs_exact_pass219_lane5_pythagorean_phase_project(&input, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    printf("PASS219_LANE5_PYTHAGOREAN_PHASE_GEOMETRY_1_49_PASS projections=%u c4=%u phase_cycle=%u\n",
           admitted,
           HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_C4,
           HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PHASE_CYCLE);
    return 0;
}

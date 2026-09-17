#include "hhs_pass219_lane5_pythagorean_phase_geometry_1_49.h"

#include <string.h>

static const uint8_t hhs_lane5_p149_lo_shu_denominators[9] = {
    4U, 9U, 2U,
    3U, 5U, 7U,
    8U, 1U, 6U
};

static int hhs_lane5_p149_valid_phase(uint32_t phase_slot) {
    return phase_slot == UINT32_C(0) ||
           phase_slot == UINT32_C(18) ||
           phase_slot == UINT32_C(36) ||
           phase_slot == UINT32_C(54);
}

static uint32_t hhs_lane5_p149_inverse_phase(uint32_t phase_slot) {
    return (phase_slot + HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PHASE_HALF) %
           HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PHASE_CYCLE;
}

static uint64_t hhs_lane5_p149_mix64(uint64_t x) {
    x ^= x >> 30;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31;
    return x;
}

static uint64_t hhs_lane5_p149_signature(
    const HHSExactPass219Lane5PythagoreanPhaseInputV1 *input,
    uint32_t inverse_orientation,
    uint32_t inverse_phase_slot,
    uint32_t lo_shu_denominator
) {
    uint64_t state = UINT64_C(0x4c35503134395047);
    state = hhs_lane5_p149_mix64(state ^ (uint64_t)input->pair_kind);
    state = hhs_lane5_p149_mix64(state ^ ((uint64_t)input->orientation << 8));
    state = hhs_lane5_p149_mix64(state ^ ((uint64_t)inverse_orientation << 16));
    state = hhs_lane5_p149_mix64(state ^ ((uint64_t)input->phase_slot << 24));
    state = hhs_lane5_p149_mix64(state ^ ((uint64_t)inverse_phase_slot << 32));
    state = hhs_lane5_p149_mix64(state ^ ((uint64_t)input->lo_shu_cell_index << 40));
    state = hhs_lane5_p149_mix64(state ^ ((uint64_t)lo_shu_denominator << 48));
    state = hhs_lane5_p149_mix64(state ^ (uint64_t)input->fibonacci_depth);
    state = hhs_lane5_p149_mix64(state ^ input->projected_p4);
    return state;
}

uint32_t hhs_exact_pass219_lane5_pythagorean_phase_geometry_version(void) {
    return HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PHASE_GEOMETRY_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_pythagorean_phase_geometry_authority(
    HHSExactPass219Lane5PythagoreanPhaseAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5PythagoreanPhaseAuthorityV1 value;

    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PHASE_GEOMETRY_VERSION;
    value.namespace_id = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PHASE_GEOMETRY_NAMESPACE;
    value.a2 = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_A2;
    value.b2 = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_B2;
    value.c2 = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_C2;
    value.c4 = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_C4;
    value.phase_cycle = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PHASE_CYCLE;
    value.phase_quarter = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PHASE_QUARTER;
    value.phase_half = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PHASE_HALF;
    value.lo_shu_line_sum = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_LO_SHU_LINE_SUM;
    value.lo_shu_center = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_LO_SHU_CENTER;
    value.pair_kind_count = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PAIR_KIND_COUNT;
    value.pass192_fibonacci_max_depth = HHS_EXACT_PASS192_FIB_MAX_DEPTH;
    value.pythagorean_constant_projection_exact = 1U;
    value.lo_shu_denominator_geometry_exact = 1U;
    value.reciprocal_phase_involution_exact = 1U;
    value.directional_pair_involution_exact = 1U;
    value.shared_fourth_power_is_typed_projection = 1U;
    value.pass192_fibonacci_schedule_reused = 1U;
    value.candidate_only = 1U;
    value.canonical_vm81_mutation_authority = 0U;
    value.canonical_hash72_authority = 0U;
    value.canonical_hash216_authority = 0U;
    value.canonical_persistence_authority = 0U;
    value.floating_point_canonical_authority = 0U;

    *out_authority = value;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_pythagorean_phase_project(
    const HHSExactPass219Lane5PythagoreanPhaseInputV1 *input,
    HHSExactPass219Lane5PythagoreanPhaseReceiptV1 *out_receipt
) {
    HHSExactPass219Lane5PythagoreanPhaseReceiptV1 receipt;
    uint32_t inverse_orientation;
    uint32_t inverse_phase_slot;
    uint32_t lo_shu_denominator;

    if (input == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (input->struct_size != sizeof(*input) ||
        input->version != HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PHASE_GEOMETRY_VERSION)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (input->pair_kind >= HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PAIR_KIND_COUNT ||
        input->orientation > UINT32_C(1) ||
        !hhs_lane5_p149_valid_phase(input->phase_slot) ||
        input->lo_shu_cell_index >= HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_LO_SHU_CELLS ||
        input->fibonacci_depth == UINT32_C(0) ||
        input->fibonacci_depth > HHS_EXACT_PASS192_FIB_MAX_DEPTH)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    inverse_orientation = input->orientation ^ UINT32_C(1);
    inverse_phase_slot = hhs_lane5_p149_inverse_phase(input->phase_slot);
    lo_shu_denominator = (uint32_t)hhs_lane5_p149_lo_shu_denominators[input->lo_shu_cell_index];

    memset(&receipt, 0, sizeof(receipt));
    receipt.struct_size = (uint32_t)sizeof(receipt);
    receipt.version = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PHASE_GEOMETRY_VERSION;
    receipt.namespace_id = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_PHASE_GEOMETRY_NAMESPACE;
    receipt.pair_kind = input->pair_kind;
    receipt.orientation = input->orientation;
    receipt.inverse_orientation = inverse_orientation;
    receipt.phase_slot = input->phase_slot;
    receipt.inverse_phase_slot = inverse_phase_slot;
    receipt.lo_shu_cell_index = input->lo_shu_cell_index;
    receipt.lo_shu_denominator = lo_shu_denominator;
    receipt.fibonacci_depth = input->fibonacci_depth;
    receipt.pass192_fibonacci_version = hhs_exact_pass192_fibonacci_version();
    receipt.a2 = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_A2;
    receipt.b2 = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_B2;
    receipt.c2 = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_C2;
    receipt.c4 = HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_C4;
    receipt.projected_p4 = input->projected_p4;
    receipt.geometry_signature64 = hhs_lane5_p149_signature(
        input,
        inverse_orientation,
        inverse_phase_slot,
        lo_shu_denominator
    );
    receipt.pythagorean_identity_verified =
        (receipt.a2 + receipt.b2 == receipt.c2) &&
        (receipt.c2 * receipt.c2 == receipt.c4);
    receipt.phase_involution_verified =
        hhs_lane5_p149_inverse_phase(inverse_phase_slot) == input->phase_slot;
    receipt.pair_involution_verified =
        (inverse_orientation ^ UINT32_C(1)) == input->orientation;
    receipt.lo_shu_cell_verified = 1U;
    receipt.fibonacci_depth_within_pass192 = 1U;
    receipt.shared_fourth_power_match =
        input->projected_p4 == (uint64_t)HHS_EXACT_PASS219_LANE5_PYTHAGOREAN_C4;
    receipt.collapse_candidate_admissible =
        receipt.pythagorean_identity_verified &&
        receipt.phase_involution_verified &&
        receipt.pair_involution_verified &&
        receipt.lo_shu_cell_verified &&
        receipt.fibonacci_depth_within_pass192 &&
        receipt.shared_fourth_power_match;
    receipt.candidate_only = 1U;
    receipt.canonical_mutation_authority = 0U;
    receipt.canonical_hash72_authority = 0U;
    receipt.canonical_hash216_authority = 0U;
    receipt.canonical_persistence_authority = 0U;

    *out_receipt = receipt;
    return HHS_EXACT_STATUS_OK;
}

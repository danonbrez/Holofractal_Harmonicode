#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static HHSExactPass219HolographicWindowResiduesV1 residues(
    int64_t t_num,
    int64_t m_num,
    uint64_t q,
    uint8_t exact
) {
    HHSExactPass219HolographicWindowResiduesV1 r;
    memset(&r, 0, sizeof(r));
    r.struct_size = (uint32_t)sizeof(r);
    r.version = hhs_exact_pass219_holographic_harmonic_window_version();
    r.t3_minus_t_numerator = t_num;
    r.m2_minus_m_numerator = m_num;
    r.common_denominator = q;
    r.exact_residue_witness = exact;
    return r;
}

static HHSExactPass219HolographicBranchRequestV1 request_at(
    uint32_t layer,
    uint64_t phase_num,
    uint64_t phase_den,
    uint8_t inclusive
) {
    HHSExactPass219HolographicBranchRequestV1 req;
    memset(&req, 0, sizeof(req));
    req.struct_size = (uint32_t)sizeof(req);
    req.version = hhs_exact_pass219_holographic_harmonic_window_version();
    req.residues = residues(1, 1, 1U, 1U);
    req.layer = layer;
    req.root_window_numerator = 25U;
    req.root_window_denominator = 3U;
    req.phase_coordinate_numerator = phase_num;
    req.phase_coordinate_denominator = phase_den;
    req.include_upper_boundary = inclusive;
    return req;
}

int main(void) {
    HHSExactPass219HolographicWindowInvariantV1 invariant;
    HHSExactPass219HolographicWindowResiduesV1 r;
    HHSExactPass219HolographicBranchRequestV1 req;
    HHSExactPass219HolographicBranchResultV1 result;

    assert(hhs_exact_pass219_holographic_harmonic_window_validate() ==
           HHS_EXACT_STATUS_OK);

    r = residues(1, 1, 1U, 1U);
    assert(hhs_exact_pass219_holographic_harmonic_window_invariant(
        &r, &invariant) == HHS_EXACT_STATUS_OK);
    assert(invariant.combined_residue_numerator == 5);
    assert(invariant.common_denominator == 1U);
    assert(invariant.ratio_numerator == 25U);
    assert(invariant.ratio_denominator == 3U);
    assert(invariant.positive_root == 1U);
    assert(invariant.negative_root == 0U);
    assert(invariant.harmonic_window_closed == 1U);
    assert(invariant.canonical_authority == 0U);
    assert(invariant.floating_point_authority == 0U);

    /* Same exact residues with a shared rational denominator. */
    r = residues(7, 7, 7U, 1U);
    assert(hhs_exact_pass219_holographic_harmonic_window_invariant(
        &r, &invariant) == HHS_EXACT_STATUS_OK);
    assert(invariant.combined_residue_numerator == 35);
    assert(invariant.common_denominator == 7U);
    assert(invariant.harmonic_window_closed == 1U);

    /* Reciprocal signed root also closes after squaring. */
    r = residues(-1, -1, 1U, 1U);
    assert(hhs_exact_pass219_holographic_harmonic_window_invariant(
        &r, &invariant) == HHS_EXACT_STATUS_OK);
    assert(invariant.combined_residue_numerator == -5);
    assert(invariant.positive_root == 0U);
    assert(invariant.negative_root == 1U);
    assert(invariant.harmonic_window_closed == 1U);

    /* Non-closing exact residues are represented but may not drive branching. */
    r = residues(1, 0, 1U, 1U);
    assert(hhs_exact_pass219_holographic_harmonic_window_invariant(
        &r, &invariant) == HHS_EXACT_STATUS_OK);
    assert(invariant.combined_residue_numerator == 2);
    assert(invariant.harmonic_window_closed == 0U);

    req = request_at(0U, 8U, 1U, 1U);
    assert(hhs_exact_pass219_holographic_branch_evaluate(
        &req, &result) == HHS_EXACT_STATUS_OK);
    assert(result.active_window_numerator == 25U);
    assert(result.active_window_denominator == 3U);
    assert(result.inside_active_window == 1U);
    assert(result.decision == HHS_EXACT_PASS219_HOLOGRAPHIC_BRANCH_THEN);

    /* W1 = (25/3)*(3/25) = 1 exactly. */
    req = request_at(1U, 1U, 1U, 1U);
    assert(hhs_exact_pass219_holographic_branch_evaluate(
        &req, &result) == HHS_EXACT_STATUS_OK);
    assert(result.active_window_numerator == 75U);
    assert(result.active_window_denominator == 75U);
    assert(result.inside_active_window == 1U);
    assert(result.decision == HHS_EXACT_PASS219_HOLOGRAPHIC_BRANCH_THEN);

    req.include_upper_boundary = 0U;
    assert(hhs_exact_pass219_holographic_branch_evaluate(
        &req, &result) == HHS_EXACT_STATUS_OK);
    assert(result.inside_active_window == 0U);
    assert(result.decision == HHS_EXACT_PASS219_HOLOGRAPHIC_BRANCH_ELSE);

    /* W2 = 3/25. */
    req = request_at(2U, 3U, 25U, 1U);
    assert(hhs_exact_pass219_holographic_branch_evaluate(
        &req, &result) == HHS_EXACT_STATUS_OK);
    assert(result.active_window_numerator == 225U);
    assert(result.active_window_denominator == 1875U);
    assert(result.inside_active_window == 1U);

    req = request_at(2U, 4U, 25U, 1U);
    assert(hhs_exact_pass219_holographic_branch_evaluate(
        &req, &result) == HHS_EXACT_STATUS_OK);
    assert(result.inside_active_window == 0U);
    assert(result.decision == HHS_EXACT_PASS219_HOLOGRAPHIC_BRANCH_ELSE);

    /* Depth 9 is directly addressable without recursive stack traversal. */
    req = request_at(9U, 0U, 1U, 1U);
    assert(hhs_exact_pass219_holographic_branch_evaluate(
        &req, &result) == HHS_EXACT_STATUS_OK);
    assert(result.active_window_numerator ==
           UINT64_C(25) * UINT64_C(19683));
    assert(result.active_window_denominator ==
           UINT64_C(3) * UINT64_C(3814697265625));
    assert(result.direct_layer_addressed == 1U);
    assert(result.recursion_stack_allocated == 0U);
    assert(result.pointer_tree_traversal_required == 0U);
    assert(result.bounded_fixed_width_branch_work == 1U);
    assert(result.whole_path_depth_bounded == 1U);
    assert(result.unbounded_depth_constant_time_claim == 0U);
    assert(result.canonical_authority == 0U);
    assert(result.floating_point_authority == 0U);
    assert(result.complete_fallback_required_on_failure == 1U);

    req.layer = 10U;
    assert(hhs_exact_pass219_holographic_branch_evaluate(
        &req, &result) == HHS_EXACT_STATUS_RANGE_ERROR);

    req = request_at(1U, 1U, 1U, 1U);
    req.residues = residues(1, 0, 1U, 1U);
    assert(hhs_exact_pass219_holographic_branch_evaluate(
        &req, &result) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    req = request_at(1U, 1U, 1U, 1U);
    req.residues.canonical_authority_requested = 1U;
    assert(hhs_exact_pass219_holographic_branch_evaluate(
        &req, &result) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    puts("PASS219_HOLOGRAPHIC_HARMONIC_WINDOW_25_3_1_0_C_OK");
    return 0;
}

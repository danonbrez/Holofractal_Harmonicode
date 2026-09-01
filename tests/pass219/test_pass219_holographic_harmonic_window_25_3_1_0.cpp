#include "hhs_runtime_exact_abi.h"

#include <cassert>
#include <cstdint>

int main() {
    HHSExactPass219HolographicWindowResiduesV1 residues{};
    residues.struct_size = sizeof(residues);
    residues.version = hhs_exact_pass219_holographic_harmonic_window_version();
    residues.t3_minus_t_numerator = 1;
    residues.m2_minus_m_numerator = 1;
    residues.common_denominator = 1;
    residues.exact_residue_witness = 1;

    HHSExactPass219HolographicWindowInvariantV1 invariant{};
    assert(hhs_exact_pass219_holographic_harmonic_window_invariant(
        &residues, &invariant) == HHS_EXACT_STATUS_OK);
    assert(invariant.harmonic_window_closed == 1);
    assert(invariant.ratio_numerator == 25);
    assert(invariant.ratio_denominator == 3);

    HHSExactPass219HolographicBranchRequestV1 request{};
    request.struct_size = sizeof(request);
    request.version = hhs_exact_pass219_holographic_harmonic_window_version();
    request.residues = residues;
    request.layer = 1;
    request.root_window_numerator = 25;
    request.root_window_denominator = 3;
    request.phase_coordinate_numerator = 1;
    request.phase_coordinate_denominator = 1;
    request.include_upper_boundary = 1;

    HHSExactPass219HolographicBranchResultV1 result{};
    assert(hhs_exact_pass219_holographic_branch_evaluate(
        &request, &result) == HHS_EXACT_STATUS_OK);
    assert(result.decision == HHS_EXACT_PASS219_HOLOGRAPHIC_BRANCH_THEN);
    assert(result.active_window_numerator == 75);
    assert(result.active_window_denominator == 75);
    assert(result.direct_layer_addressed == 1);
    assert(result.recursion_stack_allocated == 0);
    assert(result.pointer_tree_traversal_required == 0);
    assert(result.unbounded_depth_constant_time_claim == 0);
    return 0;
}

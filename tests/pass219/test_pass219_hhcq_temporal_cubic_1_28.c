#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <limits.h>
#include <stdint.h>
#include <string.h>

static int root_present(const HHSExactPass219HHCQTemporalZ72RootsV1 *roots, uint32_t t) {
    if (t < 64U)
        return (roots->roots_0_63 & (UINT64_C(1) << t)) != 0U;
    if (t < 72U)
        return (roots->roots_64_71 & (uint8_t)(UINT8_C(1) << (t - 64U))) != 0U;
    return 0;
}

int main(void) {
    HHSExactPass219HHCQTemporalCubicDescriptorV1 descriptor;
    HHSExactPass219HHCQTemporalCubicWitnessV1 witness;
    HHSExactPass219HHCQTemporalCubicWitnessV1 replay_witness;
    HHSExactPass219HHCQTemporalCardanoFactorV1 factor;
    HHSExactPass219HHCQTemporalZ72RootsV1 roots;
    HHSExactPass219HHCQTemporalZ72RootsV1 replay_roots;
    HHSExactPass219HHCQTemporalZ72RootsV1 composite_roots;
    HHSExactPass219HHCQJointStateV1 state;

    assert(hhs_exact_pass219_hhcq_temporal_cubic_version() ==
           HHS_EXACT_PASS219_HHCQ_TEMPORAL_CUBIC_VERSION);
    assert(hhs_exact_pass219_hhcq_temporal_cubic_descriptor(&descriptor) ==
           HHS_EXACT_STATUS_OK);
    assert(descriptor.inherited_policy_state_bytes == sizeof(HHSExactPass219HHCQJointStateV1));
    assert(descriptor.inherited_policy_state_bytes == 112U);
    assert(descriptor.phase_modulus == 72U);
    assert(descriptor.symbolic_cardano_branch_count == 3U);
    assert(descriptor.compact_cubic_identity == 1U);
    assert(descriptor.factored_discriminant_identity == 1U);
    assert(descriptor.radical_eliminated_from_canonical_path == 1U);
    assert(descriptor.z72_root_scan == 1U);
    assert(descriptor.composite_ring_root_count_variable == 1U);
    assert(descriptor.discrete_neighbor_direction == 1U);
    assert(descriptor.phase5_resolution_locked == 1U);
    assert(descriptor.fixed_size_policy_state == 1U);
    assert(descriptor.candidate_only == 1U);
    assert(descriptor.exact_integer_only == 1U);
    assert(descriptor.canonical_mutation_authority == 0U);
    assert(descriptor.canonical_hash72_authority == 0U);
    assert(descriptor.canonical_hash216_authority == 0U);
    assert(descriptor.canonical_persistence_authority == 0U);
    assert(descriptor.floating_point_authority == 0U);

    assert(hhs_exact_pass219_hhcq_joint_state_init(&state) == HHS_EXACT_STATUS_OK);
    assert(sizeof(state) == 112U);

    /* G=3, F(t)=t^3-t+6; t=-2 is exact.  At t=-1 the best neighbor is -2. */
    assert(hhs_exact_pass219_hhcq_temporal_cubic_witness(
        2, 1, 1, 1, 1, -1, &witness) == HHS_EXACT_STATUS_OK);
    assert(witness.cross_phase_g == 3);
    assert(witness.leading_x2y2 == 1);
    assert(witness.constant_term == 6);
    assert(witness.residual_minus == 0);
    assert(witness.residual_zero == 6);
    assert(witness.residual_plus == 6);
    assert(witness.absolute_residual_zero == 6U);
    assert(witness.temporal_gain == 6U);
    assert(witness.temporal_direction == -1);
    assert(witness.exact_integer_only == 1U);
    assert(witness.candidate_only == 1U);
    assert(witness.canonical_authority_changed == 0U);
    assert(witness.floating_point_authority == 0U);
    assert(hhs_exact_pass219_hhcq_temporal_cubic_witness(
        2, 1, 1, 1, 1, -1, &replay_witness) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&witness, &replay_witness, sizeof(witness)) == 0);

    /* B=162 and R=B^2-108=26136, matching the factored supplied radical. */
    assert(hhs_exact_pass219_hhcq_temporal_cardano_factor(
        2, 1, 1, 1, 1, &factor) == HHS_EXACT_STATUS_OK);
    assert(factor.cross_phase_g == 3);
    assert(factor.cardano_b == 162);
    assert(factor.x12y12 == 1);
    assert(factor.discriminant_r == 26136);
    assert(factor.exact_factorization == 1U);
    assert(factor.exact_integer_only == 1U);
    assert(factor.candidate_only == 1U);
    assert(factor.floating_point_authority == 0U);

    assert(hhs_exact_pass219_hhcq_temporal_z72_roots(
        2, 1, 1, 1, 1, 71U, &roots) == HHS_EXACT_STATUS_OK);
    assert(roots.root_count == 3U);
    assert(root_present(&roots, 6U));
    assert(root_present(&roots, 14U));
    assert(root_present(&roots, 70U));
    assert(roots.preferred_root72 == 70U);
    assert(roots.preferred_direction == -1);
    assert(roots.symbolic_cardano_branch_count == 3U);
    assert(roots.composite_ring_root_count_variable == 1U);
    assert(roots.exact_integer_only == 1U);
    assert(roots.candidate_only == 1U);
    assert(roots.canonical_authority_changed == 0U);
    assert(roots.floating_point_authority == 0U);
    assert(hhs_exact_pass219_hhcq_temporal_z72_roots(
        2, 1, 1, 1, 1, 71U, &replay_roots) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&roots, &replay_roots, sizeof(roots)) == 0);

    /* Z_72 is composite: this cubic has nine residue roots, not only three. */
    assert(hhs_exact_pass219_hhcq_temporal_z72_roots(
        2, 1, 1, 3, 3, 0U, &composite_roots) == HHS_EXACT_STATUS_OK);
    assert(composite_roots.root_count == 9U);
    assert(root_present(&composite_roots, 6U));
    assert(root_present(&composite_roots, 14U));
    assert(root_present(&composite_roots, 22U));
    assert(root_present(&composite_roots, 30U));
    assert(root_present(&composite_roots, 38U));
    assert(root_present(&composite_roots, 46U));
    assert(root_present(&composite_roots, 54U));
    assert(root_present(&composite_roots, 62U));
    assert(root_present(&composite_roots, 70U));

    assert(hhs_exact_pass219_hhcq_temporal_cubic_witness(
        2, 1, 0, 1, 1, 0, &witness) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(hhs_exact_pass219_hhcq_temporal_cardano_factor(
        2, 1, 1, 0, 1, &factor) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(hhs_exact_pass219_hhcq_temporal_z72_roots(
        2, 1, 1, 1, 1, 72U, &roots) == HHS_EXACT_STATUS_RANGE_ERROR);
    assert(hhs_exact_pass219_hhcq_temporal_cubic_witness(
        2, 1, 1, 1, 1, INT32_MAX, &witness) == HHS_EXACT_STATUS_RANGE_ERROR);
    assert(hhs_exact_pass219_hhcq_temporal_cardano_factor(
        INT32_MAX, INT32_MAX, INT32_MAX, INT32_MAX, INT32_MAX, &factor) ==
           HHS_EXACT_STATUS_RANGE_ERROR);

    assert(hhs_exact_pass219_hhcq_joint_validate_state(&state) == HHS_EXACT_STATUS_OK);
    assert(sizeof(state) == 112U);
    return 0;
}

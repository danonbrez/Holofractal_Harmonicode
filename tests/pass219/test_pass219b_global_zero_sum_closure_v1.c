#include "../../hhs_runtime/include/hhs_runtime_exact_abi.h"

#include <assert.h>
#include <string.h>

static HHSExactBigUIntView view1(const uint8_t *p) {
    HHSExactBigUIntView v;
    v.struct_size = (uint32_t)sizeof(v);
    v.byte_length = 1U;
    v.bytes_be = p;
    return v;
}

int main(void) {
    HHSExactPass219BGlobalZeroSumClosureV1 proof;
    HHSExactPass219BGlobalZeroSumClosureV1 bad;
    HHSExactUQCELInputV1 input;
    HHSExactUQCELAdmissionV1 admission;
    HHSExactVM81Frame candidate;
    HHSExactVM81Frame committed;
    uint8_t compatibility_source_sha[HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES];
    uint8_t global_tensor_sha[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES];
    uint8_t phase_quantization_sha[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES];
    uint8_t closure_sha[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES];
    const uint8_t P[] = {4U};
    const uint8_t p[] = {3U};
    const uint8_t q[] = {5U};
    const uint8_t delta[] = {1U};
    const uint8_t A_placeholder[] = {1U};
    const uint8_t B_placeholder[] = {2U};
    const uint8_t badP[] = {5U};
    const uint8_t badp[] = {1U};
    const uint8_t badq[] = {24U};
    size_t i;

    assert(hhs_exact_pass219b_global_zero_sum_version() == ((1U << 16) | (1U << 8)));
    assert(hhs_exact_pass219b_global_zero_sum_prove(&proof) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219b_global_zero_sum_verify(&proof) == HHS_EXACT_STATUS_OK);
    assert(proof.phase_sum_real == 0);
    assert(proof.phase_sum_imag == 0);
    assert(proof.center_zero_sum_proven == 1U);
    assert(proof.phase_carrier_zero_sum_proven == 1U);
    assert(proof.pass129_unit_delta_theorem_bound == 1U);
    assert(proof.xy_unit_projection_bound == 1U);
    assert(proof.zw_unit_projection_bound == 1U);
    assert(proof.u72_unit_projection_bound == 1U);
    assert(proof.denominator_unit_perimeter_count == 8U);
    assert(proof.denominator_center_zero_sum_preserved == 1U);
    assert(proof.global_tensor_source_bound == 1U);
    assert(proof.phase_quantization_bound == 1U);
    assert(proof.lo_shu_sudoku_qudit_bound == 1U);
    assert(proof.vm81_hydration_geometry_bound == 1U);
    assert(proof.recursive_closure_proven == 1U);
    assert(proof.global_relation_bridge_proven == 1U);
    assert(proof.cell_count81 == 81U);
    assert(proof.lo_shu_group_count41 == 41U);
    assert(proof.trit_count3 == 3U);
    assert(proof.hydration_slot_count5184 == 5184U);
    assert(proof.hydration_state_count == UINT64_C(51648192));
    assert(proof.phase_projected_state_count == UINT64_C(4183503552));
    assert(proof.canonical_mutation_authority == 0U);
    assert(proof.canonical_persistence_authority == 0U);
    assert(proof.canonical_hash72_authority == 0U);
    assert(proof.proof_mask == HHS_EXACT_PASS219B_ZERO_SUM_PROOF_REQUIRED);

    assert(hhs_exact_pass219b_global_zero_sum_source_sha256(closure_sha) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219b_global_tensor_source_sha256(global_tensor_sha) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219b_phase_quantization_source_sha256(phase_quantization_sha) == HHS_EXACT_STATUS_OK);
    assert(memcmp(closure_sha, proof.closure_extension_sha256, sizeof(closure_sha)) == 0);
    assert(memcmp(global_tensor_sha, proof.global_tensor_source_sha256, sizeof(global_tensor_sha)) == 0);
    assert(memcmp(phase_quantization_sha, proof.phase_quantization_object_sha256,
                  sizeof(phase_quantization_sha)) == 0);

    bad = proof;
    bad.phase_sum_real = 1;
    assert(hhs_exact_pass219b_global_zero_sum_verify(&bad) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    bad = proof;
    bad.recursive_closure_proven = 0U;
    assert(hhs_exact_pass219b_global_zero_sum_verify(&bad) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    bad = proof;
    bad.global_relation_bridge_proven = 0U;
    assert(hhs_exact_pass219b_global_zero_sum_verify(&bad) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    bad = proof;
    bad.phase_quantization_object_sha256[0] ^= UINT8_C(1);
    assert(hhs_exact_pass219b_global_zero_sum_verify(&bad) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    bad = proof;
    bad.canonical_mutation_authority = 1U;
    assert(hhs_exact_pass219b_global_zero_sum_verify(&bad) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    memset(&input, 0, sizeof(input));
    input.struct_size = (uint32_t)sizeof(input);
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1;
    input.P = view1(P);
    input.p = view1(p);
    input.q = view1(q);
    input.delta = view1(delta);

    /*
     * These V1 fields are compatibility transport placeholders in the
     * full-symbolic profile. Deliberately choose values unequal to P^2 to prove
     * the full bridge does not regress to A=P^2/B=P^2 scalar substitution.
     */
    input.A = view1(A_placeholder);
    input.B = view1(B_placeholder);
    input.cell81 = 41U;
    input.left_basis8 = HHS_EXACT_PHASE_X;
    input.right_basis8 = HHS_EXACT_PHASE_Y;
    memcpy(input.source_envelope_sha256, global_tensor_sha, sizeof(global_tensor_sha));
    memset(input.previous_hash72, '0', HHS_EXACT_HASH72_LEN);
    input.previous_hash72[HHS_EXACT_HASH72_LEN] = '\0';

    assert(hhs_exact_uqcel_validate(&input, &admission) == HHS_EXACT_STATUS_OK);
    assert(admission.decision == HHS_EXACT_UQCEL_DECISION_ADMIT);
    assert(admission.reject_reason == HHS_EXACT_UQCEL_REASON_NONE);
    assert(admission.required_mask == HHS_UQCEL_CONSTRAINT_FULL_SYMBOLIC_REQUIRED);
    assert((admission.satisfied_mask & admission.required_mask) == admission.required_mask);
    assert((admission.satisfied_mask & HHS_UQCEL_CONSTRAINT_GLOBAL_ZERO_SUM_CLOSURE) != 0U);
    assert((admission.satisfied_mask & HHS_UQCEL_CONSTRAINT_CENTER_DELTA_SYMMETRY) != 0U);
    assert((admission.satisfied_mask & HHS_UQCEL_CONSTRAINT_GLOBAL_RELATION_BRIDGE) != 0U);
    assert((admission.satisfied_mask & HHS_UQCEL_CONSTRAINT_LOSHU) != 0U);
    assert((admission.satisfied_mask & HHS_UQCEL_CONSTRAINT_VM5184) != 0U);
    assert((admission.satisfied_mask & HHS_UQCEL_CONSTRAINT_AB_SYMMETRIC) == 0U);
    assert((admission.satisfied_mask & HHS_UQCEL_CONSTRAINT_AB_QUARTIC) == 0U);
    assert(admission.residual_mask == 0U);
    assert(admission.frame_committed == 0U);

    /*
     * Full symbolic source identity is N, not the older compatibility-profile
     * source envelope.
     */
    assert(hhs_exact_uqcel_source_sha256(compatibility_source_sha) == HHS_EXACT_STATUS_OK);
    memcpy(input.source_envelope_sha256, compatibility_source_sha, sizeof(compatibility_source_sha));
    assert(hhs_exact_uqcel_validate(&input, &admission) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    assert(admission.reject_reason == HHS_EXACT_UQCEL_REASON_SOURCE_HASH);
    memcpy(input.source_envelope_sha256, global_tensor_sha, sizeof(global_tensor_sha));

    /*
     * P^2=pq+1 alone is insufficient. The same full-symbolic candidate must
     * belong to the exact center family p=P-1, q=P+1, and the zero-sum bit may
     * not be satisfied before that candidate binding succeeds.
     */
    input.P = view1(badP);
    input.p = view1(badp);
    input.q = view1(badq);
    assert(hhs_exact_uqcel_validate(&input, &admission) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    assert(admission.reject_reason == HHS_EXACT_UQCEL_REASON_CENTER_DELTA_SYMMETRY);
    assert((admission.satisfied_mask & HHS_UQCEL_CONSTRAINT_GLOBAL_ZERO_SUM_CLOSURE) == 0U);

    input.P = view1(P);
    input.p = view1(p);
    input.q = view1(q);

    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        candidate.words[i] = UINT64_C(0x219B000000000000) ^ (uint64_t)i;

    memset(&committed, 0, sizeof(committed));
    assert(hhs_exact_vm81_admit_uqcel(
        &input, &candidate, &committed, &admission) == HHS_EXACT_STATUS_OK);
    assert(admission.decision == HHS_EXACT_UQCEL_DECISION_ADMIT);
    assert(admission.residual_mask == 0U);
    assert(admission.frame_committed == 1U);
    assert(memcmp(&committed, &candidate, sizeof(candidate)) == 0);

    return 0;
}

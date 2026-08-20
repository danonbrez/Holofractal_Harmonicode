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
    HHSExactPass219BGlobalZeroSumClosureV1 bad_proof;
    HHSExactPass219BGlobalRelationInputV1 input;
    HHSExactPass219BGlobalRelationInputV1 bad_input;
    HHSExactPass219BGlobalRelationHydrationWitnessV1 witness37;
    HHSExactPass219BGlobalRelationHydrationWitnessV1 witness80;
    uint8_t global_tensor_sha[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES];
    uint8_t phase_quantization_sha[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES];
    uint8_t closure_sha[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES];
    const uint8_t P[] = {4U};
    const uint8_t p[] = {3U};
    const uint8_t q[] = {5U};
    const uint8_t delta[] = {1U};
    const uint8_t badp[] = {1U};
    const uint8_t badq[] = {15U};

    assert(hhs_exact_pass219b_global_zero_sum_version() ==
           ((1U << 16) | (3U << 8)));
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
    assert(proof.legacy_full_symbolic_v1_preserved == 1U);
    assert(proof.global_enforcement_required == 1U);
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

    bad_proof = proof;
    bad_proof.phase_sum_real = 1;
    assert(hhs_exact_pass219b_global_zero_sum_verify(&bad_proof) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    bad_proof = proof;
    bad_proof.legacy_full_symbolic_v1_preserved = 0U;
    assert(hhs_exact_pass219b_global_zero_sum_verify(&bad_proof) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    bad_proof = proof;
    bad_proof.canonical_mutation_authority = 1U;
    assert(hhs_exact_pass219b_global_zero_sum_verify(&bad_proof) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    memset(&input, 0, sizeof(input));
    input.struct_size = (uint32_t)sizeof(input);
    input.version = hhs_exact_pass219b_global_zero_sum_version();
    input.P = view1(P);
    input.p = view1(p);
    input.q = view1(q);
    input.delta = view1(delta);
    input.cell81 = 41U;
    input.left_basis8 = HHS_EXACT_PHASE_X;
    input.right_basis8 = HHS_EXACT_PHASE_Y;
    input.phase_origin81 = 37U;
    input.lo_shu_group = 0;
    input.g243 = 0U;
    memcpy(input.global_tensor_source_sha256, global_tensor_sha, sizeof(global_tensor_sha));
    memcpy(input.phase_quantization_source_sha256, phase_quantization_sha,
           sizeof(phase_quantization_sha));
    memset(input.previous_hash72, '0', HHS_EXACT_HASH72_LEN);
    input.previous_hash72[HHS_EXACT_HASH72_LEN] = '\0';

    assert(hhs_exact_pass219b_global_relation_hydration_verify(
        &input, &witness37) == HHS_EXACT_STATUS_OK);
    assert(witness37.global_tensor_source_verified == 1U);
    assert(witness37.phase_quantization_source_verified == 1U);
    assert(witness37.zero_sum_family_verified == 1U);
    assert(witness37.uqcel_integer_projection_verified == 1U);
    assert(witness37.uqcel_integer_projection.decision == HHS_EXACT_UQCEL_DECISION_ADMIT);
    assert(witness37.uqcel_integer_projection.frame_committed == 0U);
    assert(witness37.legacy_full_symbolic_v1_preserved == 1U);
    assert(witness37.legacy_full_symbolic_probe.decision ==
           HHS_EXACT_UQCEL_DECISION_UNSUPPORTED_DOMAIN);
    assert(witness37.legacy_full_symbolic_probe.reject_reason ==
           HHS_EXACT_UQCEL_REASON_FULL_SYMBOLIC_RESIDUAL);
    assert(witness37.legacy_full_symbolic_probe.residual_mask == HHS_UQCEL_RESIDUAL_FULL_SOURCE);
    assert(witness37.coordinate_roundtrip_verified == 1U);
    assert(witness37.native_phase_verified == 1U);
    assert(witness37.trinary_gate_verified == 1U);
    assert(witness37.phase_cell_verified == 1U);
    assert(witness37.phase_locality_verified == 1U);
    assert(witness37.global_relation_bridge_verified == 1U);
    assert(witness37.coordinate.cell81 == input.cell81);
    assert(witness37.coordinate.lo_shu_group == input.lo_shu_group);
    assert(witness37.coordinate.g243 == input.g243);
    assert(witness37.phase_cell.phase_origin81 == input.phase_origin81);
    assert(witness37.phase_cell.center_closure_preserved == 1U);
    assert(witness37.phase_cell.tensor_source_preserved == 1U);
    assert(witness37.locality_plan.potential_phase_volume == 81U);
    assert(witness37.locality_plan.materialized_phase_volume == 1U);
    assert(witness37.canonical_mutation_authority == 0U);
    assert(witness37.canonical_persistence_authority == 0U);
    assert(witness37.canonical_hash72_authority == 0U);

    input.phase_origin81 = 80U;
    assert(hhs_exact_pass219b_global_relation_hydration_verify(
        &input, &witness80) == HHS_EXACT_STATUS_OK);
    assert(witness37.phase_cell.projection_index != witness80.phase_cell.projection_index);

    bad_input = input;
    bad_input.phase_origin81 = 81U;
    assert(hhs_exact_pass219b_global_relation_hydration_verify(
        &bad_input, &witness80) == HHS_EXACT_STATUS_RANGE_ERROR);

    bad_input = input;
    bad_input.lo_shu_group = 21;
    assert(hhs_exact_pass219b_global_relation_hydration_verify(
        &bad_input, &witness80) == HHS_EXACT_STATUS_RANGE_ERROR);

    bad_input = input;
    bad_input.g243 = 243U;
    assert(hhs_exact_pass219b_global_relation_hydration_verify(
        &bad_input, &witness80) == HHS_EXACT_STATUS_RANGE_ERROR);

    bad_input = input;
    bad_input.p = view1(badp);
    bad_input.q = view1(badq);
    assert(hhs_exact_pass219b_global_relation_hydration_verify(
        &bad_input, &witness80) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);

    bad_input = input;
    bad_input.global_tensor_source_sha256[0] ^= UINT8_C(1);
    assert(hhs_exact_pass219b_global_relation_hydration_verify(
        &bad_input, &witness80) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);

    bad_input = input;
    bad_input.phase_quantization_source_sha256[0] ^= UINT8_C(1);
    assert(hhs_exact_pass219b_global_relation_hydration_verify(
        &bad_input, &witness80) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);

    return 0;
}

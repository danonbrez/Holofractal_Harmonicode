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
    uint8_t source_sha[HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES];
    uint8_t closure_sha[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES];
    const uint8_t P[] = {4U};
    const uint8_t p[] = {3U};
    const uint8_t q[] = {5U};
    const uint8_t delta[] = {1U};
    const uint8_t A[] = {16U};
    const uint8_t B[] = {16U};

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
    assert(proof.recursive_fixed_point_required == 1U);
    assert(proof.monolithic_chain_required == 1U);
    assert(proof.full_monolithic_evaluated == 0U);
    assert(proof.global_enforcement_required == 1U);
    assert(proof.canonical_mutation_authority == 0U);
    assert(proof.canonical_persistence_authority == 0U);
    assert(proof.canonical_hash72_authority == 0U);
    assert(proof.proof_mask == HHS_EXACT_PASS219B_ZERO_SUM_PROOF_REQUIRED);

    assert(hhs_exact_pass219b_global_zero_sum_source_sha256(closure_sha) == HHS_EXACT_STATUS_OK);
    assert(memcmp(closure_sha, proof.closure_extension_sha256, sizeof(closure_sha)) == 0);

    bad = proof;
    bad.phase_sum_real = 1;
    assert(hhs_exact_pass219b_global_zero_sum_verify(&bad) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    bad = proof;
    bad.full_monolithic_evaluated = 1U;
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
    input.A = view1(A);
    input.B = view1(B);
    assert(hhs_exact_uqcel_source_sha256(source_sha) == HHS_EXACT_STATUS_OK);
    memcpy(input.source_envelope_sha256, source_sha, sizeof(source_sha));

    assert(hhs_exact_uqcel_validate(&input, &admission) == HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN);
    assert(admission.decision == HHS_EXACT_UQCEL_DECISION_UNSUPPORTED_DOMAIN);
    assert(admission.required_mask == HHS_UQCEL_CONSTRAINT_FULL_SYMBOLIC_REQUIRED);
    assert((admission.satisfied_mask & HHS_UQCEL_CONSTRAINT_GLOBAL_ZERO_SUM_CLOSURE) != 0U);
    assert((admission.residual_mask & HHS_UQCEL_RESIDUAL_MONOLITHIC_EQUALITY_CHAIN) != 0U);
    assert(admission.frame_committed == 0U);

    return 0;
}

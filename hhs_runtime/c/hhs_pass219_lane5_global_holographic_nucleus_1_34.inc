#include "hhs_pass219_lane5_global_holographic_nucleus_1_34.h"

#include <string.h>

static uint64_t hhs_p219_lane5_mix_u64(uint64_t hash, uint64_t value) {
    unsigned shift;
    for (shift = 0U; shift < 64U; shift += 8U) {
        hash ^= (value >> shift) & UINT64_C(0xff);
        hash *= UINT64_C(1099511628211);
    }
    return hash;
}

uint32_t hhs_exact_pass219_lane5_nucleus_version(void) {
    return HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_nucleus_authority(
    HHSExactPass219Lane5NucleusAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5NucleusAuthorityV1 authority;
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&authority, 0, sizeof(authority));
    authority.struct_size = (uint32_t)sizeof(authority);
    authority.version = HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION;
    authority.namespace_id = HHS_EXACT_PASS219_LANE5_NAMESPACE;
    authority.global_root_orchestration = 1U;
    authority.global_traffic_mediation = 1U;
    authority.validated_hash216_read_only = 1U;
    authority.hash216_sha256_array_addressing = 1U;
    authority.four_lane_hydration_composition = 1U;
    authority.pass133_bigint_serialization = 1U;
    authority.pass211_hfc_frame_compatible = 1U;
    authority.nested_modular_fibonacci_reuse = 1U;
    authority.graphics_vector_hydration = 1U;
    authority.api_registry_visible = 1U;
    authority.learning_iteration_cycle = 1U;
    authority.rna_cpp_cell_wall_bound = 1U;
    authority.exact_vm5184_carrier = 1U;
    authority.exact_integer_only = 1U;
    authority.candidate_only = 1U;
    authority.canonical_vm81_mutation_authority = 0U;
    authority.canonical_hash72_authority = 0U;
    authority.canonical_hash216_authority = 0U;
    authority.canonical_persistence_authority = 0U;
    authority.pqc_key_authority = 0U;
    authority.receipt_clock_authority = 0U;
    authority.floating_point_canonical_authority = 0U;
    authority.requires_signed_environmental_vm81_admission = 1U;
    *out_authority = authority;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_mediate_candidate(
    const HHSExactPass219Lane5MediationRequestV1 *request,
    HHSExactPass219Lane5MediationReceiptV1 *out_receipt
) {
    HHSExactPass219Lane5MediationReceiptV1 receipt;
    uint64_t closure = UINT64_C(1469598103934665603);
    uint64_t mediation = UINT64_C(1469598103934665603);
    uint32_t i;

    if (out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_receipt, 0, sizeof(*out_receipt));
    if (request == NULL ||
        request->struct_size != (uint32_t)sizeof(*request) ||
        request->version != HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION ||
        request->namespace_id != HHS_EXACT_PASS219_LANE5_NAMESPACE ||
        request->hash216_reference_count == 0U ||
        request->hash216_reference_count > HHS_EXACT_PASS219_LANE5_MAX_HASH216_REFS ||
        request->capability_reference_count == 0U ||
        request->capability_reference_count > HHS_EXACT_PASS219_LANE5_MAX_CAPABILITY_REFS ||
        request->request_signature64 == 0U ||
        request->candidate_signature64 == 0U ||
        request->parent_hash216_signature64 == 0U ||
        request->bigint_address_signature64 == 0U ||
        request->hydration_signature64 == 0U ||
        request->capability_registry_signature64 == 0U ||
        request->learning_iteration_signature64 == 0U ||
        request->rna_prepared_signature64 == 0U ||
        request->rna_decision_signature64 == 0U) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }

    for (i = 0U; i < request->hash216_reference_count; ++i) {
        if (request->hash216_reference_signature64[i] == 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        closure = hhs_p219_lane5_mix_u64(
            closure, request->hash216_reference_signature64[i]);
    }
    for (i = 0U; i < request->capability_reference_count; ++i) {
        if (request->capability_reference_signature64[i] == 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        closure = hhs_p219_lane5_mix_u64(
            closure, request->capability_reference_signature64[i]);
    }

    closure = hhs_p219_lane5_mix_u64(closure, request->parent_hash216_signature64);
    closure = hhs_p219_lane5_mix_u64(closure, request->bigint_address_signature64);
    closure = hhs_p219_lane5_mix_u64(closure, request->hydration_signature64);
    closure = hhs_p219_lane5_mix_u64(closure, request->compression_signature64);
    closure = hhs_p219_lane5_mix_u64(closure, request->capability_registry_signature64);
    closure = hhs_p219_lane5_mix_u64(closure, request->learning_iteration_signature64);
    closure = hhs_p219_lane5_mix_u64(closure, request->rna_prepared_signature64);
    closure = hhs_p219_lane5_mix_u64(closure, request->rna_decision_signature64);
    if (closure == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    mediation = hhs_p219_lane5_mix_u64(mediation, request->request_signature64);
    mediation = hhs_p219_lane5_mix_u64(mediation, request->candidate_signature64);
    mediation = hhs_p219_lane5_mix_u64(mediation, closure);
    mediation = hhs_p219_lane5_mix_u64(mediation, request->learning_stage);
    mediation = hhs_p219_lane5_mix_u64(mediation, request->hash216_reference_count);
    mediation = hhs_p219_lane5_mix_u64(mediation, request->capability_reference_count);
    if (mediation == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(&receipt, 0, sizeof(receipt));
    receipt.struct_size = (uint32_t)sizeof(receipt);
    receipt.version = HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION;
    receipt.namespace_id = HHS_EXACT_PASS219_LANE5_NAMESPACE;
    receipt.decision = HHS_EXACT_PASS219_LANE5_DECISION_CANDIDATE_READY;
    receipt.learning_stage = request->learning_stage;
    receipt.hash216_reference_count = request->hash216_reference_count;
    receipt.capability_reference_count = request->capability_reference_count;
    receipt.request_signature64 = request->request_signature64;
    receipt.candidate_signature64 = request->candidate_signature64;
    receipt.parent_hash216_signature64 = request->parent_hash216_signature64;
    receipt.bigint_address_signature64 = request->bigint_address_signature64;
    receipt.hydration_signature64 = request->hydration_signature64;
    receipt.compression_signature64 = request->compression_signature64;
    receipt.capability_registry_signature64 = request->capability_registry_signature64;
    receipt.learning_iteration_signature64 = request->learning_iteration_signature64;
    receipt.rna_prepared_signature64 = request->rna_prepared_signature64;
    receipt.rna_decision_signature64 = request->rna_decision_signature64;
    receipt.closure_signature64 = closure;
    receipt.mediation_signature64 = mediation;
    receipt.hash216_references_validated = 1U;
    receipt.capability_registry_validated = 1U;
    receipt.exact_vm5184_bound = 1U;
    receipt.rna_cell_wall_bound = 1U;
    receipt.zero_sum_closure_passed = 1U;
    receipt.candidate_only = 1U;
    receipt.canonical_mutation_authority = 0U;
    receipt.canonical_hash72_authority = 0U;
    receipt.canonical_hash216_authority = 0U;
    receipt.canonical_persistence_authority = 0U;
    receipt.requires_environmental_admission = 1U;
    *out_receipt = receipt;
    return HHS_EXACT_STATUS_OK;
}

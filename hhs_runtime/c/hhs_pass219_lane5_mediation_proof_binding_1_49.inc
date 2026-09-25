#include "../include/hhs_pass219_lane5_mediation_proof_binding_1_49.h"

#include <string.h>

static uint64_t hhs_l5pb_mix_u64(uint64_t hash, uint64_t value) {
    unsigned shift;
    for (shift = 0U; shift < 64U; shift += 8U) {
        hash ^= (value >> shift) & UINT64_C(0xff);
        hash *= UINT64_C(1099511628211);
    }
    return hash;
}

static uint64_t hhs_l5pb_mix_bytes(uint64_t hash, const void *data, size_t length) {
    const uint8_t *bytes = (const uint8_t *)data;
    size_t i;
    for (i = 0U; i < length; ++i) {
        hash ^= (uint64_t)bytes[i];
        hash *= UINT64_C(1099511628211);
    }
    return hash;
}

static int hhs_l5pb_zero_sum_all_zero(
    const HHSExactPass219Lane5ZeroSumClosureWitnessV1 *witness
) {
    return witness != NULL &&
           witness->state_change_residual == 0 &&
           witness->dependency_change_residual == 0 &&
           witness->phase_change_residual == 0 &&
           witness->resource_work_residual == 0 &&
           witness->lineage_residual == 0 &&
           witness->inverse_recovery_residual == 0 &&
           witness->local_constraint_residual == 0 &&
           witness->global_constraint_residual == 0;
}

static uint64_t hhs_l5pb_zero_sum_signature(
    const HHSExactPass219Lane5ZeroSumClosureWitnessV1 *witness
) {
    uint64_t hash = UINT64_C(1469598103934665603);
    hash = hhs_l5pb_mix_u64(hash, (uint64_t)witness->state_change_residual);
    hash = hhs_l5pb_mix_u64(hash, (uint64_t)witness->dependency_change_residual);
    hash = hhs_l5pb_mix_u64(hash, (uint64_t)witness->phase_change_residual);
    hash = hhs_l5pb_mix_u64(hash, (uint64_t)witness->resource_work_residual);
    hash = hhs_l5pb_mix_u64(hash, (uint64_t)witness->lineage_residual);
    hash = hhs_l5pb_mix_u64(hash, (uint64_t)witness->inverse_recovery_residual);
    hash = hhs_l5pb_mix_u64(hash, (uint64_t)witness->local_constraint_residual);
    hash = hhs_l5pb_mix_u64(hash, (uint64_t)witness->global_constraint_residual);
    hash = hhs_l5pb_mix_u64(hash, witness->request_signature64);
    hash = hhs_l5pb_mix_u64(hash, witness->candidate_signature64);
    hash = hhs_l5pb_mix_u64(hash, witness->parent_hash216_signature64);
    hash = hhs_l5pb_mix_u64(hash, witness->rna_prepared_signature64);
    hash = hhs_l5pb_mix_u64(hash, witness->rna_decision_signature64);
    hash = hhs_l5pb_mix_u64(hash, witness->capability_registry_signature64);
    return hash;
}

uint32_t hhs_exact_pass219_lane5_mediation_proof_binding_version(void) {
    return HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_mediation_proof_binding_authority(
    HHSExactPass219Lane5MediationProofBindingAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5MediationProofBindingAuthorityV1 authority;
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&authority, 0, sizeof(authority));
    authority.struct_size = (uint32_t)sizeof(authority);
    authority.version = HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_VERSION;
    authority.namespace_id = HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_NAMESPACE;
    authority.legacy_1_34_proof_flags_authoritative = 0U;
    authority.request_identity_recomputed = 1U;
    authority.exact_vm5184_recomputed = 1U;
    authority.rna_cpp_cell_wall_replayed = 1U;
    authority.hash216_sha256_positions_verified = 1U;
    authority.capability_registry_recomputed = 1U;
    authority.exact_zero_sum_residual_vector_required = 1U;
    authority.deterministic_proof_binding = 1U;
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

HHSExactStatus hhs_exact_pass219_lane5_mediation_frame_signature(
    const HHSExactVM81Frame *frame,
    uint64_t *out_signature64
) {
    uint8_t bytes[HHS_EXACT_VM81_FRAME_BYTES];
    size_t written = 0U;
    uint64_t hash = UINT64_C(1469598103934665603);
    HHSExactStatus status;
    if (frame == NULL || out_signature64 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_signature64 = 0U;
    status = hhs_exact_vm81_frame_export_le(frame, bytes, sizeof(bytes), &written);
    if (status != HHS_EXACT_STATUS_OK || written != sizeof(bytes))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    hash = hhs_l5pb_mix_bytes(hash, bytes, sizeof(bytes));
    if (hash == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    *out_signature64 = hash;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_mediation_hash216_reference_signature(
    const HHSExactPass219Hash216TransitionViewV1 *reference,
    uint64_t *out_signature64
) {
    uint64_t hash = UINT64_C(1469598103934665603);
    uint32_t i;
    if (reference == NULL || out_signature64 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_signature64 = 0U;
    if (hhs_exact_pass219_vm81_pqc_hash216_reference_verify(reference) !=
        HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    hash = hhs_l5pb_mix_bytes(
        hash, reference->transition_identity216,
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    hash = hhs_l5pb_mix_bytes(
        hash, reference->previous_hash72, HHS_EXACT_HASH72_LEN);
    hash = hhs_l5pb_mix_bytes(
        hash, reference->change_hash72, HHS_EXACT_HASH72_LEN);
    hash = hhs_l5pb_mix_bytes(
        hash, reference->receipt_hash72, HHS_EXACT_HASH72_LEN);
    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++i) {
        const HHSExactPass219Hash72TokenOccurrenceV1 *occurrence =
            &reference->occurrences[i];
        hash = hhs_l5pb_mix_u64(hash, occurrence->absolute_position216);
        hash = hhs_l5pb_mix_u64(hash, occurrence->lane_role);
        hash = hhs_l5pb_mix_u64(hash, occurrence->lane_position72);
        hash = hhs_l5pb_mix_u64(hash, occurrence->glyph);
        hash = hhs_l5pb_mix_bytes(
            hash, occurrence->sha256_index_record,
            HHS_EXACT_PASS219_HASH216_SHA256_BYTES);
    }
    if (hash == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    *out_signature64 = hash;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_zero_sum_witness_seal(
    HHSExactPass219Lane5ZeroSumClosureWitnessV1 *witness
) {
    uint64_t signature;
    if (witness == NULL ||
        witness->struct_size != (uint32_t)sizeof(*witness) ||
        witness->version != HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_VERSION ||
        witness->namespace_id != HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_NAMESPACE)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    signature = hhs_l5pb_zero_sum_signature(witness);
    if (signature == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    witness->witness_signature64 = signature;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_mediation_proof_bind(
    const HHSExactPass219Lane5MediationRequestV1 *request,
    const HHSExactPass219Lane5MediationProofBundleV1 *proof,
    HHSExactPass219Lane5ProvenMediationReceiptV1 *out_receipt
) {
    HHSExactPass219Lane5MediationReceiptV1 base;
    HHSExactPass219Holo4PreparedV1 replay_prepared;
    HHSExactPass219Holo4DecisionV1 replay_decision;
    HHSExactPass219Lane5CapabilitySelfModelReceiptV1 replay_capability;
    HHSExactPass219Lane5ZeroSumClosureWitnessV1 zero_copy;
    uint64_t frame_signature = 0U;
    uint64_t parent_signature = 0U;
    uint64_t hash216_set_signature = UINT64_C(1469598103934665603);
    uint64_t proof_signature = UINT64_C(1469598103934665603);
    uint32_t i;
    HHSExactStatus status;

    if (out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_receipt, 0, sizeof(*out_receipt));

    if (request == NULL || proof == NULL ||
        proof->struct_size != (uint32_t)sizeof(*proof) ||
        proof->version != HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_VERSION ||
        proof->namespace_id != HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_NAMESPACE ||
        proof->input == NULL || proof->candidate_frame == NULL ||
        proof->parent_hash216_reference == NULL ||
        proof->rna_prepared == NULL || proof->rna_decision == NULL ||
        proof->hash216_references == NULL ||
        proof->capability_descriptor == NULL || proof->capability_receipt == NULL ||
        proof->zero_sum_witness == NULL ||
        proof->hash216_reference_count != request->hash216_reference_count)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(&base, 0, sizeof(base));
    status = hhs_exact_pass219_lane5_mediate_candidate(request, &base);
    if (status != HHS_EXACT_STATUS_OK ||
        base.decision != HHS_EXACT_PASS219_LANE5_DECISION_CANDIDATE_READY ||
        base.hash216_references_validated != 0U ||
        base.capability_registry_validated != 0U ||
        base.exact_vm5184_bound != 0U ||
        base.rna_cell_wall_bound != 0U ||
        base.zero_sum_closure_passed != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_lane5_mediation_frame_signature(
        proof->candidate_frame, &frame_signature);
    if (status != HHS_EXACT_STATUS_OK ||
        frame_signature != request->candidate_signature64)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_lane5_mediation_hash216_reference_signature(
        proof->parent_hash216_reference, &parent_signature);
    if (status != HHS_EXACT_STATUS_OK ||
        parent_signature != request->parent_hash216_signature64)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(&replay_prepared, 0, sizeof(replay_prepared));
    memset(&replay_decision, 0, sizeof(replay_decision));
    status = hhs_exact_pass219_rna_vm5184_route(
        proof->input,
        proof->candidate_frame,
        proof->parent_hash216_reference,
        proof->feedback_lane,
        proof->feedback_trinary,
        &replay_prepared,
        &replay_decision);
    if (status != HHS_EXACT_STATUS_OK ||
        memcmp(&replay_prepared, proof->rna_prepared, sizeof(replay_prepared)) != 0 ||
        memcmp(&replay_decision, proof->rna_decision, sizeof(replay_decision)) != 0 ||
        request->rna_prepared_signature64 != replay_prepared.graph_signature64 ||
        request->hydration_signature64 != replay_prepared.tensor_signature64 ||
        request->rna_decision_signature64 != replay_decision.decision_signature64)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (i = 0U; i < proof->hash216_reference_count; ++i) {
        uint64_t signature = 0U;
        status = hhs_exact_pass219_lane5_mediation_hash216_reference_signature(
            &proof->hash216_references[i], &signature);
        if (status != HHS_EXACT_STATUS_OK ||
            signature != request->hash216_reference_signature64[i])
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        hash216_set_signature = hhs_l5pb_mix_u64(hash216_set_signature, signature);
    }
    if (hash216_set_signature == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(&replay_capability, 0, sizeof(replay_capability));
    status = hhs_exact_pass219_lane5_capability_self_model_validate(
        proof->capability_descriptor, &replay_capability);
    if (status != HHS_EXACT_STATUS_OK ||
        memcmp(&replay_capability, proof->capability_receipt, sizeof(replay_capability)) != 0 ||
        replay_capability.accepted != 1U ||
        request->capability_registry_signature64 != replay_capability.receipt_signature64)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (i = 0U; i < request->capability_reference_count; ++i) {
        uint32_t j;
        int found = 0;
        for (j = 0U; j < proof->capability_descriptor->total_entries; ++j) {
            if (proof->capability_descriptor->entry_signature64[j] ==
                request->capability_reference_signature64[i]) {
                found = 1;
                break;
            }
        }
        if (!found)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (proof->zero_sum_witness->struct_size !=
            (uint32_t)sizeof(*proof->zero_sum_witness) ||
        proof->zero_sum_witness->version !=
            HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_VERSION ||
        proof->zero_sum_witness->namespace_id !=
            HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_NAMESPACE ||
        !hhs_l5pb_zero_sum_all_zero(proof->zero_sum_witness) ||
        proof->zero_sum_witness->request_signature64 != request->request_signature64 ||
        proof->zero_sum_witness->candidate_signature64 != request->candidate_signature64 ||
        proof->zero_sum_witness->parent_hash216_signature64 !=
            request->parent_hash216_signature64 ||
        proof->zero_sum_witness->rna_prepared_signature64 !=
            request->rna_prepared_signature64 ||
        proof->zero_sum_witness->rna_decision_signature64 !=
            request->rna_decision_signature64 ||
        proof->zero_sum_witness->capability_registry_signature64 !=
            request->capability_registry_signature64)
        return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;

    zero_copy = *proof->zero_sum_witness;
    zero_copy.witness_signature64 = 0U;
    status = hhs_exact_pass219_lane5_zero_sum_witness_seal(&zero_copy);
    if (status != HHS_EXACT_STATUS_OK ||
        zero_copy.witness_signature64 != proof->zero_sum_witness->witness_signature64)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    proof_signature = hhs_l5pb_mix_u64(proof_signature, base.mediation_signature64);
    proof_signature = hhs_l5pb_mix_u64(proof_signature, frame_signature);
    proof_signature = hhs_l5pb_mix_u64(proof_signature, parent_signature);
    proof_signature = hhs_l5pb_mix_u64(proof_signature, hash216_set_signature);
    proof_signature = hhs_l5pb_mix_u64(
        proof_signature, replay_capability.receipt_signature64);
    proof_signature = hhs_l5pb_mix_u64(
        proof_signature, proof->zero_sum_witness->witness_signature64);
    proof_signature = hhs_l5pb_mix_u64(
        proof_signature, replay_prepared.graph_signature64);
    proof_signature = hhs_l5pb_mix_u64(
        proof_signature, replay_prepared.tensor_signature64);
    proof_signature = hhs_l5pb_mix_u64(
        proof_signature, replay_decision.decision_signature64);
    if (proof_signature == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_receipt->struct_size = (uint32_t)sizeof(*out_receipt);
    out_receipt->version = HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_VERSION;
    out_receipt->namespace_id = HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_NAMESPACE;
    out_receipt->hash216_reference_count = request->hash216_reference_count;
    out_receipt->capability_reference_count = request->capability_reference_count;
    out_receipt->base_receipt = base;
    out_receipt->candidate_frame_signature64 = frame_signature;
    out_receipt->parent_hash216_signature64 = parent_signature;
    out_receipt->hash216_reference_set_signature64 = hash216_set_signature;
    out_receipt->capability_receipt_signature64 = replay_capability.receipt_signature64;
    out_receipt->zero_sum_witness_signature64 =
        proof->zero_sum_witness->witness_signature64;
    out_receipt->proof_binding_signature64 = proof_signature;
    out_receipt->request_recomputed = 1U;
    out_receipt->exact_vm5184_bound = 1U;
    out_receipt->rna_cell_wall_bound = 1U;
    out_receipt->hash216_references_validated = 1U;
    out_receipt->capability_registry_validated = 1U;
    out_receipt->zero_sum_closure_passed = 1U;
    out_receipt->all_proofs_bound = 1U;
    out_receipt->candidate_only = 1U;
    out_receipt->canonical_mutation_authority = 0U;
    out_receipt->canonical_hash72_authority = 0U;
    out_receipt->canonical_hash216_authority = 0U;
    out_receipt->canonical_persistence_authority = 0U;
    out_receipt->requires_environmental_admission = 1U;
    return HHS_EXACT_STATUS_OK;
}

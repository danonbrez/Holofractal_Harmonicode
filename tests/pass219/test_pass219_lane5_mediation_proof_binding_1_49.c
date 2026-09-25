#include "hhs_pass219_lane5_mediation_proof_binding_1_49.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed: %s at %s:%d\n", #expr, __FILE__, __LINE__); \
        return 1; \
    } \
} while (0)

static void make_capability_descriptor(
    HHSExactPass219Lane5CapabilitySelfModelDescriptorV1 *descriptor
) {
    memset(descriptor, 0, sizeof(*descriptor));
    descriptor->struct_size = (uint32_t)sizeof(*descriptor);
    descriptor->version = HHS_EXACT_PASS219_LANE5_CAPABILITY_SELF_MODEL_VERSION;
    descriptor->namespace_id = HHS_EXACT_PASS219_LANE5_CAPABILITY_SELF_MODEL_NAMESPACE;
    descriptor->total_entries = 2U;
    descriptor->public_entries = 1U;
    descriptor->native_entries = 1U;
    descriptor->restricted_entries = 0U;
    descriptor->canonical_boundary_entries = 1U;
    descriptor->public_catalog_signature64 = UINT64_C(0x3001);
    descriptor->native_export_signature64 = UINT64_C(0x3002);
    descriptor->dependency_signature64 = UINT64_C(0x3003);
    descriptor->model_signature64 = UINT64_C(0x3004);
    descriptor->entry_signature64[0] = UINT64_C(0x1000);
    descriptor->entry_signature64[1] = UINT64_C(0x2000);
    descriptor->source_kind[0] =
        HHS_EXACT_PASS219_LANE5_CAPABILITY_SOURCE_PUBLIC_REGISTRY;
    descriptor->source_kind[1] =
        HHS_EXACT_PASS219_LANE5_CAPABILITY_SOURCE_NATIVE_EXACT_ABI;
    descriptor->authority_class[0] =
        HHS_EXACT_PASS219_LANE5_CAPABILITY_AUTH_OBSERVATION;
    descriptor->authority_class[1] =
        HHS_EXACT_PASS219_LANE5_CAPABILITY_AUTH_CANONICAL_ADMISSION_BOUNDARY;
    descriptor->canonical_boundary_signature64 = descriptor->entry_signature64[1];
    descriptor->public_registry_complete = 1U;
    descriptor->native_exact_abi_complete = 1U;
    descriptor->ordered_unique_identity = 1U;
    descriptor->candidate_only = 1U;
    descriptor->canonical_vm81_mutation_authority = 0U;
    descriptor->canonical_hash72_authority = 0U;
    descriptor->canonical_hash216_authority = 0U;
    descriptor->canonical_persistence_authority = 0U;
    descriptor->pqc_key_authority = 0U;
    descriptor->receipt_clock_authority = 0U;
    descriptor->floating_point_canonical_authority = 0U;
    descriptor->requires_signed_environmental_vm81_admission = 1U;
}

static int bind_zero_witness(
    HHSExactPass219Lane5ZeroSumClosureWitnessV1 *witness,
    const HHSExactPass219Lane5MediationRequestV1 *request
) {
    memset(witness, 0, sizeof(*witness));
    witness->struct_size = (uint32_t)sizeof(*witness);
    witness->version = HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_VERSION;
    witness->namespace_id = HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_NAMESPACE;
    witness->request_signature64 = request->request_signature64;
    witness->candidate_signature64 = request->candidate_signature64;
    witness->parent_hash216_signature64 = request->parent_hash216_signature64;
    witness->rna_prepared_signature64 = request->rna_prepared_signature64;
    witness->rna_decision_signature64 = request->rna_decision_signature64;
    witness->capability_registry_signature64 =
        request->capability_registry_signature64;
    return hhs_exact_pass219_lane5_zero_sum_witness_seal(witness) ==
           HHS_EXACT_STATUS_OK;
}

int main(void) {
    HHSExactPass219Lane5MediationProofBindingAuthorityV1 authority;
    HHSExactPass219Hash216TransitionViewV1 parent;
    HHSExactPass219Hash216TransitionViewV1 refs[1];
    HHSExactUQCELInputV1 input;
    HHSExactVM81Frame frame;
    HHSExactPass219Holo4PreparedV1 prepared;
    HHSExactPass219Holo4DecisionV1 decision;
    HHSExactPass219Lane5CapabilitySelfModelDescriptorV1 capability_descriptor;
    HHSExactPass219Lane5CapabilitySelfModelReceiptV1 capability_receipt;
    HHSExactPass219Lane5MediationRequestV1 request;
    HHSExactPass219Lane5MediationReceiptV1 legacy_receipt;
    HHSExactPass219Lane5ZeroSumClosureWitnessV1 zero_witness;
    HHSExactPass219Lane5MediationProofBundleV1 proof;
    HHSExactPass219Lane5ProvenMediationReceiptV1 receipt;
    HHSExactVM81Frame tampered_frame;
    HHSExactPass219Hash216TransitionViewV1 tampered_ref;
    HHSExactPass219Lane5CapabilitySelfModelReceiptV1 tampered_capability;
    HHSExactPass219Holo4DecisionV1 tampered_decision;
    HHSExactPass219Lane5ZeroSumClosureWitnessV1 bad_zero;
    HHSExactPass219Lane5MediationRequestV1 bad_request;
    uint8_t one = 1U;
    uint64_t signature = 0U;
    uint64_t proven_signature = 0U;
    size_t i;

    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_mediation_proof_binding_version() ==
          HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_VERSION);
    CHECK(hhs_exact_pass219_lane5_mediation_proof_binding_authority(&authority) ==
          HHS_EXACT_STATUS_OK);
    CHECK(authority.legacy_1_34_proof_flags_authoritative == 0U);
    CHECK(authority.request_identity_recomputed == 1U);
    CHECK(authority.exact_vm5184_recomputed == 1U);
    CHECK(authority.rna_cpp_cell_wall_replayed == 1U);
    CHECK(authority.hash216_sha256_positions_verified == 1U);
    CHECK(authority.capability_registry_recomputed == 1U);
    CHECK(authority.exact_zero_sum_residual_vector_required == 1U);
    CHECK(authority.candidate_only == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);

    memset(&parent, 0, sizeof(parent));
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent) ==
          HHS_EXACT_STATUS_OK);
    refs[0] = parent;

    memset(&input, 0, sizeof(input));
    input.struct_size = (uint32_t)sizeof(input);
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.delta.struct_size = (uint32_t)sizeof(input.delta);
    input.delta.byte_length = 1U;
    input.delta.bytes_be = &one;

    memset(&frame, 0, sizeof(frame));
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        frame.words[i] = UINT64_C(0x9E3779B97F4A7C15) ^
                         ((uint64_t)i * UINT64_C(0x100000001B3));

    memset(&prepared, 0, sizeof(prepared));
    memset(&decision, 0, sizeof(decision));
    CHECK(hhs_exact_pass219_rna_vm5184_route(
              &input, &frame, &parent,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
              &prepared, &decision) == HHS_EXACT_STATUS_OK);

    make_capability_descriptor(&capability_descriptor);
    memset(&capability_receipt, 0, sizeof(capability_receipt));
    CHECK(hhs_exact_pass219_lane5_capability_self_model_validate(
              &capability_descriptor, &capability_receipt) == HHS_EXACT_STATUS_OK);

    memset(&request, 0, sizeof(request));
    request.struct_size = (uint32_t)sizeof(request);
    request.version = HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION;
    request.namespace_id = HHS_EXACT_PASS219_LANE5_NAMESPACE;
    request.hash216_reference_count = 1U;
    request.capability_reference_count = 2U;
    request.learning_stage = 7U;
    request.request_signature64 = UINT64_C(0x9101);
    CHECK(hhs_exact_pass219_lane5_mediation_frame_signature(
              &frame, &request.candidate_signature64) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_lane5_mediation_hash216_reference_signature(
              &parent, &request.parent_hash216_signature64) == HHS_EXACT_STATUS_OK);
    request.bigint_address_signature64 = UINT64_C(0x9104);
    request.hydration_signature64 = prepared.tensor_signature64;
    request.compression_signature64 = UINT64_C(0x9106);
    request.capability_registry_signature64 = capability_receipt.receipt_signature64;
    request.learning_iteration_signature64 = UINT64_C(0x9108);
    request.rna_prepared_signature64 = prepared.graph_signature64;
    request.rna_decision_signature64 = decision.decision_signature64;
    CHECK(hhs_exact_pass219_lane5_mediation_hash216_reference_signature(
              &refs[0], &request.hash216_reference_signature64[0]) ==
          HHS_EXACT_STATUS_OK);
    request.capability_reference_signature64[0] =
        capability_descriptor.entry_signature64[0];
    request.capability_reference_signature64[1] =
        capability_descriptor.entry_signature64[1];

    memset(&legacy_receipt, 0, sizeof(legacy_receipt));
    CHECK(hhs_exact_pass219_lane5_mediate_candidate(&request, &legacy_receipt) ==
          HHS_EXACT_STATUS_OK);
    CHECK(legacy_receipt.hash216_references_validated == 0U);
    CHECK(legacy_receipt.capability_registry_validated == 0U);
    CHECK(legacy_receipt.exact_vm5184_bound == 0U);
    CHECK(legacy_receipt.rna_cell_wall_bound == 0U);
    CHECK(legacy_receipt.zero_sum_closure_passed == 0U);

    CHECK(bind_zero_witness(&zero_witness, &request));

    memset(&proof, 0, sizeof(proof));
    proof.struct_size = (uint32_t)sizeof(proof);
    proof.version = HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_VERSION;
    proof.namespace_id = HHS_EXACT_PASS219_LANE5_MEDIATION_PROOF_BINDING_NAMESPACE;
    proof.hash216_reference_count = 1U;
    proof.feedback_lane = HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE;
    proof.feedback_trinary = 0;
    proof.input = &input;
    proof.candidate_frame = &frame;
    proof.parent_hash216_reference = &parent;
    proof.rna_prepared = &prepared;
    proof.rna_decision = &decision;
    proof.hash216_references = refs;
    proof.capability_descriptor = &capability_descriptor;
    proof.capability_receipt = &capability_receipt;
    proof.zero_sum_witness = &zero_witness;

    memset(&receipt, 0, sizeof(receipt));
    CHECK(hhs_exact_pass219_lane5_mediation_proof_bind(
              &request, &proof, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.request_recomputed == 1U);
    CHECK(receipt.exact_vm5184_bound == 1U);
    CHECK(receipt.rna_cell_wall_bound == 1U);
    CHECK(receipt.hash216_references_validated == 1U);
    CHECK(receipt.capability_registry_validated == 1U);
    CHECK(receipt.zero_sum_closure_passed == 1U);
    CHECK(receipt.all_proofs_bound == 1U);
    CHECK(receipt.candidate_only == 1U);
    CHECK(receipt.canonical_mutation_authority == 0U);
    CHECK(receipt.canonical_hash72_authority == 0U);
    CHECK(receipt.canonical_hash216_authority == 0U);
    CHECK(receipt.canonical_persistence_authority == 0U);
    CHECK(receipt.requires_environmental_admission == 1U);
    CHECK(receipt.proof_binding_signature64 != 0U);
    proven_signature = receipt.proof_binding_signature64;

    tampered_frame = frame;
    tampered_frame.words[7] ^= UINT64_C(1);
    proof.candidate_frame = &tampered_frame;
    CHECK(hhs_exact_pass219_lane5_mediation_proof_bind(
              &request, &proof, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    proof.candidate_frame = &frame;

    tampered_ref = refs[0];
    tampered_ref.transition_identity216[0] =
        tampered_ref.transition_identity216[0] == '0' ? '1' : '0';
    proof.hash216_references = &tampered_ref;
    CHECK(hhs_exact_pass219_lane5_mediation_proof_bind(
              &request, &proof, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    proof.hash216_references = refs;

    tampered_capability = capability_receipt;
    tampered_capability.receipt_signature64 ^= UINT64_C(1);
    proof.capability_receipt = &tampered_capability;
    CHECK(hhs_exact_pass219_lane5_mediation_proof_bind(
              &request, &proof, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    proof.capability_receipt = &capability_receipt;

    tampered_decision = decision;
    tampered_decision.selected_lane =
        (uint8_t)((tampered_decision.selected_lane + 1U) %
                  HHS_EXACT_PASS219_HOLO4_LANE_COUNT);
    proof.rna_decision = &tampered_decision;
    CHECK(hhs_exact_pass219_lane5_mediation_proof_bind(
              &request, &proof, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    proof.rna_decision = &decision;

    bad_request = request;
    bad_request.capability_reference_signature64[0] = UINT64_C(0x1999);
    CHECK(bind_zero_witness(&bad_zero, &bad_request));
    proof.zero_sum_witness = &bad_zero;
    CHECK(hhs_exact_pass219_lane5_mediation_proof_bind(
              &bad_request, &proof, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    bad_zero = zero_witness;
    bad_zero.state_change_residual = INT64_C(1);
    CHECK(hhs_exact_pass219_lane5_zero_sum_witness_seal(&bad_zero) ==
          HHS_EXACT_STATUS_OK);
    proof.zero_sum_witness = &bad_zero;
    CHECK(hhs_exact_pass219_lane5_mediation_proof_bind(
              &request, &proof, &receipt) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);

    bad_zero = zero_witness;
    bad_zero.witness_signature64 ^= UINT64_C(1);
    proof.zero_sum_witness = &bad_zero;
    CHECK(hhs_exact_pass219_lane5_mediation_proof_bind(
              &request, &proof, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    proof.zero_sum_witness = &zero_witness;

    CHECK(hhs_exact_pass219_lane5_mediation_hash216_reference_signature(
              &parent, &signature) == HHS_EXACT_STATUS_OK);
    CHECK(signature == request.parent_hash216_signature64);

    printf(
        "PASS219_LANE5_MEDIATION_PROOF_BINDING_1_49_PASS proof=%llu frame=%llu parent=%llu hash216=%llu capability=%llu zero=%llu\n",
        (unsigned long long)proven_signature,
        (unsigned long long)request.candidate_signature64,
        (unsigned long long)request.parent_hash216_signature64,
        (unsigned long long)request.hash216_reference_signature64[0],
        (unsigned long long)capability_receipt.receipt_signature64,
        (unsigned long long)zero_witness.witness_signature64);
    return 0;
}

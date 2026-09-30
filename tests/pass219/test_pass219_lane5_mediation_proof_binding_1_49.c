#include "hhs_pass219_lane5_mediation_proof_binding_1_49.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed: %s at %s:%d\n", #expr, __FILE__, __LINE__); \
        return 1; \
    } \
} while (0)

static const uint32_t GLOBAL_GATE_OFFSETS[
    HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT
] = {96U, 240U, 266U, 274U, 285U};

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

static HHSExactPass219Lane5DirectWitnessRouteV1 make_direct_route(
    const HHSExactPass219Lane5MediationRequestV1 *request
) {
    HHSExactPass219Lane5DirectWitnessRouteV1 route;
    memset(&route, 0, sizeof(route));
    route.struct_size = (uint32_t)sizeof(route);
    route.version = HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_ROUTING_VERSION;
    route.previous_signature64 = request->parent_hash216_signature64;
    route.current_signature64 = request->candidate_signature64;
    route.provenance_signature64 = request->request_signature64;
    route.goal_signature64 = request->candidate_signature64;
    route.forbidden_boundary_signature64 = UINT64_C(0xF00D);
    route.reciprocal_inverse_signature64 = UINT64_C(0xBEEF);
    route.candidate_signature64 = request->candidate_signature64;
    route.route_signature64 = UINT64_C(0x9001);
    route.represented_span = UINT64_C(5184);
    route.evidence_count = 5U;
    route.contradiction_check_count = 2U;
    route.integer_route_cost = UINT64_C(8);
    route.materialized_intermediate_states = 0U;
    route.phase_slot = 18U;
    route.inverse_phase_slot = 54U;
    route.trinary_collapse = 0;
    route.binary_collapse = 0U;
    route.nested_zero_slot = 1U;
    route.replay_witness_verified = 1U;
    route.exact_goal_reached = 1U;
    route.contradiction_free = 1U;
    route.goal_forbidden_conflict = 0U;
    route.reciprocal_phase_verified = 1U;
    route.bigint_serialization_addressed = 1U;
    route.candidate_only = 1U;
    route.requires_signed_environmental_vm81_admission = 1U;
    return route;
}

static int make_global_input(
    HHSExactPass219GlobalMembraneInputV1 *input,
    const HHSExactPass219Lane5MediationRequestV1 *request,
    const HHSExactPass219Lane5DirectWitnessReceiptV1 *direct_receipt
) {
    HHSExactPass219GlobalMembraneDescriptorV1 descriptor;
    uint32_t i;

    memset(&descriptor, 0, sizeof(descriptor));
    if (hhs_exact_pass219_global_membrane_descriptor(&descriptor) !=
        HHS_EXACT_STATUS_OK)
        return 0;

    memset(input, 0, sizeof(*input));
    input->struct_size = (uint32_t)sizeof(*input);
    input->version = hhs_exact_pass219_global_membrane_version();
    memcpy(input->combined_source_sha256,
           descriptor.combined_source_sha256,
           HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES);
    if (hhs_exact_pass219_lane5_mediation_environment_root(
            request,
            direct_receipt,
            input->global_symbol_environment_root) != HHS_EXACT_STATUS_OK)
        return 0;
    input->gate_count = HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT;
    input->global_symbol_environment_complete = 1U;
    input->cross_layer_revalidation_complete = 1U;
    input->local_symbol_shadowing_detected = 0U;

    for (i = 0U; i < HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT; ++i) {
        HHSExactPass219GlobalGateWitnessV1 *gate = &input->gates[i];
        gate->struct_size = (uint32_t)sizeof(*gate);
        gate->version = hhs_exact_pass219_global_membrane_version();
        gate->gate_index = i;
        gate->source_offset = GLOBAL_GATE_OFFSETS[i];
        gate->boolean_result = 1U;
        memcpy(gate->combined_source_sha256,
               descriptor.combined_source_sha256,
               HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES);
        memcpy(gate->global_symbol_environment_root,
               input->global_symbol_environment_root,
               HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES);
    }
    return 1;
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
    HHSExactPass219Lane5DirectWitnessRouteV1 direct_route;
    HHSExactPass219Lane5DirectWitnessReceiptV1 direct_receipt;
    HHSExactPass219GlobalMembraneInputV1 global_input;
    HHSExactPass219GlobalMembraneResultV1 global_result;
    HHSExactPass219Lane5MediationProofBundleV1 proof;
    HHSExactPass219Lane5ProvenMediationReceiptV1 receipt;
    HHSExactVM81Frame tampered_frame;
    HHSExactPass219Hash216TransitionViewV1 tampered_ref;
    HHSExactPass219Lane5CapabilitySelfModelReceiptV1 tampered_capability;
    HHSExactPass219Holo4DecisionV1 tampered_decision;
    HHSExactPass219Lane5DirectWitnessRouteV1 tampered_route;
    HHSExactPass219Lane5DirectWitnessReceiptV1 tampered_route_receipt;
    HHSExactPass219GlobalMembraneInputV1 rejected_global_input;
    HHSExactPass219GlobalMembraneResultV1 rejected_global_result;
    HHSExactPass219GlobalMembraneInputV1 substituted_global_input;
    HHSExactPass219GlobalMembraneResultV1 substituted_global_result;
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
    CHECK(authority.legacy_mediation_recomputed == 1U);
    CHECK(authority.exact_vm5184_recomputed == 1U);
    CHECK(authority.rna_cpp_cell_wall_replayed == 1U);
    CHECK(authority.hash216_sha256_positions_verified == 1U);
    CHECK(authority.capability_registry_recomputed == 1U);
    CHECK(authority.direct_witness_route_recomputed == 1U);
    CHECK(authority.global_constraint_membrane_recomputed == 1U);
    CHECK(authority.global_environment_request_bound == 1U);
    CHECK(authority.exact_zero_sum_residual_vector_derived == 1U);
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
    request.rna_prepared_signature64 = prepared.graph_signature64;
    request.rna_decision_signature64 = decision.decision_signature64;
    CHECK(hhs_exact_pass219_lane5_mediation_hash216_reference_signature(
              &refs[0], &request.hash216_reference_signature64[0]) ==
          HHS_EXACT_STATUS_OK);
    request.capability_reference_signature64[0] =
        capability_descriptor.entry_signature64[0];
    request.capability_reference_signature64[1] =
        capability_descriptor.entry_signature64[1];

    direct_route = make_direct_route(&request);
    memset(&direct_receipt, 0, sizeof(direct_receipt));
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_validate(
              &direct_route, &direct_receipt) == HHS_EXACT_STATUS_OK);
    request.learning_iteration_signature64 = direct_receipt.route_receipt_signature64;

    CHECK(make_global_input(&global_input, &request, &direct_receipt));
    memset(&global_result, 0, sizeof(global_result));
    CHECK(hhs_exact_pass219_global_membrane_evaluate(
              &global_input, &global_result) == HHS_EXACT_STATUS_OK);
    CHECK(global_result.decision == HHS_EXACT_PASS219_GLOBAL_MEMBRANE_PROPAGATE);

    memset(&legacy_receipt, 0, sizeof(legacy_receipt));
    CHECK(hhs_exact_pass219_lane5_mediate_candidate(&request, &legacy_receipt) ==
          HHS_EXACT_STATUS_OK);
    CHECK(legacy_receipt.hash216_references_validated == 0U);
    CHECK(legacy_receipt.capability_registry_validated == 0U);
    CHECK(legacy_receipt.exact_vm5184_bound == 0U);
    CHECK(legacy_receipt.rna_cell_wall_bound == 0U);
    CHECK(legacy_receipt.zero_sum_closure_passed == 0U);

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
    proof.direct_witness_route = &direct_route;
    proof.direct_witness_receipt = &direct_receipt;
    proof.global_membrane_input = &global_input;
    proof.global_membrane_result = &global_result;

    memset(&receipt, 0, sizeof(receipt));
    CHECK(hhs_exact_pass219_lane5_mediation_proof_bind(
              &request, &proof, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.legacy_mediation_recomputed == 1U);
    CHECK(receipt.exact_vm5184_bound == 1U);
    CHECK(receipt.rna_cell_wall_bound == 1U);
    CHECK(receipt.hash216_references_validated == 1U);
    CHECK(receipt.capability_registry_validated == 1U);
    CHECK(receipt.direct_witness_route_validated == 1U);
    CHECK(receipt.global_constraint_membrane_validated == 1U);
    CHECK(receipt.zero_sum_closure_passed == 1U);
    CHECK(receipt.all_proofs_bound == 1U);
    CHECK(receipt.zero_sum_witness.state_change_residual == 0);
    CHECK(receipt.zero_sum_witness.dependency_change_residual == 0);
    CHECK(receipt.zero_sum_witness.phase_change_residual == 0);
    CHECK(receipt.zero_sum_witness.resource_work_residual == 0);
    CHECK(receipt.zero_sum_witness.lineage_residual == 0);
    CHECK(receipt.zero_sum_witness.inverse_recovery_residual == 0);
    CHECK(receipt.zero_sum_witness.local_constraint_residual == 0);
    CHECK(receipt.zero_sum_witness.global_constraint_residual == 0);
    CHECK(receipt.zero_sum_witness.witness_signature64 != 0U);
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
    CHECK(hhs_exact_pass219_lane5_mediation_proof_bind(
              &bad_request, &proof, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered_route = direct_route;
    tampered_route.current_signature64 ^= UINT64_C(1);
    memset(&tampered_route_receipt, 0, sizeof(tampered_route_receipt));
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_validate(
              &tampered_route, &tampered_route_receipt) == HHS_EXACT_STATUS_OK);
    proof.direct_witness_route = &tampered_route;
    proof.direct_witness_receipt = &tampered_route_receipt;
    CHECK(hhs_exact_pass219_lane5_mediation_proof_bind(
              &request, &proof, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    proof.direct_witness_route = &direct_route;
    proof.direct_witness_receipt = &direct_receipt;

    rejected_global_input = global_input;
    rejected_global_input.gates[2].boolean_result = 0U;
    memset(&rejected_global_result, 0, sizeof(rejected_global_result));
    CHECK(hhs_exact_pass219_global_membrane_evaluate(
              &rejected_global_input, &rejected_global_result) == HHS_EXACT_STATUS_OK);
    CHECK(rejected_global_result.decision == HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REJECT);
    proof.global_membrane_input = &rejected_global_input;
    proof.global_membrane_result = &rejected_global_result;
    CHECK(hhs_exact_pass219_lane5_mediation_proof_bind(
              &request, &proof, &receipt) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    proof.global_membrane_input = &global_input;
    proof.global_membrane_result = &global_result;

    substituted_global_input = global_input;
    substituted_global_input.global_symbol_environment_root[0] ^= UINT8_C(1);
    for (i = 0U; i < HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT; ++i)
        memcpy(
            substituted_global_input.gates[i].global_symbol_environment_root,
            substituted_global_input.global_symbol_environment_root,
            HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES);
    memset(&substituted_global_result, 0, sizeof(substituted_global_result));
    CHECK(hhs_exact_pass219_global_membrane_evaluate(
              &substituted_global_input, &substituted_global_result) == HHS_EXACT_STATUS_OK);
    CHECK(substituted_global_result.decision ==
          HHS_EXACT_PASS219_GLOBAL_MEMBRANE_PROPAGATE);
    proof.global_membrane_input = &substituted_global_input;
    proof.global_membrane_result = &substituted_global_result;
    CHECK(hhs_exact_pass219_lane5_mediation_proof_bind(
              &request, &proof, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    proof.global_membrane_input = &global_input;
    proof.global_membrane_result = &global_result;

    CHECK(hhs_exact_pass219_lane5_mediation_proof_bind(
              &request, &proof, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.zero_sum_witness.state_change_residual == 0);
    CHECK(receipt.zero_sum_witness.global_constraint_residual == 0);

    CHECK(hhs_exact_pass219_lane5_mediation_hash216_reference_signature(
              &parent, &signature) == HHS_EXACT_STATUS_OK);
    CHECK(signature == request.parent_hash216_signature64);

    printf(
        "PASS219_LANE5_MEDIATION_PROOF_BINDING_1_49_PASS proof=%llu frame=%llu parent=%llu hash216=%llu capability=%llu route=%llu global=%llu zero=%llu\n",
        (unsigned long long)proven_signature,
        (unsigned long long)request.candidate_signature64,
        (unsigned long long)request.parent_hash216_signature64,
        (unsigned long long)request.hash216_reference_signature64[0],
        (unsigned long long)capability_receipt.receipt_signature64,
        (unsigned long long)direct_receipt.route_receipt_signature64,
        (unsigned long long)receipt.global_membrane_signature64,
        (unsigned long long)receipt.zero_sum_witness.witness_signature64);
    return 0;
}

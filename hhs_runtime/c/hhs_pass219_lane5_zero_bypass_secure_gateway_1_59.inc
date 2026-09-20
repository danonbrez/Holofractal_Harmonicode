#include "../include/hhs_pass219_lane5_zero_bypass_secure_gateway_1_59.h"

#include <string.h>

uint32_t hhs_exact_pass219_lane5_zero_bypass_gateway_version(void) {
    return HHS_EXACT_PASS219_LANE5_ZERO_BYPASS_GATEWAY_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_zero_bypass_gateway_descriptor(
    HHSExactPass219Lane5ZeroBypassGatewayDescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = HHS_EXACT_PASS219_LANE5_ZERO_BYPASS_GATEWAY_VERSION;
    out_descriptor->frame_bytes = HHS_EXACT_VM81_FRAME_BYTES;
    out_descriptor->frame_bits = HHS_EXACT_VM81_FRAME_BITS;
    out_descriptor->vm81_cells = HHS_EXACT_VM81_CELLS;
    out_descriptor->local_constructor_states = HHS_EXACT_PHASE_PAIR_COUNT;
    out_descriptor->hydration_lanes = HHS_EXACT_PASS219_HOLO4_LANE_COUNT;
    out_descriptor->phase_modulus = HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS;

    out_descriptor->single_public_mutation_gateway = 1U;
    out_descriptor->linux_api_redirect_required = 1U;
    out_descriptor->raw_x86_ingress_allowed = 1U;
    out_descriptor->ieee754_payload_passthrough_allowed = 1U;
    out_descriptor->arbitrary_byte_payload_passthrough_allowed = 1U;
    out_descriptor->parametric_payload_identity = 1U;
    out_descriptor->order_preservation = 1U;
    out_descriptor->concatenation_preservation = 1U;
    out_descriptor->metadata_preservation_required = 1U;

    out_descriptor->cpp_rna_cell_wall_required = 1U;
    out_descriptor->lane5_bios_required = 1U;
    out_descriptor->pqc_environmental_firewall_required = 1U;
    out_descriptor->four_lane_hydration_required = 1U;
    out_descriptor->constraint_forced_execution = 1U;
    out_descriptor->policy_choice_authority = 0U;
    out_descriptor->hash216_composition_compute_fabric = 1U;
    out_descriptor->validated_scoped_reuse_only = 1U;
    out_descriptor->hash216_memory_carries_forward = 1U;

    out_descriptor->raw_transport_is_canonical_authority = 0U;
    out_descriptor->floating_point_canonical_authority = 0U;
    out_descriptor->host_instruction_execution_authority = 0U;
    out_descriptor->hash216_cache_commit_bypass_allowed = 0U;
    out_descriptor->legacy_direct_runtime_bypass_allowed = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_zero_bypass_gateway_validate(void) {
    HHSExactPass219Lane5ZeroBypassGatewayDescriptorV1 d;
    HHSExactPass219Lane5VirtualBIOSDescriptorV1 bios;
    HHSExactPass219Lane5CompositionJumpAuthorityV1 jump;
    HHSExactPass219Lane5AutomaticRoutingAuthorityV1 automatic;
    HHSExactPass219Lane5DirectWitnessAuthorityV1 direct;
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 unbounded;
    HHSExactStatus status;

    status = hhs_exact_pass219_lane5_zero_bypass_gateway_descriptor(&d);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (d.single_public_mutation_gateway != 1U ||
        d.linux_api_redirect_required != 1U ||
        d.raw_x86_ingress_allowed != 1U ||
        d.ieee754_payload_passthrough_allowed != 1U ||
        d.arbitrary_byte_payload_passthrough_allowed != 1U ||
        d.parametric_payload_identity != 1U ||
        d.order_preservation != 1U ||
        d.concatenation_preservation != 1U ||
        d.metadata_preservation_required != 1U ||
        d.cpp_rna_cell_wall_required != 1U ||
        d.lane5_bios_required != 1U ||
        d.pqc_environmental_firewall_required != 1U ||
        d.four_lane_hydration_required != 1U ||
        d.constraint_forced_execution != 1U ||
        d.policy_choice_authority != 0U ||
        d.hash216_composition_compute_fabric != 1U ||
        d.validated_scoped_reuse_only != 1U ||
        d.hash216_memory_carries_forward != 1U ||
        d.raw_transport_is_canonical_authority != 0U ||
        d.floating_point_canonical_authority != 0U ||
        d.host_instruction_execution_authority != 0U ||
        d.hash216_cache_commit_bypass_allowed != 0U ||
        d.legacy_direct_runtime_bypass_allowed != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_lane5_virtual_bios_validate();
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_lane5_virtual_bios_descriptor(&bios);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (bios.resident_vm_bios != 1U ||
        bios.control_plane_only != 1U ||
        bios.payload_dataflow_stage != 0U ||
        bios.payload_format_translation != 0U ||
        bios.cpp_rna_cell_wall_bound != 1U ||
        bios.pqc_firewall_bound != 1U ||
        bios.four_lane_hydration_bound != 1U ||
        bios.candidate_optimization_only != 1U ||
        bios.hash72_commit_bypass_allowed != 0U ||
        bios.hash216_cache_commit_bypass_allowed != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_lane5_composition_jump_authority(&jump);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (jump.validated_hash216_jump_store != 1U ||
        jump.exact_registration_replay_required != 1U ||
        jump.direct_candidate_reuse_allowed != 1U ||
        jump.canonical_vm81_mutation_authority != 0U ||
        jump.canonical_hash72_authority != 0U ||
        jump.canonical_hash216_authority != 0U ||
        jump.requires_signed_environmental_vm81_admission != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_lane5_automatic_superedge_routing_authority(&automatic);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (automatic.exact_hash216_adjacency_required != 1U ||
        automatic.exact_target_closure_required != 1U ||
        automatic.candidate_only != 1U ||
        automatic.canonical_vm81_mutation_authority != 0U ||
        automatic.requires_signed_environmental_vm81_admission != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_lane5_direct_witness_routing_authority(&direct);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (direct.previous_current_witness_bound != 1U ||
        direct.goal_bound != 1U ||
        direct.contradiction_boundary_bound != 1U ||
        direct.candidate_only != 1U ||
        direct.canonical_vm81_mutation_authority != 0U ||
        direct.requires_signed_environmental_vm81_admission != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_lane5_unbounded_workload_scaling_authority(&unbounded);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (unbounded.any_byte_serializable_workload != 1U ||
        unbounded.workload_class_agnostic != 1U ||
        unbounded.provenance_bound != 1U ||
        unbounded.candidate_only != 1U ||
        unbounded.canonical_vm81_mutation_authority != 0U ||
        unbounded.requires_signed_environmental_vm81_admission != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_payload_roundtrip_exact(
    const uint8_t *input,
    size_t length,
    uint8_t *output,
    size_t capacity,
    size_t *out_length
) {
    HHSExactStatus status;
    if (out_length != NULL)
        *out_length = length;
    if ((length != 0U && input == NULL) || (length != 0U && output == NULL))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (capacity < length)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;

    status = hhs_x86_64_bytecode_copy_exact(
        input, length, output, capacity, out_length);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (length != 0U && memcmp(input, output, length) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_gateway_admit_raw5184(
    uint32_t pass_number,
    uint32_t signature_algorithm,
    const HHSExactUQCELInputV1 *input,
    const uint8_t *raw_payload,
    size_t raw_length,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    int8_t lo_shu_group,
    uint16_t g243,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    uint8_t *out_committed_raw,
    size_t out_capacity,
    size_t *out_length,
    HHSExactPass219RNAAdmissionV1 *out_admission,
    HHSExactPass219VM81PQCFirewallReceiptV1 *out_firewall_receipt,
    HHSExactPass219VM81PQCSignatureReceiptV1 *out_signature_receipt,
    HHSExactPass219VM81EnvironmentReceiptV1 *out_environment_receipt,
    HHSExactPass219Lane5ZeroBypassGatewayReceiptV1 *out_gateway_receipt
) {
    uint8_t staged_raw[HHS_EXACT_VM81_FRAME_BYTES];
    HHSExactVM81Frame candidate;
    HHSExactVM81Frame committed;
    HHSExactStatus status;
    size_t copied = 0U;
    size_t written = 0U;

    if (out_length != NULL)
        *out_length = HHS_EXACT_VM81_FRAME_BYTES;
    if (out_gateway_receipt != NULL)
        memset(out_gateway_receipt, 0, sizeof(*out_gateway_receipt));
    if (out_committed_raw == NULL || out_admission == NULL ||
        out_firewall_receipt == NULL || out_signature_receipt == NULL ||
        out_environment_receipt == NULL || out_gateway_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_committed_raw, 0, out_capacity);
    memset(out_admission, 0, sizeof(*out_admission));
    memset(out_firewall_receipt, 0, sizeof(*out_firewall_receipt));
    memset(out_signature_receipt, 0, sizeof(*out_signature_receipt));
    memset(out_environment_receipt, 0, sizeof(*out_environment_receipt));

    if (input == NULL || raw_payload == NULL || parent_hash216_reference == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (raw_length != HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (out_capacity < HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;

    status = hhs_exact_pass219_lane5_zero_bypass_gateway_validate();
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219_lane5_payload_roundtrip_exact(
        raw_payload, raw_length,
        staged_raw, sizeof(staged_raw), &copied);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (copied != raw_length || memcmp(raw_payload, staged_raw, raw_length) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_vm81_frame_import_le(staged_raw, copied, &candidate);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(&committed, 0, sizeof(committed));
    status = hhs_exact_pass219_vm81_environment_admit_signed_internal(
        pass_number,
        signature_algorithm,
        input,
        &candidate,
        parent_hash216_reference,
        lo_shu_group,
        g243,
        feedback_lane,
        feedback_trinary,
        &committed,
        out_admission,
        out_firewall_receipt,
        out_signature_receipt,
        out_environment_receipt
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_vm81_frame_export_le(
        &committed, out_committed_raw, out_capacity, &written);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (written != HHS_EXACT_VM81_FRAME_BYTES ||
        memcmp(out_committed_raw, raw_payload, written) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (out_length != NULL)
        *out_length = written;

    out_gateway_receipt->struct_size = (uint32_t)sizeof(*out_gateway_receipt);
    out_gateway_receipt->version = HHS_EXACT_PASS219_LANE5_ZERO_BYPASS_GATEWAY_VERSION;
    out_gateway_receipt->input_bytes = (uint32_t)raw_length;
    out_gateway_receipt->output_bytes = (uint32_t)written;
    out_gateway_receipt->instruction_sequence = out_firewall_receipt->instruction_sequence;
    out_gateway_receipt->environment_witness_sequence = out_environment_receipt->witness_sequence;
    out_gateway_receipt->payload_identity_verified = 1U;
    out_gateway_receipt->lane5_bios_validated = 1U;
    out_gateway_receipt->cpp_rna_cell_wall_routed = out_firewall_receipt->rna_cell_wall_routed;
    out_gateway_receipt->pqc_authenticated = out_firewall_receipt->pqc_authenticated;
    out_gateway_receipt->pqc_signature_verified =
        out_signature_receipt->decision == HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERIFIED ? 1U : 0U;
    out_gateway_receipt->environmental_witness_verified =
        out_environment_receipt->environment_signature_verified;
    out_gateway_receipt->parent_hash216_verified = out_firewall_receipt->parent_hash216_verified;
    out_gateway_receipt->child_hash216_verified = out_firewall_receipt->child_hash216_verified;
    out_gateway_receipt->vm81_canonical_commit_observed =
        out_firewall_receipt->decision == HHS_EXACT_PASS219_VM81_PQC_DECISION_COMMITTED ? 1U : 0U;
    out_gateway_receipt->hash216_continuation_eligible =
        (uint8_t)(out_gateway_receipt->vm81_canonical_commit_observed &&
                  out_gateway_receipt->parent_hash216_verified &&
                  out_gateway_receipt->child_hash216_verified);
    out_gateway_receipt->selected_lane = out_firewall_receipt->selected_lane;
    out_gateway_receipt->canonical_authority_owned_by_gateway = 0U;
    out_gateway_receipt->raw_transport_is_canonical_authority = 0U;
    out_gateway_receipt->floating_point_canonical_authority = 0U;
    out_gateway_receipt->host_instruction_execution_authority = 0U;

    if (out_gateway_receipt->cpp_rna_cell_wall_routed != 1U ||
        out_gateway_receipt->pqc_authenticated != 1U ||
        out_gateway_receipt->pqc_signature_verified != 1U ||
        out_gateway_receipt->environmental_witness_verified != 1U ||
        out_gateway_receipt->parent_hash216_verified != 1U ||
        out_gateway_receipt->child_hash216_verified != 1U ||
        out_gateway_receipt->vm81_canonical_commit_observed != 1U ||
        out_gateway_receipt->hash216_continuation_eligible != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}


HHSExactStatus hhs_exact_pass219_vm81_environment_admit_signed(
    uint32_t pass_number,
    uint32_t signature_algorithm,
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    int8_t lo_shu_group,
    uint16_t g243,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactVM81Frame *out_committed_frame,
    HHSExactPass219RNAAdmissionV1 *out_admission,
    HHSExactPass219VM81PQCFirewallReceiptV1 *out_firewall_receipt,
    HHSExactPass219VM81PQCSignatureReceiptV1 *out_signature_receipt,
    HHSExactPass219VM81EnvironmentReceiptV1 *out_environment_receipt
) {
    uint8_t raw[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t committed_raw[HHS_EXACT_VM81_FRAME_BYTES];
    size_t raw_length = 0U;
    size_t committed_length = 0U;
    HHSExactPass219Lane5ZeroBypassGatewayReceiptV1 gateway_receipt;
    HHSExactStatus status;

    if (candidate_frame == NULL || out_committed_frame == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_committed_frame, 0, sizeof(*out_committed_frame));
    memset(&gateway_receipt, 0, sizeof(gateway_receipt));

    status = hhs_exact_vm81_frame_export_le(
        candidate_frame, raw, sizeof(raw), &raw_length);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219_lane5_gateway_admit_raw5184(
        pass_number,
        signature_algorithm,
        input,
        raw,
        raw_length,
        parent_hash216_reference,
        lo_shu_group,
        g243,
        feedback_lane,
        feedback_trinary,
        committed_raw,
        sizeof(committed_raw),
        &committed_length,
        out_admission,
        out_firewall_receipt,
        out_signature_receipt,
        out_environment_receipt,
        &gateway_receipt
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return hhs_exact_vm81_frame_import_le(
        committed_raw, committed_length, out_committed_frame);
}

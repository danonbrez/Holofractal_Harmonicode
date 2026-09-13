#include "../include/hhs_pass219_rlm20_lane5_internal_state_closure_1_37.h"

#include <string.h>

static const uint8_t HHS_P219_RLM20_LANE5_RUNTIME_DOMAIN[] =
    "HHS-P219-RLM20-LANE5-INTERNAL-STATE-CLOSURE-V1";
static const uint8_t HHS_P219_RLM20_CAPABILITY_DOMAIN[] =
    "HHS-P219-LANE5-RUNTIME-ABI-CAPABILITY-V1";
static const uint8_t HHS_P219_RLM20_COMPRESSION_DOMAIN[] =
    "HHS-P219-H36-COMPRESSION-IDENTITY-PRESERVED-V1";

static uint64_t hhs_p219_rlm20_fnv_bytes(
    uint64_t hash,
    const uint8_t *bytes,
    size_t length
) {
    size_t i;
    if (bytes == NULL)
        return UINT64_C(0);
    for (i = 0U; i < length; ++i) {
        hash ^= (uint64_t)bytes[i];
        hash *= UINT64_C(1099511628211);
    }
    return hash;
}

static uint64_t hhs_p219_rlm20_mix_u64(uint64_t hash, uint64_t value) {
    unsigned shift;
    for (shift = 0U; shift < 64U; shift += 8U) {
        hash ^= (value >> shift) & UINT64_C(0xff);
        hash *= UINT64_C(1099511628211);
    }
    return hash;
}

static uint64_t hhs_p219_rlm20_nonzero(uint64_t value, uint64_t fallback) {
    return value == UINT64_C(0) ? fallback : value;
}

static int hhs_p219_rlm20_lane5_receipt_is_closed(
    const HHSExactPass219Lane5MediationReceiptV1 *receipt
) {
    return receipt != NULL &&
           receipt->struct_size == (uint32_t)sizeof(*receipt) &&
           receipt->version == HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION &&
           receipt->namespace_id == HHS_EXACT_PASS219_LANE5_NAMESPACE &&
           receipt->decision == HHS_EXACT_PASS219_LANE5_DECISION_CANDIDATE_READY &&
           receipt->hash216_references_validated == 1U &&
           receipt->capability_registry_validated == 1U &&
           receipt->exact_vm5184_bound == 1U &&
           receipt->rna_cell_wall_bound == 1U &&
           receipt->zero_sum_closure_passed == 1U &&
           receipt->candidate_only == 1U &&
           receipt->canonical_mutation_authority == 0U &&
           receipt->canonical_hash72_authority == 0U &&
           receipt->canonical_hash216_authority == 0U &&
           receipt->canonical_persistence_authority == 0U &&
           receipt->requires_environmental_admission == 1U &&
           receipt->closure_signature64 != UINT64_C(0) &&
           receipt->mediation_signature64 != UINT64_C(0);
}

uint32_t hhs_exact_pass219_rlm20_lane5_closure_version(void) {
    return HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_VERSION;
}

HHSExactStatus hhs_exact_pass219_rlm20_lane5_closure_authority(
    HHSExactPass219RLM20Lane5ClosureAuthorityV1 *out_authority
) {
    HHSExactPass219RLM20Lane5ClosureAuthorityV1 authority;
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&authority, 0, sizeof(authority));
    authority.struct_size = (uint32_t)sizeof(authority);
    authority.version = HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_VERSION;
    authority.pass219_specification_contracts = 1U;
    authority.lane5_implementation_logic = 1U;
    authority.lane5_inside_rna_cpp_cellular_nucleus_abi = 1U;
    authority.lane5_outside_pqc_canonical_firewall = 1U;
    authority.all_state_affecting_runtime_calls_mediated = 1U;
    authority.environment_independent_vm = 1U;
    authority.environment_hardware_bytecode_interception_required = 0U;
    authority.canonical_state_closed_under_hhs_constraints = 1U;
    authority.successor_preserves_pass219_type_invariants = 1U;
    authority.four_lane_modality_preserved = 1U;
    authority.h36_global_compilation_inherited = 1U;
    authority.rlm20_extends_lane5_kernel = 1U;
    authority.rlm20_candidate_only = 1U;
    authority.inherited_equations_unchanged = 1U;
    authority.inherited_dataflow_unchanged = 1U;
    authority.canonical_vm81_mutation_authority = 0U;
    authority.canonical_hash72_authority = 0U;
    authority.canonical_hash216_authority = 0U;
    authority.canonical_persistence_authority = 0U;
    authority.pqc_key_authority = 0U;
    authority.receipt_clock_authority = 0U;
    authority.floating_point_canonical_authority = 0U;
    authority.requires_rna_cpp_cell_wall = 1U;
    authority.requires_lane5_mediation = 1U;
    authority.requires_signed_environmental_vm81_admission = 1U;
    *out_authority = authority;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_runtime_preflight(
    uint32_t pass_number,
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    int8_t lo_shu_group,
    uint16_t g243,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219RLM20Lane5ClosureReceiptV1 *out_receipt
) {
    HHSExactPass219Holo4PreparedV1 prepared;
    HHSExactPass219Holo4DecisionV1 decision;
    HHSExactPass219Lane5MediationRequestV1 request;
    HHSExactPass219Lane5MediationReceiptV1 mediation;
    uint8_t frame_bytes[HHS_EXACT_VM81_FRAME_BYTES];
    size_t frame_length = 0U;
    uint64_t request_signature = UINT64_C(1469598103934665603);
    uint64_t candidate_signature = UINT64_C(1469598103934665603);
    uint64_t parent_signature = UINT64_C(1469598103934665603);
    uint64_t capability_signature = UINT64_C(1469598103934665603);
    uint64_t compression_signature = UINT64_C(1469598103934665603);
    uint64_t hydration_signature;
    uint64_t prepared_signature;
    uint64_t decision_signature;
    uint64_t bigint_signature;
    uint64_t learning_signature;
    HHSExactStatus status;

    if (out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = (uint32_t)sizeof(*out_receipt);
    out_receipt->version = HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_VERSION;
    out_receipt->pass_number = pass_number;
    out_receipt->learning_stage = HHS_EXACT_PASS219_RLM20_STAGE;
    out_receipt->feedback_lane = feedback_lane;
    out_receipt->feedback_trinary = feedback_trinary;
    out_receipt->lo_shu_group = lo_shu_group;
    out_receipt->g243 = g243;
    out_receipt->environment_hardware_bytecode_intercepted = 0U;

    if (input == NULL || candidate_frame == NULL || parent_hash216_reference == NULL) {
        out_receipt->decision = HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_REJECTED;
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }

    memset(&prepared, 0, sizeof(prepared));
    memset(&decision, 0, sizeof(decision));
    status = hhs_exact_pass219_rna_vm5184_route(
        input,
        candidate_frame,
        parent_hash216_reference,
        feedback_lane,
        feedback_trinary,
        &prepared,
        &decision);
    if (status != HHS_EXACT_STATUS_OK) {
        out_receipt->decision = HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_REJECTED;
        return status;
    }

    status = hhs_exact_vm81_frame_export_le(
        candidate_frame, frame_bytes, sizeof(frame_bytes), &frame_length);
    if (status != HHS_EXACT_STATUS_OK || frame_length != sizeof(frame_bytes)) {
        out_receipt->decision = HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    candidate_signature = hhs_p219_rlm20_fnv_bytes(
        candidate_signature, frame_bytes, sizeof(frame_bytes));
    parent_signature = hhs_p219_rlm20_fnv_bytes(
        parent_signature,
        (const uint8_t *)parent_hash216_reference->transition_identity216,
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    capability_signature = hhs_p219_rlm20_fnv_bytes(
        capability_signature,
        HHS_P219_RLM20_CAPABILITY_DOMAIN,
        sizeof(HHS_P219_RLM20_CAPABILITY_DOMAIN) - 1U);
    capability_signature = hhs_p219_rlm20_mix_u64(capability_signature, pass_number);
    compression_signature = hhs_p219_rlm20_fnv_bytes(
        compression_signature,
        HHS_P219_RLM20_COMPRESSION_DOMAIN,
        sizeof(HHS_P219_RLM20_COMPRESSION_DOMAIN) - 1U);
    compression_signature = hhs_p219_rlm20_mix_u64(
        compression_signature, candidate_signature);

    prepared_signature = UINT64_C(1469598103934665603);
    prepared_signature = hhs_p219_rlm20_mix_u64(prepared_signature, prepared.graph_signature64);
    prepared_signature = hhs_p219_rlm20_mix_u64(prepared_signature, prepared.tensor_signature64);
    decision_signature = hhs_p219_rlm20_nonzero(
        decision.decision_signature64, UINT64_C(0x2192000000000001));
    hydration_signature = UINT64_C(1469598103934665603);
    hydration_signature = hhs_p219_rlm20_mix_u64(hydration_signature, prepared_signature);
    hydration_signature = hhs_p219_rlm20_mix_u64(hydration_signature, decision_signature);
    hydration_signature = hhs_p219_rlm20_mix_u64(hydration_signature, decision.selected_lane);

    bigint_signature = UINT64_C(1469598103934665603);
    bigint_signature = hhs_p219_rlm20_mix_u64(bigint_signature, candidate_signature);
    bigint_signature = hhs_p219_rlm20_mix_u64(bigint_signature, UINT64_C(5184));
    bigint_signature = hhs_p219_rlm20_mix_u64(
        bigint_signature, HHS_EXACT_PASS219_LANE5_NAMESPACE);

    learning_signature = UINT64_C(1469598103934665603);
    learning_signature = hhs_p219_rlm20_fnv_bytes(
        learning_signature,
        HHS_P219_RLM20_LANE5_RUNTIME_DOMAIN,
        sizeof(HHS_P219_RLM20_LANE5_RUNTIME_DOMAIN) - 1U);
    learning_signature = hhs_p219_rlm20_mix_u64(
        learning_signature, HHS_EXACT_PASS219_RLM20_STAGE);
    learning_signature = hhs_p219_rlm20_mix_u64(learning_signature, candidate_signature);
    learning_signature = hhs_p219_rlm20_mix_u64(learning_signature, parent_signature);

    request_signature = hhs_p219_rlm20_fnv_bytes(
        request_signature,
        HHS_P219_RLM20_LANE5_RUNTIME_DOMAIN,
        sizeof(HHS_P219_RLM20_LANE5_RUNTIME_DOMAIN) - 1U);
    request_signature = hhs_p219_rlm20_mix_u64(request_signature, pass_number);
    request_signature = hhs_p219_rlm20_mix_u64(
        request_signature, (uint64_t)(uint8_t)lo_shu_group);
    request_signature = hhs_p219_rlm20_mix_u64(request_signature, g243);
    request_signature = hhs_p219_rlm20_mix_u64(request_signature, feedback_lane);
    request_signature = hhs_p219_rlm20_mix_u64(
        request_signature, (uint64_t)(uint8_t)feedback_trinary);
    request_signature = hhs_p219_rlm20_mix_u64(request_signature, candidate_signature);
    request_signature = hhs_p219_rlm20_mix_u64(request_signature, parent_signature);

    candidate_signature = hhs_p219_rlm20_nonzero(
        candidate_signature, UINT64_C(0x2192000000000002));
    parent_signature = hhs_p219_rlm20_nonzero(
        parent_signature, UINT64_C(0x2192000000000003));
    capability_signature = hhs_p219_rlm20_nonzero(
        capability_signature, UINT64_C(0x2192000000000004));
    compression_signature = hhs_p219_rlm20_nonzero(
        compression_signature, UINT64_C(0x2192000000000005));
    prepared_signature = hhs_p219_rlm20_nonzero(
        prepared_signature, UINT64_C(0x2192000000000006));
    hydration_signature = hhs_p219_rlm20_nonzero(
        hydration_signature, UINT64_C(0x2192000000000007));
    bigint_signature = hhs_p219_rlm20_nonzero(
        bigint_signature, UINT64_C(0x2192000000000008));
    learning_signature = hhs_p219_rlm20_nonzero(
        learning_signature, UINT64_C(0x2192000000000009));
    request_signature = hhs_p219_rlm20_nonzero(
        request_signature, UINT64_C(0x219200000000000a));

    memset(&request, 0, sizeof(request));
    request.struct_size = (uint32_t)sizeof(request);
    request.version = HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION;
    request.namespace_id = HHS_EXACT_PASS219_LANE5_NAMESPACE;
    request.hash216_reference_count = 1U;
    request.capability_reference_count = 1U;
    request.learning_stage = HHS_EXACT_PASS219_RLM20_STAGE;
    request.request_signature64 = request_signature;
    request.candidate_signature64 = candidate_signature;
    request.parent_hash216_signature64 = parent_signature;
    request.bigint_address_signature64 = bigint_signature;
    request.hydration_signature64 = hydration_signature;
    request.compression_signature64 = compression_signature;
    request.capability_registry_signature64 = capability_signature;
    request.learning_iteration_signature64 = learning_signature;
    request.rna_prepared_signature64 = prepared_signature;
    request.rna_decision_signature64 = decision_signature;
    request.hash216_reference_signature64[0] = parent_signature;
    request.capability_reference_signature64[0] = capability_signature;

    memset(&mediation, 0, sizeof(mediation));
    status = hhs_exact_pass219_lane5_mediate_candidate(&request, &mediation);
    if (status != HHS_EXACT_STATUS_OK ||
        !hhs_p219_rlm20_lane5_receipt_is_closed(&mediation)) {
        out_receipt->decision = HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_REJECTED;
        return status == HHS_EXACT_STATUS_OK
            ? HHS_EXACT_STATUS_INVARIANT_FAILURE
            : status;
    }

    out_receipt->decision = HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_CANDIDATE_READY;
    out_receipt->selected_lane = decision.selected_lane;
    out_receipt->request_signature64 = request_signature;
    out_receipt->candidate_signature64 = candidate_signature;
    out_receipt->parent_hash216_signature64 = parent_signature;
    out_receipt->hydration_signature64 = hydration_signature;
    out_receipt->rna_prepared_signature64 = prepared_signature;
    out_receipt->rna_decision_signature64 = decision_signature;
    out_receipt->lane5_closure_signature64 = mediation.closure_signature64;
    out_receipt->lane5_mediation_signature64 = mediation.mediation_signature64;
    out_receipt->rna_vm5184_routed = 1U;
    out_receipt->rna_cell_wall_bound = 1U;
    out_receipt->lane5_mediation_recomputed = 1U;
    out_receipt->zero_sum_closure_passed = 1U;
    out_receipt->exact_vm5184_bound = 1U;
    out_receipt->four_lane_modality_preserved =
        HHS_EXACT_PASS219_HOLO4_LANE_COUNT == 4U ? 1U : 0U;
    out_receipt->candidate_only = 1U;
    out_receipt->canonical_mutation_authority = 0U;
    out_receipt->canonical_hash72_authority = 0U;
    out_receipt->canonical_hash216_authority = 0U;
    out_receipt->canonical_persistence_authority = 0U;
    out_receipt->requires_environmental_admission = 1U;
    return HHS_EXACT_STATUS_OK;
}

/*
 * The 1.32 implementation is compiled in the aggregate under this hidden raw
 * name.  Only this 1.37 wrapper may delegate to it after Lane 5 preflight.
 */
HHSExactStatus hhs_exact_pass219_vm81_environment_admit_signed_raw(
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
);

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
    HHSExactPass219RLM20Lane5ClosureReceiptV1 closure_receipt;
    HHSExactStatus status;
    uint32_t halt_reason = HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_CELL_WALL_PATH;

    if (out_committed_frame == NULL || out_admission == NULL ||
        out_firewall_receipt == NULL || out_signature_receipt == NULL ||
        out_environment_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_committed_frame, 0, sizeof(*out_committed_frame));
    memset(out_admission, 0, sizeof(*out_admission));
    hhs_p219_pqc_zero_receipt(out_firewall_receipt, pass_number);
    hhs_p219_pqc_signature_zero_receipt(out_signature_receipt, signature_algorithm);
    hhs_p219_env_zero_receipt(out_environment_receipt, signature_algorithm);

    memset(&closure_receipt, 0, sizeof(closure_receipt));
    status = hhs_exact_pass219_lane5_runtime_preflight(
        pass_number,
        input,
        candidate_frame,
        parent_hash216_reference,
        lo_shu_group,
        g243,
        feedback_lane,
        feedback_trinary,
        &closure_receipt);
    if (status != HHS_EXACT_STATUS_OK ||
        closure_receipt.decision !=
            HHS_EXACT_PASS219_RLM20_LANE5_CLOSURE_CANDIDATE_READY ||
        closure_receipt.candidate_only != 1U ||
        closure_receipt.canonical_mutation_authority != 0U ||
        closure_receipt.canonical_hash72_authority != 0U ||
        closure_receipt.canonical_hash216_authority != 0U ||
        closure_receipt.canonical_persistence_authority != 0U ||
        closure_receipt.requires_environmental_admission != 1U) {
        if (parent_hash216_reference != NULL &&
            hhs_exact_pass219_vm81_pqc_hash216_reference_verify(
                parent_hash216_reference) != HHS_EXACT_STATUS_OK)
            halt_reason = HHS_EXACT_PASS219_VM81_PQC_HALT_INVALID_HASH216_REFERENCE;
        out_environment_receipt->state = HHS_EXACT_PASS219_VM81_ENV_STATE_FROZEN;
        out_environment_receipt->decision = HHS_EXACT_PASS219_VM81_ENV_DECISION_FROZEN;
        out_environment_receipt->reason = HHS_EXACT_PASS219_VM81_ENV_REASON_CANDIDATE_IDENTITY;
        atomic_store(&hhs_p219_env_state, HHS_EXACT_PASS219_VM81_ENV_STATE_FROZEN);
        return hhs_p219_pqc_halt_result(
            halt_reason, out_committed_frame, out_firewall_receipt);
    }

    return hhs_exact_pass219_vm81_environment_admit_signed_raw(
        pass_number,
        signature_algorithm,
        input,
        candidate_frame,
        parent_hash216_reference,
        lo_shu_group,
        g243,
        feedback_lane,
        feedback_trinary,
        out_committed_frame,
        out_admission,
        out_firewall_receipt,
        out_signature_receipt,
        out_environment_receipt);
}

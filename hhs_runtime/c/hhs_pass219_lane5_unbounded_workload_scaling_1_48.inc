#include "../include/hhs_pass219_lane5_unbounded_workload_scaling_1_48.h"

#include <limits.h>
#include <string.h>

_Static_assert(
    HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES == UINT32_C(56),
    "Lane 5 full-manifold address width must remain 56 bytes"
);

static uint64_t hhs_lane5_uws_mix64(uint64_t x) {
    x ^= x >> 30;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31;
    return x;
}

static uint64_t hhs_lane5_uws_fold(uint64_t state, uint64_t tag, uint64_t value) {
    state ^= hhs_lane5_uws_mix64(tag);
    state = hhs_lane5_uws_mix64(state);
    state ^= hhs_lane5_uws_mix64(value ^ (tag * UINT64_C(0x9e3779b97f4a7c15)));
    return hhs_lane5_uws_mix64(state);
}

static uint64_t hhs_lane5_uws_fold_bytes(
    uint64_t state,
    uint64_t tag,
    const uint8_t *bytes,
    uint32_t length
) {
    uint32_t i;
    state = hhs_lane5_uws_fold(state, tag, (uint64_t)length);
    for (i = 0U; i < length; ++i)
        state = hhs_lane5_uws_fold(state, tag + (uint64_t)i + UINT64_C(1), (uint64_t)bytes[i]);
    return state;
}

static int hhs_lane5_uws_valid_phase(uint32_t phase_slot) {
    return phase_slot == UINT32_C(0) ||
           phase_slot == UINT32_C(18) ||
           phase_slot == UINT32_C(36) ||
           phase_slot == UINT32_C(54);
}

static uint32_t hhs_lane5_uws_inverse_phase(uint32_t phase_slot) {
    return (phase_slot + HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_PHASE_HALF) %
           HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_PHASE_CYCLE;
}

static HHSExactStatus hhs_lane5_uws_validate_address(const HHSExactBigUIntView *view) {
    uint8_t canonical = 0U;
    uint8_t less_than_modulus = 0U;
    HHSExactStatus status;

    if (view == NULL || view->struct_size != sizeof(*view) || view->bytes_be == NULL ||
        view->byte_length == 0U || view->byte_length > HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_pass219_full_manifold_residue_validate(
        view,
        &canonical,
        &less_than_modulus
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (canonical != 1U || less_than_modulus != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

static int hhs_lane5_uws_address_equal(
    const HHSExactBigUIntView *left,
    const HHSExactBigUIntView *right
) {
    return left->byte_length == right->byte_length &&
           memcmp(left->bytes_be, right->bytes_be, left->byte_length) == 0;
}

static void hhs_lane5_uws_copy_address(
    uint8_t out[HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES],
    const HHSExactBigUIntView *view
) {
    uint32_t offset = HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES - view->byte_length;
    memset(out, 0, HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES);
    memcpy(out + offset, view->bytes_be, view->byte_length);
}

static uint64_t hhs_lane5_uws_binding_signature(
    const HHSExactPass219Lane5UnboundedWorkloadRouteV1 *route
) {
    uint64_t state = UINT64_C(0x4c35555753313438);
    state = hhs_lane5_uws_fold_bytes(state, UINT64_C(1), route->previous_address.bytes_be, route->previous_address.byte_length);
    state = hhs_lane5_uws_fold_bytes(state, UINT64_C(101), route->current_address.bytes_be, route->current_address.byte_length);
    state = hhs_lane5_uws_fold_bytes(state, UINT64_C(201), route->goal_address.bytes_be, route->goal_address.byte_length);
    state = hhs_lane5_uws_fold_bytes(state, UINT64_C(301), route->workload_sha256, HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_DIGEST_BYTES);
    state = hhs_lane5_uws_fold_bytes(state, UINT64_C(401), route->provenance_sha256, HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_DIGEST_BYTES);
    state = hhs_lane5_uws_fold_bytes(state, UINT64_C(501), route->forbidden_boundary_sha256, HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_DIGEST_BYTES);
    state = hhs_lane5_uws_fold(state, UINT64_C(601), route->workload_byte_count);
    return state;
}

static uint64_t hhs_lane5_uws_descriptor_signature(
    const HHSExactPass219Lane5UnboundedWorkloadRouteV1 *route
) {
    uint64_t state = hhs_lane5_uws_binding_signature(route);
    state = hhs_lane5_uws_fold_bytes(state, UINT64_C(701), route->candidate_address.bytes_be, route->candidate_address.byte_length);
    state = hhs_lane5_uws_fold_bytes(state, UINT64_C(801), route->reciprocal_witness_sha256, HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_DIGEST_BYTES);
    state = hhs_lane5_uws_fold_bytes(state, UINT64_C(901), route->route_witness_sha256, HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_DIGEST_BYTES);
    state = hhs_lane5_uws_fold(state, UINT64_C(1001), route->integer_route_cost);
    state = hhs_lane5_uws_fold(state, UINT64_C(1002), (uint64_t)route->evidence_count);
    state = hhs_lane5_uws_fold(state, UINT64_C(1003), (uint64_t)route->contradiction_check_count);
    state = hhs_lane5_uws_fold(state, UINT64_C(1004), (uint64_t)route->materialized_intermediate_states);
    state = hhs_lane5_uws_fold(state, UINT64_C(1005), (uint64_t)route->phase_slot);
    state = hhs_lane5_uws_fold(state, UINT64_C(1006), (uint64_t)route->inverse_phase_slot);
    state = hhs_lane5_uws_fold(state, UINT64_C(1007), (uint64_t)(int64_t)route->trinary_collapse);
    state = hhs_lane5_uws_fold(state, UINT64_C(1008), (uint64_t)route->binary_collapse);
    state = hhs_lane5_uws_fold(state, UINT64_C(1009), (uint64_t)route->nested_zero_slot);
    return state;
}

static HHSExactStatus hhs_lane5_uws_build_receipt(
    const HHSExactPass219Lane5UnboundedWorkloadRouteV1 *route,
    uint8_t optimizer_selected,
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 *out_receipt
) {
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 receipt;
    uint64_t expected_cost;
    uint64_t descriptor_signature;
    HHSExactStatus status;

    if (route == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (route->struct_size != sizeof(*route) ||
        route->version != HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_lane5_uws_validate_address(&route->previous_address);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_lane5_uws_validate_address(&route->current_address);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_lane5_uws_validate_address(&route->goal_address);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_lane5_uws_validate_address(&route->candidate_address);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (!hhs_lane5_uws_address_equal(&route->candidate_address, &route->goal_address))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (route->evidence_count < HHS_EXACT_PASS219_LANE5_UNBOUNDED_MIN_EVIDENCE ||
        route->contradiction_check_count < HHS_EXACT_PASS219_LANE5_UNBOUNDED_MIN_CONTRADICTION_CHECKS ||
        route->materialized_intermediate_states != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    expected_cost = (uint64_t)route->evidence_count +
                    (uint64_t)route->contradiction_check_count + UINT64_C(1);
    if (route->integer_route_cost != expected_cost)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!hhs_lane5_uws_valid_phase(route->phase_slot) ||
        !hhs_lane5_uws_valid_phase(route->inverse_phase_slot) ||
        route->inverse_phase_slot != hhs_lane5_uws_inverse_phase(route->phase_slot))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (route->trinary_collapse < -1 || route->trinary_collapse > 1 || route->binary_collapse > 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if ((route->binary_collapse == 0U && route->nested_zero_slot != 1U) ||
        (route->binary_collapse == 1U && route->nested_zero_slot != 0U))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (route->workload_serialization_exact != 1U ||
        route->source_digest_verified != 1U ||
        route->replay_witness_verified != 1U ||
        route->exact_goal_reached != 1U ||
        route->contradiction_free != 1U ||
        route->goal_forbidden_conflict != 0U ||
        route->reciprocal_phase_verified != 1U ||
        route->bigint_serialization_addressed != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (route->candidate_only != 1U ||
        route->canonical_mutation_authority != 0U ||
        route->canonical_hash72_authority != 0U ||
        route->canonical_hash216_authority != 0U ||
        route->canonical_persistence_authority != 0U ||
        route->pqc_key_authority != 0U ||
        route->receipt_clock_authority != 0U ||
        route->requires_signed_environmental_vm81_admission != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(&receipt, 0, sizeof(receipt));
    descriptor_signature = hhs_lane5_uws_descriptor_signature(route);
    receipt.struct_size = (uint32_t)sizeof(receipt);
    receipt.version = HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION;
    receipt.namespace_id = HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_NAMESPACE;
    receipt.candidate_address_length = route->candidate_address.byte_length;
    hhs_lane5_uws_copy_address(receipt.candidate_address_be, &route->candidate_address);
    memcpy(receipt.workload_sha256, route->workload_sha256, sizeof(receipt.workload_sha256));
    memcpy(receipt.provenance_sha256, route->provenance_sha256, sizeof(receipt.provenance_sha256));
    memcpy(receipt.route_witness_sha256, route->route_witness_sha256, sizeof(receipt.route_witness_sha256));
    receipt.workload_byte_count = route->workload_byte_count;
    receipt.integer_route_cost = route->integer_route_cost;
    receipt.descriptor_signature64 = descriptor_signature;
    receipt.route_receipt_signature64 = hhs_lane5_uws_fold(
        descriptor_signature,
        UINT64_C(0x5245434549505432),
        hhs_lane5_uws_binding_signature(route)
    );
    receipt.phase_slot = route->phase_slot;
    receipt.inverse_phase_slot = route->inverse_phase_slot;
    receipt.trinary_collapse = route->trinary_collapse;
    receipt.binary_collapse = route->binary_collapse;
    receipt.nested_zero_slot = route->nested_zero_slot;
    receipt.accepted = 1U;
    receipt.optimizer_selected = optimizer_selected;
    receipt.replay_witness_verified = 1U;
    receipt.exact_goal_reached = 1U;
    receipt.contradiction_free = 1U;
    receipt.reciprocal_phase_verified = 1U;
    receipt.bigint_serialization_addressed = 1U;
    receipt.full_manifold_coordinate_capable = 1U;
    receipt.workload_class_agnostic = 1U;
    receipt.materialized_intermediate_states = 0U;
    receipt.candidate_only = 1U;
    receipt.canonical_mutation_authority = 0U;
    receipt.canonical_hash72_authority = 0U;
    receipt.canonical_hash216_authority = 0U;
    receipt.canonical_persistence_authority = 0U;
    receipt.pqc_key_authority = 0U;
    receipt.receipt_clock_authority = 0U;
    receipt.requires_signed_environmental_vm81_admission = 1U;
    *out_receipt = receipt;
    return HHS_EXACT_STATUS_OK;
}

static void hhs_lane5_uws_bump(uint64_t *value, uint8_t *saturated) {
    if (*value == UINT64_MAX) {
        *saturated = 1U;
        return;
    }
    *value += UINT64_C(1);
}

static void hhs_lane5_uws_bind_stream(
    HHSExactPass219Lane5UnboundedWorkloadStreamV1 *stream,
    const HHSExactPass219Lane5UnboundedWorkloadRouteV1 *route
) {
    stream->workload_binding_signature64 = hhs_lane5_uws_binding_signature(route);
    stream->bound_workload_byte_count = route->workload_byte_count;
    stream->bound_previous_address_length = route->previous_address.byte_length;
    stream->bound_current_address_length = route->current_address.byte_length;
    stream->bound_goal_address_length = route->goal_address.byte_length;
    hhs_lane5_uws_copy_address(stream->bound_previous_address_be, &route->previous_address);
    hhs_lane5_uws_copy_address(stream->bound_current_address_be, &route->current_address);
    hhs_lane5_uws_copy_address(stream->bound_goal_address_be, &route->goal_address);
    memcpy(stream->bound_workload_sha256, route->workload_sha256, sizeof(stream->bound_workload_sha256));
    memcpy(stream->bound_provenance_sha256, route->provenance_sha256, sizeof(stream->bound_provenance_sha256));
    memcpy(stream->bound_forbidden_boundary_sha256, route->forbidden_boundary_sha256, sizeof(stream->bound_forbidden_boundary_sha256));
    stream->has_binding = 1U;
}

static int hhs_lane5_uws_stream_binding_matches(
    const HHSExactPass219Lane5UnboundedWorkloadStreamV1 *stream,
    const HHSExactPass219Lane5UnboundedWorkloadRouteV1 *route
) {
    uint32_t previous_offset;
    uint32_t current_offset;
    uint32_t goal_offset;

    if (stream->bound_workload_byte_count != route->workload_byte_count ||
        stream->bound_previous_address_length != route->previous_address.byte_length ||
        stream->bound_current_address_length != route->current_address.byte_length ||
        stream->bound_goal_address_length != route->goal_address.byte_length)
        return 0;

    previous_offset = HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES - route->previous_address.byte_length;
    current_offset = HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES - route->current_address.byte_length;
    goal_offset = HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES - route->goal_address.byte_length;

    return memcmp(stream->bound_previous_address_be + previous_offset, route->previous_address.bytes_be, route->previous_address.byte_length) == 0 &&
           memcmp(stream->bound_current_address_be + current_offset, route->current_address.bytes_be, route->current_address.byte_length) == 0 &&
           memcmp(stream->bound_goal_address_be + goal_offset, route->goal_address.bytes_be, route->goal_address.byte_length) == 0 &&
           memcmp(stream->bound_workload_sha256, route->workload_sha256, sizeof(stream->bound_workload_sha256)) == 0 &&
           memcmp(stream->bound_provenance_sha256, route->provenance_sha256, sizeof(stream->bound_provenance_sha256)) == 0 &&
           memcmp(stream->bound_forbidden_boundary_sha256, route->forbidden_boundary_sha256, sizeof(stream->bound_forbidden_boundary_sha256)) == 0;
}

static int hhs_lane5_uws_receipt_is_better(
    const HHSExactPass219Lane5UnboundedWorkloadReceiptV1 *candidate,
    const HHSExactPass219Lane5UnboundedWorkloadReceiptV1 *best
) {
    int witness_order;
    if (candidate->integer_route_cost != best->integer_route_cost)
        return candidate->integer_route_cost < best->integer_route_cost;
    witness_order = memcmp(candidate->route_witness_sha256, best->route_witness_sha256, sizeof(candidate->route_witness_sha256));
    if (witness_order != 0)
        return witness_order < 0;
    if (candidate->phase_slot != best->phase_slot)
        return candidate->phase_slot < best->phase_slot;
    if (candidate->trinary_collapse != best->trinary_collapse)
        return candidate->trinary_collapse < best->trinary_collapse;
    return candidate->binary_collapse < best->binary_collapse;
}

uint32_t hhs_exact_pass219_lane5_unbounded_workload_scaling_version(void) {
    return HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_unbounded_workload_scaling_authority(
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 value;
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION;
    value.namespace_id = HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_NAMESPACE;
    value.full_manifold_address_bytes = HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES;
    value.full_manifold_bigint_addressing = 1U;
    value.modulus_is_72_pow_72 = 1U;
    value.any_byte_serializable_workload = 1U;
    value.workload_class_agnostic = 1U;
    value.streaming_candidate_ingress = 1U;
    value.constant_memory_candidate_reduction = 1U;
    value.fixed_candidate_batch_required = 0U;
    value.intermediate_materialization_required = 0U;
    value.previous_current_goal_bound = 1U;
    value.provenance_bound = 1U;
    value.contradiction_boundary_bound = 1U;
    value.exact_reciprocal_phase_inversion = 1U;
    value.balanced_trinary_collapse = 1U;
    value.binary_qubit_collapse = 1U;
    value.nested_zero_layer = 1U;
    value.deterministic_tie_break = 1U;
    value.candidate_only = 1U;
    value.canonical_vm81_mutation_authority = 0U;
    value.canonical_hash72_authority = 0U;
    value.canonical_hash216_authority = 0U;
    value.canonical_persistence_authority = 0U;
    value.pqc_key_authority = 0U;
    value.receipt_clock_authority = 0U;
    value.requires_signed_environmental_vm81_admission = 1U;
    value.floating_point_canonical_authority = 0U;
    *out_authority = value;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_unbounded_workload_route_validate(
    const HHSExactPass219Lane5UnboundedWorkloadRouteV1 *route,
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 *out_receipt
) {
    return hhs_lane5_uws_build_receipt(route, 0U, out_receipt);
}

HHSExactStatus hhs_exact_pass219_lane5_unbounded_workload_stream_init(
    HHSExactPass219Lane5UnboundedWorkloadStreamV1 *stream
) {
    if (stream == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(stream, 0, sizeof(*stream));
    stream->struct_size = (uint32_t)sizeof(*stream);
    stream->version = HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_unbounded_workload_stream_consider(
    HHSExactPass219Lane5UnboundedWorkloadStreamV1 *stream,
    const HHSExactPass219Lane5UnboundedWorkloadRouteV1 *route,
    uint8_t *out_candidate_admitted
) {
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 receipt;
    HHSExactStatus status;

    if (stream == NULL || route == NULL || out_candidate_admitted == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (stream->struct_size != sizeof(*stream) ||
        stream->version != HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION ||
        stream->finalized != 0U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    *out_candidate_admitted = 0U;
    hhs_lane5_uws_bump(&stream->candidates_seen, &stream->count_saturated);
    status = hhs_lane5_uws_build_receipt(route, 1U, &receipt);
    if (status != HHS_EXACT_STATUS_OK) {
        hhs_lane5_uws_bump(&stream->rejected_candidates, &stream->count_saturated);
        return HHS_EXACT_STATUS_OK;
    }

    if (stream->has_binding == 0U)
        hhs_lane5_uws_bind_stream(stream, route);
    else if (!hhs_lane5_uws_stream_binding_matches(stream, route)) {
        hhs_lane5_uws_bump(&stream->rejected_candidates, &stream->count_saturated);
        return HHS_EXACT_STATUS_OK;
    }

    hhs_lane5_uws_bump(&stream->admissible_candidates, &stream->count_saturated);
    *out_candidate_admitted = 1U;
    if (stream->has_best == 0U || hhs_lane5_uws_receipt_is_better(&receipt, &stream->best_receipt)) {
        stream->best_receipt = receipt;
        stream->has_best = 1U;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_unbounded_workload_stream_finalize(
    HHSExactPass219Lane5UnboundedWorkloadStreamV1 *stream,
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 *out_receipt
) {
    if (stream == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (stream->struct_size != sizeof(*stream) ||
        stream->version != HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION ||
        stream->finalized != 0U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (stream->has_best != 1U || stream->admissible_candidates == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    stream->finalized = 1U;
    *out_receipt = stream->best_receipt;
    return HHS_EXACT_STATUS_OK;
}

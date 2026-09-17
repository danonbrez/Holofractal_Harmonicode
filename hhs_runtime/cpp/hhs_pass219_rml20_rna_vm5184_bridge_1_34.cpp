#include "hhs_pass219_rml20_rna_vm5184_bridge_1_34.h"

#include <cstring>

namespace {

constexpr uint8_t kDirectionCount =
    static_cast<uint8_t>(HHS_EXACT_PASS219_RML20_DIRECTION_COUNT);

bool valid_direction(uint8_t direction) noexcept {
    return direction < kDirectionCount;
}

uint8_t inverse_direction(uint8_t direction) noexcept {
    switch (direction) {
        case HHS_EXACT_PASS219_RML20_OPERATION_FORWARD:
            return HHS_EXACT_PASS219_RML20_OPERATION_REVERSE;
        case HHS_EXACT_PASS219_RML20_OPERATION_REVERSE:
            return HHS_EXACT_PASS219_RML20_OPERATION_FORWARD;
        case HHS_EXACT_PASS219_RML20_PHASE_FORWARD:
            return HHS_EXACT_PASS219_RML20_PHASE_REVERSE;
        case HHS_EXACT_PASS219_RML20_PHASE_REVERSE:
            return HHS_EXACT_PASS219_RML20_PHASE_FORWARD;
        case HHS_EXACT_PASS219_RML20_CELL_FORWARD:
            return HHS_EXACT_PASS219_RML20_CELL_REVERSE;
        default:
            return HHS_EXACT_PASS219_RML20_CELL_FORWARD;
    }
}

int8_t direction_flux(uint8_t direction) noexcept {
    switch (direction) {
        case HHS_EXACT_PASS219_RML20_OPERATION_FORWARD:
        case HHS_EXACT_PASS219_RML20_PHASE_FORWARD:
        case HHS_EXACT_PASS219_RML20_CELL_FORWARD:
            return INT8_C(1);
        default:
            return INT8_C(-1);
    }
}

HHSExactStatus encode_address(
    uint8_t lane,
    uint8_t operation,
    uint8_t phase,
    uint8_t cell,
    uint32_t *out_address
) noexcept {
    if (out_address == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (lane >= HHS_EXACT_PASS219_HOLO4_LANE_COUNT ||
        operation >= HHS_EXACT_PASS219_RML20_OPERATION_COUNT ||
        phase >= HHS_EXACT_PASS219_RML20_PHASE_COUNT ||
        cell >= HHS_EXACT_PASS219_RML20_CELL_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    *out_address =
        (((static_cast<uint32_t>(lane) *
           HHS_EXACT_PASS219_RML20_OPERATION_COUNT + operation) *
          HHS_EXACT_PASS219_RML20_PHASE_COUNT + phase) *
         HHS_EXACT_PASS219_RML20_CELL_COUNT + cell);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus decode_address(
    uint32_t address,
    uint8_t *out_lane,
    uint8_t *out_operation,
    uint8_t *out_phase,
    uint8_t *out_cell
) noexcept {
    if (out_lane == nullptr || out_operation == nullptr ||
        out_phase == nullptr || out_cell == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (address >= HHS_EXACT_PASS219_RML20_ADDRESS_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    uint32_t value = address;
    *out_cell = static_cast<uint8_t>(
        value % HHS_EXACT_PASS219_RML20_CELL_COUNT);
    value /= HHS_EXACT_PASS219_RML20_CELL_COUNT;
    *out_phase = static_cast<uint8_t>(
        value % HHS_EXACT_PASS219_RML20_PHASE_COUNT);
    value /= HHS_EXACT_PASS219_RML20_PHASE_COUNT;
    *out_operation = static_cast<uint8_t>(
        value % HHS_EXACT_PASS219_RML20_OPERATION_COUNT);
    value /= HHS_EXACT_PASS219_RML20_OPERATION_COUNT;
    *out_lane = static_cast<uint8_t>(value);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus neighbor_address(
    uint32_t source_address,
    uint8_t direction,
    uint32_t *out_target_address
) noexcept {
    uint8_t lane = 0U;
    uint8_t operation = 0U;
    uint8_t phase = 0U;
    uint8_t cell = 0U;

    if (out_target_address == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!valid_direction(direction))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    HHSExactStatus status = decode_address(
        source_address, &lane, &operation, &phase, &cell);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    switch (direction) {
        case HHS_EXACT_PASS219_RML20_OPERATION_FORWARD:
            operation = static_cast<uint8_t>(
                (static_cast<uint32_t>(operation) + 1U) %
                HHS_EXACT_PASS219_RML20_OPERATION_COUNT);
            break;
        case HHS_EXACT_PASS219_RML20_OPERATION_REVERSE:
            operation = static_cast<uint8_t>(
                (static_cast<uint32_t>(operation) +
                 HHS_EXACT_PASS219_RML20_OPERATION_COUNT - 1U) %
                HHS_EXACT_PASS219_RML20_OPERATION_COUNT);
            break;
        case HHS_EXACT_PASS219_RML20_PHASE_FORWARD:
            phase = static_cast<uint8_t>(
                (static_cast<uint32_t>(phase) + 1U) %
                HHS_EXACT_PASS219_RML20_PHASE_COUNT);
            break;
        case HHS_EXACT_PASS219_RML20_PHASE_REVERSE:
            phase = static_cast<uint8_t>(
                (static_cast<uint32_t>(phase) +
                 HHS_EXACT_PASS219_RML20_PHASE_COUNT - 1U) %
                HHS_EXACT_PASS219_RML20_PHASE_COUNT);
            break;
        case HHS_EXACT_PASS219_RML20_CELL_FORWARD:
            cell = static_cast<uint8_t>(
                (static_cast<uint32_t>(cell) + 1U) %
                HHS_EXACT_PASS219_RML20_CELL_COUNT);
            break;
        default:
            cell = static_cast<uint8_t>(
                (static_cast<uint32_t>(cell) +
                 HHS_EXACT_PASS219_RML20_CELL_COUNT - 1U) %
                HHS_EXACT_PASS219_RML20_CELL_COUNT);
            break;
    }

    return encode_address(lane, operation, phase, cell, out_target_address);
}

int8_t discrete_divergence() noexcept {
    int8_t sum = 0;
    for (uint8_t direction = 0U; direction < kDirectionCount; ++direction)
        sum = static_cast<int8_t>(sum + direction_flux(direction));
    return sum;
}

bool route_evidence_is_candidate_only(
    const HHSExactPass219Holo4PreparedV1& prepared,
    const HHSExactPass219Holo4DecisionV1& decision
) noexcept {
    return prepared.candidate_only == 1U &&
           prepared.exact_integer_only == 1U &&
           prepared.canonical_mutation_authority == 0U &&
           prepared.canonical_hash72_authority == 0U &&
           prepared.canonical_hash216_authority == 0U &&
           prepared.canonical_persistence_authority == 0U &&
           prepared.floating_point_authority == 0U &&
           decision.candidate_only == 1U &&
           decision.exact_integer_only == 1U &&
           decision.canonical_mutation_authority == 0U &&
           decision.canonical_hash72_authority == 0U &&
           decision.canonical_hash216_authority == 0U &&
           decision.canonical_persistence_authority == 0U &&
           decision.floating_point_authority == 0U;
}

}  // namespace

extern "C" uint32_t hhs_exact_pass219_rml20_rna_vm5184_version(void) {
    return HHS_EXACT_PASS219_RML20_RNA_VM5184_VERSION;
}

extern "C" HHSExactStatus hhs_exact_pass219_rml20_rna_vm5184_descriptor(
    HHSExactPass219RML20RNAVM5184DescriptorV1 *out_descriptor
) {
    if (out_descriptor == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    std::memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = static_cast<uint32_t>(sizeof(*out_descriptor));
    out_descriptor->version = HHS_EXACT_PASS219_RML20_RNA_VM5184_VERSION;
    out_descriptor->lane_count = HHS_EXACT_PASS219_HOLO4_LANE_COUNT;
    out_descriptor->operations_per_cell = HHS_EXACT_PASS219_RML20_OPERATION_COUNT;
    out_descriptor->phase_count = HHS_EXACT_PASS219_RML20_PHASE_COUNT;
    out_descriptor->cell_count = HHS_EXACT_PASS219_RML20_CELL_COUNT;
    out_descriptor->address_count = HHS_EXACT_PASS219_RML20_ADDRESS_COUNT;
    out_descriptor->direction_count = HHS_EXACT_PASS219_RML20_DIRECTION_COUNT;
    out_descriptor->vm5184_bytes = HHS_EXACT_VM81_FRAME_BYTES;
    out_descriptor->cpp_rna_cell_wall = 1U;
    out_descriptor->frozen_rml17_parity_surface = 1U;
    out_descriptor->lane_retaining_transport = 1U;
    out_descriptor->reciprocal_flux_transport = 1U;
    out_descriptor->candidate_only = 1U;
    out_descriptor->exact_integer_only = 1U;
    out_descriptor->canonical_mutation_authority = 0U;
    out_descriptor->canonical_hash72_authority = 0U;
    out_descriptor->canonical_hash216_authority = 0U;
    out_descriptor->canonical_persistence_authority = 0U;
    out_descriptor->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

extern "C" HHSExactStatus hhs_exact_pass219_rml20_transport_address_encode(
    uint8_t lane,
    uint8_t operation,
    uint8_t phase,
    uint8_t cell,
    uint32_t *out_address
) {
    return encode_address(lane, operation, phase, cell, out_address);
}

extern "C" HHSExactStatus hhs_exact_pass219_rml20_transport_address_decode(
    uint32_t address,
    uint8_t *out_lane,
    uint8_t *out_operation,
    uint8_t *out_phase,
    uint8_t *out_cell
) {
    return decode_address(
        address, out_lane, out_operation, out_phase, out_cell);
}

extern "C" HHSExactStatus hhs_exact_pass219_rml20_transport_neighbor(
    uint32_t source_address,
    uint8_t direction,
    uint32_t *out_target_address
) {
    return neighbor_address(source_address, direction, out_target_address);
}

extern "C" HHSExactStatus hhs_exact_pass219_rml20_transport_flux(
    uint8_t direction,
    int8_t *out_flux
) {
    if (out_flux == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!valid_direction(direction))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    *out_flux = direction_flux(direction);
    return HHS_EXACT_STATUS_OK;
}

extern "C" HHSExactStatus hhs_exact_pass219_rml20_rna_vm5184_route(
    const HHSExactUQCELInputV1 *input,
    const uint8_t *raw_frame_le,
    size_t raw_frame_length,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    uint32_t source_address,
    uint8_t direction,
    HHSExactPass219RML20RNAVM5184ReceiptV1 *out_receipt
) {
    HHSExactPass219Holo4PreparedV1 prepared{};
    HHSExactPass219Holo4DecisionV1 decision{};
    HHSExactPass219RML20RNAVM5184ReceiptV1 receipt{};
    uint8_t source_lane = 0U;
    uint8_t source_operation = 0U;
    uint8_t source_phase = 0U;
    uint8_t source_cell = 0U;
    uint8_t target_lane = 0U;
    uint8_t target_operation = 0U;
    uint8_t target_phase = 0U;
    uint8_t target_cell = 0U;
    uint32_t target_address = 0U;
    uint32_t reciprocal_address = 0U;
    uint32_t reencoded_source = 0U;

    if (out_receipt != nullptr)
        std::memset(out_receipt, 0, sizeof(*out_receipt));
    if (input == nullptr || raw_frame_le == nullptr || transition == nullptr ||
        out_receipt == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (raw_frame_length != HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (!valid_direction(direction))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    HHSExactStatus status = decode_address(
        source_address,
        &source_lane,
        &source_operation,
        &source_phase,
        &source_cell);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = encode_address(
        source_lane,
        source_operation,
        source_phase,
        source_cell,
        &reencoded_source);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = neighbor_address(source_address, direction, &target_address);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = decode_address(
        target_address,
        &target_lane,
        &target_operation,
        &target_phase,
        &target_cell);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    const uint8_t inverse = inverse_direction(direction);
    status = neighbor_address(target_address, inverse, &reciprocal_address);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    const int8_t forward_flux = direction_flux(direction);
    const int8_t reverse_flux = direction_flux(inverse);
    const int8_t divergence = discrete_divergence();

    status = hhs_exact_pass219_rna_raw5184_route(
        input,
        raw_frame_le,
        raw_frame_length,
        transition,
        source_lane,
        forward_flux,
        &prepared,
        &decision);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!route_evidence_is_candidate_only(prepared, decision))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    receipt.struct_size = static_cast<uint32_t>(sizeof(receipt));
    receipt.version = HHS_EXACT_PASS219_RML20_RNA_VM5184_VERSION;
    receipt.source_address = source_address;
    receipt.target_address = target_address;
    receipt.source_lane = source_lane;
    receipt.source_operation = source_operation;
    receipt.source_phase = source_phase;
    receipt.source_cell = source_cell;
    receipt.target_lane = target_lane;
    receipt.target_operation = target_operation;
    receipt.target_phase = target_phase;
    receipt.target_cell = target_cell;
    receipt.direction = direction;
    receipt.inverse_direction = inverse;
    receipt.forward_flux = forward_flux;
    receipt.reverse_flux = reverse_flux;
    receipt.discrete_divergence = divergence;
    receipt.encode_decode_bijective = reencoded_source == source_address ? 1U : 0U;
    receipt.reciprocal_neighbor_restores_source =
        reciprocal_address == source_address ? 1U : 0U;
    receipt.reciprocal_flux_balanced =
        forward_flux == static_cast<int8_t>(-reverse_flux) ? 1U : 0U;
    receipt.lane_identity_retained = source_lane == target_lane ? 1U : 0U;
    receipt.zero_discrete_divergence = divergence == 0 ? 1U : 0U;
    receipt.zero_diffusion_classification =
        receipt.reciprocal_neighbor_restores_source == 1U &&
        receipt.reciprocal_flux_balanced == 1U &&
        receipt.lane_identity_retained == 1U &&
        receipt.zero_discrete_divergence == 1U &&
        prepared.reciprocal_phase_closure == 1U
            ? 1U
            : 0U;
    receipt.feedback_lane_bound = decision.feedback_lane == source_lane ? 1U : 0U;
    receipt.feedback_trinary_bound =
        decision.feedback_trinary == forward_flux ? 1U : 0U;
    receipt.rna_cell_wall_routed = 1U;
    receipt.selected_lane = decision.selected_lane;
    receipt.candidate_only = 1U;
    receipt.exact_integer_only = 1U;
    receipt.canonical_mutation_authority = 0U;
    receipt.canonical_hash72_authority = 0U;
    receipt.canonical_hash216_authority = 0U;
    receipt.canonical_persistence_authority = 0U;
    receipt.floating_point_authority = 0U;
    receipt.graph_signature64 = prepared.graph_signature64;
    receipt.tensor_signature64 = prepared.tensor_signature64;
    receipt.decision_signature64 = decision.decision_signature64;
    std::memcpy(
        receipt.transition_identity216,
        transition->transition_identity216,
        HHS_EXACT_UQCEL_HASH216_STRLEN);

    if (receipt.encode_decode_bijective != 1U ||
        receipt.reciprocal_neighbor_restores_source != 1U ||
        receipt.reciprocal_flux_balanced != 1U ||
        receipt.lane_identity_retained != 1U ||
        receipt.zero_discrete_divergence != 1U ||
        receipt.zero_diffusion_classification != 1U ||
        receipt.feedback_lane_bound != 1U ||
        receipt.feedback_trinary_bound != 1U ||
        receipt.selected_lane >= HHS_EXACT_PASS219_HOLO4_LANE_COUNT)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    std::memcpy(out_receipt, &receipt, sizeof(receipt));
    return HHS_EXACT_STATUS_OK;
}

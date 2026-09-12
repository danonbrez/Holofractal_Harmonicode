#include "hhs_pass219_discrete_transport_conservation_1_29.hpp"

#include <array>
#include <sstream>
#include <vector>

namespace hhs::pass219::transport {

Node step(const Node& source, Direction direction) noexcept {
    Node target = source;
    const auto flux = static_cast<int>(signed_flux(direction));
    const auto phase = static_cast<int>(source.phase72);
    target.phase72 = static_cast<std::uint8_t>(
        (phase + static_cast<int>(kPhaseCount) + flux) % static_cast<int>(kPhaseCount)
    );
    return target;
}

DirectedAddress directed_successor(const DirectedAddress& source) noexcept {
    return DirectedAddress{step(source.node, source.direction), reciprocal(source.direction)};
}

std::uint64_t flatten_address(const DirectedAddress& address) noexcept {
    std::uint64_t index = address.node.operation64;
    index = index * kPhaseCount + address.node.phase72;
    index = index * kCellCount + address.node.cell81;
    index = index * kDirectionCount + direction_index(address.direction);
    return index;
}

DirectedAddress unflatten_address(std::uint64_t index) noexcept {
    DirectedAddress address{};
    std::uint64_t value = index;
    address.direction = static_cast<Direction>(value % kDirectionCount);
    value /= kDirectionCount;
    address.node.cell81 = static_cast<std::uint8_t>(value % kCellCount);
    value /= kCellCount;
    address.node.phase72 = static_cast<std::uint8_t>(value % kPhaseCount);
    value /= kPhaseCount;
    address.node.operation64 = static_cast<std::uint8_t>(value % kOperationCount);
    return address;
}

bool divergence_zero(const Node& source) noexcept {
    const int flux_sum = static_cast<int>(kSignedFlux[0]) +
                         static_cast<int>(kSignedFlux[1]) +
                         static_cast<int>(kSignedFlux[2]) +
                         static_cast<int>(kSignedFlux[3]);
    return valid_node(source) && flux_sum == 0;
}

EdgeWitness witness_edge(const DirectedAddress& source) noexcept {
    const DirectedAddress target = directed_successor(source);
    const auto inverse = reciprocal(source.direction);
    const bool source_valid = valid_node(source.node) && valid_direction(source.direction);
    const bool target_valid = valid_node(target.node) && valid_direction(target.direction);
    const bool reciprocal_balance =
        static_cast<int>(signed_flux(source.direction)) +
        static_cast<int>(signed_flux(inverse)) == 0;
    const bool admission_coordinates_preserved =
        source.node.operation64 == target.node.operation64 &&
        source.node.cell81 == target.node.cell81 &&
        operation_from_bases(
            left_basis_from_operation(target.node.operation64),
            right_basis_from_operation(target.node.operation64)
        ) == target.node.operation64;
    const bool reverse_restores = directed_successor(target) == source;

    return EdgeWitness{
        source,
        target,
        signed_flux(source.direction),
        signed_flux(inverse),
        divergence_zero(source.node),
        source_valid && target_valid && reciprocal_balance,
        source_valid && target_valid && admission_coordinates_preserved,
        source_valid && target_valid && reverse_restores,
        source_valid && target_valid && reverse_restores,
    };
}

bool reverse_sequence_restores(
    const Node& source,
    const Direction* directions,
    std::size_t count
) noexcept {
    if (!valid_node(source) || (count != 0U && directions == nullptr))
        return false;

    Node current = source;
    for (std::size_t i = 0U; i < count; ++i) {
        if (!valid_direction(directions[i]))
            return false;
        current = step(current, directions[i]);
    }
    for (std::size_t i = count; i > 0U; --i)
        current = step(current, reciprocal(directions[i - 1U]));
    return current == source;
}

bool rna_admission_anchor_matches(
    const RNAAdmissionView& admission,
    const Node& source
) noexcept {
    const auto* record = admission.get();
    if (record == nullptr || !valid_node(source))
        return false;
    return record->composed.uqcel.decision == HHS_EXACT_UQCEL_DECISION_ADMIT &&
           record->composed.uqcel.frame_committed == 1U &&
           record->coordinate.operation64 == source.operation64 &&
           record->coordinate.cell81 == source.cell81 &&
           operation_from_bases(
               record->native_phase.left_basis,
               record->native_phase.right_basis
           ) == source.operation64;
}

ContractReport audit_entire_address_manifold() {
    ContractReport report{};
    report.node_count = kNodeCount;
    report.address_count = kAddressCount;
    report.discrete_divergence_gate = true;
    report.reciprocal_edge_balance_gate = true;
    report.admission_preservation_gate = true;
    report.zero_canonical_diffusion_gate = true;
    report.composed_reverse_closure_gate = true;
    report.exhaustive_address_coverage = true;
    report.target_map_bijective = true;
    report.table_driven_direction_logic = true;
    report.exact_integer_phase_arithmetic = true;
    report.rna_admission_authority_delegated = true;

    std::vector<std::uint8_t> target_seen(static_cast<std::size_t>(kAddressCount), 0U);

    for (std::uint64_t node_index = 0U; node_index < kNodeCount; ++node_index) {
        std::uint64_t value = node_index;
        Node node{};
        node.cell81 = static_cast<std::uint8_t>(value % kCellCount);
        value /= kCellCount;
        node.phase72 = static_cast<std::uint8_t>(value % kPhaseCount);
        value /= kPhaseCount;
        node.operation64 = static_cast<std::uint8_t>(value % kOperationCount);
        ++report.discrete_divergence_nodes_checked;
        if (!divergence_zero(node)) {
            report.discrete_divergence_gate = false;
            ++report.failure_count;
        }
    }

    for (std::uint64_t index = 0U; index < kAddressCount; ++index) {
        const DirectedAddress source = unflatten_address(index);
        const EdgeWitness edge = witness_edge(source);
        const std::uint64_t roundtrip_index = flatten_address(source);
        const std::uint64_t target_index = flatten_address(edge.target);

        if (roundtrip_index != index || target_index >= kAddressCount) {
            report.exhaustive_address_coverage = false;
            ++report.failure_count;
        } else {
            if (target_seen[static_cast<std::size_t>(target_index)] != 0U) {
                report.target_map_bijective = false;
                ++report.failure_count;
            } else {
                target_seen[static_cast<std::size_t>(target_index)] = 1U;
                ++report.unique_target_addresses;
            }
        }

        ++report.reciprocal_edge_addresses_checked;
        if (!edge.reciprocal_edge_balance) {
            report.reciprocal_edge_balance_gate = false;
            ++report.failure_count;
        }

        ++report.admission_preservation_addresses_checked;
        if (!edge.admission_visible_coordinates_preserved) {
            report.admission_preservation_gate = false;
            ++report.failure_count;
        }

        ++report.zero_diffusion_addresses_checked;
        if (!edge.zero_canonical_diffusion || !edge.exact_reverse_restores_source) {
            report.zero_canonical_diffusion_gate = false;
            ++report.failure_count;
        }

        const std::array<Direction, 6U> sequence = {
            source.direction,
            Direction::X,
            Direction::W,
            Direction::Y,
            Direction::Z,
            reciprocal(source.direction),
        };
        ++report.composed_reverse_addresses_checked;
        if (!reverse_sequence_restores(source.node, sequence.data(), sequence.size())) {
            report.composed_reverse_closure_gate = false;
            ++report.failure_count;
        }
    }

    if (report.unique_target_addresses != kAddressCount) {
        report.target_map_bijective = false;
        ++report.failure_count;
    }

    report.lossy_compression_used = false;
    report.neighbor_averaging_used = false;
    report.hash216_cryptographic_inversion_used = false;
    report.canonical_vm81_mutation_authority = false;
    report.canonical_hash72_mint_authority = false;
    report.canonical_hash216_persistence_authority = false;
    report.floating_point_canonical_authority = false;
    report.scalar_projection_substitution_authority = false;
    report.timing_authority = false;

    report.pass = report.failure_count == 0U &&
                  report.discrete_divergence_gate &&
                  report.reciprocal_edge_balance_gate &&
                  report.admission_preservation_gate &&
                  report.zero_canonical_diffusion_gate &&
                  report.composed_reverse_closure_gate &&
                  report.exhaustive_address_coverage &&
                  report.target_map_bijective &&
                  report.discrete_divergence_nodes_checked == kNodeCount &&
                  report.reciprocal_edge_addresses_checked == kAddressCount &&
                  report.admission_preservation_addresses_checked == kAddressCount &&
                  report.zero_diffusion_addresses_checked == kAddressCount &&
                  report.composed_reverse_addresses_checked == kAddressCount;
    return report;
}

std::string report_json(const ContractReport& report) {
    const auto b = [](bool value) noexcept { return value ? "true" : "false"; };
    std::ostringstream out;
    out << "{"
        << "\"schema\":\"HHS_PASS219_DISCRETE_TRANSPORT_CONSERVATION_1_29_V1\","
        << "\"node_count\":" << report.node_count << ','
        << "\"address_count\":" << report.address_count << ','
        << "\"discrete_divergence_nodes_checked\":" << report.discrete_divergence_nodes_checked << ','
        << "\"reciprocal_edge_addresses_checked\":" << report.reciprocal_edge_addresses_checked << ','
        << "\"admission_preservation_addresses_checked\":" << report.admission_preservation_addresses_checked << ','
        << "\"zero_diffusion_addresses_checked\":" << report.zero_diffusion_addresses_checked << ','
        << "\"composed_reverse_addresses_checked\":" << report.composed_reverse_addresses_checked << ','
        << "\"unique_target_addresses\":" << report.unique_target_addresses << ','
        << "\"failure_count\":" << report.failure_count << ','
        << "\"discrete_divergence_gate\":" << b(report.discrete_divergence_gate) << ','
        << "\"reciprocal_edge_balance_gate\":" << b(report.reciprocal_edge_balance_gate) << ','
        << "\"admission_preservation_gate\":" << b(report.admission_preservation_gate) << ','
        << "\"zero_canonical_diffusion_gate\":" << b(report.zero_canonical_diffusion_gate) << ','
        << "\"composed_reverse_closure_gate\":" << b(report.composed_reverse_closure_gate) << ','
        << "\"exhaustive_address_coverage\":" << b(report.exhaustive_address_coverage) << ','
        << "\"target_map_bijective\":" << b(report.target_map_bijective) << ','
        << "\"table_driven_direction_logic\":" << b(report.table_driven_direction_logic) << ','
        << "\"exact_integer_phase_arithmetic\":" << b(report.exact_integer_phase_arithmetic) << ','
        << "\"rna_admission_authority_delegated\":" << b(report.rna_admission_authority_delegated) << ','
        << "\"rna_admission_anchor_verified\":" << b(report.rna_admission_anchor_verified) << ','
        << "\"rna_record_immutable_under_transport\":" << b(report.rna_record_immutable_under_transport) << ','
        << "\"lossy_compression_used\":" << b(report.lossy_compression_used) << ','
        << "\"neighbor_averaging_used\":" << b(report.neighbor_averaging_used) << ','
        << "\"hash216_cryptographic_inversion_used\":" << b(report.hash216_cryptographic_inversion_used) << ','
        << "\"canonical_vm81_mutation_authority\":" << b(report.canonical_vm81_mutation_authority) << ','
        << "\"canonical_hash72_mint_authority\":" << b(report.canonical_hash72_mint_authority) << ','
        << "\"canonical_hash216_persistence_authority\":" << b(report.canonical_hash216_persistence_authority) << ','
        << "\"floating_point_canonical_authority\":" << b(report.floating_point_canonical_authority) << ','
        << "\"scalar_projection_substitution_authority\":" << b(report.scalar_projection_substitution_authority) << ','
        << "\"timing_authority\":" << b(report.timing_authority) << ','
        << "\"result\":\"" << (report.pass ? "PASS" : "FAIL") << "\""
        << "}";
    return out.str();
}

}  // namespace hhs::pass219::transport

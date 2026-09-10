#include "hhs_pass219_rml17_transport_abi_1_30.h"
#include "hhs_pass219_discrete_transport_conservation_1_29.hpp"

#include <cstdint>

namespace {

using hhs::pass219::transport::DirectedAddress;
using hhs::pass219::transport::Direction;
using hhs::pass219::transport::Node;

bool valid_c_address(const HHSPass219RML17TransportAddressV1& address) noexcept {
    return address.operation64 < HHS_PASS219_RML17_TRANSPORT_OPERATION_COUNT &&
           address.phase72 < HHS_PASS219_RML17_TRANSPORT_PHASE_COUNT &&
           address.cell81 < HHS_PASS219_RML17_TRANSPORT_CELL_COUNT &&
           address.direction4 < HHS_PASS219_RML17_TRANSPORT_DIRECTION_COUNT;
}

DirectedAddress to_cpp(const HHSPass219RML17TransportAddressV1& address) noexcept {
    return DirectedAddress{
        Node{address.operation64, address.phase72, address.cell81},
        static_cast<Direction>(address.direction4),
    };
}

HHSPass219RML17TransportAddressV1 to_c(const DirectedAddress& address) noexcept {
    return HHSPass219RML17TransportAddressV1{
        address.node.operation64,
        address.node.phase72,
        address.node.cell81,
        static_cast<std::uint8_t>(address.direction),
    };
}

HHSPass219RML17TransportParityRowV1 parity_row(std::uint64_t source_index) noexcept {
    const DirectedAddress source = hhs::pass219::transport::unflatten_address(source_index);
    const auto edge = hhs::pass219::transport::witness_edge(source);
    return HHSPass219RML17TransportParityRowV1{
        source_index,
        hhs::pass219::transport::flatten_address(edge.target),
        to_c(source),
        to_c(edge.target),
        edge.source_flux,
        static_cast<std::uint8_t>(edge.target.direction),
        static_cast<std::uint8_t>(edge.zero_canonical_diffusion),
        static_cast<std::uint8_t>(edge.exact_reverse_restores_source),
    };
}

}  // namespace

extern "C" {

uint32_t hhs_pass219_rml17_transport_abi_version(void) {
    return (HHS_PASS219_RML17_TRANSPORT_ABI_VERSION_MAJOR << 16U) |
           (HHS_PASS219_RML17_TRANSPORT_ABI_VERSION_MINOR << 8U) |
           HHS_PASS219_RML17_TRANSPORT_ABI_VERSION_PATCH;
}

uint64_t hhs_pass219_rml17_transport_node_count(void) {
    return hhs::pass219::transport::kNodeCount;
}

uint64_t hhs_pass219_rml17_transport_address_count(void) {
    return hhs::pass219::transport::kAddressCount;
}

int hhs_pass219_rml17_transport_flatten(
    const HHSPass219RML17TransportAddressV1* address,
    uint64_t* out_index
) {
    if (address == nullptr || out_index == nullptr || !valid_c_address(*address))
        return 0;
    *out_index = hhs::pass219::transport::flatten_address(to_cpp(*address));
    return 1;
}

int hhs_pass219_rml17_transport_unflatten(
    uint64_t index,
    HHSPass219RML17TransportAddressV1* out_address
) {
    if (out_address == nullptr || index >= hhs::pass219::transport::kAddressCount)
        return 0;
    *out_address = to_c(hhs::pass219::transport::unflatten_address(index));
    return 1;
}

int hhs_pass219_rml17_transport_signed_flux(uint8_t direction4, int8_t* out_flux) {
    if (out_flux == nullptr || direction4 >= HHS_PASS219_RML17_TRANSPORT_DIRECTION_COUNT)
        return 0;
    *out_flux = hhs::pass219::transport::signed_flux(static_cast<Direction>(direction4));
    return 1;
}

int hhs_pass219_rml17_transport_reciprocal(uint8_t direction4, uint8_t* out_direction4) {
    if (out_direction4 == nullptr || direction4 >= HHS_PASS219_RML17_TRANSPORT_DIRECTION_COUNT)
        return 0;
    *out_direction4 = static_cast<std::uint8_t>(
        hhs::pass219::transport::reciprocal(static_cast<Direction>(direction4))
    );
    return 1;
}

int hhs_pass219_rml17_transport_successor(
    const HHSPass219RML17TransportAddressV1* source,
    HHSPass219RML17TransportAddressV1* out_target
) {
    if (source == nullptr || out_target == nullptr || !valid_c_address(*source))
        return 0;
    *out_target = to_c(hhs::pass219::transport::directed_successor(to_cpp(*source)));
    return 1;
}

int hhs_pass219_rml17_transport_zero_diffusion(
    const HHSPass219RML17TransportAddressV1* source,
    uint8_t* out_zero_diffusion
) {
    if (source == nullptr || out_zero_diffusion == nullptr || !valid_c_address(*source))
        return 0;
    const auto witness = hhs::pass219::transport::witness_edge(to_cpp(*source));
    *out_zero_diffusion = static_cast<std::uint8_t>(
        witness.zero_canonical_diffusion && witness.exact_reverse_restores_source
    );
    return 1;
}

int hhs_pass219_rml17_transport_export_parity_rows(
    uint64_t start_index,
    uint64_t row_count,
    HHSPass219RML17TransportParityRowV1* out_rows
) {
    if (out_rows == nullptr || start_index > hhs::pass219::transport::kAddressCount)
        return 0;
    if (row_count > hhs::pass219::transport::kAddressCount - start_index)
        return 0;
    for (std::uint64_t offset = 0U; offset < row_count; ++offset)
        out_rows[offset] = parity_row(start_index + offset);
    return 1;
}

int hhs_pass219_rml17_transport_audit(HHSPass219RML17TransportReportV1* out_report) {
    if (out_report == nullptr)
        return 0;
    const auto report = hhs::pass219::transport::audit_entire_address_manifold();
    *out_report = HHSPass219RML17TransportReportV1{
        report.node_count,
        report.address_count,
        report.discrete_divergence_nodes_checked,
        report.reciprocal_edge_addresses_checked,
        report.admission_preservation_addresses_checked,
        report.zero_diffusion_addresses_checked,
        report.composed_reverse_addresses_checked,
        report.unique_target_addresses,
        report.failure_count,
        static_cast<std::uint8_t>(report.discrete_divergence_gate),
        static_cast<std::uint8_t>(report.reciprocal_edge_balance_gate),
        static_cast<std::uint8_t>(report.admission_preservation_gate),
        static_cast<std::uint8_t>(report.zero_canonical_diffusion_gate),
        static_cast<std::uint8_t>(report.composed_reverse_closure_gate),
        static_cast<std::uint8_t>(report.exhaustive_address_coverage),
        static_cast<std::uint8_t>(report.target_map_bijective),
        static_cast<std::uint8_t>(report.exact_integer_phase_arithmetic),
        UINT8_C(0),
        static_cast<std::uint8_t>(report.canonical_vm81_mutation_authority),
        static_cast<std::uint8_t>(report.canonical_hash72_mint_authority),
        static_cast<std::uint8_t>(report.canonical_hash216_persistence_authority),
        static_cast<std::uint8_t>(report.pass),
    };
    return 1;
}

int hhs_pass219_rml17_transport_has_transition_authority(void) {
    return 0;
}

}  // extern "C"

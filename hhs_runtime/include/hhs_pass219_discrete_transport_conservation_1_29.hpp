#ifndef HHS_PASS219_DISCRETE_TRANSPORT_CONSERVATION_1_29_HPP
#define HHS_PASS219_DISCRETE_TRANSPORT_CONSERVATION_1_29_HPP

#include "hhs_pass219_rna_transcription_1_10.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <string>

namespace hhs::pass219::transport {

inline constexpr std::uint32_t kVersionMajor = 1U;
inline constexpr std::uint32_t kVersionMinor = 29U;
inline constexpr std::uint32_t kVersionPatch = 0U;

inline constexpr std::uint32_t kOperationCount = HHS_EXACT_PASS219_OPERATION64_COUNT;
inline constexpr std::uint32_t kPhaseCount = 72U;
inline constexpr std::uint32_t kCellCount = HHS_EXACT_VM81_CELLS;
inline constexpr std::uint32_t kDirectionCount = 4U;
inline constexpr std::uint64_t kNodeCount =
    static_cast<std::uint64_t>(kOperationCount) * kPhaseCount * kCellCount;
inline constexpr std::uint64_t kAddressCount = kNodeCount * kDirectionCount;

static_assert(kOperationCount == 64U);
static_assert(kPhaseCount == 72U);
static_assert(kCellCount == 81U);
static_assert(kDirectionCount == 4U);
static_assert(kNodeCount == UINT64_C(373248));
static_assert(kAddressCount == UINT64_C(1492992));
static_assert(HHS_EXACT_PHASE_BASIS_COUNT * HHS_EXACT_PHASE_BASIS_COUNT == kOperationCount);
static_assert(HHS_EXACT_HASH72_LEN == kPhaseCount);

enum class Direction : std::uint8_t {
    X = 0U,
    Y = 1U,
    Z = 2U,
    W = 3U,
};

/*
 * RML4 primitive orientation is compiled as data, not a direction switch:
 * x=+1, y=-1, z=-1, w=+1. Reciprocal edge pairs are x<->y and z<->w.
 */
inline constexpr std::array<std::int8_t, kDirectionCount> kSignedFlux = {
    INT8_C(1), INT8_C(-1), INT8_C(-1), INT8_C(1)
};
inline constexpr std::array<Direction, kDirectionCount> kReciprocalDirection = {
    Direction::Y, Direction::X, Direction::W, Direction::Z
};
inline constexpr std::array<const char*, kDirectionCount> kDirectionName = {
    "x", "y", "z", "w"
};

struct Node final {
    std::uint8_t operation64{};
    std::uint8_t phase72{};
    std::uint8_t cell81{};

    constexpr bool operator==(const Node&) const noexcept = default;
};

struct DirectedAddress final {
    Node node{};
    Direction direction{Direction::X};

    constexpr bool operator==(const DirectedAddress&) const noexcept = default;
};

struct EdgeWitness final {
    DirectedAddress source{};
    DirectedAddress target{};
    std::int8_t source_flux{};
    std::int8_t reciprocal_flux{};
    bool discrete_divergence_zero{};
    bool reciprocal_edge_balance{};
    bool admission_visible_coordinates_preserved{};
    bool zero_canonical_diffusion{};
    bool exact_reverse_restores_source{};
};

struct ContractReport final {
    std::uint64_t node_count{};
    std::uint64_t address_count{};
    std::uint64_t discrete_divergence_nodes_checked{};
    std::uint64_t reciprocal_edge_addresses_checked{};
    std::uint64_t admission_preservation_addresses_checked{};
    std::uint64_t zero_diffusion_addresses_checked{};
    std::uint64_t composed_reverse_addresses_checked{};
    std::uint64_t unique_target_addresses{};
    std::uint64_t failure_count{};

    bool discrete_divergence_gate{};
    bool reciprocal_edge_balance_gate{};
    bool admission_preservation_gate{};
    bool zero_canonical_diffusion_gate{};
    bool composed_reverse_closure_gate{};
    bool exhaustive_address_coverage{};
    bool target_map_bijective{};
    bool table_driven_direction_logic{};
    bool exact_integer_phase_arithmetic{};
    bool rna_admission_authority_delegated{};
    bool rna_admission_anchor_verified{};
    bool rna_record_immutable_under_transport{};

    bool lossy_compression_used{};
    bool neighbor_averaging_used{};
    bool hash216_cryptographic_inversion_used{};
    bool canonical_vm81_mutation_authority{};
    bool canonical_hash72_mint_authority{};
    bool canonical_hash216_persistence_authority{};
    bool floating_point_canonical_authority{};
    bool scalar_projection_substitution_authority{};
    bool timing_authority{};
    bool pass{};
};

constexpr std::size_t direction_index(Direction direction) noexcept {
    return static_cast<std::size_t>(direction);
}

constexpr bool valid_node(const Node& node) noexcept {
    return node.operation64 < kOperationCount &&
           node.phase72 < kPhaseCount &&
           node.cell81 < kCellCount;
}

constexpr bool valid_direction(Direction direction) noexcept {
    return direction_index(direction) < kDirectionCount;
}

constexpr std::int8_t signed_flux(Direction direction) noexcept {
    return kSignedFlux[direction_index(direction)];
}

constexpr Direction reciprocal(Direction direction) noexcept {
    return kReciprocalDirection[direction_index(direction)];
}

constexpr std::uint8_t left_basis_from_operation(std::uint8_t operation64) noexcept {
    return static_cast<std::uint8_t>(operation64 / HHS_EXACT_PHASE_BASIS_COUNT);
}

constexpr std::uint8_t right_basis_from_operation(std::uint8_t operation64) noexcept {
    return static_cast<std::uint8_t>(operation64 % HHS_EXACT_PHASE_BASIS_COUNT);
}

constexpr std::uint8_t operation_from_bases(std::uint8_t left, std::uint8_t right) noexcept {
    return static_cast<std::uint8_t>(left * HHS_EXACT_PHASE_BASIS_COUNT + right);
}

Node step(const Node& source, Direction direction) noexcept;
DirectedAddress directed_successor(const DirectedAddress& source) noexcept;
std::uint64_t flatten_address(const DirectedAddress& address) noexcept;
DirectedAddress unflatten_address(std::uint64_t index) noexcept;
EdgeWitness witness_edge(const DirectedAddress& source) noexcept;
bool divergence_zero(const Node& source) noexcept;
bool reverse_sequence_restores(
    const Node& source,
    const Direction* directions,
    std::size_t count
) noexcept;
bool rna_admission_anchor_matches(
    const RNAAdmissionView& admission,
    const Node& source
) noexcept;
ContractReport audit_entire_address_manifold();
std::string report_json(const ContractReport& report);

}  // namespace hhs::pass219::transport

#endif

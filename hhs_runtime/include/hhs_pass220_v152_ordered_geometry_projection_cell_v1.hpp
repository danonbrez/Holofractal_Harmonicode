#ifndef HHS_PASS220_V152_ORDERED_GEOMETRY_PROJECTION_CELL_V1_HPP
#define HHS_PASS220_V152_ORDERED_GEOMETRY_PROJECTION_CELL_V1_HPP

/* Additive typed V152 physical-coordinate projection boundary.
 * Inherits the frozen I059 GeometryCellWall and RenderCellWall.
 * Float32LE is *observable output*, not an authoritative exact transform.
 * No VM81/Hash72/Hash216 minting or physics tick scheduling occurs here.
 */
#include "hhs_pass220_native_3d_engine_cell_wall_1_0.hpp"

#include <cstddef>
#include <cstdint>
#include <limits>

namespace hhs::game::v152 {

inline constexpr std::uint32_t kRequiredParticles = 10368U;
inline constexpr std::uint32_t kComponents = 3U;
inline constexpr std::size_t kPositionBytes =
    static_cast<std::size_t>(kRequiredParticles) * kComponents * sizeof(std::uint32_t);

enum class ProjectionDecision : std::uint8_t {
    Accepted = 0U,
    Missing = 1U,
    Length = 2U,
    Tick = 3U,
    FloatNonfinite = 4U,
    FrozenCellRejected = 5U
};

struct OrderedProjectionCandidate final {
    const std::uint8_t* position_f32le{};
    std::size_t position_bytes{};
    std::uint32_t particle_count{};
    std::uint64_t producer_tick{};
    std::uint64_t geometry_tick{};
    std::uint64_t render_tick{};
    std::uint8_t projection_only{1U};
    std::uint8_t canonical_mutation_requested{};
};

struct OrderedProjectionWitness final {
    ProjectionDecision decision{ProjectionDecision::Missing};
    std::uint64_t producer_tick{};
    std::uint32_t particle_count{};
    std::size_t consumed_bytes{};
    std::uint32_t checked_components{};
    std::uint8_t inherited_geometry_cell_accepted{};
    std::uint8_t inherited_render_cell_accepted{};
    std::uint8_t exact_vm81_admission{};
    std::uint8_t physical_source_provenance_verified{};
    std::uint8_t hash216_mutation_authority{};
    std::uint8_t physics_mutation_authority{};
};

inline std::uint32_t read_u32le(const std::uint8_t* p) noexcept {
    return static_cast<std::uint32_t>(p[0]) |
        (static_cast<std::uint32_t>(p[1]) << 8U) |
        (static_cast<std::uint32_t>(p[2]) << 16U) |
        (static_cast<std::uint32_t>(p[3]) << 24U);
}

inline OrderedProjectionWitness validate(
    const OrderedProjectionCandidate& candidate
) noexcept {
    OrderedProjectionWitness witness{};
    witness.producer_tick = candidate.producer_tick;
    witness.particle_count = candidate.particle_count;
    if (candidate.position_f32le == nullptr) return witness;
    if (candidate.particle_count != kRequiredParticles ||
        candidate.position_bytes != kPositionBytes) {
        witness.decision = ProjectionDecision::Length;
        return witness;
    }
    if (candidate.producer_tick != candidate.geometry_tick ||
        candidate.producer_tick != candidate.render_tick ||
        candidate.projection_only != 1U ||
        candidate.canonical_mutation_requested != 0U) {
        witness.decision = ProjectionDecision::Tick;
        return witness;
    }
    // Float32 bits are checked without floating arithmetic; NaNs and
    // infinities have all exponent bits set. Both signed zeros are retained.
    for (std::size_t offset = 0U; offset < kPositionBytes; offset += 4U) {
        const std::uint32_t bits = read_u32le(candidate.position_f32le + offset);
        if ((bits & UINT32_C(0x7f800000)) == UINT32_C(0x7f800000)) {
            witness.decision = ProjectionDecision::FloatNonfinite;
            return witness;
        }
    }
    WorldCandidate world{};
    world.tick = candidate.producer_tick;
    GeometryCandidate geometry{};
    geometry.tick = candidate.geometry_tick;
    geometry.mesh_count = 1U;
    geometry.procedural_mesh_count = 1U;
    RenderCandidate render{};
    render.tick = candidate.render_tick;
    render.draw_batch_count = 1U;
    render.camera_count = 1U;
    EngineCellReceipt geometry_receipt{};
    EngineCellReceipt render_receipt{};
    const GeometryCellWall geometry_wall{};
    const RenderCellWall render_wall{};
    if (geometry_wall.evaluate(world, geometry, geometry_receipt) != HHS_EXACT_STATUS_OK ||
        render_wall.evaluate(world, render, render_receipt) != HHS_EXACT_STATUS_OK ||
        geometry_receipt.accepted != 1U || render_receipt.accepted != 1U) {
        witness.decision = ProjectionDecision::FrozenCellRejected;
        return witness;
    }
    witness.decision = ProjectionDecision::Accepted;
    witness.consumed_bytes = kPositionBytes;
    witness.checked_components = kRequiredParticles * kComponents;
    witness.inherited_geometry_cell_accepted = 1U;
    witness.inherited_render_cell_accepted = 1U;
    // This validates only projection shape/lineage. A VM81 receipt
    // and trusted source binding must be supplied by the existing authority.
    return witness;
}

} // namespace hhs::game::v152

#endif

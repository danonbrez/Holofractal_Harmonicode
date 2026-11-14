#ifndef HHS_PASS220_V153_GEOMETRY_RESOURCE_BINDING_CELL_V1_HPP
#define HHS_PASS220_V153_GEOMETRY_RESOURCE_BINDING_CELL_V1_HPP

/* Additive ordered physical geometry -> GFX4 draw-resource preflight.
 * This does not establish provenance or mint VM81/Hash72/Hash216 receipts.
 * Trusted source and admitted resource checks MUST come from the inherited
 * Lane 5/GFX4 authority before this candidate can be presented as admitted.
 */
#include "hhs_pass220_v152_ordered_geometry_projection_cell_v1.hpp"
#include <cstddef>
#include <cstdint>

namespace hhs::game::v153 {

enum class BindingDecision : std::uint8_t {
    Prepared = 0U, Missing = 1U, ProjectionRejected = 2U,
    SourceMismatch = 3U, ResourceMismatch = 4U, AuthorityRequired = 5U
};

struct GeometryResourceCandidate final {
    v152::OrderedProjectionCandidate projection{};
    const std::uint8_t* source_position_f32le{};
    std::size_t source_position_bytes{};
    std::uint64_t source_producer_tick{};
    std::uint64_t gfx4_draw_resource_id{};
    std::uint64_t scene_resource_id{};
    std::uint64_t source_geometry_resource_id{};
    // A caller-controlled boolean is never a sufficient trust witness.
    std::uint8_t client_claims_native_admission{};
};

struct GeometryResourcePreflight final {
    BindingDecision decision{BindingDecision::Missing};
    v152::ProjectionDecision projection_decision{v152::ProjectionDecision::Missing};
    std::uint64_t producer_tick{};
    std::uint64_t draw_resource_id{};
    std::size_t compared_bytes{};
    std::uint8_t source_content_equal{};
    std::uint8_t exact_vm81_admission{};
    std::uint8_t physical_source_provenance_verified{};
    std::uint8_t hash216_mutation_authority{};
    std::uint8_t physics_mutation_authority{};
};

inline GeometryResourcePreflight prepare(
    const GeometryResourceCandidate& candidate
) noexcept {
    GeometryResourcePreflight result{};
    result.producer_tick = candidate.projection.producer_tick;
    result.draw_resource_id = candidate.gfx4_draw_resource_id;
    const auto projection = v152::validate(candidate.projection);
    result.projection_decision = projection.decision;
    if (projection.decision != v152::ProjectionDecision::Accepted) {
        result.decision = BindingDecision::ProjectionRejected;
        return result;
    }
    if (candidate.source_position_f32le == nullptr) return result;
    if (candidate.source_position_bytes != v152::kPositionBytes ||
        candidate.source_producer_tick != candidate.projection.producer_tick) {
        result.decision = BindingDecision::SourceMismatch;
        return result;
    }
    if (candidate.gfx4_draw_resource_id == 0U ||
        candidate.scene_resource_id == 0U ||
        candidate.source_geometry_resource_id == 0U ||
        candidate.gfx4_draw_resource_id != candidate.scene_resource_id ||
        candidate.gfx4_draw_resource_id != candidate.source_geometry_resource_id) {
        result.decision = BindingDecision::ResourceMismatch;
        return result;
    }
    // Exact ordered byte comparison, retaining signed zero and particle order.
    // This comparison is NOT proof of trusted origin.
    for (std::size_t i = 0U; i < v152::kPositionBytes; ++i) {
        if (candidate.projection.position_f32le[i] != candidate.source_position_f32le[i]) {
            result.decision = BindingDecision::SourceMismatch;
            return result;
        }
    }
    result.compared_bytes = v152::kPositionBytes;
    result.source_content_equal = 1U;
    // Reject any attempt to promote a browser/client assertion to authority.
    if (candidate.client_claims_native_admission != 0U) {
        result.decision = BindingDecision::AuthorityRequired;
        return result;
    }
    result.decision = BindingDecision::Prepared;
    return result;
}

} // namespace hhs::game::v153

#endif

#include "hhs_pass220_v156_ordered_geometry_resource_transfer_v1.hpp"
#include <cassert>
#include <cstdint>
#include <vector>

using namespace hhs::game;

int main() {
    std::vector<std::uint8_t> positions(v152::kPositionBytes, 0U);
    std::vector<std::uint8_t> source(positions);
    positions[3] = 0x80U; source[3] = 0x80U;  // negative zero bit identity
    positions[7] = 0x01U; source[7] = 0x01U;
    v153::GeometryResourceCandidate candidate{};
    candidate.projection.position_f32le = positions.data();
    candidate.projection.position_bytes = positions.size();
    candidate.projection.particle_count = v152::kRequiredParticles;
    candidate.projection.producer_tick = 144U;
    candidate.projection.geometry_tick = 144U;
    candidate.projection.render_tick = 144U;
    candidate.source_position_f32le = source.data();
    candidate.source_position_bytes = source.size();
    candidate.source_producer_tick = 144U;
    candidate.gfx4_draw_resource_id = 9U;
    candidate.scene_resource_id = 9U;
    candidate.source_geometry_resource_id = 9U;
    v156::OrderedGeometryResource::Payload owned{};
    auto result = v156::prepare_owned_resource(candidate, 144U, 9U, owned);
    assert(result.decision == v156::TransferDecision::Prepared);
    assert(result.copied_bytes == v152::kPositionBytes);
    assert(result.physical_source_provenance_verified == 0U);
    assert(result.vm81_admission_authority == 0U);
    assert(owned[3] == 0x80U && owned[7] == 0x01U);

    v156::OrderedGeometryResource resource(owned, 144U, 9U);
    assert(resource.size() == v152::kPositionBytes);
    assert(resource.producer_tick() == 144U);
    assert(resource.draw_resource_id() == 9U);
    positions[3] = 0U;
    assert(resource.data()[3] == 0x80U);
    assert(v156::prepare_owned_resource(candidate, 144U, 9U, owned).decision ==
           v156::TransferDecision::PreflightRejected);
    positions[3] = 0x80U;

    assert(v156::prepare_owned_resource(candidate, 145U, 9U, owned).decision ==
           v156::TransferDecision::StaleTick);
    assert(v156::prepare_owned_resource(candidate, 144U, 10U, owned).decision ==
           v156::TransferDecision::DrawResourceMismatch);
    candidate.client_claims_native_admission = 1U;
    assert(v156::prepare_owned_resource(candidate, 144U, 9U, owned).decision ==
           v156::TransferDecision::PreflightRejected);
    candidate.client_claims_native_admission = 0U;
    source[7] = 0x00U;
    assert(v156::prepare_owned_resource(candidate, 144U, 9U, owned).decision ==
           v156::TransferDecision::PreflightRejected);
}

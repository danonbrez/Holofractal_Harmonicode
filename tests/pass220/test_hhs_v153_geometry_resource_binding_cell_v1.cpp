#include "hhs_pass220_v153_geometry_resource_binding_cell_v1.hpp"
#include <cassert>
#include <cstdint>
#include <vector>

using namespace hhs::game;
int main() {
    std::vector<std::uint8_t> bytes(v152::kPositionBytes, 0U);
    std::vector<std::uint8_t> source(bytes);
    // Preserve bit-exact negative zero in an otherwise finite buffer.
    bytes[3] = source[3] = 0x80U;
    v153::GeometryResourceCandidate candidate{};
    candidate.projection.position_f32le = bytes.data();
    candidate.projection.position_bytes = bytes.size();
    candidate.projection.particle_count = v152::kRequiredParticles;
    candidate.projection.producer_tick = 72U;
    candidate.projection.geometry_tick = 72U;
    candidate.projection.render_tick = 72U;
    candidate.source_position_f32le = source.data();
    candidate.source_position_bytes = source.size();
    candidate.source_producer_tick = 72U;
    candidate.gfx4_draw_resource_id = 9U;
    candidate.scene_resource_id = 9U;
    candidate.source_geometry_resource_id = 9U;
    auto witness = v153::prepare(candidate);
    assert(witness.decision == v153::BindingDecision::Prepared);
    assert(witness.compared_bytes == v152::kPositionBytes);
    assert(witness.source_content_equal == 1U);
    assert(witness.exact_vm81_admission == 0U);
    assert(witness.physical_source_provenance_verified == 0U);
    assert(witness.hash216_mutation_authority == 0U);
    assert(witness.physics_mutation_authority == 0U);

    source[3] = 0U;
    assert(v153::prepare(candidate).decision == v153::BindingDecision::SourceMismatch);
    source[3] = 0x80U;
    candidate.source_producer_tick = 73U;
    assert(v153::prepare(candidate).decision == v153::BindingDecision::SourceMismatch);
    candidate.source_producer_tick = 72U;
    candidate.scene_resource_id = 10U;
    assert(v153::prepare(candidate).decision == v153::BindingDecision::ResourceMismatch);
    candidate.scene_resource_id = 9U;
    candidate.client_claims_native_admission = 1U;
    assert(v153::prepare(candidate).decision == v153::BindingDecision::AuthorityRequired);
    candidate.client_claims_native_admission = 0U;
    candidate.projection.render_tick = 73U;
    assert(v153::prepare(candidate).decision == v153::BindingDecision::ProjectionRejected);
    candidate.projection.render_tick = 72U;
    bytes[3] = 0x7fU; bytes[2] = 0x80U; bytes[0] = 0U;
    assert(v153::prepare(candidate).decision == v153::BindingDecision::ProjectionRejected);
    bytes[3] = 0x80U; bytes[2] = 0U;
    assert(v153::prepare(candidate).decision == v153::BindingDecision::Prepared);
}

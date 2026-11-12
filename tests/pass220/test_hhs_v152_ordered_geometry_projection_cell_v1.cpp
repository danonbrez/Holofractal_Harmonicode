#include "hhs_pass220_v152_ordered_geometry_projection_cell_v1.hpp"

#include <cassert>
#include <cstddef>
#include <cstdint>
#include <vector>

using namespace hhs::game::v152;

int main() {
    static_assert(kPositionBytes == 10368U * 3U * 4U);
    std::vector<std::uint8_t> bytes(kPositionBytes, 0U);
    auto input = OrderedProjectionCandidate{};
    input.position_f32le = bytes.data();
    input.position_bytes = bytes.size();
    input.particle_count = 10368U;
    input.producer_tick = 100U;
    input.geometry_tick = 100U;
    input.render_tick = 100U;
    // The producer can preserve both positive and negative zero exactly.
    bytes[0] = 0U;
    bytes[1] = 0U;
    bytes[2] = 0U;
    bytes[3] = 0x80U;
    auto result = validate(input);
    assert(result.decision == ProjectionDecision::Accepted);
    assert(result.inherited_geometry_cell_accepted == 1U);
    assert(result.inherited_render_cell_accepted == 1U);
    assert(result.consumed_bytes == kPositionBytes);
    assert(result.checked_components == 10368U * 3U);
    assert(result.exact_vm81_admission == 0U);
    assert(result.physical_source_provenance_verified == 0U);
    assert(result.hash216_mutation_authority == 0U);
    assert(result.physics_mutation_authority == 0U);
    assert(read_u32le(bytes.data()) == UINT32_C(0x80000000));

    input.render_tick = 101U;
    assert(validate(input).decision == ProjectionDecision::Tick);
    input.render_tick = 100U;
    input.canonical_mutation_requested = 1U;
    assert(validate(input).decision == ProjectionDecision::Tick);
    input.canonical_mutation_requested = 0U;
    input.position_bytes -= 4U;
    assert(validate(input).decision == ProjectionDecision::Length);
    input.position_bytes += 4U;
    input.position_f32le = nullptr;
    assert(validate(input).decision == ProjectionDecision::Missing);
    input.position_f32le = bytes.data();
    bytes[3] = 0x7fU;
    bytes[2] = 0x80U; // +Infinity = 0x7f800000
    assert(validate(input).decision == ProjectionDecision::FloatNonfinite);
    bytes[0] = 1U; // NaN
    assert(validate(input).decision == ProjectionDecision::FloatNonfinite);
    bytes[0] = 0U;
    bytes[2] = 0U;
    bytes[3] = 0U;
    assert(validate(input).decision == ProjectionDecision::Accepted);
}

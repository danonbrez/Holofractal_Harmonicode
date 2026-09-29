#include "hhs_pass220_native_3d_engine_cell_wall_1_0.hpp"

#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstring>

using namespace hhs::game;

namespace {

void fill_hash216(char (&out)[HHS_HASH216_LEN + 1], char symbol = '0') {
    for (std::size_t i = 0U; i < HHS_HASH216_LEN; ++i)
        out[i] = symbol;
    out[HHS_HASH216_LEN] = '\0';
}

EnginePipelineCandidate valid_candidate() {
    EnginePipelineCandidate c{};

    c.world.tick = 42U;
    c.world.world_epoch = 7U;
    c.world.entity_count = 128U;
    c.world.active_entity_count = 96U;
    c.world.deterministic_replay_required = 1U;
    c.world.exact_transform_authority = 1U;
    fill_hash216(c.world.parent_hash216);

    c.physics.tick = c.world.tick;
    c.physics.body_count = 96U;
    c.physics.collider_count = 144U;
    c.physics.constraint_count = 64U;
    c.physics.delta_time = HHSExactRational64{1, 60U};
    c.physics.exact_state_required = 1U;

    c.geometry.tick = c.world.tick;
    c.geometry.mesh_count = 12U;
    c.geometry.procedural_mesh_count = 12U;
    c.geometry.imported_mesh_count = 0U;
    c.geometry.imported_sources_attested = 0U;
    c.geometry.exact_constructor_identity_required = 1U;

    c.render.tick = c.world.tick;
    c.render.draw_batch_count = 32U;
    c.render.light_count = 8U;
    c.render.camera_count = 2U;
    c.render.layered_shader_count = 6U;
    c.render.projection_only = 1U;
    c.render.interpolation_allowed = 1U;

    c.script.tick = c.world.tick;
    c.script.registered_class_count = 4U;
    c.script.active_behavior_count = 16U;
    c.script.classes_registered_through_rna = 1U;
    c.script.instance_mutations_require_admission = 1U;

    c.compute.tick = c.world.tick;
    c.compute.python_lane_mask = 0x03U;
    c.compute.numpy_enabled = 1U;
    c.compute.matplotlib_enabled = 1U;
    c.compute.gpu_candidate_lane_enabled = 1U;

    c.asset.tick = c.world.tick;
    c.asset.asset_count = 9U;
    c.asset.external_asset_count = 0U;
    c.asset.procedural_asset_count = 9U;
    c.asset.external_sources_attested = 0U;
    c.asset.stable_asset_identity_required = 1U;

    return c;
}

void test_descriptor() {
    constexpr auto d = Native3DEngineCellWall::descriptor();
    static_assert(d.required_cell_mask == kRequiredCellMask);
    static_assert(d.vm81_cells == 81U);
    static_assert(d.operation64 == 64U);
    static_assert(d.frame_bits == 5184U);
    static_assert(d.hash72_coordinates == 5184U);
    static_assert(d.q144_positions == 144U);
    static_assert(d.frozen_i057_renderer == 1U);
    static_assert(d.inherited_i058_equation_mechanics == 1U);
    static_assert(d.exact_state_uses_host_float == 0U);
}

void test_exact_transform_validation() {
    ExactTransform t{};
    t.position.x = HHSExactRational64{3, 2U};
    t.position.y = HHSExactRational64{-4, 3U};
    t.position.z = HHSExactRational64{5, 7U};
    t.address5184 = 5183U;
    t.q144_index = 143U;
    t.phase_left8 = 7U;
    t.phase_right8 = 7U;
    assert(EngineFoundationValidation::valid_transform(t));

    t.address5184 = 5184U;
    assert(!EngineFoundationValidation::valid_transform(t));
}

void test_full_pipeline_accepts() {
    const auto candidate = valid_candidate();
    Native3DEngineCellWall wall{};
    EnginePipelineReceipt receipt{};

    const HHSExactStatus status = wall.evaluate(candidate, receipt);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(receipt.accepted == 1U);
    assert(receipt.completed_cell_mask == kRequiredCellMask);
    assert(receipt.failed_cell_mask == 0U);
    assert(receipt.deterministic_replay_required == 1U);
    assert(receipt.exact_state_preserved == 1U);
    assert(receipt.frozen_i057_renderer_preserved == 1U);
    assert(receipt.inherited_i058_mechanics_preserved == 1U);
    assert(receipt.candidate_only == 1U);
    assert(receipt.canonical_vm81_mutation_authority == 0U);
    assert(receipt.canonical_hash72_authority == 0U);
    assert(receipt.canonical_hash216_authority == 0U);
    assert(receipt.canonical_persistence_authority == 0U);
    assert(receipt.floating_point_canonical_authority == 0U);
    assert(std::memcmp(
        receipt.parent_hash216,
        candidate.world.parent_hash216,
        HHS_HASH216_LEN + 1U) == 0);

    for (const auto& cell : receipt.cell_receipts) {
        assert(cell.accepted == 1U);
        assert(cell.exact_input_verified == 1U);
        assert(cell.tick_lineage_verified == 1U);
        assert(cell.parent_identity_preserved == 1U);
        assert(cell.candidate_only == 1U);
        assert(cell.canonical_vm81_mutation_authority == 0U);
        assert(cell.canonical_hash72_authority == 0U);
        assert(cell.canonical_hash216_authority == 0U);
        assert(cell.canonical_persistence_authority == 0U);
        assert(cell.floating_point_canonical_authority == 0U);
    }
}

void test_fail_closed_tick_drift() {
    auto candidate = valid_candidate();
    candidate.physics.tick++;
    Native3DEngineCellWall wall{};
    EnginePipelineReceipt receipt{};
    assert(wall.evaluate(candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(receipt.accepted == 0U);
    assert((receipt.failed_cell_mask & kCellPhysics) != 0U);
}

void test_fail_closed_physics_float_authority() {
    auto candidate = valid_candidate();
    candidate.physics.host_float_authority_requested = 1U;
    Native3DEngineCellWall wall{};
    EnginePipelineReceipt receipt{};
    assert(wall.evaluate(candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert((receipt.failed_cell_mask & kCellPhysics) != 0U);
}

void test_fail_closed_render_authority() {
    auto candidate = valid_candidate();
    candidate.render.canonical_mutation_authority_requested = 1U;
    Native3DEngineCellWall wall{};
    EnginePipelineReceipt receipt{};
    assert(wall.evaluate(candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert((receipt.failed_cell_mask & kCellRender) != 0U);
}

void test_fail_closed_unregistered_script_class() {
    auto candidate = valid_candidate();
    candidate.script.classes_registered_through_rna = 0U;
    Native3DEngineCellWall wall{};
    EnginePipelineReceipt receipt{};
    assert(wall.evaluate(candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert((receipt.failed_cell_mask & kCellScript) != 0U);
}

void test_fail_closed_compute_authority() {
    auto candidate = valid_candidate();
    candidate.compute.canonical_arithmetic_authority_requested = 1U;
    Native3DEngineCellWall wall{};
    EnginePipelineReceipt receipt{};
    assert(wall.evaluate(candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert((receipt.failed_cell_mask & kCellCompute) != 0U);
}

void test_external_geometry_requires_attestation() {
    auto candidate = valid_candidate();
    candidate.geometry.mesh_count = 4U;
    candidate.geometry.procedural_mesh_count = 3U;
    candidate.geometry.imported_mesh_count = 1U;
    candidate.geometry.imported_sources_attested = 0U;

    Native3DEngineCellWall wall{};
    EnginePipelineReceipt receipt{};
    assert(wall.evaluate(candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert((receipt.failed_cell_mask & kCellGeometry) != 0U);

    candidate.geometry.imported_sources_attested = 1U;
    receipt = EnginePipelineReceipt{};
    assert(wall.evaluate(candidate, receipt) == HHS_EXACT_STATUS_OK);
}

void test_external_assets_require_attestation() {
    auto candidate = valid_candidate();
    candidate.asset.asset_count = 3U;
    candidate.asset.procedural_asset_count = 2U;
    candidate.asset.external_asset_count = 1U;
    candidate.asset.external_sources_attested = 0U;

    Native3DEngineCellWall wall{};
    EnginePipelineReceipt receipt{};
    assert(wall.evaluate(candidate, receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert((receipt.failed_cell_mask & kCellAsset) != 0U);

    candidate.asset.external_sources_attested = 1U;
    receipt = EnginePipelineReceipt{};
    assert(wall.evaluate(candidate, receipt) == HHS_EXACT_STATUS_OK);
}

void test_invalid_parent_identity_fails_before_pipeline() {
    auto candidate = valid_candidate();
    candidate.world.parent_hash216[12] = '\0';

    Native3DEngineCellWall wall{};
    EnginePipelineReceipt receipt{};
    assert(wall.evaluate(candidate, receipt) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    assert((receipt.failed_cell_mask & kCellWorld) != 0U);
    assert(receipt.completed_cell_mask == 0U);
}

}  // namespace

int main() {
    test_descriptor();
    test_exact_transform_validation();
    test_full_pipeline_accepts();
    test_fail_closed_tick_drift();
    test_fail_closed_physics_float_authority();
    test_fail_closed_render_authority();
    test_fail_closed_unregistered_script_class();
    test_fail_closed_compute_authority();
    test_external_geometry_requires_attestation();
    test_external_assets_require_attestation();
    test_invalid_parent_identity_fails_before_pipeline();
    return 0;
}

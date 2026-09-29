#ifndef HHS_PASS220_NATIVE_3D_ENGINE_CELL_WALL_1_0_HPP
#define HHS_PASS220_NATIVE_3D_ENGINE_CELL_WALL_1_0_HPP

#include "hhs_runtime_exact_abi_v1_1_base.h"
#include "hhs_hash216.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace hhs::game {

inline constexpr std::uint32_t kEngineFoundationVersion = UINT32_C(0x00010000);
inline constexpr std::uint32_t kEngineFoundationNamespace = UINT32_C(0x00022059);

inline constexpr std::uint32_t kCellWorld    = UINT32_C(1) << 0U;
inline constexpr std::uint32_t kCellPhysics  = UINT32_C(1) << 1U;
inline constexpr std::uint32_t kCellGeometry = UINT32_C(1) << 2U;
inline constexpr std::uint32_t kCellRender   = UINT32_C(1) << 3U;
inline constexpr std::uint32_t kCellScript   = UINT32_C(1) << 4U;
inline constexpr std::uint32_t kCellCompute  = UINT32_C(1) << 5U;
inline constexpr std::uint32_t kCellAsset    = UINT32_C(1) << 6U;
inline constexpr std::uint32_t kRequiredCellMask =
    kCellWorld | kCellPhysics | kCellGeometry | kCellRender |
    kCellScript | kCellCompute | kCellAsset;

inline constexpr std::uint32_t kMaxEntities = UINT32_C(1048576);
inline constexpr std::uint32_t kMaxBodies = UINT32_C(1048576);
inline constexpr std::uint32_t kMaxColliders = UINT32_C(4194304);
inline constexpr std::uint32_t kMaxConstraints = UINT32_C(4194304);
inline constexpr std::uint32_t kMaxMeshes = UINT32_C(1048576);
inline constexpr std::uint32_t kMaxDrawBatches = UINT32_C(1048576);
inline constexpr std::uint32_t kMaxLights = UINT32_C(65536);
inline constexpr std::uint32_t kMaxCameras = UINT32_C(4096);
inline constexpr std::uint32_t kMaxScriptClasses = UINT32_C(1048576);
inline constexpr std::uint32_t kMaxAssets = UINT32_C(1048576);

enum class EngineCellKind : std::uint8_t {
    World = 0U,
    Physics = 1U,
    Geometry = 2U,
    Render = 3U,
    Script = 4U,
    Compute = 5U,
    Asset = 6U,
};

struct EngineFoundationDescriptor final {
    std::uint32_t version{kEngineFoundationVersion};
    std::uint32_t namespace_id{kEngineFoundationNamespace};
    std::uint32_t required_cell_mask{kRequiredCellMask};
    std::uint32_t vm81_cells{HHS_EXACT_VM81_CELLS};
    std::uint32_t operation64{HHS_EXACT_PHASE_PAIR_COUNT};
    std::uint32_t frame_bits{HHS_EXACT_VM81_FRAME_BITS};
    std::uint32_t hash72_coordinates{HHS_EXACT_HASH72_COORDS};
    std::uint32_t q144_positions{144U};
    std::uint32_t frozen_i057_renderer{1U};
    std::uint32_t inherited_i058_equation_mechanics{1U};
    std::uint32_t exact_state_uses_host_float{0U};
    std::uint32_t renderer_has_canonical_mutation_authority{0U};
    std::uint32_t compute_has_canonical_mutation_authority{0U};
    std::uint32_t script_has_direct_canonical_mutation_authority{0U};
};

struct ExactVec3 final {
    HHSExactRational64 x{0, 1U};
    HHSExactRational64 y{0, 1U};
    HHSExactRational64 z{0, 1U};
};

struct ExactTransform final {
    ExactVec3 position{};
    ExactVec3 scale{
        HHSExactRational64{1, 1U},
        HHSExactRational64{1, 1U},
        HHSExactRational64{1, 1U},
    };
    std::uint16_t address5184{};
    std::uint8_t q144_index{};
    std::uint8_t phase_left8{};
    std::uint8_t phase_right8{};
};

struct WorldCandidate final {
    std::uint64_t tick{};
    std::uint64_t world_epoch{};
    std::uint32_t entity_count{};
    std::uint32_t active_entity_count{};
    std::uint8_t deterministic_replay_required{1U};
    std::uint8_t exact_transform_authority{1U};
    std::uint8_t reserved0{};
    std::uint8_t reserved1{};
    char parent_hash216[HHS_HASH216_LEN + 1]{};
};

struct PhysicsCandidate final {
    std::uint64_t tick{};
    std::uint32_t body_count{};
    std::uint32_t collider_count{};
    std::uint32_t constraint_count{};
    HHSExactRational64 delta_time{1, 60U};
    std::uint8_t exact_state_required{1U};
    std::uint8_t host_float_authority_requested{};
    std::uint8_t renderer_mutation_authority_requested{};
    std::uint8_t reserved0{};
};

struct GeometryCandidate final {
    std::uint64_t tick{};
    std::uint32_t mesh_count{};
    std::uint32_t procedural_mesh_count{};
    std::uint32_t imported_mesh_count{};
    std::uint8_t imported_sources_attested{};
    std::uint8_t exact_constructor_identity_required{1U};
    std::uint8_t external_geometry_authority_requested{};
    std::uint8_t reserved0{};
};

struct RenderCandidate final {
    std::uint64_t tick{};
    std::uint32_t draw_batch_count{};
    std::uint32_t light_count{};
    std::uint32_t camera_count{};
    std::uint32_t layered_shader_count{};
    std::uint8_t projection_only{1U};
    std::uint8_t interpolation_allowed{1U};
    std::uint8_t canonical_mutation_authority_requested{};
    std::uint8_t canonical_hash_authority_requested{};
};

struct ScriptCandidate final {
    std::uint64_t tick{};
    std::uint32_t registered_class_count{};
    std::uint32_t active_behavior_count{};
    std::uint8_t classes_registered_through_rna{1U};
    std::uint8_t instance_mutations_require_admission{1U};
    std::uint8_t direct_vm81_mutation_authority_requested{};
    std::uint8_t direct_hash_authority_requested{};
};

struct ComputeCandidate final {
    std::uint64_t tick{};
    std::uint8_t python_lane_mask{};
    std::uint8_t numpy_enabled{};
    std::uint8_t matplotlib_enabled{};
    std::uint8_t gpu_candidate_lane_enabled{};
    std::uint8_t canonical_arithmetic_authority_requested{};
    std::uint8_t canonical_mutation_authority_requested{};
    std::uint8_t canonical_hash_authority_requested{};
    std::uint8_t reserved0{};
};

struct AssetCandidate final {
    std::uint64_t tick{};
    std::uint32_t asset_count{};
    std::uint32_t external_asset_count{};
    std::uint32_t procedural_asset_count{};
    std::uint8_t external_sources_attested{};
    std::uint8_t stable_asset_identity_required{1U};
    std::uint8_t external_asset_authority_requested{};
    std::uint8_t reserved0{};
};

struct EnginePipelineCandidate final {
    WorldCandidate world{};
    PhysicsCandidate physics{};
    GeometryCandidate geometry{};
    RenderCandidate render{};
    ScriptCandidate script{};
    ComputeCandidate compute{};
    AssetCandidate asset{};
};

struct EngineCellReceipt final {
    std::uint32_t version{kEngineFoundationVersion};
    std::uint32_t namespace_id{kEngineFoundationNamespace};
    std::uint8_t cell_kind{};
    std::uint8_t accepted{};
    std::uint8_t exact_input_verified{};
    std::uint8_t tick_lineage_verified{};
    std::uint8_t parent_identity_preserved{};
    std::uint8_t candidate_only{1U};
    std::uint8_t canonical_vm81_mutation_authority{};
    std::uint8_t canonical_hash72_authority{};
    std::uint8_t canonical_hash216_authority{};
    std::uint8_t canonical_persistence_authority{};
    std::uint8_t floating_point_canonical_authority{};
    std::uint8_t reserved0{};
    std::uint8_t reserved1{};
    std::uint8_t reserved2{};
};

struct EnginePipelineReceipt final {
    std::uint32_t version{kEngineFoundationVersion};
    std::uint32_t namespace_id{kEngineFoundationNamespace};
    std::uint8_t accepted{};
    std::uint8_t deterministic_replay_required{};
    std::uint8_t exact_state_preserved{};
    std::uint8_t frozen_i057_renderer_preserved{};
    std::uint8_t inherited_i058_mechanics_preserved{};
    std::uint8_t candidate_only{1U};
    std::uint8_t canonical_vm81_mutation_authority{};
    std::uint8_t canonical_hash72_authority{};
    std::uint8_t canonical_hash216_authority{};
    std::uint8_t canonical_persistence_authority{};
    std::uint8_t floating_point_canonical_authority{};
    std::uint8_t reserved0{};
    std::uint32_t completed_cell_mask{};
    std::uint32_t failed_cell_mask{};
    std::array<EngineCellReceipt, 7U> cell_receipts{};
    char parent_hash216[HHS_HASH216_LEN + 1]{};
};

class EngineFoundationValidation final {
public:
    static bool valid_rational(const HHSExactRational64& value) noexcept {
        return value.denominator != 0U;
    }

    static bool positive_rational(const HHSExactRational64& value) noexcept {
        return valid_rational(value) && value.numerator > 0;
    }

    static bool valid_vec3(const ExactVec3& value) noexcept {
        return valid_rational(value.x) &&
               valid_rational(value.y) &&
               valid_rational(value.z);
    }

    static bool valid_transform(const ExactTransform& value) noexcept {
        return valid_vec3(value.position) &&
               valid_vec3(value.scale) &&
               value.scale.x.numerator != 0 &&
               value.scale.y.numerator != 0 &&
               value.scale.z.numerator != 0 &&
               value.address5184 < HHS_EXACT_HASH72_COORDS &&
               value.q144_index < 144U &&
               value.phase_left8 < HHS_EXACT_PHASE_BASIS_COUNT &&
               value.phase_right8 < HHS_EXACT_PHASE_BASIS_COUNT;
    }

    static bool valid_hash216_shape(
        const char value[HHS_HASH216_LEN + 1]
    ) noexcept {
        if (value == nullptr || value[HHS_HASH216_LEN] != '\0')
            return false;
        for (std::size_t i = 0U; i < HHS_HASH216_LEN; ++i) {
            if (value[i] == '\0')
                return false;
        }
        return true;
    }

    static void init_receipt(
        EngineCellKind kind,
        EngineCellReceipt& out
    ) noexcept {
        out = EngineCellReceipt{};
        out.cell_kind = static_cast<std::uint8_t>(kind);
    }

    static void accept(
        EngineCellReceipt& out,
        bool exact_input,
        bool tick_lineage,
        bool parent_identity
    ) noexcept {
        out.accepted = 1U;
        out.exact_input_verified = exact_input ? 1U : 0U;
        out.tick_lineage_verified = tick_lineage ? 1U : 0U;
        out.parent_identity_preserved = parent_identity ? 1U : 0U;
        out.candidate_only = 1U;
        out.canonical_vm81_mutation_authority = 0U;
        out.canonical_hash72_authority = 0U;
        out.canonical_hash216_authority = 0U;
        out.canonical_persistence_authority = 0U;
        out.floating_point_canonical_authority = 0U;
    }
};

class WorldCellWall final {
public:
    HHSExactStatus evaluate(
        const WorldCandidate& candidate,
        EngineCellReceipt& out
    ) const noexcept {
        EngineFoundationValidation::init_receipt(EngineCellKind::World, out);
        if (candidate.entity_count > kMaxEntities ||
            candidate.active_entity_count > candidate.entity_count)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        if (candidate.deterministic_replay_required != 1U ||
            candidate.exact_transform_authority != 1U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (!EngineFoundationValidation::valid_hash216_shape(
                candidate.parent_hash216))
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        EngineFoundationValidation::accept(out, true, true, true);
        return HHS_EXACT_STATUS_OK;
    }
};

class PhysicsCellWall final {
public:
    HHSExactStatus evaluate(
        const WorldCandidate& world,
        const PhysicsCandidate& candidate,
        EngineCellReceipt& out
    ) const noexcept {
        EngineFoundationValidation::init_receipt(EngineCellKind::Physics, out);
        if (candidate.tick != world.tick)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (candidate.body_count > world.entity_count ||
            candidate.body_count > kMaxBodies ||
            candidate.collider_count > kMaxColliders ||
            candidate.constraint_count > kMaxConstraints)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        if (!EngineFoundationValidation::positive_rational(candidate.delta_time))
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        if (candidate.exact_state_required != 1U ||
            candidate.host_float_authority_requested != 0U ||
            candidate.renderer_mutation_authority_requested != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        EngineFoundationValidation::accept(out, true, true, true);
        return HHS_EXACT_STATUS_OK;
    }
};

class GeometryCellWall final {
public:
    HHSExactStatus evaluate(
        const WorldCandidate& world,
        const GeometryCandidate& candidate,
        EngineCellReceipt& out
    ) const noexcept {
        EngineFoundationValidation::init_receipt(EngineCellKind::Geometry, out);
        if (candidate.tick != world.tick)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (candidate.mesh_count > kMaxMeshes ||
            candidate.procedural_mesh_count > candidate.mesh_count ||
            candidate.imported_mesh_count > candidate.mesh_count ||
            candidate.procedural_mesh_count + candidate.imported_mesh_count >
                candidate.mesh_count)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        if (candidate.imported_mesh_count > 0U &&
            candidate.imported_sources_attested != 1U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (candidate.exact_constructor_identity_required != 1U ||
            candidate.external_geometry_authority_requested != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        EngineFoundationValidation::accept(out, true, true, true);
        return HHS_EXACT_STATUS_OK;
    }
};

class RenderCellWall final {
public:
    HHSExactStatus evaluate(
        const WorldCandidate& world,
        const RenderCandidate& candidate,
        EngineCellReceipt& out
    ) const noexcept {
        EngineFoundationValidation::init_receipt(EngineCellKind::Render, out);
        if (candidate.tick != world.tick)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (candidate.draw_batch_count > kMaxDrawBatches ||
            candidate.light_count > kMaxLights ||
            candidate.camera_count > kMaxCameras)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        if (candidate.projection_only != 1U ||
            candidate.canonical_mutation_authority_requested != 0U ||
            candidate.canonical_hash_authority_requested != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        EngineFoundationValidation::accept(out, true, true, true);
        return HHS_EXACT_STATUS_OK;
    }
};

class ScriptCellWall final {
public:
    HHSExactStatus evaluate(
        const WorldCandidate& world,
        const ScriptCandidate& candidate,
        EngineCellReceipt& out
    ) const noexcept {
        EngineFoundationValidation::init_receipt(EngineCellKind::Script, out);
        if (candidate.tick != world.tick)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (candidate.registered_class_count > kMaxScriptClasses)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        if (candidate.registered_class_count > 0U &&
            candidate.classes_registered_through_rna != 1U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (candidate.instance_mutations_require_admission != 1U ||
            candidate.direct_vm81_mutation_authority_requested != 0U ||
            candidate.direct_hash_authority_requested != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        EngineFoundationValidation::accept(out, true, true, true);
        return HHS_EXACT_STATUS_OK;
    }
};

class ComputeCellWall final {
public:
    HHSExactStatus evaluate(
        const WorldCandidate& world,
        const ComputeCandidate& candidate,
        EngineCellReceipt& out
    ) const noexcept {
        EngineFoundationValidation::init_receipt(EngineCellKind::Compute, out);
        if (candidate.tick != world.tick)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if ((candidate.python_lane_mask & static_cast<std::uint8_t>(~0x03U)) != 0U)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        if (candidate.canonical_arithmetic_authority_requested != 0U ||
            candidate.canonical_mutation_authority_requested != 0U ||
            candidate.canonical_hash_authority_requested != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        EngineFoundationValidation::accept(out, true, true, true);
        return HHS_EXACT_STATUS_OK;
    }
};

class AssetCellWall final {
public:
    HHSExactStatus evaluate(
        const WorldCandidate& world,
        const AssetCandidate& candidate,
        EngineCellReceipt& out
    ) const noexcept {
        EngineFoundationValidation::init_receipt(EngineCellKind::Asset, out);
        if (candidate.tick != world.tick)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (candidate.asset_count > kMaxAssets ||
            candidate.external_asset_count > candidate.asset_count ||
            candidate.procedural_asset_count > candidate.asset_count ||
            candidate.external_asset_count + candidate.procedural_asset_count >
                candidate.asset_count)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        if (candidate.external_asset_count > 0U &&
            candidate.external_sources_attested != 1U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (candidate.stable_asset_identity_required != 1U ||
            candidate.external_asset_authority_requested != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        EngineFoundationValidation::accept(out, true, true, true);
        return HHS_EXACT_STATUS_OK;
    }
};

class Native3DEngineCellWall final {
public:
    static constexpr EngineFoundationDescriptor descriptor() noexcept {
        return EngineFoundationDescriptor{};
    }

    HHSExactStatus evaluate(
        const EnginePipelineCandidate& candidate,
        EnginePipelineReceipt& out
    ) const noexcept {
        out = EnginePipelineReceipt{};
        out.deterministic_replay_required =
            candidate.world.deterministic_replay_required;
        out.exact_state_preserved = candidate.world.exact_transform_authority;
        out.frozen_i057_renderer_preserved = 1U;
        out.inherited_i058_mechanics_preserved = 1U;

        if (!EngineFoundationValidation::valid_hash216_shape(
                candidate.world.parent_hash216)) {
            out.failed_cell_mask |= kCellWorld;
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        }

        std::memcpy(
            out.parent_hash216,
            candidate.world.parent_hash216,
            HHS_HASH216_LEN + 1U);

        HHSExactStatus status = world_.evaluate(candidate.world, out.cell_receipts[0]);
        if (status != HHS_EXACT_STATUS_OK) {
            out.failed_cell_mask |= kCellWorld;
            return status;
        }
        out.completed_cell_mask |= kCellWorld;

        status = physics_.evaluate(
            candidate.world, candidate.physics, out.cell_receipts[1]);
        if (status != HHS_EXACT_STATUS_OK) {
            out.failed_cell_mask |= kCellPhysics;
            return status;
        }
        out.completed_cell_mask |= kCellPhysics;

        status = geometry_.evaluate(
            candidate.world, candidate.geometry, out.cell_receipts[2]);
        if (status != HHS_EXACT_STATUS_OK) {
            out.failed_cell_mask |= kCellGeometry;
            return status;
        }
        out.completed_cell_mask |= kCellGeometry;

        status = render_.evaluate(
            candidate.world, candidate.render, out.cell_receipts[3]);
        if (status != HHS_EXACT_STATUS_OK) {
            out.failed_cell_mask |= kCellRender;
            return status;
        }
        out.completed_cell_mask |= kCellRender;

        status = script_.evaluate(
            candidate.world, candidate.script, out.cell_receipts[4]);
        if (status != HHS_EXACT_STATUS_OK) {
            out.failed_cell_mask |= kCellScript;
            return status;
        }
        out.completed_cell_mask |= kCellScript;

        status = compute_.evaluate(
            candidate.world, candidate.compute, out.cell_receipts[5]);
        if (status != HHS_EXACT_STATUS_OK) {
            out.failed_cell_mask |= kCellCompute;
            return status;
        }
        out.completed_cell_mask |= kCellCompute;

        status = asset_.evaluate(
            candidate.world, candidate.asset, out.cell_receipts[6]);
        if (status != HHS_EXACT_STATUS_OK) {
            out.failed_cell_mask |= kCellAsset;
            return status;
        }
        out.completed_cell_mask |= kCellAsset;

        if (out.completed_cell_mask != kRequiredCellMask)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        out.accepted = 1U;
        out.candidate_only = 1U;
        out.canonical_vm81_mutation_authority = 0U;
        out.canonical_hash72_authority = 0U;
        out.canonical_hash216_authority = 0U;
        out.canonical_persistence_authority = 0U;
        out.floating_point_canonical_authority = 0U;
        return HHS_EXACT_STATUS_OK;
    }

private:
    WorldCellWall world_{};
    PhysicsCellWall physics_{};
    GeometryCellWall geometry_{};
    RenderCellWall render_{};
    ScriptCellWall script_{};
    ComputeCellWall compute_{};
    AssetCellWall asset_{};
};

static_assert(HHS_EXACT_VM81_CELLS * HHS_EXACT_PHASE_PAIR_COUNT ==
                  HHS_EXACT_VM81_FRAME_BITS,
              "81 VM81 cells x 64 ordered operations must close 5184");
static_assert(HHS_EXACT_HASH72_COORDS == HHS_EXACT_VM81_FRAME_BITS,
              "Hash72 72x72 coordinate space must equal VM81 5184 frame");
static_assert(kRequiredCellMask == UINT32_C(0x7F),
              "foundation requires exactly seven organized engine cells");

}  // namespace hhs::game

#endif

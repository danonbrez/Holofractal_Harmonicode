#define main hhs_pass219_phase6_reference_main
#include "hhcq_joint_local_router_phase6_benchmark.cpp"
#undef main

namespace {

bool symbolic_clean(const HHSExactPass219HHCQSymbolicManifoldV1& m) {
    return m.symbolic_carrier_admitted == 1U &&
           m.global_relation_graph_exact == 1U &&
           m.symbolic_equilibrium_exact == 1U &&
           m.symbolic_square_gate_exact == 1U &&
           m.ordered_products_exact == 1U &&
           m.constraint_intersection_satisfied == 1U &&
           m.raw_projection_authority == 0U &&
           m.scalar_integer_semantic_authority == 0U &&
           m.gate.scalar_x_parity_evaluated == 0U &&
           m.gate.phase10_projection_authority == 0U &&
           m.gate.x_squared_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2 &&
           m.gate.negative_xy_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2 &&
           m.canonical_mutation_authority == 0U &&
           m.canonical_hash72_authority == 0U &&
           m.canonical_hash216_authority == 0U &&
           m.canonical_persistence_authority == 0U &&
           m.floating_point_authority == 0U;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::fprintf(stderr, "usage: %s <phase3-frame-binary>\n", argv[0]);
        return 2;
    }

    HHSExactPass219HHCQStructuralPhaseDescriptorV1 descriptor{};
    if (hhs_exact_pass219_hhcq_structural_phase_descriptor(&descriptor) != HHS_EXACT_STATUS_OK ||
        descriptor.version != HHS_EXACT_PASS219_HHCQ_STRUCTURAL_PHASE_LIFT_VERSION ||
        descriptor.pass219b_phase_version != hhs_exact_pass219b_phase_version() ||
        descriptor.symbolic_phase_version != hhs_exact_pass219_hhcq_symbolic_phase_version() ||
        descriptor.relation_role_count != 8U || descriptor.phase_origin_count != 81U ||
        descriptor.pass219b_structural_source_required != 1U ||
        descriptor.parent_hydration_coordinate_required != 1U ||
        descriptor.complete_role_graph_required != 1U ||
        descriptor.orientation_from_structural_direction != 1U ||
        descriptor.raw_vm81_word_semantic_authority != 0U ||
        descriptor.raw_phase_residue_semantic_authority != 0U ||
        descriptor.scalar_phase_position_semantic_authority != 0U ||
        descriptor.scalar_integer_semantic_authority != 0U ||
        descriptor.canonical_mutation_authority != 0U ||
        descriptor.canonical_hash72_authority != 0U ||
        descriptor.canonical_hash216_authority != 0U ||
        descriptor.canonical_persistence_authority != 0U ||
        descriptor.floating_point_authority != 0U)
        return 3;

    std::ifstream in(argv[1], std::ios::binary);
    if (!in) return 4;
    std::array<char, 8> magic{};
    if (!read_exact(in, magic.data(), magic.size()) ||
        std::string(magic.data(), magic.size()) != "HHS3WGT1") return 5;
    std::uint32_t version = 0U;
    std::uint32_t record_count = 0U;
    std::uint32_t checkpoint_count = 0U;
    std::uint32_t frame_kind_count = 0U;
    if (!read_u32_le(in, version) || !read_u32_le(in, record_count) ||
        !read_u32_le(in, checkpoint_count) || !read_u32_le(in, frame_kind_count)) return 6;
    if (version != kVersion || checkpoint_count != kCheckpointCount ||
        frame_kind_count != kFrameKindCount || record_count != 2116U) return 7;

    std::uint32_t summary_records = 0U;
    std::uint32_t local_samples = 0U;
    std::uint32_t phase5_roundtrip_checks = 0U;
    std::uint32_t structural_lift_checks = 0U;
    std::uint32_t structural_replay_checks = 0U;
    std::uint32_t structural_role_checks = 0U;
    std::uint32_t xy_direct_ring_checks = 0U;
    std::uint32_t zw_reverse_ring_checks = 0U;
    std::uint32_t mixed_carrier_checks = 0U;
    std::uint32_t raw_residue_semantic_promotions = 0U;
    std::array<bool, HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT> origin_seen{};
    std::set<std::string> unique_digests;
    std::uint64_t signature = UINT64_C(0x2195133000b00101);

    for (std::uint32_t i = 0U; i < record_count; ++i) {
        Record record{};
        if (!read_record(in, record)) return 8;
        if (record.frame_kind != kSummaryFrameKind) continue;
        ++summary_records;
        unique_digests.insert(record.chunk_digest);

        HHSExactVM81Frame frame{};
        HHSExactPass219CoreCircuitFeaturesV1 core{};
        if (!import_frame(record, frame)) return 9;
        if (hhs_exact_pass219_core_circuit_extract(&frame, &core) != HHS_EXACT_STATUS_OK)
            return 10;

        for (std::size_t anchor_index = 0U; anchor_index < kAnchorCount; ++anchor_index) {
            HHSExactPass219HHCQJointPreparedV1 prepared{};
            if (!prepare_local(frame, core, anchor_index, prepared)) return 11;
            if (!phase5_roundtrip_exact(frame, prepared)) return 12;
            ++phase5_roundtrip_checks;

            const std::uint16_t anchor = anchor_for(anchor_index);
            const std::uint8_t cell = static_cast<std::uint8_t>(anchor / 64U);
            const std::uint8_t operation64 = static_cast<std::uint8_t>(anchor / HHS_EXACT_PASS219_G243_COUNT);
            const std::uint16_t g243 = static_cast<std::uint16_t>(anchor % HHS_EXACT_PASS219_G243_COUNT);
            HHSExactPass219HydrationCoordinateV1 parent{};
            if (hhs_exact_pass219_coordinate_from_pass189(
                    cell, 0, operation64, g243, &parent) != HHS_EXACT_STATUS_OK)
                return 13;
            if (parent.trit != 0U || parent.slot5184 != anchor || parent.cell81 != cell)
                return 14;

            const std::uint8_t origin = cell;
            origin_seen[origin] = true;
            HHSExactPass219HHCQStructuralPhaseLiftV1 lift{};
            HHSExactPass219HHCQStructuralPhaseLiftV1 replay{};
            if (hhs_exact_pass219_hhcq_structural_phase_lift_from_coordinate(
                    &parent, origin, 2U, 3U,
                    prepared.resolution.resolution_index, &lift) != HHS_EXACT_STATUS_OK)
                return 15;
            if (hhs_exact_pass219_hhcq_structural_phase_lift_validate(&lift) != HHS_EXACT_STATUS_OK)
                return 16;
            if (hhs_exact_pass219_hhcq_structural_phase_lift_from_coordinate(
                    &parent, origin, 2U, 3U,
                    prepared.resolution.resolution_index, &replay) != HHS_EXACT_STATUS_OK)
                return 17;
            if (std::memcmp(&lift, &replay, sizeof(lift)) != 0)
                return 18;

            if (lift.phase_cell.parent.slot5184 != anchor ||
                lift.phase_cell.parent.cell81 != cell ||
                lift.phase_cell.phase_origin81 != origin ||
                lift.relation_role_mask != HHS_EXACT_PASS219_HHCQ_STRUCTURAL_PHASE_ROLE_MASK ||
                lift.structural_topology_exact != 1U ||
                lift.parent_coordinate_exact != 1U ||
                lift.relation_roles_exact != 1U ||
                lift.ring_topology_exact != 1U ||
                lift.phase_positions_exact != 1U ||
                lift.tensor_source_preserved != 1U ||
                lift.center_closure_preserved != 1U ||
                lift.xy_ring_orientation != HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT ||
                lift.zw_ring_orientation != HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED ||
                lift.symbolic_carrier_admitted != 1U ||
                lift.constraint_intersection_satisfied != 1U ||
                !symbolic_clean(lift.manifold))
                return 19;

            if (lift.raw_vm81_word_semantic_authority != 0U ||
                lift.raw_phase_residue_semantic_authority != 0U ||
                lift.scalar_phase_position_semantic_authority != 0U ||
                lift.scalar_integer_semantic_authority != 0U ||
                lift.carrier.projection_residue_authority != 0U ||
                lift.manifold.raw_projection_authority != 0U ||
                lift.manifold.scalar_integer_semantic_authority != 0U ||
                lift.manifold.gate.scalar_x_parity_evaluated != 0U ||
                lift.canonical_mutation_authority != 0U ||
                lift.canonical_hash72_authority != 0U ||
                lift.canonical_hash216_authority != 0U ||
                lift.canonical_persistence_authority != 0U ||
                lift.floating_point_authority != 0U)
                return 20;

            for (std::uint32_t role = 0U; role < HHS_EXACT_PASS219B_OUTER_CELL_COUNT; ++role) {
                if (lift.phase_cell.outer[role].relation_role != role)
                    return 21;
                ++structural_role_checks;
            }

            ++structural_lift_checks;
            ++structural_replay_checks;
            ++xy_direct_ring_checks;
            ++zw_reverse_ring_checks;
            ++mixed_carrier_checks;
            raw_residue_semantic_promotions += lift.raw_phase_residue_semantic_authority;
            signature ^= lift.structural_signature64 + UINT64_C(0x9e3779b97f4a7c15);
            ++local_samples;
        }
    }

    std::uint32_t authenticated_origin_coverage = 0U;
    for (bool seen : origin_seen)
        if (seen) ++authenticated_origin_coverage;

    if (summary_records != 529U || unique_digests.size() != 489U ||
        local_samples != 4761U || phase5_roundtrip_checks != 4761U ||
        structural_lift_checks != 4761U || structural_replay_checks != 4761U ||
        structural_role_checks != 38088U ||
        xy_direct_ring_checks != 4761U || zw_reverse_ring_checks != 4761U ||
        mixed_carrier_checks != 4761U || raw_residue_semantic_promotions != 0U)
        return 22;

    std::printf("{\n");
    std::printf("  \"schema\": \"HHS_PASS219_HHCQ_STRUCTURAL_PHASE_LIFT_PHASE12_V1\",\n");
    std::printf("  \"classification\": \"STRUCTURAL_PHASE_LIFT_VALIDATED\",\n");
    std::printf("  \"phase3_frame_binary_sha256\": \"%s\",\n", kPhase3FrameSha256);
    std::printf("  \"summary_records\": %u,\n", summary_records);
    std::printf("  \"authenticated_unique_digests\": %zu,\n", unique_digests.size());
    std::printf("  \"local_samples\": %u,\n", local_samples);
    std::printf("  \"phase5_exact_roundtrip_checks\": %u,\n", phase5_roundtrip_checks);
    std::printf("  \"structural_lift_checks\": %u,\n", structural_lift_checks);
    std::printf("  \"structural_replay_checks\": %u,\n", structural_replay_checks);
    std::printf("  \"structural_role_checks\": %u,\n", structural_role_checks);
    std::printf("  \"xy_direct_ring_checks\": %u,\n", xy_direct_ring_checks);
    std::printf("  \"zw_reverse_ring_checks\": %u,\n", zw_reverse_ring_checks);
    std::printf("  \"mixed_carrier_checks\": %u,\n", mixed_carrier_checks);
    std::printf("  \"authenticated_origin_coverage\": %u,\n", authenticated_origin_coverage);
    std::printf("  \"raw_residue_semantic_promotions\": %u,\n", raw_residue_semantic_promotions);
    std::printf("  \"raw_phase_residue_authority\": false,\n");
    std::printf("  \"scalar_integer_semantic_authority\": false,\n");
    std::printf("  \"phase_position_semantic_authority\": false,\n");
    std::printf("  \"candidate_only\": true,\n");
    std::printf("  \"canonical_authority_changed\": false,\n");
    std::printf("  \"floating_point_authority\": false,\n");
    std::printf("  \"signature64\": \"%llu\"\n",
                static_cast<unsigned long long>(signature));
    std::printf("}\n");
    return 0;
}

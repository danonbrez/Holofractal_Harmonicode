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

    HHSExactPass219HHCQSymbolicPhaseDescriptorV1 descriptor{};
    if (hhs_exact_pass219_hhcq_symbolic_phase_descriptor(&descriptor) != HHS_EXACT_STATUS_OK ||
        descriptor.phase_modulus != 72U || descriptor.parameter_count != 5184U ||
        descriptor.basis_count != 8U || descriptor.inherited_policy_state_bytes != 112U ||
        descriptor.phase11_source_bytes != 700U || descriptor.symbolic_phase_symbols != 1U ||
        descriptor.global_constraint_graph_required != 1U ||
        descriptor.reciprocal_opposition_relations_required != 1U ||
        descriptor.ordered_noncommutative_products_required != 1U ||
        descriptor.symbolic_phi8_equilibrium != 1U || descriptor.symbolic_x_squared_gate != 1U ||
        descriptor.phase11_scalar_equilibrium_superseded != 1U ||
        descriptor.phase11_scalar_parity_superseded != 1U ||
        descriptor.raw_phase_residue_authority != 0U ||
        descriptor.scalar_phase_sum_authority != 0U ||
        descriptor.scalar_x_parity_authority != 0U ||
        descriptor.phase10_projection_witness_only != 1U ||
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
    std::uint32_t raw_projection_checks = 0U;
    std::uint32_t raw_projection_admitted = 0U;
    std::uint32_t raw_projection_rejected = 0U;
    std::uint32_t raw_zero_xy_projection_count = 0U;
    std::uint32_t raw_zero_xy_admitted = 0U;
    std::uint32_t symbolic_direct_checks = 0U;
    std::uint32_t symbolic_reverse_checks = 0U;
    std::uint32_t symbolic_mixed_checks = 0U;
    std::uint32_t symbolic_manifold_checks = 0U;
    std::uint32_t symbolic_replay_checks = 0U;
    std::set<std::string> unique_digests;
    std::uint64_t signature = UINT64_C(0x21951320b0010001);

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
            HHSExactPass219OctonionSurfaceV1 raw_surface{};
            if (hhs_exact_pass219_octonion_from_vm81(
                    &frame,
                    cell,
                    static_cast<std::uint8_t>((cell + 1U) % HHS_EXACT_VM81_CELLS),
                    static_cast<std::uint8_t>((cell + 9U) % HHS_EXACT_VM81_CELLS),
                    static_cast<std::uint8_t>((cell + 10U) % HHS_EXACT_VM81_CELLS),
                    &raw_surface) != HHS_EXACT_STATUS_OK)
                return 13;

            HHSExactPass219HHCQSymbolicManifoldV1 raw_manifold{};
            if (hhs_exact_pass219_hhcq_symbolic_manifold_from_projection(
                    &raw_surface.state, 2U, 3U,
                    prepared.resolution.resolution_index,
                    &raw_manifold) != HHS_EXACT_STATUS_OK)
                return 14;
            ++raw_projection_checks;
            if (raw_surface.state.x == 0U && raw_surface.state.y == 0U) {
                ++raw_zero_xy_projection_count;
                if (raw_manifold.symbolic_carrier_admitted != 0U)
                    ++raw_zero_xy_admitted;
            }
            if (raw_manifold.symbolic_carrier_admitted != 0U) {
                if (!symbolic_clean(raw_manifold)) return 15;
                ++raw_projection_admitted;
            } else {
                if (raw_manifold.constraint_intersection_satisfied != 0U ||
                    raw_manifold.raw_projection_authority != 0U ||
                    raw_manifold.scalar_integer_semantic_authority != 0U ||
                    raw_manifold.admission.scalar_zero_reinterpreted_as_symbolic_zero != 0U)
                    return 16;
                ++raw_projection_rejected;
            }

            static const std::uint8_t orientations[2] = {
                HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT,
                HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED
            };
            for (std::uint32_t xo = 0U; xo < 2U; ++xo) {
                for (std::uint32_t zo = 0U; zo < 2U; ++zo) {
                    HHSExactPass219HHCQSymbolicCarrierV1 carrier{};
                    HHSExactPass219HHCQSymbolicManifoldV1 a{};
                    HHSExactPass219HHCQSymbolicManifoldV1 b{};
                    if (hhs_exact_pass219_hhcq_symbolic_carrier_construct(
                            orientations[xo], orientations[zo], &carrier) != HHS_EXACT_STATUS_OK)
                        return 17;
                    if (hhs_exact_pass219_hhcq_symbolic_manifold_from_carrier(
                            &carrier, 2U, 3U, prepared.resolution.resolution_index, &a) !=
                            HHS_EXACT_STATUS_OK ||
                        hhs_exact_pass219_hhcq_symbolic_manifold_from_carrier(
                            &carrier, 2U, 3U, prepared.resolution.resolution_index, &b) !=
                            HHS_EXACT_STATUS_OK)
                        return 18;
                    if (std::memcmp(&a, &b, sizeof(a)) != 0 || !symbolic_clean(a))
                        return 19;
                    ++symbolic_replay_checks;
                    ++symbolic_manifold_checks;
                    if (xo == zo && xo == 0U) ++symbolic_direct_checks;
                    else if (xo == zo && xo == 1U) ++symbolic_reverse_checks;
                    else ++symbolic_mixed_checks;
                    signature ^= a.manifold_signature64 + UINT64_C(0x9e3779b97f4a7c15);
                }
            }
            ++local_samples;
        }
    }

    if (summary_records != 529U || unique_digests.size() != 489U ||
        local_samples != 4761U || phase5_roundtrip_checks != 4761U ||
        raw_projection_checks != 4761U ||
        raw_projection_admitted + raw_projection_rejected != raw_projection_checks ||
        raw_zero_xy_projection_count != 2U || raw_zero_xy_admitted != 0U ||
        symbolic_direct_checks != 4761U || symbolic_reverse_checks != 4761U ||
        symbolic_mixed_checks != 9522U || symbolic_manifold_checks != 19044U ||
        symbolic_replay_checks != symbolic_manifold_checks)
        return 20;

    std::printf("{\n");
    std::printf("  \"schema\": \"HHS_PASS219_HHCQ_SYMBOLIC_PHASE_GEAR_PHASE11_REPAIR_V1\",\n");
    std::printf("  \"classification\": \"SYMBOLIC_TYPE_AUTHORITY_REPAIRED\",\n");
    std::printf("  \"phase3_frame_binary_sha256\": \"%s\",\n", kPhase3FrameSha256);
    std::printf("  \"summary_records\": %u,\n", summary_records);
    std::printf("  \"authenticated_unique_digests\": %zu,\n", unique_digests.size());
    std::printf("  \"local_samples\": %u,\n", local_samples);
    std::printf("  \"phase5_exact_roundtrip_checks\": %u,\n", phase5_roundtrip_checks);
    std::printf("  \"raw_projection_checks\": %u,\n", raw_projection_checks);
    std::printf("  \"raw_projection_admitted\": %u,\n", raw_projection_admitted);
    std::printf("  \"raw_projection_rejected\": %u,\n", raw_projection_rejected);
    std::printf("  \"raw_zero_xy_projection_count\": %u,\n", raw_zero_xy_projection_count);
    std::printf("  \"raw_zero_xy_admitted\": %u,\n", raw_zero_xy_admitted);
    std::printf("  \"symbolic_direct_checks\": %u,\n", symbolic_direct_checks);
    std::printf("  \"symbolic_reverse_checks\": %u,\n", symbolic_reverse_checks);
    std::printf("  \"symbolic_mixed_checks\": %u,\n", symbolic_mixed_checks);
    std::printf("  \"symbolic_manifold_checks\": %u,\n", symbolic_manifold_checks);
    std::printf("  \"symbolic_replay_checks\": %u,\n", symbolic_replay_checks);
    std::printf("  \"phase11_scalar_equilibrium_superseded\": true,\n");
    std::printf("  \"phase11_scalar_parity_superseded\": true,\n");
    std::printf("  \"raw_phase_residue_authority\": false,\n");
    std::printf("  \"scalar_phase_sum_authority\": false,\n");
    std::printf("  \"scalar_x_parity_authority\": false,\n");
    std::printf("  \"phase10_projection_witness_only\": true,\n");
    std::printf("  \"symbolic_x_squared_is_i2\": true,\n");
    std::printf("  \"candidate_only\": true,\n");
    std::printf("  \"canonical_authority_changed\": false,\n");
    std::printf("  \"floating_point_authority\": false,\n");
    std::printf("  \"signature64\": \"%llu\"\n",
                static_cast<unsigned long long>(signature));
    std::printf("}\n");
    return 0;
}

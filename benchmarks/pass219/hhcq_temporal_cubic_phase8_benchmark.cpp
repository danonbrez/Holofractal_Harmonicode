#define main hhs_pass219_phase6_reference_main
#include "hhcq_joint_local_router_phase6_benchmark.cpp"
#undef main

namespace {

struct Phase8Eval {
    std::uint32_t correct{};
    std::uint64_t regret{};
    std::uint32_t count{};
    std::vector<std::uint8_t> predictions;
};

struct Phase8TrainStats {
    std::uint64_t steps{};
    std::uint32_t updates{};
    std::array<std::uint64_t, 3> collapse_direction_counts{};
    std::array<std::uint64_t, 3> temporal_direction_counts{};
    std::array<std::uint64_t, 3> temporal_alignment_counts{};
    std::array<std::uint64_t, HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_PRESSURE + 1U> pressure_counts{};
};

struct TemporalGeometryStats {
    std::array<std::uint64_t, 3> temporal_direction_counts{};
    std::array<std::uint64_t, 3> root_direction_counts{};
    std::array<std::uint64_t, 73> root_count_histogram{};
    std::uint32_t no_root_samples{};
    std::uint32_t more_than_three_root_samples{};
    std::uint32_t exact_phase_root_samples{};
    std::uint8_t max_root_count{};
    std::uint64_t signature64{};
};

struct QuantumScale8 {
    std::uint32_t numerator;
    std::uint32_t denominator;
};

constexpr std::array<QuantumScale8, 6> kQuantumScales8 = {{
    {1U,8U}, {1U,4U}, {1U,2U}, {1U,1U}, {2U,1U}, {4U,1U}
}};
constexpr std::array<std::uint32_t, 4> kEpochCandidates8 = {4U,8U,12U,16U};

bool tuning_validation_bucket8(const std::string& digest) {
    if (!training_bucket(digest) || digest.size() != 64U) return false;
    const int value = hex_value(digest[digest.size() - 2U]);
    return value >= 0 && (value & 3) == 0;
}

bool evaluate_subset8(
    const HHSExactPass219HHCQJointStateV1& state,
    const std::vector<LocalSample>& samples,
    int mode,
    Phase8Eval& out
) {
    for (const LocalSample& sample : samples) {
        bool take = false;
        if (mode == 0) take = !sample.training;
        else if (mode == 1) take = sample.training && tuning_validation_bucket8(sample.digest);
        else if (mode == 2) take = sample.training && !tuning_validation_bucket8(sample.digest);
        else if (mode == 3) take = sample.training;
        if (!take) continue;
        HHSExactPass219HHCQJointDecisionV1 decision{};
        if (hhs_exact_pass219_hhcq_joint_predict(&sample.prepared, &state, &decision) !=
            HHS_EXACT_STATUS_OK)
            return false;
        if (decision.phase5_resolution_locked != 1U || decision.candidate_only != 1U ||
            decision.canonical_mutation_authority != 0U ||
            decision.canonical_hash72_authority != 0U ||
            decision.canonical_hash216_authority != 0U ||
            decision.canonical_persistence_authority != 0U ||
            decision.floating_point_authority != 0U ||
            decision.resolution_index != sample.prepared.resolution.resolution_index ||
            decision.resolution_parameters != sample.prepared.resolution.resolution_parameters)
            return false;
        ++out.count;
        out.predictions.push_back(decision.selected_lane);
        if (decision.selected_lane == sample.target_lane) ++out.correct;
        out.regret += sample.cost[decision.selected_lane] - sample.cost[sample.target_lane];
    }
    return true;
}

std::uint64_t quantized_regret_scale8(
    const std::vector<LocalSample>& samples,
    QuantumScale8 scale
) {
    std::vector<std::uint64_t> margins;
    for (const LocalSample& sample : samples) {
        if (!sample.training || tuning_validation_bucket8(sample.digest)) continue;
        for (std::size_t lane = 0U; lane < kLaneCount; ++lane) {
            if (lane == sample.target_lane) continue;
            const std::uint64_t margin = sample.cost[lane] - sample.cost[sample.target_lane];
            if (margin != 0U) margins.push_back(margin);
        }
    }
    std::uint64_t base = median_vector(std::move(margins));
    if (base == 0U) base = 1U;
    std::uint64_t value =
        (base * scale.numerator + scale.denominator - 1U) / scale.denominator;
    return value == 0U ? 1U : value;
}

bool train_phase7_reference(
    HHSExactPass219HHCQJointStateV1& state,
    const std::vector<LocalSample>& samples,
    std::uint32_t epochs,
    std::uint64_t regret_quantum,
    bool fit_only,
    Phase8TrainStats* stats
) {
    for (std::uint32_t epoch = 0U; epoch < epochs; ++epoch) {
        for (const LocalSample& sample : samples) {
            if (!sample.training) continue;
            if (fit_only && tuning_validation_bucket8(sample.digest)) continue;
            HHSExactPass219HHCQJointDecisionV1 before{};
            if (hhs_exact_pass219_hhcq_joint_predict(&sample.prepared, &state, &before) !=
                HHS_EXACT_STATUS_OK)
                return false;
            if (stats != nullptr) ++stats->steps;
            if (before.selected_lane == sample.target_lane) continue;
            const std::uint64_t margin =
                sample.cost[before.selected_lane] - sample.cost[sample.target_lane];
            if (margin == 0U) continue;
            HHSExactPass219HHCQCollapseRegretDecisionV1 update{};
            if (hhs_exact_pass219_hhcq_collapse_regret_step(
                    &sample.prepared, sample.target_lane, margin, regret_quantum,
                    &state, &update) != HHS_EXACT_STATUS_OK)
                return false;
            if (update.phase5_resolution_locked != 1U ||
                update.base_decision.resolution_index != sample.prepared.resolution.resolution_index ||
                update.base_decision.resolution_parameters != sample.prepared.resolution.resolution_parameters ||
                update.inherited_policy_state_bytes != 112U ||
                update.update_pressure == 0U ||
                update.update_pressure > HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_PRESSURE ||
                update.candidate_only != 1U || update.canonical_authority_changed != 0U ||
                update.floating_point_authority != 0U)
                return false;
            if (stats != nullptr) {
                if (update.updated != 0U) ++stats->updates;
                ++stats->pressure_counts[update.update_pressure];
                ++stats->collapse_direction_counts[
                    static_cast<std::size_t>(update.collapse.collapse_direction + 1)];
            }
        }
    }
    return state_clean(state) && sizeof(state) == 112U;
}

bool train_phase8_temporal(
    HHSExactPass219HHCQJointStateV1& state,
    const std::vector<LocalSample>& samples,
    std::uint32_t epochs,
    std::uint64_t regret_quantum,
    bool fit_only,
    Phase8TrainStats* stats
) {
    for (std::uint32_t epoch = 0U; epoch < epochs; ++epoch) {
        for (const LocalSample& sample : samples) {
            if (!sample.training) continue;
            if (fit_only && tuning_validation_bucket8(sample.digest)) continue;
            HHSExactPass219HHCQJointDecisionV1 before{};
            if (hhs_exact_pass219_hhcq_joint_predict(&sample.prepared, &state, &before) !=
                HHS_EXACT_STATUS_OK)
                return false;
            if (stats != nullptr) ++stats->steps;
            if (before.selected_lane == sample.target_lane) continue;
            const std::uint64_t margin =
                sample.cost[before.selected_lane] - sample.cost[sample.target_lane];
            if (margin == 0U) continue;
            HHSExactPass219HHCQTemporalRegretDecisionV1 update{};
            if (hhs_exact_pass219_hhcq_temporal_regret_step(
                    &sample.prepared, sample.target_lane, margin, regret_quantum,
                    &state, &update) != HHS_EXACT_STATUS_OK)
                return false;
            if (update.phase5_resolution_locked != 1U ||
                update.base_decision.resolution_index != sample.prepared.resolution.resolution_index ||
                update.base_decision.resolution_parameters != sample.prepared.resolution.resolution_parameters ||
                update.inherited_policy_state_bytes != 112U ||
                update.update_pressure == 0U ||
                update.update_pressure > HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_PRESSURE ||
                update.temporal_alignment < -1 || update.temporal_alignment > 1 ||
                update.temporal.exact_integer_only != 1U || update.roots.exact_integer_only != 1U ||
                update.candidate_only != 1U || update.canonical_authority_changed != 0U ||
                update.floating_point_authority != 0U)
                return false;
            if (stats != nullptr) {
                if (update.updated != 0U) ++stats->updates;
                ++stats->pressure_counts[update.update_pressure];
                ++stats->collapse_direction_counts[
                    static_cast<std::size_t>(update.collapse.collapse_direction + 1)];
                ++stats->temporal_direction_counts[
                    static_cast<std::size_t>(update.temporal.temporal_direction + 1)];
                ++stats->temporal_alignment_counts[
                    static_cast<std::size_t>(update.temporal_alignment + 1)];
            }
        }
    }
    return state_clean(state) && sizeof(state) == 112U;
}

bool collect_temporal_geometry(
    const std::vector<LocalSample>& samples,
    TemporalGeometryStats& stats
) {
    for (const LocalSample& sample : samples) {
        const auto& p = sample.prepared;
        const std::int32_t m = 2 + static_cast<std::int32_t>(p.resolution.resolution_index);
        const std::int32_t w = 1 + static_cast<std::int32_t>((p.touched_vm81_words - 1U) % 9U);
        const std::int32_t x = 1 + static_cast<std::int32_t>(p.anchor_parameter % 9U);
        const std::int32_t y = static_cast<std::int32_t>(p.loshu_value);
        const std::int32_t z = 1 + static_cast<std::int32_t>((p.touched_h36_words - 1U) % 9U);
        const std::int32_t t = static_cast<std::int32_t>(p.resolution.rotated_phase72);
        HHSExactPass219HHCQTemporalCubicWitnessV1 witness{};
        HHSExactPass219HHCQTemporalZ72RootsV1 roots{};
        if (hhs_exact_pass219_hhcq_temporal_cubic_witness(
                m, w, x, y, z, t, &witness) != HHS_EXACT_STATUS_OK)
            return false;
        if (hhs_exact_pass219_hhcq_temporal_z72_roots(
                m, w, x, y, z, p.resolution.rotated_phase72, &roots) != HHS_EXACT_STATUS_OK)
            return false;
        if (witness.exact_integer_only != 1U || witness.candidate_only != 1U ||
            witness.canonical_authority_changed != 0U || witness.floating_point_authority != 0U ||
            roots.exact_integer_only != 1U || roots.candidate_only != 1U ||
            roots.canonical_authority_changed != 0U || roots.floating_point_authority != 0U)
            return false;
        ++stats.temporal_direction_counts[
            static_cast<std::size_t>(witness.temporal_direction + 1)];
        ++stats.root_direction_counts[
            static_cast<std::size_t>(roots.preferred_direction + 1)];
        ++stats.root_count_histogram[roots.root_count];
        if (roots.root_count == 0U) ++stats.no_root_samples;
        if (roots.root_count > 3U) ++stats.more_than_three_root_samples;
        if (roots.preferred_direction == 0 && roots.root_count != 0U)
            ++stats.exact_phase_root_samples;
        if (roots.root_count > stats.max_root_count) stats.max_root_count = roots.root_count;
        stats.signature64 ^= witness.witness_signature64;
        stats.signature64 ^= roots.root_signature64 + UINT64_C(0x9e3779b97f4a7c15);
    }
    return true;
}

void print_u64_10_8(const std::array<std::uint64_t, 10>& values) {
    std::printf("[");
    for (std::size_t i = 0U; i < values.size(); ++i) {
        if (i != 0U) std::printf(",");
        std::printf("%llu", static_cast<unsigned long long>(values[i]));
    }
    std::printf("]");
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::fprintf(stderr, "usage: %s <phase3-frame-binary>\n", argv[0]);
        return 2;
    }
    if (hhs_exact_pass219_h36_validate() != HHS_EXACT_STATUS_OK) return 3;
    HHSExactPass219HHCQTemporalCubicDescriptorV1 descriptor{};
    if (hhs_exact_pass219_hhcq_temporal_cubic_descriptor(&descriptor) != HHS_EXACT_STATUS_OK ||
        descriptor.inherited_policy_state_bytes != 112U ||
        descriptor.phase_modulus != 72U || descriptor.symbolic_cardano_branch_count != 3U ||
        descriptor.compact_cubic_identity != 1U || descriptor.factored_discriminant_identity != 1U ||
        descriptor.radical_eliminated_from_canonical_path != 1U || descriptor.z72_root_scan != 1U ||
        descriptor.composite_ring_root_count_variable != 1U ||
        descriptor.phase5_resolution_locked != 1U || descriptor.fixed_size_policy_state != 1U ||
        descriptor.candidate_only != 1U || descriptor.floating_point_authority != 0U)
        return 4;

    std::ifstream in(argv[1], std::ios::binary);
    if (!in) return 5;
    std::array<char, 8> magic{};
    if (!read_exact(in, magic.data(), magic.size()) ||
        std::string(magic.data(), magic.size()) != "HHS3WGT1") return 6;
    std::uint32_t version = 0U;
    std::uint32_t record_count = 0U;
    std::uint32_t checkpoint_count = 0U;
    std::uint32_t frame_kind_count = 0U;
    if (!read_u32_le(in, version) || !read_u32_le(in, record_count) ||
        !read_u32_le(in, checkpoint_count) || !read_u32_le(in, frame_kind_count)) return 7;
    if (version != kVersion || checkpoint_count != kCheckpointCount ||
        frame_kind_count != kFrameKindCount || record_count != 2116U) return 8;

    std::vector<FrameSample> frames;
    frames.reserve(529U);
    std::array<std::vector<std::uint64_t>, kLaneCount> lane_costs;
    std::uint32_t whole_frame_semantic_checks = 0U;
    std::uint32_t phase5_roundtrip_checks = 0U;
    std::uint32_t local_container_checks = 0U;
    for (std::uint32_t i = 0U; i < record_count; ++i) {
        Record record{};
        if (!read_record(in, record)) return 9;
        if (record.frame_kind != kSummaryFrameKind) continue;
        FrameSample fs{};
        fs.record = std::move(record);
        if (!import_frame(fs.record, fs.frame)) return 10;
        if (hhs_exact_pass219_core_circuit_extract(&fs.frame, &fs.core) != HHS_EXACT_STATUS_OK)
            return 11;
        for (std::uint8_t lane = 0U; lane < kLaneCount; ++lane) {
            if (!measure_lane(lane, fs.record, fs.frame, fs.lane_median_ns[lane])) return 12;
            lane_costs[lane].push_back(fs.lane_median_ns[lane]);
            ++whole_frame_semantic_checks;
        }
        for (std::size_t anchor = 0U; anchor < kAnchorCount; ++anchor) {
            if (!prepare_local(fs.frame, fs.core, anchor, fs.prepared[anchor])) return 13;
            if (!phase5_roundtrip_exact(fs.frame, fs.prepared[anchor])) return 14;
            ++phase5_roundtrip_checks;
            for (std::size_t lane = 0U; lane < kLaneCount; ++lane) {
                if (!region_container_exact(fs.frame, fs.prepared[anchor], kNativeWidthBits[lane]))
                    return 15;
                ++local_container_checks;
            }
        }
        frames.push_back(std::move(fs));
    }
    if (frames.size() != 529U || whole_frame_semantic_checks != 2116U ||
        phase5_roundtrip_checks != 4761U || local_container_checks != 19044U)
        return 16;

    std::array<std::uint64_t, kLaneCount> global_lane_median_ns{};
    for (std::size_t lane = 0U; lane < kLaneCount; ++lane) {
        global_lane_median_ns[lane] = median_vector(lane_costs[lane]);
        if (global_lane_median_ns[lane] == 0U) return 17;
    }

    std::vector<LocalSample> samples;
    samples.reserve(frames.size() * kAnchorCount);
    std::array<std::uint32_t, kLaneCount> target_lane_counts{};
    std::array<std::uint32_t, HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT> resolution_counts{};
    for (const FrameSample& fs : frames) {
        for (std::size_t anchor = 0U; anchor < kAnchorCount; ++anchor) {
            LocalSample sample{};
            sample.prepared = fs.prepared[anchor];
            sample.digest = fs.record.chunk_digest;
            sample.training = training_bucket(sample.digest);
            sample.target_lane = 0U;
            for (std::size_t lane = 0U; lane < kLaneCount; ++lane) {
                const std::uint64_t normalized_x1m =
                    (fs.lane_median_ns[lane] * UINT64_C(1000000) +
                     global_lane_median_ns[lane] / 2U) /
                    global_lane_median_ns[lane];
                const std::uint64_t amp =
                    amplification_x1024(sample.prepared, kNativeWidthBits[lane]);
                sample.cost[lane] =
                    (normalized_x1m * amp + UINT64_C(512)) / UINT64_C(1024);
                if (sample.cost[lane] == 0U) sample.cost[lane] = 1U;
                if (lane != 0U && sample.cost[lane] < sample.cost[sample.target_lane])
                    sample.target_lane = static_cast<std::uint8_t>(lane);
            }
            ++target_lane_counts[sample.target_lane];
            ++resolution_counts[sample.prepared.resolution.resolution_index];
            samples.push_back(std::move(sample));
        }
    }
    if (samples.size() != 4761U) return 18;

    std::set<std::string> train_digests;
    std::set<std::string> heldout_digests;
    std::uint32_t train_samples = 0U;
    std::uint32_t heldout_samples = 0U;
    std::uint32_t tuning_fit_samples = 0U;
    std::uint32_t tuning_validation_samples = 0U;
    for (const LocalSample& sample : samples) {
        if (sample.training) {
            ++train_samples;
            train_digests.insert(sample.digest);
            if (tuning_validation_bucket8(sample.digest)) ++tuning_validation_samples;
            else ++tuning_fit_samples;
        } else {
            ++heldout_samples;
            heldout_digests.insert(sample.digest);
        }
    }
    std::uint32_t overlap = 0U;
    for (const auto& digest : train_digests)
        if (heldout_digests.count(digest) != 0U) ++overlap;
    if (train_samples != 3456U || heldout_samples != 1305U || overlap != 0U ||
        train_digests.size() != 352U || heldout_digests.size() != 137U ||
        tuning_fit_samples == 0U || tuning_validation_samples == 0U)
        return 19;

    std::uint32_t resolution_diversity = 0U;
    std::uint32_t target_lane_diversity = 0U;
    for (std::size_t i = 0U; i < resolution_counts.size(); ++i)
        if (resolution_counts[i] != 0U) ++resolution_diversity;
    for (std::size_t lane = 0U; lane < kLaneCount; ++lane)
        if (target_lane_counts[lane] != 0U) ++target_lane_diversity;
    if (resolution_diversity != 35U || target_lane_diversity != 4U) return 20;

    TemporalGeometryStats geometry{};
    if (!collect_temporal_geometry(samples, geometry)) return 21;
    if (geometry.temporal_direction_counts[0] + geometry.temporal_direction_counts[1] +
            geometry.temporal_direction_counts[2] != samples.size() ||
        geometry.root_direction_counts[0] + geometry.root_direction_counts[1] +
            geometry.root_direction_counts[2] != samples.size() ||
        geometry.max_root_count > 72U)
        return 22;

    HHSExactPass219HHCQJointStateV1 initial{};
    if (hhs_exact_pass219_hhcq_joint_state_init(&initial) != HHS_EXACT_STATUS_OK ||
        !state_clean(initial) || sizeof(initial) != 112U) return 23;
    Phase8Eval pre{};
    if (!evaluate_subset8(initial, samples, 0, pre) || pre.count != heldout_samples) return 24;

    std::uint64_t best_phase7_validation_regret = UINT64_MAX;
    std::uint32_t best_phase7_validation_correct = 0U;
    std::uint32_t phase7_epochs = 0U;
    std::uint64_t phase7_quantum = 0U;
    QuantumScale8 phase7_scale{1U,1U};
    std::uint64_t best_phase8_validation_regret = UINT64_MAX;
    std::uint32_t best_phase8_validation_correct = 0U;
    std::uint32_t phase8_epochs = 0U;
    std::uint64_t phase8_quantum = 0U;
    QuantumScale8 phase8_scale{1U,1U};
    std::uint32_t phase7_candidates = 0U;
    std::uint32_t phase8_candidates = 0U;

    for (const QuantumScale8 scale : kQuantumScales8) {
        const std::uint64_t quantum = quantized_regret_scale8(samples, scale);
        for (const std::uint32_t epochs : kEpochCandidates8) {
            HHSExactPass219HHCQJointStateV1 c7{};
            HHSExactPass219HHCQJointStateV1 c8{};
            if (hhs_exact_pass219_hhcq_joint_state_init(&c7) != HHS_EXACT_STATUS_OK ||
                hhs_exact_pass219_hhcq_joint_state_init(&c8) != HHS_EXACT_STATUS_OK)
                return 25;
            if (!train_phase7_reference(c7, samples, epochs, quantum, true, nullptr)) return 26;
            if (!train_phase8_temporal(c8, samples, epochs, quantum, true, nullptr)) return 27;
            Phase8Eval v7{};
            Phase8Eval v8{};
            if (!evaluate_subset8(c7, samples, 1, v7) ||
                !evaluate_subset8(c8, samples, 1, v8) ||
                v7.count != tuning_validation_samples || v8.count != tuning_validation_samples)
                return 28;
            ++phase7_candidates;
            ++phase8_candidates;
            if (v7.regret < best_phase7_validation_regret ||
                (v7.regret == best_phase7_validation_regret &&
                 v7.correct > best_phase7_validation_correct)) {
                best_phase7_validation_regret = v7.regret;
                best_phase7_validation_correct = v7.correct;
                phase7_epochs = epochs;
                phase7_quantum = quantum;
                phase7_scale = scale;
            }
            if (v8.regret < best_phase8_validation_regret ||
                (v8.regret == best_phase8_validation_regret &&
                 v8.correct > best_phase8_validation_correct)) {
                best_phase8_validation_regret = v8.regret;
                best_phase8_validation_correct = v8.correct;
                phase8_epochs = epochs;
                phase8_quantum = quantum;
                phase8_scale = scale;
            }
        }
    }
    if (phase7_candidates != 24U || phase8_candidates != 24U ||
        phase7_epochs == 0U || phase8_epochs == 0U ||
        phase7_quantum == 0U || phase8_quantum == 0U)
        return 29;

    HHSExactPass219HHCQJointStateV1 trained7{};
    HHSExactPass219HHCQJointStateV1 trained8{};
    if (hhs_exact_pass219_hhcq_joint_state_init(&trained7) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_hhcq_joint_state_init(&trained8) != HHS_EXACT_STATUS_OK)
        return 30;
    Phase8TrainStats stats7{};
    Phase8TrainStats stats8{};
    if (!train_phase7_reference(trained7, samples, phase7_epochs, phase7_quantum, false, &stats7))
        return 31;
    if (!train_phase8_temporal(trained8, samples, phase8_epochs, phase8_quantum, false, &stats8))
        return 32;
    if (sizeof(trained7) != 112U || sizeof(trained8) != 112U) return 33;

    Phase8Eval post7a{};
    Phase8Eval post7b{};
    Phase8Eval post8a{};
    Phase8Eval post8b{};
    if (!evaluate_subset8(trained7, samples, 0, post7a) ||
        !evaluate_subset8(trained7, samples, 0, post7b) ||
        !evaluate_subset8(trained8, samples, 0, post8a) ||
        !evaluate_subset8(trained8, samples, 0, post8b)) return 34;
    if (post7a.predictions != post7b.predictions || post7a.regret != post7b.regret ||
        post7a.correct != post7b.correct ||
        post8a.predictions != post8b.predictions || post8a.regret != post8b.regret ||
        post8a.correct != post8b.correct)
        return 35;

    std::array<std::uint64_t, kLaneCount> training_fixed_cost{};
    for (const LocalSample& sample : samples) {
        if (!sample.training) continue;
        for (std::size_t lane = 0U; lane < kLaneCount; ++lane)
            training_fixed_cost[lane] += sample.cost[lane];
    }
    std::uint8_t best_fixed_lane = 0U;
    for (std::uint8_t lane = 1U; lane < kLaneCount; ++lane)
        if (training_fixed_cost[lane] < training_fixed_cost[best_fixed_lane])
            best_fixed_lane = lane;
    std::uint64_t fixed_heldout_regret = 0U;
    for (const LocalSample& sample : samples) {
        if (sample.training) continue;
        fixed_heldout_regret += sample.cost[best_fixed_lane] - sample.cost[sample.target_lane];
    }

    const std::uint64_t pre_mean = pre.regret / heldout_samples;
    const std::uint64_t phase7_mean = post7a.regret / heldout_samples;
    const std::uint64_t phase8_mean = post8a.regret / heldout_samples;
    const std::uint64_t fixed_mean = fixed_heldout_regret / heldout_samples;
    const std::uint32_t pre_accuracy_x1000 =
        static_cast<std::uint32_t>((static_cast<std::uint64_t>(pre.correct) * 1000U) /
                                   heldout_samples);
    const std::uint32_t phase7_accuracy_x1000 =
        static_cast<std::uint32_t>((static_cast<std::uint64_t>(post7a.correct) * 1000U) /
                                   heldout_samples);
    const std::uint32_t phase8_accuracy_x1000 =
        static_cast<std::uint32_t>((static_cast<std::uint64_t>(post8a.correct) * 1000U) /
                                   heldout_samples);

    const char* classification = "TEMPORAL_REGRESSION_VS_PHASE7";
    if (phase8_mean < phase7_mean && phase8_mean < fixed_mean && phase8_mean < pre_mean)
        classification = "TEMPORAL_BEATS_PHASE7_AND_FIXED";
    else if (phase8_mean < phase7_mean)
        classification = "TEMPORAL_BEATS_PHASE7_ONLY";
    else if (phase8_mean == phase7_mean)
        classification = "TEMPORAL_PHASE7_REGRET_PARITY";

    std::printf("{\n");
    std::printf("  \"schema\": \"HHS_PASS219_HHCQ_TEMPORAL_CUBIC_PHASE8_V1\",\n");
    std::printf("  \"classification\": \"%s\",\n", classification);
    std::printf("  \"phase3_frame_binary_sha256\": \"%s\",\n", kPhase3FrameSha256);
    std::printf("  \"summary_records\": %zu,\n", frames.size());
    std::printf("  \"local_samples\": %zu,\n", samples.size());
    std::printf("  \"phase5_exact_roundtrip_checks\": %u,\n", phase5_roundtrip_checks);
    std::printf("  \"lane_local_container_identity_checks\": %u,\n", local_container_checks);
    std::printf("  \"resolution_diversity\": %u,\n", resolution_diversity);
    std::printf("  \"target_lane_diversity\": %u,\n", target_lane_diversity);
    std::printf("  \"target_lane_counts\": "); print_u32_array(target_lane_counts); std::printf(",\n");
    std::printf("  \"global_lane_median_ns\": "); print_u64_array(global_lane_median_ns); std::printf(",\n");
    std::printf("  \"training_local_samples\": %u,\n", train_samples);
    std::printf("  \"heldout_local_samples\": %u,\n", heldout_samples);
    std::printf("  \"training_unique_digest_count\": %zu,\n", train_digests.size());
    std::printf("  \"heldout_unique_digest_count\": %zu,\n", heldout_digests.size());
    std::printf("  \"train_heldout_digest_overlap\": %u,\n", overlap);
    std::printf("  \"tuning_fit_samples\": %u,\n", tuning_fit_samples);
    std::printf("  \"tuning_validation_samples\": %u,\n", tuning_validation_samples);
    std::printf("  \"temporal_direction_counts_minus_zero_plus\": [%llu,%llu,%llu],\n",
                static_cast<unsigned long long>(geometry.temporal_direction_counts[0]),
                static_cast<unsigned long long>(geometry.temporal_direction_counts[1]),
                static_cast<unsigned long long>(geometry.temporal_direction_counts[2]));
    std::printf("  \"root_direction_counts_minus_zero_plus\": [%llu,%llu,%llu],\n",
                static_cast<unsigned long long>(geometry.root_direction_counts[0]),
                static_cast<unsigned long long>(geometry.root_direction_counts[1]),
                static_cast<unsigned long long>(geometry.root_direction_counts[2]));
    std::printf("  \"z72_no_root_samples\": %u,\n", geometry.no_root_samples);
    std::printf("  \"z72_more_than_three_root_samples\": %u,\n", geometry.more_than_three_root_samples);
    std::printf("  \"z72_exact_phase_root_samples\": %u,\n", geometry.exact_phase_root_samples);
    std::printf("  \"z72_max_root_count\": %u,\n", geometry.max_root_count);
    std::printf("  \"temporal_geometry_signature64\": \"%llu\",\n",
                static_cast<unsigned long long>(geometry.signature64));
    std::printf("  \"phase7_selected_quantum_scale\": [%u,%u],\n",
                phase7_scale.numerator, phase7_scale.denominator);
    std::printf("  \"phase7_selected_regret_quantum_units\": %llu,\n",
                static_cast<unsigned long long>(phase7_quantum));
    std::printf("  \"phase7_selected_training_epochs\": %u,\n", phase7_epochs);
    std::printf("  \"phase8_selected_quantum_scale\": [%u,%u],\n",
                phase8_scale.numerator, phase8_scale.denominator);
    std::printf("  \"phase8_selected_regret_quantum_units\": %llu,\n",
                static_cast<unsigned long long>(phase8_quantum));
    std::printf("  \"phase8_selected_training_epochs\": %u,\n", phase8_epochs);
    std::printf("  \"phase7_training_steps\": %llu,\n",
                static_cast<unsigned long long>(stats7.steps));
    std::printf("  \"phase7_training_updates\": %u,\n", stats7.updates);
    std::printf("  \"phase8_training_steps\": %llu,\n",
                static_cast<unsigned long long>(stats8.steps));
    std::printf("  \"phase8_training_updates\": %u,\n", stats8.updates);
    std::printf("  \"phase8_temporal_alignment_counts_minus_zero_plus\": [%llu,%llu,%llu],\n",
                static_cast<unsigned long long>(stats8.temporal_alignment_counts[0]),
                static_cast<unsigned long long>(stats8.temporal_alignment_counts[1]),
                static_cast<unsigned long long>(stats8.temporal_alignment_counts[2]));
    std::printf("  \"phase8_update_pressure_counts_0_to_9\": "); print_u64_10_8(stats8.pressure_counts); std::printf(",\n");
    std::printf("  \"fixed_policy_state_bytes\": %zu,\n", sizeof(trained8));
    std::printf("  \"heldout_pretrain_accuracy_x1000\": %u,\n", pre_accuracy_x1000);
    std::printf("  \"heldout_phase7_accuracy_x1000\": %u,\n", phase7_accuracy_x1000);
    std::printf("  \"heldout_phase8_accuracy_x1000\": %u,\n", phase8_accuracy_x1000);
    std::printf("  \"heldout_pretrain_mean_regret\": %llu,\n",
                static_cast<unsigned long long>(pre_mean));
    std::printf("  \"heldout_phase7_mean_regret\": %llu,\n",
                static_cast<unsigned long long>(phase7_mean));
    std::printf("  \"heldout_phase8_mean_regret\": %llu,\n",
                static_cast<unsigned long long>(phase8_mean));
    std::printf("  \"best_training_fixed_lane\": %u,\n", best_fixed_lane);
    std::printf("  \"heldout_fixed_lane_mean_regret\": %llu,\n",
                static_cast<unsigned long long>(fixed_mean));
    std::printf("  \"phase7_prediction_replay_equal\": true,\n");
    std::printf("  \"phase8_prediction_replay_equal\": true,\n");
    std::printf("  \"compact_temporal_cubic_exact_integer\": true,\n");
    std::printf("  \"canonical_radical_or_float_solver_used\": false,\n");
    std::printf("  \"symbolic_cardano_branch_count\": 3,\n");
    std::printf("  \"z72_root_count_not_forced_three\": true,\n");
    std::printf("  \"phase5_resolution_locked_during_learning\": true,\n");
    std::printf("  \"fixed_size_policy_state\": true,\n");
    std::printf("  \"candidate_only\": true,\n");
    std::printf("  \"canonical_authority_changed\": false,\n");
    std::printf("  \"floating_point_authority\": false,\n");
    std::printf("  \"measurement_sink64\": \"%llu\"\n",
                static_cast<unsigned long long>(g_sink));
    std::printf("}\n");
    return 0;
}

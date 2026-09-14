#define main hhs_pass219_phase6_reference_main
#include "hhcq_joint_local_router_phase6_benchmark.cpp"
#undef main

namespace {

struct Phase7Eval {
    std::uint32_t correct{};
    std::uint64_t regret{};
    std::uint32_t count{};
    std::vector<std::uint8_t> predictions;
};

struct TrainStats {
    std::uint64_t steps{};
    std::uint32_t updates{};
    std::array<std::uint64_t, 3> collapse_direction_counts{};
    std::array<std::uint64_t, HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_PRESSURE + 1U> pressure_counts{};
};

struct QuantumScale {
    std::uint32_t numerator;
    std::uint32_t denominator;
};

constexpr std::array<QuantumScale, 6> kQuantumScales = {{
    {1U,8U}, {1U,4U}, {1U,2U}, {1U,1U}, {2U,1U}, {4U,1U}
}};
constexpr std::array<std::uint32_t, 4> kEpochCandidates = {4U,8U,12U,16U};

bool tuning_validation_bucket(const std::string& digest) {
    if (!training_bucket(digest) || digest.size() != 64U) return false;
    const int value = hex_value(digest[digest.size() - 2U]);
    return value >= 0 && (value & 3) == 0;
}

bool evaluate_subset(
    const HHSExactPass219HHCQJointStateV1& state,
    const std::vector<LocalSample>& samples,
    int mode,
    Phase7Eval& out
) {
    for (const LocalSample& sample : samples) {
        bool take = false;
        if (mode == 0) take = !sample.training;
        else if (mode == 1) take = sample.training && tuning_validation_bucket(sample.digest);
        else if (mode == 2) take = sample.training && !tuning_validation_bucket(sample.digest);
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

std::uint64_t quantized_regret_scale(
    const std::vector<LocalSample>& samples,
    QuantumScale scale
) {
    std::vector<std::uint64_t> margins;
    for (const LocalSample& sample : samples) {
        if (!sample.training || tuning_validation_bucket(sample.digest)) continue;
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

bool train_state(
    HHSExactPass219HHCQJointStateV1& state,
    const std::vector<LocalSample>& samples,
    std::uint32_t epochs,
    std::uint64_t regret_quantum,
    bool fit_only,
    TrainStats* stats
) {
    for (std::uint32_t epoch = 0U; epoch < epochs; ++epoch) {
        for (const LocalSample& sample : samples) {
            if (!sample.training) continue;
            if (fit_only && tuning_validation_bucket(sample.digest)) continue;
            HHSExactPass219HHCQJointDecisionV1 before{};
            if (hhs_exact_pass219_hhcq_joint_predict(&sample.prepared, &state, &before) !=
                HHS_EXACT_STATUS_OK)
                return false;
            if (before.phase5_resolution_locked != 1U ||
                before.resolution_index != sample.prepared.resolution.resolution_index ||
                before.resolution_parameters != sample.prepared.resolution.resolution_parameters)
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
                update.inherited_policy_state_bytes != sizeof(HHSExactPass219HHCQJointStateV1) ||
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
    return state_clean(state) && sizeof(state) == sizeof(HHSExactPass219HHCQJointStateV1);
}

void print_u64_10(const std::array<std::uint64_t, 10>& values) {
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
    HHSExactPass219HHCQCollapseRegretDescriptorV1 collapse_descriptor{};
    if (hhs_exact_pass219_hhcq_collapse_regret_descriptor(&collapse_descriptor) !=
            HHS_EXACT_STATUS_OK ||
        collapse_descriptor.inherited_policy_state_bytes != sizeof(HHSExactPass219HHCQJointStateV1) ||
        collapse_descriptor.inherited_policy_state_bytes != 112U ||
        collapse_descriptor.exact_quadratic_collapse != 1U ||
        collapse_descriptor.radical_eliminated_from_canonical_path != 1U ||
        collapse_descriptor.phase5_resolution_locked != 1U ||
        collapse_descriptor.fixed_size_policy_state != 1U ||
        collapse_descriptor.candidate_only != 1U ||
        collapse_descriptor.floating_point_authority != 0U)
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
    std::set<std::string> tuning_fit_digests;
    std::set<std::string> tuning_validation_digests;
    std::uint32_t train_samples = 0U;
    std::uint32_t heldout_samples = 0U;
    std::uint32_t tuning_fit_samples = 0U;
    std::uint32_t tuning_validation_samples = 0U;
    for (const LocalSample& sample : samples) {
        if (sample.training) {
            ++train_samples;
            train_digests.insert(sample.digest);
            if (tuning_validation_bucket(sample.digest)) {
                ++tuning_validation_samples;
                tuning_validation_digests.insert(sample.digest);
            } else {
                ++tuning_fit_samples;
                tuning_fit_digests.insert(sample.digest);
            }
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
        tuning_fit_samples == 0U || tuning_validation_samples == 0U ||
        tuning_fit_digests.size() + tuning_validation_digests.size() != train_digests.size())
        return 19;

    std::uint32_t resolution_diversity = 0U;
    std::uint32_t target_lane_diversity = 0U;
    for (std::size_t i = 0U; i < resolution_counts.size(); ++i)
        if (resolution_counts[i] != 0U) ++resolution_diversity;
    for (std::size_t lane = 0U; lane < kLaneCount; ++lane)
        if (target_lane_counts[lane] != 0U) ++target_lane_diversity;
    if (resolution_diversity != 35U || target_lane_diversity != 4U) return 20;

    HHSExactPass219HHCQJointStateV1 initial{};
    if (hhs_exact_pass219_hhcq_joint_state_init(&initial) != HHS_EXACT_STATUS_OK ||
        !state_clean(initial) || sizeof(initial) != 112U) return 21;
    Phase7Eval pre{};
    if (!evaluate_subset(initial, samples, 0, pre) || pre.count != heldout_samples) return 22;

    std::uint64_t best_validation_regret = UINT64_MAX;
    std::uint32_t best_validation_correct = 0U;
    std::uint32_t selected_epochs = 0U;
    std::uint64_t selected_quantum = 0U;
    QuantumScale selected_scale{1U,1U};
    std::uint32_t tuning_candidates = 0U;
    for (const QuantumScale scale : kQuantumScales) {
        const std::uint64_t quantum = quantized_regret_scale(samples, scale);
        for (const std::uint32_t epochs : kEpochCandidates) {
            HHSExactPass219HHCQJointStateV1 candidate{};
            if (hhs_exact_pass219_hhcq_joint_state_init(&candidate) != HHS_EXACT_STATUS_OK)
                return 23;
            if (!train_state(candidate, samples, epochs, quantum, true, nullptr)) return 24;
            Phase7Eval validation{};
            if (!evaluate_subset(candidate, samples, 1, validation) ||
                validation.count != tuning_validation_samples)
                return 25;
            ++tuning_candidates;
            if (validation.regret < best_validation_regret ||
                (validation.regret == best_validation_regret &&
                 validation.correct > best_validation_correct)) {
                best_validation_regret = validation.regret;
                best_validation_correct = validation.correct;
                selected_epochs = epochs;
                selected_quantum = quantum;
                selected_scale = scale;
            }
        }
    }
    if (tuning_candidates != kQuantumScales.size() * kEpochCandidates.size() ||
        selected_epochs == 0U || selected_quantum == 0U)
        return 26;

    HHSExactPass219HHCQJointStateV1 trained{};
    if (hhs_exact_pass219_hhcq_joint_state_init(&trained) != HHS_EXACT_STATUS_OK) return 27;
    TrainStats train_stats{};
    if (!train_state(trained, samples, selected_epochs, selected_quantum, false, &train_stats))
        return 28;
    if (sizeof(trained) != sizeof(initial) || sizeof(trained) != 112U) return 29;

    Phase7Eval post_a{};
    Phase7Eval post_b{};
    if (!evaluate_subset(trained, samples, 0, post_a) ||
        !evaluate_subset(trained, samples, 0, post_b)) return 30;
    if (post_a.count != heldout_samples || post_a.predictions != post_b.predictions ||
        post_a.correct != post_b.correct || post_a.regret != post_b.regret)
        return 31;

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
    const std::uint64_t post_mean = post_a.regret / heldout_samples;
    const std::uint64_t fixed_mean = fixed_heldout_regret / heldout_samples;
    const std::uint32_t pre_accuracy_x1000 =
        static_cast<std::uint32_t>((static_cast<std::uint64_t>(pre.correct) * 1000U) /
                                   heldout_samples);
    const std::uint32_t post_accuracy_x1000 =
        static_cast<std::uint32_t>((static_cast<std::uint64_t>(post_a.correct) * 1000U) /
                                   heldout_samples);

    const char* classification = "NO_HELDOUT_IMPROVEMENT";
    if (post_mean < pre_mean && post_mean < fixed_mean)
        classification = "HELDOUT_FIXED_BASELINE_BEATEN";
    else if (post_mean < pre_mean)
        classification = "HELDOUT_IMPROVEMENT_FIXED_BASELINE_NOT_BEATEN";
    else if (post_mean > pre_mean)
        classification = "HELDOUT_REGRESSION";

    std::printf("{\n");
    std::printf("  \"schema\": \"HHS_PASS219_HHCQ_COLLAPSE_REGRET_PHASE7_V1\",\n");
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
    std::printf("  \"tuning_candidate_count\": %u,\n", tuning_candidates);
    std::printf("  \"selected_quantum_scale_numerator\": %u,\n", selected_scale.numerator);
    std::printf("  \"selected_quantum_scale_denominator\": %u,\n", selected_scale.denominator);
    std::printf("  \"selected_regret_quantum_units\": %llu,\n",
                static_cast<unsigned long long>(selected_quantum));
    std::printf("  \"selected_training_epochs\": %u,\n", selected_epochs);
    std::printf("  \"final_training_steps\": %llu,\n",
                static_cast<unsigned long long>(train_stats.steps));
    std::printf("  \"final_training_updates\": %u,\n", train_stats.updates);
    std::printf("  \"collapse_direction_counts_minus_zero_plus\": [%llu,%llu,%llu],\n",
                static_cast<unsigned long long>(train_stats.collapse_direction_counts[0]),
                static_cast<unsigned long long>(train_stats.collapse_direction_counts[1]),
                static_cast<unsigned long long>(train_stats.collapse_direction_counts[2]));
    std::printf("  \"update_pressure_counts_0_to_9\": "); print_u64_10(train_stats.pressure_counts); std::printf(",\n");
    std::printf("  \"fixed_policy_state_bytes\": %zu,\n", sizeof(trained));
    std::printf("  \"heldout_pretrain_accuracy_x1000\": %u,\n", pre_accuracy_x1000);
    std::printf("  \"heldout_posttrain_accuracy_x1000\": %u,\n", post_accuracy_x1000);
    std::printf("  \"heldout_pretrain_mean_regret\": %llu,\n",
                static_cast<unsigned long long>(pre_mean));
    std::printf("  \"heldout_posttrain_mean_regret\": %llu,\n",
                static_cast<unsigned long long>(post_mean));
    std::printf("  \"best_training_fixed_lane\": %u,\n", best_fixed_lane);
    std::printf("  \"heldout_fixed_lane_mean_regret\": %llu,\n",
                static_cast<unsigned long long>(fixed_mean));
    std::printf("  \"heldout_prediction_replay_equal\": true,\n");
    std::printf("  \"collapse_polynomial_exact_integer\": true,\n");
    std::printf("  \"canonical_sqrt_or_division_used\": false,\n");
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

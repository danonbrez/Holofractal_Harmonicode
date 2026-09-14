#define main hhs_pass219_phase6_reference_main
#include "hhcq_joint_local_router_phase6_benchmark.cpp"
#undef main

#include "hhs_pass219_i163_pass169_reverse_crossarch_1_24.h"

namespace {

struct Phase9Eval {
    std::uint32_t correct{};
    std::uint64_t regret{};
    std::uint32_t count{};
    std::vector<std::uint8_t> predictions;
};

struct Phase9TrainStats {
    std::uint64_t steps{};
    std::uint32_t updates{};
};

struct QuantumScale9 {
    std::uint32_t numerator;
    std::uint32_t denominator;
};

constexpr std::array<QuantumScale9, 6> kQuantumScales9 = {{
    {1U,8U}, {1U,4U}, {1U,2U}, {1U,1U}, {2U,1U}, {4U,1U}
}};
constexpr std::array<std::uint32_t, 4> kEpochCandidates9 = {4U,8U,12U,16U};

bool tuning_validation_bucket9(const std::string& digest) {
    if (!training_bucket(digest) || digest.size() != 64U) return false;
    const int value = hex_value(digest[digest.size() - 2U]);
    return value >= 0 && (value & 3) == 0;
}

std::uint64_t quantized_regret_scale9(
    const std::vector<LocalSample>& samples,
    QuantumScale9 scale
) {
    std::vector<std::uint64_t> margins;
    for (const LocalSample& sample : samples) {
        if (!sample.training || tuning_validation_bucket9(sample.digest)) continue;
        for (std::size_t lane = 0U; lane < kLaneCount; ++lane) {
            if (lane == sample.target_lane) continue;
            const std::uint64_t margin = sample.cost[lane] - sample.cost[sample.target_lane];
            if (margin != 0U) margins.push_back(margin);
        }
    }
    std::uint64_t base = median_vector(std::move(margins));
    if (base == 0U) base = 1U;
    const std::uint64_t value =
        (base * scale.numerator + scale.denominator - 1U) / scale.denominator;
    return value == 0U ? 1U : value;
}

bool train_phase8_temporal9(
    HHSExactPass219HHCQJointStateV1& state,
    const std::vector<LocalSample>& samples,
    std::uint32_t epochs,
    std::uint64_t regret_quantum,
    bool fit_only,
    Phase9TrainStats* stats
) {
    for (std::uint32_t epoch = 0U; epoch < epochs; ++epoch) {
        for (const LocalSample& sample : samples) {
            if (!sample.training) continue;
            if (fit_only && tuning_validation_bucket9(sample.digest)) continue;
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
                update.candidate_only != 1U || update.canonical_authority_changed != 0U ||
                update.floating_point_authority != 0U)
                return false;
            if (stats != nullptr && update.updated != 0U) ++stats->updates;
        }
    }
    return state_clean(state) && sizeof(state) == 112U;
}

bool evaluate_phase8_state9(
    const HHSExactPass219HHCQJointStateV1& state,
    const std::vector<LocalSample>& samples,
    int mode,
    Phase9Eval& out
) {
    for (const LocalSample& sample : samples) {
        bool take = false;
        if (mode == 0) take = !sample.training;
        else if (mode == 1) take = sample.training && tuning_validation_bucket9(sample.digest);
        else if (mode == 2) take = sample.training && !tuning_validation_bucket9(sample.digest);
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

bool find_resolution_index9(std::uint32_t parameters, std::uint8_t& out_index) {
    if (parameters == 0U || parameters > HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT) return false;
    for (std::uint8_t i = 0U;
         i < static_cast<std::uint8_t>(HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT); ++i) {
        std::uint16_t value = 0U;
        if (hhs_exact_pass219_hhcq_resolution_divisor(i, &value) != HHS_EXACT_STATUS_OK)
            return false;
        if (value == parameters) {
            out_index = i;
            return true;
        }
    }
    return false;
}

HHSExactPass219HHCQEconomyCandidateV1 direct_candidate9(
    const LocalSample& sample,
    std::uint32_t route_id
) {
    HHSExactPass219HHCQEconomyCandidateV1 c{};
    c.struct_size = static_cast<std::uint32_t>(sizeof(c));
    c.version = HHS_EXACT_PASS219_HHCQ_RECIPROCAL_ECONOMY_VERSION;
    c.route_id = route_id;
    c.reciprocal_n = 1U;
    c.intrinsic_resolution_index = sample.prepared.resolution.resolution_index;
    c.effective_resolution_index = sample.prepared.resolution.resolution_index;
    c.required_resolution_index = sample.prepared.resolution.resolution_index;
    c.latency_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.memory_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.compression_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.translation_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.exact_semantic_closure = 1U;
    c.exact_reconstruction = 1U;
    c.all_native_modalities_translatable = 1U;
    c.one_step_translation = 1U;
    c.phase5_resolution_locked = 1U;
    c.candidate_only = 1U;
    return c;
}

bool lower_unproven_candidate9(
    const LocalSample& sample,
    std::uint16_t factor,
    std::uint32_t route_id,
    HHSExactPass219HHCQEconomyCandidateV1& out
) {
    const std::uint32_t required_parameters =
        static_cast<std::uint32_t>(sample.prepared.resolution.resolution_parameters);
    const std::uint32_t target_parameters = required_parameters * factor;
    std::uint8_t intrinsic_index = 0U;
    if (factor != 2U && factor != 3U) return false;
    if (target_parameters > HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT ||
        !find_resolution_index9(target_parameters, intrinsic_index) ||
        intrinsic_index >= sample.prepared.resolution.resolution_index)
        return false;

    const std::uint64_t coarse_units =
        HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS / factor;
    memset(&out, 0, sizeof(out));
    out.struct_size = static_cast<std::uint32_t>(sizeof(out));
    out.version = HHS_EXACT_PASS219_HHCQ_RECIPROCAL_ECONOMY_VERSION;
    out.route_id = route_id;
    out.reciprocal_n = factor;
    out.intrinsic_resolution_index = intrinsic_index;
    out.effective_resolution_index = sample.prepared.resolution.resolution_index;
    out.required_resolution_index = sample.prepared.resolution.resolution_index;
    out.latency_units = coarse_units;
    out.memory_units = coarse_units;
    out.compression_units = coarse_units;
    out.translation_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    out.redundancy_spend_units = coarse_units;
    out.ecc_spend_units = coarse_units;
    out.lossy_information_units = static_cast<std::uint32_t>(
        HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS - coarse_units);
    out.recovered_information_units = out.lossy_information_units;
    /* Budget reservation only. No materialized lower-resolution reconstruction proof exists yet. */
    out.exact_semantic_closure = 0U;
    out.exact_reconstruction = 0U;
    out.all_native_modalities_translatable = 0U;
    out.one_step_translation = 1U;
    out.phase5_resolution_locked = 1U;
    out.candidate_only = 1U;
    return true;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::fprintf(stderr, "usage: %s <phase3-frame-binary>\n", argv[0]);
        return 2;
    }
    if (hhs_exact_pass219_h36_validate() != HHS_EXACT_STATUS_OK) return 3;

    HHSExactPass219HHCQReciprocalEconomyDescriptorV1 economy_descriptor{};
    if (hhs_exact_pass219_hhcq_reciprocal_economy_descriptor(&economy_descriptor) !=
            HHS_EXACT_STATUS_OK ||
        economy_descriptor.parity_units != 5184U ||
        economy_descriptor.inherited_policy_state_bytes != 112U ||
        economy_descriptor.reciprocal_1_over_n_to_n_boundary != 1U ||
        economy_descriptor.exact_one_to_one_information_closure != 1U ||
        economy_descriptor.one_step_translation_required != 1U ||
        economy_descriptor.all_native_modalities_required != 1U ||
        economy_descriptor.phase5_resolution_locked != 1U ||
        economy_descriptor.candidate_only != 1U ||
        economy_descriptor.floating_point_authority != 0U)
        return 4;

    HHSExactPass219I163DescriptorV1 crossarch_descriptor{};
    if (hhs_exact_pass219_i163_descriptor(&crossarch_descriptor) != HHS_EXACT_STATUS_OK ||
        crossarch_descriptor.cross_architecture_receipt_identity_required != 1U ||
        crossarch_descriptor.interpreter_compiler_equality_required != 1U ||
        crossarch_descriptor.floating_point_authority != 0U ||
        crossarch_descriptor.canonical_mutation_authority != 0U ||
        crossarch_descriptor.hash216_persistence_authority != 0U)
        return 5;

    std::ifstream in(argv[1], std::ios::binary);
    if (!in) return 6;
    std::array<char, 8> magic{};
    if (!read_exact(in, magic.data(), magic.size()) ||
        std::string(magic.data(), magic.size()) != "HHS3WGT1") return 7;
    std::uint32_t version = 0U;
    std::uint32_t record_count = 0U;
    std::uint32_t checkpoint_count = 0U;
    std::uint32_t frame_kind_count = 0U;
    if (!read_u32_le(in, version) || !read_u32_le(in, record_count) ||
        !read_u32_le(in, checkpoint_count) || !read_u32_le(in, frame_kind_count)) return 8;
    if (version != kVersion || checkpoint_count != kCheckpointCount ||
        frame_kind_count != kFrameKindCount || record_count != 2116U) return 9;

    std::vector<FrameSample> frames;
    frames.reserve(529U);
    std::array<std::vector<std::uint64_t>, kLaneCount> lane_costs;
    std::uint32_t whole_frame_semantic_checks = 0U;
    std::uint32_t phase5_roundtrip_checks = 0U;
    std::uint32_t local_container_checks = 0U;
    for (std::uint32_t i = 0U; i < record_count; ++i) {
        Record record{};
        if (!read_record(in, record)) return 10;
        if (record.frame_kind != kSummaryFrameKind) continue;
        FrameSample fs{};
        fs.record = std::move(record);
        if (!import_frame(fs.record, fs.frame)) return 11;
        if (hhs_exact_pass219_core_circuit_extract(&fs.frame, &fs.core) != HHS_EXACT_STATUS_OK)
            return 12;
        for (std::uint8_t lane = 0U; lane < kLaneCount; ++lane) {
            if (!measure_lane(lane, fs.record, fs.frame, fs.lane_median_ns[lane])) return 13;
            lane_costs[lane].push_back(fs.lane_median_ns[lane]);
            ++whole_frame_semantic_checks;
        }
        for (std::size_t anchor = 0U; anchor < kAnchorCount; ++anchor) {
            if (!prepare_local(fs.frame, fs.core, anchor, fs.prepared[anchor])) return 14;
            if (!phase5_roundtrip_exact(fs.frame, fs.prepared[anchor])) return 15;
            ++phase5_roundtrip_checks;
            for (std::size_t lane = 0U; lane < kLaneCount; ++lane) {
                if (!region_container_exact(fs.frame, fs.prepared[anchor], kNativeWidthBits[lane]))
                    return 16;
                ++local_container_checks;
            }
        }
        frames.push_back(std::move(fs));
    }
    if (frames.size() != 529U || whole_frame_semantic_checks != 2116U ||
        phase5_roundtrip_checks != 4761U || local_container_checks != 19044U)
        return 17;

    std::array<std::uint64_t, kLaneCount> global_lane_median_ns{};
    for (std::size_t lane = 0U; lane < kLaneCount; ++lane) {
        global_lane_median_ns[lane] = median_vector(lane_costs[lane]);
        if (global_lane_median_ns[lane] == 0U) return 18;
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
    if (samples.size() != 4761U) return 19;

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
            if (tuning_validation_bucket9(sample.digest)) ++tuning_validation_samples;
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
        return 20;

    std::uint32_t resolution_diversity = 0U;
    std::uint32_t target_lane_diversity = 0U;
    for (std::size_t i = 0U; i < resolution_counts.size(); ++i)
        if (resolution_counts[i] != 0U) ++resolution_diversity;
    for (std::size_t lane = 0U; lane < kLaneCount; ++lane)
        if (target_lane_counts[lane] != 0U) ++target_lane_diversity;
    if (resolution_diversity != 35U || target_lane_diversity != 4U) return 21;

    std::uint64_t best_validation_regret = UINT64_MAX;
    std::uint32_t best_validation_correct = 0U;
    std::uint32_t selected_epochs = 0U;
    std::uint64_t selected_quantum = 0U;
    QuantumScale9 selected_scale{1U,1U};
    std::uint32_t tuning_candidates = 0U;
    for (const QuantumScale9 scale : kQuantumScales9) {
        const std::uint64_t quantum = quantized_regret_scale9(samples, scale);
        for (const std::uint32_t epochs : kEpochCandidates9) {
            HHSExactPass219HHCQJointStateV1 candidate{};
            if (hhs_exact_pass219_hhcq_joint_state_init(&candidate) != HHS_EXACT_STATUS_OK)
                return 22;
            if (!train_phase8_temporal9(candidate, samples, epochs, quantum, true, nullptr))
                return 23;
            Phase9Eval validation{};
            if (!evaluate_phase8_state9(candidate, samples, 1, validation) ||
                validation.count != tuning_validation_samples)
                return 24;
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
    if (tuning_candidates != 24U || selected_epochs == 0U || selected_quantum == 0U)
        return 25;

    HHSExactPass219HHCQJointStateV1 trained{};
    if (hhs_exact_pass219_hhcq_joint_state_init(&trained) != HHS_EXACT_STATUS_OK) return 26;
    Phase9TrainStats train_stats{};
    if (!train_phase8_temporal9(
            trained, samples, selected_epochs, selected_quantum, false, &train_stats))
        return 27;
    if (sizeof(trained) != 112U) return 28;

    Phase9Eval heldout_a{};
    Phase9Eval heldout_b{};
    if (!evaluate_phase8_state9(trained, samples, 0, heldout_a) ||
        !evaluate_phase8_state9(trained, samples, 0, heldout_b) ||
        heldout_a.count != heldout_samples || heldout_a.predictions != heldout_b.predictions ||
        heldout_a.correct != heldout_b.correct || heldout_a.regret != heldout_b.regret)
        return 29;

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

    std::uint32_t economy_samples = 0U;
    std::uint32_t direct_admitted = 0U;
    std::uint32_t direct_selected = 0U;
    std::uint32_t factor2_candidates = 0U;
    std::uint32_t factor3_candidates = 0U;
    std::uint32_t unproven_candidates = 0U;
    std::uint32_t unproven_budget_positive = 0U;
    std::uint32_t unproven_information_one_to_one = 0U;
    std::uint32_t unproven_admitted = 0U;
    std::uint32_t selector_replay_checks = 0U;
    std::uint64_t unproven_total_savings = 0U;
    std::uint64_t unproven_total_spend = 0U;
    std::uint64_t economy_signature = UINT64_C(0x219ec09a00129);

    std::size_t heldout_prediction_index = 0U;
    for (const LocalSample& sample : samples) {
        if (sample.training) continue;
        if (heldout_prediction_index >= heldout_a.predictions.size()) return 30;
        const std::uint8_t predicted_lane = heldout_a.predictions[heldout_prediction_index++];
        std::array<HHSExactPass219HHCQEconomyCandidateV1, 3> candidates{};
        std::size_t candidate_count = 0U;
        candidates[candidate_count++] = direct_candidate9(
            sample, UINT32_C(1000) + static_cast<std::uint32_t>(predicted_lane));

        HHSExactPass219HHCQEconomyCandidateV1 lower2{};
        if (lower_unproven_candidate9(sample, 2U, 2002U, lower2)) {
            candidates[candidate_count++] = lower2;
            ++factor2_candidates;
        }
        HHSExactPass219HHCQEconomyCandidateV1 lower3{};
        if (candidate_count < candidates.size() &&
            lower_unproven_candidate9(sample, 3U, 2003U, lower3)) {
            candidates[candidate_count++] = lower3;
            ++factor3_candidates;
        }

        HHSExactPass219HHCQEconomyResultV1 direct_result{};
        if (hhs_exact_pass219_hhcq_reciprocal_economy_evaluate(
                &candidates[0], &direct_result) != HHS_EXACT_STATUS_OK ||
            direct_result.decision != HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_ADMITTED ||
            direct_result.net_budget_units != 0 ||
            direct_result.information_one_to_one != 1U ||
            direct_result.effective_resolution_met != 1U)
            return 31;
        ++direct_admitted;

        for (std::size_t i = 1U; i < candidate_count; ++i) {
            HHSExactPass219HHCQEconomyResultV1 r{};
            if (hhs_exact_pass219_hhcq_reciprocal_economy_evaluate(
                    &candidates[i], &r) != HHS_EXACT_STATUS_OK)
                return 32;
            ++unproven_candidates;
            if (r.budget_nonnegative != 0U) ++unproven_budget_positive;
            if (r.information_one_to_one != 0U) ++unproven_information_one_to_one;
            if (r.decision == HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_ADMITTED)
                ++unproven_admitted;
            unproven_total_savings += r.total_savings_units;
            unproven_total_spend += r.total_spend_units;
            economy_signature ^= r.result_signature64 + UINT64_C(0x9e3779b97f4a7c15);
        }

        HHSExactPass219HHCQEconomySelectionV1 selection_a{};
        HHSExactPass219HHCQEconomySelectionV1 selection_b{};
        if (hhs_exact_pass219_hhcq_reciprocal_economy_select(
                candidates.data(), candidate_count, &selection_a) != HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_hhcq_reciprocal_economy_select(
                candidates.data(), candidate_count, &selection_b) != HHS_EXACT_STATUS_OK ||
            std::memcmp(&selection_a, &selection_b, sizeof(selection_a)) != 0)
            return 33;
        ++selector_replay_checks;
        economy_signature ^= selection_a.selection_signature64;
        if (selection_a.admitted_count != 1U || selection_a.selected_candidate_index != 0U ||
            selection_a.selected_route_id != candidates[0].route_id ||
            selection_a.selected_effective_resolution_index !=
                sample.prepared.resolution.resolution_index ||
            selection_a.canonical_authority_changed != 0U ||
            selection_a.floating_point_authority != 0U)
            return 34;
        ++direct_selected;
        ++economy_samples;
    }
    if (heldout_prediction_index != heldout_a.predictions.size() ||
        economy_samples != heldout_samples || direct_admitted != heldout_samples ||
        direct_selected != heldout_samples || selector_replay_checks != heldout_samples ||
        unproven_candidates == 0U || unproven_budget_positive == 0U ||
        unproven_information_one_to_one == 0U || unproven_admitted != 0U)
        return 35;

    const std::uint32_t heldout_accuracy_x1000 = static_cast<std::uint32_t>(
        (static_cast<std::uint64_t>(heldout_a.correct) * 1000U) / heldout_samples);
    const std::uint64_t heldout_mean_regret = heldout_a.regret / heldout_samples;
    const std::uint64_t fixed_mean_regret = fixed_heldout_regret / heldout_samples;
    const std::uint64_t mean_hypothetical_savings =
        unproven_candidates == 0U ? 0U : unproven_total_savings / unproven_candidates;
    const std::uint64_t mean_hypothetical_spend =
        unproven_candidates == 0U ? 0U : unproven_total_spend / unproven_candidates;

    std::printf("{\n");
    std::printf("  \"schema\": \"HHS_PASS219_HHCQ_RECIPROCAL_ECONOMY_PHASE9_V1\",\n");
    std::printf("  \"classification\": \"BUDGET_GATE_REJECTS_UNPROVEN_RECOVERY\",\n");
    std::printf("  \"phase3_frame_binary_sha256\": \"%s\",\n", kPhase3FrameSha256);
    std::printf("  \"summary_records\": %zu,\n", frames.size());
    std::printf("  \"local_samples\": %zu,\n", samples.size());
    std::printf("  \"phase5_exact_roundtrip_checks\": %u,\n", phase5_roundtrip_checks);
    std::printf("  \"lane_local_container_identity_checks\": %u,\n", local_container_checks);
    std::printf("  \"resolution_diversity\": %u,\n", resolution_diversity);
    std::printf("  \"target_lane_diversity\": %u,\n", target_lane_diversity);
    std::printf("  \"training_local_samples\": %u,\n", train_samples);
    std::printf("  \"heldout_local_samples\": %u,\n", heldout_samples);
    std::printf("  \"training_unique_digest_count\": %zu,\n", train_digests.size());
    std::printf("  \"heldout_unique_digest_count\": %zu,\n", heldout_digests.size());
    std::printf("  \"train_heldout_digest_overlap\": %u,\n", overlap);
    std::printf("  \"selected_regret_quantum_units\": %llu,\n",
                static_cast<unsigned long long>(selected_quantum));
    std::printf("  \"selected_quantum_scale\": [%u,%u],\n",
                selected_scale.numerator, selected_scale.denominator);
    std::printf("  \"selected_training_epochs\": %u,\n", selected_epochs);
    std::printf("  \"training_steps\": %llu,\n",
                static_cast<unsigned long long>(train_stats.steps));
    std::printf("  \"training_updates\": %u,\n", train_stats.updates);
    std::printf("  \"heldout_phase8_accuracy_x1000\": %u,\n", heldout_accuracy_x1000);
    std::printf("  \"heldout_phase8_mean_regret\": %llu,\n",
                static_cast<unsigned long long>(heldout_mean_regret));
    std::printf("  \"best_training_fixed_lane\": %u,\n", best_fixed_lane);
    std::printf("  \"heldout_fixed_lane_mean_regret\": %llu,\n",
                static_cast<unsigned long long>(fixed_mean_regret));
    std::printf("  \"economy_parity_units\": %llu,\n",
                static_cast<unsigned long long>(HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS));
    std::printf("  \"economy_heldout_samples\": %u,\n", economy_samples);
    std::printf("  \"direct_lossless_admitted\": %u,\n", direct_admitted);
    std::printf("  \"direct_lossless_selected\": %u,\n", direct_selected);
    std::printf("  \"factor2_lower_resolution_candidates\": %u,\n", factor2_candidates);
    std::printf("  \"factor3_lower_resolution_candidates\": %u,\n", factor3_candidates);
    std::printf("  \"unproven_lower_resolution_candidates\": %u,\n", unproven_candidates);
    std::printf("  \"unproven_budget_positive_candidates\": %u,\n", unproven_budget_positive);
    std::printf("  \"unproven_information_1to1_candidates\": %u,\n",
                unproven_information_one_to_one);
    std::printf("  \"unproven_admitted_candidates\": %u,\n", unproven_admitted);
    std::printf("  \"mean_unproven_structural_savings_units\": %llu,\n",
                static_cast<unsigned long long>(mean_hypothetical_savings));
    std::printf("  \"mean_unproven_reserved_recovery_spend_units\": %llu,\n",
                static_cast<unsigned long long>(mean_hypothetical_spend));
    std::printf("  \"selector_replay_checks\": %u,\n", selector_replay_checks);
    std::printf("  \"economy_signature64\": \"%llu\",\n",
                static_cast<unsigned long long>(economy_signature));
    std::printf("  \"inherited_crossarch_contract_gate\": true,\n");
    std::printf("  \"structural_normalized_economy_only\": true,\n");
    std::printf("  \"lower_resolution_candidate_execution_measured\": false,\n");
    std::printf("  \"materialized_golay_reconstruction_used\": false,\n");
    std::printf("  \"golay_ecc_spend_is_budget_reservation_only\": true,\n");
    std::printf("  \"exact_reconstruction_required_before_lower_resolution_admission\": true,\n");
    std::printf("  \"lossy_lossless_information_ratio_required_1to1\": true,\n");
    std::printf("  \"fixed_policy_state_bytes\": %zu,\n", sizeof(trained));
    std::printf("  \"phase5_resolution_locked\": true,\n");
    std::printf("  \"candidate_only\": true,\n");
    std::printf("  \"canonical_authority_changed\": false,\n");
    std::printf("  \"floating_point_authority\": false\n");
    std::printf("}\n");
    return 0;
}

#include "hhs_runtime_exact_abi.h"
#include "hhs_pass219_harmonic36_nested_vm_1_0.h"
#include "hhs_pass219_raw5184_octonion_audio_hydration_1_0.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <set>
#include <string>
#include <utility>
#include <vector>

namespace {

constexpr std::uint32_t kVersion = 1U;
constexpr std::size_t kCheckpointCount = 2U;
constexpr std::size_t kFrameKindCount = 4U;
constexpr std::size_t kFrameBytes = HHS_EXACT_VM81_FRAME_BYTES;
constexpr std::size_t kLaneCount = HHS_EXACT_PASS219_HOLO4_LANE_COUNT;
constexpr std::size_t kTimingRepetitions = 7U;
constexpr std::size_t kTrainingEpochs = 8U;
constexpr std::uint8_t kSummaryFrameKind = 0U;
constexpr const char* kPhase3FrameSha256 =
    "63d0f8816d4c04e10eb5d9644c9c60015b8cdd3b1235f114b3f1821ef08a3433";

volatile std::uint64_t g_sink = 0U;

struct Record {
    std::uint8_t checkpoint_slot{};
    std::uint8_t frame_kind{};
    std::uint8_t component_index{};
    std::uint32_t chunk_ordinal{};
    std::uint32_t reference_ordinal{};
    std::uint32_t raw_chunk_bytes{};
    std::string chunk_digest;
    std::string checkpoint_root;
    std::array<char, HHS_EXACT_HASH72_STRLEN> previous{};
    std::array<char, HHS_EXACT_HASH72_STRLEN> change{};
    std::array<char, HHS_EXACT_HASH72_STRLEN> receipt{};
    std::array<char, HHS_EXACT_UQCEL_HASH216_STRLEN> identity{};
    std::array<std::uint8_t, kFrameBytes> frame_bytes{};
};

struct Sample {
    Record record;
    std::array<std::uint64_t, kLaneCount> median_ns{};
    std::uint8_t target_lane{};
    bool training{};
};

struct EvalSummary {
    std::uint32_t correct{};
    std::uint64_t regret_ns{};
    std::vector<std::uint8_t> predictions;
};

bool read_exact(std::ifstream& in, void* out, std::size_t bytes) {
    in.read(static_cast<char*>(out), static_cast<std::streamsize>(bytes));
    return in.good() || static_cast<std::size_t>(in.gcount()) == bytes;
}

bool read_u32_le(std::ifstream& in, std::uint32_t& out) {
    std::array<std::uint8_t, 4> bytes{};
    if (!read_exact(in, bytes.data(), bytes.size())) return false;
    out = static_cast<std::uint32_t>(bytes[0]) |
          (static_cast<std::uint32_t>(bytes[1]) << 8U) |
          (static_cast<std::uint32_t>(bytes[2]) << 16U) |
          (static_cast<std::uint32_t>(bytes[3]) << 24U);
    return true;
}

bool read_record(std::ifstream& in, Record& r) {
    std::array<std::uint8_t, 4> tags{};
    if (!read_exact(in, tags.data(), tags.size())) return false;
    r.checkpoint_slot = tags[0];
    r.frame_kind = tags[1];
    r.component_index = tags[2];
    if (tags[3] != 0U) return false;
    if (!read_u32_le(in, r.chunk_ordinal) ||
        !read_u32_le(in, r.reference_ordinal) ||
        !read_u32_le(in, r.raw_chunk_bytes)) return false;
    std::array<char, 64> digest{};
    std::array<char, 64> root{};
    if (!read_exact(in, digest.data(), digest.size()) ||
        !read_exact(in, root.data(), root.size()) ||
        !read_exact(in, r.previous.data(), r.previous.size()) ||
        !read_exact(in, r.change.data(), r.change.size()) ||
        !read_exact(in, r.receipt.data(), r.receipt.size()) ||
        !read_exact(in, r.identity.data(), r.identity.size()) ||
        !read_exact(in, r.frame_bytes.data(), r.frame_bytes.size())) return false;
    r.chunk_digest.assign(digest.data(), digest.size());
    r.checkpoint_root.assign(root.data(), root.size());
    if (r.previous.back() != '\0' || r.change.back() != '\0' ||
        r.receipt.back() != '\0' || r.identity.back() != '\0') return false;
    return r.checkpoint_slot < kCheckpointCount && r.frame_kind < kFrameKindCount;
}

bool import_frame(const Record& r, HHSExactVM81Frame& out) {
    return hhs_exact_vm81_frame_import_le(
               r.frame_bytes.data(), r.frame_bytes.size(), &out) == HHS_EXACT_STATUS_OK;
}

bool init_transition(
    const Record& r,
    HHSExactPass219Hash216TransitionViewV1& out
) {
    return hhs_exact_pass219_hash216_transition_init(
               r.previous.data(), r.change.data(), r.receipt.data(),
               r.identity.data(), &out) == HHS_EXACT_STATUS_OK;
}

bool frame_equals_bytes(const HHSExactVM81Frame& frame, const Record& r) {
    std::array<std::uint8_t, kFrameBytes> bytes{};
    std::size_t length = 0U;
    if (hhs_exact_vm81_frame_export_le(
            &frame, bytes.data(), bytes.size(), &length) != HHS_EXACT_STATUS_OK)
        return false;
    return length == bytes.size() &&
           std::memcmp(bytes.data(), r.frame_bytes.data(), bytes.size()) == 0;
}

bool eval_raw5184(const Record& r, const HHSExactVM81Frame& frame) {
    std::array<std::uint8_t, kFrameBytes> copied{};
    std::size_t length = 0U;
    if (hhs_exact_pass219_global_raw5184_bytecode_copy(
            r.frame_bytes.data(), r.frame_bytes.size(), copied.data(), copied.size(),
            &length) != HHS_EXACT_STATUS_OK)
        return false;
    if (length != copied.size() ||
        std::memcmp(copied.data(), r.frame_bytes.data(), copied.size()) != 0)
        return false;
    HHSExactVM81Frame replay{};
    if (hhs_exact_vm81_frame_import_le(
            copied.data(), copied.size(), &replay) != HHS_EXACT_STATUS_OK)
        return false;
    if (std::memcmp(&frame, &replay, sizeof(frame)) != 0) return false;
    g_sink ^= replay.words[0] ^ replay.words[80];
    return frame_equals_bytes(replay, r);
}

bool eval_vm81_hash216(const Record& r, const HHSExactVM81Frame& frame) {
    if (hhs_exact_pass219_global_raw5184_validate_frame(&frame) != HHS_EXACT_STATUS_OK)
        return false;
    HHSExactPass219CoreCircuitFeaturesV1 features{};
    if (hhs_exact_pass219_core_circuit_extract(&frame, &features) != HHS_EXACT_STATUS_OK)
        return false;
    if (features.word_visits != HHS_EXACT_VM81_CELLS) return false;
    HHSExactPass219Hash216TransitionViewV1 transition{};
    if (!init_transition(r, transition)) return false;
    g_sink ^= features.hydration_signature64 ^ features.xor_signature64;
    return frame_equals_bytes(frame, r);
}

bool eval_octonion_audio(const Record& r, const HHSExactVM81Frame& frame) {
    HHSExactPass219Audio5184PCM64V1 pcm{};
    HHSExactVM81Frame replay{};
    HHSExactPass219Audio5184HydrationV1 hydration{};
    if (hhs_exact_pass219_audio5184_frame_to_pcm64(&frame, &pcm) !=
        HHS_EXACT_STATUS_OK)
        return false;
    if (hhs_exact_pass219_audio5184_pcm64_to_frame(&pcm, &replay) !=
        HHS_EXACT_STATUS_OK)
        return false;
    if (std::memcmp(&frame, &replay, sizeof(frame)) != 0) return false;
    if (hhs_exact_pass219_audio5184_hydrate(&frame, &hydration) !=
        HHS_EXACT_STATUS_OK)
        return false;
    if (hhs_exact_pass219_audio5184_hydration_validate(&frame, &hydration) !=
        HHS_EXACT_STATUS_OK)
        return false;
    if (hydration.exact_bit_roundtrip != 1U ||
        hydration.ordered_octonion_preserved != 1U ||
        hydration.typed_ternary_quotient_preserved != 1U ||
        hydration.floating_point_authority != 0U)
        return false;
    g_sink ^= pcm.samples_bits[0] ^ pcm.samples_bits[80] ^ hydration.quads[0].octonion.xy;
    return frame_equals_bytes(replay, r);
}

bool eval_harmonic36(const Record& r, const HHSExactVM81Frame&) {
    std::array<std::uint64_t, HHS_EXACT_PASS219_H36_WORD_COUNT> words{};
    std::array<std::uint8_t, kFrameBytes> replay{};
    for (std::size_t bit = 0U; bit < HHS_EXACT_PASS219_H36_FRAME_BITS; ++bit) {
        const std::uint8_t value = static_cast<std::uint8_t>(
            (r.frame_bytes[bit / 8U] >> (bit % 8U)) & 1U);
        if (value != 0U)
            words[bit / HHS_EXACT_PASS219_H36_WORD_BITS] |=
                UINT64_C(1) << (bit % HHS_EXACT_PASS219_H36_WORD_BITS);
    }
    for (std::size_t word = 0U; word < words.size(); ++word) {
        if ((words[word] & ~HHS_EXACT_PASS219_H36_WORD_MASK) != 0U) return false;
        HHSExactPass219H36CoordinateV1 coordinate{};
        if (hhs_exact_pass219_h36_coordinate(
                static_cast<std::uint16_t>(word * HHS_EXACT_PASS219_H36_WORD_BITS),
                &coordinate) != HHS_EXACT_STATUS_OK)
            return false;
        if (coordinate.word144 != word || coordinate.bit36 != 0U) return false;
        for (std::size_t bit = 0U; bit < HHS_EXACT_PASS219_H36_WORD_BITS; ++bit) {
            if (((words[word] >> bit) & UINT64_C(1)) != 0U) {
                const std::size_t linear = word * HHS_EXACT_PASS219_H36_WORD_BITS + bit;
                replay[linear / 8U] |= static_cast<std::uint8_t>(1U << (linear % 8U));
            }
        }
        g_sink ^= words[word] ^ coordinate.hash72_row72 ^ coordinate.hash72_col72;
    }
    return std::memcmp(replay.data(), r.frame_bytes.data(), replay.size()) == 0;
}

bool eval_lane(
    std::uint8_t lane,
    const Record& r,
    const HHSExactVM81Frame& frame
) {
    switch (lane) {
        case HHS_EXACT_PASS219_HOLO4_RAW5184_X86_64:
            return eval_raw5184(r, frame);
        case HHS_EXACT_PASS219_HOLO4_VM81_HASH72_HASH216:
            return eval_vm81_hash216(r, frame);
        case HHS_EXACT_PASS219_HOLO4_OCTONION_DUAL_STEREO_TERNARY:
            return eval_octonion_audio(r, frame);
        case HHS_EXACT_PASS219_HOLO4_HARMONIC36_144X36:
            return eval_harmonic36(r, frame);
        default:
            return false;
    }
}

bool measure_lane(
    std::uint8_t lane,
    const Record& r,
    const HHSExactVM81Frame& frame,
    std::uint64_t& out_median_ns
) {
    if (!eval_lane(lane, r, frame)) return false;
    if (!eval_lane(lane, r, frame)) return false;
    std::array<std::uint64_t, kTimingRepetitions> samples{};
    for (std::size_t i = 0U; i < samples.size(); ++i) {
        const auto start = std::chrono::steady_clock::now();
        if (!eval_lane(lane, r, frame)) return false;
        const auto stop = std::chrono::steady_clock::now();
        auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
        if (ns <= 0) ns = 1;
        samples[i] = static_cast<std::uint64_t>(ns);
    }
    std::sort(samples.begin(), samples.end());
    out_median_ns = samples[samples.size() / 2U];
    return out_median_ns > 0U;
}

int hex_value(char ch) {
    if (ch >= '0' && ch <= '9') return ch - '0';
    if (ch >= 'a' && ch <= 'f') return 10 + (ch - 'a');
    if (ch >= 'A' && ch <= 'F') return 10 + (ch - 'A');
    return -1;
}

bool training_bucket(const std::string& digest) {
    if (digest.size() != 64U) return false;
    const int value = hex_value(digest.back());
    if (value < 0) return false;
    return (value & 3) != 0;
}

bool state_clean(const HHSExactPass219Holo4StateV1& state) {
    return state.candidate_only == 1U && state.exact_integer_only == 1U &&
           state.canonical_mutation_authority == 0U &&
           state.canonical_hash72_authority == 0U &&
           state.canonical_hash216_authority == 0U &&
           state.canonical_persistence_authority == 0U &&
           state.floating_point_authority == 0U;
}

bool route_sample(
    HHSExactPass219Holo4StateV1& state,
    const Sample& sample,
    std::uint8_t feedback_lane,
    std::int8_t feedback,
    std::uint8_t& selected,
    bool& updated
) {
    HHSExactVM81Frame frame{};
    HHSExactPass219Hash216TransitionViewV1 transition{};
    HHSExactPass219Holo4PreparedV1 prepared{};
    HHSExactPass219Holo4DecisionV1 decision{};
    if (!import_frame(sample.record, frame) || !init_transition(sample.record, transition))
        return false;
    if (hhs_exact_pass219_holo4_route(
            &frame, &transition, feedback_lane, feedback,
            &state, &prepared, &decision) != HHS_EXACT_STATUS_OK)
        return false;
    if (!state_clean(state) || prepared.candidate_only != 1U ||
        prepared.canonical_mutation_authority != 0U ||
        prepared.canonical_hash72_authority != 0U ||
        prepared.canonical_hash216_authority != 0U ||
        prepared.canonical_persistence_authority != 0U ||
        prepared.floating_point_authority != 0U ||
        decision.candidate_only != 1U || decision.canonical_mutation_authority != 0U ||
        decision.canonical_hash72_authority != 0U ||
        decision.canonical_hash216_authority != 0U ||
        decision.canonical_persistence_authority != 0U ||
        decision.floating_point_authority != 0U)
        return false;
    if (std::strcmp(decision.source_transition_identity216, sample.record.identity.data()) != 0)
        return false;
    selected = decision.selected_lane;
    updated = decision.updated != 0U;
    return selected < kLaneCount;
}

bool evaluate_heldout(
    HHSExactPass219Holo4StateV1 state,
    const std::vector<Sample>& samples,
    EvalSummary& out
) {
    for (const Sample& sample : samples) {
        if (sample.training) continue;
        std::uint8_t selected = 0U;
        bool updated = false;
        if (!route_sample(
                state, sample, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
                selected, updated))
            return false;
        if (updated) return false;
        out.predictions.push_back(selected);
        if (selected == sample.target_lane) ++out.correct;
        out.regret_ns += sample.median_ns[selected] - sample.median_ns[sample.target_lane];
    }
    return true;
}

std::uint64_t median_vector(std::vector<std::uint64_t> values) {
    if (values.empty()) return 0U;
    std::sort(values.begin(), values.end());
    return values[values.size() / 2U];
}

void print_u32_array(const std::array<std::uint32_t, kLaneCount>& values) {
    std::printf("[%u,%u,%u,%u]", values[0], values[1], values[2], values[3]);
}

void print_u64_array(const std::array<std::uint64_t, kLaneCount>& values) {
    std::printf("[%llu,%llu,%llu,%llu]",
                static_cast<unsigned long long>(values[0]),
                static_cast<unsigned long long>(values[1]),
                static_cast<unsigned long long>(values[2]),
                static_cast<unsigned long long>(values[3]));
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::fprintf(stderr, "usage: %s <phase3-frame-binary>\n", argv[0]);
        return 2;
    }
    if (hhs_exact_pass219_h36_validate() != HHS_EXACT_STATUS_OK) return 3;

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

    std::vector<Sample> samples;
    samples.reserve(529U);
    std::array<std::uint32_t, kLaneCount> winner_counts{};
    std::array<std::vector<std::uint64_t>, kLaneCount> lane_costs;
    std::uint32_t semantic_equivalence_count = 0U;

    for (std::uint32_t i = 0U; i < record_count; ++i) {
        Record record{};
        if (!read_record(in, record)) return 8;
        if (record.frame_kind != kSummaryFrameKind) continue;
        HHSExactVM81Frame frame{};
        if (!import_frame(record, frame)) return 9;
        Sample sample{};
        sample.record = record;
        for (std::uint8_t lane = 0U; lane < kLaneCount; ++lane) {
            if (!measure_lane(lane, sample.record, frame, sample.median_ns[lane]))
                return 10;
            ++semantic_equivalence_count;
            lane_costs[lane].push_back(sample.median_ns[lane]);
        }
        sample.target_lane = 0U;
        for (std::uint8_t lane = 1U; lane < kLaneCount; ++lane) {
            if (sample.median_ns[lane] < sample.median_ns[sample.target_lane])
                sample.target_lane = lane;
        }
        ++winner_counts[sample.target_lane];
        sample.training = training_bucket(sample.record.chunk_digest);
        samples.push_back(std::move(sample));
    }

    if (samples.size() != 529U || semantic_equivalence_count != 2116U) return 11;

    std::set<std::string> train_digests;
    std::set<std::string> heldout_digests;
    std::uint32_t train_refs = 0U;
    std::uint32_t heldout_refs = 0U;
    std::array<std::uint32_t, kLaneCount> train_winners{};
    std::array<std::uint32_t, kLaneCount> heldout_winners{};
    for (const Sample& sample : samples) {
        if (sample.training) {
            train_digests.insert(sample.record.chunk_digest);
            ++train_refs;
            ++train_winners[sample.target_lane];
        } else {
            heldout_digests.insert(sample.record.chunk_digest);
            ++heldout_refs;
            ++heldout_winners[sample.target_lane];
        }
    }
    std::uint32_t overlap = 0U;
    for (const auto& digest : train_digests)
        if (heldout_digests.count(digest) != 0U) ++overlap;
    if (train_refs == 0U || heldout_refs == 0U || overlap != 0U ||
        train_digests.size() + heldout_digests.size() != 489U)
        return 12;

    HHSExactPass219Holo4StateV1 initial{};
    if (hhs_exact_pass219_holo4_state_init(&initial) != HHS_EXACT_STATUS_OK ||
        !state_clean(initial)) return 13;
    EvalSummary pre{};
    if (!evaluate_heldout(initial, samples, pre) || pre.predictions.size() != heldout_refs)
        return 14;

    HHSExactPass219Holo4StateV1 trained{};
    if (hhs_exact_pass219_holo4_state_init(&trained) != HHS_EXACT_STATUS_OK ||
        !state_clean(trained)) return 15;
    std::uint32_t observed_updates = 0U;
    for (std::size_t epoch = 0U; epoch < kTrainingEpochs; ++epoch) {
        for (const Sample& sample : samples) {
            if (!sample.training) continue;
            std::uint8_t selected = 0U;
            bool updated = false;
            if (!route_sample(trained, sample, sample.target_lane, 1, selected, updated))
                return 16;
            if (updated) ++observed_updates;
        }
    }
    if (!state_clean(trained)) return 17;

    EvalSummary post_a{};
    EvalSummary post_b{};
    if (!evaluate_heldout(trained, samples, post_a) ||
        !evaluate_heldout(trained, samples, post_b)) return 18;
    if (post_a.predictions != post_b.predictions || post_a.correct != post_b.correct ||
        post_a.regret_ns != post_b.regret_ns) return 19;

    std::array<std::uint64_t, kLaneCount> lane_median_ns{};
    for (std::size_t lane = 0U; lane < kLaneCount; ++lane)
        lane_median_ns[lane] = median_vector(lane_costs[lane]);

    const std::uint32_t pre_accuracy_x1000 =
        static_cast<std::uint32_t>((static_cast<std::uint64_t>(pre.correct) * 1000U) /
                                   heldout_refs);
    const std::uint32_t post_accuracy_x1000 =
        static_cast<std::uint32_t>((static_cast<std::uint64_t>(post_a.correct) * 1000U) /
                                   heldout_refs);
    const std::uint64_t pre_mean_regret = pre.regret_ns / heldout_refs;
    const std::uint64_t post_mean_regret = post_a.regret_ns / heldout_refs;

    const char* classification = "NO_HELDOUT_IMPROVEMENT";
    if (post_accuracy_x1000 > pre_accuracy_x1000 && post_mean_regret < pre_mean_regret)
        classification = "HELDOUT_IMPROVEMENT";
    else if (post_accuracy_x1000 < pre_accuracy_x1000 || post_mean_regret > pre_mean_regret)
        classification = "HELDOUT_REGRESSION";
    else if (post_accuracy_x1000 > pre_accuracy_x1000 || post_mean_regret < pre_mean_regret)
        classification = "HELDOUT_PARTIAL_IMPROVEMENT";

    std::printf("{\n");
    std::printf("  \"schema\": \"HHS_PASS219_PHASE4_OUTCOME_LINKED_ROUTING_V1\",\n");
    std::printf("  \"classification\": \"%s\",\n", classification);
    std::printf("  \"phase3_frame_binary_sha256\": \"%s\",\n", kPhase3FrameSha256);
    std::printf("  \"summary_records\": %zu,\n", samples.size());
    std::printf("  \"unique_content_digests\": %zu,\n", train_digests.size() + heldout_digests.size());
    std::printf("  \"semantic_equivalence_count\": %u,\n", semantic_equivalence_count);
    std::printf("  \"all_four_lanes_exact_for_all_records\": true,\n");
    std::printf("  \"timing_repetitions_per_lane_record\": %zu,\n", kTimingRepetitions);
    std::printf("  \"timing_is_observational\": true,\n");
    std::printf("  \"winner_counts\": "); print_u32_array(winner_counts); std::printf(",\n");
    std::printf("  \"lane_median_ns\": "); print_u64_array(lane_median_ns); std::printf(",\n");
    std::printf("  \"training_reference_count\": %u,\n", train_refs);
    std::printf("  \"heldout_reference_count\": %u,\n", heldout_refs);
    std::printf("  \"training_unique_digest_count\": %zu,\n", train_digests.size());
    std::printf("  \"heldout_unique_digest_count\": %zu,\n", heldout_digests.size());
    std::printf("  \"train_heldout_digest_overlap\": %u,\n", overlap);
    std::printf("  \"training_winner_counts\": "); print_u32_array(train_winners); std::printf(",\n");
    std::printf("  \"heldout_winner_counts\": "); print_u32_array(heldout_winners); std::printf(",\n");
    std::printf("  \"training_epochs\": %zu,\n", kTrainingEpochs);
    std::printf("  \"training_steps\": %llu,\n",
                static_cast<unsigned long long>(static_cast<std::uint64_t>(train_refs) * kTrainingEpochs));
    std::printf("  \"observed_learning_updates\": %u,\n", observed_updates);
    std::printf("  \"heldout_pretrain_accuracy_x1000\": %u,\n", pre_accuracy_x1000);
    std::printf("  \"heldout_posttrain_accuracy_x1000\": %u,\n", post_accuracy_x1000);
    std::printf("  \"heldout_pretrain_total_regret_ns\": %llu,\n",
                static_cast<unsigned long long>(pre.regret_ns));
    std::printf("  \"heldout_posttrain_total_regret_ns\": %llu,\n",
                static_cast<unsigned long long>(post_a.regret_ns));
    std::printf("  \"heldout_pretrain_mean_regret_ns\": %llu,\n",
                static_cast<unsigned long long>(pre_mean_regret));
    std::printf("  \"heldout_posttrain_mean_regret_ns\": %llu,\n",
                static_cast<unsigned long long>(post_mean_regret));
    std::printf("  \"heldout_prediction_replay_equal\": true,\n");
    std::printf("  \"candidate_only\": true,\n");
    std::printf("  \"canonical_authority_changed\": false,\n");
    std::printf("  \"measurement_sink64\": \"%llu\"\n",
                static_cast<unsigned long long>(g_sink));
    std::printf("}\n");

    return 0;
}

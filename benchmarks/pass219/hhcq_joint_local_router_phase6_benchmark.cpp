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
constexpr std::size_t kLaneCount = HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT;
constexpr std::size_t kTimingRepetitions = 3U;
constexpr std::size_t kTrainingEpochs = 12U;
constexpr std::size_t kAnchorCount = 9U;
constexpr std::uint8_t kSummaryFrameKind = 0U;
constexpr std::array<std::uint8_t, kAnchorCount> kLoShu = {4U,9U,2U,3U,5U,7U,8U,1U,6U};
constexpr std::array<std::uint32_t, kLaneCount> kNativeWidthBits = {8U,64U,64U,36U};
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

struct FrameSample {
    Record record;
    HHSExactVM81Frame frame{};
    HHSExactPass219CoreCircuitFeaturesV1 core{};
    std::array<std::uint64_t, kLaneCount> lane_median_ns{};
    std::array<HHSExactPass219HHCQJointPreparedV1, kAnchorCount> prepared{};
};

struct LocalSample {
    HHSExactPass219HHCQJointPreparedV1 prepared{};
    std::string digest;
    std::array<std::uint64_t, kLaneCount> cost{};
    std::uint8_t target_lane{};
    bool training{};
};

struct EvalSummary {
    std::uint32_t correct{};
    std::uint64_t regret{};
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

bool init_transition(const Record& r, HHSExactPass219Hash216TransitionViewV1& out) {
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
    if (hhs_exact_pass219_audio5184_frame_to_pcm64(&frame, &pcm) != HHS_EXACT_STATUS_OK)
        return false;
    if (hhs_exact_pass219_audio5184_pcm64_to_frame(&pcm, &replay) != HHS_EXACT_STATUS_OK)
        return false;
    if (std::memcmp(&frame, &replay, sizeof(frame)) != 0) return false;
    if (hhs_exact_pass219_audio5184_hydrate(&frame, &hydration) != HHS_EXACT_STATUS_OK)
        return false;
    if (hhs_exact_pass219_audio5184_hydration_validate(&frame, &hydration) != HHS_EXACT_STATUS_OK)
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

bool eval_lane(std::uint8_t lane, const Record& r, const HHSExactVM81Frame& frame) {
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
    if (!eval_lane(lane, r, frame) || !eval_lane(lane, r, frame)) return false;
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

std::uint64_t median_vector(std::vector<std::uint64_t> values) {
    if (values.empty()) return 0U;
    std::sort(values.begin(), values.end());
    return values[values.size() / 2U];
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
    return value >= 0 && (value & 3) != 0;
}

std::uint16_t anchor_for(std::size_t index) {
    const std::uint32_t cell = static_cast<std::uint32_t>(index * 9U + (kLoShu[index] - 1U));
    const std::uint32_t offset =
        (static_cast<std::uint32_t>(kLoShu[(index + 3U) % kAnchorCount]) * 7U +
         static_cast<std::uint32_t>(index)) % 64U;
    return static_cast<std::uint16_t>(cell * 64U + offset);
}

bool prepare_local(
    const HHSExactVM81Frame& frame,
    const HHSExactPass219CoreCircuitFeaturesV1& core,
    std::size_t anchor_index,
    HHSExactPass219HHCQJointPreparedV1& out
) {
    const std::uint16_t anchor = anchor_for(anchor_index);
    const std::uint8_t cell = static_cast<std::uint8_t>(anchor / 64U);
    HHSExactPass219OctonionSurfaceV1 surface{};
    if (hhs_exact_pass219_octonion_from_vm81(
            &frame,
            cell,
            static_cast<std::uint8_t>((cell + 1U) % HHS_EXACT_VM81_CELLS),
            static_cast<std::uint8_t>((cell + 9U) % HHS_EXACT_VM81_CELLS),
            static_cast<std::uint8_t>((cell + 10U) % HHS_EXACT_VM81_CELLS),
            &surface) != HHS_EXACT_STATUS_OK)
        return false;
    const std::int8_t tri = core.trinary_phase[cell % HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_FEATURES];
    return hhs_exact_pass219_hhcq_joint_prepare(
               &frame, anchor,
               surface.state.x, surface.state.y, surface.state.z, surface.state.w,
               tri, &out) == HHS_EXACT_STATUS_OK;
}

bool phase5_roundtrip_exact(
    const HHSExactVM81Frame& frame,
    const HHSExactPass219HHCQJointPreparedV1& prepared
) {
    HHSExactVM81Frame replay{};
    HHSExactPass219HHCQRoundtripReportV1 report{};
    if (hhs_exact_pass219_hhcq_decompose_recompose(
            &frame, &prepared.resolution, &replay, &report) != HHS_EXACT_STATUS_OK)
        return false;
    return report.parameters_visited == HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT &&
           report.orthogonal_partition_complete == 1U && report.no_overlap == 1U &&
           report.no_gap == 1U && report.exact_recomposition == 1U &&
           report.canonical_authority_changed == 0U &&
           report.floating_point_authority == 0U &&
           std::memcmp(&frame, &replay, sizeof(frame)) == 0;
}

bool region_container_exact(
    const HHSExactVM81Frame& frame,
    const HHSExactPass219HHCQJointPreparedV1& prepared,
    std::uint32_t width_bits
) {
    if (width_bits == 0U) return false;
    const std::uint32_t start = prepared.coordinate.region_start;
    const std::uint32_t length = prepared.resolution.resolution_parameters;
    const std::uint32_t end = start + length;
    if (end > HHS_EXACT_VM81_FRAME_BITS || length == 0U) return false;
    std::array<std::uint64_t, HHS_EXACT_VM81_CELLS> replay{};
    const std::uint32_t first = start / width_bits;
    const std::uint32_t last = (end - 1U) / width_bits;
    for (std::uint32_t unit = first; unit <= last; ++unit) {
        const std::uint32_t unit_start = unit * width_bits;
        const std::uint32_t lo = std::max(start, unit_start);
        const std::uint32_t hi = std::min(end, unit_start + width_bits);
        for (std::uint32_t bit = lo; bit < hi; ++bit) {
            const std::uint32_t word = bit / 64U;
            const std::uint32_t offset = bit % 64U;
            if ((frame.words[word] & (UINT64_C(1) << offset)) != 0U)
                replay[word] |= UINT64_C(1) << offset;
        }
    }
    for (std::uint32_t bit = 0U; bit < HHS_EXACT_VM81_FRAME_BITS; ++bit) {
        const std::uint32_t word = bit / 64U;
        const std::uint32_t offset = bit % 64U;
        const bool got = (replay[word] & (UINT64_C(1) << offset)) != 0U;
        const bool expected = bit >= start && bit < end &&
            (frame.words[word] & (UINT64_C(1) << offset)) != 0U;
        if (got != expected) return false;
    }
    return true;
}

std::uint64_t amplification_x1024(
    const HHSExactPass219HHCQJointPreparedV1& prepared,
    std::uint32_t width_bits
) {
    const std::uint64_t start = prepared.coordinate.region_start;
    const std::uint64_t length = prepared.resolution.resolution_parameters;
    const std::uint64_t end = start + length;
    const std::uint64_t first = start / width_bits;
    const std::uint64_t last = (end - 1U) / width_bits;
    const std::uint64_t touched_bits = (last - first + 1U) * width_bits;
    return (touched_bits * UINT64_C(1024) + length - 1U) / length;
}

bool state_clean(const HHSExactPass219HHCQJointStateV1& state) {
    return state.candidate_only == 1U && state.bounded_weights == 1U &&
           state.fixed_size_policy_state == 1U && state.exact_integer_only == 1U &&
           state.canonical_mutation_authority == 0U &&
           state.canonical_hash72_authority == 0U &&
           state.canonical_hash216_authority == 0U &&
           state.canonical_persistence_authority == 0U &&
           state.floating_point_authority == 0U;
}

bool evaluate(
    const HHSExactPass219HHCQJointStateV1& state,
    const std::vector<LocalSample>& samples,
    EvalSummary& out
) {
    for (const LocalSample& sample : samples) {
        if (sample.training) continue;
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
        out.predictions.push_back(decision.selected_lane);
        if (decision.selected_lane == sample.target_lane) ++out.correct;
        out.regret += sample.cost[decision.selected_lane] - sample.cost[sample.target_lane];
    }
    return true;
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
    HHSExactPass219HHCQJointDescriptorV1 descriptor{};
    if (hhs_exact_pass219_hhcq_joint_descriptor(&descriptor) != HHS_EXACT_STATUS_OK ||
        descriptor.phase5_resolution_constraint_authority != 1U ||
        descriptor.fixed_size_policy_state != 1U || descriptor.candidate_only != 1U ||
        descriptor.floating_point_authority != 0U)
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
            if (!measure_lane(lane, fs.record, fs.frame, fs.lane_median_ns[lane]))
                return 12;
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
    if (frames.size() != 529U || whole_frame_semantic_checks != 529U * kLaneCount ||
        phase5_roundtrip_checks != 529U * kAnchorCount ||
        local_container_checks != 529U * kAnchorCount * kLaneCount)
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
                const std::uint64_t amp = amplification_x1024(sample.prepared, kNativeWidthBits[lane]);
                sample.cost[lane] = (normalized_x1m * amp + UINT64_C(512)) / UINT64_C(1024);
                if (sample.cost[lane] == 0U) sample.cost[lane] = 1U;
                if (lane != 0U && sample.cost[lane] < sample.cost[sample.target_lane])
                    sample.target_lane = static_cast<std::uint8_t>(lane);
            }
            ++target_lane_counts[sample.target_lane];
            ++resolution_counts[sample.prepared.resolution.resolution_index];
            samples.push_back(std::move(sample));
        }
    }
    if (samples.size() != 529U * kAnchorCount) return 18;

    std::set<std::string> train_digests;
    std::set<std::string> heldout_digests;
    std::uint32_t train_samples = 0U;
    std::uint32_t heldout_samples = 0U;
    std::uint32_t train_refs = 0U;
    std::uint32_t heldout_refs = 0U;
    for (const FrameSample& fs : frames) {
        if (training_bucket(fs.record.chunk_digest)) {
            train_digests.insert(fs.record.chunk_digest);
            ++train_refs;
        } else {
            heldout_digests.insert(fs.record.chunk_digest);
            ++heldout_refs;
        }
    }
    for (const LocalSample& sample : samples) {
        if (sample.training) ++train_samples; else ++heldout_samples;
    }
    std::uint32_t overlap = 0U;
    for (const auto& digest : train_digests)
        if (heldout_digests.count(digest) != 0U) ++overlap;
    if (train_refs == 0U || heldout_refs == 0U || overlap != 0U ||
        train_digests.size() + heldout_digests.size() != 489U ||
        train_samples != train_refs * kAnchorCount || heldout_samples != heldout_refs * kAnchorCount)
        return 19;

    std::uint32_t resolution_diversity = 0U;
    std::uint32_t target_lane_diversity = 0U;
    for (std::size_t i = 0U; i < resolution_counts.size(); ++i)
        if (resolution_counts[i] != 0U) ++resolution_diversity;
    for (std::size_t lane = 0U; lane < kLaneCount; ++lane)
        if (target_lane_counts[lane] != 0U) ++target_lane_diversity;
    if (resolution_diversity < 2U || target_lane_diversity < 1U) return 20;

    HHSExactPass219HHCQJointStateV1 initial{};
    if (hhs_exact_pass219_hhcq_joint_state_init(&initial) != HHS_EXACT_STATUS_OK ||
        !state_clean(initial)) return 21;
    const std::size_t fixed_policy_state_bytes = sizeof(initial);

    EvalSummary pre{};
    if (!evaluate(initial, samples, pre) || pre.predictions.size() != heldout_samples)
        return 22;

    HHSExactPass219HHCQJointStateV1 trained{};
    if (hhs_exact_pass219_hhcq_joint_state_init(&trained) != HHS_EXACT_STATUS_OK ||
        !state_clean(trained)) return 23;
    std::uint32_t observed_updates = 0U;
    for (std::size_t epoch = 0U; epoch < kTrainingEpochs; ++epoch) {
        for (const LocalSample& sample : samples) {
            if (!sample.training) continue;
            HHSExactPass219HHCQJointDecisionV1 decision{};
            const std::uint8_t locked_resolution = sample.prepared.resolution.resolution_index;
            const std::uint16_t locked_parameters = sample.prepared.resolution.resolution_parameters;
            if (hhs_exact_pass219_hhcq_joint_step(
                    &sample.prepared, sample.target_lane, 1, &trained, &decision) !=
                HHS_EXACT_STATUS_OK)
                return 24;
            if (decision.resolution_index != locked_resolution ||
                decision.resolution_parameters != locked_parameters ||
                decision.phase5_resolution_locked != 1U)
                return 25;
            if (decision.updated != 0U) ++observed_updates;
        }
    }
    if (!state_clean(trained) || sizeof(trained) != fixed_policy_state_bytes) return 26;

    EvalSummary post_a{};
    EvalSummary post_b{};
    if (!evaluate(trained, samples, post_a) || !evaluate(trained, samples, post_b)) return 27;
    if (post_a.predictions != post_b.predictions || post_a.correct != post_b.correct ||
        post_a.regret != post_b.regret) return 28;

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
    std::uint64_t fixed_lane_heldout_regret = 0U;
    for (const LocalSample& sample : samples) {
        if (sample.training) continue;
        fixed_lane_heldout_regret += sample.cost[best_fixed_lane] - sample.cost[sample.target_lane];
    }

    const std::uint32_t pre_accuracy_x1000 =
        static_cast<std::uint32_t>((static_cast<std::uint64_t>(pre.correct) * 1000U) /
                                   heldout_samples);
    const std::uint32_t post_accuracy_x1000 =
        static_cast<std::uint32_t>((static_cast<std::uint64_t>(post_a.correct) * 1000U) /
                                   heldout_samples);
    const std::uint64_t pre_mean_regret = pre.regret / heldout_samples;
    const std::uint64_t post_mean_regret = post_a.regret / heldout_samples;
    const std::uint64_t fixed_mean_regret = fixed_lane_heldout_regret / heldout_samples;

    const char* classification = "NO_HELDOUT_IMPROVEMENT";
    if (post_accuracy_x1000 > pre_accuracy_x1000 && post_mean_regret < pre_mean_regret)
        classification = "HELDOUT_IMPROVEMENT";
    else if (post_accuracy_x1000 < pre_accuracy_x1000 || post_mean_regret > pre_mean_regret)
        classification = "HELDOUT_REGRESSION";
    else if (post_accuracy_x1000 > pre_accuracy_x1000 || post_mean_regret < pre_mean_regret)
        classification = "HELDOUT_PARTIAL_IMPROVEMENT";

    std::printf("{\n");
    std::printf("  \"schema\": \"HHS_PASS219_HHCQ_JOINT_LOCAL_ROUTER_PHASE6_V1\",\n");
    std::printf("  \"classification\": \"%s\",\n", classification);
    std::printf("  \"phase3_frame_binary_sha256\": \"%s\",\n", kPhase3FrameSha256);
    std::printf("  \"summary_records\": %zu,\n", frames.size());
    std::printf("  \"anchors_per_record\": %zu,\n", kAnchorCount);
    std::printf("  \"local_samples\": %zu,\n", samples.size());
    std::printf("  \"whole_frame_semantic_checks\": %u,\n", whole_frame_semantic_checks);
    std::printf("  \"phase5_exact_roundtrip_checks\": %u,\n", phase5_roundtrip_checks);
    std::printf("  \"lane_local_container_identity_checks\": %u,\n", local_container_checks);
    std::printf("  \"global_lane_median_ns\": "); print_u64_array(global_lane_median_ns); std::printf(",\n");
    std::printf("  \"timing_repetitions_per_lane_record\": %zu,\n", kTimingRepetitions);
    std::printf("  \"timing_is_observational\": true,\n");
    std::printf("  \"local_cost_is_normalized_observational_timing_times_exact_native_width_amplification\": true,\n");
    std::printf("  \"native_width_bits\": [%u,%u,%u,%u],\n",
                kNativeWidthBits[0], kNativeWidthBits[1], kNativeWidthBits[2], kNativeWidthBits[3]);
    std::printf("  \"target_lane_counts\": "); print_u32_array(target_lane_counts); std::printf(",\n");
    std::printf("  \"target_lane_diversity\": %u,\n", target_lane_diversity);
    std::printf("  \"resolution_diversity\": %u,\n", resolution_diversity);
    std::printf("  \"training_reference_count\": %u,\n", train_refs);
    std::printf("  \"heldout_reference_count\": %u,\n", heldout_refs);
    std::printf("  \"training_local_samples\": %u,\n", train_samples);
    std::printf("  \"heldout_local_samples\": %u,\n", heldout_samples);
    std::printf("  \"training_unique_digest_count\": %zu,\n", train_digests.size());
    std::printf("  \"heldout_unique_digest_count\": %zu,\n", heldout_digests.size());
    std::printf("  \"train_heldout_digest_overlap\": %u,\n", overlap);
    std::printf("  \"training_epochs\": %zu,\n", kTrainingEpochs);
    std::printf("  \"training_steps\": %llu,\n",
                static_cast<unsigned long long>(static_cast<std::uint64_t>(train_samples) * kTrainingEpochs));
    std::printf("  \"observed_learning_updates\": %u,\n", observed_updates);
    std::printf("  \"fixed_policy_state_bytes\": %zu,\n", fixed_policy_state_bytes);
    std::printf("  \"heldout_pretrain_accuracy_x1000\": %u,\n", pre_accuracy_x1000);
    std::printf("  \"heldout_posttrain_accuracy_x1000\": %u,\n", post_accuracy_x1000);
    std::printf("  \"heldout_pretrain_total_regret\": %llu,\n",
                static_cast<unsigned long long>(pre.regret));
    std::printf("  \"heldout_posttrain_total_regret\": %llu,\n",
                static_cast<unsigned long long>(post_a.regret));
    std::printf("  \"heldout_pretrain_mean_regret\": %llu,\n",
                static_cast<unsigned long long>(pre_mean_regret));
    std::printf("  \"heldout_posttrain_mean_regret\": %llu,\n",
                static_cast<unsigned long long>(post_mean_regret));
    std::printf("  \"best_training_fixed_lane\": %u,\n", best_fixed_lane);
    std::printf("  \"heldout_fixed_lane_mean_regret\": %llu,\n",
                static_cast<unsigned long long>(fixed_mean_regret));
    std::printf("  \"heldout_prediction_replay_equal\": true,\n");
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

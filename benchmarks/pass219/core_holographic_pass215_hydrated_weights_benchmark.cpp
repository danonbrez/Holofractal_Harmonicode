#include "hhs_runtime_exact_abi.h"

#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <map>
#include <set>
#include <string>

namespace {

constexpr std::uint32_t kVersion = 1U;
constexpr std::size_t kCheckpointCount = 2U;
constexpr std::size_t kFrameKindCount = 4U;
constexpr std::size_t kLaneCount = HHS_EXACT_PASS219_HOLO4_LANE_COUNT;
constexpr std::size_t kComponentCount = 6U;
constexpr std::uint32_t kPhase1Work = 81U;
constexpr std::uint32_t kPhase2SharedWork = 2061U;
constexpr std::uint32_t kPhase2IndependentWork = 7164U;
constexpr std::uint32_t kCombinedSharedWork = kPhase1Work + kPhase2SharedWork;
constexpr std::uint32_t kCombinedIndependentWork = kPhase1Work + kPhase2IndependentWork;

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
    std::array<std::uint8_t, HHS_EXACT_VM81_FRAME_BYTES> frame_bytes{};
};

struct DigestLanePair {
    int earlier{-1};
    int later{-1};
};

struct RunSummary {
    std::uint32_t record_count{};
    std::uint32_t feature_parity_count{};
    std::uint32_t transition_identity_preserved_count{};
    std::uint32_t authority_violation_count{};
    std::uint32_t short_chunk_count{};
    std::uint64_t aggregate_signature{};
    std::array<std::array<std::array<std::uint32_t, kLaneCount>, kFrameKindCount>, kCheckpointCount> lane_counts{};
    std::array<std::uint32_t, kCheckpointCount> summary_reference_counts{};
    std::set<std::string> unique_digests;
    std::map<std::string, DigestLanePair> summary_lane_by_digest;
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
    return true;
}

std::uint64_t mix64(std::uint64_t x) {
    x ^= x >> 30U;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27U;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31U;
    return x;
}

bool equal_features(
    const HHSExactPass219CoreCircuitFeaturesV1& a,
    const HHSExactPass219CoreCircuitFeaturesV1& b
) {
    if (a.struct_size != b.struct_size || a.version != b.version ||
        a.word_visits != b.word_visits || a.nonzero_words != b.nonzero_words ||
        a.total_popcount != b.total_popcount ||
        a.xor_signature64 != b.xor_signature64 ||
        a.sum_signature64 != b.sum_signature64 ||
        a.hydration_signature64 != b.hydration_signature64) return false;
    for (std::size_t i = 0; i < HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_FEATURES; ++i) {
        if (a.phase_popcount[i] != b.phase_popcount[i] ||
            a.trinary_phase[i] != b.trinary_phase[i]) return false;
    }
    for (std::size_t i = 0; i < HHS_EXACT_PASS219_CORE_CIRCUIT_LOSHU_FEATURES; ++i) {
        if (a.loshu_popcount[i] != b.loshu_popcount[i]) return false;
    }
    return true;
}

bool prepared_authority_clean(const HHSExactPass219Holo4PreparedV1& p) {
    return p.candidate_only == 1U && p.exact_integer_only == 1U &&
           p.canonical_mutation_authority == 0U &&
           p.canonical_hash72_authority == 0U &&
           p.canonical_hash216_authority == 0U &&
           p.canonical_persistence_authority == 0U &&
           p.floating_point_authority == 0U;
}

bool decision_authority_clean(const HHSExactPass219Holo4DecisionV1& d) {
    return d.candidate_only == 1U && d.exact_integer_only == 1U &&
           d.canonical_mutation_authority == 0U &&
           d.canonical_hash72_authority == 0U &&
           d.canonical_hash216_authority == 0U &&
           d.canonical_persistence_authority == 0U &&
           d.floating_point_authority == 0U;
}

bool state_authority_clean(const HHSExactPass219Holo4StateV1& s) {
    return s.candidate_only == 1U && s.exact_integer_only == 1U &&
           s.canonical_mutation_authority == 0U &&
           s.canonical_hash72_authority == 0U &&
           s.canonical_hash216_authority == 0U &&
           s.canonical_persistence_authority == 0U &&
           s.floating_point_authority == 0U;
}

bool run_file(const char* path, RunSummary& out) {
    std::ifstream in(path, std::ios::binary);
    if (!in) return false;
    std::array<char, 8> magic{};
    if (!read_exact(in, magic.data(), magic.size()) ||
        std::string(magic.data(), magic.size()) != "HHS3WGT1") return false;
    std::uint32_t version = 0U;
    std::uint32_t record_count = 0U;
    std::uint32_t checkpoint_count = 0U;
    std::uint32_t frame_kind_count = 0U;
    if (!read_u32_le(in, version) || !read_u32_le(in, record_count) ||
        !read_u32_le(in, checkpoint_count) || !read_u32_le(in, frame_kind_count)) return false;
    if (version != kVersion || checkpoint_count != kCheckpointCount ||
        frame_kind_count != kFrameKindCount || record_count == 0U) return false;

    HHSExactPass219Holo4StateV1 state{};
    if (hhs_exact_pass219_holo4_state_init(&state) != HHS_EXACT_STATUS_OK ||
        !state_authority_clean(state)) return false;

    for (std::uint32_t index = 0U; index < record_count; ++index) {
        Record record{};
        if (!read_record(in, record)) return false;
        if (record.checkpoint_slot >= kCheckpointCount ||
            record.frame_kind >= kFrameKindCount ||
            record.component_index >= kComponentCount ||
            record.reference_ordinal >= record_count / kFrameKindCount) return false;
        if (record.raw_chunk_bytes < HHS_EXACT_VM81_FRAME_BYTES) ++out.short_chunk_count;

        HHSExactVM81Frame frame{};
        if (hhs_exact_vm81_frame_import_le(
                record.frame_bytes.data(), record.frame_bytes.size(), &frame) != HHS_EXACT_STATUS_OK)
            return false;

        HHSExactPass219CoreCircuitFeaturesV1 direct{};
        if (hhs_exact_pass219_core_circuit_extract(&frame, &direct) != HHS_EXACT_STATUS_OK)
            return false;
        if (direct.word_visits != HHS_EXACT_VM81_CELLS) return false;

        HHSExactPass219Hash216TransitionViewV1 transition{};
        if (hhs_exact_pass219_hash216_transition_init(
                record.previous.data(), record.change.data(), record.receipt.data(),
                record.identity.data(), &transition) != HHS_EXACT_STATUS_OK)
            return false;

        HHSExactPass219Holo4PreparedV1 prepared{};
        if (hhs_exact_pass219_holo4_prepare(&frame, &transition, &state, &prepared) != HHS_EXACT_STATUS_OK)
            return false;
        if (prepared.word_visits != HHS_EXACT_VM81_CELLS ||
            prepared.graph_edge_visits != HHS_EXACT_PASS219_HOLO4_DIRECTED_GRAPH_EDGES)
            return false;
        if (!equal_features(direct, prepared.core_features)) return false;
        ++out.feature_parity_count;
        if (std::strcmp(prepared.source_transition_identity216, record.identity.data()) != 0)
            return false;

        HHSExactPass219Holo4LaneScoreV1 lanes[HHS_EXACT_PASS219_HOLO4_LANE_COUNT]{};
        for (std::uint8_t lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane) {
            if (hhs_exact_pass219_holo4_score_lane(&prepared, &state, lane, &lanes[lane]) != HHS_EXACT_STATUS_OK)
                return false;
        }
        HHSExactPass219Holo4DecisionV1 decision{};
        if (hhs_exact_pass219_holo4_finalize(
                &prepared, lanes, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
                &state, &decision) != HHS_EXACT_STATUS_OK)
            return false;
        if (decision.selected_lane >= kLaneCount || decision.updated != 0U)
            return false;
        if (std::strcmp(decision.source_transition_identity216, record.identity.data()) != 0)
            return false;
        ++out.transition_identity_preserved_count;
        if (!prepared_authority_clean(prepared) || !decision_authority_clean(decision) ||
            !state_authority_clean(state)) ++out.authority_violation_count;

        ++out.lane_counts[record.checkpoint_slot][record.frame_kind][decision.selected_lane];
        out.unique_digests.insert(record.chunk_digest);
        if (record.frame_kind == 0U) {
            ++out.summary_reference_counts[record.checkpoint_slot];
            DigestLanePair& pair = out.summary_lane_by_digest[record.chunk_digest];
            int& slot = record.checkpoint_slot == 0U ? pair.earlier : pair.later;
            if (slot != -1 && slot != static_cast<int>(decision.selected_lane)) return false;
            slot = static_cast<int>(decision.selected_lane);
        }

        std::uint64_t local = decision.decision_signature64 ^ direct.hydration_signature64;
        for (std::size_t lane = 0; lane < kLaneCount; ++lane)
            local = mix64(local ^ static_cast<std::uint64_t>(lanes[lane].score));
        out.aggregate_signature = mix64(
            out.aggregate_signature ^ local ^
            (static_cast<std::uint64_t>(record.checkpoint_slot) << 61U) ^
            (static_cast<std::uint64_t>(record.frame_kind) << 57U) ^
            static_cast<std::uint64_t>(record.reference_ordinal));
        ++out.record_count;
    }

    if (out.record_count != record_count || out.feature_parity_count != record_count ||
        out.transition_identity_preserved_count != record_count ||
        out.authority_violation_count != 0U || state.update_count != 0U ||
        state.step_count != record_count) return false;
    char trailing = 0;
    if (in.read(&trailing, 1)) return false;
    return true;
}

bool summaries_equal(const RunSummary& a, const RunSummary& b) {
    return a.record_count == b.record_count &&
           a.feature_parity_count == b.feature_parity_count &&
           a.transition_identity_preserved_count == b.transition_identity_preserved_count &&
           a.authority_violation_count == b.authority_violation_count &&
           a.short_chunk_count == b.short_chunk_count &&
           a.aggregate_signature == b.aggregate_signature &&
           a.lane_counts == b.lane_counts &&
           a.summary_reference_counts == b.summary_reference_counts &&
           a.unique_digests == b.unique_digests &&
           a.summary_lane_by_digest.size() == b.summary_lane_by_digest.size();
}

void print_lane_array(const std::array<std::uint32_t, kLaneCount>& values) {
    std::printf("[%u,%u,%u,%u]", values[0], values[1], values[2], values[3]);
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::fprintf(stderr, "usage: %s <phase3-frames.bin>\n", argv[0]);
        return 2;
    }
    HHSExactPass219Holo4DescriptorV1 descriptor{};
    if (hhs_exact_pass219_holo4_descriptor(&descriptor) != HHS_EXACT_STATUS_OK)
        return 3;
    if (descriptor.cell_count != 81U || descriptor.peers_per_cell != 20U ||
        descriptor.directed_graph_edges != 1620U || descriptor.lane_count != 4U ||
        descriptor.phase_modulus != 72U || descriptor.update_quantum != 5U)
        return 4;

    RunSummary first{};
    RunSummary replay{};
    if (!run_file(argv[1], first)) return 5;
    if (!run_file(argv[1], replay)) return 6;
    if (!summaries_equal(first, replay)) return 7;

    std::uint32_t reused_summary_digests = 0U;
    std::uint32_t stable_reused = 0U;
    std::uint32_t changed_reused = 0U;
    std::array<std::array<std::uint32_t, kLaneCount>, kLaneCount> migration{};
    for (const auto& entry : first.summary_lane_by_digest) {
        const DigestLanePair& pair = entry.second;
        if (pair.earlier >= 0 && pair.later >= 0) {
            ++reused_summary_digests;
            ++migration[static_cast<std::size_t>(pair.earlier)][static_cast<std::size_t>(pair.later)];
            if (pair.earlier == pair.later) ++stable_reused;
            else ++changed_reused;
        }
    }

    constexpr std::uint32_t phase2_reduction_x1000 =
        (kPhase2IndependentWork * 1000U) / kPhase2SharedWork;
    constexpr std::uint32_t combined_reduction_x1000 =
        (kCombinedIndependentWork * 1000U) / kCombinedSharedWork;

    std::printf("{\n");
    std::printf("  \"schema\": \"HHS_PASS219_PHASE3_PASS215_HYDRATED_WEIGHT_ROUTING_V1\",\n");
    std::printf("  \"record_count\": %u,\n", first.record_count);
    std::printf("  \"feature_parity_count\": %u,\n", first.feature_parity_count);
    std::printf("  \"phase1_direct_and_phase2_embedded_core_equal\": true,\n");
    std::printf("  \"transition_identity_preserved_count\": %u,\n", first.transition_identity_preserved_count);
    std::printf("  \"deterministic_replay_equal\": true,\n");
    std::printf("  \"aggregate_signature64\": \"%llu\",\n", static_cast<unsigned long long>(first.aggregate_signature));
    std::printf("  \"unique_content_chunks_observed\": %zu,\n", first.unique_digests.size());
    std::printf("  \"reused_summary_chunk_digests\": %u,\n", reused_summary_digests);
    std::printf("  \"reused_summary_lane_stable\": %u,\n", stable_reused);
    std::printf("  \"reused_summary_lane_changed_with_checkpoint_provenance\": %u,\n", changed_reused);
    std::printf("  \"short_chunk_zero_padding_count\": %u,\n", first.short_chunk_count);
    std::printf("  \"candidate_only\": true,\n");
    std::printf("  \"canonical_authority_changed\": false,\n");
    std::printf("  \"phase1_word_work_per_record\": %u,\n", kPhase1Work);
    std::printf("  \"phase2_independent_lane_work_per_record\": %u,\n", kPhase2IndependentWork);
    std::printf("  \"phase2_shared_tensor_work_per_record\": %u,\n", kPhase2SharedWork);
    std::printf("  \"phase2_shared_work_reduction_x1000\": %u,\n", phase2_reduction_x1000);
    std::printf("  \"phase1_plus_independent_lane_work_per_record\": %u,\n", kCombinedIndependentWork);
    std::printf("  \"phase1_plus_shared_tensor_work_per_record\": %u,\n", kCombinedSharedWork);
    std::printf("  \"combined_shared_work_reduction_x1000\": %u,\n", combined_reduction_x1000);
    std::printf("  \"summary_reference_counts\": [%u,%u],\n",
                first.summary_reference_counts[0], first.summary_reference_counts[1]);
    std::printf("  \"summary_lane_counts\": [");
    print_lane_array(first.lane_counts[0][0]);
    std::printf(",");
    print_lane_array(first.lane_counts[1][0]);
    std::printf("],\n");
    std::printf("  \"head_lane_counts\": [");
    print_lane_array(first.lane_counts[0][1]);
    std::printf(",");
    print_lane_array(first.lane_counts[1][1]);
    std::printf("],\n");
    std::printf("  \"middle_lane_counts\": [");
    print_lane_array(first.lane_counts[0][2]);
    std::printf(",");
    print_lane_array(first.lane_counts[1][2]);
    std::printf("],\n");
    std::printf("  \"tail_lane_counts\": [");
    print_lane_array(first.lane_counts[0][3]);
    std::printf(",");
    print_lane_array(first.lane_counts[1][3]);
    std::printf("],\n");
    std::printf("  \"reused_summary_lane_migration_matrix\": [");
    for (std::size_t row = 0; row < kLaneCount; ++row) {
        if (row) std::printf(",");
        print_lane_array(migration[row]);
    }
    std::printf("]\n");
    std::printf("}\n");

    if (first.short_chunk_count != 0U) return 8;
    if (phase2_reduction_x1000 != 3475U || combined_reduction_x1000 != 3382U)
        return 9;
    return 0;
}

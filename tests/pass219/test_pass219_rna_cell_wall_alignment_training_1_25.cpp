#include "hhs_pass219_rna_cell_wall_alignment_training_1_25.hpp"

#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>

using hhs::rna::AlignmentTrainingCycleResultV1;
using hhs::rna::AlignmentTrainingDispositionV1;
using hhs::rna::AlignmentTrainingSampleV1;
using hhs::rna::CoreHolographicRNACellWall;
using hhs::rna::OrthogonalGlyphMembrane;
using hhs::rna::RNACellWallAlignmentTrainer;

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static void fill_hash72(char out[HHS_EXACT_HASH72_STRLEN], std::uint8_t offset) {
    for (std::size_t i = 0U; i < HHS_EXACT_HASH72_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_HASH72_LEN] = '\0';
}

static void fill_identity216(char out[HHS_EXACT_UQCEL_HASH216_STRLEN], std::uint8_t offset) {
    for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i * 13U + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
}

static HHSExactPass219Hash216TransitionViewV1 build_transition(std::uint8_t offset) {
    HHSExactPass219Hash216TransitionViewV1 transition{};
    char previous[HHS_EXACT_HASH72_STRLEN]{};
    char change[HHS_EXACT_HASH72_STRLEN]{};
    char receipt[HHS_EXACT_HASH72_STRLEN]{};
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN]{};
    fill_hash72(previous, offset);
    fill_hash72(change, static_cast<std::uint8_t>(offset + 1U));
    fill_hash72(receipt, static_cast<std::uint8_t>(offset + 2U));
    fill_identity216(identity, static_cast<std::uint8_t>(offset + 3U));
    if (hhs_exact_pass219_hash216_transition_init(
            previous, change, receipt, identity, &transition) != HHS_EXACT_STATUS_OK)
        std::memset(&transition, 0, sizeof(transition));
    return transition;
}

static HHSExactVM81Frame build_frame(std::uint64_t salt) {
    HHSExactVM81Frame frame{};
    for (std::uint32_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        const std::uint64_t v =
            (UINT64_C(0xd6e8feb86659fd93) ^ salt) * static_cast<std::uint64_t>(i + 1U);
        frame.words[i] = v ^ (UINT64_C(1) << (i % 63U)) ^ (salt << (i % 7U));
    }
    return frame;
}

static std::uint8_t selected_lane_for(
    CoreHolographicRNACellWall& wall,
    const HHSExactPass219Holo4StateV1& state,
    const HHSExactVM81Frame& frame,
    const HHSExactPass219Hash216TransitionViewV1& transition
) {
    HHSExactPass219Holo4StateV1 probe_state = state;
    HHSExactPass219Holo4PreparedV1 prepared{};
    HHSExactPass219Holo4DecisionV1 decision{};
    if (wall.route_parallel(
            frame, transition, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
            probe_state, prepared, decision) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE;
    return decision.selected_lane;
}

int main() {
    std::uint8_t one = 1U;
    HHSExactBigUIntView a2{
        static_cast<std::uint32_t>(sizeof(HHSExactBigUIntView)), 1U, &one};
    HHSExactBigUIntView delta{
        static_cast<std::uint32_t>(sizeof(HHSExactBigUIntView)), 1U, &one};
    OrthogonalGlyphMembrane membrane(a2, delta);
    CHECK(membrane.status() == HHS_EXACT_STATUS_OK);
    CoreHolographicRNACellWall wall(membrane);
    CHECK(wall.status() == HHS_EXACT_STATUS_OK);
    RNACellWallAlignmentTrainer trainer(wall);
    CHECK(trainer.status() == HHS_EXACT_STATUS_OK);

    HHSExactPass219Holo4StateV1 baseline{};
    CHECK(hhs_exact_pass219_holo4_state_init(&baseline) == HHS_EXACT_STATUS_OK);
    const HHSExactPass219Holo4StateV1 frozen_baseline = baseline;

    std::array<AlignmentTrainingSampleV1, 3> samples{};
    for (std::size_t i = 0U; i < samples.size(); ++i) {
        samples[i].frame = build_frame(UINT64_C(0x100) + i * UINT64_C(0x31));
        samples[i].transition = build_transition(static_cast<std::uint8_t>(11U + i * 7U));
        const std::uint8_t selected = selected_lane_for(
            wall, baseline, samples[i].frame, samples[i].transition);
        CHECK(selected < HHS_EXACT_PASS219_HOLO4_LANE_COUNT);
        samples[i].feedback_lane = static_cast<std::uint8_t>(
            (selected + 1U + static_cast<std::uint8_t>(i)) % HHS_EXACT_PASS219_HOLO4_LANE_COUNT);
        if (samples[i].feedback_lane == selected)
            samples[i].feedback_lane = static_cast<std::uint8_t>((selected + 1U) % HHS_EXACT_PASS219_HOLO4_LANE_COUNT);
        samples[i].feedback_trinary = 1;
    }

    HHSExactPass219Holo4StateV1 candidate{};
    AlignmentTrainingCycleResultV1 result{};
    CHECK(trainer.train_reverse_cycle(
              samples.data(), samples.size(), baseline, candidate, result) == HHS_EXACT_STATUS_OK);
    CHECK(result.status == HHS_EXACT_STATUS_OK);
    CHECK(result.disposition == AlignmentTrainingDispositionV1::CANDIDATE_READY);
    CHECK(result.reverse_order_applied);
    CHECK(result.bounded_backward_credit);
    CHECK(result.reverse_training_sample_count == samples.size());
    CHECK(result.protected_replay_count == 0U);
    CHECK(result.update_event_count > 0U);
    CHECK(result.dependency_scoped_delta_observed);
    CHECK(result.anti_forgetting_passed);
    CHECK(result.candidate_only);
    CHECK(result.exact_integer_only);
    CHECK(!result.canonical_mutation_authority);
    CHECK(!result.canonical_hash72_authority);
    CHECK(!result.canonical_hash216_authority);
    CHECK(!result.canonical_persistence_authority);
    CHECK(!result.floating_point_authority);
    CHECK(std::memcmp(&baseline, &frozen_baseline, sizeof(baseline)) == 0);
    CHECK(hhs_exact_pass219_holo4_validate_state(&candidate) == HHS_EXACT_STATUS_OK);

    /* The trainer must equal the inherited learner executed in reverse order. */
    HHSExactPass219Holo4StateV1 manual = baseline;
    for (std::size_t remaining = samples.size(); remaining > 0U; --remaining) {
        const AlignmentTrainingSampleV1& sample = samples[remaining - 1U];
        HHSExactPass219Holo4PreparedV1 prepared{};
        HHSExactPass219Holo4DecisionV1 decision{};
        CHECK(wall.route_parallel(
                  sample.frame, sample.transition,
                  sample.feedback_lane, sample.feedback_trinary,
                  manual, prepared, decision) == HHS_EXACT_STATUS_OK);
    }
    CHECK(std::memcmp(&manual, &candidate, sizeof(candidate)) == 0);

    /* Identical baseline/evidence must replay to the identical candidate and receipt. */
    HHSExactPass219Holo4StateV1 candidate_replay{};
    AlignmentTrainingCycleResultV1 result_replay{};
    CHECK(trainer.train_reverse_cycle(
              samples.data(), samples.size(), baseline, candidate_replay, result_replay) == HHS_EXACT_STATUS_OK);
    CHECK(std::memcmp(&candidate, &candidate_replay, sizeof(candidate)) == 0);
    CHECK(result.training_signature64 == result_replay.training_signature64);
    CHECK(result.changed_core_weight_count == result_replay.changed_core_weight_count);
    CHECK(result.changed_cell_weight_count == result_replay.changed_cell_weight_count);
    CHECK(result.changed_bank_weight_count == result_replay.changed_bank_weight_count);
    CHECK(result.changed_lane_bias_count == result_replay.changed_lane_bias_count);

    /*
     * Protected historical replay must veto a candidate that learns the same
     * protected stimulus toward a different lane strongly enough to change its
     * baseline decision.  The rejected output is the exact baseline state.
     */
    std::array<AlignmentTrainingSampleV1, hhs::rna::HHS_PASS219_RNA_ALIGNMENT_MAX_SAMPLES> guarded{};
    guarded[0].frame = build_frame(UINT64_C(0x4242));
    guarded[0].transition = build_transition(37U);
    guarded[0].protected_replay = true;
    const std::uint8_t protected_lane = selected_lane_for(
        wall, baseline, guarded[0].frame, guarded[0].transition);
    CHECK(protected_lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT);
    const std::uint8_t target_lane = static_cast<std::uint8_t>(
        (protected_lane + 1U) % HHS_EXACT_PASS219_HOLO4_LANE_COUNT);
    for (std::size_t i = 1U; i < guarded.size(); ++i) {
        guarded[i].frame = guarded[0].frame;
        guarded[i].transition = guarded[0].transition;
        guarded[i].feedback_lane = target_lane;
        guarded[i].feedback_trinary = 1;
    }

    HHSExactPass219Holo4StateV1 rejected_candidate{};
    AlignmentTrainingCycleResultV1 rejected_result{};
    CHECK(trainer.train_reverse_cycle(
              guarded.data(), guarded.size(), baseline,
              rejected_candidate, rejected_result) == HHS_EXACT_STATUS_OK);
    CHECK(rejected_result.disposition == AlignmentTrainingDispositionV1::REJECT_PROTECTED_REPLAY);
    CHECK(rejected_result.protected_replay_count == 1U);
    CHECK(rejected_result.protected_replay_failure_count > 0U);
    CHECK(!rejected_result.anti_forgetting_passed);
    CHECK(std::memcmp(&rejected_candidate, &baseline, sizeof(baseline)) == 0);

    /* Malformed feedback cannot enter the training relation. */
    AlignmentTrainingSampleV1 invalid = samples[0];
    invalid.feedback_lane = HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE;
    invalid.feedback_trinary = 1;
    HHSExactPass219Holo4StateV1 invalid_candidate{};
    AlignmentTrainingCycleResultV1 invalid_result{};
    CHECK(trainer.train_reverse_cycle(
              &invalid, 1U, baseline, invalid_candidate, invalid_result) == HHS_EXACT_STATUS_RANGE_ERROR);
    CHECK(invalid_result.disposition == AlignmentTrainingDispositionV1::INVALID_SAMPLE);
    CHECK(std::memcmp(&invalid_candidate, &baseline, sizeof(baseline)) == 0);

    return 0;
}

#include "hhs_pass219_rna_cell_wall_alignment_training_1_26.hpp"

#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>

using hhs::rna::AlignmentAuthorityPlaneV2;
using hhs::rna::AlignmentTrainingCycleResultV1;
using hhs::rna::AlignmentTrainingCycleResultV2;
using hhs::rna::AlignmentTrainingDispositionV1;
using hhs::rna::AlignmentTrainingSampleV1;
using hhs::rna::AlignmentTrainingSampleV2;
using hhs::rna::CoreHolographicRNACellWall;
using hhs::rna::OrthogonalGlyphMembrane;
using hhs::rna::RNACellWallAlignmentTrainer;
using hhs::rna::RNACellWallContextualAlignmentTrainer;

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

static AlignmentTrainingSampleV2 build_training_sample(
    CoreHolographicRNACellWall& wall,
    const HHSExactPass219Holo4StateV1& baseline,
    AlignmentAuthorityPlaneV2 plane,
    std::uint64_t salt,
    std::uint8_t transition_offset
) {
    AlignmentTrainingSampleV2 sample{};
    sample.plane = plane;
    sample.inherited.frame = build_frame(salt);
    sample.inherited.transition = build_transition(transition_offset);
    const std::uint8_t selected = selected_lane_for(
        wall, baseline, sample.inherited.frame, sample.inherited.transition);
    if (selected >= HHS_EXACT_PASS219_HOLO4_LANE_COUNT)
        return sample;
    sample.inherited.feedback_lane = static_cast<std::uint8_t>(
        (selected + 1U) % HHS_EXACT_PASS219_HOLO4_LANE_COUNT);
    sample.inherited.feedback_trinary = 1;
    return sample;
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
    RNACellWallContextualAlignmentTrainer trainer(wall);
    CHECK(trainer.status() == HHS_EXACT_STATUS_OK);

    HHSExactPass219Holo4StateV1 baseline{};
    CHECK(hhs_exact_pass219_holo4_state_init(&baseline) == HHS_EXACT_STATUS_OK);
    const HHSExactPass219Holo4StateV1 frozen_baseline = baseline;

    std::array<AlignmentTrainingSampleV2, 4> samples{};
    samples[0] = build_training_sample(
        wall, baseline, AlignmentAuthorityPlaneV2::RELATIONAL_COGNITION,
        UINT64_C(0x1200), 13U);
    samples[1] = build_training_sample(
        wall, baseline, AlignmentAuthorityPlaneV2::NARRATIVE_EXPRESSION,
        UINT64_C(0x2300), 23U);
    samples[1].gate.narrative_modality_preserved = true;
    samples[2] = build_training_sample(
        wall, baseline, AlignmentAuthorityPlaneV2::AGENTIC_ACTION,
        UINT64_C(0x3400), 33U);
    samples[3] = build_training_sample(
        wall, baseline, AlignmentAuthorityPlaneV2::TRUTH_PROMOTION,
        UINT64_C(0x4500), 43U);

    for (const auto& sample : samples)
        CHECK(sample.inherited.feedback_lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT);

    HHSExactPass219Holo4StateV1 candidate{};
    AlignmentTrainingCycleResultV2 result{};
    CHECK(trainer.train_contextual_cycle(
              samples.data(), samples.size(), baseline, candidate, result) == HHS_EXACT_STATUS_OK);
    CHECK(result.status == HHS_EXACT_STATUS_OK);
    CHECK(result.disposition == AlignmentTrainingDispositionV1::CANDIDATE_READY);
    CHECK(result.sample_count == 4U);
    CHECK(result.admitted_training_sample_count == 2U);
    CHECK(result.held_training_sample_count == 2U);
    CHECK(result.protected_replay_sample_count == 0U);
    CHECK(result.requested_per_plane[0] == 1U);
    CHECK(result.requested_per_plane[1] == 1U);
    CHECK(result.requested_per_plane[2] == 1U);
    CHECK(result.requested_per_plane[3] == 1U);
    CHECK(result.admitted_per_plane[0] == 1U);
    CHECK(result.admitted_per_plane[1] == 1U);
    CHECK(result.admitted_per_plane[2] == 0U);
    CHECK(result.admitted_per_plane[3] == 0U);
    CHECK(result.held_per_plane[0] == 0U);
    CHECK(result.held_per_plane[1] == 0U);
    CHECK(result.held_per_plane[2] == 1U);
    CHECK(result.held_per_plane[3] == 1U);
    CHECK(result.four_plane_objectives_applied);
    CHECK(result.independent_plane_gates);
    CHECK(result.relation_type_required);
    CHECK(result.provenance_required);
    CHECK(result.narrative_modality_required);
    CHECK(result.agentic_capability_required);
    CHECK(result.agentic_validation_required);
    CHECK(result.truth_evidence_required);
    CHECK(result.truth_validator_required);
    CHECK(result.protected_replay_retained);
    CHECK(result.inherited_reverse_trainer_only);
    CHECK(result.candidate_only);
    CHECK(result.exact_integer_only);
    CHECK(!result.canonical_mutation_authority);
    CHECK(!result.canonical_hash72_authority);
    CHECK(!result.canonical_hash216_authority);
    CHECK(!result.canonical_persistence_authority);
    CHECK(!result.floating_point_authority);
    CHECK(std::memcmp(&baseline, &frozen_baseline, sizeof(baseline)) == 0);

    /* Cycle 2 must equal Cycle 1 over exactly the plane-admitted evidence. */
    std::array<AlignmentTrainingSampleV1, 2> admitted{
        samples[0].inherited,
        samples[1].inherited,
    };
    RNACellWallAlignmentTrainer inherited_manual(wall);
    HHSExactPass219Holo4StateV1 manual_candidate{};
    AlignmentTrainingCycleResultV1 manual_result{};
    CHECK(inherited_manual.train_reverse_cycle(
              admitted.data(), admitted.size(), baseline,
              manual_candidate, manual_result) == HHS_EXACT_STATUS_OK);
    CHECK(std::memcmp(&candidate, &manual_candidate, sizeof(candidate)) == 0);
    CHECK(result.inherited_cycle.training_signature64 == manual_result.training_signature64);
    CHECK(result.inherited_cycle.reverse_training_sample_count == admitted.size());

    /* Identical plane-typed evidence must replay identically. */
    HHSExactPass219Holo4StateV1 replay_candidate{};
    AlignmentTrainingCycleResultV2 replay_result{};
    CHECK(trainer.train_contextual_cycle(
              samples.data(), samples.size(), baseline,
              replay_candidate, replay_result) == HHS_EXACT_STATUS_OK);
    CHECK(std::memcmp(&candidate, &replay_candidate, sizeof(candidate)) == 0);
    CHECK(result.objective_signature64 == replay_result.objective_signature64);
    CHECK(result.inherited_cycle.training_signature64 ==
          replay_result.inherited_cycle.training_signature64);

    /* Agentic and truth planes become trainable only through their own gates. */
    auto unlocked = samples;
    unlocked[2].gate.action_capability_authorized = true;
    unlocked[2].gate.action_validation_satisfied = true;
    unlocked[3].gate.truth_evidence_satisfied = true;
    unlocked[3].gate.truth_validator_satisfied = true;
    HHSExactPass219Holo4StateV1 unlocked_candidate{};
    AlignmentTrainingCycleResultV2 unlocked_result{};
    CHECK(trainer.train_contextual_cycle(
              unlocked.data(), unlocked.size(), baseline,
              unlocked_candidate, unlocked_result) == HHS_EXACT_STATUS_OK);
    CHECK(unlocked_result.admitted_training_sample_count == 4U);
    CHECK(unlocked_result.held_training_sample_count == 0U);
    CHECK(unlocked_result.admitted_per_plane[2] == 1U);
    CHECK(unlocked_result.admitted_per_plane[3] == 1U);
    CHECK(unlocked_result.inherited_cycle.reverse_training_sample_count == 4U);

    /* The same underlying relation can cross some planes while other planes hold it. */
    std::array<AlignmentTrainingSampleV2, 4> shared{};
    for (std::size_t i = 0U; i < shared.size(); ++i) {
        shared[i] = samples[0];
        shared[i].plane = static_cast<AlignmentAuthorityPlaneV2>(i);
    }
    shared[1].gate.narrative_modality_preserved = true;
    HHSExactPass219Holo4StateV1 shared_candidate{};
    AlignmentTrainingCycleResultV2 shared_result{};
    CHECK(trainer.train_contextual_cycle(
              shared.data(), shared.size(), baseline,
              shared_candidate, shared_result) == HHS_EXACT_STATUS_OK);
    CHECK(shared_result.admitted_per_plane[0] == 1U);
    CHECK(shared_result.admitted_per_plane[1] == 1U);
    CHECK(shared_result.held_per_plane[2] == 1U);
    CHECK(shared_result.held_per_plane[3] == 1U);

    /* A narrative objective with broken modality is held without mutating baseline. */
    AlignmentTrainingSampleV2 held = samples[1];
    held.gate.narrative_modality_preserved = false;
    HHSExactPass219Holo4StateV1 held_candidate{};
    AlignmentTrainingCycleResultV2 held_result{};
    CHECK(trainer.train_contextual_cycle(
              &held, 1U, baseline, held_candidate, held_result) == HHS_EXACT_STATUS_OK);
    CHECK(held_result.disposition == AlignmentTrainingDispositionV1::NO_UPDATE_REQUIRED);
    CHECK(held_result.admitted_training_sample_count == 0U);
    CHECK(held_result.held_training_sample_count == 1U);
    CHECK(held_result.held_per_plane[1] == 1U);
    CHECK(held_result.objective_signature64 != 0U);
    CHECK(std::memcmp(&held_candidate, &baseline, sizeof(baseline)) == 0);

    /* Protected history remains in anti-forgetting replay even when current gates hold training. */
    AlignmentTrainingSampleV2 protected_sample = samples[3];
    protected_sample.inherited.protected_replay = true;
    protected_sample.gate.relation_type_preserved = false;
    protected_sample.gate.provenance_preserved = false;
    HHSExactPass219Holo4StateV1 protected_candidate{};
    AlignmentTrainingCycleResultV2 protected_result{};
    CHECK(trainer.train_contextual_cycle(
              &protected_sample, 1U, baseline,
              protected_candidate, protected_result) == HHS_EXACT_STATUS_OK);
    CHECK(protected_result.protected_replay_sample_count == 1U);
    CHECK(protected_result.admitted_training_sample_count == 0U);
    CHECK(protected_result.held_training_sample_count == 0U);
    CHECK(protected_result.inherited_cycle.protected_replay_count == 1U);
    CHECK(protected_result.inherited_cycle.anti_forgetting_passed);
    CHECK(std::memcmp(&protected_candidate, &baseline, sizeof(baseline)) == 0);

    /* Unknown plane values fail closed before training. */
    AlignmentTrainingSampleV2 invalid = samples[0];
    invalid.plane = static_cast<AlignmentAuthorityPlaneV2>(9U);
    HHSExactPass219Holo4StateV1 invalid_candidate{};
    AlignmentTrainingCycleResultV2 invalid_result{};
    CHECK(trainer.train_contextual_cycle(
              &invalid, 1U, baseline,
              invalid_candidate, invalid_result) == HHS_EXACT_STATUS_RANGE_ERROR);
    CHECK(invalid_result.disposition == AlignmentTrainingDispositionV1::INVALID_SAMPLE);
    CHECK(std::memcmp(&invalid_candidate, &baseline, sizeof(baseline)) == 0);

    return 0;
}

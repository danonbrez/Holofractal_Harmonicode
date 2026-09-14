#ifndef HHS_PASS219_RNA_CELL_WALL_ALIGNMENT_TRAINING_1_25_HPP
#define HHS_PASS219_RNA_CELL_WALL_ALIGNMENT_TRAINING_1_25_HPP

#include "hhs_pass219_core_holographic_rna_cell_wall_1_24.hpp"

#include <cstddef>
#include <cstdint>
#include <cstring>

namespace hhs::rna {

/*
 * Pass 219 RNA cell-wall alignment training cycle v1.
 *
 * This layer is deliberately subordinate to the existing four-lane learner and
 * VM81 singleton authority.  It performs bounded reverse-order candidate
 * training, records the dependency frontier actually changed by the inherited
 * learner, and rejects any candidate that changes a protected historical
 * replay decision.
 *
 * It does not mint Hash72/Hash216, persist canonical state, or establish a
 * second transition authority.
 */

static constexpr std::size_t HHS_PASS219_RNA_ALIGNMENT_MAX_SAMPLES = 64U;

enum class AlignmentTrainingDispositionV1 : std::uint8_t {
    NO_UPDATE_REQUIRED = 0U,
    CANDIDATE_READY = 1U,
    REJECT_PROTECTED_REPLAY = 2U,
    INVALID_SAMPLE = 3U
};

struct AlignmentTrainingSampleV1 final {
    HHSExactVM81Frame frame{};
    HHSExactPass219Hash216TransitionViewV1 transition{};
    std::uint8_t feedback_lane{HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE};
    std::int8_t feedback_trinary{0};
    bool protected_replay{false};
};

struct AlignmentTrainingCycleResultV1 final {
    HHSExactStatus status{HHS_EXACT_STATUS_INVALID_ARGUMENT};
    AlignmentTrainingDispositionV1 disposition{AlignmentTrainingDispositionV1::INVALID_SAMPLE};
    std::uint32_t sample_count{};
    std::uint32_t reverse_training_sample_count{};
    std::uint32_t protected_replay_count{};
    std::uint32_t update_event_count{};
    std::uint32_t changed_core_weight_count{};
    std::uint32_t changed_cell_weight_count{};
    std::uint32_t changed_bank_weight_count{};
    std::uint32_t changed_lane_bias_count{};
    std::uint32_t protected_replay_failure_count{};
    std::uint64_t baseline_step_count{};
    std::uint64_t candidate_step_count{};
    std::uint32_t baseline_update_count{};
    std::uint32_t candidate_update_count{};
    std::uint64_t training_signature64{};
    bool reverse_order_applied{false};
    bool bounded_backward_credit{false};
    bool dependency_scoped_delta_observed{false};
    bool anti_forgetting_passed{false};
    bool candidate_only{true};
    bool exact_integer_only{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
    char last_transition_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN]{};
};

class RNACellWallAlignmentTrainer final {
public:
    explicit RNACellWallAlignmentTrainer(CoreHolographicRNACellWall& wall) noexcept
        : wall_(wall) {}

    HHSExactStatus status() const noexcept {
        return wall_.status();
    }

    CoreHolographicRNACellWall& wall() noexcept {
        return wall_;
    }

    const CoreHolographicRNACellWall& wall() const noexcept {
        return wall_;
    }

    HHSExactStatus train_reverse_cycle(
        const AlignmentTrainingSampleV1* samples,
        std::size_t sample_count,
        const HHSExactPass219Holo4StateV1& baseline_state,
        HHSExactPass219Holo4StateV1& out_candidate_state,
        AlignmentTrainingCycleResultV1& out_result
    ) {
        out_result = AlignmentTrainingCycleResultV1{};
        out_candidate_state = baseline_state;

        if (wall_.status() != HHS_EXACT_STATUS_OK) {
            out_result.status = wall_.status();
            return out_result.status;
        }
        if (samples == nullptr || sample_count == 0U ||
            sample_count > HHS_PASS219_RNA_ALIGNMENT_MAX_SAMPLES) {
            out_result.status = HHS_EXACT_STATUS_INVALID_ARGUMENT;
            return out_result.status;
        }

        HHSExactStatus status = hhs_exact_pass219_holo4_validate_state(&baseline_state);
        if (status != HHS_EXACT_STATUS_OK) {
            out_result.status = status;
            return status;
        }

        out_result.sample_count = static_cast<std::uint32_t>(sample_count);
        out_result.baseline_step_count = baseline_state.step_count;
        out_result.baseline_update_count = baseline_state.update_count;
        out_result.reverse_order_applied = true;
        out_result.bounded_backward_credit = true;

        HHSExactPass219Holo4StateV1 candidate = baseline_state;
        std::uint64_t signature = UINT64_C(0x2190125000000001);

        /*
         * Training evidence is traversed newest-to-oldest.  Protected replay
         * samples are excluded from weight mutation and are evaluated only by
         * the anti-forgetting gate below.
         */
        for (std::size_t remaining = sample_count; remaining > 0U; --remaining) {
            const std::size_t index = remaining - 1U;
            const AlignmentTrainingSampleV1& sample = samples[index];
            if (sample.protected_replay) {
                ++out_result.protected_replay_count;
                continue;
            }
            ++out_result.reverse_training_sample_count;

            if (!feedback_valid(sample.feedback_lane, sample.feedback_trinary)) {
                out_candidate_state = baseline_state;
                out_result.status = HHS_EXACT_STATUS_RANGE_ERROR;
                out_result.disposition = AlignmentTrainingDispositionV1::INVALID_SAMPLE;
                return out_result.status;
            }

            const HHSExactPass219Holo4StateV1 before = candidate;
            HHSExactPass219Holo4PreparedV1 prepared{};
            HHSExactPass219Holo4DecisionV1 decision{};
            status = wall_.route_parallel(
                sample.frame,
                sample.transition,
                sample.feedback_lane,
                sample.feedback_trinary,
                candidate,
                prepared,
                decision);
            if (status != HHS_EXACT_STATUS_OK) {
                out_candidate_state = baseline_state;
                out_result.status = status;
                out_result.disposition = AlignmentTrainingDispositionV1::INVALID_SAMPLE;
                return status;
            }

            if (decision.updated != 0U)
                ++out_result.update_event_count;
            count_dependency_deltas(before, candidate, out_result);

            signature = fold_signature(signature, decision.decision_signature64);
            signature = fold_signature(signature, prepared.graph_signature64);
            signature = fold_signature(signature, prepared.tensor_signature64);
            signature = fold_signature(signature, static_cast<std::uint64_t>(index));
            signature = fold_signature(signature, static_cast<std::uint64_t>(decision.updated));
            std::memcpy(
                out_result.last_transition_identity216,
                decision.source_transition_identity216,
                HHS_EXACT_UQCEL_HASH216_STRLEN);
        }

        out_result.dependency_scoped_delta_observed =
            out_result.changed_core_weight_count != 0U ||
            out_result.changed_cell_weight_count != 0U ||
            out_result.changed_bank_weight_count != 0U ||
            out_result.changed_lane_bias_count != 0U;

        /*
         * Protected historical replay is evaluated against both the frozen
         * baseline and the proposed candidate.  Replays use private state
         * copies so the comparison itself cannot train either state.
         */
        for (std::size_t index = 0U; index < sample_count; ++index) {
            const AlignmentTrainingSampleV1& sample = samples[index];
            if (!sample.protected_replay)
                continue;

            ProtectedOutcome baseline_outcome{};
            ProtectedOutcome candidate_outcome{};
            status = protected_outcome(sample, baseline_state, baseline_outcome);
            if (status != HHS_EXACT_STATUS_OK) {
                out_candidate_state = baseline_state;
                out_result.status = status;
                out_result.disposition = AlignmentTrainingDispositionV1::INVALID_SAMPLE;
                return status;
            }
            status = protected_outcome(sample, candidate, candidate_outcome);
            if (status != HHS_EXACT_STATUS_OK) {
                out_candidate_state = baseline_state;
                out_result.status = status;
                out_result.disposition = AlignmentTrainingDispositionV1::INVALID_SAMPLE;
                return status;
            }

            signature = fold_signature(signature, baseline_outcome.signature64);
            signature = fold_signature(signature, candidate_outcome.signature64);
            if (!same_protected_outcome(baseline_outcome, candidate_outcome))
                ++out_result.protected_replay_failure_count;
        }

        out_result.training_signature64 = signature;
        out_result.candidate_step_count = candidate.step_count;
        out_result.candidate_update_count = candidate.update_count;
        out_result.anti_forgetting_passed = out_result.protected_replay_failure_count == 0U;

        if (!out_result.anti_forgetting_passed) {
            out_candidate_state = baseline_state;
            out_result.disposition = AlignmentTrainingDispositionV1::REJECT_PROTECTED_REPLAY;
            out_result.status = HHS_EXACT_STATUS_OK;
            return HHS_EXACT_STATUS_OK;
        }

        status = hhs_exact_pass219_holo4_validate_state(&candidate);
        if (status != HHS_EXACT_STATUS_OK) {
            out_candidate_state = baseline_state;
            out_result.status = status;
            return status;
        }

        out_candidate_state = candidate;
        out_result.disposition = out_result.update_event_count == 0U
            ? AlignmentTrainingDispositionV1::NO_UPDATE_REQUIRED
            : AlignmentTrainingDispositionV1::CANDIDATE_READY;
        out_result.status = HHS_EXACT_STATUS_OK;
        return HHS_EXACT_STATUS_OK;
    }

private:
    struct ProtectedOutcome final {
        std::uint8_t selected_lane{};
        std::int8_t prediction_trinary{};
        std::uint64_t signature64{};
        char transition_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN]{};
    };

    static bool feedback_valid(std::uint8_t lane, std::int8_t trinary) noexcept {
        if (trinary < -1 || trinary > 1)
            return false;
        if (lane == HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE)
            return trinary == 0;
        return lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT;
    }

    static std::uint64_t mix64(std::uint64_t value) noexcept {
        value ^= value >> 30U;
        value *= UINT64_C(0xbf58476d1ce4e5b9);
        value ^= value >> 27U;
        value *= UINT64_C(0x94d049bb133111eb);
        value ^= value >> 31U;
        return value;
    }

    static std::uint64_t fold_signature(std::uint64_t acc, std::uint64_t value) noexcept {
        return mix64(acc ^ mix64(value + UINT64_C(0x9e3779b97f4a7c15)));
    }

    static void count_dependency_deltas(
        const HHSExactPass219Holo4StateV1& before,
        const HHSExactPass219Holo4StateV1& after,
        AlignmentTrainingCycleResultV1& result
    ) noexcept {
        for (std::size_t i = 0U; i < HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_COUNT; ++i) {
            if (before.core.weights[i] != after.core.weights[i])
                ++result.changed_core_weight_count;
        }
        if (before.core.bias != after.core.bias)
            ++result.changed_core_weight_count;

        for (std::size_t lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane) {
            if (before.lane_bias[lane] != after.lane_bias[lane])
                ++result.changed_lane_bias_count;
            for (std::size_t cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_CELL_COUNT; ++cell) {
                if (before.cell_lane_weights[lane][cell] != after.cell_lane_weights[lane][cell])
                    ++result.changed_cell_weight_count;
            }
            for (std::size_t bank = 0U; bank < HHS_EXACT_PASS219_HOLO4_BANK_COUNT; ++bank) {
                if (before.bank_lane_weights[lane][bank] != after.bank_lane_weights[lane][bank])
                    ++result.changed_bank_weight_count;
            }
        }
    }

    HHSExactStatus protected_outcome(
        const AlignmentTrainingSampleV1& sample,
        const HHSExactPass219Holo4StateV1& source_state,
        ProtectedOutcome& out
    ) {
        HHSExactPass219Holo4StateV1 replay_state = source_state;
        HHSExactPass219Holo4PreparedV1 prepared{};
        HHSExactPass219Holo4DecisionV1 decision{};
        const HHSExactStatus status = wall_.route_parallel(
            sample.frame,
            sample.transition,
            HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
            0,
            replay_state,
            prepared,
            decision);
        if (status != HHS_EXACT_STATUS_OK)
            return status;

        out.selected_lane = decision.selected_lane;
        out.prediction_trinary = prepared.core_decision.prediction_trinary;
        out.signature64 = fold_signature(
            decision.decision_signature64,
            fold_signature(prepared.graph_signature64, prepared.tensor_signature64));
        std::memcpy(
            out.transition_identity216,
            decision.source_transition_identity216,
            HHS_EXACT_UQCEL_HASH216_STRLEN);
        return HHS_EXACT_STATUS_OK;
    }

    static bool same_protected_outcome(
        const ProtectedOutcome& a,
        const ProtectedOutcome& b
    ) noexcept {
        return a.selected_lane == b.selected_lane &&
               a.prediction_trinary == b.prediction_trinary &&
               std::memcmp(
                   a.transition_identity216,
                   b.transition_identity216,
                   HHS_EXACT_UQCEL_HASH216_STRLEN) == 0;
    }

    CoreHolographicRNACellWall& wall_;
};

}  // namespace hhs::rna

#endif

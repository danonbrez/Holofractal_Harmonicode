#ifndef HHS_PASS219_RNA_CELL_WALL_ALIGNMENT_TRAINING_1_26_HPP
#define HHS_PASS219_RNA_CELL_WALL_ALIGNMENT_TRAINING_1_26_HPP

#include "hhs_pass219_rna_cell_wall_alignment_training_1_25.hpp"

#include <array>
#include <cstddef>
#include <cstdint>

namespace hhs::rna {

/*
 * Pass 219 RNA cell-wall alignment training cycle v2.
 *
 * Cycle 2 does not introduce another learner. It types each training objective
 * onto one of the four inherited Pass 218/219 authority planes, applies an
 * exact plane-local gate, and then delegates every admitted weight update to
 * the already validated Cycle 1 reverse trainer / inherited four-lane learner.
 *
 * Protected replay evidence is always retained for anti-forgetting comparison
 * even when its current plane gate would hold new training. Plane permission
 * never grants canonical VM81, Hash72, Hash216, persistence, or floating-point
 * authority.
 */

static constexpr std::size_t HHS_PASS219_RNA_ALIGNMENT_PLANE_COUNT = 4U;

enum class AlignmentAuthorityPlaneV2 : std::uint8_t {
    RELATIONAL_COGNITION = 0U,
    NARRATIVE_EXPRESSION = 1U,
    AGENTIC_ACTION = 2U,
    TRUTH_PROMOTION = 3U
};

struct AlignmentPlaneGateV2 final {
    bool relation_type_preserved{true};
    bool provenance_preserved{true};
    bool narrative_modality_preserved{false};
    bool action_capability_authorized{false};
    bool action_validation_satisfied{false};
    bool truth_evidence_satisfied{false};
    bool truth_validator_satisfied{false};
};

struct AlignmentTrainingSampleV2 final {
    AlignmentTrainingSampleV1 inherited{};
    AlignmentAuthorityPlaneV2 plane{AlignmentAuthorityPlaneV2::RELATIONAL_COGNITION};
    AlignmentPlaneGateV2 gate{};
};

struct AlignmentTrainingCycleResultV2 final {
    HHSExactStatus status{HHS_EXACT_STATUS_INVALID_ARGUMENT};
    AlignmentTrainingDispositionV1 disposition{AlignmentTrainingDispositionV1::INVALID_SAMPLE};
    std::uint32_t sample_count{};
    std::uint32_t admitted_training_sample_count{};
    std::uint32_t held_training_sample_count{};
    std::uint32_t protected_replay_sample_count{};
    std::array<std::uint32_t, HHS_PASS219_RNA_ALIGNMENT_PLANE_COUNT> requested_per_plane{};
    std::array<std::uint32_t, HHS_PASS219_RNA_ALIGNMENT_PLANE_COUNT> admitted_per_plane{};
    std::array<std::uint32_t, HHS_PASS219_RNA_ALIGNMENT_PLANE_COUNT> held_per_plane{};
    AlignmentTrainingCycleResultV1 inherited_cycle{};
    std::uint64_t objective_signature64{};
    bool four_plane_objectives_applied{true};
    bool independent_plane_gates{true};
    bool relation_type_required{true};
    bool provenance_required{true};
    bool narrative_modality_required{true};
    bool agentic_capability_required{true};
    bool agentic_validation_required{true};
    bool truth_evidence_required{true};
    bool truth_validator_required{true};
    bool protected_replay_retained{true};
    bool inherited_reverse_trainer_only{true};
    bool candidate_only{true};
    bool exact_integer_only{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
};

class RNACellWallContextualAlignmentTrainer final {
public:
    explicit RNACellWallContextualAlignmentTrainer(CoreHolographicRNACellWall& wall) noexcept
        : inherited_(wall) {}

    HHSExactStatus status() const noexcept {
        return inherited_.status();
    }

    RNACellWallAlignmentTrainer& inherited_trainer() noexcept {
        return inherited_;
    }

    const RNACellWallAlignmentTrainer& inherited_trainer() const noexcept {
        return inherited_;
    }

    HHSExactStatus train_contextual_cycle(
        const AlignmentTrainingSampleV2* samples,
        std::size_t sample_count,
        const HHSExactPass219Holo4StateV1& baseline_state,
        HHSExactPass219Holo4StateV1& out_candidate_state,
        AlignmentTrainingCycleResultV2& out_result
    ) {
        out_result = AlignmentTrainingCycleResultV2{};
        out_candidate_state = baseline_state;

        if (inherited_.status() != HHS_EXACT_STATUS_OK) {
            out_result.status = inherited_.status();
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
        std::array<AlignmentTrainingSampleV1, HHS_PASS219_RNA_ALIGNMENT_MAX_SAMPLES> selected{};
        std::size_t selected_count = 0U;
        std::uint64_t signature = UINT64_C(0x2190126000000002);

        for (std::size_t index = 0U; index < sample_count; ++index) {
            const AlignmentTrainingSampleV2& sample = samples[index];
            std::size_t plane_index_value = 0U;
            if (!plane_index(sample.plane, plane_index_value)) {
                out_candidate_state = baseline_state;
                out_result.status = HHS_EXACT_STATUS_RANGE_ERROR;
                out_result.disposition = AlignmentTrainingDispositionV1::INVALID_SAMPLE;
                return out_result.status;
            }

            ++out_result.requested_per_plane[plane_index_value];
            signature = fold_signature(signature, static_cast<std::uint64_t>(index));
            signature = fold_signature(signature, static_cast<std::uint64_t>(plane_index_value));
            signature = fold_signature(signature, gate_bits(sample.gate));
            signature = fold_signature(
                signature,
                static_cast<std::uint64_t>(sample.inherited.feedback_lane));
            signature = fold_signature(
                signature,
                static_cast<std::uint64_t>(
                    static_cast<std::uint8_t>(sample.inherited.feedback_trinary + 1)));
            signature = fold_signature(
                signature,
                static_cast<std::uint64_t>(sample.inherited.protected_replay ? 1U : 0U));
            signature = fold_identity(
                signature,
                sample.inherited.transition.transition_identity216);

            if (sample.inherited.protected_replay) {
                selected[selected_count++] = sample.inherited;
                ++out_result.protected_replay_sample_count;
                continue;
            }

            if (gate_allows(sample.plane, sample.gate)) {
                selected[selected_count++] = sample.inherited;
                ++out_result.admitted_training_sample_count;
                ++out_result.admitted_per_plane[plane_index_value];
            } else {
                ++out_result.held_training_sample_count;
                ++out_result.held_per_plane[plane_index_value];
            }
        }

        if (selected_count == 0U) {
            out_result.inherited_cycle.status = HHS_EXACT_STATUS_OK;
            out_result.inherited_cycle.disposition = AlignmentTrainingDispositionV1::NO_UPDATE_REQUIRED;
            out_result.inherited_cycle.anti_forgetting_passed = true;
            out_result.disposition = AlignmentTrainingDispositionV1::NO_UPDATE_REQUIRED;
            out_result.objective_signature64 = fold_signature(signature, UINT64_C(0));
            out_result.status = HHS_EXACT_STATUS_OK;
            return HHS_EXACT_STATUS_OK;
        }

        status = inherited_.train_reverse_cycle(
            selected.data(),
            selected_count,
            baseline_state,
            out_candidate_state,
            out_result.inherited_cycle);
        if (status != HHS_EXACT_STATUS_OK) {
            out_candidate_state = baseline_state;
            out_result.status = status;
            out_result.disposition = out_result.inherited_cycle.disposition;
            return status;
        }

        out_result.disposition = out_result.inherited_cycle.disposition;
        signature = fold_signature(signature, out_result.inherited_cycle.training_signature64);
        signature = fold_signature(
            signature,
            static_cast<std::uint64_t>(out_result.admitted_training_sample_count));
        signature = fold_signature(
            signature,
            static_cast<std::uint64_t>(out_result.held_training_sample_count));
        signature = fold_signature(
            signature,
            static_cast<std::uint64_t>(out_result.protected_replay_sample_count));
        out_result.objective_signature64 = signature;
        out_result.status = HHS_EXACT_STATUS_OK;
        return HHS_EXACT_STATUS_OK;
    }

private:
    static bool plane_index(
        AlignmentAuthorityPlaneV2 plane,
        std::size_t& out_index
    ) noexcept {
        const std::uint8_t raw = static_cast<std::uint8_t>(plane);
        if (raw >= HHS_PASS219_RNA_ALIGNMENT_PLANE_COUNT)
            return false;
        out_index = static_cast<std::size_t>(raw);
        return true;
    }

    static bool gate_allows(
        AlignmentAuthorityPlaneV2 plane,
        const AlignmentPlaneGateV2& gate
    ) noexcept {
        if (!gate.relation_type_preserved || !gate.provenance_preserved)
            return false;

        switch (plane) {
        case AlignmentAuthorityPlaneV2::RELATIONAL_COGNITION:
            return true;
        case AlignmentAuthorityPlaneV2::NARRATIVE_EXPRESSION:
            return gate.narrative_modality_preserved;
        case AlignmentAuthorityPlaneV2::AGENTIC_ACTION:
            return gate.action_capability_authorized &&
                   gate.action_validation_satisfied;
        case AlignmentAuthorityPlaneV2::TRUTH_PROMOTION:
            return gate.truth_evidence_satisfied &&
                   gate.truth_validator_satisfied;
        }
        return false;
    }

    static std::uint64_t gate_bits(const AlignmentPlaneGateV2& gate) noexcept {
        std::uint64_t bits = 0U;
        bits |= static_cast<std::uint64_t>(gate.relation_type_preserved ? 1U : 0U) << 0U;
        bits |= static_cast<std::uint64_t>(gate.provenance_preserved ? 1U : 0U) << 1U;
        bits |= static_cast<std::uint64_t>(gate.narrative_modality_preserved ? 1U : 0U) << 2U;
        bits |= static_cast<std::uint64_t>(gate.action_capability_authorized ? 1U : 0U) << 3U;
        bits |= static_cast<std::uint64_t>(gate.action_validation_satisfied ? 1U : 0U) << 4U;
        bits |= static_cast<std::uint64_t>(gate.truth_evidence_satisfied ? 1U : 0U) << 5U;
        bits |= static_cast<std::uint64_t>(gate.truth_validator_satisfied ? 1U : 0U) << 6U;
        return bits;
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

    static std::uint64_t fold_identity(
        std::uint64_t acc,
        const char identity[HHS_EXACT_UQCEL_HASH216_STRLEN]
    ) noexcept {
        for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i)
            acc = fold_signature(acc, static_cast<std::uint8_t>(identity[i]));
        return acc;
    }

    RNACellWallAlignmentTrainer inherited_;
};

}  // namespace hhs::rna

#endif

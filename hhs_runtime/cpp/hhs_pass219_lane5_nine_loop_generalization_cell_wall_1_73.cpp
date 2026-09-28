#include "hhs_pass219_lane5_nine_loop_generalization_cell_wall_1_73.hpp"

#include <cstddef>
#include <cinttypes>
#include <cstdio>
#include <cstring>

namespace hhs::lane5 {
namespace {

constexpr char kModelRootHash72[] =
    "0000000000000000000000000000002rd>Jdh(*jXM9IMuM^931?)TxIUlEV>A5MH81cDfqL";
constexpr char kValidationRootHash72[] =
    "0000000000000000000000000000004uxkwBpAEdc+=PCnAuM+5cGH26usFYmSWD3kSLSkPM";
constexpr char kReplayBundleSha256[] =
    "238556f95e17e77d01a9e37e4be4cbbd56181982f3599dc941cfe77be32aaf69";

bool hash216_text_valid(const char value[HHS_HASH216_LEN + 1]) noexcept {
    if (value == nullptr || value[HHS_HASH216_LEN] != '\0')
        return false;
    for (std::size_t i = 0U; i < HHS_HASH216_LEN; ++i) {
        if (value[i] == '\0')
            return false;
    }
    return true;
}

template <std::size_t N>
bool exact_text(const char (&value)[N], const char (&expected)[N]) noexcept {
    return std::memcmp(value, expected, N) == 0;
}

bool exact_generalization_witness(
    const NineLoopGeneralizationInput& input
) noexcept {
    return exact_text(input.model_root_hash72, kModelRootHash72) &&
           exact_text(
               input.validation_receipt_root_hash72,
               kValidationRootHash72
           ) &&
           exact_text(input.replay_bundle_sha256, kReplayBundleSha256) &&
           input.training_example_count == kNineLoopGeneralizationExampleCount &&
           input.holdout_example_count == kNineLoopGeneralizationExampleCount &&
           input.rule_count == kNineLoopGeneralizationExampleCount &&
           input.accuracy_numerator == kNineLoopGeneralizationExampleCount &&
           input.accuracy_denominator == kNineLoopGeneralizationExampleCount &&
           input.semantic_drift_count == 0U &&
           input.entropy_growth_bits == 0U &&
           input.replay_count == kNineLoopGeneralizationExampleCount &&
           input.training_holdout_disjoint == 1U &&
           input.all_replays_validated == 1U &&
           input.validated_knowledge_model_only == 1U &&
           input.model_weight_update_requested == 0U &&
           input.learning_commit_requested == 0U &&
           input.execution_authority_requested == 0U;
}

}  // namespace

HHSExactStatus NineLoopGeneralizationCellWall::derive_candidate_hash216(
    const NineLoopGeneralizationInput& input,
    char out_hash216[HHS_HASH216_LEN + 1]
) noexcept {
    if (out_hash216 == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hash216_text_valid(input.parent_relation_dataset_hash216) ||
        !exact_generalization_witness(input))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    char material[1200]{};
    const int written = std::snprintf(
        material,
        sizeof(material),
        "HHS-P219-LANE5-NINE-LOOP-1.73|"
        "parent=%s|model=%s|validation=%s|replay=%s|"
        "train=%" PRIu32 "|holdout=%" PRIu32 "|rules=%" PRIu32
        "|accuracy=%" PRIu32 "/%" PRIu32 "|drift=%" PRIu32
        "|entropy=%" PRIu32 "|replays=%" PRIu32
        "|disjoint=%u|replayValid=%u|validatedModelOnly=%u|"
        "weightRequest=%u|learningRequest=%u|executionRequest=%u",
        input.parent_relation_dataset_hash216,
        input.model_root_hash72,
        input.validation_receipt_root_hash72,
        input.replay_bundle_sha256,
        input.training_example_count,
        input.holdout_example_count,
        input.rule_count,
        input.accuracy_numerator,
        input.accuracy_denominator,
        input.semantic_drift_count,
        input.entropy_growth_bits,
        input.replay_count,
        static_cast<unsigned>(input.training_holdout_disjoint),
        static_cast<unsigned>(input.all_replays_validated),
        static_cast<unsigned>(input.validated_knowledge_model_only),
        static_cast<unsigned>(input.model_weight_update_requested),
        static_cast<unsigned>(input.learning_commit_requested),
        static_cast<unsigned>(input.execution_authority_requested)
    );
    if (written <= 0 || static_cast<std::size_t>(written) >= sizeof(material))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    HHSHash216 hash{};
    hhs_hash216_compute(material, static_cast<std::size_t>(written), &hash);
    std::memcpy(out_hash216, hash.value, HHS_HASH216_LEN + 1U);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus NineLoopGeneralizationCellWall::evaluate(
    const NineLoopGeneralizationInput& input,
    const char expected_hash216[HHS_HASH216_LEN + 1],
    NineLoopGeneralizationReceipt& out
) const noexcept {
    out = NineLoopGeneralizationReceipt{};
    out.version = kNineLoopGeneralizationVersion;
    out.namespace_id = kNineLoopGeneralizationNamespace;
    out.candidate_only = 1U;

    NineLoopRelationDatasetCellWall parent_wall;
    NineLoopRelationDatasetReceipt parent_receipt{};
    HHSExactStatus status = parent_wall.evaluate(
        input.parent_input,
        input.parent_relation_dataset_hash216,
        parent_receipt
    );
    if (status != HHS_EXACT_STATUS_OK ||
        parent_receipt.accepted != 1U ||
        parent_receipt.candidate_only != 1U ||
        parent_receipt.model_weight_update_authority != 0U ||
        parent_receipt.learning_commit_authority != 0U ||
        parent_receipt.canonical_vm81_mutation_authority != 0U ||
        parent_receipt.canonical_hash72_authority != 0U ||
        parent_receipt.canonical_hash216_authority != 0U ||
        parent_receipt.canonical_persistence_authority != 0U ||
        parent_receipt.floating_point_canonical_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.parent_1_72_verified = 1U;
    std::memcpy(
        out.parent_hash216,
        parent_receipt.relation_dataset_candidate_hash216,
        HHS_HASH216_LEN + 1U
    );

    if (!exact_generalization_witness(input))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.frozen_receipts_verified = 1U;
    out.exact_holdout_verified = 1U;
    out.semantic_drift_zero_verified = 1U;
    out.deterministic_replay_verified = 1U;
    out.validated_knowledge_model_only = 1U;

    status = derive_candidate_hash216(
        input,
        out.generalization_candidate_hash216
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!hash216_text_valid(expected_hash216) ||
        std::memcmp(
            expected_hash216,
            out.generalization_candidate_hash216,
            HHS_HASH216_LEN + 1U
        ) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.hash216_replay_verified = 1U;
    out.accepted = 1U;
    return HHS_EXACT_STATUS_OK;
}

}  // namespace hhs::lane5

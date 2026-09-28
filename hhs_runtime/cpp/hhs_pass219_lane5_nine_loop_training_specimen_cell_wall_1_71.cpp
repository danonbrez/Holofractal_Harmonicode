#include "hhs_pass219_lane5_nine_loop_training_specimen_cell_wall_1_71.hpp"

#include <cstddef>
#include <cinttypes>
#include <cstdio>
#include <cstring>

namespace hhs::lane5 {
namespace {

constexpr char kTrainingSpecimenSha256[] =
    "96a9f686a1ab35c8600ba7a38a367af38339b51a70182c3d7981ee529ff50191";
constexpr char kParentFeedbackPayloadSha256[] =
    "78f2cc37e9304017cf0b6a233f2cb5ab080757fec57e6eb5897295bf0d2bed70";
constexpr char kParentRelationSha256[] =
    "4acc66c250129d5a42f976d673027313707633012b2de6f85d6491a4083ed73a";
constexpr char kParentSupportSha256[] =
    "64cd7ae9027ef41969948efc35b1273ba03ba3f759c076700d8a09940ebbf54d";

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

bool exact_specimen_witness(const NineLoopTrainingSpecimenInput& input) noexcept {
    return exact_text(input.training_specimen_sha256, kTrainingSpecimenSha256) &&
           exact_text(
               input.parent_feedback_payload_sha256,
               kParentFeedbackPayloadSha256
           ) &&
           exact_text(input.parent_relation_sha256, kParentRelationSha256) &&
           exact_text(input.parent_support_sha256, kParentSupportSha256) &&
           input.training_feedback_label_count == UINT32_C(13) &&
           input.learning_objective_count == UINT32_C(5) &&
           input.deviation_feature_count == UINT32_C(16) &&
           input.source_lineage_verified == 1U &&
           input.negative_example_preserved == 1U &&
           input.exact_ratio_features_verified == 1U &&
           input.trinary_features_verified == 1U &&
           input.dataset_preparation_only == 1U &&
           input.model_weight_update_requested == 0U &&
           input.learning_commit_requested == 0U;
}

}  // namespace

HHSExactStatus NineLoopTrainingSpecimenCellWall::derive_candidate_hash216(
    const NineLoopTrainingSpecimenInput& input,
    char out_hash216[HHS_HASH216_LEN + 1]
) noexcept {
    if (out_hash216 == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hash216_text_valid(input.parent_feedback_hash216) ||
        !exact_specimen_witness(input))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    char material[1100]{};
    const int written = std::snprintf(
        material,
        sizeof(material),
        "HHS-P219-LANE5-NINE-LOOP-1.71|"
        "parent=%s|specimen=%s|feedback=%s|relation=%s|support=%s|"
        "labels=%" PRIu32 "|objectives=%" PRIu32 "|deviation=%" PRIu32
        "|lineage=%u|negative=%u|ratios=%u|trinary=%u|datasetOnly=%u|"
        "weightRequest=%u|learningCommitRequest=%u",
        input.parent_feedback_hash216,
        input.training_specimen_sha256,
        input.parent_feedback_payload_sha256,
        input.parent_relation_sha256,
        input.parent_support_sha256,
        input.training_feedback_label_count,
        input.learning_objective_count,
        input.deviation_feature_count,
        static_cast<unsigned>(input.source_lineage_verified),
        static_cast<unsigned>(input.negative_example_preserved),
        static_cast<unsigned>(input.exact_ratio_features_verified),
        static_cast<unsigned>(input.trinary_features_verified),
        static_cast<unsigned>(input.dataset_preparation_only),
        static_cast<unsigned>(input.model_weight_update_requested),
        static_cast<unsigned>(input.learning_commit_requested)
    );
    if (written <= 0 || static_cast<std::size_t>(written) >= sizeof(material))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    HHSHash216 hash{};
    hhs_hash216_compute(material, static_cast<std::size_t>(written), &hash);
    std::memcpy(out_hash216, hash.value, HHS_HASH216_LEN + 1U);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus NineLoopTrainingSpecimenCellWall::evaluate(
    const NineLoopTrainingSpecimenInput& input,
    const char expected_hash216[HHS_HASH216_LEN + 1],
    NineLoopTrainingSpecimenReceipt& out
) const noexcept {
    out = NineLoopTrainingSpecimenReceipt{};
    out.version = kNineLoopTrainingSpecimenVersion;
    out.namespace_id = kNineLoopTrainingSpecimenNamespace;
    out.candidate_only = 1U;

    NineLoopFeedbackCellWall parent_wall;
    NineLoopFeedbackReceipt parent_receipt{};
    HHSExactStatus status = parent_wall.evaluate(
        input.parent_input,
        input.parent_feedback_hash216,
        parent_receipt
    );
    if (status != HHS_EXACT_STATUS_OK ||
        parent_receipt.accepted != 1U ||
        parent_receipt.candidate_only != 1U ||
        parent_receipt.canonical_vm81_mutation_authority != 0U ||
        parent_receipt.canonical_hash72_authority != 0U ||
        parent_receipt.canonical_hash216_authority != 0U ||
        parent_receipt.canonical_persistence_authority != 0U ||
        parent_receipt.floating_point_canonical_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.parent_1_70_verified = 1U;
    std::memcpy(
        out.parent_hash216,
        parent_receipt.feedback_candidate_hash216,
        HHS_HASH216_LEN + 1U
    );

    if (!exact_specimen_witness(input))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.specimen_identity_verified = 1U;
    out.source_lineage_verified = 1U;
    out.negative_example_verified = 1U;
    out.dataset_scope_verified = 1U;

    status = derive_candidate_hash216(input, out.training_candidate_hash216);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!hash216_text_valid(expected_hash216) ||
        std::memcmp(
            expected_hash216,
            out.training_candidate_hash216,
            HHS_HASH216_LEN + 1U
        ) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.hash216_replay_verified = 1U;
    out.accepted = 1U;
    return HHS_EXACT_STATUS_OK;
}

}  // namespace hhs::lane5

#include "hhs_pass219_lane5_nine_loop_relation_dataset_cell_wall_1_72.hpp"

#include <cstddef>
#include <cinttypes>
#include <cstdio>
#include <cstring>

namespace hhs::lane5 {
namespace {

constexpr char kDatasetSha256[] =
    "dd623f4fc778364274e7ba05c914fb441b724ca3ce41a4eb4df4cdc64935d587";
constexpr char kRecordChainSha256[] =
    "4a951f76afcd3f759e74263bc9cd0019b50f034bc07e93341b73200e0c85bd6a";
constexpr char kParentSpecimenSha256[] =
    "96a9f686a1ab35c8600ba7a38a367af38339b51a70182c3d7981ee529ff50191";

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

bool exact_dataset_witness(const NineLoopRelationDatasetInput& input) noexcept {
    return exact_text(input.dataset_sha256, kDatasetSha256) &&
           exact_text(input.ordered_record_chain_sha256, kRecordChainSha256) &&
           exact_text(input.parent_specimen_sha256, kParentSpecimenSha256) &&
           input.record_count == UINT32_C(12) &&
           input.additive_record_count == UINT32_C(6) &&
           input.neutral_record_count == UINT32_C(4) &&
           input.negative_record_count == UINT32_C(2) &&
           input.additive_record_count +
               input.neutral_record_count +
               input.negative_record_count == input.record_count &&
           input.source_bound_features_verified == 1U &&
           input.negative_examples_verified == 1U &&
           input.ordered_chain_verified == 1U &&
           input.dataset_preparation_only == 1U &&
           input.model_weight_update_requested == 0U &&
           input.learning_commit_requested == 0U;
}

}  // namespace

HHSExactStatus NineLoopRelationDatasetCellWall::derive_candidate_hash216(
    const NineLoopRelationDatasetInput& input,
    char out_hash216[HHS_HASH216_LEN + 1]
) noexcept {
    if (out_hash216 == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hash216_text_valid(input.parent_training_hash216) ||
        !exact_dataset_witness(input))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    char material[1100]{};
    const int written = std::snprintf(
        material,
        sizeof(material),
        "HHS-P219-LANE5-NINE-LOOP-1.72|"
        "parent=%s|dataset=%s|recordChain=%s|specimen=%s|"
        "records=%" PRIu32 "|positive=%" PRIu32 "|neutral=%" PRIu32
        "|negative=%" PRIu32 "|sourceBound=%u|negativeExamples=%u|"
        "orderedChain=%u|datasetOnly=%u|weightRequest=%u|learningRequest=%u",
        input.parent_training_hash216,
        input.dataset_sha256,
        input.ordered_record_chain_sha256,
        input.parent_specimen_sha256,
        input.record_count,
        input.additive_record_count,
        input.neutral_record_count,
        input.negative_record_count,
        static_cast<unsigned>(input.source_bound_features_verified),
        static_cast<unsigned>(input.negative_examples_verified),
        static_cast<unsigned>(input.ordered_chain_verified),
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

HHSExactStatus NineLoopRelationDatasetCellWall::evaluate(
    const NineLoopRelationDatasetInput& input,
    const char expected_hash216[HHS_HASH216_LEN + 1],
    NineLoopRelationDatasetReceipt& out
) const noexcept {
    out = NineLoopRelationDatasetReceipt{};
    out.version = kNineLoopRelationDatasetVersion;
    out.namespace_id = kNineLoopRelationDatasetNamespace;
    out.candidate_only = 1U;

    NineLoopTrainingSpecimenCellWall parent_wall;
    NineLoopTrainingSpecimenReceipt parent_receipt{};
    HHSExactStatus status = parent_wall.evaluate(
        input.parent_input,
        input.parent_training_hash216,
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

    out.parent_1_71_verified = 1U;
    std::memcpy(
        out.parent_hash216,
        parent_receipt.training_candidate_hash216,
        HHS_HASH216_LEN + 1U
    );

    if (!exact_dataset_witness(input))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.dataset_identity_verified = 1U;
    out.ordered_chain_verified = 1U;
    out.record_partition_verified = 1U;
    out.source_bound_features_verified = 1U;
    out.negative_examples_verified = 1U;
    out.dataset_scope_verified = 1U;

    status = derive_candidate_hash216(
        input,
        out.relation_dataset_candidate_hash216
    );
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!hash216_text_valid(expected_hash216) ||
        std::memcmp(
            expected_hash216,
            out.relation_dataset_candidate_hash216,
            HHS_HASH216_LEN + 1U
        ) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.hash216_replay_verified = 1U;
    out.accepted = 1U;
    return HHS_EXACT_STATUS_OK;
}

}  // namespace hhs::lane5

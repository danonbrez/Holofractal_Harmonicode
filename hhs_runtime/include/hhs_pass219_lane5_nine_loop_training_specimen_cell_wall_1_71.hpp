#ifndef HHS_PASS219_LANE5_NINE_LOOP_TRAINING_SPECIMEN_CELL_WALL_1_71_HPP
#define HHS_PASS219_LANE5_NINE_LOOP_TRAINING_SPECIMEN_CELL_WALL_1_71_HPP

#include "hhs_pass219_lane5_nine_loop_feedback_cell_wall_1_70.hpp"

#include <cstdint>

namespace hhs::lane5 {

inline constexpr std::uint32_t kNineLoopTrainingSpecimenVersion = UINT32_C(0x00010047);
inline constexpr std::uint32_t kNineLoopTrainingSpecimenNamespace = UINT32_C(0x00021947);

struct NineLoopTrainingSpecimenInput final {
    NineLoopFeedbackInput parent_input{};
    char parent_feedback_hash216[HHS_HASH216_LEN + 1]{};
    char training_specimen_sha256[65]{};
    char parent_feedback_payload_sha256[65]{};
    char parent_relation_sha256[65]{};
    char parent_support_sha256[65]{};
    std::uint32_t training_feedback_label_count{};
    std::uint32_t learning_objective_count{};
    std::uint32_t deviation_feature_count{};
    std::uint8_t source_lineage_verified{};
    std::uint8_t negative_example_preserved{};
    std::uint8_t exact_ratio_features_verified{};
    std::uint8_t trinary_features_verified{};
    std::uint8_t dataset_preparation_only{};
    std::uint8_t model_weight_update_requested{};
    std::uint8_t learning_commit_requested{};
};

struct NineLoopTrainingSpecimenReceipt final {
    std::uint32_t version{};
    std::uint32_t namespace_id{};
    std::uint8_t accepted{};
    std::uint8_t parent_1_70_verified{};
    std::uint8_t specimen_identity_verified{};
    std::uint8_t source_lineage_verified{};
    std::uint8_t negative_example_verified{};
    std::uint8_t dataset_scope_verified{};
    std::uint8_t hash216_replay_verified{};
    std::uint8_t candidate_only{};
    std::uint8_t model_weight_update_authority{};
    std::uint8_t learning_commit_authority{};
    std::uint8_t canonical_vm81_mutation_authority{};
    std::uint8_t canonical_hash72_authority{};
    std::uint8_t canonical_hash216_authority{};
    std::uint8_t canonical_persistence_authority{};
    std::uint8_t floating_point_canonical_authority{};
    char parent_hash216[HHS_HASH216_LEN + 1]{};
    char training_candidate_hash216[HHS_HASH216_LEN + 1]{};
};

class NineLoopTrainingSpecimenCellWall final {
public:
    static HHSExactStatus derive_candidate_hash216(
        const NineLoopTrainingSpecimenInput& input,
        char out_hash216[HHS_HASH216_LEN + 1]
    ) noexcept;

    HHSExactStatus evaluate(
        const NineLoopTrainingSpecimenInput& input,
        const char expected_hash216[HHS_HASH216_LEN + 1],
        NineLoopTrainingSpecimenReceipt& out_receipt
    ) const noexcept;
};

}  // namespace hhs::lane5

#endif

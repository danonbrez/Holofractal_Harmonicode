#ifndef HHS_PASS219_LANE5_NINE_LOOP_RELATION_DATASET_CELL_WALL_1_72_HPP
#define HHS_PASS219_LANE5_NINE_LOOP_RELATION_DATASET_CELL_WALL_1_72_HPP

#include "hhs_pass219_lane5_nine_loop_training_specimen_cell_wall_1_71.hpp"

#include <cstdint>

namespace hhs::lane5 {

inline constexpr std::uint32_t kNineLoopRelationDatasetVersion = UINT32_C(0x00010048);
inline constexpr std::uint32_t kNineLoopRelationDatasetNamespace = UINT32_C(0x00021948);

struct NineLoopRelationDatasetInput final {
    NineLoopTrainingSpecimenInput parent_input{};
    char parent_training_hash216[HHS_HASH216_LEN + 1]{};
    char dataset_sha256[65]{};
    char ordered_record_chain_sha256[65]{};
    char parent_specimen_sha256[65]{};
    std::uint32_t record_count{};
    std::uint32_t additive_record_count{};
    std::uint32_t neutral_record_count{};
    std::uint32_t negative_record_count{};
    std::uint8_t source_bound_features_verified{};
    std::uint8_t negative_examples_verified{};
    std::uint8_t ordered_chain_verified{};
    std::uint8_t dataset_preparation_only{};
    std::uint8_t model_weight_update_requested{};
    std::uint8_t learning_commit_requested{};
};

struct NineLoopRelationDatasetReceipt final {
    std::uint32_t version{};
    std::uint32_t namespace_id{};
    std::uint8_t accepted{};
    std::uint8_t parent_1_71_verified{};
    std::uint8_t dataset_identity_verified{};
    std::uint8_t ordered_chain_verified{};
    std::uint8_t record_partition_verified{};
    std::uint8_t source_bound_features_verified{};
    std::uint8_t negative_examples_verified{};
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
    char relation_dataset_candidate_hash216[HHS_HASH216_LEN + 1]{};
};

class NineLoopRelationDatasetCellWall final {
public:
    static HHSExactStatus derive_candidate_hash216(
        const NineLoopRelationDatasetInput& input,
        char out_hash216[HHS_HASH216_LEN + 1]
    ) noexcept;

    HHSExactStatus evaluate(
        const NineLoopRelationDatasetInput& input,
        const char expected_hash216[HHS_HASH216_LEN + 1],
        NineLoopRelationDatasetReceipt& out_receipt
    ) const noexcept;
};

}  // namespace hhs::lane5

#endif

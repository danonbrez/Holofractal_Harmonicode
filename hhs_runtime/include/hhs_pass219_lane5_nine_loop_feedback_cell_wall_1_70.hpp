#ifndef HHS_PASS219_LANE5_NINE_LOOP_FEEDBACK_CELL_WALL_1_70_HPP
#define HHS_PASS219_LANE5_NINE_LOOP_FEEDBACK_CELL_WALL_1_70_HPP

#include "hhs_pass219_lane5_nine_loop_large_artifact_cell_wall_1_69.hpp"

#include <cstdint>

namespace hhs::lane5 {

inline constexpr std::uint32_t kNineLoopFeedbackVersion = UINT32_C(0x00010046);
inline constexpr std::uint32_t kNineLoopFeedbackNamespace = UINT32_C(0x00021946);

struct NineLoopFeedbackInput final {
    NineLoopLargeArtifactInput parent_input{};
    char parent_large_artifact_hash216[HHS_HASH216_LEN + 1]{};
    char parent_relation_sha256[65]{};
    char parent_support_sha256[65]{};
    char wolfram_feedback_material_sha256[65]{};
    char feedback_payload_sha256[65]{};
    char genesis_identity[96]{};
    std::uint64_t root_seed_numerator{};
    std::uint32_t root_seed_denominator{};
    std::uint32_t certified_rational_coordinates{};
    std::uint32_t total_nonzero_coordinates{};
    std::uint32_t two_prime_only_coordinates{};
    std::uint32_t comparison_rows{};
    std::uint32_t comparison_two_prime_only_rows{};
    std::int8_t literal_container_identity_assumption{};
    std::int8_t logical_representation_equivalence{};
    std::int8_t support_geometry{};
    std::int8_t foreign_rational_reconstruction_complete{};
    std::uint8_t wolfram_receipt_verified{};
    std::uint8_t deviation_vector_verified{};
};

struct NineLoopFeedbackReceipt final {
    std::uint32_t version{};
    std::uint32_t namespace_id{};
    std::uint8_t accepted{};
    std::uint8_t parent_1_69_verified{};
    std::uint8_t relation_identity_verified{};
    std::uint8_t wolfram_receipt_verified{};
    std::uint8_t feedback_payload_verified{};
    std::uint8_t coverage_verified{};
    std::uint8_t genesis_identity_verified{};
    std::uint8_t deviation_vector_verified{};
    std::uint8_t hash216_replay_verified{};
    std::uint8_t candidate_only{};
    std::uint8_t canonical_vm81_mutation_authority{};
    std::uint8_t canonical_hash72_authority{};
    std::uint8_t canonical_hash216_authority{};
    std::uint8_t canonical_persistence_authority{};
    std::uint8_t floating_point_canonical_authority{};
    char parent_hash216[HHS_HASH216_LEN + 1]{};
    char feedback_candidate_hash216[HHS_HASH216_LEN + 1]{};
};

class NineLoopFeedbackCellWall final {
public:
    static HHSExactStatus derive_candidate_hash216(
        const NineLoopFeedbackInput& input,
        char out_hash216[HHS_HASH216_LEN + 1]
    ) noexcept;

    HHSExactStatus evaluate(
        const NineLoopFeedbackInput& input,
        const char expected_hash216[HHS_HASH216_LEN + 1],
        NineLoopFeedbackReceipt& out_receipt
    ) const noexcept;
};

}  // namespace hhs::lane5

#endif

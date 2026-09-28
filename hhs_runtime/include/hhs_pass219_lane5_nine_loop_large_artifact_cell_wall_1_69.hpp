#ifndef HHS_PASS219_LANE5_NINE_LOOP_LARGE_ARTIFACT_CELL_WALL_1_69_HPP
#define HHS_PASS219_LANE5_NINE_LOOP_LARGE_ARTIFACT_CELL_WALL_1_69_HPP

#include "hhs_pass219_lane5_nine_loop_source_cell_wall_1_68.hpp"

#include <cstdint>

namespace hhs::lane5 {

inline constexpr std::uint32_t kNineLoopLargeArtifactVersion = UINT32_C(0x00010045);
inline constexpr std::uint32_t kNineLoopLargeArtifactNamespace = UINT32_C(0x00021945);
inline constexpr std::uint32_t kNineLoopMatrixRows = UINT32_C(424);
inline constexpr std::uint32_t kNineLoopMatrixColumns = UINT32_C(5431);
inline constexpr std::uint32_t kNineLoopMatrixNonzero = UINT32_C(1018297);
inline constexpr std::uint32_t kNineLoopComparisonRows = UINT32_C(107053);

struct NineLoopLargeArtifactInput final {
    NineLoopSourceAttestationInput parent_input{};
    char parent_source_hash216[HHS_HASH216_LEN + 1]{};
    char p1_source_sha256[65]{};
    char p2_source_sha256[65]{};
    char comparison_source_sha256[65]{};
    char septuple_source_sha256[65]{};
    char e0_support_sha256[65]{};
    char comparison_normalized_sha256[65]{};
    char septuple_structure_sha256[65]{};
    char relation_sha256[65]{};
    std::uint32_t matrix_rows{};
    std::uint32_t matrix_columns{};
    std::uint32_t matrix_nonzero{};
    std::uint32_t comparison_rows{};
    std::uint8_t source_manifest_verified{};
    std::uint8_t logical_equivalence_verified{};
    std::uint8_t archive_integrity_verified{};
    std::uint8_t comparison_integrity_verified{};
};

struct NineLoopLargeArtifactReceipt final {
    std::uint32_t version{};
    std::uint32_t namespace_id{};
    std::uint8_t accepted{};
    std::uint8_t parent_1_68_verified{};
    std::uint8_t source_identities_verified{};
    std::uint8_t matrix_geometry_verified{};
    std::uint8_t support_geometry_verified{};
    std::uint8_t comparison_verified{};
    std::uint8_t archive_verified{};
    std::uint8_t relation_identity_verified{};
    std::uint8_t hash216_replay_verified{};
    std::uint8_t candidate_only{};
    std::uint8_t canonical_vm81_mutation_authority{};
    std::uint8_t canonical_hash72_authority{};
    std::uint8_t canonical_hash216_authority{};
    std::uint8_t canonical_persistence_authority{};
    std::uint8_t floating_point_canonical_authority{};
    char parent_hash216[HHS_HASH216_LEN + 1]{};
    char large_artifact_candidate_hash216[HHS_HASH216_LEN + 1]{};
};

class NineLoopLargeArtifactCellWall final {
public:
    static HHSExactStatus derive_candidate_hash216(
        const NineLoopLargeArtifactInput& input,
        char out_hash216[HHS_HASH216_LEN + 1]
    ) noexcept;

    HHSExactStatus evaluate(
        const NineLoopLargeArtifactInput& input,
        const char expected_hash216[HHS_HASH216_LEN + 1],
        NineLoopLargeArtifactReceipt& out_receipt
    ) const noexcept;
};

}  // namespace hhs::lane5

#endif

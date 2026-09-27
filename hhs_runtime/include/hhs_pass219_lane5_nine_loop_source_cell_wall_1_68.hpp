#ifndef HHS_PASS219_LANE5_NINE_LOOP_SOURCE_CELL_WALL_1_68_HPP
#define HHS_PASS219_LANE5_NINE_LOOP_SOURCE_CELL_WALL_1_68_HPP

#include "hhs_pass219_lane5_nine_loop_cell_wall_1_67.hpp"

#include <cstdint>

namespace hhs::lane5 {

inline constexpr std::uint32_t kNineLoopSourceAttestationVersion = UINT32_C(0x00010044);
inline constexpr std::uint32_t kNineLoopSourceAttestationNamespace = UINT32_C(0x00021944);
inline constexpr std::uint32_t kNineLoopSourceNonzeroRows = UINT32_C(20400);
inline constexpr std::uint32_t kNineLoopSourceZeroRows = UINT32_C(230);
inline constexpr std::uint32_t kNineLoopSourceTotalRows = UINT32_C(20630);

struct NineLoopSourceAttestationInput final {
    NineLoopForeignMetadata parent_metadata{};
    char parent_candidate_hash216[HHS_HASH216_LEN + 1]{};
    char manifest_sha256[65]{};
    char sample_sha256[65]{};
    char summary_sha256[65]{};
    std::uint32_t nonzero_rows{};
    std::uint32_t zero_rows{};
    std::uint32_t total_rows{};
    std::uint32_t unique_words{};
    std::uint8_t manifest_member_verified{};
    std::uint8_t all_nonzero_rationals_exact{};
    std::uint8_t all_zero_rows_exact{};
    std::uint8_t reserved0{};
};

struct NineLoopSourceAttestationReceipt final {
    std::uint32_t version{};
    std::uint32_t namespace_id{};
    std::uint8_t accepted{};
    std::uint8_t parent_1_67_verified{};
    std::uint8_t manifest_identity_verified{};
    std::uint8_t sample_identity_verified{};
    std::uint8_t summary_identity_verified{};
    std::uint8_t exact_row_counts_verified{};
    std::uint8_t exact_rational_replay_verified{};
    std::uint8_t manifest_membership_verified{};
    std::uint8_t candidate_only{};
    std::uint8_t canonical_vm81_mutation_authority{};
    std::uint8_t canonical_hash72_authority{};
    std::uint8_t canonical_hash216_authority{};
    std::uint8_t canonical_persistence_authority{};
    std::uint8_t floating_point_canonical_authority{};
    char parent_hash216[HHS_HASH216_LEN + 1]{};
    char source_candidate_hash216[HHS_HASH216_LEN + 1]{};
};

class NineLoopSourceAttestationCellWall final {
public:
    static HHSExactStatus derive_candidate_hash216(
        const NineLoopSourceAttestationInput& input,
        char out_hash216[HHS_HASH216_LEN + 1]
    ) noexcept;

    HHSExactStatus evaluate(
        const NineLoopSourceAttestationInput& input,
        const char expected_hash216[HHS_HASH216_LEN + 1],
        NineLoopSourceAttestationReceipt& out_receipt
    ) const noexcept;
};

}  // namespace hhs::lane5

#endif

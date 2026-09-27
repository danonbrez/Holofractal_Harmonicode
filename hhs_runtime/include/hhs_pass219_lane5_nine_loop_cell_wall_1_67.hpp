#ifndef HHS_PASS219_LANE5_NINE_LOOP_CELL_WALL_1_67_HPP
#define HHS_PASS219_LANE5_NINE_LOOP_CELL_WALL_1_67_HPP

#include "hhs_hash216.h"
#include "hhs_pass219_global_conservation_polarity_1_66.h"
#include "hhs_pass219_monolithic_constraint_abi_1_20.h"

#include <cstdint>

namespace hhs::lane5 {

inline constexpr std::uint32_t kNineLoopEquivalenceVersion = UINT32_C(0x00010043);
inline constexpr std::uint32_t kNineLoopEquivalenceNamespace = UINT32_C(0x00021943);

struct NineLoopForeignMetadata final {
    std::uint32_t loop_order{};
    std::uint32_t symbol_weight{};
    std::uint32_t primitive_alphabet_count{};
    std::uint32_t quintuple_coproduct_count{};
    std::uint32_t weight13_basis_dimension{};
    std::uint32_t delta0_octuple_term_count{};
    std::uint32_t septuple_determining_nonzero_coefficients{};
    std::uint32_t quintuple_rank{};
    std::int64_t sample_numerator{};
    std::uint64_t sample_denominator{};
    std::uint32_t prime_moduli[2]{};
    std::uint32_t sample_residues[2]{};
    std::uint8_t foreign_delta_is_kinematic{};
    std::uint8_t native_delta_e_is_error_closure{};
    std::uint8_t delta_alias_authorized{};
    std::uint8_t dual_route_agreement{};
};

struct NineLoopEquivalenceReceipt final {
    std::uint32_t version{};
    std::uint32_t namespace_id{};
    std::uint8_t accepted{};
    std::uint8_t parent_1_66_verified{};
    std::uint8_t monolithic_source_identity_verified{};
    std::uint8_t foreign_delta_quarantine_verified{};
    std::uint8_t exact_sample_oracle_verified{};
    std::uint8_t structure_counts_verified{};
    std::uint8_t dual_route_metadata_verified{};
    std::uint8_t hash216_composition_validated{};
    std::uint8_t candidate_only{};
    std::uint8_t canonical_vm81_mutation_authority{};
    std::uint8_t canonical_hash72_authority{};
    std::uint8_t canonical_hash216_authority{};
    std::uint8_t canonical_persistence_authority{};
    std::uint8_t floating_point_canonical_authority{};
    char candidate_hash216[HHS_HASH216_LEN + 1]{};
};

class NineLoopForeignEquivalenceCellWall final {
public:
    static HHSExactStatus derive_candidate_hash216(
        const NineLoopForeignMetadata& metadata,
        char out_hash216[HHS_HASH216_LEN + 1]
    ) noexcept;

    HHSExactStatus evaluate(
        const NineLoopForeignMetadata& metadata,
        const char expected_hash216[HHS_HASH216_LEN + 1],
        NineLoopEquivalenceReceipt& out_receipt
    ) const noexcept;
};

}  // namespace hhs::lane5

#endif

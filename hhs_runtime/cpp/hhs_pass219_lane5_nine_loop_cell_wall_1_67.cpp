#include "hhs_pass219_lane5_nine_loop_cell_wall_1_67.hpp"

#include <cstddef>
#include <cinttypes>
#include <cstdio>
#include <cstring>

namespace hhs::lane5 {
namespace {

constexpr std::uint8_t kMonolithicFrozenTexSha256[32] = {
    0x9f,0x22,0x38,0x98,0x1b,0xf5,0x09,0xd2,
    0x2f,0xfe,0xbb,0x46,0x81,0x63,0x46,0xf3,
    0x89,0xfd,0x2d,0x94,0x9c,0xcd,0x79,0x56,
    0xcd,0xe3,0x63,0x0a,0xb2,0xb5,0x69,0x44
};

std::uint64_t pow_mod(std::uint64_t base, std::uint64_t exponent, std::uint64_t modulus) noexcept {
    std::uint64_t result = 1U;
    base %= modulus;
    while (exponent != 0U) {
        if ((exponent & 1U) != 0U)
            result = (result * base) % modulus;
        base = (base * base) % modulus;
        exponent >>= 1U;
    }
    return result;
}

std::uint32_t rational_residue(
    std::int64_t numerator,
    std::uint64_t denominator,
    std::uint32_t prime
) noexcept {
    if (denominator == 0U || prime <= 2U || denominator % prime == 0U)
        return UINT32_MAX;
    std::int64_t signed_residue = numerator % static_cast<std::int64_t>(prime);
    if (signed_residue < 0)
        signed_residue += static_cast<std::int64_t>(prime);
    const std::uint64_t inverse = pow_mod(
        denominator % prime,
        static_cast<std::uint64_t>(prime) - 2U,
        prime
    );
    return static_cast<std::uint32_t>(
        (static_cast<std::uint64_t>(signed_residue) * inverse) % prime
    );
}

bool exact_structure(const NineLoopForeignMetadata& m) noexcept {
    return m.loop_order == 9U &&
           m.symbol_weight == 18U &&
           m.primitive_alphabet_count == 9U &&
           m.quintuple_coproduct_count == 424U &&
           m.weight13_basis_dimension == 5431U &&
           m.delta0_octuple_term_count == 295186924U &&
           m.septuple_determining_nonzero_coefficients == 107053U &&
           m.quintuple_rank == 400U;
}

bool exact_oracle(const NineLoopForeignMetadata& m) noexcept {
    return m.sample_numerator == INT64_C(-105757) &&
           m.sample_denominator == UINT64_C(65536) &&
           m.prime_moduli[0] == UINT32_C(2147483647) &&
           m.prime_moduli[1] == UINT32_C(2147483629) &&
           m.sample_residues[0] == UINT32_C(829521918) &&
           m.sample_residues[1] == UINT32_C(1173913588) &&
           rational_residue(m.sample_numerator, m.sample_denominator, m.prime_moduli[0]) ==
               m.sample_residues[0] &&
           rational_residue(m.sample_numerator, m.sample_denominator, m.prime_moduli[1]) ==
               m.sample_residues[1];
}

bool delta_quarantine(const NineLoopForeignMetadata& m) noexcept {
    return m.foreign_delta_is_kinematic == 1U &&
           m.native_delta_e_is_error_closure == 1U &&
           m.delta_alias_authorized == 0U;
}

bool hash216_text_valid(const char value[HHS_HASH216_LEN + 1]) noexcept {
    if (value == nullptr || value[HHS_HASH216_LEN] != '\0')
        return false;
    for (std::size_t i = 0U; i < HHS_HASH216_LEN; ++i) {
        if (value[i] == '\0')
            return false;
    }
    return true;
}

}  // namespace

HHSExactStatus NineLoopForeignEquivalenceCellWall::derive_candidate_hash216(
    const NineLoopForeignMetadata& m,
    char out_hash216[HHS_HASH216_LEN + 1]
) noexcept {
    if (out_hash216 == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    char payload[768]{};
    const int written = std::snprintf(
        payload,
        sizeof(payload),
        "HHS-P219-LANE5-NINE-LOOP-1.67|"
        "loop=%" PRIu32 "|weight=%" PRIu32 "|alphabet=%" PRIu32
        "|q5=%" PRIu32 "|w13=%" PRIu32 "|delta0=%" PRIu32
        "|septuple=%" PRIu32 "|rank=%" PRIu32
        "|num=%" PRId64 "|den=%" PRIu64
        "|p0=%" PRIu32 "|p1=%" PRIu32
        "|r0=%" PRIu32 "|r1=%" PRIu32
        "|foreignDelta=%u|nativeDeltaE=%u|alias=%u|dualRoute=%u",
        m.loop_order,
        m.symbol_weight,
        m.primitive_alphabet_count,
        m.quintuple_coproduct_count,
        m.weight13_basis_dimension,
        m.delta0_octuple_term_count,
        m.septuple_determining_nonzero_coefficients,
        m.quintuple_rank,
        m.sample_numerator,
        m.sample_denominator,
        m.prime_moduli[0],
        m.prime_moduli[1],
        m.sample_residues[0],
        m.sample_residues[1],
        static_cast<unsigned>(m.foreign_delta_is_kinematic),
        static_cast<unsigned>(m.native_delta_e_is_error_closure),
        static_cast<unsigned>(m.delta_alias_authorized),
        static_cast<unsigned>(m.dual_route_agreement)
    );
    if (written <= 0 || static_cast<std::size_t>(written) >= sizeof(payload))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    HHSHash216 hash{};
    hhs_hash216_compute(payload, static_cast<std::size_t>(written), &hash);
    std::memcpy(out_hash216, hash.value, HHS_HASH216_LEN + 1U);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus NineLoopForeignEquivalenceCellWall::evaluate(
    const NineLoopForeignMetadata& metadata,
    const char expected_hash216[HHS_HASH216_LEN + 1],
    NineLoopEquivalenceReceipt& out
) const noexcept {
    std::memset(&out, 0, sizeof(out));
    out.version = kNineLoopEquivalenceVersion;
    out.namespace_id = kNineLoopEquivalenceNamespace;
    out.candidate_only = 1U;

    HHSExactPass219ConservationReceiptV1 parent{};
    HHSExactStatus status = hhs_exact_pass219_conservation_1_66_verify(&parent);
    if (status != HHS_EXACT_STATUS_OK ||
        parent.decision != HHS_EXACT_PASS219_CONSERVATION_DECISION_VERIFIED ||
        parent.operator_typing_verified != 1U ||
        parent.canonical_c2_preserved != 1U ||
        parent.canonical_vm81_mutation_authority != 0U ||
        parent.canonical_hash216_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out.parent_1_66_verified = 1U;

    HHSExactPass219MonolithicDescriptorV1 monolithic{};
    status = hhs_exact_pass219_monolithic_descriptor(&monolithic);
    if (status != HHS_EXACT_STATUS_OK ||
        monolithic.monolithic_admission_only != 1U ||
        monolithic.source_structure_preserved != 1U ||
        monolithic.vm81_proof_required != 1U ||
        std::memcmp(
            monolithic.frozen_tex_sha256,
            kMonolithicFrozenTexSha256,
            sizeof(kMonolithicFrozenTexSha256)
        ) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out.monolithic_source_identity_verified = 1U;

    if (!delta_quarantine(metadata))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out.foreign_delta_quarantine_verified = 1U;

    if (!exact_structure(metadata))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out.structure_counts_verified = 1U;

    if (!exact_oracle(metadata))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out.exact_sample_oracle_verified = 1U;

    if (metadata.dual_route_agreement != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out.dual_route_metadata_verified = 1U;

    status = derive_candidate_hash216(metadata, out.candidate_hash216);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!hash216_text_valid(expected_hash216) ||
        std::memcmp(expected_hash216, out.candidate_hash216, HHS_HASH216_LEN + 1U) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out.hash216_composition_validated = 1U;

    out.accepted = 1U;
    return HHS_EXACT_STATUS_OK;
}

}  // namespace hhs::lane5

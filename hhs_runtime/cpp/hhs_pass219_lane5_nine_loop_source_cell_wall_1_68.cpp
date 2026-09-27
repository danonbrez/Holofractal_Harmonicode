#include "hhs_pass219_lane5_nine_loop_source_cell_wall_1_68.hpp"

#include <cinttypes>
#include <cstdio>
#include <cstring>

namespace hhs::lane5 {
namespace {

constexpr char kManifestSha256[] =
    "f96534526482f03e638ee030b1a88968348901f70967bb89618c76420a21ffe5";
constexpr char kSampleSha256[] =
    "a78557e58efb3e12cccb647974131a3f694322bebb97607a5648db0484099b18";
constexpr char kSummarySha256[] =
    "fbda1f90205bcf4f02b154aba25346aa83768e6cbbccbeeceaef9187eb691088";

bool hash216_text_valid(const char value[HHS_HASH216_LEN + 1]) noexcept {
    if (value == nullptr || value[HHS_HASH216_LEN] != '\0')
        return false;
    for (std::size_t i = 0U; i < HHS_HASH216_LEN; ++i) {
        if (value[i] == '\0')
            return false;
    }
    return true;
}

bool exact_source_identity(const NineLoopSourceAttestationInput& input) noexcept {
    return std::strcmp(input.manifest_sha256, kManifestSha256) == 0 &&
           std::strcmp(input.sample_sha256, kSampleSha256) == 0 &&
           std::strcmp(input.summary_sha256, kSummarySha256) == 0;
}

bool exact_counts(const NineLoopSourceAttestationInput& input) noexcept {
    return input.nonzero_rows == kNineLoopSourceNonzeroRows &&
           input.zero_rows == kNineLoopSourceZeroRows &&
           input.total_rows == kNineLoopSourceTotalRows &&
           input.unique_words == kNineLoopSourceTotalRows;
}

}  // namespace

HHSExactStatus NineLoopSourceAttestationCellWall::derive_candidate_hash216(
    const NineLoopSourceAttestationInput& input,
    char out_hash216[HHS_HASH216_LEN + 1]
) noexcept {
    if (out_hash216 == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hash216_text_valid(input.parent_candidate_hash216))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    char material[1024]{};
    const int written = std::snprintf(
        material,
        sizeof(material),
        "HHS-P219-LANE5-NINE-LOOP-1.68|"
        "parent=%s|manifest=%s|sample=%s|summary=%s|"
        "nonzero=%" PRIu32 "|zero=%" PRIu32 "|total=%" PRIu32 "|unique=%" PRIu32
        "|member=%u|rationals=%u|zeros=%u",
        input.parent_candidate_hash216,
        input.manifest_sha256,
        input.sample_sha256,
        input.summary_sha256,
        input.nonzero_rows,
        input.zero_rows,
        input.total_rows,
        input.unique_words,
        static_cast<unsigned>(input.manifest_member_verified),
        static_cast<unsigned>(input.all_nonzero_rationals_exact),
        static_cast<unsigned>(input.all_zero_rows_exact)
    );
    if (written <= 0 || static_cast<std::size_t>(written) >= sizeof(material))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    HHSHash216 hash{};
    hhs_hash216_compute(material, static_cast<std::size_t>(written), &hash);
    std::memcpy(out_hash216, hash.value, HHS_HASH216_LEN + 1U);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus NineLoopSourceAttestationCellWall::evaluate(
    const NineLoopSourceAttestationInput& input,
    const char expected_hash216[HHS_HASH216_LEN + 1],
    NineLoopSourceAttestationReceipt& out
) const noexcept {
    out = NineLoopSourceAttestationReceipt{};
    out.version = kNineLoopSourceAttestationVersion;
    out.namespace_id = kNineLoopSourceAttestationNamespace;
    out.candidate_only = 1U;

    NineLoopForeignEquivalenceCellWall parent_wall;
    NineLoopEquivalenceReceipt parent_receipt{};
    HHSExactStatus status = parent_wall.evaluate(
        input.parent_metadata,
        input.parent_candidate_hash216,
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
    out.parent_1_67_verified = 1U;
    std::memcpy(
        out.parent_hash216,
        parent_receipt.candidate_hash216,
        HHS_HASH216_LEN + 1U
    );

    if (!exact_source_identity(input))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out.manifest_identity_verified = 1U;
    out.sample_identity_verified = 1U;
    out.summary_identity_verified = 1U;

    if (!exact_counts(input))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out.exact_row_counts_verified = 1U;

    if (input.manifest_member_verified != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out.manifest_membership_verified = 1U;

    if (input.all_nonzero_rationals_exact != 1U ||
        input.all_zero_rows_exact != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out.exact_rational_replay_verified = 1U;

    status = derive_candidate_hash216(input, out.source_candidate_hash216);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!hash216_text_valid(expected_hash216) ||
        std::memcmp(
            expected_hash216,
            out.source_candidate_hash216,
            HHS_HASH216_LEN + 1U
        ) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out.accepted = 1U;
    return HHS_EXACT_STATUS_OK;
}

}  // namespace hhs::lane5
